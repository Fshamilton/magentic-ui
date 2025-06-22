import autogen
from typing import Optional, List, Dict, Any
from magentic_ui.tools.xiaohongshu import (
    MediaCrawlerTool,
    TextAnalysisTool,
    ContentGenerationTool,
    ContentQATool,
)
from magentic_ui.config_manager import get_model_config_from_name # MagenticUIConfig no longer directly imported
from loguru import logger

DEFAULT_XIAOHONGSHU_CODER_SYSTEM_MESSAGE = """
You are a specialized Coder Agent with expertise in Xiaohongshu content operations.
You can use various tools for web crawling, content analysis, content generation, and quality assurance for Xiaohongshu notes.

You must use the tools provided to fulfill requests from the Orchestrator.
Strictly follow the Orchestrator's instructions regarding which tool to use and its parameters.

Available tools:
- MediaCrawlerTool: Searches for hot Xiaohongshu notes. (call search_hot_notes)
- TextAnalysisTool: Extracts insights from crawled data. (call extract_insights_from_crawled_data)
- ContentGenerationTool: Generates text copy and images for notes. (call generate_text, generate_image)
- ContentQATool: Evaluates image aesthetics and checks text compliance. (call evaluate_aesthetics, check_text_compliance)

When a tool call is successful, the output will be a JSON string. Analyze this JSON to inform your next steps or to provide results.
If a tool call fails, the output will also be a JSON string, usually with a "status": "error" and a "message" field. Report this error clearly.

Always respond by calling a tool or by providing a summary of results if the task is complete.
Do not ask the user for API keys or any other sensitive information. Assume all tools are ready to use.
"""

class XiaohongshuCoderAgent(autogen.ConversableAgent):
    def __init__(
        self,
        name: str = "XiaohongshuCoder",
        system_message: Optional[str] = DEFAULT_XIAOHONGSHU_CODER_SYSTEM_MESSAGE,
        llm_config: Optional[List[Dict[str, Any]]] = None, # Type hint for llm_config is List[Dict] or bool
        **kwargs,
    ):
        super().__init__(
            name=name,
            system_message=system_message,
            llm_config=llm_config,
            **kwargs,
        )
        logger.info(f"[{self.name}] Initialized with system message: '{system_message[:100]}...' and llm_config: {llm_config}")

        # Register tools
        function_map={
            "search_hot_notes": MediaCrawlerTool.search_hot_notes,
            "extract_insights_from_crawled_data": TextAnalysisTool.extract_insights_from_crawled_data,
            "generate_text": ContentGenerationTool.generate_text,
            "generate_image": ContentGenerationTool.generate_image,
            "evaluate_aesthetics": ContentQATool.evaluate_aesthetics,
            "check_text_compliance": ContentQATool.check_text_compliance,
        }
        self.register_function(function_map=function_map)
        logger.info(f"[{self.name}] Registered tools: {list(function_map.keys())}")


def get_xiaohongshu_coder_agent(
    name_suffix: str = "",
    llm_config_name: Optional[str] = None,
    config_list: Optional[List[Dict[str, Any]]] = None,
    custom_system_message: Optional[str] = None
) -> XiaohongshuCoderAgent:
    """Helper function to create and configure a XiaohongshuCoderAgent."""
    agent_name = f"XiaohongshuCoder{name_suffix}"
    logger.info(f"Creating XiaohongshuCoderAgent: {agent_name}")

    final_llm_config: Optional[List[Dict[str, Any]]] = None # Default to None, autogen handles False for human_input

    if config_list: # If a raw config_list is provided, it takes precedence
        logger.debug(f"Using provided config_list for {agent_name}: {config_list}")
        if isinstance(config_list, list) and all(isinstance(item, dict) for item in config_list):
            final_llm_config = config_list
        elif isinstance(config_list, dict) and "model" in config_list:
            final_llm_config = [config_list]
            logger.debug(f"Wrapped single model dict into list for {agent_name}.")
        else:
            logger.warning(f"Provided config_list for {agent_name} is not in the expected format (list of dicts or a single model dict). Will try llm_config_name or default.")

    if not final_llm_config and llm_config_name:
        logger.debug(f"Attempting to load LLM config '{llm_config_name}' for {agent_name}.")
        raw_config = get_model_config_from_name(llm_config_name) # This is part of Magentic-UI
        if raw_config:
            if isinstance(raw_config, dict) and "model" in raw_config:
                 final_llm_config = [raw_config]
                 logger.info(f"Loaded and wrapped LLM config '{llm_config_name}' for {agent_name}: {final_llm_config}")
            elif isinstance(raw_config, list) and all(isinstance(item, dict) for item in raw_config):
                 final_llm_config = raw_config
                 logger.info(f"Loaded LLM config list '{llm_config_name}' for {agent_name}: {final_llm_config}")
            else:
                logger.warning(f"LLM config '{llm_config_name}' from get_model_config_from_name was not in expected format (dict or list). Type: {type(raw_config)}. Agent {agent_name} may not have LLM configured.")
        else:
            logger.warning(f"LLM config '{llm_config_name}' not found or empty. Agent {agent_name} may not have LLM configured.")

    if not final_llm_config:
        logger.warning(f"No LLM configuration provided or found for {agent_name}. Agent will operate without LLM capabilities if not human_input_mode.")


    sys_msg = custom_system_message if custom_system_message else DEFAULT_XIAOHONGSHU_CODER_SYSTEM_MESSAGE
    logger.debug(f"System message for {agent_name} (first 100 chars): '{sys_msg[:100]}...'")

    agent = XiaohongshuCoderAgent(
        name=agent_name,
        llm_config=final_llm_config if final_llm_config else False, # Pass False if None for autogen's default behavior (often human input)
        system_message=sys_msg,
        human_input_mode="NEVER",
        code_execution_config=False,
    )
    logger.info(f"XiaohongshuCoderAgent '{agent_name}' created successfully.")
    return agent

# Example of how this might be used (for testing purposes, not part of the agent file itself)
if __name__ == '__main__':
    # This part is for local testing of the agent class if run directly.
    # It requires a config.json or similar for autogen to load model configs.
    logger.info("Running __main__ for XiaohongshuCoderAgent (local test mode)...")

    # Mock get_model_config_from_name for standalone testing
    def mock_get_model_config_from_name(name):
        logger.debug(f"Mocked get_model_config_from_name called with: {name}")
        if name == "coder_client_ollama_qwen3":
            return {
                "model": "ollama/qwen3",
                "api_key": "ollama",
                "base_url": "http://localhost:11434/v1"
            }
        return None

    original_get_model_config_from_name = get_model_config_from_name
    try:
        # Patching the import for the scope of this test
        globals()['get_model_config_from_name'] = mock_get_model_config_from_name

        logger.info("Testing XiaohongshuCoderAgent instantiation...")

        # Test instantiation via helper using mocked llm_config_name
        coder_test_llm_name = get_xiaohongshu_coder_agent(llm_config_name="coder_client_ollama_qwen3")
        logger.info(f"Agent '{coder_test_llm_name.name}' created using llm_config_name. LLM config: {coder_test_llm_name.llm_config}")

        # Test instantiation via helper using direct config_list
        example_config_list = [{
            "model": "test_model",
            "api_key": "test_key",
            "base_url": "http://localhost:1234/v1"
        }]
        coder_test_config_list = get_xiaohongshu_coder_agent(config_list=example_config_list)
        logger.info(f"Agent '{coder_test_config_list.name}' created using config_list. LLM config: {coder_test_config_list.llm_config}")

        # Test instantiation without LLM config
        coder_no_llm = get_xiaohongshu_coder_agent()
        logger.info(f"Agent '{coder_no_llm.name}' created without LLM config. LLM config: {coder_no_llm.llm_config}")

        # logger.info(f"System message for {coder.name}:\n{coder.system_message}")
        # logger.info(f"Registered functions for {coder.name}: {coder_test_llm_name._function_map.keys()}")

    except Exception as e:
        logger.error(f"Error during local testing of XiaohongshuCoderAgent: {e}", exc_info=True)
    finally:
        # Restore original import
        globals()['get_model_config_from_name'] = original_get_model_config_from_name

    logger.info("NOTE: Full functional test of tool usage requires LLM interaction and proper Magentic-UI environment.")

# Make agent available for import
__all__ = ["XiaohongshuCoderAgent", "get_xiaohongshu_coder_agent", "DEFAULT_XIAOHONGSHU_CODER_SYSTEM_MESSAGE"]
