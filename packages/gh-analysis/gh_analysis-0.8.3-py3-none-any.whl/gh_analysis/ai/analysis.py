"""Core analysis logic for AI processing."""

import json
from typing import Any

from pydantic_ai import Agent
from pydantic_ai.messages import BinaryContent, ImageUrl

from .image_utils import load_downloaded_images


def prepare_issue_for_troubleshooting(
    issue_data: dict[str, Any], include_images: bool = True
) -> list[str | ImageUrl | BinaryContent]:
    """Prepare issue data for troubleshooting analysis.

    Args:
        issue_data: Issue data dictionary containing issue content
        include_images: Whether to include images in analysis

    Returns:
        List of message parts for PydanticAI troubleshooting agent
    """
    # Load images if requested
    image_contents = load_downloaded_images(issue_data, include_images)

    # Build text prompt using troubleshooting formatter
    text_prompt = format_troubleshooting_prompt(issue_data, len(image_contents))

    # Build message parts
    message_parts: list[str | ImageUrl | BinaryContent] = [text_prompt]

    # Add images as BinaryContent (works with all model providers)
    for img_content in image_contents:
        if img_content.get("type") == "binary_content":
            message_parts.append(
                BinaryContent(
                    data=img_content["data"], media_type=img_content["media_type"]
                )
            )
        elif img_content.get("type") == "image_url":
            # Legacy support for data URLs
            image_url = img_content["image_url"]["url"]
            if image_url.startswith("data:"):
                import base64

                header, data = image_url.split(",", 1)
                media_type = header.split(";")[0].split(":")[1]
                img_bytes = base64.b64decode(data)
                message_parts.append(
                    BinaryContent(data=img_bytes, media_type=media_type)
                )

    return message_parts


def prepare_issue_for_analysis(
    issue_data: dict[str, Any], include_images: bool = True
) -> list[str | ImageUrl | BinaryContent]:
    """Prepare issue data for AI analysis.

    Args:
        issue_data: Issue data dictionary containing issue content
        include_images: Whether to include images in analysis

    Returns:
        List of message parts for PydanticAI agent
    """
    # Load images if requested
    image_contents = load_downloaded_images(issue_data, include_images)

    # Build text prompt
    text_prompt = format_issue_prompt(issue_data, len(image_contents))

    # Build message parts
    message_parts: list[str | ImageUrl | BinaryContent] = [text_prompt]

    # Add images as BinaryContent (works with all model providers)
    for img_content in image_contents:
        if img_content.get("type") == "binary_content":
            message_parts.append(
                BinaryContent(
                    data=img_content["data"], media_type=img_content["media_type"]
                )
            )
        elif img_content.get("type") == "image_url":
            # Legacy support for data URLs
            image_url = img_content["image_url"]["url"]
            if image_url.startswith("data:"):
                import base64

                header, data = image_url.split(",", 1)
                media_type = header.split(";")[0].split(":")[1]
                img_bytes = base64.b64decode(data)
                message_parts.append(
                    BinaryContent(data=img_bytes, media_type=media_type)
                )
            else:
                message_parts.append(ImageUrl(url=image_url))

    return message_parts


def format_troubleshooting_prompt(
    issue_data: dict[str, Any], image_count: int = 0
) -> str:
    """Format issue data into a prompt for troubleshooting analysis.

    Uses the same compact formatting as exp03 for optimal agent parsing.

    Args:
        issue_data: Issue data dictionary
        image_count: Number of images included in analysis

    Returns:
        Formatted prompt string for troubleshooting
    """
    issue = issue_data["issue"]

    # Build context using exp03's simple format
    context = f"Title: {issue.get('title', 'No Title')}\nBody: {issue.get('body', 'No Body')}\n"

    if issue.get("comments"):
        context += "\nComments:\n"
        for comment in issue.get("comments", []):
            context += f"- {comment.get('body', '')}\n"

    # Add image context if needed (keep minimal)
    if image_count > 0:
        context += f"\n[{image_count} image(s) provided for analysis]\n"

    return f"**Problem Description:**\n{context}"


def format_issue_prompt(issue_data: dict[str, Any], image_count: int = 0) -> str:
    """Format issue data into a prompt for analysis.

    Args:
        issue_data: Issue data dictionary
        image_count: Number of images included in analysis

    Returns:
        Formatted prompt string
    """
    issue = issue_data["issue"]

    # Include all comments with full content
    comment_text = ""
    if issue.get("comments"):
        all_comments = issue.get("comments", [])
        comment_entries = []
        for comment in all_comments:
            user = comment.get("user", {}).get("login", "Unknown")
            body = comment.get("body", "").replace("\n", " ").strip()
            comment_entries.append(f"{user}: {body}")
        comment_text = " | ".join(comment_entries)

    # Add explicit image context instructions
    if image_count > 0:
        image_instruction = f"""

**IMAGES PROVIDED:** This issue contains {image_count} image(s) that you should analyze.
When analyzing the images, look for:
- UI screenshots showing specific product interfaces
- Error messages or logs that indicate which product is failing
- File browser views, admin consoles, or diagnostic outputs
- Any visual indicators of the affected product

IMPORTANT: Fill in the images_analyzed array with descriptions of what each image
shows and how it influences your classification. Fill in image_impact with how
the images affected your decision.
"""
    else:
        image_instruction = """

**NO IMAGES PROVIDED:** This issue contains no images to analyze.
IMPORTANT: Leave images_analyzed as an empty array and image_impact as an empty
string since no images were provided.
"""

    return f"""
Analyze this GitHub issue for product labeling:

**Title:** {issue.get("title", "No Title")}

**Body:** {issue.get("body", "No Body")}

**Current Labels:** {
        json.dumps(
            [
                label.get("name", "")
                for label in issue.get("labels", [])
                if label.get("name", "").startswith("product::")
            ],
            separators=(",", ":"),
        )
    }

**Repository:** {issue_data["org"]}/{issue_data["repo"]}

**Comments:** {comment_text or "No comments"}
{image_instruction}

Recommend the most appropriate product label(s) based on the issue content.
"""


async def analyze_troubleshooting_issue(
    agent: Agent[None, Any],
    issue_data: dict[str, Any],
    include_images: bool = True,
    model: str | None = None,
    model_settings: dict[str, Any] | None = None,
) -> Any:
    """Analyze a GitHub issue for troubleshooting using the provided agent.

    Args:
        agent: PydanticAI troubleshooting agent to use for analysis
        issue_data: Issue data dictionary
        include_images: Whether to include images in analysis
        model: Optional model override
        model_settings: Optional model settings override

    Returns:
        Agent response data

    Raises:
        Exception: If analysis fails
    """
    message_parts = prepare_issue_for_troubleshooting(issue_data, include_images)

    try:
        # Run with optional overrides and usage limits for complex troubleshooting
        kwargs: dict[str, Any] = {}
        if model:
            kwargs["model"] = model
        if model_settings:
            kwargs["model_settings"] = model_settings

        # Set higher usage limits for complex troubleshooting analysis
        from pydantic_ai.usage import UsageLimits

        kwargs["usage_limits"] = UsageLimits(request_limit=150)

        result = await agent.run(message_parts, **kwargs)
        return result.output
    except Exception as e:
        print(f"DEBUG: Exception caught in analyze_troubleshooting_issue: {e}")
        print(f"DEBUG: Exception type: {type(e)}")
        if hasattr(e, "__cause__") and e.__cause__:
            print(f"DEBUG: Exception cause: {e.__cause__}")

        # If multimodal fails and we have images, try text-only as fallback
        if include_images and len(message_parts) > 1:
            print(f"Multimodal processing failed, falling back to text-only: {e}")
            # Try again with just the text prompt
            text_only = [message_parts[0]]
            result = await agent.run(text_only, **kwargs)
            return result.output
        else:
            raise


async def analyze_issue(
    agent: Agent[None, Any],
    issue_data: dict[str, Any],
    include_images: bool = True,
    model: str | None = None,
    model_settings: dict[str, Any] | None = None,
) -> Any:
    """Analyze a GitHub issue using the provided agent.

    Args:
        agent: PydanticAI agent to use for analysis
        issue_data: Issue data dictionary
        include_images: Whether to include images in analysis
        model: Optional model override
        model_settings: Optional model settings override

    Returns:
        Agent response data

    Raises:
        Exception: If analysis fails
    """
    message_parts = prepare_issue_for_analysis(issue_data, include_images)

    try:
        # Run with optional overrides
        kwargs: dict[str, Any] = {}
        if model:
            kwargs["model"] = model
        if model_settings:
            kwargs["model_settings"] = model_settings

        result = await agent.run(message_parts, **kwargs)
        return result.output
    except Exception as e:
        # If multimodal fails and we have images, try text-only as fallback
        if include_images and len(message_parts) > 1:
            print(f"Multimodal processing failed, falling back to text-only: {e}")
            fallback_prompt = format_issue_prompt(issue_data, 0)
            result = await agent.run(fallback_prompt, **kwargs)
            return result.output
        else:
            # Re-raise if not image-related
            raise
