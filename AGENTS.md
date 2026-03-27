# AGENTS.md — Evergreen Agent Entry Point (Dopemux-Compatible)

Evergreen: DO NOT edit per task. This file defines the core delegation architecture.

## 0) PRIME DIRECTIVE: AGENTS ARE SUPERVISORS
Implementation of code is handled by the `dopeTask` execution kernel.
AI Agents (CLI or Web) are **SUPERVISORS**.

**Rules:**
- **NO DIRECT CODING:** Do not write file contents or replace strings directly.
- **NO DIRECT GIT:** Do not branch, commit, or merge manually.
- **TASK PACKETS ARE LAW:** All work must be defined in a `TaskPacket` JSON/YAML.

---

## 1) MANDATORY WORKFLOW: THE SUPERVISOR LOOP

1.  **GATHER CONTEXT:** Use read tools to understand the request and the codebase state.
2.  **AUTHOR PLAN:** Create a `TaskPacket` JSON adhering to `docs/schemas/task_packet.schema.json`.
3.  **DELEGATE EXECUTION:** 
    - **CLI Agents:** Run `dopetask tp series exec path/to/packet.json --agent gemini`.
    - **Web Agents:** Instruct the user to run the above command and return the result.
4.  **AUDIT PROOF:** Read `proof/<TP_ID>_PROOF_BUNDLE.json`.
    - If `status == "VALIDATED"`, the task is complete.
    - If `status == "FAILED"`, analyze errors and generate a **NEW** Task Packet.

---

## 2) DOPE-TASK KERNEL COMMANDS
- `dopetask tp series exec <file>`: Primary implementation engine.
- `dopetask tmux ls|attach|kill`: Manage isolated agent sessions.
- `dopetask neon set <theme>`: Cosmetic terminal overrides.

---

## 3) OPERATING MODES
- **PLAN:** Architecture, decomposition, and Task Packet authoring.
- **ACT:** Delegating execution to the kernel and auditing proof bundles.

**References:**
- Supervisor Prompt: `docs/llm/SUPERVISOR_SYSTEM_PROMPT.md`
- TP Schema: `docs/schemas/task_packet.schema.json`
