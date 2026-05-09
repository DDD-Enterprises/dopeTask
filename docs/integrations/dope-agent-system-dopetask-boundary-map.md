# dopeTask ↔ dope-agent-system Authority Boundary Map

**TP:** TP-DT-DAS-INVESTIGATE-0001  
**Status:** Evidence-backed (HIGH confidence unless noted)  
**Source:** OWNERSHIP_MATRIX.json (TP-AGENT-SYSTEM-0011), DOPETASK_INTEGRATION_CONTRACT.md, runners/*, orchestrator/kernel.py

---

## Column Key

| Column | Meaning |
|--------|---------|
| Responsibility | The capability or decision |
| Current Owner | Who owns it today (proven from code/files) |
| Recommended Owner | Confirmed same (boundary already decided) |
| Evidence | File paths proving ownership |
| Risk if Wrong | Consequence of misassigning ownership |
| Design Implication | What this means for interactive executor / PAL Link integration |

---

## Boundary Matrix

| Responsibility | Current Owner | Recommended Owner | Evidence | Risk if Wrong | Design Implication |
|----------------|---------------|-------------------|----------|---------------|-------------------|
| Task Packet schema (generic) | dopeTask | dopeTask | `dopetask_schemas/task_packet.schema.json` | Schema drift, invalid packets accepted | dope-agent-system must not ship alternate schema files |
| Task Packet schema (strict, with repo_binding) | dopeTask | dopeTask | `dopetask_schemas/task_packet.strict.schema.json` | Bypass of repo-binding enforcement | Strict schema is the correct shape for supervised execution |
| Proof bundle schema and aggregation | dopeTask | dopeTask | `src/dopetask/obs/proof_aggregator.py`, `proof/standards/` | Proof fields diverge; audit cannot compare | ClaudeCode runner must emit ExecutionResult that aggregator can process |
| Series ledger (SERIES_STATE.json) | dopeTask | dopeTask | `src/dopetask/ops/tp_series/logic.py` | Ledger corruption, double-execution | Never write to SERIES_STATE.json from dope-agent-system |
| State machine transitions | dopeTask | dopeTask | `src/dopetask/orchestrator/kernel.py`, `pipeline/task_runner/runner.py` | Invalid state transitions cause stuck TPs | dope-agent-system REFERENCE docs may describe conceptual states; dopeTask enforces them |
| Policy engine (allowlist gate) | dopeTask | dopeTask | `src/dopetask/pipeline/compliance/gate.py` | Allowlist bypassed; unauthorized files written | Adapter prompt must not claim authority to write outside allowlist |
| Routing engine (planner, scoring, availability) | dopeTask | dopeTask | `src/dopetask/router/` | Wrong runner selected; suboptimal model routing | dope-agent-system's TOOL_ROUTING_MATRIX.md is a conceptual reference only |
| Next-runnable TP selection | dopeTask | dopeTask | `src/dopetask/ops/tp_series/cli.py` (--next flag) | Wrong TP executed; DAG ordering broken | Must never be delegated |
| Dependency resolution (DAG) | dopeTask | dopeTask | `src/dopetask/ops/tp_series/logic.py` | Cycle detection fails; starvation goes undetected | Must never be delegated |
| Worktree isolation and lifecycle | dopeTask | dopeTask | `src/dopetask/git/worktree.py`, `git/worktree_ops.py` | Concurrent worktree collision; uncommitted state lost | ClaudeCode adapter executes within kernel-created worktree |
| Repo identity and branch guard | dopeTask | dopeTask | `src/dopetask/guard/identity.py`, `git/branch_guard.py` | Wrong-repo mutation; main-branch contamination | Adapter cannot override identity check |
| Commit plan validation | dopeTask | dopeTask | `src/dopetask/git/commit_sequence.py` | Out-of-allowlist files committed | Adapter prompt must include narrow allowlist |
| Promotion-token gate and final acceptance | dopeTask | dopeTask | `src/dopetask/pipeline/promotion/gate.py`, `ops/tp_series/logic.py` | Unverified TPs promoted to ledger | Must never be delegated |
| Proof validation (adapter output) | dopeTask | dopeTask | `src/dopetask/pipeline/task_runner/executor.py` | Invalid adapter output accepted as valid | TaskExecutor.execute() always validates ExecutionResult |
| Refusal protocol and codes | dopeTask | dopeTask | `src/dopetask/orchestrator/kernel.py` (refusal routes) | Refusals not recorded; execution continues when it should stop | RUNNER_NOT_IMPLEMENTED is a valid refusal; adapter must surface it |
| ClaudeCode runner implementation | dopeTask (stub) | dopeTask | `src/dopetask/runners/claude_code.py` | Interactive executor not functional | **Primary integration gap.** Next TP must implement this runner. |
| Skill and command templates | dope-agent-system | dope-agent-system | `claude/`, `codex/`, `gemini/`, `copilot/` | Templates drift without governance | Templates may be injected pre-run or installed per release TP |
| Adapter templates (.agent-project/ family) | dope-agent-system | dope-agent-system | `templates/agent-project/`, `.agent-project/` | Projects bootstrap incorrect adapter structure | Consuming projects must bootstrap from dope-agent-system templates |
| Dry-run install planning | dope-agent-system | dope-agent-system | `scripts/plan_install_release.py`, `scripts/plan_project_adapter.py` | Install happens without dry-run proof | Dry-run plans are proof artifacts only; actual install blocked |
| Source bundle export (template content) | dope-agent-system | dope-agent-system | `scripts/build_source_bundle.py` | Template content mixed with runtime artifacts | Different from dopeTask's log-focused bundle export |
| Audit and supervisor prompt corpus | dope-agent-system | dope-agent-system | `claude/agents/`, `codex/skills/` | Prompts drift without template governance | May be consumed by ClaudeCode runner via prompt injection |
| Self-adapter governance | dope-agent-system (for its own repo) | dope-agent-system | `.agent-project/` | Policy applied to wrong repo | .agent-project/ is ONLY for dope-agent-system; consuming repos need their own |
| PAL thinking layer (analyze, planner, clink) | Neither (PAL MCP) | Neither (PAL MCP) | `docs/guides/dopetask-pal-integration-playbook.md` | PAL treated as execution transport | PAL is think/plan; dopeTask is execute; clink is PAL CLI context injection |
| dopeTask version pinning reference | dope-agent-system | dope-agent-system | `DOPETASK_VERSION_PIN.lock` | Reference docs drift from runtime | Pin must be refreshed via read-only dopeTask inspection when contracts change |

---

## Summary: Who Owns the Planes

```
Planning Plane:          PAL (analyze, planner, challenge)
                         Supervisor (human or AI authoring JSON task packets)
                         
Implementation Plane:    dopeTask (runner adapters: Codex ✅, ClaudeCode 🔴, Copilot, GoogleJules)
                         dope-agent-system (skill/prompt templates consumed by runners)
                         
Proof Plane:             dopeTask (proof_aggregator.py, ExecutionResult, proof/standards/)
                         dope-agent-system (extended proof fields for its own TPs — REFERENCE)
                         
Ledger Plane:            dopeTask (SERIES_STATE.json, promotion-token gate)
                         
Template/Asset Plane:    dope-agent-system (skills, commands, adapter templates, source bundles)
```

---

## Currently Unresolved

1. **Proof contract field divergence**: dope-agent-system's `PROOF_CONTRACT.md` requires `proof_backfilled`, `commit_hash_semantics`, `audit_submission_head`. dopeTask's runtime proof does not currently require these. If dopeTask adopts them, alignment is needed.

2. **`.agent-project/` consumption**: No dopeTask code currently reads `.agent-project/` adapter profiles. Model C (Adapter-Profile Consumption) requires new dopeTask code and explicit authority reconciliation.

3. **Claude CLI invocation**: The exact `claude` CLI flags for non-interactive subprocess invocation (analogous to `codex exec --skip-git-repo-check --sandbox workspace-write`) are not verified. Required for ClaudeCodeAdapter implementation.
