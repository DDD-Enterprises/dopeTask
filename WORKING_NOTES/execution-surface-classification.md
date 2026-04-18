# Execution Surface Classification

## 1. Default operator path

### JSON TP series workflow
Status: **default**
Surface:
- `dopetask tp series exec <packet.json> --agent <agent>`
- `dopetask tp series status <series-id>`
- `dopetask tp series finalize <series-id> --title "..."`
Why:
- current docs canon identifies this as the modern default operator workflow
- series state and proof bundle flow are the main current operator story
Notes:
- keep separate from orchestrator v0 and router surfaces
- low-level runtime currently recognizes `agent="gemini"` in the execution path

---

## 2. Active but non-default surfaces

### Orchestrator v0
Status: **active, non-default, reference/manual-handoff-oriented**
Surface:
- `dopetask orchestrate <packet.json>`
Why:
- remains a live CLI/runtime surface
- still matters architecturally as part of the deterministic route/orchestrate plane
- not demonstrated to be operational in auto mode in this checkout
Current checkout reality:
- `.dopetask/runtime/availability.yaml` is missing
- loader has no fallback
- `codex_desktop` runner is refusal-only
Operational interpretation:
- treat as a deterministic reference/manual-handoff surface
- do not treat auto mode as currently usable in this checkout

### Router plane
Status: **active, non-default**
Surface:
- `dopetask route init`
- `dopetask route plan`
- `dopetask route handoff`
- `dopetask route explain`
Why:
- still a public runtime surface
- owns deterministic route planning and handoff artifacts
Notes:
- route artifacts are separate from run artifacts
- do not confuse route planning with actual packet execution

### Low-level TP execution
Status: **active, specialist**
Surface:
- `dopetask tp exec ...`
Why:
- still a live low-level execution path
Notes:
- separate from series logic
- not the default operator workflow

---

## 3. Legacy/manual surfaces

### Worktree / commit-sequence / finish path
Status: **legacy/manual**
Surface:
- `dopetask wt ...`
- `dopetask commit-sequence ...`
- `dopetask finish ...`
Why:
- maintainer/manual path
- explicitly non-default in current docs

### `tp git` workflow
Status: **legacy/manual**
Surface:
- `dopetask tp git ...`
Why:
- preserved for manual intervention and older workflows
- not the recommended new-work path

---

## 4. Practical operator rule

Use:
- **tp series** for default supervised execution
- **Codex Desktop** for read-only repo inspection and analysis
- **orchestrator v0** as an architecture/reference/manual-handoff surface unless and until runtime setup proves otherwise
- **route** as a separate planning/handoff plane, not the main execution story

Avoid:
- treating orchestrator v0 auto mode as currently operational in this checkout
- conflating orchestrator v0, route, tp exec, and tp series
- calling Codex a viable orchestrator auto runner in current repo state
