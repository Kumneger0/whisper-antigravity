"""Unit tests for whisper_antigravity.tts audio player detection."""

from pathlib import Path
import pytest
from whisper_antigravity import tts


def test_find_audio_player_macos(monkeypatch):
    monkeypatch.setattr("sys.platform", "darwin")
    monkeypatch.setattr("shutil.which", lambda cmd: "/usr/bin/afplay" if cmd == "afplay" else None)

    player = tts.find_audio_player()
    assert player == ["afplay"]


def test_find_audio_player_linux_mpv(monkeypatch):
    monkeypatch.setattr("sys.platform", "linux")
    monkeypatch.setattr("shutil.which", lambda cmd: "/usr/bin/mpv" if cmd == "mpv" else None)

    player = tts.find_audio_player()
    assert player == ["mpv", "--no-video", "--really-quiet"]


def test_find_audio_player_windows_powershell(monkeypatch):
    monkeypatch.setattr("sys.platform", "win32")
    # Neither mpv nor ffplay installed, but powershell is
    monkeypatch.setattr("shutil.which", lambda cmd: "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe" if cmd == "powershell" else None)

    player = tts.find_audio_player()
    assert player is not None
    assert player[0] == "powershell"
    assert "System.Windows.Media.MediaPlayer" in player[-1]
