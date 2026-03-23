# TP-UX-004: Operator Interface & Tmux Integration

## Objective
Provide a seamless, robust operator interface using `tmux` to manage isolated execution sessions for Task Packets. This allows human operators to monitor, intervene, and safely detach from long-running or complex multi-agent execution loops without terminating the process.

## Background & Motivation
As the CLI runner (`dopetask tp exec`) scales to execute larger, multi-step TPs across different agents (Gemini, Codex, Vibe), execution can become long-running. An operator needs the ability to multiplex their terminal, monitor parallel executions, and jump into an interactive state if an agent fails-closed or requires human sign-off.

## Scope & Impact
- Creates `src/dopetask/ops/tp_tmux/` module.
- Introduces `dopetask tmux` CLI commands to start, attach, list, and kill isolated TP workspaces.
- Integrates with the `dopetask tp exec` flow to optionally spawn executions inside a managed tmux window.

## Proposed Solution

### 1. Tmux Session Manager (`tmux_manager.py`)
Implement Python bindings for the `tmux` CLI:
- `start_session(session_name, working_dir, startup_command)`
- `list_sessions()`
- `attach_session(session_name)`
- `kill_session(session_name)`

### 2. Operator Interface CLI
Add the following commands:
- `dopetask tmux start <tp_id>`: Creates a new tmux session named after the `tp_id`, mounts the correct `worktree`, and drops the user into a shell ready to run `dopetask tp exec`.
- `dopetask tmux attach <tp_id>`: Reattaches to the backgrounded execution.
- `dopetask tmux ls`: Lists all active TP execution sessions.

### 3. Execution Integration
Add an option to `dopetask tp exec` (e.g., `--daemon` or `--tmux`) that automatically spins up a detached tmux session and pipes the execution logs into it, freeing up the primary terminal.

## Verification & Testing
- Verify session creation, listing, and destruction using the CLI.
- Ensure isolated environments (e.g., environment variables, working directories) are correctly passed into the tmux session.
- Ensure the commands degrade gracefully if `tmux` is not installed on the host system.

## Migration & Rollback
Additive UX changes. Requires `tmux` as an external system dependency (will be documented). Rollback by removing the CLI registration.
