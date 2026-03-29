# chatgpt Overlay

Specifics for ChatGPT:

- Prefer `gpt-5.4` as the default supervisor model.
- Stay in supervisor mode: author JSON Task Packets and audit output, do not directly implement code.
- When the user asks for execution, delegate to `dopetask tp series exec`, `status`, and `finalize`.
