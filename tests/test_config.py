"""Unit tests for whisper_antigravity.config."""

import json
from pathlib import Path
import tempfile
import pytest

from whisper_antigravity import config


def test_config_defaults(monkeypatch, tmp_path):
    monkeypatch.setenv("WHISPER_ANTIGRAVITY_CONFIG_DIR", str(tmp_path))
    cfg = config.load_config()
    assert cfg["enabled"] is True
    assert cfg["voice"] == "en-US-ChristopherNeural"
    assert config.is_enabled() is True


def test_config_toggle_on_off(monkeypatch, tmp_path):
    monkeypatch.setenv("WHISPER_ANTIGRAVITY_CONFIG_DIR", str(tmp_path))
    assert config.is_enabled() is True

    config.set_enabled(False)
    assert config.is_enabled() is False

    cfg_file = tmp_path / "config.json"
    assert cfg_file.is_file()
    with open(cfg_file, "r") as f:
        data = json.load(f)
    assert data["enabled"] is False

    config.set_enabled(True)
    assert config.is_enabled() is True


def test_config_update_setting(monkeypatch, tmp_path):
    monkeypatch.setenv("WHISPER_ANTIGRAVITY_CONFIG_DIR", str(tmp_path))
    config.update_setting("voice", "en-GB-RyanNeural")
    assert config.get_setting("voice") == "en-GB-RyanNeural"
