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

## 1. The System Prompt

To transform your AI into a dopeTask Supervisor, you must give it a specific set of instructions at the very beginning of your chat session.

We have created a pre-written set of instructions for you.

You can find it in the dopeTask repository here:
`docs/llm/SUPERVISOR_SYSTEM_PROMPT.md`

## 2. Bootstrapping Your Session

Whenever you start a new conversation with ChatGPT or Claude to work on your project, follow this exact process:

1. **Open a new chat window.**
2. **Copy** the entire contents of the `SUPERVISOR_SYSTEM_PROMPT.md` file.
3. **Paste** it into the first message of the chat and press send.

The AI should respond by confirming it understands its new role as a Supervisor and that it will only output Task Packet JSON files.

## 3. What Did You Just Do?

By pasting that prompt, you have given the AI strict boundaries:
*   **"Do not write code directly."**
*   **"Only output a blueprint (Task Packet) formatted as JSON."**
*   **"Every step in your blueprint must include automated validation."**
*   **"New work must use `depends_on`, `series`, and `commit` metadata so dopeTask can run each TP in its own worktree and finish the series as one PR."**

## 4. Cursor and CLI Agents

If you are using an IDE like **Cursor**, or a CLI agent like the **Gemini CLI**, you do not need to paste this prompt manually every time.

These tools can read "workspace files." As long as you have the `AGENTS.md` and `CLAUDE.md` files (provided in the dopeTask repo) in the root folder of your project, they will automatically adopt the Supervisor role when working in that folder.

---

Now that your AI is acting as a strict manager, you are ready to actually build something!

👉 **[Next: The Daily Workflow](04_WORKFLOW.md)**
