# Whisper Antigravity Voice Briefing Rule

When you finish completing a coding task, fixing a bug, or concluding your final turn, always append an invisible markdown comment at the very end of your final response:

<!-- voice-briefing: [2-3 natural spoken sentences in a friendly teammate persona summarizing what was done, what was fixed, and status] -->

Guidelines:
- Keep the briefing conversational, punchy, and natural to listen to.
- Do NOT include markdown formatting, code snippets, backticks, or URLs inside the comment.
- Example: `<!-- voice-briefing: Hey, I wrapped up that task! I updated the user validation logic and all unit tests are now passing smoothly. -->`
- Because it is an HTML comment (`<!-- ... -->`), it will remain completely invisible in the rendered chat UI.
