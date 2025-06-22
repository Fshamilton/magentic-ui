import json
from typing import Annotated
from loguru import logger

class TextAnalysisTool:
    @staticmethod
    def extract_insights_from_crawled_data(crawled_json_string: Annotated[str, "JSON string from MediaCrawlerTool.search_hot_notes"]) -> Annotated[str, "A JSON string containing the extracted insights or an error message"]:
        """Extracts insights from crawled Xiaohongshu note data using an LLM.

        Args:
            crawled_json_string: The JSON string output from MediaCrawlerTool.search_hot_notes.

        Returns:
            A JSON string. Example:
            {"status": "success", "data": {"themes": ["DIY", "Budget-friendly"], "visual_styles": ["Bright", "Minimalist"], "keywords": ["#desksetup", "#homeoffice"], "tone": "Inspirational"}}
            or {"status": "error", "message": "Analysis failed"}.
        """
        logger.info(f"[TextAnalysisTool] Called extract_insights_from_crawled_data.")
        logger.debug(f"[TextAnalysisTool] Input crawled_json_string (first 100 chars): {crawled_json_string[:100]}...")

        try:
            crawled_data = json.loads(crawled_json_string)
            if crawled_data.get("status") == "error":
                result = json.dumps({"status": "error", "message": "Analysis failed: Input data indicates an error from crawler."})
                logger.warning(f"[TextAnalysisTool] Input data from crawler was an error: {crawled_data.get('message')}")
                return result
        except json.JSONDecodeError as e:
            result = json.dumps({"status": "error", "message": "Analysis failed: Invalid JSON input."})
            logger.error(f"[TextAnalysisTool] JSONDecodeError while parsing input: {e}. Input (first 100 chars): {crawled_json_string[:100]}...")
            return result

        # Placeholder implementation for LLM analysis
        # In a real scenario, this would involve formatting a prompt with the crawled_data
        # and sending it to an LLM (e.g., via an Autogen client).
        logger.debug("[TextAnalysisTool] Starting placeholder LLM analysis.")

        titles = []
        if crawled_data.get("data") and isinstance(crawled_data["data"], list):
            for item in crawled_data["data"]:
                if isinstance(item, dict) and "title" in item:
                    titles.append(item["title"])
        logger.debug(f"[TextAnalysisTool] Extracted {len(titles)} titles for analysis.")

        if not titles:
            insights_data = {
                "themes": ["General Topic", "Popular Content"],
                "visual_styles": ["Varied", "Engaging"],
                "keywords": ["#热门", "#小红书"],
                "tone": "Neutral"
            }
            logger.info("[TextAnalysisTool] No titles found in crawled data, returning default insights.")
        elif "error_topic" in titles[0] if titles else False:
            result = json.dumps({"status": "error", "message": "Analysis failed due to error topic from crawler"})
            logger.warning("[TextAnalysisTool] Analysis failed: 'error_topic' detected in titles.")
            return result
        else:
            topic_hint = titles[0].split(' - ')[0] if titles else 'Unknown'
            insights_data = {
                "themes": ["DIY Projects", "Budget-friendly Ideas", f"Theme based on '{topic_hint}'"],
                "visual_styles": ["Bright and Airy", "Minimalist Chic"],
                "keywords": ["#hashtag1", "#hashtag2", "#inspiration"],
                "tone": "Upbeat and Friendly"
            }
            logger.info(f"[TextAnalysisTool] Simulated insights generated for topic hint: '{topic_hint}'.")

        final_result = json.dumps({"status": "success", "data": insights_data})
        logger.info("[TextAnalysisTool] extract_insights_from_crawled_data completed successfully.")
        logger.debug(f"[TextAnalysisTool] Result: {final_result}")
        return final_result
