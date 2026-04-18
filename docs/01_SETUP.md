# Setup and Tool Configuration

This guide covers the necessary steps to set up your environment to use `dopeTask`.

## Prerequisites

1.  **Python**: Python 3.9 or newer is required.
2.  **GitHub CLI**: The `gh` command-line tool is required for creating pull requests with `dopetask tp series finalize`.
    -   **Installation**: Follow the [official installation instructions](https://github.com/cli/cli#installation).
    -   **Authentication**: After installing, run:
        ```bash
        gh auth login
        ```
3.  **Git**: A working `git` installation is required. If you are starting from an empty folder, `dopetask setup-git` can check for `git`, install missing tools when possible, create the repository, create the GitHub remote, push the initial `main` branch, and configure repository safety defaults.

## Installation

To install `dopeTask` for development, clone the repository and install it in editable mode:

```bash
git clone https://github.com/DDD-Enterprises/dopeTask.git
cd dopeTask
pip install -e .
```

Alternatively, if you are using `uv`:

```bash
uv sync
```

## Configuration

`dopeTask` is designed to be zero-config for most projects. However, you should ensure your environment has the following set up:

-   **Environment Variables**: Ensure `GITHUB_TOKEN` is set if you are running in a CI environment where `gh auth login` is not practical.
-   **Path**: Ensure the `scripts/` directory is in your `PATH` if you want to use the repository shims.
-   **Repo-local venvs**: The repo-local launcher prefers `.venv-dopetask`, then `.venv`, then legacy `.dopetask_venv`.

## Verification

Verify your installation by running the `doctor` command:

```bash
dopetask doctor
```

And checking the version:

```bash
dopetask --version
```

If you are starting a brand-new project directory, bootstrap git and GitHub first:

```bash
dopetask setup-git --visibility private
```

This applies these defaults after the repository exists:

- local git defaults such as `pull.ff=only`, `fetch.prune=true`, and `push.autoSetupRemote=true`
- GitHub merge defaults: auto-merge on, delete branch on merge, update branch allowed, squash/rebase enabled, merge commits disabled
- GitHub Actions default workflow token permission set to read-only
- GitHub branch protection on `main` with linear history, PR-based changes, stale-review dismissal, conversation resolution, and force-push/deletion disabled

## Supervisor prompt setup

The easiest way to set up a supervisor prompt is to use the built-in `ops` commands instead of copying a static markdown file by hand.

Initialize the prompt profile and export a ChatGPT prompt:

```bash
dopetask ops init --platform chatgpt --model gpt-5.4
```

This writes the generated prompt to:

```text
ops/EXPORTED_OPERATOR_PROMPT.md
```

For workspace-aware tools such as Claude Code, Codex CLI, Gemini CLI, or Copilot CLI, apply the prompt directly into the repo instruction files:

```bash
dopetask ops apply
```

Use `dopetask ops doctor --no-export` to confirm the canonical target is current.

For the full prompt-generation and installation matrix, see `26_SUPERVISOR_PROMPTS.md`.

## Strict packet bootstrap

If this repository should reject wrong-repo execution, bootstrap the repo-local instruction files and the strict packet policy at the same time:

```bash
dopetask project shell init
dopetask ops init --platform chatgpt --model gpt-5.4
dopetask ops apply
```

Then make sure new work uses the strict repo-aware Task Packet contract with `repo_binding`, `execution`, `commit.verify`, and `pr` when the work is repo-bound. PAL metadata stays optional for non-Gemini packets and is required and enabled for Gemini. The portable schema pack lives in `dopetask_schemas/task_packet.strict.schema.json`.
