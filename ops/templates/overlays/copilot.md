# copilot Overlay

Specifics for Copilot CLI:

- Copilot CLI should honor the repo instruction block and stay in supervisor mode.
- Prefer Task Packet JSON output and audit output over direct code generation in the supervisor path.
- Keep execution delegated to `dopetask tp series exec`.
