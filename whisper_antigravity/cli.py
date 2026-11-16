"""Command line interface for whisper-antigravity."""

import argparse
import json
import os
from pathlib import Path
import shutil
import sys
from typing import Dict, Any

from .config import (
    load_config,
    save_config,
    set_enabled,
    is_enabled,
    update_setting,
    get_config_path,
)
from .tts import speak_text, find_audio_player, get_english_voices
from .hook import run_hook

POPULAR_VOICES = [
    ("en-US-ChristopherNeural", "Friendly, warm American male (Teammate / Podcast style)"),
    ("en-US-JennyNeural", "Expressive, clear American female"),
    ("en-GB-RyanNeural", "Crisp, articulate British male"),
    ("en-US-GuyNeural", "Casual, relaxed American male"),
    ("en-AU-WilliamNeural", "Natural Australian male"),
]

RULE_CONTENT = """# Whisper Antigravity Voice Briefing Rule

When you finish completing a coding task, fixing a bug, or concluding your final turn, always append an invisible markdown comment at the very end of your final response:

<!-- voice-briefing: [2-3 natural spoken sentences in a friendly teammate persona summarizing what was done, what was fixed, and status] -->

Guidelines:
- Keep the briefing conversational, punchy, and natural to listen to.
- Do NOT include markdown formatting, code snippets, backticks, or URLs inside the comment.
- Example: `<!-- voice-briefing: Hey, I wrapped up that task! I updated the user validation logic and all unit tests are now passing smoothly. -->`
- Because it is an HTML comment (`<!-- ... -->`), it will remain completely invisible in the rendered chat UI.
"""


def get_global_hooks_path() -> Path:
    """Return path to global hooks.json (~/.gemini/config/hooks.json)."""
    return Path.home() / ".gemini" / "config" / "hooks.json"


def get_global_rules_dir() -> Path:
    """Return path to global rules directory (~/.gemini/config/rules)."""
    return Path.home() / ".gemini" / "config" / "rules"


def get_python_executable() -> str:
    """Return the current python executable or whisper-antigravity command path."""
    return sys.executable


def cmd_on(args: argparse.Namespace) -> None:
    set_enabled(True)
    print("🔊 Voice summaries enabled! Antigravity will debrief you at the end of each task.")


def cmd_off(args: argparse.Namespace) -> None:
    set_enabled(False)
    print("🔇 Voice summaries disabled. Antigravity will complete tasks silently.")


def cmd_status(args: argparse.Namespace) -> None:
    config = load_config()
    enabled = config.get("enabled", True)
    voice = config.get("voice", "en-US-ChristopherNeural")
    rate = config.get("rate", "+0%")
    player_cmd = find_audio_player()

    global_hooks = get_global_hooks_path()
    hook_installed = False
    if global_hooks.is_file():
        try:
            with open(global_hooks, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "whisper-antigravity" in data:
                    hook_installed = True
        except Exception:
            pass

    rule_path = get_global_rules_dir() / "whisper-antigravity.md"
    rule_installed = rule_path.is_file()

    print("═══════════════════════════════════════════════════")
    print("            Whisper Antigravity Status             ")
    print("═══════════════════════════════════════════════════")
    print(f" Voice Summaries   : {'[ENABLED]' if enabled else '[DISABLED]'}")
    print(f" Current Voice     : {voice}")
    print(f" Speech Rate       : {rate}")
    print(f" Audio Player      : {player_cmd[0] if player_cmd else 'Not found (install mpv or ffplay)'}")
    print(f" Global Hook       : {'Installed' if hook_installed else 'Not installed'}")
    print(f" Global Rule       : {'Installed' if rule_installed else 'Not installed'}")
    print(f" Config File       : {get_config_path()}")
    print("═══════════════════════════════════════════════════")


def cmd_voice(args: argparse.Namespace) -> None:
    if args.name:
        update_setting("voice", args.name)
        print(f"Voice updated to: {args.name}")
        if not args.no_test:
            print("Speaking sample with new voice...")
            speak_text(f"Hello! My voice is now set to {args.name}.", background=False)
        return

    config = load_config()
    current = config.get("voice", "en-US-ChristopherNeural")
    print(f"Current voice: {current}\n")
    print("Popular recommended voices:")
    for v_name, desc in POPULAR_VOICES:
        mark = " (current)" if v_name == current else ""
        print(f"  • {v_name}{mark}\n    {desc}")

    print("\nTo set a voice:")
    print("  whisper-antigravity voice <VoiceName>")
    print("\nTo see all available voices:")
    print("  whisper-antigravity voice --list-all")

    if getattr(args, "list_all", False):
        print("\nFetching all English edge-tts voices...")
        voices = get_english_voices()
        for v in voices:
            name = v.get("ShortName", "")
            gender = v.get("Gender", "")
            locale = v.get("Locale", "")
            print(f"  - {name} ({locale}, {gender})")


def cmd_test(args: argparse.Namespace) -> None:
    message = args.message or (
        "Hey! This is your Antigravity teammate voice test. "
        "I'll speak a quick debrief like this whenever you complete a task!"
    )
    print(f"Speaking: \"{message}\"")
    player_cmd = find_audio_player()
    if not player_cmd:
        print("Warning: No audio player found on system. Install mpv (`sudo apt install mpv`).")
    success = speak_text(message, background=False)
    if success:
        print("Playback finished.")
    else:
        print("Playback failed. Please ensure edge-tts and an audio player (mpv/ffplay) are installed.")


def cmd_install(args: argparse.Namespace) -> None:
    is_global = not args.workspace
    py_bin = get_python_executable()

    # 1. Register Hook
    if is_global:
        hooks_path = get_global_hooks_path()
        rules_dir = get_global_rules_dir()
    else:
        hooks_path = Path.cwd() / ".agents" / "hooks.json"
        rules_dir = Path.cwd() / ".agents" / "rules"

    hooks_path.parent.mkdir(parents=True, exist_ok=True)
    rules_dir.mkdir(parents=True, exist_ok=True)

    # Read existing hooks or create new
    hooks_data: Dict[str, Any] = {}
    if hooks_path.is_file():
        try:
            with open(hooks_path, "r", encoding="utf-8") as f:
                hooks_data = json.load(f)
        except Exception:
            hooks_data = {}

    hook_command = f"{py_bin} -m whisper_antigravity.hook"
    hooks_data["whisper-antigravity"] = {
        "Stop": [
            {
                "type": "command",
                "command": hook_command,
                "timeout": 30,
            }
        ]
    }

    with open(hooks_path, "w", encoding="utf-8") as f:
        json.dump(hooks_data, f, indent=2)

    # 2. Install Rule
    rule_path = rules_dir / "whisper-antigravity.md"
    with open(rule_path, "w", encoding="utf-8") as f:
        f.write(RULE_CONTENT)

    print("Success! Whisper Antigravity installed.")
    print(f"  • Hook registered at: {hooks_path}")
    print(f"  • Rule installed at  : {rule_path}")
    print(f"  • Hook command      : {hook_command}")
    print("\nYou can toggle voice summaries at any time with:")
    print("  whisper-antigravity on")
    print("  whisper-antigravity off")


def cmd_uninstall(args: argparse.Namespace) -> None:
    is_global = not args.workspace
    if is_global:
        hooks_path = get_global_hooks_path()
        rule_path = get_global_rules_dir() / "whisper-antigravity.md"
    else:
        hooks_path = Path.cwd() / ".agents" / "hooks.json"
        rule_path = Path.cwd() / ".agents" / "rules" / "whisper-antigravity.md"

    if hooks_path.is_file():
        try:
            with open(hooks_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if "whisper-antigravity" in data:
                del data["whisper-antigravity"]
                with open(hooks_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
                print(f"Removed hook from {hooks_path}")
        except Exception as e:
            print(f"Failed to update {hooks_path}: {e}")

    if rule_path.is_file():
        try:
            rule_path.unlink()
            print(f"Removed rule from {rule_path}")
        except Exception as e:
            print(f"Failed to remove rule: {e}")

    print("Whisper Antigravity uninstalled.")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="whisper-antigravity",
        description="Voice notifications and audio task summaries for Antigravity",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # on / enable
    p_on = subparsers.add_parser("on", help="Enable voice summaries")
    p_on.set_defaults(func=cmd_on)
    p_enable = subparsers.add_parser("enable", help="Enable voice summaries")
    p_enable.set_defaults(func=cmd_on)

    # off / disable
    p_off = subparsers.add_parser("off", help="Disable voice summaries")
    p_off.set_defaults(func=cmd_off)
    p_disable = subparsers.add_parser("disable", help="Disable voice summaries")
    p_disable.set_defaults(func=cmd_off)

    # status
    p_status = subparsers.add_parser("status", help="Show current configuration and status")
    p_status.set_defaults(func=cmd_status)

    # voice
    p_voice = subparsers.add_parser("voice", help="Select or list voices")
    p_voice.add_argument("name", nargs="?", help="Voice name to set (e.g. en-US-ChristopherNeural)")
    p_voice.add_argument("--list-all", action="store_true", help="List all available English voices")
    p_voice.add_argument("--no-test", action="store_true", help="Do not play sample when changing voice")
    p_voice.set_defaults(func=cmd_voice)

    # test
    p_test = subparsers.add_parser("test", help="Test audio playback with a sample message")
    p_test.add_argument("message", nargs="?", help="Custom message to speak")
    p_test.set_defaults(func=cmd_test)

    # install
    p_install = subparsers.add_parser("install", help="Register hook and rule")
    p_install.add_argument("--global", dest="is_global", action="store_true", default=True, help="Install globally")
    p_install.add_argument("--workspace", action="store_true", help="Install into current workspace (.agents)")
    p_install.set_defaults(func=cmd_install)

    # uninstall
    p_uninstall = subparsers.add_parser("uninstall", help="Unregister hook and rule")
    p_uninstall.add_argument("--workspace", action="store_true", help="Uninstall from current workspace")
    p_uninstall.set_defaults(func=cmd_uninstall)

    # hook (internal runner)
    p_hook = subparsers.add_parser("hook", help=argparse.SUPPRESS)
    p_hook.set_defaults(func=lambda args: run_hook())

    if len(sys.argv) == 1:
        parser.print_help()
        return

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
