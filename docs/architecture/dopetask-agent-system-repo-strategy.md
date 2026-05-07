# dopeTask + dope-agent-system: Repo Strategy Analysis

**Status:** Design-pass artifact. No consolidation authorized by this document.
**Source:** Opus architecture design pass, 2026-05-06
**Authority:** dopeTask runtime authority governs execution in all options.

---

## 1. Current State

| Repo | Role | Relationship |
|------|------|-------------|
| `/Users/hue/code/dopeTask` | Runtime authority: executor, state machine, proof, ledger | Primary |
| `/Users/hue/code/dope-agent-system` | Template / asset / reference authority: skills, adapters, reference contracts | Secondary |

The boundary is formally decided (TP-AGENT-SYSTEM-0011 OWNERSHIP_MATRIX.json, TP-AGENT-SYSTEM-0012 supersession). dopeTask wins on all conflicts. dope-agent-system explicitly pins dopeTask at version 0.5.7 as REFERENCE_ONLY.

---

## 2. Option Analysis

### Option A: Keep Separate Repos (Status Quo with Explicit Contracts)

**What it is:** Each repo stays independent. Integration is through explicit version pins, documented contracts (DOPETASK_INTEGRATION_CONTRACT.md), and optional release artifact consumption. No automatic coupling.

**Product UX benefits:**
- Clear mental model: "I'm working on the executor" (dopeTask) vs. "I'm working on templates" (dope-agent-system)
- No accidental cross-contamination of runtime vs. template changes
- Each repo can evolve at its own pace
- dope-agent-system can be archived or replaced without touching dopeTask core

**Implementation complexity:** Low for current state. Integration points (skill injection, template consumption) require explicit handshake protocols but no repo changes.

**Release/versioning model:** Independent semantic versioning. dope-agent-system pins dopeTask version explicitly. Consumers can use either repo independently.

**Authority-boundary risk:** Low. Clear file-system separation enforces boundary. The main risk is someone editing a "reference" doc and thinking it changed runtime behavior — mitigated by REFERENCE_ONLY markers.

**Testing strategy:** Each repo tests independently. Integration is tested via explicit boundary crossing (e.g., `plan_project_adapter.py` dry-run output is tested in dope-agent-system; runtime behavior is tested in dopeTask).

**Migration cost:** Zero. Current state.

**Packaging/install impact:** None. Each repo is independently installable.

**Contributor/operator mental model:** Simple. "dopeTask runs things. dope-agent-system has templates." No shared namespace confusion.

**Proof/audit implications:** Proof bundles live in dopeTask. dope-agent-system's PROOF_CONTRACT.md is reference-only. No audit confusion across repo boundaries.

**Combined UI impact:** UI must know about both repos. Data is pulled from both paths. This is manageable with a configured path for dope-agent-system (env var or `.dopetask/das_path`).

**Plan-backed session impact:** No impact. Both repos are used locally; billing is determined by how runners are invoked, not by repo structure.

**Score: Best for 0–30 days. Lowest risk.**

---

### Option B: Monorepo

**What it is:** Both repos merged into a single repository with a shared docs/, tests/, and versioning system. Likely structure:
```
dopeTask/
├── src/dopetask/          (runtime)
├── src/dopetask_adapters/ (adapters)
├── das/                   (former dope-agent-system)
│   ├── claude/skills/
│   ├── templates/
│   └── docs/
├── tests/
└── docs/
```

**Product UX benefits:**
- Single repo for contributors
- Unified PR workflow
- Easier to maintain shared docs (no version drift)
- Simpler combined UI: all data in one repo root

**Implementation complexity:** High. Requires:
- Migrating dope-agent-system files into dopeTask
- Updating all cross-repo references (DOPETASK_INTEGRATION_CONTRACT.md, version pins, absolute paths)
- Updating CI for both workflows
- Deciding how to handle existing proof bundles in dope-agent-system

**Release/versioning model:** Shared version. If a template changes, dopeTask version bumps even if runtime is unchanged. This is semantically wrong and creates noisy changelogs.

**Authority-boundary risk:** HIGH. The main risk: developers see `das/claude/skills/` and `src/dopetask/runners/claude_code.py` in the same IDE and assume they are architecturally equal. The asset/runtime boundary must be enforced via documentation and linting, not physical separation. Humans and LLMs routinely ignore this.

**Testing strategy:** All tests in one repo. Risk: runtime tests and template tests share a test runner, making it easier to accidentally test templates as if they were runtime.

**Migration cost:** High. 3–5 days of careful file migration, reference updating, CI work, and proof-bundle migration.

**Packaging/install impact:** If both ship as one package, consuming projects get both runtime and templates even if they only need runtime. Adds bloat and creates questions about whether templates are "installed" vs. "available".

**Contributor/operator mental model:** Confusing at first. Clear once you understand the directory convention, but requires documentation and tooling to enforce it.

**Proof/audit implications:** Proof bundles from dope-agent-system's own accepted TPs would be in the same repo as dopeTask runtime proofs. This creates audit confusion: which proof bundle governs what?

**Combined UI impact:** Easiest: one repo root, all data accessible without cross-repo path resolution.

**Plan-backed session impact:** No direct impact, but monorepo increases blast radius of a bad implementation TP — a TP that mutates templates could also mutate runtime code in one operation.

**Score: Best for UI simplicity, worst for authority boundary. Not recommended until authority boundary can be enforced mechanically.**

---

### Option C: Hybrid Workspace (Recommended for 30–90 days)

**What it is:** Two separate publishable packages in separate repos, with an optional shared workspace or parent config. Explicit package contracts:

```
packages:
  dopetask-runtime    → /Users/hue/code/dopeTask  (pip install dopetask)
  dope-agent-assets   → /Users/hue/code/dope-agent-system  (pip install dope-agent-assets)
  dopetask-ui         → future repo or src/dopetask/ui/
  dopetask-schemas    → extracted from dopetask, possibly published separately
```

A `dopetask.workspace.yaml` (or `.dopetask/workspace.yaml`) at a configured root ties the repos together for local development:
```yaml
repos:
  runtime: /Users/hue/code/dopeTask
  assets: /Users/hue/code/dope-agent-system
das_path: /Users/hue/code/dope-agent-system
```

**Product UX benefits:**
- dopeTask runtime consumers can install without dope-agent-system
- dope-agent-system can release versioned asset bundles independent of runtime
- Combined UI can reference both repos via workspace config
- Clear package contracts prevent accidental coupling

**Implementation complexity:** Medium. Requires:
- Adding `das_path` to dopeTask config (`.dopetask/workspace.yaml` or env var)
- Versioned releases of dope-agent-system as installable package
- Optional: workspace resolver in dopeTask to find asset paths

**Release/versioning model:** Independent versioning. dope-agent-system has its own release cadence. dopeTask consumes pinned releases. The pin in DOPETASK_VERSION_PIN.lock becomes a package version pin, not a path reference.

**Authority-boundary risk:** Low-Medium. Physical repo separation maintained. The workspace config is read-only from dopeTask's perspective — it points to assets, does not grant them execution authority.

**Testing strategy:** Unit tests per repo. Integration tests via workspace config (point to local path of dope-agent-system for development, point to installed release for CI).

**Migration cost:** Low-Medium. Mostly adding config/workspace resolution code to dopeTask. No file migration required.

**Packaging/install impact:** Consumers who don't need dope-agent-system assets don't install them. Consumers who want skills can `pip install dope-agent-assets` or configure das_path to local repo.

**Contributor/operator mental model:** Slightly more complex than pure separate repos, but workspace config makes it explicit. Clear.

**Proof/audit implications:** Each repo has its own proof chain. No cross-contamination.

**Combined UI impact:** Good. UI reads workspace config to find both repos. No hardcoded paths.

**Plan-backed session impact:** Positive. Workspace config can specify `permission_mode: bypassPermissions` and `auth_mode: subscription` (not bare), making it easy to ensure correct billing defaults are applied.

**Score: Best balance for 30–90 days.**

---

### Option D: Runtime Repo + Vendored/Released Asset Bundles

**What it is:** dopeTask consumes versioned releases of dope-agent-system as tarballs or pip packages. No local repo reference. dope-agent-system assets are "vendored" into a `vendor/dope-agent-assets/` directory inside dopeTask, or installed to a standard location.

**Product UX benefits:**
- Zero local path dependency
- dopeTask is fully self-contained post-install
- Releases are pinned and auditable

**Implementation complexity:** High for dope-agent-system (requires proper release pipeline). Low for dopeTask once assets are released.

**Release/versioning model:** dope-agent-system must have a release TP and CI/CD. Currently blocked (install targets are blocked until explicit release TP).

**Authority-boundary risk:** Low. Vendored assets cannot change without an explicit release and pin update.

**Score: Best for mature production state. Premature for current development phase.**

---

## 3. Option Comparison Matrix

| Criterion | A: Separate | B: Monorepo | C: Hybrid Workspace | D: Vendored Releases |
|-----------|------------|-------------|--------------------|--------------------|
| Authority boundary clarity | ★★★★★ | ★★★ | ★★★★ | ★★★★★ |
| Implementation effort | ★★★★★ | ★★ | ★★★★ | ★★ |
| Combined UI support | ★★★ | ★★★★★ | ★★★★ | ★★★ |
| Release simplicity | ★★★★★ | ★★★ | ★★★★ | ★★ |
| Contributor mental model | ★★★★★ | ★★★ | ★★★★ | ★★★★ |
| Proof/audit cleanliness | ★★★★★ | ★★★ | ★★★★★ | ★★★★★ |
| Plan-backed session safety | ★★★★ | ★★★ | ★★★★★ | ★★★★ |
| Migration cost | ★★★★★ | ★★ | ★★★★ | ★★ |

---

## 4. Recommended Strategy: 30-Day Window

**Option A: Separate repos, explicit contracts, no consolidation.**

Rationale:
- The immediate work (ClaudeCode runner implementation) requires no repo changes
- Both repos are currently clean and well-separated
- The boundary is formally decided and documented
- Consolidation risk is real: the monorepo creates a physical path by which LLMs and humans confuse template ownership with runtime authority
- The dope-agent-system release TP has not been authored; vendored releases are premature
- A hybrid workspace config (Option C starter) can be added as a 1-file addition to dopeTask without full consolidation

**30-day actions:**
1. Add `.dopetask/workspace.yaml` with `das_path` pointing to local dope-agent-system repo
2. Add `DOPE_AGENT_SYSTEM_PATH` env var support to dopeTask adapter config
3. Implement ClaudeCode runner (primary focus)
4. Keep both repos independent

---

## 5. Recommended Strategy: 90-Day Window

**Option C: Hybrid workspace with versioned releases.**

Rationale:
- By 90 days, the ClaudeCode runner should be implemented and exercised in real workflows
- dope-agent-system release TP should be authored and executed
- Once release artifacts exist, dopeTask can pin a version instead of a local path
- The workspace config can graduate from a local path reference to a version pin
- A combined UI can be started (Tier 1: CLI report command, Tier 1: TUI cockpit)

**90-day actions:**
1. Author and execute dope-agent-system release TP (blocked prerequisite)
2. Publish dope-agent-system as `pip install dope-agent-assets`
3. Replace `das_path` local path in workspace.yaml with `das_version: 0.1.0`
4. Implement `dopetask report <series_id>` markdown dashboard
5. Evaluate Tier 1 TUI if runner is stable

---

## 6. Conditions for Monorepo (Option B)

Only consider a monorepo when ALL of the following are true:
1. The authority boundary can be enforced by automated linting (e.g., import checks, namespace rules)
2. A shared CI pipeline can verify both runtime tests and template validity in one run
3. Both repos have settled and neither has pending breaking changes
4. A mechanical system (not documentation) prevents template files from being imported by runtime code
5. The combined UI is the primary developer experience and a monorepo genuinely simplifies it

Current status: **None of these conditions are met.**

---

## 7. Conditions for Staying Separate (Option A)

Stay with separate repos as long as ANY of the following are true:
1. Runtime and template boundaries are still being actively debated or clarified
2. dope-agent-system does not have a release pipeline
3. The combined UI is not yet the primary developer experience
4. Cross-repo confusion incidents occur (a TP accidentally modifying templates instead of runtime)
5. The ClaudeCode runner is not yet stable and exercised in real workflows

Current status: **All of these conditions are currently met.**

---

## 8. Merge Prerequisite Analysis

**Does merging make the product easier to use?**
Marginally, if the combined UI is the primary surface. Not meaningfully for CLI-first workflows.

**Does merging make authority boundaries less clear?**
Yes, unless mechanical enforcement exists. Physical separation is the cheapest enforcer.

**Does merging make UI development easier?**
Yes — single repo root, no cross-repo path resolution.

**Does merging make install/release simpler?**
No. It makes it more complex: consumers who want runtime don't need templates. Monorepo forces both.

**Does merging increase accidental runtime coupling?**
Yes. History shows that when template docs and runtime code share a repo, contributors and LLMs treat them as architecturally equivalent.

**Does a monorepo allow cleaner shared UI/data schemas?**
Yes, if schemas are extracted to a shared `packages/dopetask-schemas` package. This benefit can also be achieved with Option C.

**Can package boundaries preserve the current authority split?**
Yes, with explicit package contracts. But this requires mechanical enforcement.

**Smallest reversible step toward consolidation:**
Add `.dopetask/workspace.yaml` with `das_path` in dopeTask. This ties the repos logically without merging them physically. Fully reversible by deleting the config file.

---

## 9. Migration Path (if consolidation is chosen)

**Phase 1: Workspace config** (reversible)
- Add `.dopetask/workspace.yaml` to dopeTask
- Add `DOPE_AGENT_SYSTEM_PATH` env support
- Cost: 1 TP, ~1 day

**Phase 2: Package extraction** (reversible)
- Extract `dopetask-schemas` as separate package
- Add `dope-agent-assets` pip package for dope-agent-system
- Cost: 1–2 TPs, ~1 week

**Phase 3: Hybrid workspace** (Option C, reversible)
- Create workspace parent config tying both packages
- Combined UI reads workspace config
- Cost: 1 TP for config, 2–3 TPs for UI Tier 1
- Prerequisites: both packages have releases, ClaudeCode runner stable

**Phase 4: Monorepo consideration** (only after Phase 3 is stable)
- Only if authority boundary linting exists
- Cost: 1–2 days migration, 1 TP for validation, risk: HIGH

---

## 10. Rollback Path (if consolidation fails)

If a monorepo merge creates authority confusion incidents:
1. Extract runtime back to separate repo (git history is preserved in both)
2. Re-establish REFERENCE_ONLY markers and contracts
3. Restore separate CI pipelines
4. The workspace.yaml approach (Option C) provides a graceful landing zone without requiring full separation

The workspace config approach is designed as a rollback target. Keep it available.

---

## 11. Recommendation Summary

| Timeframe | Strategy | Action |
|-----------|----------|--------|
| **Now (0–30 days)** | Option A: Separate repos | Focus on ClaudeCode runner. Add `.dopetask/workspace.yaml` with das_path as the only consolidation step. |
| **30–90 days** | Option C: Hybrid workspace | Author dope-agent-system release TP. Publish `dope-agent-assets` package. Implement report command. |
| **90+ days** | Evaluate Option B | Only if authority boundary linting exists and combined UI is primary surface. |
| **Never (without prerequisites)** | Option B: Monorepo | Do not merge until mechanical boundary enforcement exists. |
