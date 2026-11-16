"""Configuration management for whisper-antigravity."""

import json
import os
from pathlib import Path
from typing import Any, Dict

DEFAULT_CONFIG: Dict[str, Any] = {
    "enabled": True,
    "voice": "en-US-ChristopherNeural",
    "rate": "+0%",
    "pitch": "+0Hz",
    "volume": "+0%",
    "audio_player": "auto",  # auto, mpv, ffplay, paplay, aplay
    "announce_errors": True,
}


def get_config_dir() -> Path:
    """Return the configuration directory path (~/.config/whisper-antigravity)."""
    custom_dir = os.environ.get("WHISPER_ANTIGRAVITY_CONFIG_DIR")
    if custom_dir:
        return Path(custom_dir)
    return Path.home() / ".config" / "whisper-antigravity"


def get_config_path() -> Path:
    """Return the configuration file path."""
    return get_config_dir() / "config.json"


def load_config() -> Dict[str, Any]:
    """Load configuration from disk, falling back to defaults."""
    config_path = get_config_path()
    config = DEFAULT_CONFIG.copy()

    if config_path.is_file():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                saved = json.load(f)
                if isinstance(saved, dict):
                    config.update(saved)
        except Exception:
            # Fall back to defaults on read errors
            pass

    return config


def save_config(config: Dict[str, Any]) -> None:
    """Save configuration to disk."""
    config_dir = get_config_dir()
    config_dir.mkdir(parents=True, exist_ok=True)
    config_path = get_config_path()

    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)


def is_enabled() -> bool:
    """Quickly check if voice announcements are enabled."""
    return bool(load_config().get("enabled", True))


def set_enabled(enabled: bool) -> None:
    """Enable or disable voice announcements without modifying hooks.json."""
    config = load_config()
    config["enabled"] = bool(enabled)
    save_config(config)


def get_setting(key: str, default: Any = None) -> Any:
    """Get a specific setting value."""
    return load_config().get(key, default)


def update_setting(key: str, value: Any) -> None:
    """Update a specific setting value."""
    config = load_config()
    config[key] = value
    save_config(config)
