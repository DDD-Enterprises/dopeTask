# Integration Guide: Connecting dopeTask to Your Ecosystem

This guide provides patterns for integrating `dopeTask` with CI/CD pipelines, custom agents, and external systems.

## CI/CD Integration

`dopeTask` is optimized for headless execution.

### GitHub Actions Pattern
Use the following pattern to execute a Task Packet series in a workflow:

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

To integrate a new AI agent (e.g., GPT-4, Claude) with the `dopeTask` execution kernel:

1. **Implement an Adapter**: Create a new class in `src/dopetask_adapters/` following the `BaseExecutor` interface.
2. **Register the Agent**: Update the router in `src/dopetask/ops/tp_exec/engine.py` to recognize your agent slug.
3. **Task Packet Hand-off**: Configure your supervisor to emit JSON packets matching the `task_packet.schema.json`.

## Proof Data Consumption

Every `dopeTask` execution produces a `PROOF_BUNDLE.json`. External systems can ingest these bundles to:
- Verify deployment integrity.
- Generate automated release notes.
- Audit AI-driven code changes.

```json
{
  "tp_id": "TP-123",
  "status": "VALIDATED",
  "summary": {
    "result": "Success",
    "key_findings": ["All tests passed"]
  }
}
```

## Programmatic CLI Usage

You can parse the JSON output of most `dopetask` commands using the `--json` flag (where supported) or by reading the state files in `out/tp_series/`.

```python
import json
from pathlib import Path

state = json.loads(Path("out/tp_series/my-series/SERIES_STATE.json").read_text())
print(f"Series Status: {state['status']}")
```
