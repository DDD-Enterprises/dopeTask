# Task Packet Format

This document defines the JSON `TaskPacket` contract for new dopeTask work.

Legacy markdown packet docs remain available for manual maintainer workflows, but the default supervisor path is JSON-only and runs through `dopetask tp series`.

## Required top-level fields

Every Task Packet must be valid JSON and include:

- `id`
- `target`
- `steps`

The parser rejects packets that fail schema validation before any worktree or git mutation occurs.

Runtime schema authority for Task Packets is `dopetask_schemas/task_packet.schema.json`.
Runtime validation uses packaged schemas through `src/dopetask/utils/schema_registry.py` and `src/dopetask/schemas/validator.py`, not the docs tree.
If you reference `docs/schemas/task_packet.schema.json`, treat it as a documentation mirror rather than the runtime validation source.

## Core execution fields

- `project`: optional project name, defaults to `dopetask`
- `invariants`: optional strings that must remain true across the packet
- `steps`: ordered implementation steps

Each step must include:

- `id`
- `task`
- `validation`

Optional step fields:

- `requirements`
- `commands`
- `expected_files`
- `context_files`

`validation` must be non-empty. If you cannot verify a step with a shell command, the step is underspecified.

## Series fields

New supervisor-driven work should include:

- `depends_on: string[]`
- `series.id`
- `series.base_branch`
- `series.parent_tp_id`
- `series.final_packet`
- `commit.message`
- `commit.allowlist`
- `commit.verify` (optional)

These fields define both packet readiness and git ancestry:

- `depends_on` controls when a packet is allowed to execute
- `series.parent_tp_id` selects the single parent branch used for git ancestry
- root packets use `series.parent_tp_id = null`
- if `series.parent_tp_id` is set, it must also appear in `depends_on`
- multi-branch fan-in happens in an explicit integration packet, not through implicit merging

## Runtime flow

The default execution flow for JSON packets is:

1. Author one or more JSON packets with shared `series.id`, then save each packet JSON to a file.
2. Run ready packets with `dopetask tp series exec <packet.json> --agent <agent>`
3. Inspect proof bundles and the authoritative ledger with `dopetask tp series status <series-id>`
4. Open one PR for the completed series with `dopetask tp series finalize <series-id> --title "..."`

Each JSON TP runs in its own worktree, creates one commit, and records its outcome in `out/tp_series/<series-id>/SERIES_STATE.json`.

## Compatibility and versioning policy

- Additive changes to the packet format should remain backward-compatible where possible.
- Contract-breaking schema changes require a major version bump of dopeTask.
- `dopetask_schemas` package versioning is separate from the dopeTask app version.

## Security Considerations

Task Packet commands currently execute via `subprocess.run(shell=True)`. This allows for complex shell pipelines but requires that Task Packets originate from a **trusted source** (e.g., a verified Supervisor LLM).

- **Isolation**: Each Task Packet runs in a dedicated git worktree to prevent side effects on the primary repository state.
- **Auditability**: All commands and their outputs are recorded in deterministic proof bundles for post-execution auditing.
