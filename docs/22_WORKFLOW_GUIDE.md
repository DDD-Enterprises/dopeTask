# Workflow Guide: The Task Packet Series Lifecycle

This guide details the modern, DAG-aware workflow for executing complex tasks using `dopeTask` series.

## Overview

The series workflow is designed for high-trust, deterministic execution of multi-step engineering tasks. Each step is represented by a JSON Task Packet (TP) and executes in an isolated git worktree.

Use this as the canonical workflow reference. If you are upgrading from older `tp exec` or `commit-sequence` habits, read `24_UPGRADE_GUIDE.md` alongside this guide. If you intentionally need the older manual path, see `20_WORKTREES_COMMIT_SEQUENCING.md`.

## Lifecycle Stages

### 1. Planning (Task Packet Authoring)
The Supervisor (AI or human) decomposes a high-level objective into atomic Task Packets.
- **Key Metadata**: `series.id`, `depends_on`, `commit.allowlist`.
- **Validation**: Every packet MUST have empirical verification commands.
- **Clipboard handoff**: If your supervisor emitted strict JSON to the clipboard, import it with `dopetask tp series import` before execution.

```bash
dopetask tp series import
```

### 2. Execution (`tp series exec`)
Invoke the kernel to execute a specific packet:
```bash
dopetask tp series exec path/to/packet.json --agent gemini
```
**Kernel Actions**:
1. **Doctor Check**: Ensures the primary repository is clean and on `main`.
2. **Worktree Isolation**: Creates a dedicated worktree and branch for the packet.
3. **Task Execution**: Runs the `commands` defined in the packet.
4. **Verification**: Runs the `validation` commands.
5. **Commit**: Stages and commits changes matching the `allowlist`.
6. **Cleanup**: Deterministically removes the worktree.

### 3. Monitoring (`tp series status`)
Track the progress of a series and its dependency graph:
```bash
dopetask tp series status <series-id>
```

### 4. Finalization (`tp series finalize`)
Once all packets in the series (including the one marked `final_packet: true`) are completed, push the changes and open a PR:
```bash
dopetask tp series finalize <series-id> --title "Implement Feature X" --body "Details..."
```

## Error Recovery

If a packet fails:
1. **Inspect Proofs**: Check `out/tp_series/<series-id>/packets/<tp-id>/` for logs and the `EXEC_ERROR.json` trace.
2. **Remediate**: Fix the issue in the Task Packet JSON.
3. **Resume**: Rerun `tp series exec` for the failed packet. The kernel will automatically pick up from the failed state.

## Best Practices

- **Atomic Commits**: Keep `commit.allowlist` narrow to ensure each packet produces a clean, focused commit.
- **Fail-Closed Validation**: Use `grep`, `test`, and exit codes in the `validation` block to ensure the task actually succeeded.
- **Explicit Dependencies**: Always list all immediate parent packets in `depends_on`.
