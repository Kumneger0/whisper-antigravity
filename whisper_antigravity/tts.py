"""Text-To-Speech generation using edge-tts and background audio playback."""

import asyncio
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
from typing import List, Optional
import edge_tts

from .config import load_config


def find_audio_player(file_path: Optional[Path] = None) -> Optional[List[str]]:
    """Detect available audio players on the system (Linux, macOS, Windows)."""
    import sys

    config = load_config()
    configured_player = config.get("audio_player", "auto")

    # If user explicitly configured a player
    if configured_player != "auto":
        if shutil.which(configured_player):
            if configured_player == "mpv":
                return ["mpv", "--no-video", "--really-quiet"]
            elif configured_player == "ffplay":
                return ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet"]
            elif configured_player == "afplay":
                return ["afplay"]
            elif configured_player in ("paplay", "aplay"):
                return [configured_player]
            return [configured_player]

    # 1. macOS Native Audio Player
    if sys.platform == "darwin":
        if shutil.which("afplay"):
            return ["afplay"]
        elif shutil.which("mpv"):
            return ["mpv", "--no-video", "--really-quiet"]

    # 2. Windows Native & Ported Players
    if sys.platform == "win32":
        if shutil.which("mpv"):
            return ["mpv", "--no-video", "--really-quiet"]
        elif shutil.which("ffplay"):
            return ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet"]
        # Fall back to PowerShell Media Player if available
        if shutil.which("powershell"):
            ps_script = (
                "Add-Type -AssemblyName presentationCore; "
                "$player = New-Object System.Windows.Media.MediaPlayer; "
                "$player.Open([System.Uri]$args[0]); "
                "$player.Play(); "
                "Start-Sleep -Milliseconds 1000; "
                "while ($player.NaturalDuration.HasTimeSpan -eq $false -or $player.Position -lt $player.NaturalDuration.TimeSpan) { Start-Sleep -Milliseconds 250 }"
            )
            return ["powershell", "-NoProfile", "-NonInteractive", "-WindowStyle", "Hidden", "-Command", ps_script]

    # 3. Linux & Generic Unix Players
    if shutil.which("mpv"):
        return ["mpv", "--no-video", "--really-quiet"]
    elif shutil.which("ffplay"):
        return ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet"]
    elif shutil.which("paplay"):
        return ["paplay"]
    elif shutil.which("aplay"):
        return ["aplay"]

    return None


def cleanup_old_audio_files(max_age_seconds: int = 3600) -> None:
    """Clean up old temporary audio files in /tmp."""
    temp_dir = Path(tempfile.gettempdir())
    now = time.time()
    try:
        for file in temp_dir.glob("whisper_antigravity_*.mp3"):
            if now - file.stat().st_mtime > max_age_seconds:
                try:
                    file.unlink()
                except OSError:
                    pass
    except Exception:
        pass


async def synthesize_speech_async(
    text: str,
    output_path: Path,
    voice: str = "en-US-ChristopherNeural",
    rate: str = "+0%",
    pitch: str = "+0Hz",
    volume: str = "+0%",
) -> None:
    """Synthesize text to an mp3 file using edge-tts asynchronously."""
    communicate = edge_tts.Communicate(
        text=text,
        voice=voice,
        rate=rate,
        pitch=pitch,
        volume=volume,
    )
    await communicate.save(str(output_path))


def synthesize_speech(
    text: str,
    output_path: Path,
    voice: Optional[str] = None,
    rate: Optional[str] = None,
    pitch: Optional[str] = None,
    volume: Optional[str] = None,
) -> None:
    """Synthesize text to speech synchronously."""
    config = load_config()
    voice = voice or config.get("voice", "en-US-ChristopherNeural")
    rate = rate or config.get("rate", "+0%")
    pitch = pitch or config.get("pitch", "+0Hz")
    volume = volume or config.get("volume", "+0%")

    asyncio.run(synthesize_speech_async(
        text=text,
        output_path=output_path,
        voice=voice,
        rate=rate,
        pitch=pitch,
        volume=volume,
    ))


def play_audio_file(file_path: Path, background: bool = True) -> bool:
    """Play an audio file using system player. If background=True, does not block."""
    import sys

    player_cmd = find_audio_player(file_path)
    if not player_cmd:
        # Fall back to python edge-playback if available
        if shutil.which("edge-playback"):
            player_cmd = ["edge-playback"]
        else:
            return False

    cmd = player_cmd + [str(file_path)]

    try:
        if background:
            popen_kwargs = {
                "stdout": subprocess.DEVNULL,
                "stderr": subprocess.DEVNULL,
                "stdin": subprocess.DEVNULL,
            }
            if sys.platform == "win32":
                # Windows detached process flags
                DETACHED_PROCESS = 0x00000008
                CREATE_NEW_PROCESS_GROUP = 0x00000200
                CREATE_NO_WINDOW = 0x08000000
                popen_kwargs["creationflags"] = DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP | CREATE_NO_WINDOW
            else:
                # POSIX detached session
                popen_kwargs["start_new_session"] = True

            subprocess.Popen(cmd, **popen_kwargs)
        else:
            subprocess.run(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
        return True
    except Exception:
        return False


def speak_text(text: str, background: bool = True) -> bool:
    """Convenience function to synthesize and play text immediately."""
    if not text.strip():
        return False

    cleanup_old_audio_files()

    fd, temp_path_str = tempfile.mkstemp(prefix="whisper_antigravity_", suffix=".mp3")
    os.close(fd)
    temp_path = Path(temp_path_str)

    try:
        synthesize_speech(text, temp_path)
        return play_audio_file(temp_path, background=background)
    except Exception as e:
        try:
            temp_path.unlink()
        except OSError:
            pass
        return False


async def get_english_voices_async() -> List[dict]:
    """Fetch available English voices from edge-tts."""
    voices = await edge_tts.list_voices()
    return [v for v in voices if v.get("Locale", "").startswith("en-")]


def get_english_voices() -> List[dict]:
    """Return available English voices synchronously."""
    return asyncio.run(get_english_voices_async())
