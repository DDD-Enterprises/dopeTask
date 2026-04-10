# Repair Batch 1 Summary

## Repaired docs
- docs/10_ARCHITECTURE.md
- docs/11_PUBLIC_CONTRACT.md
- docs/12_ROUTER.md
- docs/23_INTEGRATION_GUIDE.md
- docs/22_WORKFLOW_GUIDE.md

## What was corrected
- default operator workflow is now consistently centered on `tp series`
- route/orchestrate is preserved as active but non-default
- router is clarified as planning/handoff, not default execution
- integration surfaces are better separated
- workflow guide no longer instructs use of known drifted `tp series import`

## What remains open
- schema-authority wording still needs review in docs that reference `docs/schemas/...`
- orchestrator v0 role may still need stronger explicit wording in some surfaces
- broader artifact taxonomy remains distributed across docs
- runtime/help verification pass should still be run before calling the docs fully reconciled

## Recommended next pass
1. quick cross-doc consistency scan
2. schema-authority cleanup targets
3. operator/runtime-help reconciliation pass
