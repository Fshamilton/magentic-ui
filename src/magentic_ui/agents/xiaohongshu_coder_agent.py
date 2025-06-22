import autogen
from typing import Optional, Callable, Dict, Any
from magentic_ui.tools.xiaohongshu import (
    MediaCrawlerTool,
    TextAnalysisTool,
    ContentGenerationTool,
    ContentQATool,
)
from magentic_ui.config_manager import get_model_config_from_name,MagenticUIConfig # Changed from 近_MODEL_CONFIG_TYPE

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
        llm_config: Optional[MagenticUIConfig] = None, # Changed from 近_MODEL_CONFIG_TYPE
        **kwargs,
    ):
        super().__init__(
            name=name,
            system_message=system_message,
            llm_config=llm_config,
            **kwargs,
        )

        # Register tools
        self.register_function(
            function_map={
                "search_hot_notes": MediaCrawlerTool.search_hot_notes,
                "extract_insights_from_crawled_data": TextAnalysisTool.extract_insights_from_crawled_data,
                "generate_text": ContentGenerationTool.generate_text,
                "generate_image": ContentGenerationTool.generate_image,
                "evaluate_aesthetics": ContentQATool.evaluate_aesthetics,
                "check_text_compliance": ContentQATool.check_text_compliance,
            }
        )

def get_xiaohongshu_coder_agent(
    name_suffix: str = "",
    llm_config_name: Optional[str] = None,
    config_list: Optional[list] = None, # Added for flexibility if passing raw config_list
    custom_system_message: Optional[str] = None
) -> XiaohongshuCoderAgent:
    """Helper function to create and configure a XiaohongshuCoderAgent."""
    agent_name = f"XiaohongshuCoder{name_suffix}"

    final_llm_config = False # Default to no LLM / human input

    if llm_config_name:
        # This assumes get_model_config_from_name returns a dict compatible with autogen's llm_config
        # Or it returns a list of such dicts (config_list)
        # Based on Magentic-UI's config_manager, it returns a dict for a single model,
        # or a list if multiple models are under that name (though typically it's one).
        # Autogen expects llm_config to be a dict or list of dicts.
        raw_config = get_model_config_from_name(llm_config_name)
        if raw_config:
            # Autogen's llm_config usually expects a list of model configs.
            # If get_model_config_from_name returns a single dict, wrap it in a list.
            if isinstance(raw_config, dict) and "model" in raw_config:
                 final_llm_config = [raw_config]
            elif isinstance(raw_config, list):
                 final_llm_config = raw_config
            else:
                print(f"Warning: LLM config '{llm_config_name}' from get_model_config_from_name was not in expected format (dict or list). Type: {type(raw_config)}")
        else:
            print(f"Warning: LLM config '{llm_config_name}' not found or empty.")

    if config_list: # If a raw config_list is provided, it takes precedence or can be a fallback
        if isinstance(config_list, list) and all(isinstance(item, dict) for item in config_list):
            final_llm_config = config_list
        elif isinstance(config_list, dict) and "model" in config_list: # Handle single model dict case
            final_llm_config = [config_list]
        else:
            print(f"Warning: Provided config_list is not in the expected format (list of dicts or a single model dict).")


    sys_msg = custom_system_message if custom_system_message else DEFAULT_XIAOHONGSHU_CODER_SYSTEM_MESSAGE

    agent = XiaohongshuCoderAgent(
        name=agent_name,
        llm_config=final_llm_config,
        system_message=sys_msg,
        human_input_mode="NEVER",
        code_execution_config=False,
    )
    return agent

# Example of how this might be used (for testing purposes, not part of the agent file itself)
if __name__ == '__main__':
    # This part is for local testing of the agent class if run directly.
    # It requires a config.json or similar for autogen to load model configs.
    # For example, create an OAI_CONFIG_LIST.json in this directory:
    # [
    #   {
    #     "model": "gpt-3.5-turbo",
    #     "api_key": "YOUR_API_KEY"
    #   }
    # ]
    # And set environment variable OAI_CONFIG_LIST="OAI_CONFIG_LIST.json"

    # Or, more aligned with Magentic-UI, you'd load from its config structure.
    # The `get_model_config_from_name` is meant to handle that.
    # For a standalone test, we might mock it or provide a simple config_list.

    print("Testing XiaohongshuCoderAgent instantiation...")
    try:
        # Attempt to create with a placeholder config if MagenticUI's config isn't fully available in this context
        # In a real run, MagenticUI's config loading would provide this.
        example_config_list = [{
            "model": "ollama/qwen3", # Example, adjust to your actual model string for ollama via LiteLLM/OpenAI proxy
            "api_key": "ollama",
            "base_url": "http://localhost:11434/v1"
        }]

        # Test instantiation via helper
        coder = get_xiaohongshu_coder_agent(llm_config_name="coder_client", config_list=example_config_list) # Assuming "coder_client" is a key in your magentic_ui config
        print(f"Agent '{coder.name}' created successfully with system message:")
        print(coder.system_message)
        print("\\nRegistered functions:")
        # print(coder._function_map) # Accessing protected member for debug

        # Test direct instantiation
        # coder_direct = XiaohongshuCoderAgent(name="TestCoderDirect", llm_config=example_config_list)
        # print(f"Agent '{coder_direct.name}' created successfully.")

        # Simulate a message to see if it tries to use a tool (requires LLM call)
        # This part would typically be orchestrated by a GroupChat or another agent.
        # response = coder.generate_reply(messages=[{"role": "user", "content": "Please search for 'DIY makeup' notes."}])
        # print(f"Simulated response: {response}")

    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()

    print("\\nNOTE: Full functional test of tool usage requires LLM interaction and proper configuration.")

# Make agent available for import
__all__ = ["XiaohongshuCoderAgent", "get_xiaohongshu_coder_agent", "DEFAULT_XIAOHONGSHU_CODER_SYSTEM_MESSAGE"]
