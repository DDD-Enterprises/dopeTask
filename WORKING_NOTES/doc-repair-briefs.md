# Doc Repair Briefs

## 1. docs/10_ARCHITECTURE.md

### Current problem
- It presents the route/orchestrate kernel plane as the core execution spine in a way that reads like the main current execution story.
- That conflicts with the current classification where `tp series` is the default operator workflow and route/orchestrate is active but non-default.

### Required correction
- Reframe the doc so it explicitly distinguishes:
  - architecture-wide planes
  - the default operator workflow
  - non-default but active execution surfaces
- Keep route/orchestrate as an active architecture plane without implying it is the default operator path.

### What must stay true
- dopeTask is multi-plane, not one single clean execution spine
- route/orchestrate remains architecturally real and publicly present
- determinism, refusal, and artifact-first framing remain important

### What must not be implied
- that orchestrator v0 is the default day-to-day operator workflow
- that one plane fully describes all current execution behavior
- that current checkout auto-mode usability is established

---

## 2. docs/11_PUBLIC_CONTRACT.md

### Current problem
- It centers route artifacts and availability config as if they define the main public operating contract.
- That over-centers a non-default surface relative to current operator reality.

### Required correction
- Split public contract language into:
  - active public surfaces
  - default operator path
  - specialist/non-default paths
- Make room for `tp series`, series state, and proof-oriented operator reality without deleting route/orchestrate contract language.

### What must stay true
- route/orchestrate artifacts are still real public surfaces
- explicit inputs/outputs and refusal behavior still matter
- deterministic contract framing remains useful

### What must not be implied
- that route/orchestrate is the only meaningful public contract
- that `.dopetask/runtime/availability.yaml` is the main prerequisite for the default operator workflow
- that current checkout orchestrator auto mode is generally usable

---

## 3. docs/12_ROUTER.md

### Current problem
- It is mostly correct, but can still blur router planning with the main execution story.

### Required correction
- Add a clear boundary near the top:
  - router is an active, non-default planning/handoff plane
  - router is not the default operator execution workflow
- Clarify relationship to route artifacts versus run/proof/series artifacts.

### What must stay true
- router is active
- route artifacts and handoff artifacts are legitimate outputs
- routing remains deterministic and separate from execution

### What must not be implied
- that router planning equals packet execution
- that router is obsolete
- that route artifacts are the main operator record for all workflows

---

## 4. docs/23_INTEGRATION_GUIDE.md

### Current problem
- It is largely aligned, but boundaries between default series flow and specialist low-level surfaces can still be sharper.

### Required correction
- Preserve `tp series` as the default integration story for new work.
- Clarify the distinction between:
  - default series workflow
  - low-level `tp exec`
  - route/orchestrate-related surfaces
  - proof bundle consumption

### What must stay true
- `tp series` is the default integration path for new work
- low-level paths still exist
- proof bundles and series state are important integration artifacts

### What must not be implied
- that all execution surfaces are equally recommended
- that low-level executor paths have broader runtime support than is proven
- that route/orchestrate and series are interchangeable

---

## 5. docs/22_WORKFLOW_GUIDE.md

### Current problem
- No major classification problem; mostly a consistency target.

### Required correction
- Only perform consistency cleanup after higher-conflict docs are repaired.
- Ensure wording remains aligned with the repaired architecture/public-contract framing.

### What must stay true
- `tp series` is the canonical modern operator workflow
- packet series, status, and finalize flow stay central
- distinction from older/manual paths remains explicit

### What must not be implied
- that route/orchestrate has been deleted or is fake
- that specialist or legacy surfaces no longer exist
- that workflow language automatically applies to every execution plane
