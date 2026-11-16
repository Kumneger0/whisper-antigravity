"""Extract and format spoken summaries from Antigravity task completions."""

import json
import os
from pathlib import Path
import re
from typing import Any, Dict, Optional


def extract_voice_tag(text: str) -> Optional[str]:
    """Extract debrief from <!-- voice-briefing: ... --> or <voice-briefing> tags."""
    if not text:
        return None

    # Match <!-- voice-briefing: ... --> or <!-- voice: ... -->
    comment_pattern = r"<!--\s*(?:voice-briefing|voice_briefing|voice)\s*:\s*([\s\S]*?)\s*-->"
    match = re.search(comment_pattern, text, re.IGNORECASE)
    if match:
        clean = match.group(1).strip()
        if clean:
            return clean

    # Match <voice-briefing>...</voice-briefing>
    tag_pattern = r"<\s*(?:voice-briefing|voice_briefing)\s*>([\s\S]*?)<\s*/\s*(?:voice-briefing|voice_briefing)\s*>"
    match = re.search(tag_pattern, text, re.IGNORECASE)
    if match:
        clean = match.group(1).strip()
        if clean:
            return clean

    return None


def clean_markdown_for_speech(text: str) -> str:
    """Sanitize markdown text into natural spoken English."""
    if not text:
        return ""

    # Remove HTML comments
    text = re.sub(r"<!--[\s\S]*?-->", "", text)

    # Remove code blocks (fenced by ``` or ````)
    text = re.sub(r"```[\s\S]*?```", "", text)
    text = re.sub(r"````[\s\S]*?````", "", text)

    # Remove image links: ![alt](url)
    text = re.sub(r"!\[([^\]]*)\]\([^\)]+\)", "", text)

    # Convert markdown links: [label](url) -> label
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)

    # Remove inline code backticks: `code` -> code
    text = re.sub(r"`([^`]+)`", r"\1", text)

    # Remove markdown tables (| col | col |)
    text = re.sub(r"\|[^\n]+\|", "", text)

    # Remove blockquotes marker (> ...)
    text = re.sub(r"^\s*>\s*", "", text, flags=re.MULTILINE)

    # Remove markdown headers (# Title)
    text = re.sub(r"^\s*#{1,6}\s+", "", text, flags=re.MULTILINE)

    # Remove bold and italic markers: **bold**, *italic*, __bold__, _italic_
    text = re.sub(r"\*\*([^\*]+)\*\*", r"\1", text)
    text = re.sub(r"\*([^\*]+)\*", r"\1", text)
    text = re.sub(r"__([^_]+)__", r"\1", text)
    text = re.sub(r"_([^_]+)_", r"\1", text)

    # Remove list bullet markers (-, *, +, 1.)
    text = re.sub(r"^\s*[\-\*\+]\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*\d+\.\s+", "", text, flags=re.MULTILINE)

    # Remove HTML tags
    text = re.sub(r"<[^>]+>", "", text)

    # Clean whitespace and repeated newlines
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    cleaned = " ".join(lines)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    return cleaned


def extract_key_sentences(text: str, max_sentences: int = 2) -> str:
    """Extract the first 1-2 key sentences from sanitized text."""
    if not text:
        return ""

    # Split into sentences
    sentences = re.split(r"(?<=[.!?])\s+", text)
    meaningful = [s.strip() for s in sentences if len(s.strip()) > 8]

    if not meaningful:
        return text[:150]

    selected = meaningful[:max_sentences]
    summary = " ".join(selected)

    # Cap length to avoid over-talking
    if len(summary) > 300:
        summary = summary[:297].rstrip() + "..."

    return summary


def get_last_assistant_message(transcript_path: Path) -> Optional[str]:
    """Parse transcript.jsonl and find the content of the last model response."""
    if not transcript_path.is_file():
        return None

    last_content = None
    try:
        with open(transcript_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    step = json.loads(line)
                    # Look for model responses or planner responses
                    step_type = step.get("type", "")
                    source = step.get("source", "")
                    content = step.get("content", "")

                    if (step_type == "PLANNER_RESPONSE" or source == "MODEL") and content:
                        last_content = content
                except json.JSONDecodeError:
                    continue
    except Exception:
        return None

    return last_content


def get_walkthrough_summary(artifact_dir: Path) -> Optional[str]:
    """Check for walkthrough.md in artifact directory and extract summary."""
    walkthrough_file = artifact_dir / "walkthrough.md"
    if not walkthrough_file.is_file():
        return None

    try:
        content = walkthrough_file.read_text(encoding="utf-8")
        tag = extract_voice_tag(content)
        if tag:
            return tag

        cleaned = clean_markdown_for_speech(content)
        if cleaned:
            return extract_key_sentences(cleaned, max_sentences=2)
    except Exception:
        pass

    return None


def generate_summary(payload: Dict[str, Any]) -> str:
    """
    Generate spoken debrief from Stop hook payload.
    Prioritizes Antigravity's self-generated voice-briefing comment,
    with smart fallback to walkthrough and transcript parsing.
    """
    error = payload.get("error", "")
    termination_reason = payload.get("terminationReason", "")

    # Handle error cases verbally
    if error or termination_reason == "error":
        error_msg = clean_markdown_for_speech(str(error)) if error else "Execution stopped with an error."
        if len(error_msg) > 150:
            error_msg = error_msg[:147] + "..."
        return f"Hey, heads up: we ran into an issue on that task. {error_msg}"

    # Check transcriptPath for self-generated voice tag
    transcript_path_str = payload.get("transcriptPath")
    if transcript_path_str:
        transcript_path = Path(os.path.expanduser(transcript_path_str))
        last_message = get_last_assistant_message(transcript_path)
        if last_message:
            tag = extract_voice_tag(last_message)
            if tag:
                return tag

    # Check walkthrough.md in artifactDirectoryPath
    artifact_dir_str = payload.get("artifactDirectoryPath")
    if artifact_dir_str:
        artifact_dir = Path(os.path.expanduser(artifact_dir_str))
        walkthrough_summary = get_walkthrough_summary(artifact_dir)
        if walkthrough_summary:
            return f"All done! {walkthrough_summary}"

    # Fallback to cleaning the last assistant message
    if transcript_path_str:
        transcript_path = Path(os.path.expanduser(transcript_path_str))
        last_message = get_last_assistant_message(transcript_path)
        if last_message:
            cleaned = clean_markdown_for_speech(last_message)
            summary = extract_key_sentences(cleaned, max_sentences=2)
            if summary:
                return f"All done! {summary}"

    # Ultimate fallback if nothing could be read
    last_user_input = payload.get("lastUserInput", "").strip()
    if last_user_input:
        cleaned_input = clean_markdown_for_speech(last_user_input)
        if len(cleaned_input) > 60:
            cleaned_input = cleaned_input[:57] + "..."
        return f"Hey! I've finished working on: {cleaned_input}."

    return "Hey! I've finished the task."
