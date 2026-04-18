# Docs Reconciliation Status

## Repaired docs
- docs/10_ARCHITECTURE.md
- docs/11_PUBLIC_CONTRACT.md
- docs/12_ROUTER.md
- docs/22_WORKFLOW_GUIDE.md
- docs/23_INTEGRATION_GUIDE.md
- docs/13_TASK_PACKET_FORMAT.md

## What is now coherent
- `tp series` is consistently presented as the default operator workflow
- route/orchestrate is consistently active but non-default
- router is consistently framed as planning/handoff, not default execution
- public contract surfaces are distinguished from default workflow
- schema runtime authority points to `dopetask_schemas/...`, with docs schema treated as a mirror

## Remaining known drift
- runtime help vs actual low-level executor implementation still needs code/runtime reconciliation
- broader repo surfaces outside this targeted batch may still contain stale references
- orchestrator v0 operational status remains checkout-sensitive because availability/runtime setup matters

## Boundary of this batch
- this batch repaired doc framing and authority wording
- it did not change code, CLI registration, or runtime behavior

## Recommended next phase
- return to architecture/implementation planning
- or do targeted code/runtime reconciliation for remaining drifted surfaces
