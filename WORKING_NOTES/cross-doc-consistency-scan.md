# Cross-Doc Consistency Scan

## Docs reviewed
- docs/10_ARCHITECTURE.md
- docs/11_PUBLIC_CONTRACT.md
- docs/12_ROUTER.md
- docs/23_INTEGRATION_GUIDE.md
- docs/22_WORKFLOW_GUIDE.md

## Consistency checks

### 1. Default operator workflow
Question:
- Do all relevant docs now consistently present `tp series` as the default operator workflow?

Result:
- pass

Notes:
- Yes. `10_ARCHITECTURE.md`, `11_PUBLIC_CONTRACT.md`, `22_WORKFLOW_GUIDE.md`, and `23_INTEGRATION_GUIDE.md` explicitly call `tp series` the default operator or integration workflow, while `12_ROUTER.md` limits itself to the router plane and explicitly says it is not the default execution workflow.

### 2. Route/orchestrate status
Question:
- Do all relevant docs consistently treat route/orchestrate as active but non-default?

Result:
- partial

Notes:
- The architecture, public-contract, router, and integration docs consistently present route/orchestrate as active but non-default. `22_WORKFLOW_GUIDE.md` preserves the default/non-default split, but it refers only to "other active planes" rather than naming route/orchestrate directly, so the cross-doc story is aligned but not stated with the same precision everywhere.

### 3. Router boundary
Question:
- Is router consistently described as planning/handoff rather than default execution?

Result:
- pass

Notes:
- Yes. `12_ROUTER.md` defines the router as a planning and handoff surface that writes route artifacts, and both `10_ARCHITECTURE.md` and `23_INTEGRATION_GUIDE.md` reinforce that it is a separate non-default plane rather than the normal execution path.

### 4. Public contract vs default workflow
Question:
- Are public contract surfaces clearly distinguished from the default operator workflow?

Result:
- pass

Notes:
- Yes. `11_PUBLIC_CONTRACT.md` separates default operator inputs and outputs from active non-default public surfaces, and the architecture, workflow, and integration docs keep that distinction intact by treating `tp series` as the default operator path without pretending it is the only public contract surface.

### 5. Artifact-surface distinctions
Question:
- Are route artifacts, run/proof artifacts, and series-state artifacts kept meaningfully distinct?

Result:
- pass

Notes:
- Yes. `12_ROUTER.md` isolates route-plane artifacts under `out/dopetask_route/`, `23_INTEGRATION_GUIDE.md` distinguishes canonical proof bundles from higher-level integration envelopes and from `out/tp_series/` series-state data, and `11_PUBLIC_CONTRACT.md` keeps route outputs separate from default series/proof outputs.

### 6. Known drifted commands
Question:
- Do any of these repaired docs still instruct users to use known drifted or non-live commands?

Result:
- pass

Notes:
- No clear drift remains in this five-doc set. `22_WORKFLOW_GUIDE.md` uses live `tp series` commands, `12_ROUTER.md` documents live route subcommands, and the mentions of older paths in `22_WORKFLOW_GUIDE.md` are framed as upgrade or intentional manual references rather than the default instruction path.

## Net assessment
- mostly coherent

## Remaining cleanup candidates
- `docs/22_WORKFLOW_GUIDE.md` could name route/orchestrate explicitly when it says other active planes still exist, to match the sharper wording used in the other four docs.
- The set is coherent on default workflow and artifact boundaries, but only `docs/23_INTEGRATION_GUIDE.md` gives the full proof-bundle vs derived-envelope vs series-state distinction in one place.
- `docs/12_ROUTER.md` still uses the older markdown `PACKET.md` surface for router inputs; that appears intentional and live, but it remains a terminology seam beside the JSON `tp series` story.

## Recommendation
- move to schema-authority cleanup
