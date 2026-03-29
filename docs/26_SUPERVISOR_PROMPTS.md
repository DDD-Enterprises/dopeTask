# Supervisor Prompt Generation and Installation

This is the canonical guide for generating, exporting, and installing dopeTask supervisor prompts.

Use this guide when you need to:

- generate a fresh supervisor prompt for ChatGPT or Claude web
- apply the generated prompt into workspace instruction files for Claude Code, Codex CLI, Gemini CLI, or Copilot CLI
- update your repo after a dopeTask upgrade

For the JSON Task Packet contract, see `13_TASK_PACKET_FORMAT.md`. For the execution flow after the prompt is installed, see `22_WORKFLOW_GUIDE.md`. For migration notes, see `24_UPGRADE_GUIDE.md`.

## Recommended targets as of March 29, 2026

### Web supervisors

| Surface | Recommended target | Why |
| --- | --- | --- |
| ChatGPT | `gpt-5.4` | Current OpenAI docs present GPT-5.4 as the latest/default frontier model. |
| Claude web | `claude-sonnet-4-6` for normal work, `claude-opus-4-6` for the hardest planning | Anthropic’s current models overview lists Sonnet 4.6 and Opus 4.6 as the latest Claude models. |

### CLI and workspace-aware agents

| Tool | Current version checked on March 29, 2026 | Notes |
| --- | --- | --- |
| Codex CLI | `0.117.0` | Checked from the `@openai/codex` npm registry and the latest GitHub release feed. |
| Claude Code | `2.1.87` | Checked from the `@anthropic-ai/claude-code` npm registry package. |
| Gemini CLI | `0.35.3` | Checked from the npm registry and latest GitHub release feed. |
| Copilot CLI | `1.0.12` | Checked from the npm registry and latest GitHub release feed. |

## Install or update the coding CLIs

If you install these tools through npm, these are the current package names:

```bash
npm install -g @openai/codex@latest
npm install -g @anthropic-ai/claude-code@latest
npm install -g @google/gemini-cli@latest
npm install -g @github/copilot@latest
```

Copilot CLI also has official Homebrew, WinGet, and install-script paths. See the GitHub Copilot CLI install docs if you prefer those package managers.

## The easiest path

If you are setting up a repository for the first time, run:

```bash
dopetask ops init --platform chatgpt --model gpt-5.4
```

This creates:

- `ops/operator_profile.yaml`
- `ops/templates/`
- `ops/EXPORTED_OPERATOR_PROMPT.md`

Then choose one of the two installation paths below.

## Path A: Web chat products

Use this for ChatGPT or Claude in the browser.

### Generate a pasteable prompt

For ChatGPT:

```bash
dopetask ops export --platform chatgpt --model gpt-5.4
```

For Claude web with Sonnet 4.6:

```bash
dopetask ops export --platform claude --model claude-sonnet-4-6
```

For Claude web with Opus 4.6:

```bash
dopetask ops export --platform claude --model claude-opus-4-6
```

The exported prompt is written to:

```text
ops/EXPORTED_OPERATOR_PROMPT.md
```

### Install it

1. Open a new chat.
2. Open `ops/EXPORTED_OPERATOR_PROMPT.md`.
3. Copy the entire file.
4. Paste it into the chat’s system/custom instructions surface, or use it as the first message if the product has no persistent system-instruction UI.

### Verify the session

Ask the model:

```text
What is your role in this repository?
```

The answer should stay supervisor-oriented:

- author JSON Task Packets
- do not implement code directly
- delegate execution through `dopetask tp series exec`

## Path B: Workspace-aware coding agents

Use this for tools that read repo instruction files automatically, such as Claude Code, Codex CLI, Gemini CLI, Copilot CLI, Cursor, and Vibe.

### Preview the generated block

```bash
dopetask ops preview
```

### Apply the generated prompt into the repo

If your repo already uses `AGENTS.md`, `CLAUDE.md`, or `.claude/CLAUDE.md`, dopeTask will pick the canonical target automatically:

```bash
dopetask ops apply
```

If you want to force a specific target file:

```bash
dopetask ops apply --target AGENTS.md --platform codex --model gpt-5.4
dopetask ops apply --target CLAUDE.md --platform claude-code --model claude-sonnet-4-6
dopetask ops apply --target AGENTS.md --platform gemini --model gemini-cli-0.35.3
dopetask ops apply --target AGENTS.md --platform copilot --model copilot-cli-1.0.12
```

### Verify the applied prompt

Run:

```bash
dopetask ops doctor --no-export
```

You want the canonical target to report `BLOCK_OK`. If it reports `BLOCK_STALE`, rerun `dopetask ops apply`.

### Tool-specific files now supported in this repo

- `AGENTS.md` for cross-tool supervisor doctrine
- `CLAUDE.md` plus `.claude/rules/` and `.claude/skills/` for Claude Code
- `.github/copilot-instructions.md` plus `.github/agents/` for Copilot
- `.cursor/rules/` for Cursor
- `.vibe/prompts/` and `.vibe/agents/` for Vibe

## Practical defaults

Use these defaults unless you have a repo-specific reason not to:

- ChatGPT: `gpt-5.4`
- Claude web: `claude-sonnet-4-6`
- Claude Code: `claude-sonnet-4-6`
- Codex CLI: `gpt-5.4`
- Gemini CLI: keep the dopeTask supervisor prompt in `AGENTS.md`, let Gemini CLI stay on its own current binary version
- Copilot CLI: keep the dopeTask supervisor prompt in `AGENTS.md`, let Copilot CLI stay on its own current binary version

## When to regenerate prompts

Regenerate or reapply the prompt when:

- you upgrade dopeTask
- you change the target platform or model
- `dopetask ops doctor` reports `BLOCK_STALE`
- you changed `ops/templates/` or `ops/operator_profile.yaml`

## Fallback: manual source prompt

If you cannot use `dopetask ops export` for some reason, the fallback source prompt remains:

```text
docs/llm/SUPERVISOR_SYSTEM_PROMPT.md
```

That file is the manual baseline. The exported prompt is preferred because it includes your repo metadata, current platform, current model, and the generated operator header.
