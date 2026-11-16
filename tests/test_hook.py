"""Unit tests for whisper_antigravity.hook."""

import io
import json
import sys
from whisper_antigravity import hook, config


def test_hook_disabled(monkeypatch, tmp_path):
    monkeypatch.setenv("WHISPER_ANTIGRAVITY_CONFIG_DIR", str(tmp_path))
    config.set_enabled(False)

    fake_stdin = io.StringIO(json.dumps({"fullyIdle": True, "terminationReason": "model_stop"}))
    fake_stdout = io.StringIO()

    monkeypatch.setattr(sys, "stdin", fake_stdin)
    monkeypatch.setattr(sys, "stdout", fake_stdout)

    hook.run_hook()

    output = fake_stdout.getvalue().strip()
    assert output == "{}"


def test_hook_not_fully_idle(monkeypatch, tmp_path):
    monkeypatch.setenv("WHISPER_ANTIGRAVITY_CONFIG_DIR", str(tmp_path))
    config.set_enabled(True)

    # When background tasks are still running, fullyIdle is False
    fake_stdin = io.StringIO(json.dumps({"fullyIdle": False, "terminationReason": "model_stop"}))
    fake_stdout = io.StringIO()

    monkeypatch.setattr(sys, "stdin", fake_stdin)
    monkeypatch.setattr(sys, "stdout", fake_stdout)

    hook.run_hook()

    output = fake_stdout.getvalue().strip()
    assert output == "{}"


def test_hook_speaks_when_idle(monkeypatch, tmp_path):
    monkeypatch.setenv("WHISPER_ANTIGRAVITY_CONFIG_DIR", str(tmp_path))
    config.set_enabled(True)

    spoken_messages = []

    def fake_speak(text, background=True):
        spoken_messages.append(text)
        return True

    monkeypatch.setattr(hook, "speak_text", fake_speak)

    payload = {
        "fullyIdle": True,
        "terminationReason": "model_stop",
        "lastUserInput": "Build the new feature",
    }

    fake_stdin = io.StringIO(json.dumps(payload))
    fake_stdout = io.StringIO()

    monkeypatch.setattr(sys, "stdin", fake_stdin)
    monkeypatch.setattr(sys, "stdout", fake_stdout)

    hook.run_hook()

    assert fake_stdout.getvalue().strip() == "{}"
    assert len(spoken_messages) == 1
    assert "Build the new feature" in spoken_messages[0]
