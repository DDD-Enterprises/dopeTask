# Implementation Plan: Multi-Mode Execution

## 1. Implementation Goals
Transition the `dopeTask` kernel from a monolithic "script-runner" to a formal "Adapter-Executor" architecture.
- Enable strictly typed outcomes via `ExecutionResult`.
- Support local shell runners and multi-provider agents (Gemini, Claude).

## 2. Phased Roadmap
**WARNING:** DO NOT implement all phases at once. Each phase must be fully validated and committed before the next begins.

### Phase 1: The Contract (In Progress)
Establish types and the core executor class.
- **Affected:** `src/dopetask/pipeline/task_runner/types.py`, `src/dopetask/pipeline/task_runner/executor.py`, `src/dopetask_adapters/gemini/executor.py`.
- **Testing:** Unit tests for `TaskExecutor` with a `MockAdapter`.

### Phase 2: Kernel Orchestration Refactor
Replace legacy logic in the execution engine.
- **Affected:** `src/dopetask/ops/tp_exec/engine.py`.
- **Testing:** Integration tests comparing legacy output to the new `EXEC.json`.
- **Rollout:** **Shadow Mode** - write both legacy and new formats concurrently.

### Phase 3: Multi-Mode Support
Introduce `ShellAdapter` for non-agent steps.
- **Affected:** `src/dopetask_adapters/shell/`, `src/dopetask/core/tp_parser.py`.
- **Testing:** E2E test of a Task Packet with mixed `shell` and `agent` steps.

### Phase 4: Observability and Telemetry
Enrich proof bundles with traces and metrics.
- **Affected:** `src/dopetask/obs/`, `src/dopetask/pipeline/task_runner/executor.py`.
- **Testing:** Verify `METRICS.json` generation.

## 3. Backward Compatibility
Adapters will temporarily return a tuple `(list[ExecutionResult], legacy_proof_path)` to ensure the `ProofAggregator` and existing skills (e.g., `dopetask-proof-review`) remain functional. Legacy fields in `normalized_output` will be maintained during the transition.

## 4. Risks and Mitigations
- **Risk:** Breaking the current stable execution path.
- **Mitigation:** Comprehensive shadow-mode testing and incremental feature flagging.
- **Risk:** High complexity in multi-agent orchestration.
- **Mitigation:** Strict phase boundaries and mandatory unit testing for all new adapters.
