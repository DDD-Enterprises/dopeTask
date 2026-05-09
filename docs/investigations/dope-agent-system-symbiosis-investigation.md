# dope-agent-system Symbiosis Investigation

**TP:** TP-DT-DAS-INVESTIGATE-0001  
**Status:** PASS  
**Conducted:** 2026-05-06  
**Scope:** Evidence-only. No source code mutated.

---

## Executive Finding

The boundary between dopeTask and dope-agent-system is **already formally decided and implemented**. TP-AGENT-SYSTEM-0011 (boundary audit) and TP-AGENT-SYSTEM-0012 (supersession decision) formalized Option C: dopeTask owns all runtime authority; dope-agent-system owns templates, prompts, adapters, and reference contracts. TP-DA-0002a executed the supersession by removing the duplicate `src/dope_agent/` runtime.

The integration pressure point is **not** a boundary confusion problem — it is a **missing runner implementation**: `ClaudeCodeAdapter` in `src/dopetask/runners/claude_code.py` returns `RUNNER_NOT_IMPLEMENTED`. The symbiosis design question is: how do dope-agent-system's skill/prompt/adapter assets flow into dopeTask's ClaudeCode runner to make it operational?

---

## Repositories Inspected

| Repo | Path | Clean |
|------|------|-------|
| dopeTask (primary) | `/Users/hue/code/dopeTask` | ✅ |
| dope-agent-system (secondary) | `/Users/hue/code/dope-agent-system` | ✅ |

Secondary repo resolved via `/Users/hue/code/dope-agent-system` (resolution order item 3; `DOPE_AGENT_SYSTEM_REPO` env not set, `../dope-agent-system` resolved to same path).

---

## dope-agent-system Current Role (Q1)

Evidence from `README.md`, `CLAUDE.md`, `docs/AGENT_SYSTEM_OVERVIEW.md`, and `docs/DOPETASK_INTEGRATION_CONTRACT.md`:

**What it IS:**
- Canonical source for generic skill templates (Claude Code, Codex, Gemini CLI, GitHub Copilot CLI)
- Adapter templates for consuming projects (`.agent-project/` family: 8 files)
- Reference-only orchestrator contract documentation
- Dry-run install planners (`plan_install_release.py`, `plan_project_adapter.py`)
- Upload-safe source bundle export (`build_source_bundle.py`)
- Repository hygiene validation (`check_repo_hygiene.py`)
- Meta-validator (`validate_agent_system.py`) enforcing asset-author boundary
- Proof bundles for its own accepted task packets

**What it is NOT:**
- A runtime executor for task packets
- A thin client around dopeTask
- A schema authority (schemas were removed by TP-DA-0002a; `schemas/dopeTask_schema_references.json` is a pointer only)
- An installer (all install targets blocked until explicit release TP)
- A network, browser, MCP, or hook surface

**Authoritative quote** (from `DOPETASK_INTEGRATION_CONTRACT.md`):
> dopeTask is the runtime authority. dope-agent-system is the asset/template/reference owner… If dope-agent-system reference text, generated proof plans, task packets, or local adapter policy conflict with dopeTask runtime behavior, dopeTask wins.

---

## dopeTask Current Integration Pressure

Evidence from `src/dopetask/runners/claude_code.py`, `runners/__init__.py`, and `docs/plans/dopetask-multi-mode-execution-plan.md`:

1. **`ClaudeCodeAdapter` is a stub.** `run()` returns `{"status": "refused", "reason_code": "RUNNER_NOT_IMPLEMENTED"}`. It is registered in `RUNNER_ADAPTERS["claude_code"]` but not implemented.

2. **Multi-mode execution plan is in Phase 1.** Phase 1 establishes the `ExecutionResult` contract and `TaskExecutor`. Phase 3 adds multi-mode support (shell + agent steps). The claude_code runner would be implemented in Phase 2–3.

3. **Codex runner IS implemented** (`subprocess codex exec --skip-git-repo-check`). This is the pattern to follow for Claude Code.

4. **PAL is the thinking layer, not an execution transport.** `docs/guides/dopetask-pal-integration-playbook.md` defines PAL as the Research/Plan/Verify layer and dopeTask as the Execute layer. `clink` is a PAL tool for injecting CLI context into PAL sessions, not a transport for delegating bounded prompts to dopeTask.

---

## Evidence Inventory

29 files inspected. Full index: `proof/tp-dt-das-investigate-0001/evidence_index.json`.

Key evidence clusters:

| Cluster | Files | Confidence |
|---------|-------|------------|
| Boundary formally decided | OWNERSHIP_MATRIX.json, RECOMMENDATION.md, DOPETASK_INTEGRATION_CONTRACT.md | HIGH |
| dope-agent-system role | README.md, CLAUDE.md, AGENT_SYSTEM_OVERVIEW.md | HIGH |
| ClaudeCode runner is a stub | runners/claude_code.py, runners/__init__.py | HIGH (direct code read) |
| Codex runner is implemented | runners/codex_cli.py | HIGH (direct code read) |
| PAL is think-layer not transport | dopetask-pal-integration-playbook.md, PAL_CHAINING_DOCTRINE.md | HIGH |
| RunnerAdapter protocol | runners/base.py, executor.py, supervisor-executor-adapter-spec.md | HIGH |
| Adapter templates available | .agent-project/, templates/agent-project/, PROJECT_ADAPTER_CONTRACT.md | HIGH |

---

## Overlap and Collision Map (Q2)

| Concept | dopeTask | dope-agent-system | Status |
|---------|----------|-------------------|--------|
| Task Packet schema | AUTHORITATIVE (`dopetask_schemas/`) | REFERENCE pointer only | ✅ Resolved |
| Proof bundle schema | AUTHORITATIVE (`proof/standards/`) | REFERENCE pointer only | ✅ Resolved |
| Ledger record | AUTHORITATIVE (`out/tp_series/`) | REFERENCE doc only | ✅ Resolved |
| State machine | AUTHORITATIVE (`orchestrator/kernel.py`) | REFERENCE doc only | ✅ Resolved |
| Policy engine | AUTHORITATIVE (`pipeline/compliance/gate.py`) | REFERENCE doc only | ✅ Resolved |
| Routing engine | AUTHORITATIVE (`router/`) | REFERENCE doc only | ✅ Resolved |
| Proof contract fields | Live enforcement | Extended fields (backfill, commit hash semantics) | ⚠️ Gap: dope-agent-system has richer field requirements |
| Skill/command templates | Not present | AUTHORITATIVE (`claude/`, `codex/`, etc.) | ✅ No collision |
| Adapter templates | Entry-point group only | AUTHORITATIVE (`.agent-project/` family) | ✅ No collision |
| ClaudeCode runner | STUB (RUNNER_NOT_IMPLEMENTED) | Has skill source, prompt patterns | 🔴 Active gap |
| Install dry-run planning | Actual installers (`scripts/install.sh`) | Dry-run planners only | ✅ Complementary |
| Source bundle export | Log/run artifacts | Template source artifacts | ✅ Different content |
| Audit prompting | Runner integration surface | Long-form prompt corpus | ✅ Complementary |

---

## Authority Boundary Findings (Q3)

Formally decided per TP-AGENT-SYSTEM-0011 OWNERSHIP_MATRIX.json (all HIGH confidence):

**dopeTask owns:**
- Task-packet schema, strict schema, validation
- Proof-bundle schema, aggregator, writer
- Series ledger (`SERIES_STATE.json`), finalize semantics, promotion-token gating
- Allowlist gate, repo-identity guard, branch guard
- Routing engine (planner, scoring, availability, handoff, reporting)
- Refusal protocol and refusal codes
- Worktree isolation and bounded commit/PR flow
- Concrete runner adapters (ClaudeCode stub, Codex ✅, Copilot, GoogleJules)
- TP series exec (`tp series exec`, `tp series status`, `tp series finalize`)
- Runtime authorization (what is authorized vs what is accepted)

**dope-agent-system owns:**
- Source bundles (template-content focused)
- Adapter templates (PROJECT_PROFILE.json, AUTHORITY_ORDER.md, etc.)
- Skill/command templates (claude/, codex/, gemini/, copilot/)
- Install manifests (dry-run only; actual install blocked)
- Self-adapter `.agent-project/` (for dope-agent-system only)
- Audit prompting and supervisor prompt corpus

---

## Candidate Integration Surfaces (Q4)

Files in dope-agent-system that could become input to dopeTask execution:

| File | Type | Integration Role |
|------|------|-----------------|
| `.agent-project/PROJECT_PROFILE.json` | Live adapter profile | Could be consumed by dopeTask's project adapter loader |
| `.agent-project/AUTHORITY_ORDER.md` | Authority decision hierarchy | Reference for supervisor boundary enforcement |
| `.agent-project/SAFETY_BOUNDARIES.md` | Default-deny list | Reference for what the ClaudeCode runner must refuse |
| `.agent-project/PROOF_CONTRACT.md` | Proof required fields | Extended fields (backfill, commit semantics) could inform dopeTask's proof aggregator |
| `.agent-project/HANDOFF_FORMATS.md` | Handoff shapes | Protocol for handing off to external tool destinations |
| `templates/agent-project/` | Adapter templates (8 files) | Bootstrap template for dopeTask consuming-project adapters |
| `claude/skills/` | Claude Code skill source | Skills to install before running ClaudeCode runner |
| `claude/agents/` | Claude Code subagents | Subagents available to Claude Code when acting as implementer |
| `schemas/dopeTask_schema_references.json` | Schema pointer | Tells dope-agent-system where authoritative schemas live |
| `docs/TOOL_ROUTING_MATRIX.md` | Routing reference | Role-to-tool routing patterns |
| `docs/HANDOFF_PROTOCOL.md` | Handoff protocol | Handoff shapes for multi-tool workflows |

**Not candidate inputs** (pure reference docs, not executable):
- `schemas/REFERENCE.md`, `orchestrator/REFERENCE.md` (REFERENCE-only markers)
- `examples/*/README_NOT_AUTHORITATIVE.md` (explicitly not live policy)

---

## Non-Delegable dopeTask Responsibilities (Q5)

From `docs/architecture/dopetask-supervisor-executor-adapter-spec.md`, `docs/22_WORKFLOW_GUIDE.md`, and OWNERSHIP_MATRIX.json:

dopeTask must NEVER delegate to dope-agent-system:

1. **Next-runnable TP selection** (`tp series exec --next` DAG eligibility rules)
2. **Dependency resolution** (DAG cycle detection, starvation detection)
3. **Execution validity** (Doctor check: main must be clean, correct identity)
4. **Proof validation** (TaskExecutor validates adapter output; proof_aggregator.py is authoritative)
5. **Allowlist enforcement** (compliance/gate.py allowlist gate)
6. **Commit plan validation** (bounded commit per packet, only allowlisted paths)
7. **Final acceptance** (promotion-token gate, ledger acceptance)
8. **Worktree lifecycle** (creation, isolation, cleanup — kernel responsibility)
9. **Refusal protocol** (RUNNER_NOT_IMPLEMENTED, PACKET_READ_ERROR, etc.)
10. **Series state machine** (`SERIES_STATE.json` transitions)

Any future integration design that causes dope-agent-system to make decisions about these items is a boundary violation.

---

## What dope-agent-system Already Assumes About dopeTask (Q6)

Direct quotes:

1. **`DOPETASK_VERSION_PIN.lock`**: `dopeTask_version = 0.5.7 | local_reference_status = REFERENCE_ONLY | conflict_rule = dopeTask wins`
2. **`schemas/dopeTask_schema_references.json`**: `"runtime_authority": "dopeTask" | "local_reference_status": "REFERENCE_ONLY" | "authoritative_schema_paths": ["/Users/hue/code/dopeTask/dopetask_schemas/..."]`
3. **`docs/AGENT_SYSTEM_OVERVIEW.md`**: "Live executable state machine lives in dopeTask (`src/dopetask/orchestrator/kernel.py`, `src/dopetask/pipeline/task_runner/runner.py`)."
4. **`AUTHORITY_ORDER.md`**: Authority order starts with "runtime repo state of `/Users/hue/code/dope-agent-system`" then "accepted TP proof" — never claims dopeTask-level authority.
5. **`DOPETASK_INTEGRATION_CONTRACT.md`**: "If dope-agent-system reference text… conflict with dopeTask runtime behavior, dopeTask wins."

dope-agent-system treats dopeTask as: **external runtime authority, pinned to a specific version, REFERENCE_ONLY relationship, conflict rule: dopeTask wins.**

---

## Candidate Integration Models (Q7)

### Model A: Skill-Install-Before-Run

**Shape**: Before dopeTask's `ClaudeCodeAdapter.run()` invokes `claude`, it installs the relevant dope-agent-system skills from `claude/skills/` into the worktree's `.claude/skills/` directory. Claude then picks them up automatically.

**Pros**: Simple handshake; dope-agent-system's skill assets are used as intended; no runtime coupling; respects install-blocks-until-release-TP posture once install TP exists.

**Cons**: Requires a dope-agent-system release TP before install is authorized. In the interim, skills must be manually installed or the runner must install from a local path (not from a release artifact). Skills mutate the worktree slightly before execution.

**Risk**: Install-blocking posture in dope-agent-system means this is currently unauthorized until a release TP is accepted.

**Required repo changes**: `ClaudeCodeAdapter.run()` gains a pre-run skill installer step. dopeTask gets a `skill_source_path` in its adapter config. dope-agent-system needs a release TP.

---

### Model B: Prompt-Template-Injection

**Shape**: `ClaudeCodeAdapter.prepare()` reads a prompt template from dope-agent-system's `claude/skills/` source tree and injects it as the `--system-prompt` when invoking `claude`. dopeTask reads the template from a local path (similar to how Codex reads from `packet_path`).

**Pros**: No install required; templates are source-controlled in dope-agent-system; clean separation; follows the existing Codex pattern (prompt constructed then passed via stdin); works within current install-blocking posture.

**Cons**: Path coupling — dopeTask's adapter must know where dope-agent-system lives (env var or config). Claude Code's `--system-prompt` flag and its interaction with project CLAUDE.md must be verified.

**Risk**: Path coupling is fragile if repos move. Claude Code CLI flags need empirical verification.

**Required repo changes**: `ClaudeCodeAdapter.run()` gains prompt construction from a configurable template path. A `claude` CLI invocation pattern (analogous to `codex exec`) must be verified.

---

### Model C: Adapter-Profile Consumption

**Shape**: dopeTask's project adapter loader reads a consuming project's `.agent-project/PROJECT_PROFILE.json` (bootstrapped from dope-agent-system's templates) before deciding how to invoke Claude Code. The profile's `default_implementer`, `threading.mode`, and `tool_families` fields influence routing.

**Pros**: Full adapter lifecycle as designed by dope-agent-system; rich governance (safety boundaries, handoff formats, proof contract, thread protocol); aligns with dope-agent-system's stated purpose.

**Cons**: Requires dopeTask to implement a profile reader and to know about dope-agent-system adapter conventions. Currently no dopeTask code reads `.agent-project/`. High implementation cost.

**Risk**: Two governance systems (dopeTask's `.dopetask/project.json` and dope-agent-system's `.agent-project/`) could collide. Requires explicit reconciliation of authority order.

**Required repo changes**: dopeTask gains an adapter-profile reader. Consuming projects must bootstrap their `.agent-project/` before running `tp series exec`. dopeTask CLAUDE.md must be updated to describe the adapter load order.

---

### Model D: PAL-Mediated Packet Handoff

**Shape**: PAL's `planner` tool drafts the Task Packet; PAL's `clink` injects CLI context into the session; dopeTask executes the packet via `tp series exec`. dope-agent-system contributes prompt templates that PAL uses during the planning phase.

**Pros**: Matches the existing PAL integration playbook exactly; no new runtime coupling; PAL stays in the thinking layer.

**Cons**: `clink` is a PAL tool for CLI context injection, not a delegation transport for dopeTask. This model does not implement the ClaudeCode runner — it just improves how packets are authored. Does not address `RUNNER_NOT_IMPLEMENTED`.

**Risk**: This model is already how dopeTask is used with PAL. Calling it an "integration model" may be misleading. It does not advance interactive executor design.

**Required repo changes**: None in either repo. At most, dope-agent-system prompt templates could be made available to PAL via source bundle upload.

---

## Recommended Next Design Packet

**TP-DT-CLAUDE-RUNNER-0001: Implement ClaudeCodeAdapter via `claude` CLI subprocess**

Scope:
- Implement `ClaudeCodeAdapter.run()` following the Codex pattern (`subprocess` invocation of `claude`)
- Verify `claude` CLI flags: `--system-prompt`, `--sandbox`, `-C` (working dir), `-o` (output path)
- Define prompt construction pattern: packet_path + step + model
- Decide whether to inject dope-agent-system skill templates via Model A or Model B
- Validate that `ExecutionResult` contract is satisfied

This is the minimum viable runner implementation. Model B (prompt-template injection) is the recommended starting shape because it works within current install-blocking posture.

---

## Risks and Unknowns

1. **`claude` CLI flags unverified**: The exact invocation pattern for `claude` (equivalent to `codex exec --skip-git-repo-check --sandbox workspace-write`) is not in scope for this investigation. Must be empirically verified in the next TP.

2. **dope-agent-system install blocking**: Model A (skill install) requires a release TP in dope-agent-system. That TP has not been authored.

3. **`.agent-project/` in dopeTask**: dopeTask has no mechanism to read `.agent-project/` adapter files. Model C requires new dopeTask code.

4. **PAL `clink` semantics**: `clink` injects CLI context into PAL sessions; it is not a transport for dopeTask TPs. Its role in any deeper integration is speculative.

5. **Proof contract field divergence**: dope-agent-system's `PROOF_CONTRACT.md` requires fields not currently in dopeTask's runtime proof (e.g., `proof_backfilled`, `commit_hash_semantics`, `audit_submission_head`). If dopeTask adopts these, alignment is needed.

---

## Blocked or Unverified Claims

- **Unverified**: `claude` CLI supports `--system-prompt` flag and a `--sandbox workspace-write` equivalent.
- **Unverified**: Whether dope-agent-system skills installed into a worktree's `.claude/skills/` are automatically picked up by `claude` when invoked non-interactively.
- **Unverified**: Current dopeTask version vs. pinned version (0.5.7) — whether it has changed since `DOPETASK_VERSION_PIN.lock` was written.
