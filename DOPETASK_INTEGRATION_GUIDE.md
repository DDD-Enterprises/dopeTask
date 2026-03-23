# dopeTask 0.3.0 Integration Guide

The 0.3.0 release introduces a completely revamped deterministic execution architecture, featuring explicit LLM compiler pipelines and strict fail-closed state validation. This guide provides the necessary steps to integrate this new execution kernel into `Dopemux` or other downstream consumer projects.

## 1. Dependency Update

Ensure your project is pulling the latest `0.3.0` version of `dopetask`.

### For standard `pip` environments:
```bash
pip install dopetask==0.3.0
```

### For `uv` environments:
```bash
uv add dopetask==0.3.0
```

### For local/editable builds (Dopemux):
If Dopemux mounts `dopeTask` locally, ensure the submodule or linked directory is checked out to the `v0.3.0` tag.
```bash
cd path/to/dopeTask
git fetch --tags
git checkout v0.3.0
pip install -e .
```

## 2. Using the New Execution CLI

Downstream pipelines should no longer rely on manually parsing Task Packets and calling LLMs independently. You must now delegate task execution to the deterministic runner:

```bash
dopetask tp exec path/to/packet.json --agent gemini
```

### Key Flags:
- `--agent [gemini|codex|vibe]`: Targets the specific compiler profile. Note that `gemini` is currently the only fully supported strict executor.
- `--tmux`: Runs the agent loop inside a detached `tmux` session, freeing up the pipeline orchestrator and allowing human operators to attach safely if needed.
- `--dry-run`: Use this in CI or planning gates to emit the compiled prompt structure without executing any state mutations.

## 3. Handling Output (Observability)

The `dopetask tp exec` command now automatically aggregates proofs via the `ProofAggregator` layer. 

Downstream systems (like Dopemux routers) must now look for the unified bundle rather than scraping raw traces:
1. **The Bundle:** `proof/<TP-ID>_PROOF_BUNDLE.json`. This is the canonical review surface. Parse this for the `status` (VALIDATED or FAILED).
2. **The Archive:** `proof/<TP-ID>_PROOF_ARCHIVE.zip`. Contains the full forensic footprint and manifest.

If `status == "FAILED"`, the pipeline should halt and request operator intervention.

## 4. Operator Intervention (Tmux UX)

If you are using the `--tmux` execution flag in your orchestrator, operators can now interact with hanging or failed sessions natively using the new `dopetask tmux` group:

- **List active agents:** `dopetask tmux ls`
- **Intervene:** `dopetask tmux attach <TP-ID>`
- **Terminate:** `dopetask tmux kill <TP-ID>`

*Note: Ensure `tmux` (>= 3.0) is installed on the host running the execution agents.*
