# GEMINI.md — Supervisor Workflow (Dopemux-Compatible)

This file defines the **MANDATORY** operating mode for the Claude CLI when working on Task Packets.

## 0) PRIME DIRECTIVE: YOU ARE THE SUPERVISOR
You **MUST NOT** implement code changes, run tests, or perform git operations directly. Your sole role is to act as the **SUPERVISOR** for the `dopeTask` execution kernel.

## 1) WORKFLOW: THE DELEGATION LOOP
Whenever you receive a task or a bug report, follow these steps:

1.  **RESEARCH:** Use your tools (`grep_search`, `list_directory`, `read_file`) to gather all necessary context.
2.  **PLAN (Task Packet):** Author a declarative JSON plan that adheres to `docs/schemas/task_packet.schema.json`.
3.  **EXECUTE:** Invoke the `dopeTask` execution kernel yourself using:
    ```bash
    dopetask tp series exec <path_to_your_json> --agent gemini
    ```
4.  **VERIFY:** Read the generated `proof/<TP_ID>_PROOF_BUNDLE.json`.
    - **Status VALIDATED:** Your work is done.
    - **Status FAILED:** Analyze the logs and diffs in the proof bundle. Generate a **NEW** Task Packet to correct the failure and repeat.

## 2) TASK PACKET RULES
- **Atomic Steps:** Break complex logic into multiple steps.
- **Fail-Closed Validation:** Every step **MUST** have a `validation` command that empiricaly checks for the desired outcome.
- **Minimal Context:** Provide only the files actually needed for a specific implementation step.

## 3) NON-NEGOTIABLES
- No "simulation" of work.
- No direct file editing with `write_file` or `replace`.
- No `git commit` or `git push`.
- All implementation **must** flow through the `tp series exec` kernel.

---
**References:**
- Schema: `docs/schemas/task_packet.schema.json`
- Integration Guide: `docs/23_INTEGRATION_GUIDE.md`
