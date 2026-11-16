#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "======================================================="
echo "        Installing Whisper Antigravity                 "
echo "======================================================="

# 1. Check Python
PYTHON_CMD=""
if command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_CMD="python"
else
    echo "Error: Python 3 is required but not found."
    exit 1
fi

echo "Using Python: $($PYTHON_CMD --version)"

# 2. Check Audio Player
PLAYER_FOUND=false
for player in mpv ffplay paplay aplay; do
    if command -v "$player" >/dev/null 2>&1; then
        echo "Found audio player: $player"
        PLAYER_FOUND=true
        break
    fi
done

if [ "$PLAYER_FOUND" = false ]; then
    echo "Notice: No audio player found (mpv, ffplay, paplay, aplay)."
    echo "Recommended: Install mpv for best playback experience:"
    echo "  sudo apt install -y mpv   # Debian / Ubuntu"
    echo "  sudo dnf install -y mpv   # Fedora / RHEL"
    echo "  sudo pacman -S mpv        # Arch"
fi

# 3. Setup Virtual Environment
VENV_DIR="$SCRIPT_DIR/.venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment at $VENV_DIR..."
    $PYTHON_CMD -m venv "$VENV_DIR"
fi

VENV_PY="$VENV_DIR/bin/python"
VENV_PIP="$VENV_DIR/bin/pip"

echo "Installing whisper-antigravity in editable mode..."
"$VENV_PIP" install -q --upgrade pip
"$VENV_PIP" install -q -e "$SCRIPT_DIR"

# 4. Optional symlink to ~/.local/bin
USER_BIN="$HOME/.local/bin"
if [ -d "$USER_BIN" ]; then
    mkdir -p "$USER_BIN"
    ln -sf "$VENV_DIR/bin/whisper-antigravity" "$USER_BIN/whisper-antigravity"
    echo "Linked CLI to $USER_BIN/whisper-antigravity"
fi

# 5. Run internal installer to register hook & rule
echo "Registering global Antigravity hook and rule..."
"$VENV_PY" -m whisper_antigravity.cli install --global

echo ""
echo "======================================================="
echo "  Whisper Antigravity installed successfully!"
echo "======================================================="
echo "Quick Commands:"
echo "  • Test speech   : $VENV_DIR/bin/whisper-antigravity test"
echo "  • Toggle ON     : $VENV_DIR/bin/whisper-antigravity on"
echo "  • Toggle OFF    : $VENV_DIR/bin/whisper-antigravity off"
echo "  • Status        : $VENV_DIR/bin/whisper-antigravity status"
echo "  • Select Voice  : $VENV_DIR/bin/whisper-antigravity voice"
echo "======================================================="
