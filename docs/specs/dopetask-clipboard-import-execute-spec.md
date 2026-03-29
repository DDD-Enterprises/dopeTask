# Spec: Command UX - Import and Execution

## 1. User-Facing Command Contract

### Import Command Variants
- **Clipboard Import:** `dopetask tp series import --auto`
  - Siphons the system clipboard for a Task Packet JSON using backends like `pbpaste` (macOS), `xclip` (Linux), or `powershell` (Windows).
- **Stdin Import:** `cat packet.json | dopetask tp series import -`
  - Reads the packet directly from standard input.
- **File Import:** `dopetask tp series import <path_to_file>`
  - Reads and validates a local JSON file.

### Overwrite Semantics
By default, importing a packet with an ID already present in the `SERIES_STATE.json` will fail.
- **Option:** `--overwrite` resets the existing packet state to `pending` and replaces the stored file.

### Packet Status Lifecycle
- **Running:** Packet is currently locked by an active worktree. Re-execution is blocked.
- **Completed:** Packet successfully committed and merged. Re-execution requires `--force`.
- **Failed:** Packet encountered an error during `exec`. Can be re-run with `--force` or updated via `import --overwrite`.

### Execution: Next-Runnable Selection
The command `dopetask tp series exec --next` uses these deterministic rules:
1. **DAG Eligibility:** Only packets with all `depends_on` IDs marked `completed` are eligible.
2. **Ordering:** Selection follows the alphabetical order of Packet IDs.
3. **Tie-Break:** Metadata `priority` (integer) overrides alphabetical ordering (highest priority first).

### Conflict and Starvation Rules
- **Cycle Detection:** Import or execution fails if a circular dependency is detected (`DAG_CYCLE_ERROR`).
- **Starvation:** Blocked packets (missing dependencies) are clearly labeled in the series status output.

### Cleanup and Force Behavior
- **Cleanup:** `dopetask tp series cleanup <series_id>` removes all stale worktrees and temporary branches.
- **Force Execution:** `--force` bypasses "Completed" or "Running" checks. **WARNING:** This can lead to divergent git history and is intended for recovery only.

## 2. Model Resolution
The kernel attempts to resolve the optimal model via `dopetask.router`.
- If a specific `--model` flag is provided to `exec`, it overrides both the router and the Task Packet's internal model metadata.

## 3. Anti-Footgun Warnings
- **Dirty Main:** Kernel refuses `exec` if the main repository has uncommitted changes (enforced by `SeriesDoctor`).
- **Worktree Marker:** Kernel checks for existing directory markers before creating a worktree to prevent overwriting unrelated work.

---

## 4. Implementation Notes (Internal Mechanics)
*These details are descriptive and subject to change.*
- **Task Packets:** Stored in `out/task_packets/<TP_ID>.json`.
- **Worktrees:** Created in `out/worktrees/<TP_ID>`.
- **Context Injection:** `SERIES_CONTEXT.json` provides the agent with parent dependency completion proof without full repository scanning.
