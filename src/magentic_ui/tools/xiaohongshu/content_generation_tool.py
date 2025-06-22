import json
from typing import Annotated, List

class ContentGenerationTool:
    @staticmethod
    def generate_text(title_suggestion: Annotated[str, "Suggestion for the note title"],
                      key_points: Annotated[List[str], "Key points to be covered in the body"],
                      persona: Annotated[str, "The desired persona for writing"],
                      tone: Annotated[str, "The desired tone of the note"],
                      target_platform: Annotated[str, "Target platform, e.g., Xiaohongshu"] = "Xiaohongshu") -> Annotated[str, "A JSON string containing the generated text or an error message"]:
        """Generates Xiaohongshu note copy (title and body) using an LLM.

        Args:
            title_suggestion: Suggestion for the note title from Orchestrator's brief.
            key_points: Core message/angles, key points to cover in the body.
            persona: Desired writing persona.
            tone: Desired writing tone.
            target_platform: Target platform (default is Xiaohongshu).

        Returns:
            A JSON string. Example:
            {"status": "success", "data": {"title": "Generated Title", "body": "Generated body text..."}}
            or {"status": "error", "message": "Text generation failed"}.
        """
        print(f"[ContentGenerationTool] Generating text for {target_platform} with title suggestion: '{title_suggestion}'")
        print(f"[ContentGenerationTool] Key points: {key_points}, Persona: {persona}, Tone: {tone}")

        if not title_suggestion or not key_points:
            return json.dumps({"status": "error", "message": "Text generation failed: Missing title suggestion or key points."})

        # Placeholder for LLM text generation
        generated_title = f"✨ {title_suggestion} - {tone} & {persona} ✨"
        generated_body = f"Hey 小红薯们! 🍠 今天给大家分享关于 '{title_suggestion}' 的小技巧!\\n"
        for i, point in enumerate(key_points):
            generated_body += f"\\n पॉइंट {i+1}: {point} 😉"
        generated_body += f"\\n\\n希望这篇笔记对你有帮助哦! 记得点赞收藏评论呀 ❤️\\n#{target_platform} #{persona} #{tone}"

        return json.dumps({
            "status": "success",
            "data": {"title": generated_title, "body": generated_body}
        })

    @staticmethod
    def generate_image(prompt: Annotated[str, "Visual concept prompt for image generation"],
                       style_hints: Annotated[str, "Optional style hints for the image"] = None,
                       aspect_ratio: Annotated[str, "Desired aspect ratio, e.g., 3:4"] = "3:4") -> Annotated[str, "A JSON string containing the image URL or an error message"]:
        """Generates an image using an image generation API.

        Args:
            prompt: Visual concept prompt from Orchestrator's brief.
            style_hints: Optional style hints.
            aspect_ratio: Desired aspect ratio.

        Returns:
            A JSON string. Example:
            {"status": "success", "data": {"image_url": "http://...", "alt_text_suggestion": "A bright desk setup..."}}
            or {"status": "error", "message": "Image generation failed"}.
        """
        print(f"[ContentGenerationTool] Generating image with prompt: '{prompt}'")
        print(f"[ContentGenerationTool] Style: {style_hints}, Aspect Ratio: {aspect_ratio}")

        if not prompt:
            return json.dumps({"status": "error", "message": "Image generation failed: Missing prompt."})

        # Placeholder for image generation API call
        # Simulate different outputs based on prompt for testing
        image_url = f"https://picsum.photos/seed/{prompt.replace(' ','_')}/600/800" # Using picsum for placeholder
        alt_text = f"A generated image representing: {prompt}. Style: {style_hints if style_hints else 'default'}. Aspect ratio: {aspect_ratio}."

        if "fail_image_generation" in prompt:
            return json.dumps({"status": "error", "message": "Image generation failed: Simulated API error"})

        return json.dumps({
            "status": "success",
            "data": {"image_url": image_url, "alt_text_suggestion": alt_text}
        })
