# Doc Repair Execution Order

## 1. docs/10_ARCHITECTURE.md

### Input prompt to use
Use the prompt from `WORKING_NOTES/doc-edit-prompts.md` for `docs/10_ARCHITECTURE.md`.

### Source notes to keep open while editing
- `WORKING_NOTES/execution-surface-classification.md`
- `WORKING_NOTES/doc-repair-rules.md`
- `WORKING_NOTES/doc-repair-briefs.md`
- `WORKING_NOTES/doc-edit-sequence.md`

### Validation check after edit
- opening boundary note present
- `tp series` explicitly named as default operator workflow
- route/orchestrate preserved as active but non-default
- no wording implying one universal current execution spine
- no wording implying orchestrator v0 auto mode is operational in this checkout

### Stop conditions
- if preserving determinism/refusal/kernel-boundary concepts requires large structural rewrite
- if the edit starts changing adjacent docs by implication
- if the doc begins drifting into product workflow detail better owned by `docs/22_WORKFLOW_GUIDE.md`

---

## 2. docs/11_PUBLIC_CONTRACT.md

### Input prompt to use
Use the prompt from `WORKING_NOTES/doc-edit-prompts.md` for `docs/11_PUBLIC_CONTRACT.md`.

### Source notes to keep open while editing
- `WORKING_NOTES/execution-surface-classification.md`
- `WORKING_NOTES/doc-repair-rules.md`
- `WORKING_NOTES/doc-repair-briefs.md`
- `WORKING_NOTES/doc-edit-sequence.md`

### Validation check after edit
- opening boundary note present
- `tp series` identified as default operator workflow
- active public surfaces vs default operator path are distinguished
- route/orchestrate artifacts remain real public surfaces
- `.dopetask/runtime/availability.yaml` is not framed as the main prerequisite for default operator flow

### Stop conditions
- if the doc begins absorbing architecture-plane explanation better owned by `docs/10_ARCHITECTURE.md`
- if the contract becomes vague in order to avoid surface distinctions
- if the edit starts rewriting integration guidance better owned by `docs/23_INTEGRATION_GUIDE.md`

---

## 3. docs/12_ROUTER.md

### Input prompt to use
Use the prompt from `WORKING_NOTES/doc-edit-prompts.md` for `docs/12_ROUTER.md`.

### Source notes to keep open while editing
- `WORKING_NOTES/execution-surface-classification.md`
- `WORKING_NOTES/doc-repair-rules.md`
- `WORKING_NOTES/doc-repair-briefs.md`
- `WORKING_NOTES/doc-edit-sequence.md`

### Validation check after edit
- opening boundary note present
- router explicitly labeled active, non-default
- router not described as default operator execution workflow
- route planning clearly separated from packet execution
- route artifacts clearly separated from run/proof/series artifacts

### Stop conditions
- if the edit starts demoting router into false legacy status
- if the edit starts importing default workflow detail better owned by `docs/22_WORKFLOW_GUIDE.md`
- if the doc loses clarity about router determinism and handoff outputs

---

## 4. docs/23_INTEGRATION_GUIDE.md

### Input prompt to use
Use the prompt from `WORKING_NOTES/doc-edit-prompts.md` for `docs/23_INTEGRATION_GUIDE.md`.

### Source notes to keep open while editing
- `WORKING_NOTES/execution-surface-classification.md`
- `WORKING_NOTES/doc-repair-rules.md`
- `WORKING_NOTES/doc-repair-briefs.md`
- `WORKING_NOTES/doc-edit-sequence.md`

### Validation check after edit
- opening boundary note present
- `tp series` identified as default integration path for new work
- `tp exec`, route/orchestrate, and proof/state artifacts clearly distinguished
- no implication that all execution surfaces are equally recommended
- no implication of broader runtime support than is currently proven

### Stop conditions
- if the edit starts re-explaining architecture theory better owned by `docs/10_ARCHITECTURE.md`
- if the doc starts collapsing specialist surfaces into one generic execution story
- if proof/state distinctions become muddier instead of clearer

---

## 5. docs/22_WORKFLOW_GUIDE.md

### Input prompt to use
Use the prompt from `WORKING_NOTES/doc-edit-prompts.md` for `docs/22_WORKFLOW_GUIDE.md`.

### Source notes to keep open while editing
- `WORKING_NOTES/execution-surface-classification.md`
- `WORKING_NOTES/doc-repair-rules.md`
- `WORKING_NOTES/doc-repair-briefs.md`
- `WORKING_NOTES/doc-edit-sequence.md`

### Validation check after edit
- boundary note present or tightened
- `tp series` remains the canonical modern operator workflow
- distinction from older/manual paths remains explicit
- no implication that other active surfaces are fake or gone
- changes remain minimal compared with higher-conflict docs

### Stop conditions
- if the edit grows beyond consistency cleanup
- if the doc starts taking on architecture/public-contract repair work
- if the workflow guide becomes responsible for explaining every execution plane

---

## Execution rule

Edit in this order:
1. `docs/10_ARCHITECTURE.md`
2. `docs/11_PUBLIC_CONTRACT.md`
3. `docs/12_ROUTER.md`
4. `docs/23_INTEGRATION_GUIDE.md`
5. `docs/22_WORKFLOW_GUIDE.md`

Reason:
- repair the docs that misstate the default story first
- then sharpen active non-default boundaries
- then do consistency cleanup last

## Global stop rule

If an edit requires changing the repo-wide classification itself, stop editing and return to the working notes rather than improvising new doctrine inside the doc.
