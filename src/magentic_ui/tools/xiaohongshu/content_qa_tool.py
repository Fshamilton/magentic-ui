import json
from typing import Annotated, Dict, List

class ContentQATool:
    @staticmethod
    def evaluate_aesthetics(image_url: Annotated[str, "URL of the generated image"]) -> Annotated[str, "A JSON string containing the aesthetic evaluation or an error message"]:
        """Evaluates the aesthetics of a generated image.

        Args:
            image_url: The URL of the image to evaluate.

        Returns:
            A JSON string. Example:
            {"status": "success", "data": {"score": 8.5, "feedback": "Good composition."}}
            or {"status": "error", "message": "Aesthetic evaluation failed"}.
        """
        print(f"[ContentQATool] Evaluating aesthetics for image: {image_url}")
        if not image_url:
            return json.dumps({"status": "error", "message": "Aesthetic evaluation failed: Missing image URL."})

        # Placeholder for HumanAesExpert or similar tool
        # Simulate score based on URL for testing
        score = 8.0
        feedback = "Looks good! Colors are vibrant and composition is balanced."
        if "picsum.photos" not in image_url: # Basic check
            score = 4.0
            feedback = "Image URL might not be from a standard source, quality uncertain."
        elif "fail_image_generation" in image_url: # if the image itself was a fail
            score = 2.0
            feedback = "Image generation failed, so aesthetics cannot be properly evaluated."
        elif len(image_url) % 2 == 0: # Arbitrary condition for varied feedback
            score = 6.5
            feedback = "Decent, but could be improved. Consider adjusting brightness."

        if "error_eval" in image_url:
             return json.dumps({"status": "error", "message": "Aesthetic evaluation failed: Simulated tool error."})

        return json.dumps({"status": "success", "data": {"score": score, "feedback": feedback}})

    @staticmethod
    def check_text_compliance(text_content: Annotated[Dict[str, str], "Generated text, e.g., {'title': '...', 'body': '...'}"],
                              rules: Annotated[Dict, "Compliance rules, e.g., {'min_length_body': 50, 'must_include_keywords': ['#DIY']}"],) -> Annotated[str, "A JSON string containing compliance check results or an error message"]:
        """Checks generated text for compliance with basic rules.

        Args:
            text_content: A dictionary containing the generated text (e.g., {"title": "...", "body": "..."}).
            rules: A dictionary of simple rules (e.g., {"min_length_body": 50, "must_include_keywords": ["#DIY"]}).

        Returns:
            A JSON string. Example:
            {"status": "success", "data": {"passed": true, "issues": []}}
            or {"status": "success", "data": {"passed": false, "issues": ["Body too short"]}}.
        """
        print(f"[ContentQATool] Checking text compliance. Title: {text_content.get('title')[:30]}... Rules: {rules}")
        if not text_content or not isinstance(text_content, dict):
            return json.dumps({"status": "error", "message": "Text compliance check failed: Invalid text_content."})

        issues: List[str] = []
        body = text_content.get("body", "")
        title = text_content.get("title", "")

        min_length_body = rules.get("min_length_body")
        if min_length_body is not None and isinstance(min_length_body, int):
            if len(body) < min_length_body:
                issues.append(f"Body too short. Expected at least {min_length_body} characters, got {len(body)}.")

        must_include_keywords: List[str] = rules.get("must_include_keywords", [])
        if must_include_keywords and isinstance(must_include_keywords, list):
            for keyword in must_include_keywords:
                if keyword.lower() not in body.lower() and keyword.lower() not in title.lower():
                    issues.append(f"Missing required keyword: {keyword}")

        # Simulate an error condition for the tool itself
        if rules.get("simulate_tool_error"):
            return json.dumps({"status": "error", "message": "Text compliance check failed: Simulated tool error"})

        passed = not bool(issues)
        return json.dumps({"status": "success", "data": {"passed": passed, "issues": issues}})
