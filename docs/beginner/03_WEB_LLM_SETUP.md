# Setting up your Web LLM (Supervisor)

You have dopeTask installed on your computer. Now you need to tell your AI (ChatGPT, Claude, etc.) how to use it.

If you just tell Claude, *"Build me a login page,"* it will immediately start writing Python or HTML code for you to copy and paste.

**We do NOT want this.** As we learned in the [Welcome Guide](00_WELCOME.md), copying and pasting code directly is how things break.

Instead, we want the AI to act as a **Supervisor**. We want it to write a **Task Packet** (the blueprint), which dopeTask will then execute safely.

This page is the beginner onboarding version of the supervisor setup. For the canonical packet contract and workflow, use:

- `../13_TASK_PACKET_FORMAT.md`
- `../22_WORKFLOW_GUIDE.md`
- `../24_UPGRADE_GUIDE.md`

---

## 1. Generate the Prompt First

Do not start by manually opening a markdown file.

Instead, let dopeTask generate the current prompt for your tool:

```bash
dopetask ops init --platform chatgpt --model gpt-5.4
```

This creates a generated prompt file at:

```text
ops/EXPORTED_OPERATOR_PROMPT.md
```

If you want Claude web instead, export a Claude-specific prompt:

```bash
dopetask ops export --platform claude --model claude-sonnet-4-6
```

## 2. Bootstrapping Your Session

Whenever you start a new conversation with ChatGPT or Claude to work on your project, follow this process:

1. **Open a new chat window.**
2. **Open** `ops/EXPORTED_OPERATOR_PROMPT.md`.
3. **Copy** the entire contents of that file.
4. **Paste** it into the first message of the chat and press send.

The AI should respond by confirming it understands its new role as a Supervisor and that it will only output Task Packet JSON files.

## 3. What Did You Just Do?

By pasting that prompt, you have given the AI strict boundaries:
*   **"Do not write code directly."**
*   **"Only output a blueprint (Task Packet) formatted as JSON."**
*   **"Every step in your blueprint must include automated validation."**
*   **"New work must use `depends_on`, `series`, and `commit` metadata so dopeTask can run each TP in its own worktree and finish the series as one PR."**
*   If the work is repo-bound, include `repo_binding`, `execution`, `commit.verify`, and `pr`; use the strict schema pack for identity-checked repos.
*   If the packet target is Gemini, add `pal_chain` and keep it enabled so the PAL metadata is explicit.

## 4. Cursor and CLI Agents

If you are using a workspace-aware coding tool like **Claude Code**, **Codex CLI**, **Gemini CLI**, or **Copilot CLI**, you usually do not need to paste the prompt manually every time.

Instead, apply the generated prompt into the repo instruction files:

```bash
dopetask ops apply
```

Then verify it:

```bash
dopetask ops doctor --no-export
```

For the full current model and CLI matrix, see `../26_SUPERVISOR_PROMPTS.md`.

If you need the manual fallback source prompt, it still exists at:

```text
docs/llm/SUPERVISOR_SYSTEM_PROMPT.md
```

---

Now that your AI is acting as a strict manager, you are ready to actually build something!

👉 **[Next: The Daily Workflow](04_WORKFLOW.md)**
