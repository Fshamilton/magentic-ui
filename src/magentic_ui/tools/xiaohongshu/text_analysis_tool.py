import json
from typing import Annotated

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
        print(f"[TextAnalysisTool] Extracting insights from: {crawled_json_string[:100]}...")
        try:
            crawled_data = json.loads(crawled_json_string)
            if crawled_data.get("status") == "error":
                return json.dumps({"status": "error", "message": "Analysis failed: Input data indicates an error from crawler."})
        except json.JSONDecodeError:
            return json.dumps({"status": "error", "message": "Analysis failed: Invalid JSON input."})

        # Placeholder implementation for LLM analysis
        # In a real scenario, this would involve formatting a prompt with the crawled_data
        # and sending it to an LLM (e.g., via an Autogen client).

        # Simulate LLM analysis based on input data
        # This is a very simplified simulation
        titles = []
        if crawled_data.get("data") and isinstance(crawled_data["data"], list):
            for item in crawled_data["data"]:
                if isinstance(item, dict) and "title" in item:
                    titles.append(item["title"])

        if not titles:
            # Default insights if no titles found or data is not as expected
             insights_data = {
                "themes": ["General Topic", "Popular Content"],
                "visual_styles": ["Varied", "Engaging"],
                "keywords": ["#热门", "#小红书"],
                "tone": "Neutral"
            }
        elif "error_topic" in titles[0] if titles else False: # check if it's an error topic based on crawler's input
            return json.dumps({"status": "error", "message": "Analysis failed due to error topic from crawler"})
        else: # Simulate some insights
            insights_data = {
                "themes": ["DIY Projects", "Budget-friendly Ideas", f"Theme based on '{titles[0].split(' - ')[0] if titles else 'Unknown'}'"],
                "visual_styles": ["Bright and Airy", "Minimalist Chic"],
                "keywords": ["#hashtag1", "#hashtag2", "#inspiration"],
                "tone": "Upbeat and Friendly"
            }

        return json.dumps({"status": "success", "data": insights_data})
