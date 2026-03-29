# dopeTask Higher-Level Recovery and Delivery Plan

## Purpose

This plan resets the project around three realities:

1. The PAL research and usage guidance work is valuable and should be preserved.
2. The architecture/spec work is partially valid but currently under-specified in important areas.
3. There is active repair and implementation work happening in a second terminal, which must be brought back under disciplined control.

This plan is meant to keep the project on track and prevent further drift.

---

## Current situation summary

### Confirmed assets
- A PAL research playbook exists and is grounded in actual PAL tool usage patterns.
- Three architecture/spec docs were generated:
  - `docs/architecture/dopetask-supervisor-executor-adapter-spec.md`
  - `docs/specs/dopetask-clipboard-import-execute-spec.md`
  - `docs/plans/dopetask-multi-mode-execution-plan.md`
- Execution-related code changes survived on the salvage branch:
  - `src/dopetask/pipeline/task_runner/types.py`
  - `src/dopetask/pipeline/task_runner/executor.py`
  - `src/dopetask_adapters/gemini/executor.py`

### Confirmed problems
- The three docs are still too compressed and under-specify key contracts.
- The architecture doc still incorrectly implies trust in adapters.
- The ExecutionResult contract is referenced but not concretely defined in the docs.
- Worktree lifecycle, overwrite semantics, and deterministic next-runnable logic are incomplete.
- There is parallel work happening in another terminal that risks further divergence unless coordinated.

---

## Project priorities

### Priority 1: Restore and harden the docs
Before more implementation work happens, the project needs trustworthy architecture and command contracts.

### Priority 2: Preserve and review surviving code
The salvage branch contains real implementation progress and must not be lost or casually overwritten.

### Priority 3: Finish the PAL usage guide
The PAL guide was the original validation thread and remains important. It should become a real project document, not just an ad hoc artifact.

### Priority 4: Re-scope active repair work
The work happening in the other terminal must be pulled back into a reviewed, phase-based plan.

### Priority 5: Resume implementation in narrow slices
Only after docs and contracts are restored should Phase 1 implementation continue.

---

## Workstreams

## Workstream A — Documentation Recovery

### Goal
Turn the three short docs into implementation-grade project references.

### Required outputs
1. `docs/architecture/dopetask-supervisor-executor-adapter-spec.md`
2. `docs/specs/dopetask-clipboard-import-execute-spec.md`
3. `docs/plans/dopetask-multi-mode-execution-plan.md`

### Mandatory corrections
- Explicitly state that the kernel is deterministic.
- Explicitly state that adapters are untrusted and must be normalized/validated.
- Define the ExecutionResult schema in the architecture doc.
- Clarify worktree lifecycle rules.
- Clarify degraded-mode transition rules.
- Clarify overwrite behavior for failed, running, and completed packets.
- Clarify deterministic next-runnable selection rules.
- Clarify cycle and starvation behavior.
- Preserve current decisions; expand and tighten them rather than inventing new architecture.

### Exit criteria
- Docs are long enough to be implementation-grade.
- Docs contain explicit contracts, not just summary prose.
- Docs are reviewed before more code is written.

---

## Workstream B — PAL Playbook Productization

### Goal
Promote the PAL research into a durable project doc.

### Required output
- `docs/guides/dopetask-pal-integration-playbook.md`

### Scope
This guide should cover:
- PAL tool inventory
- when to use `analyze`, `planner`, `challenge`, `thinkdeep`, `consensus`, `clink`
- safe chaining patterns
- anti-patterns
- timeout-safe request sizing
- the PAL role in supervisor-mode dopeTask workflows
- the line between PAL thinking and dopeTask execution

### Exit criteria
- The guide is stored in-repo.
- It is written as operator guidance, not marketing fluff.
- It is referenced by future architecture/spec work.

---

## Workstream C — Salvage Branch Review

### Goal
Preserve and assess the surviving implementation changes before continuing.

### Files to review
- `src/dopetask/pipeline/task_runner/types.py`
- `src/dopetask/pipeline/task_runner/executor.py`
- `src/dopetask_adapters/gemini/executor.py`

### Questions to answer
- Is ExecutionResult actually defined and enforced?
- Does the kernel validate adapter output fail-fast?
- Is Gemini being normalized into kernel-safe output, or is provider logic still leaking through?
- Did the implementation accidentally entangle series logic or CLI behavior too early?

### Exit criteria
- Code review summary exists.
- Good changes are kept.
- Any unsafe or premature changes are reverted or deferred.

---

## Workstream D — Other Terminal Repair Stream

### Goal
Bring the parallel Gemini work back under disciplined control.

### Rules
- No uncontrolled code edits while architecture/spec docs are still being repaired.
- No additional TP execution for doc writing.
- No more broad “continue implementation” prompts.
- The other terminal must operate in one of only two modes:
  - review mode
  - tightly scoped implementation mode

### Immediate action
Create a short checkpoint from the second terminal:
- files changed
- current objective
- assumptions driving the edits
- whether those assumptions are fully backed by the repaired docs

### Exit criteria
- The second terminal is no longer drifting independently.
- Work is synchronized back to the agreed phase plan.

---

## Workstream E — Phase 1 Implementation Restart

### Goal
Resume implementation only after documentation and review gates pass.

### Phase 1 scope
- Lock ExecutionResult contract
- Validate adapter output in the kernel
- Refactor Gemini path only
- Do not touch broader TP series logic yet
- Do not attempt multi-provider support yet

### Non-goals
- No broad CLI redesign
- No cross-series execution work
- No full streaming refactor
- No all-provider rollout

### Exit criteria
- Phase 1 contract is coded and tested
- No hidden provider trust remains
- No drift into later phases

---

## Recommended sequence

### Step 1
Freeze the second terminal in review-only mode.

### Step 2
Restore and expand the three docs.

### Step 3
Promote the PAL guide into the repo.

### Step 4
Review surviving code on the salvage branch.

### Step 5
Reconcile the other terminal's repair work with the updated docs.

### Step 6
Resume Phase 1 implementation in one narrow slice only.

---

## Review checkpoints

At the end of each workstream, require a checkpoint containing:
- files changed
- what was decided
- what remains uncertain
- whether the next workstream may begin

This is mandatory. The current project problems are not just implementation bugs. They are control-flow and scope-discipline failures.

---

## Rules for the next 24 hours of work

- One active implementation objective at a time.
- One Gemini terminal should be considered authoritative.
- No new architecture changes without document updates first.
- No TP execution for writing or repairing docs.
- No code expansion beyond Phase 1 until the docs and PAL guide are stable.
- Preserve branch state before risky edits.
- Prefer reversible, narrow edits over sweeping cleanup.

---

## Success condition

The project is back on track when all of the following are true:

- Architecture doc is explicit and trustworthy.
- Command UX spec is deterministic and operationally clear.
- Implementation plan is phased and actionable.
- PAL guide is in the repo and usable.
- Salvage code is reviewed and preserved.
- Parallel repair work is synchronized.
- Phase 1 implementation can resume without relying on guesswork.
