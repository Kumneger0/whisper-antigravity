# 🎙️ Whisper Antigravity

> **Voice task debriefs for Google Antigravity.**  
> Makes Antigravity speak a conversational debrief whenever it finishes a task or encounters an error — so you never have to read a giant wall of text just to know what was fixed.

---

## ✨ Features

- **🗣️ Natural Neural Voices**: Uses `edge-tts` for high-quality, expressive speech (zero API keys and zero cost).
- **⚡ 100% Antigravity Native**: Antigravity crafts its own conversational debrief in its final response turn inside an invisible comment (`<!-- voice-briefing: ... -->`). Invisible in the chat UI, but spoken aloud.
- **🚀 Non-Blocking Background Playback**: The audio player is dispatched detached in the background, so Antigravity releases immediately and is ready for your next prompt.
- **🎛️ Instant On/Off Toggle**: Mute or unmute voice summaries anytime using `whisper-antigravity on` or `whisper-antigravity off` without having to edit configuration files.
- **🛡️ Built-in Error Warnings**: If a task fails or aborts with an error, Antigravity verbally announces the error so you can intervene quickly.
- **🧩 Fallback Text Cleaning**: If an older session or task didn't include the voice briefing tag, the built-in sanitizer cleans markdown formatting, tables, diffs, and code blocks to speak a crisp 2-sentence takeaway.

---

## 📦 Prerequisites

On Linux, an audio player is recommended for playback. `mpv` works best:

```bash
# Debian / Ubuntu
sudo apt install -y mpv

# Fedora / RHEL
sudo dnf install -y mpv

# Arch Linux
sudo pacman -S mpv
```

*(If `mpv` is not installed, `whisper-antigravity` will automatically look for `ffplay`, `paplay`, or `aplay`.)*

---

## 🚀 Quick Start & Installation

Run the one-step installer:

```bash
./install.sh
```

The installer will:
1. Create a Python virtual environment (`.venv`) and install dependencies (`edge-tts`).
2. Symlink the CLI to `~/.local/bin/whisper-antigravity` (if available on your PATH).
3. Register the global `Stop` hook in `~/.gemini/config/hooks.json`.
4. Install the global Antigravity rule in `~/.gemini/config/rules/whisper-antigravity.md`.

---

## 🎮 CLI Usage

```bash
# Test audio playback with a sample voice line
whisper-antigravity test

# Check current configuration and active hook status
whisper-antigravity status

# Turn voice announcements OFF (quiet mode)
whisper-antigravity off

# Turn voice announcements back ON
whisper-antigravity on

# Change voice (default: en-US-ChristopherNeural)
whisper-antigravity voice en-US-JennyNeural

# See all available voices
whisper-antigravity voice --list-all
```

---

## 🎭 Recommended Voices

| Voice | Description |
| :--- | :--- |
| **`en-US-ChristopherNeural`** *(Default)* | Friendly, warm American male (Teammate / Podcast co-host style) |
| **`en-US-JennyNeural`** | Expressive, natural American female |
| **`en-GB-RyanNeural`** | Crisp, articulate British male |
| **`en-US-GuyNeural`** | Relaxed, casual American male |
| **`en-AU-WilliamNeural`** | Casual Australian male |

---

## 🛠️ How It Works

1. **Antigravity Rule (`~/.gemini/config/rules/whisper-antigravity.md`)**:  
   Teaches Antigravity to append an invisible HTML comment at the end of its final turn:
   ```html
   <!-- voice-briefing: Hey, I wrapped up that task! I updated the user validation logic and all unit tests are passing now. -->
   ```
2. **Stop Hook (`~/.gemini/config/hooks.json`)**:  
   Antigravity fires the `Stop` event when execution finishes. The hook script:
   - Verifies `enabled == true` in `~/.config/whisper-antigravity/config.json`.
   - Verifies `fullyIdle == true` (no lingering background jobs).
   - Extracts the voice debrief from `transcript.jsonl`.
   - Synthesizes audio using `edge-tts`.
   - Spawns the audio player detached in the background and returns `{}` immediately.

---

## 📄 License

MIT
