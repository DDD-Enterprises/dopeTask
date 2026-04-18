# Operational Status: Orchestrator v0

> [!IMPORTANT] PRODUCTION STATUS: The `tp series` workflow is the authoritative and default operator plane.

**Status:** NORMATIVE REFERENCE (v0)
**Date:** 2026-04-10
**Environment:** `dopeTask` root checkout

## Summary
The `orchestrate` command (Orchestrator v0) now has a real `codex_desktop` runner path in `auto` mode, but it is still not a default production workflow and still depends on route availability data plus runner-specific output contracts.

## Critical Blockers
1. **Missing Configuration:** The required `.dopetask/runtime/availability.yaml` file is missing. The router refuses to plan without this authoritative source of runner/model availability.
2. **Partial Runner Coverage:** `codex_desktop` now has a real runner path, but the other registered runners remain refusal stubs.
3. **Plane Separation:** The low-level `tp exec` adapters and the orchestrator runner registry are still separate execution planes with different contracts and evidence surfaces.

## Intended Role
Orchestrator v0 currently serves as the **Normative Reference Implementation** for the "Execution Spine." It is the authoritative site for:
- Deterministic route planning logic.
- The "Refusal with Evidence" contract.
- Manual handoff chunk generation.
- Codex Desktop runner selection and deterministic runner artifact writing.

For active supervisor-led automation, the project has transitioned to the `tp series` (Task Packet Series) workflow, which utilizes a separate execution engine (`src/dopetask/ops/tp_exec/engine.py`).
