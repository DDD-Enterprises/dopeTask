# dopeTask Docs Source Index

[DOCS/PLANS] Scope basis: this index covers the 38 tracked documentation and plan files selected for the architecture + product docs canon pass.

[CODE] Exclusions from this index: `docs/specs/*`, proof-only docs, schema-only docs, release/audit artifact docs, archive docs, and untracked local guides such as `docs/guides/PAL_*`.

## Core and Operator Docs

| Path | Subsystem/doc family | File type | Authority role | Provenance class | Purpose summary | Key claims/contracts touched | Drift flag |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `docs/00_OVERVIEW.md` | core-overview | `.md` | authoritative | DOCS/PLANS | Maps the current documentation set and frames dopeTask as a deterministic kernel. | docs navigation; default workflow framing; product identity | no |
| `docs/01_SETUP.md` | setup | `.md` | authoritative | DOCS/PLANS | Defines development and repo setup prerequisites, install paths, and prompt bootstrap steps. | Python/git/gh requirements; `setup-git`; `ops init`; `ops apply` | no |
| `docs/10_ARCHITECTURE.md` | architecture | `.md` | authoritative | DOCS/PLANS | States the kernel philosophy, execution spine, packet-law, refusal model, and artifact-first posture. | execution spine; packet law; determinism; refusal | yes |
| `docs/11_PUBLIC_CONTRACT.md` | public-contract | `.md` | authoritative | DOCS/PLANS | Defines user-visible contract language for inputs, outputs, determinism, exit codes, and non-goals. | output surfaces; exit codes; public inputs | yes |
| `docs/12_ROUTER.md` | router-docs | `.md` | authoritative | DOCS/PLANS | Documents Router v1 flow, route artifacts, and availability config. | route planning; `availability.yaml`; handoff artifacts | yes |
| `docs/13_TASK_PACKET_FORMAT.md` | task-packet-json | `.md` | authoritative | DOCS/PLANS | Canonical JSON Task Packet reference for new work. | JSON TP schema; series fields; execution flow | yes |
| `docs/14_PROJECT_DOCTOR.md` | project-doctor | `.md` | authoritative | DOCS/PLANS | Describes doctor semantics, PASS/WARN/FAIL behavior, and operator prompt export policy. | doctor exit semantics; fix-mode boundary; ops doctor export policy | no |
| `docs/20_WORKTREES_COMMIT_SEQUENCING.md` | legacy-worktree-flow | `.md` | supporting | DOCS/PLANS | Maintainer-only manual worktree and commit-sequence reference. | `wt start`; `commit-sequence`; `finish`; dirty policy | no |
| `docs/21_CASE_BUNDLES.md` | case-bundles | `.md` | supporting | DOCS/PLANS | Defines case bundle, implementer report, and supervisor review concepts for auditing. | case transfer artifacts; schema names; review vocabulary | no |
| `docs/22_WORKFLOW_GUIDE.md` | series-workflow | `.md` | authoritative | DOCS/PLANS | Canonical operator guide for the JSON TP series lifecycle. | `tp series exec/status/finalize`; worktree lifecycle; series ledger | yes |
| `docs/23_INTEGRATION_GUIDE.md` | integration | `.md` | authoritative | DOCS/PLANS | Canonical integration guide for CI, external agents, proof ingestion, and series-state consumption. | CI usage; agent integration; proof bundle consumption; series state | yes |
| `docs/24_UPGRADE_GUIDE.md` | upgrade | `.md` | authoritative | DOCS/PLANS | Migration guide from older packet/workflow assumptions into the JSON TP series flow. | default path migration; series state authority; proof review | no |
| `docs/25_CONSUMER_INSTALL.md` | downstream-install | `.md` | authoritative | DOCS/PLANS | Downstream consumer install guide for non-vendored use. | install script; repo-local venv; top-level upgrade flow | yes |
| `docs/26_SUPERVISOR_PROMPTS.md` | prompt-lifecycle | `.md` | authoritative | DOCS/PLANS | Canonical guide for generating, exporting, previewing, and applying supervisor prompts. | `ops export`; `ops apply`; target files; model/version recommendations | yes |
| `docs/DISTRIBUTION_GUIDE.md` | release-distribution | `.md` | supporting | DOCS/PLANS | Release maintainer guide for PyPI distribution through GitHub Actions. | version bump flow; tagging; publish/install paths | no |
| `docs/KERNEL_PRINCIPLES.md` | kernel-principles | `.md` | authoritative | DOCS/PLANS | Concise statement of kernel invariants and design consequences. | packet law; refusal; determinism; version pinning | no |
| `docs/PR_FLOW.md` | pr-flow | `.md` | authoritative | DOCS/PLANS | Documents assisted PR opening, refusal rails, restore semantics, and report artifacts. | `pr open`; restore behavior; report paths | no |
| `docs/REFUSAL_PHILOSOPHY.md` | refusal | `.md` | supporting | DOCS/PLANS | Explains why refusal is treated as an integrity boundary rather than ordinary failure. | refusal philosophy; evidence boundary; operator posture | no |
| `docs/TASK_PACKET_FORMAT.md` | task-packet-redirect | `.md` | supporting | DOCS/PLANS | Redirect shim pointing readers to the canonical JSON packet doc. | packet-format redirection; compatibility notice | no |
| `docs/TP_GIT_WORKFLOW.md` | legacy-tp-git | `.md` | supporting | DOCS/PLANS | Legacy/manual `tp git` workflow reference. | `tp git` doctor/start/pr/merge/sync-main/cleanup | no |

## Architecture, Onboarding, and Design Docs

| Path | Subsystem/doc family | File type | Authority role | Provenance class | Purpose summary | Key claims/contracts touched | Drift flag |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `docs/architecture/dopetask-supervisor-executor-adapter-spec.md` | architecture-spec | `.md` | docs-claim | DOCS/PLANS | Transitional architecture spec for supervisor, executor, adapter, and ExecutionResult responsibilities. | adapter-executor contract; worktree lifecycle; degraded mode | yes |
| `docs/beginner/00A_HOW_DOPETASK_WORKS.md` | beginner-how-it-works | `.md` | supporting | DOCS/PLANS | Beginner explanation of structured tasks, supervisors, implementers, proof bundles, and git isolation. | product positioning; agent roles; proof bundle value | yes |
| `docs/beginner/00_WELCOME.md` | beginner-welcome | `.md` | supporting | DOCS/PLANS | Introductory onboarding narrative for safe AI-assisted coding with dopeTask. | product narrative; worktree isolation; proof bundle promise | yes |
| `docs/beginner/01_CONCEPTS.md` | beginner-concepts | `.md` | supporting | DOCS/PLANS | Beginner glossary translating repository and workflow terminology into plain language. | terminology alignment; onboarding vocabulary | no |
| `docs/beginner/02_INSTALLATION.md` | beginner-install | `.md` | supporting | DOCS/PLANS | Tutorial setup walkthrough that delegates canonical reference to `docs/01_SETUP.md`. | beginner install path; canonical setup handoff | no |
| `docs/beginner/03_WEB_LLM_SETUP.md` | beginner-web-supervisor | `.md` | supporting | DOCS/PLANS | Tutorial for configuring a web LLM to behave as a dopeTask supervisor. | web supervisor behavior; prompt application; no-direct-code doctrine | no |
| `docs/beginner/04_WORKFLOW.md` | beginner-workflow | `.md` | supporting | DOCS/PLANS | Tutorial daily workflow for beginners, delegating canonical operator behavior to top-level workflow docs. | beginner series loop; proof review; top-level doc handoff | yes |
| `docs/guides/dopetask-pal-integration-playbook.md` | pal-guide | `.md` | docs-claim | DOCS/PLANS | Operator guide describing PAL as a thinking layer distinct from dopeTask execution. | PAL chaining; supervisor cycle; correction TP flow | yes |
| `docs/integrations/dopetask/ADAPTER_SCHEMA.md` | dopemux-adapter | `.md` | supporting | DOCS/PLANS | Defines the derived Dopemux integration envelope built from canonical dopeTask artifacts. | adapter envelope; canonical input artifacts; status vocabulary | no |
| `docs/llm/DOPETASK_OPERATOR_SYSTEM.md` | generated-llm-asset | `.md` | supporting | DOCS/PLANS | Generated operator prompt artifact with embedded version, commit, and project metadata. | point-in-time operator prompt output; generated metadata | yes |
| `docs/llm/SUPERVISOR_SYSTEM_PROMPT.md` | manual-llm-prompt | `.md` | supporting | DOCS/PLANS | Manual fallback supervisor prompt source for web UI workflows. | supervisor role; no-direct-code doctrine; Task Packet authoring | no |

## Plans and Transitional Intent

| Path | Subsystem/doc family | File type | Authority role | Provenance class | Purpose summary | Key claims/contracts touched | Drift flag |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `docs/plans/dopeTask_higher_level_recovery_plan.md` | recovery-plan | `.md` | plan | DOCS/PLANS | Recovery plan for hardening docs, reviewing salvage code, and restoring execution discipline. | architecture repair; PAL productization; phased restart | yes |
| `docs/plans/dopetask-multi-mode-execution-plan.md` | multi-mode-plan | `.md` | plan | DOCS/PLANS | Phased implementation plan for adapter-executor architecture and multi-mode execution. | `ExecutionResult`; shell adapter; shadow mode; telemetry | yes |
| `llm-plans/TP-CORE-001-gemini-adapter.md` | llm-plan-adapter | `.md` | plan | DOCS/PLANS | Historical plan for a deterministic Gemini adapter and agent-specific prompt systems. | Gemini adapter; multi-turn prompt systems; audit-safe proof | yes |
| `llm-plans/TP-CORE-002-tp-parser-normalizer.md` | llm-plan-parser | `.md` | plan | DOCS/PLANS | Historical plan for parser and normalization layers targeting multiple agent profiles. | parser normalization; validation rails; multi-agent compile targets | yes |
| `llm-plans/TP-CORE-003-cli-runner.md` | llm-plan-cli-runner | `.md` | plan | DOCS/PLANS | Historical plan for `dopetask tp exec` as a unified agent-execution CLI runner. | `tp exec`; parser-to-adapter linkage; execution triggers | yes |
| `llm-plans/TP-OBS-005-proof-aggregation.md` | llm-plan-proof | `.md` | plan | DOCS/PLANS | Historical plan for proof aggregation and standardized audit surfaces. | proof bundle standardization; archive contract; audit surface | yes |
| `llm-plans/TP-UX-004-operator-interface.md` | llm-plan-tmux | `.md` | plan | DOCS/PLANS | Historical plan for tmux-backed operator UX and detached task execution sessions. | tmux commands; `tp exec --tmux`; operator monitoring | yes |
