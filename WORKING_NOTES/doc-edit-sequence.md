# Doc Edit Sequence

## 1. docs/10_ARCHITECTURE.md

### Opening boundary note to add
This doc covers the architecture planes of dopeTask as a whole.  
It does not by itself define the default day-to-day operator workflow.  
`tp series` is the default operator workflow; route/orchestrate remains an active but non-default architecture plane.

### Key paragraph(s) to reframe
- Any opening or summary language that makes the route/orchestrate spine sound like the single current execution story
- Any language implying “the kernel” has one universal execution path when the repo has multiple active planes

### Claims to preserve
- determinism
- refusal-first behavior
- artifact-first execution record
- route/orchestrate as a real active plane
- kernel-boundary philosophy

### Claims to delete or weaken
- any implication that orchestrator v0 is the main operator path
- any implication that one spine explains all current runtime surfaces
- any wording that overstates current auto-mode practicality for orchestrator v0 in this checkout

---

## 2. docs/11_PUBLIC_CONTRACT.md

### Opening boundary note to add
This doc describes public contract surfaces across dopeTask.  
Not all public surfaces are the default operator path.  
For current operator workflow, `tp series` is the default; route/orchestrate is an active non-default contract surface.

### Key paragraph(s) to reframe
- the inputs/outputs section if it centers `.dopetask/runtime/availability.yaml` and route artifacts as if they define the main current workflow
- any summary that implies one public contract surface dominates all operator use

### Claims to preserve
- explicit inputs/outputs matter
- refusal/reporting behavior matters
- route/orchestrate artifacts are still real contract surfaces
- deterministic contract framing

### Claims to delete or weaken
- route/orchestrate as the only meaningful public contract
- availability config as the main prerequisite for the default operator workflow
- any suggestion that current checkout orchestrator auto mode is broadly usable

---

## 3. docs/12_ROUTER.md

### Opening boundary note to add
This doc covers the router plane.  
The router is an active, non-default planning/handoff surface.  
It is not the default operator execution workflow.

### Key paragraph(s) to reframe
- any introductory language that leaves router status ambiguous relative to `tp series`
- any wording that blurs route planning with packet execution

### Claims to preserve
- router is active
- routing is deterministic
- route and handoff artifacts are valid outputs
- router remains separate from execution

### Claims to delete or weaken
- any implication that router planning is the main execution story
- any ambiguity between route artifacts and run/proof/series artifacts

---

## 4. docs/23_INTEGRATION_GUIDE.md

### Opening boundary note to add
This doc covers integration patterns for current dopeTask surfaces.  
For new work, `tp series` is the default integration path.  
Low-level and non-default surfaces still exist but should be treated as separate planes.

### Key paragraph(s) to reframe
- any sections that blur `tp series`, `tp exec`, and route/orchestrate
- any low-level executor language that feels broader than current proven support

### Claims to preserve
- `tp series` as the default integration story
- proof bundles and series state as important integration artifacts
- low-level surfaces still exist
- external agent integration remains a valid topic

### Claims to delete or weaken
- any implication that all execution surfaces are equally recommended
- any implication that low-level agent/runtime support is broader than proven
- any suggestion that route/orchestrate and `tp series` are interchangeable

---

## 5. docs/22_WORKFLOW_GUIDE.md

### Opening boundary note to add
This doc covers the default operator workflow.  
Other active planes still exist in dopeTask, but this guide is specifically about the modern `tp series` workflow.

### Key paragraph(s) to reframe
- only consistency wording if needed after higher-conflict docs are repaired
- any phrasing that accidentally implies other planes do not exist

### Claims to preserve
- `tp series` is the canonical modern operator workflow
- series status/finalize flow stays central
- distinction from older/manual flows remains explicit

### Claims to delete or weaken
- any implication that other active surfaces are fake or gone
- any wording that universalizes `tp series` behavior across every plane
