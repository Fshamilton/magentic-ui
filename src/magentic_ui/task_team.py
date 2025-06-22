from typing import Any, Dict, List, Optional, Union

from autogen_agentchat.agents import UserProxyAgent
from autogen_agentchat.base import ChatAgent
from autogen_core import ComponentModel
from autogen_core.models import ChatCompletionClient

from .agents import USER_PROXY_DESCRIPTION, CoderAgent, FileSurfer, WebSurfer, get_xiaohongshu_coder_agent, XiaohongshuCoderAgent
from .agents.mcp import McpAgent
from .agents.users import DummyUserProxy, MetadataUserProxy
from .agents.web_surfer import WebSurferConfig
from .approval_guard import (
    ApprovalConfig,
    ApprovalGuard,
    ApprovalGuardContext,
    BaseApprovalGuard,
)
from .input_func import InputFuncType, make_agentchat_input_func
from .learning.memory_provider import MemoryControllerProvider
from .magentic_ui_config import MagenticUIConfig, ModelClientConfigs
from .teams import GroupChat, RoundRobinGroupChat
from .teams.orchestrator.orchestrator_config import OrchestratorConfig
from .tools.playwright.browser import get_browser_resource_config
from .types import RunPaths, Plan # Added Plan
from .utils import get_internal_urls
from loguru import logger # Added logger


async def get_task_team(
    magentic_ui_config: Optional[MagenticUIConfig] = None,
    input_func: Optional[InputFuncType] = None,
    *,
    paths: RunPaths,
) -> GroupChat | RoundRobinGroupChat:
    """
    Creates and returns a GroupChat team with specified configuration.

    Args:
        magentic_ui_config (MagenticUIConfig, optional): Magentic UI configuration for team. Default: None.
        paths (RunPaths): Paths for internal and external run directories.

    Returns:
        GroupChat | RoundRobinGroupChat: An instance of GroupChat or RoundRobinGroupChat with the specified agents and configuration.
    """
    if magentic_ui_config is None:
        magentic_ui_config = MagenticUIConfig()

    def get_model_client(
        model_client_config: Union[ComponentModel, Dict[str, Any], None],
        is_action_guard: bool = False,
    ) -> ChatCompletionClient:
        if model_client_config is None:
            return ChatCompletionClient.load_component(
                ModelClientConfigs.get_default_client_config()
                if not is_action_guard
                else ModelClientConfigs.get_default_action_guard_config()
            )
        return ChatCompletionClient.load_component(model_client_config)

    if not magentic_ui_config.inside_docker:
        assert (
            paths.external_run_dir == paths.internal_run_dir
        ), "External and internal run dirs must be the same in non-docker mode"

    model_client_orch = get_model_client(
        magentic_ui_config.model_client_configs.orchestrator
    )
    approval_guard: BaseApprovalGuard | None = None

    approval_policy = (
        magentic_ui_config.approval_policy
        if magentic_ui_config.approval_policy
        else "never"
    )

    websurfer_loop_team: bool = (
        magentic_ui_config.websurfer_loop if magentic_ui_config else False
    )

    model_client_coder = get_model_client(magentic_ui_config.model_client_configs.coder)
    model_client_file_surfer = get_model_client(
        magentic_ui_config.model_client_configs.file_surfer
    )
    browser_resource_config, _novnc_port, _playwright_port = (
        get_browser_resource_config(
            paths.external_run_dir,
            magentic_ui_config.novnc_port,
            magentic_ui_config.playwright_port,
            magentic_ui_config.inside_docker,
            headless=magentic_ui_config.browser_headless,
            local=magentic_ui_config.browser_local
            or magentic_ui_config.run_without_docker,
        )
    )

    orchestrator_config = OrchestratorConfig(
        cooperative_planning=magentic_ui_config.cooperative_planning,
        autonomous_execution=magentic_ui_config.autonomous_execution,
        allowed_websites=magentic_ui_config.allowed_websites,
        plan=magentic_ui_config.plan,
        model_context_token_limit=magentic_ui_config.model_context_token_limit,
        do_bing_search=magentic_ui_config.do_bing_search,
        retrieve_relevant_plans=magentic_ui_config.retrieve_relevant_plans,
        memory_controller_key=magentic_ui_config.memory_controller_key,
        allow_follow_up_input=magentic_ui_config.allow_follow_up_input,
        final_answer_prompt=magentic_ui_config.final_answer_prompt,
    )
    websurfer_model_client = magentic_ui_config.model_client_configs.web_surfer
    if websurfer_model_client is None:
        websurfer_model_client = ModelClientConfigs.get_default_client_config()
    websurfer_config = WebSurferConfig(
        name="web_surfer",
        model_client=websurfer_model_client,
        browser=browser_resource_config,
        single_tab_mode=False,
        max_actions_per_step=magentic_ui_config.max_actions_per_step,
        url_statuses={key: "allowed" for key in orchestrator_config.allowed_websites}
        if orchestrator_config.allowed_websites
        else None,
        url_block_list=get_internal_urls(magentic_ui_config.inside_docker, paths),
        multiple_tools_per_call=magentic_ui_config.multiple_tools_per_call,
        downloads_folder=str(paths.internal_run_dir),
        debug_dir=str(paths.internal_run_dir),
        animate_actions=True,
        start_page=None,
        use_action_guard=True,
        to_save_screenshots=False,
    )

    user_proxy: DummyUserProxy | MetadataUserProxy | UserProxyAgent

    if magentic_ui_config.user_proxy_type == "dummy":
        user_proxy = DummyUserProxy(name="user_proxy")
    elif magentic_ui_config.user_proxy_type == "metadata":
        assert (
            magentic_ui_config.task is not None
        ), "Task must be provided for metadata user proxy"
        assert (
            magentic_ui_config.hints is not None
        ), "Hints must be provided for metadata user proxy"
        assert (
            magentic_ui_config.answer is not None
        ), "Answer must be provided for metadata user proxy"
        user_proxy = MetadataUserProxy(
            name="user_proxy",
            description="Metadata User Proxy Agent",
            task=magentic_ui_config.task,
            helpful_task_hints=magentic_ui_config.hints,
            task_answer=magentic_ui_config.answer,
            model_client=model_client_orch,
        )
    else:
        user_proxy_input_func = make_agentchat_input_func(input_func)
        user_proxy = UserProxyAgent(
            description=USER_PROXY_DESCRIPTION,
            name="user_proxy",
            input_func=user_proxy_input_func,
        )

    if magentic_ui_config.user_proxy_type in ["dummy", "metadata"]:
        model_client_action_guard = get_model_client(
            magentic_ui_config.model_client_configs.action_guard,
            is_action_guard=True,
        )

        # Simple approval function that always returns yes
        def always_yes_input(prompt: str, input_type: str = "text_input") -> str:
            return "yes"

        approval_guard = ApprovalGuard(
            input_func=always_yes_input,
            default_approval=False,
            model_client=model_client_action_guard,
            config=ApprovalConfig(
                approval_policy=approval_policy,
            ),
        )
    elif input_func is not None:
        model_client_action_guard = get_model_client(
            magentic_ui_config.model_client_configs.action_guard
        )
        approval_guard = ApprovalGuard(
            input_func=input_func,
            default_approval=False,
            model_client=model_client_action_guard,
            config=ApprovalConfig(
                approval_policy=approval_policy,
            ),
        )
    with ApprovalGuardContext.populate_context(approval_guard):
        web_surfer = WebSurfer.from_config(websurfer_config)
    if websurfer_loop_team:
        # simplified team of only the web surfer
        team = RoundRobinGroupChat(
            participants=[web_surfer, user_proxy],
            max_turns=10000,
        )
        await team.lazy_init()
        return team
    coder_agent: CoderAgent | None = None
    file_surfer: FileSurfer | None = None
    if not magentic_ui_config.run_without_docker:
        coder_agent = CoderAgent(
            name="coder_agent",
            model_client=model_client_coder,
            work_dir=paths.internal_run_dir,
            bind_dir=paths.external_run_dir,
            model_context_token_limit=magentic_ui_config.model_context_token_limit,
            approval_guard=approval_guard,
        )

        file_surfer = FileSurfer(
            name="file_surfer",
            model_client=model_client_file_surfer,
            work_dir=paths.internal_run_dir,
            bind_dir=paths.external_run_dir,
            model_context_token_limit=magentic_ui_config.model_context_token_limit,
            approval_guard=approval_guard,
        )

    # Setup any mcp_agents
    mcp_agents: List[McpAgent] = [
        # TODO: Init from constructor?
        McpAgent._from_config(config)  # type: ignore
        for config in magentic_ui_config.mcp_agent_configs
    ]

    if (
        orchestrator_config.memory_controller_key is not None
        and orchestrator_config.retrieve_relevant_plans in ["reuse", "hint"]
    ):
        memory_provider = MemoryControllerProvider(
            internal_workspace_root=paths.internal_root_dir,
            external_workspace_root=paths.external_root_dir,
            inside_docker=magentic_ui_config.inside_docker,
        )
    else:
        memory_provider = None

    team_participants: List[ChatAgent] = [
        web_surfer,
        user_proxy,
    ]
    if not magentic_ui_config.run_without_docker:
        assert coder_agent is not None
        assert file_surfer is not None
        team_participants.extend([coder_agent, file_surfer])
    team_participants.extend(mcp_agents)
    logger.info(f"[TaskTeam] Initial team participants before mode selection: {[agent.name for agent in team_participants]}")

    if magentic_ui_config.task_type == "xiaohongshu":
        logger.info("[TaskTeam] Xiaohongshu mode activated. Configuring team for Xiaohongshu note generation.")

        raw_coder_config = magentic_ui_config.model_client_configs.coder
        xhs_coder_llm_config_list: List[Dict[str, Any]]
        if isinstance(raw_coder_config, dict):
            xhs_coder_llm_config_list = [raw_coder_config]
            logger.debug(f"[TaskTeam] XiaohongshuCoder LLM config (dict): {xhs_coder_llm_config_list}")
        elif isinstance(raw_coder_config, ComponentModel):
            xhs_coder_llm_config_list = [raw_coder_config.model_dump(exclude_none=True)]
            logger.debug(f"[TaskTeam] XiaohongshuCoder LLM config (ComponentModel): {xhs_coder_llm_config_list}")
        elif raw_coder_config is None:
            xhs_coder_llm_config_list = [ModelClientConfigs.get_default_client_config()]
            logger.warning("[TaskTeam] XiaohongshuCoder LLM config not specified, using default.")
        else:
            logger.error(f"[TaskTeam] Unexpected type for coder config: {type(raw_coder_config)}. Using default for XiaohongshuCoder.")
            xhs_coder_llm_config_list = [ModelClientConfigs.get_default_client_config()]

        xhs_coder = get_xiaohongshu_coder_agent(
            name_suffix="_xhs",
            config_list=xhs_coder_llm_config_list
        )
        actual_xiaohongshu_agent_name_in_team = xhs_coder.name
        logger.info(f"[TaskTeam] Instantiated XiaohongshuCoderAgent: {actual_xiaohongshu_agent_name_in_team}")

        xiaohongshu_plan_steps = [
            {"title": "热门内容抓取", "details": f"指示 {actual_xiaohongshu_agent_name_in_team} 使用 MediaCrawlerTool.search_hot_notes 搜索与用户提供的主题相关的热门小红书笔记。", "agent_name": actual_xiaohongshu_agent_name_in_team},
            {"title": "内容分析与洞察提取", "details": f"指示 {actual_xiaohongshu_agent_name_in_team} 使用 TextAnalysisTool.extract_insights_from_crawled_data 分析上一步抓取到的JSON数据。", "agent_name": actual_xiaohongshu_agent_name_in_team},
            {"title": "新笔记规划与简报生成 (Orchestrator 内部动作)", "details": "Orchestrator 根据上一步的洞察，为新的小红书笔记制定一个计划/简报，包含建议的标题方向, 核心信息/角度, 正文需涵盖的关键点, 期望的写作语气/人设, 图片的视觉概念/元素。", "agent_name": "no_action_agent"},
            {"title": "内容生成（文案与图片）", "details": f"指示 {actual_xiaohongshu_agent_name_in_team} 使用 ContentGenerationTool.generate_text (传入简报中的文本部分) 和 ContentGenerationTool.generate_image (传入简报中的视觉概念) 生成文案和图片。", "agent_name": actual_xiaohongshu_agent_name_in_team},
            {"title": "基础质量与美学检查", "details": f"指示 {actual_xiaohongshu_agent_name_in_team} 使用 ContentQATool.evaluate_aesthetics (对图片URL) 和 ContentQATool.check_text_compliance (对文本) 进行检查。", "agent_name": actual_xiaohongshu_agent_name_in_team},
            {"title": "呈现草稿供用户审核", "details": f"Orchestrator 将生成的文本、图片URL和QA结果打包，发送给 UserProxy ({user_proxy.name}) 以呈现给用户。", "agent_name": user_proxy.name}
        ]
        logger.debug(f"[TaskTeam] Defined Xiaohongshu plan steps: {xiaohongshu_plan_steps}")

        current_task_description = magentic_ui_config.task if magentic_ui_config.task else "生成小红书笔记"
        orchestrator_config.plan = Plan(task=current_task_description, steps=xiaohongshu_plan_steps)
        logger.info(f"[TaskTeam] Set pre-defined plan for Orchestrator. Task: {current_task_description}")

        final_team_participants_names = {user_proxy.name, xhs_coder.name}
        final_team_participants = [user_proxy, xhs_coder]

        for p_agent in team_participants:
            if p_agent.name not in final_team_participants_names and not isinstance(p_agent, (WebSurfer, CoderAgent)):
                logger.debug(f"[TaskTeam] Adding existing agent to Xiaohongshu team: {p_agent.name}")
                final_team_participants.append(p_agent)
                final_team_participants_names.add(p_agent.name)

        team_participants = final_team_participants
        logger.info(f"[TaskTeam] Final team participants for Xiaohongshu mode: {[agent.name for agent in team_participants]}")

    else:
        logger.info("[TaskTeam] General mode activated.")

    team = GroupChat(
        participants=team_participants,
        orchestrator_config=orchestrator_config,
        model_client=model_client_orch,
        memory_provider=memory_provider,
    )
    logger.info(f"[TaskTeam] GroupChat created with {len(team_participants)} participants.")

    await team.lazy_init()
    logger.info("[TaskTeam] Team initialized (lazy_init).")
    return team
