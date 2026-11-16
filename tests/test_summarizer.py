"""Unit tests for whisper_antigravity.summarizer."""

import json
from pathlib import Path
import pytest

from whisper_antigravity import summarizer


def test_extract_voice_tag():
    text_with_comment = (
        "Here are the changes I made to your project:\n"
        "- Fixed bug in auth.py\n"
        "<!-- voice-briefing: Hey, I fixed the authentication error and tests pass! -->\n"
    )
    tag = summarizer.extract_voice_tag(text_with_comment)
    assert tag == "Hey, I fixed the authentication error and tests pass!"

    text_with_tag = "<voice-briefing>All done! Everything looks clean.</voice-briefing>"
    assert summarizer.extract_voice_tag(text_with_tag) == "All done! Everything looks clean."

    assert summarizer.extract_voice_tag("Just regular text") is None


def test_clean_markdown_for_speech():
    markdown = """# Release Notes
Here is the fix for [`calculate_tax`](file:///path/to/tax.py#L10):
```python
def calculate_tax(amount):
    return amount * 0.15
```
> Note: this is **important** for *billing*!

Check the [docs link](https://example.com) for details.
| Column A | Column B |
| --- | --- |
| val1 | val2 |

- First item
- Second item
"""
    cleaned = summarizer.clean_markdown_for_speech(markdown)
    assert "```" not in cleaned
    assert "def calculate_tax" not in cleaned
    assert "file:///" not in cleaned
    assert "https://example.com" not in cleaned
    assert "docs link" in cleaned
    assert "important for billing" in cleaned
    assert "#" not in cleaned
    assert "|" not in cleaned


def test_generate_summary_with_voice_tag(tmp_path):
    transcript_file = tmp_path / "transcript.jsonl"
    step1 = {"type": "USER_INPUT", "source": "USER", "content": "Fix the broken login"}
    step2 = {
        "type": "PLANNER_RESPONSE",
        "source": "MODEL",
        "content": (
            "I have investigated and fixed the login issue.\n"
            "<!-- voice-briefing: All fixed! The login redirect issue has been solved and verified. -->"
        ),
    }
    with open(transcript_file, "w") as f:
        f.write(json.dumps(step1) + "\n")
        f.write(json.dumps(step2) + "\n")

    payload = {
        "fullyIdle": True,
        "terminationReason": "model_stop",
        "error": "",
        "transcriptPath": str(transcript_file),
    }

    summary = summarizer.generate_summary(payload)
    assert summary == "All fixed! The login redirect issue has been solved and verified."


def test_generate_summary_error():
    payload = {
        "fullyIdle": True,
        "terminationReason": "error",
        "error": "Failed to compile: syntax error in main.go:14",
    }
    summary = summarizer.generate_summary(payload)
    assert "heads up" in summary.lower()
    assert "Failed to compile" in summary


def test_generate_summary_fallback_without_tag(tmp_path):
    transcript_file = tmp_path / "transcript.jsonl"
    step = {
        "type": "PLANNER_RESPONSE",
        "source": "MODEL",
        "content": "I successfully refactored the database connection pool. All 12 integration tests passed without issues.",
    }
    with open(transcript_file, "w") as f:
        f.write(json.dumps(step) + "\n")

    payload = {
        "fullyIdle": True,
        "terminationReason": "model_stop",
        "error": "",
        "transcriptPath": str(transcript_file),
    }

    summary = summarizer.generate_summary(payload)
    assert "All done!" in summary
    assert "refactored the database connection pool" in summary
