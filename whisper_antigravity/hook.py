"""Hook handler for Antigravity's Stop lifecycle event."""

import json
import sys
from typing import Any, Dict

from .config import is_enabled, get_setting
from .summarizer import generate_summary
from .tts import speak_text


def run_hook() -> None:
    """Execute Stop hook processing incoming JSON payload from stdin."""
    # Fast path: If disabled, exit immediately with empty response
    if not is_enabled():
        sys.stdout.write("{}\n")
        sys.stdout.flush()
        return

    try:
        raw_input = sys.stdin.read()
        if not raw_input.strip():
            return

        payload: Dict[str, Any] = json.loads(raw_input)

        # Only speak when all background tasks are fully finished
        fully_idle = payload.get("fullyIdle", True)
        if not fully_idle:
            return

        # Check if errors should be announced
        error = payload.get("error")
        termination_reason = payload.get("terminationReason")
        is_error = bool(error or termination_reason == "error")

        if is_error and not get_setting("announce_errors", True):
            return

        # Generate conversational summary
        summary = generate_summary(payload)

        # Speak in the background so Antigravity hook returns instantly
        speak_text(summary, background=True)

    except Exception:
        # Never fail or crash Antigravity's loop
        pass
    finally:
        sys.stdout.write("{}\n")
        sys.stdout.flush()


if __name__ == "__main__":
    run_hook()
