# Design Inputs: dope-agent-system ↔ dopeTask Interactive Executor and PAL Link Integration

**TP:** TP-DT-DAS-INVESTIGATE-0001  
**Status:** Evidence-backed design inputs. These are requirements for the next implementation TP, not decisions.

---

## Inputs Needed for Interactive Executor Transport

The remaining interactive executor gap is `ClaudeCodeAdapter` in `src/dopetask/runners/claude_code.py`, the separate route/orchestrate runner plane. TP series Claude Code execution is already implemented through `dopetask_adapters/claude_code`; before implementing the route/orchestrate runner, the following must be known:

| Input | Question | Source |
|-------|----------|--------|
| **Claude CLI invocation pattern** | What is the subprocess command for `claude` in non-interactive mode? Does it support `--skip-git-repo-check`, `--sandbox workspace-write`, `-C <dir>`, `-o <output_file>`, stdin prompt? | Empirical verification against `claude --help` |
| **Output capture** | How does `claude` write its output? Same `-o` flag as Codex? Or stdout? | Empirical verification |
| **Model selection** | Does `claude` support `--model` flag analogous to `codex --model`? | Empirical verification |
| **Prompt construction** | Should the adapter prompt include: packet path, step description, model, allowlist, validation commands? What format does Claude Code expect for task-level instructions? | Test run in worktree |
| **Execution result shape** | Does the ClaudeCode run produce a `last_message` file analogous to `CODEX_LAST_MESSAGE.txt`? | Depends on CLI output capture |
| **Mutation detection** | Should `ClaudeCodeAdapter` use the same `_git_status_paths()` mutation detection as `CodexCliAdapter`? | Yes — follow existing Codex pattern unless Claude CLI differs |
| **Worktree entry point** | Should `claude` be invoked at the worktree root (like Codex `-C repo_root`)? Or at repo root with worktree passed? | Align with Codex `-C` pattern |

**Blocking question**: What are the verified `claude` CLI flags for non-interactive subprocess invocation?

---

## Inputs Needed for PAL Link / clink Transport

**Finding**: PAL `clink` is not a delegation transport for dopeTask TPs. It is a PAL tool for injecting CLI context into PAL sessions (see `docs/guides/dopetask-pal-integration-playbook.md`). The PAL integration is already defined:
- PAL = thinking layer (analyze, planner, challenge)
- dopeTask = execution layer (tp series exec)
- `clink` = CLI context injection for PAL sessions

If "PAL Link" means something beyond this (e.g., a new transport where PAL orchestrates dopeTask step execution directly), the following inputs are needed:

| Input | Question | Current Status |
|-------|----------|----------------|
| **PAL as executor** | Is PAL intended to directly invoke `dopetask tp series exec` as part of its chain? | Not in current doctrine. Would require a new PAL tool (not `clink`). |
| **clink semantics** | Is `clink` the CLI context injection tool in PAL, or is there a "clink" tool separate from PAL for subprocess delegation? | `clink` is a PAL MCP tool per playbook. No separate "clink" tool found in dopeTask. |
| **Bounded prompt handoff** | If PAL Link means: PAL generates a bounded prompt → delegates to Claude Code CLI → Claude Code acts as implementer → returns proof, this would be an extension of the ClaudeCode runner design. | Need to decide if this is Model A, B, or C from the investigation. |
| **Session boundary** | Does PAL Link mean within-session tool chaining, or cross-session handoff via subprocess? | Needs decision before designing transport. |

**Recommendation**: Clarify "PAL Link / clink" semantics before designing. Current evidence suggests this is the existing PAL→dopeTask workflow, not a new transport.

---

## Inputs Needed for Project Adapter Consumption

dope-agent-system ships adapter templates (`.agent-project/` family). dopeTask currently does not read these. If dopeTask is to consume adapter profiles:

| Input | Question | Evidence |
|-------|----------|----------|
| **Adapter profile loader** | Where in dopeTask's execution path would PROJECT_PROFILE.json be loaded? Before Doctor check? Before routing? | Currently: nowhere. Needs new code. |
| **Authority reconciliation** | dopeTask has `.dopetask/project.json`. dope-agent-system has `.agent-project/PROJECT_PROFILE.json`. Which wins on conflict? | dopeTask wins (per DOPETASK_INTEGRATION_CONTRACT.md). Must be explicit in loader. |
| **Consuming repo bootstrap** | Must every consuming project run `plan_project_adapter.py` before `tp series exec`? | Currently: no. Would require documentation update in `docs/01_SETUP.md`. |
| **Thread protocol integration** | Does `threading.mode` (single_thread_role_blocks vs multi_thread_role_channels) affect dopeTask's execution? | Currently: no. Would be new behavior. |
| **Tool family enablement** | Does `tool_families.claude_code.enabled` influence which runner dopeTask picks? | Currently: routing is via `--agent` flag and router scoring. Integration point unclear. |

**Minimum viable input**: Decide whether Model C (Adapter-Profile Consumption) is in scope for the next TP or deferred.

---

## Inputs Needed for Proof Contract Normalization

dope-agent-system's `PROOF_CONTRACT.md` requires fields not currently enforced by dopeTask's runtime proof:

| Field | dope-agent-system requires | dopeTask runtime status | Risk |
|-------|---------------------------|------------------------|------|
| `proof_backfilled` | true when proof is updated post-commit | Not required | If dopeTask adopts auditing for these fields, must be added |
| `commit_hash_semantics` | Explicit statement of commit field semantics | Not required | Self-referential git hash limitation must be documented |
| `audit_submission_head` | Marker requiring Audit to verify HEAD with `git rev-parse HEAD` | Not required | Audit boundary blurry without this |
| `implementation_commit` | SHA of primary implementation commit | Not in current proof_aggregator | Required for post-commit proof backfill |
| `git_status_final` | "clean" after all commits | Not required | Proof may be incomplete if captured before cleanup |

**Inputs needed**:
1. Does dopeTask's `proof_aggregator.py` need to adopt these fields?
2. If yes, which fields are mandatory vs. optional extensions?
3. Is there a migration path for existing proof bundles?

---

## Inputs Needed for Model / Tool Routing

dopeTask's router (`router/planner.py`, `router/scoring.py`, `router/availability.py`) decides which runner to use. Current state:

| Input | Question | Current State |
|-------|----------|---------------|
| **Claude model selection** | Which models does `--agent claude_code` route to? | The TP series/low-level executor resolves a route-derived model when available; TP-DT-CLAUDE-ROUTING-READINESS-0001 selected `sonnet-4.6` for `run-task`. Route/orchestrate runner execution remains separate. |
| **Availability check** | Is there an `availability_path_for_repo` for claude_code? | Yes. The router uses `.dopetask/runtime/availability.yaml`; readiness verified `claude_code` in the availability template and generated availability file. |
| **Route scoring** | What score does claude_code get vs codex_desktop? | Readiness route planning selected `claude_code` for `run-task` with `sonnet-4.6`; exact scores remain route-plan artifact data, not dope-agent-system authority. |
| **dope-agent-system tool_families** | Do `tool_families.claude_code.enabled` flags in PROJECT_PROFILE.json affect routing? | No integration exists today |

**Minimum viable input**: Verify whether `docs/12_ROUTER.md` describes how to add a new runner to the routing table.

---

## Inputs Needed for Ledger / Supervisor Compatibility

The TP series Claude Code MVP0 entrypoint is `dopetask tp series exec --agent claude_code <packet.json>`. For Claude:

| Input | Question | Current State |
|-------|----------|---------------|
| **`--agent` flag value** | Is it `--agent claude_code` or `--agent claude`? | The TP exec/series agent slug is `claude_code`; the route/orchestrate runner registry uses the same slug for its separate deferred plane. |
| **Ledger update** | Does `tp series exec --agent claude_code` currently write to SERIES_STATE.json? | Valid TP series entrypoint; this design note does not re-exercise Claude execution. |
| **Series integration** | Is `claude_code` a valid selected agent for TP series execution? | Yes for MVP0 through `dopetask_adapters/claude_code`. |
| **Supervisor prompts** | Does `docs/26_SUPERVISOR_PROMPTS.md` need updating to include claude_code as a valid agent? | Updated to include `claude_code` while preserving route/orchestrate as a separate plane. |

---

## Minimum Viable Integration Proposal

**Route/orchestrate follow-up**: Implement `ClaudeCodeAdapter.run()` following the Codex subprocess pattern. This is separate from the completed TP series Claude Code MVP0 path.

Steps:
1. Verify `claude` CLI flags (requires empirical test, out of scope for this investigation)
2. Implement `ClaudeCodeAdapter.run()`:
   - Construct prompt from packet_path + step + model
   - Invoke `claude` via subprocess with `-C <worktree_root>` and `-o <output_file>`
   - Capture stdout/stderr
   - Detect mutations via `_git_status_paths()`
   - Return normalized ExecutionResult
3. Add a unit test analogous to `CodexCliAdapter` tests
4. Update `docs/22_WORKFLOW_GUIDE.md` to include `--agent claude_code` examples

dope-agent-system integration at MVP level: **None required**. The TP series MVP0 path does not consume dope-agent-system adapter profiles or skill installation. Any future route/orchestrate runner integration can remain separate from dope-agent-system template assets unless a later TP explicitly changes that boundary.

---

## Questions for Supervisor Before Implementation

1. **What is "PAL Link / clink transport"?** Is this the existing PAL→dopeTask workflow (plan with PAL, execute with dopeTask), or is there a new transport layer being designed?

2. **What `claude` CLI flags exist for non-interactive subprocess invocation?** This is the hard blocker for ClaudeCodeAdapter.

3. **Is Model C (Adapter-Profile Consumption) in scope for the next TP?** If yes, dopeTask needs a PROJECT_PROFILE.json reader. If no, focus on Model B (prompt-template injection).

4. **Should dope-agent-system skills be injected into the runner before execution?** If yes, a release TP must be authored for dope-agent-system first (install targets are currently blocked).

5. **What proof contract fields should the ClaudeCode runner produce?** At minimum: `ExecutionResult` fields. Should it also produce `proof_backfilled`, `commit_hash_semantics`?

6. **Is the dopeTask version (0.5.7) still current?** The `DOPETASK_VERSION_PIN.lock` in dope-agent-system pins to 0.5.7. If dopeTask has moved beyond that, the pin must be refreshed.
