# dopeTask 0.5.0 Integration Guide

The `0.5.0` release makes the JSON Task Packet series workflow the default integration path for new work. Downstream systems should treat `dopetask tp series` as the authoritative execution surface and use proof bundles plus the series ledger for audit and release gating.

## 1. Dependency Update

Ensure your project is pulling the current `0.5.0` version of `dopetask`.

### For standard `pip` environments

```bash
pip install dopetask==0.5.0
```

### For `uv` environments

```bash
uv add dopetask==0.5.0
```

### For local or editable builds

If a downstream project mounts `dopeTask` locally, ensure that checkout is on the `v0.5.0` tag before installing:

```bash
cd path/to/dopeTask
git fetch --tags
git checkout v0.5.0
pip install -e .
```

## 2. Using the Series Execution CLI

Downstream pipelines should no longer treat `dopetask tp series exec` as the default new-work path. Supervisors should author JSON Task Packets with explicit `depends_on`, `series`, and `commit` metadata, then execute each ready packet with:

```bash
dopetask tp series exec path/to/packet.json --agent gemini
```

The runner will:

1. Validate the packet schema before any git mutation.
2. Resolve the packet's branch ancestry from `series.base_branch` or `series.parent_tp_id`.
3. Create an isolated worktree for that packet.
4. Run the low-level implementation engine inside that worktree.
5. Execute `commit.verify`, stage only `commit.allowlist`, and create one commit for that packet.
6. Record the packet outcome in the series ledger.

### Runtime rules to preserve

- `depends_on` controls readiness.
- `series.parent_tp_id` selects the single git parent branch.
- Root packets use `series.parent_tp_id = null`.
- Parallel execution is allowed only when all dependencies are already completed.
- Multi-branch fan-in must happen in an explicit integration packet.

## 3. Handling Output and Audit Surfaces

Each executed packet still emits a proof bundle:

1. **Bundle:** `proof/<TP-ID>_PROOF_BUNDLE.json`
2. **Archive:** `proof/<TP-ID>_PROOF_ARCHIVE.zip`

For series-aware integrations, downstream systems should also inspect the authoritative ledger:

```bash
dopetask tp series status <series-id>
```

This reads `out/tp_series/<series-id>/SERIES_STATE.json`, which is the canonical runtime state for packet completion, dependency closure, packet branches, and finalization status.

If a packet proof bundle reports `FAILED`, or the series ledger shows unmet dependencies or an incomplete final packet, the pipeline should halt and request operator intervention.

## 4. Finalizing the Series

Once the declared final packet has completed and every non-final packet is in its transitive dependency closure, open the single PR for the series with:

```bash
dopetask tp series finalize <series-id> --title "feat: example change"
```

This pushes the final packet branch and opens one PR against `series.base_branch`. Earlier packet commits are already part of that branch through the declared packet ancestry.

## 5. Optional Manual Session Handling

`dopetask tmux` remains available for manual or legacy flows that invoke `dopetask tp series exec --tmux`, but it is not part of the default JSON series workflow.

- List active agents: `dopetask tmux ls`
- Attach to a session: `dopetask tmux attach <TP-ID>`
- Terminate a session: `dopetask tmux kill <TP-ID>`

## 6. LLM Supervisor Onboarding

Integrating the execution kernel still requires re-onboarding LLM agents to act as supervisors rather than direct implementers.

### Mandatory agent instructions

1. Stop direct coding in new-work flows.
2. Author JSON Task Packets that conform to `docs/schemas/task_packet.schema.json`.
3. Delegate each ready packet with `dopetask tp series exec <packet.json> --agent <agent>`.
4. Audit proof bundles and the series ledger with `dopetask tp series status <series-id>`.
5. Finalize the completed series with `dopetask tp series finalize <series-id> --title "<pr title>"`.

### Instruction sources

- For web UI agents: provide `docs/llm/SUPERVISOR_SYSTEM_PROMPT.md`.
- For CLI or IDE agents: ensure the workspace includes the current `AGENTS.md` and agent-specific instruction files.

### Contract reference

Supervisors must adhere to the formal JSON schema located at:
`docs/schemas/task_packet.schema.json`
