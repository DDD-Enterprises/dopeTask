# Surface Decision Open Questions

## Q1. Should orchestrator v0 remain publicly documented as active?
### Current evidence
- live CLI surface exists: `dopetask orchestrate <packet>`
- architecture/docs canon still treats route/orchestrate as an active plane
- current checkout does not demonstrate auto-mode operability
### Current best answer
- active in architecture/runtime surface
- not validated as practically usable auto path in this checkout
### Confidence
- Medium-High
### What would settle it
- stronger maintainer-facing doc or code comment explicitly classifying its role

---

## Q2. Should orchestrator v0 be explicitly described as manual/reference-oriented?
### Current evidence
- deterministic refusal/manual-handoff behavior is well defined
- auto mode depends on missing availability config in this checkout
- codex_desktop runner is refusal-only
### Current best answer
- yes, that is the safest current operator interpretation
### Confidence
- Medium-High
### What would settle it
- explicit operator docs or runtime help language

---

## Q3. Should planner selection pre-filter refusal-only runners?
### Current evidence
- planner scores candidates before kernel adapter viability check
- kernel refuses unknown/unusable runner only after selection
### Current best answer
- open design question, not yet decided
### Confidence
- Medium
### What would settle it
- code-level design decision on planner vs kernel responsibility boundary

---

## Q4. Should missing availability config be documented as a hard operational prerequisite?
### Current evidence
- canonical path is `REPO_ROOT/.dopetask/runtime/availability.yaml`
- missing file is a hard loader failure
- no fallback exists
### Current best answer
- yes, based on current runtime truth
### Confidence
- High
### What would settle it
- none needed beyond current code truth

---

## Q5. Should Codex remain analysis-only in current operator guidance?
### Current evidence
- Codex Desktop is useful for read-only inspection
- codex_desktop runner path is refusal-only in orchestrator plane
### Current best answer
- yes, in current repo state
### Confidence
- High
### What would settle it
- implemented runnable Codex adapter path
