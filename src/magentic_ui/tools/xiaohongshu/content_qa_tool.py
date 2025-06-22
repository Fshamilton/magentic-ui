import json
from typing import Annotated, Dict, List
from loguru import logger

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
        logger.info(f"[ContentQATool] Called evaluate_aesthetics for image_url: '{image_url}'.")
        if not image_url:
            result = json.dumps({"status": "error", "message": "Aesthetic evaluation failed: Missing image URL."})
            logger.warning("[ContentQATool] evaluate_aesthetics failed due to missing image_url.")
            return result

        # Placeholder for HumanAesExpert or similar tool
        score = 8.0
        feedback = "Looks good! Colors are vibrant and composition is balanced."
        if "picsum.photos" not in image_url:
            score = 4.0
            feedback = "Image URL might not be from a standard source, quality uncertain."
            logger.debug(f"[ContentQATool] Image URL '{image_url}' not from picsum.photos, assigned lower score.")
        elif "fail_image_generation" in image_url:
            score = 2.0
            feedback = "Image generation failed, so aesthetics cannot be properly evaluated."
            logger.debug(f"[ContentQATool] 'fail_image_generation' in URL '{image_url}', aesthetics evaluation impacted.")
        elif len(image_url) % 2 == 0:
            score = 6.5
            feedback = "Decent, but could be improved. Consider adjusting brightness."
            logger.debug(f"[ContentQATool] Image URL '{image_url}' has even length, varied feedback given.")

        if "error_eval" in image_url:
            result = json.dumps({"status": "error", "message": "Aesthetic evaluation failed: Simulated tool error."})
            logger.warning(f"[ContentQATool] evaluate_aesthetics simulated tool error for image_url: '{image_url}'.")
            return result

        final_result_data = {"score": score, "feedback": feedback}
        final_result = json.dumps({"status": "success", "data": final_result_data})
        logger.info(f"[ContentQATool] evaluate_aesthetics completed for '{image_url}'. Score: {score}.")
        logger.debug(f"[ContentQATool] Evaluation result: {final_result_data}")
        return final_result

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
        logger.info(f"[ContentQATool] Called check_text_compliance.")
        logger.debug(f"[ContentQATool] Args: text_content_keys='{list(text_content.keys()) if isinstance(text_content, dict) else 'N/A'}', rules={rules}")

        if not text_content or not isinstance(text_content, dict):
            result = json.dumps({"status": "error", "message": "Text compliance check failed: Invalid text_content."})
            logger.warning(f"[ContentQATool] check_text_compliance failed due to invalid text_content type: {type(text_content)}.")
            return result

        issues: List[str] = []
        body = text_content.get("body", "")
        title = text_content.get("title", "")
        logger.debug(f"[ContentQATool] Text content - Title (first 30 chars): '{title[:30]}...', Body (first 50 chars): '{body[:50]}...'")

        min_length_body = rules.get("min_length_body")
        if min_length_body is not None and isinstance(min_length_body, int):
            if len(body) < min_length_body:
                issue_msg = f"Body too short. Expected at least {min_length_body} characters, got {len(body)}."
                issues.append(issue_msg)
                logger.debug(f"[ContentQATool] Compliance issue: {issue_msg}")

        must_include_keywords: List[str] = rules.get("must_include_keywords", [])
        if must_include_keywords and isinstance(must_include_keywords, list):
            for keyword in must_include_keywords:
                if keyword.lower() not in body.lower() and keyword.lower() not in title.lower():
                    issue_msg = f"Missing required keyword: {keyword}"
                    issues.append(issue_msg)
                    logger.debug(f"[ContentQATool] Compliance issue: {issue_msg}")

        if rules.get("simulate_tool_error"):
            result = json.dumps({"status": "error", "message": "Text compliance check failed: Simulated tool error"})
            logger.warning("[ContentQATool] check_text_compliance simulated tool error.")
            return result

        passed = not bool(issues)
        final_result_data = {"passed": passed, "issues": issues}
        final_result = json.dumps({"status": "success", "data": final_result_data})

        logger.info(f"[ContentQATool] check_text_compliance completed. Passed: {passed}. Issues: {issues if issues else 'None'}.")
        logger.debug(f"[ContentQATool] Compliance check result: {final_result_data}")
        return final_result
