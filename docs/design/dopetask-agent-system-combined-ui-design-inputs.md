# Combined dopeTask + dope-agent-system Operator UI: Design Inputs

**Status:** Design inputs only. No implementation authorized by this document.
**Source:** Opus architecture design pass, 2026-05-06
**Authority:** dopeTask runtime authority governs all execution decisions shown in this UI.

---

## 1. Product Thesis

A combined operator UI gives a single human supervisor — or a supervised AI operator — a coherent view of:

1. **What is authorized to run** (dopeTask runtime: TP schema, availability, routing, series state)
2. **What templates and assets exist** (dope-agent-system: skills, prompt templates, adapter profiles)
3. **What has been executed and proven** (dopeTask: proof bundles, series ledger, EXEC.json records)
4. **What the repo health status is** (dopeTask: doctor checks, worktree state, branch audit)

The product does NOT conflate template ownership with runtime authority. dope-agent-system assets appear in a clearly labeled "Asset Library" or "Template Plane" region. dopeTask runtime decisions appear in a clearly labeled "Execution Authority" region. These regions cannot override each other in the UI.

---

## 2. Primary Users / Personas

### 2.1 Solo Operator / Supervisor
- Writes or imports JSON Task Packets
- Selects agent/runner for execution
- Monitors series execution state
- Reviews proof bundles post-run
- Makes authorization decisions (authorize next TP, authorize PR, authorize cleanup)

**Key needs:** fast state visibility, clear current-step indication, proof pass/fail at a glance, ability to pause/resume series without losing context, ADHD-friendly linear task flow with no ambiguity about what step is next

### 2.2 Implementer Agent Operator
- Receives Task Packet context injected into their session
- Executes bounded work within worktree
- Does not touch series state, ledger, or commit authority
- Sees only their assigned step context, not full series ledger

**Key needs:** exact step context, allowlist, validation commands, expected files, cwd clearly stated

### 2.3 Auditor / Red-Team Operator
- Reviews proof bundles for completeness, honesty, and compliance
- Compares `EXEC.json` claims against git log
- Verifies allowlist enforcement: did the committed files match the allowlist?
- Checks for mutation outside allowlist, unexpected API calls, `--bare` mode usage

**Key needs:** diff of claimed vs. actual, easy proof bundle traversal, refusal code explanation, ability to flag suspicious patterns

### 2.4 Project Bootstrapper
- Initializes a new consuming project's dopeTask configuration
- Installs dope-agent-system adapter templates (`.agent-project/` family)
- Configures availability.yaml with runner/model selections
- Does not execute TPs; only sets up the environment

**Key needs:** step-by-step wizard, clear confirmation of what was installed, diff of template vs. local adapter, doctor health check at end

### 2.5 Multi-Repo Maintainer
- Works with dopeTask and dope-agent-system as separate repos
- Needs to know which version of dope-agent-system is pinned in dopeTask
- Needs to see if dope-agent-system reference docs have drifted from dopeTask runtime
- Does not merge repos; manages boundary explicitly

**Key needs:** version pin status, diff of reference contracts vs. runtime enforcement, boundary health indicator

---

## 3. Core Workflows

### 3.1 Create / Import Task Packet
1. Paste JSON or load from file / clipboard
2. UI validates against `dopetask_schemas/task_packet.strict.schema.json`
3. UI shows: series metadata, steps, commit allowlist, depends_on, execution.agent
4. UI checks: is series state initialized? are dependencies satisfied?
5. Supervisor authorizes or rejects

### 3.2 Select / Route Implementer
1. UI shows `availability.yaml` runner/model matrix
2. Router scoring shown per runner (score, confidence, reasons)
3. User may override `--agent` flag
4. UI warns if selected agent is unavailable or stub (e.g., `RUNNER_NOT_IMPLEMENTED`)
5. UI warns if `--bare` mode would be used (billing risk)

### 3.3 Inspect Runner Availability
1. Shows current `availability.yaml` content
2. Shows which runners have working binaries (doctor-level check: `which claude`, `which codex`, etc.)
3. Shows last-verified status per runner
4. Shows routing policy (min_score, max_cost_tier, escalation_ladder)
5. Distinguishes "available in config" from "binary confirmed present"

### 3.4 Execute TP
1. Preflight: doctor check (main clean, correct identity, no stash)
2. Worktree creation (shown in UI: branch name, worktree path)
3. Context injection (SERIES_CONTEXT.json written to worktree)
4. Adapter execution (live log streaming if available)
5. Post-execution: validation commands run, results shown
6. Commit: changed files shown, allowlist check shown, commit SHA
7. Proof bundle: copied to series run_dir, shown in UI

### 3.5 Inspect Proof Bundle
1. Load `*_PROOF_BUNDLE.json` from `out/tp_series/<series_id>/packets/<tp_id>/`
2. Show: summary status (PASS / FAIL), step-by-step validation results
3. Show: `EXEC.json` claims (agent, model, committed_files, head_sha)
4. Show: raw artifacts (PROOF.json, TRACE.log if present)
5. Allow: flag for audit, mark as reviewed, generate audit report

### 3.6 Audit Result
1. Compare `EXEC.json` claimed committed_files against `git show --name-only <sha>`
2. Compare allowlist in TP against actual committed paths
3. Flag any out-of-allowlist writes
4. Flag any `--bare` mode evidence in proof metadata
5. Check `effective_model_source`: was model explicitly set or defaulted?
6. Export audit report as JSON or markdown

### 3.7 Manage Project Adapter / Profile
1. Show current `.dopetask/runtime/availability.yaml`
2. Show dope-agent-system adapter template source (if local path configured)
3. Show diff between consumed template and current project adapter
4. Allow: run dry-run install plan (`plan_project_adapter.py`)
5. Show: install readiness matrix
6. Do NOT allow: execute install without explicit release TP authorization

### 3.8 Inspect Templates / Skills (dope-agent-system Plane)
1. Show: `claude/skills/`, `claude/agents/`, `codex/`, `gemini/`, `copilot/` from dope-agent-system
2. Show: `.agent-project/` adapter profile for dope-agent-system itself
3. Clearly label: "Template Plane — dope-agent-system assets. These are NOT runtime authority."
4. Allow: preview skill file content
5. Do NOT allow: execute skills directly from this view; execution goes through dopeTask

### 3.9 Compare Runtime Truth vs. Reference Truth
1. Show: dopeTask runtime proof contract fields (from proof_aggregator.py)
2. Show: dope-agent-system PROOF_CONTRACT.md required fields
3. Highlight divergence (e.g., `proof_backfilled`, `commit_hash_semantics` present in reference, absent in runtime)
4. Allow: supervisor to flag divergence for remediation TP
5. Do NOT allow: UI to automatically update runtime behavior from reference

### 3.10 Resolve Dirty Worktree / Doctor Failures
1. Show: current git status of main branch
2. Show: stash list
3. Show: worktree list (`git worktree list`)
4. Show: which series have stale worktrees or branches
5. Allow: run `dopetask tp series cleanup --series-id <id>`
6. Allow: force-cleanup with explicit confirmation
7. Show: what is gitignored (e.g., proof/*) vs. what is untracked/modified

### 3.11 Browse Ledger / History
1. Show: `out/tp_series/<series_id>/SERIES_STATE.json` per series
2. Show: packet status (running / completed / failed) with timestamps
3. Show: head_sha and branch per completed packet
4. Show: PR status if series is finalized
5. Allow: drill into individual run dirs, proof bundles, EXEC.json

### 3.12 Prepare Source Bundle / Upload Bundle
1. Show: dope-agent-system `build_source_bundle.py` dry-run output
2. Show: what would be included in bundle
3. Allow: approve and run bundle export
4. Do NOT allow: merge bundle content into dopeTask runtime without release TP

---

## 4. Information Architecture

| Surface | Content | Authority Source |
|---------|---------|-----------------|
| **Dashboard** | Active series count, next runnable TP, repo health, runner availability | dopeTask runtime |
| **Task Packets** | List of imported/discovered packets, schema validation status, dependency graph | dopeTask schema |
| **Execution Runs** | Per-TP run history, EXEC.json, status, model used, timing | dopeTask out/tp_series |
| **Proof Bundles** | Per-TP proof bundle viewer, PASS/FAIL, artifact list | dopeTask proof/ |
| **Ledger** | SERIES_STATE.json viewer, packet timeline, PR linkage | dopeTask out/tp_series |
| **Runners / Models** | availability.yaml, runner binary health, routing decisions, scoring | dopeTask router |
| **Project Adapters** | .dopetask/runtime/availability.yaml, doctor check output | dopeTask doctor |
| **Skills / Templates** | dope-agent-system claude/codex/gemini/copilot assets | dope-agent-system |
| **PAL Planning** | PAL session context, planning output, clink injection (read-only view) | PAL MCP |
| **Repo Health** | git status, worktree list, stash list, identity check, gitignore analysis | dopeTask git ops |
| **Settings / Authority** | Version pins, authority order, runner flags, billing mode warning | dopeTask config |

---

## 5. UI Surfaces to Consider

### 5.1 CLI Commands (Tier 0 — Already Exists)
The existing `dopetask` CLI is the primary surface. All other UI surfaces build on top of it, not instead of it.

Commands already working:
- `dopetask tp series exec`
- `dopetask tp series import`
- `dopetask tp series status`
- `dopetask tp series cleanup`
- `dopetask tp series finalize`
- `dopetask route plan`
- `dopetask doctor`

Current state: `--agent claude_code` is implemented for the TP series/low-level executor path through `dopetask_adapters/claude_code`. The remaining Claude Code gap is the separate route/orchestrate runner plane, not the TP series MVP0 path.

### 5.2 TUI / Cockpit (Tier 1 — First Viable Slice)
A `dopetask cockpit` or `dopetask tui` command that renders:
- Current series state as a live table
- Proof bundle status for last completed TP
- Doctor health indicators
- Runner availability matrix
- Next runnable TP suggestion

Candidate library: `textual` (Python, rich TUI). No web server required.

### 5.3 Local Web UI (Tier 2 — Later)
A `dopetask serve` command spawning a local-only FastAPI + HTMX or SvelteKit server.
- Richer proof bundle visualization
- Diff views for allowlist enforcement
- Template/runtime comparison views
- Audit export

### 5.4 Generated Markdown Reports (Tier 1 — Already Possible)
The existing proof bundle system already generates JSON. A `dopetask report <series_id>` command could render markdown summaries from SERIES_STATE.json + PROOF_BUNDLE files. Low engineering cost, high value.

### 5.5 Command Palette (Tier 2)
For TUI and web: a fuzzy-search command palette that surfaces `dopetask` subcommands with contextual help.

---

## 6. Required UI States

| State | Trigger | UI Response |
|-------|---------|------------|
| **ready** | Doctor passes, no running series | Show next runnable TP, enable exec |
| **blocked** | Series dependency not satisfied | Show which dep is missing, show dep status |
| **dirty_worktree** | git status non-empty on main | Show dirty files, offer cleanup, block exec |
| **runner_unavailable** | Binary not found or RUNNER_NOT_IMPLEMENTED | Show which runner failed, suggest alternatives |
| **proof_failed** | Any step validation_passed=False | Show failed step, show errors, block series progression |
| **proof_passed_with_risks** | Proof pass but unexpected model / out-of-allowlist near-miss | Show warning, require acknowledgment |
| **adapter_mismatch** | execution.agent in TP != --agent flag | Show mismatch, require explicit override |
| **repo_version_drift** | dopeTask version newer than dope-agent-system pin | Show version delta, recommend pin refresh |
| **uncommitted_proof** | Proof artifacts untracked (gitignored) | Show gitignore status, explain force-add path |
| **stale_worktree** | Worktree from previous run still exists | Show stale worktrees, offer cleanup |
| **branch_collision** | TP branch name already exists | Show collision, offer force-cleanup |
| **bare_mode_risk** | --bare flag or ANTHROPIC_API_KEY-only mode detected | Show billing warning, require explicit opt-in |

---

## 7. Safety and Authority UX

**Principle 1: Runtime authority is always clearly labeled.**
Every UI surface that shows dopeTask state uses the label "Runtime" or "Execution Authority". Every surface that shows dope-agent-system state uses "Template Library" or "Asset Plane".

**Principle 2: Templates are never executable from the template view.**
The Skills/Templates surface has no "Run" button. Execution always flows through a Task Packet via `tp series exec`.

**Principle 3: --bare mode requires explicit supervisor opt-in.**
The UI shows a warning whenever `--bare` would be used: "Bare mode uses ANTHROPIC_API_KEY, not your subscription. API credits will be billed." The flag must be explicitly set in `availability.yaml` or via CLI flag, never automatically defaulted.

**Principle 4: PAL planning is read-only in the UI.**
The PAL Planning surface shows PAL session context and planning output. It has no "Execute" button. PAL output feeds into Task Packet authoring; execution always goes through dopeTask.

**Principle 5: Non-delegable responsibilities are non-interactive.**
The UI does not allow human override of: DAG dependency ordering, allowlist enforcement, proof validation, repo identity check. These are shown as read-only status indicators, not editable fields.

**Principle 6: dope-agent-system reference docs cannot override runtime behavior.**
The "Compare Runtime vs. Reference" view shows divergence but has no "Apply Reference" action. Applying reference requires authoring a remediation TP.

---

## 8. Data Model Inputs

### From dopeTask
- `TaskPacket` fields: id, title, steps, commit.allowlist, commit.message, commit.verify, series metadata, execution.agent, depends_on, repo_binding
- `SERIES_STATE.json`: series_id, base_branch, packets[*].{status, branch, head_sha, worktree_path, proof_bundle, error, timing}
- `EXEC.json`: agent, model, effective_model, effective_model_source, committed_files, verify results, head_sha
- `*_PROOF_BUNDLE.json`: aggregated proof with step results, validation_passed, files_created, changed_files
- `availability.yaml`: runners, models, policy
- `RoutePlan`: status, steps[*].{runner, model, confidence, scores, reasons}
- Doctor check output: branch, head, git status, stash, worktree list
- Git status: modified paths, untracked paths, staged paths

### From dope-agent-system
- `.agent-project/PROJECT_PROFILE.json`: project metadata, tool_families, threading.mode
- `.agent-project/PROOF_CONTRACT.md`: extended proof field requirements
- `DOPETASK_VERSION_PIN.lock`: pinned version, reference status
- `claude/skills/` file listing: skill name, description, path
- `claude/agents/` file listing: agent name, description, path
- `docs/DOPETASK_INTEGRATION_CONTRACT.md`: contract summary

### Derived / Computed
- Runner binary presence: `shutil.which("claude")`, `shutil.which("codex")`
- Version comparison: current dopeTask version vs. dope-agent-system pin
- Template vs. runtime diff: dope-agent-system proof fields vs. dopeTask proof fields
- Allowlist enforcement audit: `EXEC.json` claimed_files vs. `git show --name-only <sha>`

---

## 9. First Viable UI Slice

**Recommendation: Markdown Dashboard + CLI Report Command**

Start with `dopetask report <series_id>` that renders a markdown summary from existing artifacts. This:
- Requires no new dependencies
- Works immediately once proof bundles exist
- Is readable in any terminal, editor, or GitHub PR description
- Sets up data extraction patterns for TUI and web later

**What it outputs:**

```markdown
# Series Report: <series_id>
Generated: <timestamp>

## Status Summary
Completed: 3/4 | Failed: 0 | Running: 1

## Packets
| TP ID | Status | Agent | Model | Branch | SHA | Proof |
|-------|--------|-------|-------|--------|-----|-------|
| TP-001 | completed | codex | gpt-5.3-codex | tp/001-impl | abc123 | PASS |
| TP-002 | running | claude_code | sonnet-4.6 | tp/002-tests | — | — |

## Repo Health
Branch: main | Clean: yes | Worktrees: 1 active

## Runner Availability
claude_code: binary=yes | status=implemented
codex: binary=yes | status=implemented
```

**Second slice: `dopetask cockpit` TUI** using `textual` or `rich`. Renders the above in a live-updating terminal view with keyboard navigation to drill into proof bundles.

---

## 10. Open Questions and Red-Team Risks

1. **Auth mode visibility**: The UI currently has no way to tell whether Claude ran in subscription mode vs. bare/API-key mode from the proof bundle alone. `effective_model_source` is recorded but billing mode is not. Consider adding `auth_mode: "subscription" | "api_key" | "bare"` to proof metadata.

2. **Template drift detection**: dope-agent-system skills can change without dopeTask knowing. The UI should show "last verified against dope-agent-system commit <sha>" so the supervisor knows when template inputs are stale.

3. **PAL planning surface**: If PAL session context is surfaced in the UI, it must be clearly marked "planning artifact — not execution authority" to prevent it from being mistaken for a proof bundle.

4. **Gitignored proof artifacts**: `proof/*` is in `.gitignore`. The UI should show whether proof artifacts are gitignored, tracked, or force-added, to prevent confusion about proof durability.

5. **Multi-series collision**: If two series are running simultaneously (different worktrees), the dashboard must show isolation clearly. Series-level locking via `_locked_state()` is already in place; the UI should reflect this.

6. **dope-agent-system version drift warning**: The pin in `DOPETASK_VERSION_PIN.lock` is `0.5.7`. If dopeTask has moved past this, the UI should flag it. The current dopeTask version should be read from `pyproject.toml` and compared.

7. **Bare mode accident surface**: The `--bare` flag description says "Anthropic auth is strictly ANTHROPIC_API_KEY". If a user's keychain has a valid subscription token but `ANTHROPIC_API_KEY` env is also set, the ordering matters. The UI must make the effective auth mode observable, not just the flag state.
