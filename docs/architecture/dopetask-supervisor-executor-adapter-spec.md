# Architecture Spec: Supervisor, Executor, and Adapter Contract

## Overview
This document defines the standardized relationship between the `dopeTask` execution kernel and provider-specific adapters. It introduces a formal contract for execution outcomes to ensure consistent validation and fail-fast behavior across all agent profiles.

## Core Components

### 1. ExecutionResult (The Contract)
Located in `src/dopetask/pipeline/task_runner/types.py`, this dataclass is the authoritative outcome format for every task step.

**Fields:**
- `step_id`: Unique identifier for the step.
- `status`: `succeeded`, `failed`, `pending`, or `running`.
- `execution_mode`: `shell` (direct execution) or `agent` (LLM-orchestrated).
- `raw_output`: Unprocessed output log (JSON-stringified trace for agents).
- `normalized_output`: Standardized dictionary containing `files_created`, `commands_run`, and `validation_passed`.
- `metrics`: Dictionary for execution telemetry (token usage, duration).
- `error`: Optional string containing failure details.

### 2. TaskExecutor (The Kernel)
Located in `src/dopetask/pipeline/task_runner/executor.py`, the `TaskExecutor` acts as the kernel-side gatekeeper.

**Responsibilities:**
- Accepts an implementation of the `Adapter` protocol.
- Invokes the adapter's `run_tp` method.
- Validates that the adapter returns compliant `ExecutionResult` objects.
- Enforces a "Fail-Closed" policy: Immediate termination and error reporting upon the first failed step.

### 3. The Adapter Protocol
Adapters provide the bridge between `dopeTask` and specific providers (e.g., Gemini, Claude).

**Method Contract:**
- `run_tp(tp: dict) -> tuple[list[ExecutionResult], str]`
  - Returns a sequence of results for the kernel to process.
  - Returns the path to the legacy proof bundle for backward compatibility with the `ProofAggregator`.

## Design Principles
1. **Provider Isolation:** Adapters must not leak provider-specific fields (e.g., `finish_reason`, `usage_metadata`) into the `normalized_output`.
2. **Empirical Validation:** The `status` of a result must be tied to the successful execution of `validation` commands defined in the Task Packet.
3. **Atomic Finality:** A Task Packet is only considered `succeeded` if all steps in the sequence return a `succeeded` status.
