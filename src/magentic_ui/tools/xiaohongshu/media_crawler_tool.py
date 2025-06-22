import json
from typing import Annotated
from loguru import logger

class MediaCrawlerTool:
    @staticmethod
    def search_hot_notes(topic: Annotated[str, "The search topic for Xiaohongshu notes"],
                         count: Annotated[int, "The number of notes to retrieve"] = 5) -> Annotated[str, "A JSON string containing the search results or an error message"]:
        """Searches for hot Xiaohongshu notes related to a given topic.

        Args:
            topic: The search topic.
            count: The number of popular notes to retrieve (e.g., top N, N=5-10).

        Returns:
            A JSON string. Example:
            {"status": "success", "data": [{"id": "...", "title": "...", "likes": 123, "summary": "...", "visual_desc": "..."}, ...]}
            or {"status": "error", "message": "Crawling failed: [reason]"}.
        """
        logger.info(f"[MediaCrawlerTool] Called search_hot_notes with topic: '{topic}', count: {count}")
        # Placeholder implementation
        # In a real scenario, this would interact with a MediaCrawler library/script.
        # print(f"[MediaCrawlerTool] Searching for {count} hot notes on topic: {topic}") # Replaced by logger
        if topic == "error_topic":
            result = json.dumps({"status": "error", "message": "Crawling failed: Simulated error"})
            logger.warning(f"[MediaCrawlerTool] search_hot_notes returning error for topic '{topic}': {result}")
            return result

        sample_data = []
        for i in range(count):
            sample_data.append({
                "id": f"note_{i+1}",
                "title": f"{topic} - Hot Note Title {i+1}",
                "likes": 100 + i * 10,
                "summary": f"This is a summary for hot note {i+1} about {topic}. It's very popular!",
                "visual_desc": f"Visual description for note {i+1}: bright colors, aesthetic layout."
            })

        result = json.dumps({"status": "success", "data": sample_data})
        logger.info(f"[MediaCrawlerTool] search_hot_notes successfully processed topic '{topic}'. Returning {len(sample_data)} notes.")
        logger.debug(f"[MediaCrawlerTool] search_hot_notes result for '{topic}': {result[:200]}...") # Log a snippet of the result
        return result
