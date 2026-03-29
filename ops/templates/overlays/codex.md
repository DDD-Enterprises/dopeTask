# codex Overlay

Specifics for Codex:

- Use `gpt-5.4` as the default supervisor model.
- Respect repo instruction files and maintain supervisor-only behavior.
- Emit JSON Task Packets or audit output; do not directly implement code from the supervisor channel.
