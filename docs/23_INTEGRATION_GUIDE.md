# Integration Guide: Connecting dopeTask to Your Ecosystem

This guide provides patterns for integrating `dopeTask` with CI/CD pipelines, custom agents, and external systems.
For new work, `tp series` is the default integration path.
Low-level and non-default surfaces still exist, but they remain separate planes and should not be treated as interchangeable.

Use this as the canonical integration reference for current `0.5.x` behavior. For packet structure, see `13_TASK_PACKET_FORMAT.md`. For migration from older execution assumptions, see `24_UPGRADE_GUIDE.md`.

## CI/CD Integration

`dopeTask` is optimized for headless execution.
For new work, prefer the `tp series` workflow as the first-choice integration surface.

### GitHub Actions Pattern
Use the following pattern to execute one ready Task Packet in a workflow:

```yaml
jobs:
  execute-packet:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dopeTask
        run: pip install dopetask
      - name: Execute Packet
        run: |
          dopetask tp series exec ${{ github.event.client_payload.packet_path }}
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## External Agent Integration

The current low-level JSON TP executor is a separate specialist surface.
Its runtime-supported execution surface now includes both `gemini` and `codex`.
It is still a different plane from the default `tp series` workflow and from route/orchestrate runners.
Strict repo-aware packets can adopt `dopetask_schemas/task_packet.strict.schema.json` when a repo wants mandatory `repo_binding`, `execution`, `commit.verify`, and Gemini PAL rules.

To add another agent profile:

1. **Implement the executor**: add an executor under `src/dopetask_adapters/<agent>/` that can run a compiled JSON TP and return the raw proof path.
2. **Register the agent slug**: update `src/dopetask/ops/tp_exec/engine.py` so `execute_task_packet()` recognizes the new `--agent` value.
3. **Keep the packet contract stable**: supervisors still emit JSON packets matching `dopetask_schemas/task_packet.schema.json`. Strict repo-aware packets may add `repo_binding`, `execution`, and `pr` metadata, but the packaged generic schema remains the runtime authority. Use the strict policy schema only when the repo explicitly wants the stricter contract.
4. **Use the series workflow as the entrypoint**: new work should still run through `dopetask tp series exec ... --agent <agent> [--model <model>]`.

Mutating entrypoints refuse wrong-repo execution before worktree or PR mutation. If a packet declares `repo_binding.require_identity_match = true`, the active repo must match the binding before `tp exec`, `tp series exec`, `tp series finalize`, or `tp git` PR/merge operations proceed.

Route/orchestrate surfaces remain separate from both `tp series` and low-level `tp exec`.
They provide route planning and runner-based execution behavior, not the default integration path for new work.

## Proof Data Consumption

Every `dopeTask` execution produces a canonical proof bundle at `proof/<TP_ID>_PROOF_BUNDLE.json`. External systems can ingest these bundles to:
- Verify deployment integrity.
- Generate automated release notes.
- Audit AI-driven code changes.

```json
{
  "tp_id": "TP-123",
  "status": "VALIDATED",
  "packet_family": "implementation",
  "lane": "default",
  "summary": {
    "result": "Success",
    "key_findings": ["All tests passed"]
  },
  "artifacts": {
    "archive": {
      "present": true,
      "filename": "TP-123_PROOF_ARCHIVE.zip"
    }
  }
}
```

If you need a higher-level derived object for Dopemux, use the schema documented in `docs/integrations/dopetask/ADAPTER_SCHEMA.md`. That envelope is an integration-side normalization layer, not the canonical dopeTask proof artifact.

For proof bundle semantics, use `docs/proof/PROOF_BUNDLE_CONTRACT.md` and `docs/proof/DOPETASK_BUNDLE_SCHEMA.md` as the authority.

## Programmatic CLI Usage

You can read the authoritative series ledger in `out/tp_series/` directly or call `dopetask tp series status <series-id>`.

```python
import json
from pathlib import Path

state = json.loads(Path("out/tp_series/my-series/SERIES_STATE.json").read_text())
print(f"Completed packets: {sum(1 for packet in state['packets'].values() if packet['status'] == 'completed')}")
print(f"Tracked packets: {sorted(state['packets'])}")
```
