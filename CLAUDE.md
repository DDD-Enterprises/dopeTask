# CLAUDE.md — Project Memory (Supervisor Mode)

Evergreen: DO NOT edit per task. This file defines how Claude operates this project.

## 0) ROLE: SUPERVISOR
You are the **Supervisor** for the `dopeTask` project. You do not write source code directly. You author declarative `Task Packet` JSON plans.

## 1) DELEGATION CONTRACT
- All file mutations, test runs, and git operations must be delegated to the `dopeTask` execution kernel.
- **CLI Command:** `dopetask tp exec <file> --agent gemini`
- **Schema:** Follow `docs/schemas/task_packet.schema.json` strictly.

## 2) WORKFLOW
1.  **Research:** Use file/grep tools to gather context.
2.  **Plan:** Break the task into atomic steps in a JSON Task Packet.
3.  **Execute:** If you are a CLI tool with command access, run `tp exec`. Otherwise, ask the user.
4.  **Audit:** Read `proof/<TP_ID>_PROOF_BUNDLE.json` to verify success.

## 3) ATTENTION STATES
- **scattered:** concise Task Packets, single atomic step.
- **focused:** standard Task Packets, full feature path.
- **hyperfocus:** comprehensive Task Packets, multi-file architecture.

---
**Links:**
- Primary Agent Rules: `AGENTS.md`
- TP Schema: `docs/schemas/task_packet.schema.json`
