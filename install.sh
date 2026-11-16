#!/usr/bin/env bash
set -e

REPO_URL="${WHISPER_ANTIGRAVITY_REPO:-https://github.com/Kumneger0/whisper-antigravity.git}"
INSTALL_DIR="${WHISPER_ANTIGRAVITY_HOME:-$HOME/.local/share/whisper-antigravity}"
BIN_DIR="$HOME/.local/bin"

echo "======================================================="
echo "        Installing Whisper Antigravity                 "
echo "======================================================="

# 1. Determine Source (Local directory vs. Remote Clone)
LOCAL_DIR=""
if [ -n "${BASH_SOURCE[0]}" ] && [ -f "${BASH_SOURCE[0]}" ]; then
    POTENTIAL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    if [ -f "$POTENTIAL_DIR/pyproject.toml" ]; then
        LOCAL_DIR="$POTENTIAL_DIR"
    fi
fi

# 2. Check Python
PYTHON_CMD=""
if command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_CMD="python"
else
    echo "Error: Python 3 is required but not found on your system."
    echo "Please install Python 3.9 or higher and try again."
    exit 1
fi

echo "Using Python: $($PYTHON_CMD --version)"

# 3. Check Audio Player
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

# 4. Prepare Install Directory
if [ -n "$LOCAL_DIR" ] && [ "$LOCAL_DIR" != "$INSTALL_DIR" ]; then
    echo "Syncing local repository to $INSTALL_DIR..."
    mkdir -p "$INSTALL_DIR"
    # Copy files excluding virtualenvs and git metadata
    if command -v rsync >/dev/null 2>&1; then
        rsync -a --exclude='.venv' --exclude='__pycache__' --exclude='.pytest_cache' --exclude='.git' "$LOCAL_DIR/" "$INSTALL_DIR/"
    else
        cp -R "$LOCAL_DIR/." "$INSTALL_DIR/"
        rm -rf "$INSTALL_DIR/.venv" "$INSTALL_DIR/__pycache__" "$INSTALL_DIR/.pytest_cache"
    fi
elif [ -z "$LOCAL_DIR" ]; then
    # Running via curl | bash (no local files)
    if [ -d "$INSTALL_DIR/.git" ]; then
        echo "Updating existing installation in $INSTALL_DIR..."
        git -C "$INSTALL_DIR" pull --quiet
    else
        echo "Cloning whisper-antigravity into $INSTALL_DIR..."
        rm -rf "$INSTALL_DIR"
        mkdir -p "$INSTALL_DIR"
        git clone --depth 1 "$REPO_URL" "$INSTALL_DIR" --quiet
    fi
fi

# 5. Setup Python Virtual Environment in INSTALL_DIR
VENV_DIR="$INSTALL_DIR/.venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment at $VENV_DIR..."
    $PYTHON_CMD -m venv "$VENV_DIR"
fi

VENV_PY="$VENV_DIR/bin/python"
VENV_PIP="$VENV_DIR/bin/pip"

echo "Installing whisper-antigravity dependencies..."
"$VENV_PIP" install -q --upgrade pip
"$VENV_PIP" install -q -e "$INSTALL_DIR"

# 6. Symlink CLI to ~/.local/bin
mkdir -p "$BIN_DIR"
ln -sf "$VENV_DIR/bin/whisper-antigravity" "$BIN_DIR/whisper-antigravity"
echo "Linked CLI to $BIN_DIR/whisper-antigravity"

# 7. Check if ~/.local/bin is in PATH
PATH_NOTICE=""
case ":$PATH:" in
    *":$BIN_DIR:"*) ;;
    *)
        PATH_NOTICE="Note: $BIN_DIR is not currently in your PATH.
Add it by running:
  echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.bashrc && source ~/.bashrc
(or replace ~/.bashrc with ~/.zshrc if using zsh)"
        ;;
esac

# 8. Register Global Hook & Rule in Antigravity
echo "Registering global Antigravity hook and rule..."
"$VENV_PY" -m whisper_antigravity.cli install --global

echo ""
echo "======================================================="
echo "  Whisper Antigravity installed successfully!"
echo "======================================================="
if [ -n "$PATH_NOTICE" ]; then
    echo "$PATH_NOTICE"
    echo "-------------------------------------------------------"
fi
echo "Quick Commands:"
echo "  • Test speech   : whisper-antigravity test"
echo "  • Toggle ON     : whisper-antigravity on"
echo "  • Toggle OFF    : whisper-antigravity off"
echo "  • Status        : whisper-antigravity status"
echo "  • Select Voice  : whisper-antigravity voice"
echo "======================================================="
