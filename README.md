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

## 💻 Platform Support & Audio Prerequisites

Whisper Antigravity works natively on **macOS**, **Linux**, and **Windows**:

| OS | Audio Player | Setup Required |
| :--- | :--- | :--- |
| **macOS** | Native `afplay` *(or `mpv` / `ffplay`)* | **Zero setup!** Built directly into macOS. |
| **Linux** | `mpv` *(or `ffplay`, `paplay`, `aplay`)* | `sudo apt install -y mpv` *(recommended)* |
| **Windows** | Native PowerShell `MediaPlayer` *(or `mpv`)* | **Zero setup!** Built into Windows 10/11. |

---

## 🚀 Quick Start & Installation

### Linux & macOS (curl)

Run in your terminal:

```bash
curl -fsSL https://raw.githubusercontent.com/Kumneger0/whisper-antigravity/main/install.sh | bash
```

### Windows (PowerShell)

Run in PowerShell:

```powershell
irm https://raw.githubusercontent.com/Kumneger0/whisper-antigravity/main/install.ps1 | iex
```

---

The installer will automatically:
1. Clone the project into `~/.local/share/whisper-antigravity` (or `%USERPROFILE%\.local\share\whisper-antigravity`).
2. Create an isolated Python virtual environment and install `edge-tts`.
3. Provide the `whisper-antigravity` CLI command.
4. Register the global `Stop` hook in `~/.gemini/config/hooks.json`.
5. Install the global Antigravity rule in `~/.gemini/config/rules/whisper-antigravity.md`.

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
