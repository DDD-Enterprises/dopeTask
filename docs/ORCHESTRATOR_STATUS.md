# Operational Status: Orchestrator v0

**Status:** NON-FUNCTIONAL (AUTO MODE)
**Date:** 2026-04-09
**Environment:** `dopeTask` root checkout

## Summary
The `orchestrate` command (Orchestrator v0) is currently in a "Fail-Closed" state for automated execution. While the command surface is public and the kernel logic is active, it cannot execute work in `auto` mode in the current environment.

## Critical Blockers
1. **Missing Configuration:** The required `.dopetask/runtime/availability.yaml` file is missing. The router refuses to plan without this authoritative source of runner/model availability.
2. **Refusal-Only Stubs:** All runners registered in the orchestrator plane (`claude_code`, `codex_desktop`, `copilot_cli`, `google_jules`) are implemented as "v0 deterministic refusal stubs." They are hardcoded to return `RUNNER_NOT_IMPLEMENTED`.
3. **Adapter Mismatch:** The functional `GeminiAdapter` used by the newer `tp series` workflow is not registered in the `RUNNER_ADAPTERS` registry used by Orchestrator v0.

## Intended Role
Orchestrator v0 currently serves as the **Normative Reference Implementation** for the "Execution Spine." It is the authoritative site for:
- Deterministic route planning logic.
- The "Refusal with Evidence" contract.
- Manual handoff chunk generation.

For active supervisor-led automation, the project has transitioned to the `tp series` (Task Packet Series) workflow, which utilizes a separate execution engine (`src/dopetask/ops/tp_exec/engine.py`).
