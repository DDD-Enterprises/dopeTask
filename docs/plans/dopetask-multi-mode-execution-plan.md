# Plan: Multi-Mode Execution Implementation

## Phase 1: The Contract (COMPLETED)
- [x] Define `ExecutionResult` schema.
- [x] Implement `TaskExecutor` with validation logic.
- [x] Refactor `GeminiAdapter` to the new contract.
- [x] Implement fail-fast kernel behavior.

## Phase 2: Orchestration Refactor (NEXT)
- [ ] Migrate `src/dopetask/ops/tp_exec/engine.py` to use `TaskExecutor` exclusively.
- [ ] Decouple `ProofAggregator` from the execution loop, feeding it via `ExecutionResult` streams.
- [ ] Implement `ShellAdapter` for non-agent, direct-command execution.

## Phase 3: Multi-Agent Support
- [ ] Refactor `ClaudeCodeAdapter` and `CodexCliAdapter` to implement the `ExecutionResult` protocol.
- [ ] Standardize the `runspec` preparation logic across all adapters.
- [ ] Add support for "Mixed-Mode" packets where some steps are `shell` and others are `agent`.

## Phase 4: Observability and Proofs
- [ ] Update `ProofAggregator` to support the `raw_output` trace format.
- [ ] Implement `METRICS.json` generation from the `ExecutionResult.metrics` field.
- [ ] Add real-time TUI progress tracking for multi-step execution using the `pending/running` status states.
