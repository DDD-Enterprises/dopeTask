# Doc Repair Priority Order

## 1. Must clarify first

### docs/10_ARCHITECTURE.md
Why first:
- it presents the route/orchestrate kernel plane as the core execution spine
- this conflicts with the current execution-surface classification where `tp series` is the default operator path
Risk if left alone:
- readers will infer orchestrator v0 is the main current execution story
Repair goal:
- keep route/orchestrate as an active architecture plane
- stop implying it is the default operator workflow

### docs/11_PUBLIC_CONTRACT.md
Why first:
- it centers route artifacts and `.dopetask/runtime/availability.yaml` as public inputs/outputs
- this conflicts with the current classification where router/orchestrator are active but non-default
Risk if left alone:
- operators and integrators will misunderstand the main public workflow surface
Repair goal:
- distinguish route/orchestrate public contract from the default operator contract
- make room for `tp series` as the current operator-default path

---

## 2. Broadly right but needs framing fixes

### docs/12_ROUTER.md
Why here:
- mostly aligned as an active, non-default surface
- drift is mainly framing, not core misclassification
Risk if left alone:
- readers may still blur router planning with main execution workflow
Repair goal:
- explicitly state router is a separate active plane
- clarify that it is not the default operator execution story

### docs/23_INTEGRATION_GUIDE.md
Why here:
- largely aligned
- already says new work should use `tp series`
- low-level executor caveats appear mostly correct
Risk if left alone:
- integration readers may still miss the boundary between default series flow and specialist low-level surfaces
Repair goal:
- sharpen surface boundaries, not rewrite the whole guide

---

## 3. Can wait

### docs/22_WORKFLOW_GUIDE.md
Why it can wait:
- aligned with current execution-surface classification
- already centers `tp series` as the canonical modern workflow
Risk if left alone:
- low
Repair goal later:
- minor consistency pass only, after higher-conflict docs are repaired

---

## Repair sequencing rule

Order:
1. `docs/10_ARCHITECTURE.md`
2. `docs/11_PUBLIC_CONTRACT.md`
3. `docs/12_ROUTER.md`
4. `docs/23_INTEGRATION_GUIDE.md`
5. `docs/22_WORKFLOW_GUIDE.md` only for consistency cleanup

Reason:
- first fix the docs that misstate the default execution story
- then fix docs that are broadly correct but need clearer boundaries
- leave already-aligned workflow docs for last
