# TP-CORE-003: CLI Runner for Agent Execution

## Objective
Create a unified CLI interface (`dopetask tp exec`) to trigger the Task Packet (TP) parsing, normalization, and agent-specific execution flow. This command will link the `TPParser/Normalizer` (TP-CORE-002) with the `GeminiExecutor` (TP-CORE-001).

## Background & Motivation
We have the adapter layer and the normalization layer, but we lack a convenient entry point to trigger the end-to-end flow. Users need a CLI command to execute a Task Packet file using a specific agent profile.

## Key Files & Context
- `src/dopetask/ops/tp_exec/cli.py`: New CLI registration for the `exec` command.
- `src/dopetask/cli.py`: Update to register the new `tp exec` sub-command.
- `src/dopetask_adapters/gemini/executor.py`: (Reference) The orchestrator for execution.
- `src/dopetask/core/tp_parser.py`: (Reference) The parser and normalizer.

## Implementation Steps

### 1. Create `tp_exec` Module
- Create directory `src/dopetask/ops/tp_exec/`.
- Implement `src/dopetask/ops/tp_exec/cli.py` with a `typer` command:
  - `tp_file`: Path to the generic TP (JSON/YAML).
  - `--agent`: Agent profile (`gemini`, `codex`, `vibe`). Default: `gemini`.
  - `--dry-run`: Compile and show prompts without executing.
  - `--output-dir`: Optional override for proof output.

### 2. Implement Execution Orchestration
In `src/dopetask/ops/tp_exec/cli.py`:
- Use `TPParser.parse_file(tp_file)` to load the TP.
- Use `TPNormalizer.compile(tp, agent)` to get the compiled profile.
- Instantiate the appropriate executor based on the profile.
  - For `gemini`, use `GeminiExecutor`.
  - (Stub others for now).
- Call `executor.run_tp(compiled_tp)`.
- Capture and display the resulting proof path and status.

### 3. Register in Main CLI
Update `src/dopetask/cli.py`:
- Import `register` from `dopetask.ops.tp_exec.cli`.
- Call `register_tp_exec(tp_app)` in the initialization block.

## Verification & Testing
- Run `dopetask tp exec --help` to verify the command is registered.
- Run `dopetask tp exec sample_tp.json --agent gemini --dry-run` to see compiled prompts.
- Run a full execution with a dummy TP and verify the proof bundle is created.
- Verify fail-closed behavior if the TP is invalid or if a step fails.

## Migration & Rollback
- Additive changes in a new `ops/tp_exec` module.
- Minimal hook in `src/dopetask/cli.py`.
- Rollback by removing the hook and the new module.
