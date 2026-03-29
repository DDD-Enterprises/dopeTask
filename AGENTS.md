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

---

## 4) PACKET QUALITY BAR

Every proposed packet should prefer:

- `id`
- `project`
- `target`
- `invariants`
- `depends_on`
- `series.id`
- `series.base_branch`
- `series.parent_tp_id`
- `series.final_packet`
- `commit.message`
- `commit.allowlist`
- `commit.verify`
- `steps`

Every step must include:

- `id`
- `task`
- `validation`

Use optional step fields only when they add real execution value:

- `requirements`
- `commands`
- `expected_files`
- `context_files`

Avoid:

- vague instructions
- hidden scope expansion
- markdown packets as the default path
- broad allowlists such as `["**/*"]`

---

## 5) PROOF REVIEW ORDER

When execution artifacts exist, review them in this order:

1. `*_PROOF_BUNDLE.json`
2. supporting artifacts only if needed
3. archive only if the bundle is insufficient

Do not start from the archive.
Do not silently rewrite old packet history.
If remediation is needed, emit a new corrective JSON Task Packet.

---

## 6) REFUSAL RULES

Refuse when:

- repository truth is missing
- validation cannot be specified empirically
- safe packetization is not possible
- the user asks for hidden retries or undeclared side effects

A refusal must include:

- the exact missing evidence
- why it blocks correct packet generation
- the minimum evidence required to continue
