> **ADVISORY: Transitional Architecture Intent.** This document describes the target core abstraction. Note that in the current runtime, worktree lifecycle management is implemented in the `ops` layer (`tp series`) rather than the kernel/adapter boundary.

# Architecture Spec: Supervisor, Executor, and Adapter Contract

## 1. Purpose and Scope
This document defines the structural relationship between the `dopeTask` execution kernel and its external provider interfaces. The primary goal is to standardize task execution outcomes, enabling a "plug-and-play" architecture for LLM providers and local shell execution while maintaining a strictly deterministic core.

## 2. Deterministic Kernel Philosophy
The `dopeTask` kernel operates on the principle of **Atomic Finality**. 
- **Authority:** The kernel is the absolute source of truth for execution state.
- **Untrusted Adapters:** Adapters are treated as external shims. Their outputs MUST be normalized and validated by the kernel before being accepted.
- **Fail-Closed:** The kernel terminates execution at the first sign of an unhandled error or a failed validation command.
- **Evidence-First:** Execution is not complete until a proof bundle (EVIDENCE.md, artifacts, and logs) is successfully archived.

## 3. Core Definitions

### Supervisor (The Planner)
The high-level orchestration layer (Agent or User) that generates Task Packets. It is responsible for planning, but NOT for direct execution. It delegates the "Act" phase to the Kernel.

### TaskExecutor (The Kernel Authority)
Located in `src/dopetask/pipeline/task_runner/executor.py`. It is responsible for:
- Enforcing the `ExecutionResult` contract.
- Managing status transitions (`pending` -> `running` -> `succeeded`|`failed`).
- Orchestrating the "Fail-Closed" logic.

### Adapter (The Untrusted Shim)
A provider-specific shim (e.g., `GeminiAdapter`). It translates the generic Task Packet into provider-specific actions and normalizes the results into the kernel's format.

## 4. ExecutionResult Schema
Every task step must produce an `ExecutionResult` with the following fields:
- `step_id`: (str) Unique identifier for the step.
- `status`: (Literal["pending", "running", "succeeded", "failed"]) Current execution state.
- `execution_mode`: (Literal["shell", "agent"]) Direct execution or LLM-orchestrated.
- `raw_output`: (str) Unprocessed output log (JSON-stringified trace for agents).
- `normalized_output`: (dict) Standardized fields: `files_created`, `commands_run`, `validation_passed`.
- `metrics`: (dict) Telemetry (tokens, duration).
- `error`: (Optional[str]) Failure details.

## 5. Worktree Lifecycle Rules
1. **Creation:** A dedicated git worktree is created per Task Packet ID.
2. **Isolation:** Adapters execute strictly within this worktree.
3. **Validation:** Kernel runs validation commands post-adapter execution.
4. **Commit/Promotion:** Success triggers a commit in the worktree branch.
5. **Removal:** Worktree is pruned only after successful aggregation or explicit cleanup.

## 6. Degraded-Mode Transition Rules
If a step fails:
1. Kernel halts execution and locks the worktree.
2. User/Supervisor enters **Degraded Mode** to apply manual fixes or "Correction Packets".
3. The original failure evidence is preserved; correction is appended as a distinct event.

## 7. Gemini Classification: Transitional
`GeminiAdapter` is currently classified as **Transitional**. It implements the `ExecutionResult` contract but retains a deprecated return of the legacy proof path for backward compatibility. These transitional seams are temporary and will be removed once the kernel-side aggregator is fully implemented.

## 8. Open Risks and v1 Scope
- **Cross-Series Dependency:** Out of scope for v1. Each series is treated as a self-contained DAG.
- **Worktree Collisions:** Assumes unique TP IDs; kernel must verify directory availability before creation.
