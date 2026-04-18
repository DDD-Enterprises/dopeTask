# dopeTask Architecture Source Index

[CODE] Coverage basis: the architecture bundle indexes **95** in-scope source and documentation files.
[CODE] Scope includes architecture docs/plans plus routing, orchestration, series, low-level execution, manual git, artifacts, manifests, project rails, runners, schemas, and adapter surfaces.
[CODE] Scope excludes previously generated `docs/specs/*` outputs and the general test tree; tests remain validation evidence for the architecture bundle but are not indexed here.
[CODE] Authority-role counts: `authoritative`=67, `docs-claim`=1, `plan`=7, `supporting`=20
[CODE] Provenance-class counts: `CODE`=70, `DOCS/PLANS`=25

| Path | Plane/subsystem | File type | Authority role | Provenance class | Purpose summary | Boundaries/invariants touched | Drift flag |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `docs/10_ARCHITECTURE.md` | architecture-plane-docs | .md | authoritative | DOCS/PLANS | Audience: Contributors, Maintainers Status: Normative Tone: Deterministic. | kernel-boundary; determinism; refusal | yes |
| `docs/11_PUBLIC_CONTRACT.md` | contract-docs | .md | authoritative | DOCS/PLANS | This document defines dopeTask's public, user-visible contract: inputs, outputs, determinism, exit codes, and non-goals. | kernel-boundary; determinism; refusal | yes |
| `docs/12_ROUTER.md` | routing-docs | .md | authoritative | DOCS/PLANS | dopeTask Router v1 selects runner/model pairs deterministically and writes route artifacts. | routing; route-plan; refusal | yes |
| `docs/13_TASK_PACKET_FORMAT.md` | contract-docs | .md | authoritative | DOCS/PLANS | This document defines the JSON `TaskPacket` contract for new dopeTask work. | TaskPacket-contract; schema-loading; parser-normalizer | yes |
| `docs/14_PROJECT_DOCTOR.md` | project-prompt-docs | .md | authoritative | DOCS/PLANS | The project doctor inspects a repository and reports integrity status. | project-rails; install-integrity; prompt-surface | no |
| `docs/20_WORKTREES_COMMIT_SEQUENCING.md` | manual-integration-docs | .md | supporting | DOCS/PLANS | This document is maintainer-level. | manual-git; dirty-main-guard; branch-isolation | no |
| `docs/21_CASE_BUNDLES.md` | manual-integration-docs | .md | supporting | DOCS/PLANS | dopeTask introduces "Case Bundles" as a meta-layer for ingesting, auditing, and reviewing task execution across environments. | artifacts; proof-bundle; audit-surface | no |
| `docs/22_WORKFLOW_GUIDE.md` | operator-flow-docs | .md | authoritative | DOCS/PLANS | This guide details the modern, DAG-aware workflow for executing complex tasks using `dopeTask` series. | series-ledger; DAG-readiness; worktree-lifecycle | yes |
| `docs/23_INTEGRATION_GUIDE.md` | operator-flow-docs | .md | authoritative | DOCS/PLANS | This guide provides patterns for integrating `dopeTask` with CI/CD pipelines, custom agents, and external systems. | architecture | yes |
| `docs/24_UPGRADE_GUIDE.md` | operator-flow-docs | .md | authoritative | DOCS/PLANS | This guide covers the operator-facing changes introduced by the JSON TP series workflow in `dopeTask` `0.5.x`. | series-ledger; DAG-readiness; worktree-lifecycle | no |
| `docs/26_SUPERVISOR_PROMPTS.md` | project-prompt-docs | .md | authoritative | DOCS/PLANS | This is the canonical guide for generating, exporting, and installing dopeTask supervisor prompts. | project-rails; install-integrity; prompt-surface | yes |
| `docs/KERNEL_PRINCIPLES.md` | architecture-plane-docs | .md | authoritative | DOCS/PLANS | dopeTask operates as a constrained kernel, not an improvisational assistant. | kernel-boundary; determinism; refusal | no |
| `docs/PR_FLOW.md` | manual-integration-docs | .md | authoritative | DOCS/PLANS | dopeTask PR flow opens a pull request with refusal rails and branch restore semantics. | manual-git; dirty-main-guard; branch-isolation | no |
| `docs/REFUSAL_PHILOSOPHY.md` | manual-integration-docs | .md | supporting | DOCS/PLANS | dopeTask does not treat refusal as a failure mode. | kernel-boundary; determinism; refusal | no |
| `docs/TP_GIT_WORKFLOW.md` | manual-integration-docs | .md | supporting | DOCS/PLANS | This document describes the legacy/manual `dopetask tp git` path. | manual-git; dirty-main-guard; branch-isolation | no |
| `docs/architecture/dopetask-supervisor-executor-adapter-spec.md` | architecture-plane-docs | .md | docs-claim | DOCS/PLANS | This document defines the structural relationship between the `dopeTask` execution kernel and its external provider interfaces. | architecture | yes |
| `docs/integrations/dopetask/ADAPTER_SCHEMA.md` | manual-integration-docs | .md | supporting | DOCS/PLANS | This is the normalized integration envelope Dopemux can use internally after reading canonical dopeTask artifacts. | integration-adapter; derived-envelope | no |
| `docs/llm/SUPERVISOR_SYSTEM_PROMPT.md` | project-prompt-docs | .md | supporting | DOCS/PLANS | Preferred generation path: use `dopetask ops export` to generate `ops/EXPORTED_OPERATOR_PROMPT.md` for the current platform and model. | architecture | no |
| `docs/plans/dopeTask_higher_level_recovery_plan.md` | architecture-plans | .md | plan | DOCS/PLANS | This plan resets the project around three realities: 1. | transitional-intent; roadmap; architecture-drift | yes |
| `docs/plans/dopetask-multi-mode-execution-plan.md` | architecture-plans | .md | plan | DOCS/PLANS | Transition the `dopeTask` kernel from a monolithic "script-runner" to a formal "Adapter-Executor" architecture. | transitional-intent; roadmap; architecture-drift | yes |
| `llm-plans/TP-CORE-001-gemini-adapter.md` | architecture-plans | .md | plan | DOCS/PLANS | Create a deterministic execution wrapper (adapter layer) for the Gemini CLI so it can execute Task Packets (TPs) rigidly, without drifting, and produce structured, audit-safe proof bundles. | transitional-intent; roadmap; architecture-drift | yes |
| `llm-plans/TP-CORE-002-tp-parser-normalizer.md` | architecture-plans | .md | plan | DOCS/PLANS | Create the Task Packet (TP) Parser and Normalization layer to ingest generic TPs and compile them down into distinct agent execution profiles: Gemini (STRICT_EXECUTOR), Codex (SMART_IMPLEMENTER), and Vibe (MICRO_TASK). | transitional-intent; roadmap; architecture-drift | yes |
| `llm-plans/TP-CORE-003-cli-runner.md` | architecture-plans | .md | plan | DOCS/PLANS | Create a unified CLI interface (`dopetask tp exec`) to trigger the Task Packet (TP) parsing, normalization, and agent-specific execution flow. | transitional-intent; roadmap; architecture-drift | yes |
| `llm-plans/TP-OBS-005-proof-aggregation.md` | architecture-plans | .md | plan | DOCS/PLANS | Aggregate the deterministic execution proofs generated by the `GeminiExecutor` (TP-CORE-001) into a fully compliant, standardized audit surface. | transitional-intent; roadmap; architecture-drift | yes |
| `llm-plans/TP-UX-004-operator-interface.md` | architecture-plans | .md | plan | DOCS/PLANS | Provide a seamless, robust operator interface using `tmux` to manage isolated execution sessions for Task Packets. | tmux-session; operator-surface | yes |
| `src/dopetask/artifacts/__init__.py` | artifact-plane | .py | supporting | CODE | Deterministic artifact utilities for dopeTask orchestration. | artifacts; proof-bundle; audit-surface | no |
| `src/dopetask/artifacts/canonical_json.py` | artifact-plane | .py | authoritative | CODE | Canonical JSON helpers for deterministic dopeTask artifacts. | artifacts; proof-bundle; audit-surface | no |
| `src/dopetask/artifacts/writer.py` | artifact-plane | .py | authoritative | CODE | Deterministic artifact writer for orchestrator runs. | artifacts; proof-bundle; audit-surface | no |
| `src/dopetask/core/schema.py` | contract-schema-plane | .py | authoritative | CODE | Task Packet (TP) schema definitions. | TaskPacket-contract; schema-loading; parser-normalizer | no |
| `src/dopetask/core/tp_parser.py` | contract-schema-plane | .py | authoritative | CODE | Task Packet Parser and Normalizer. | TaskPacket-contract; schema-loading; parser-normalizer | yes |
| `src/dopetask/doctor.py` | project-rails-plane | .py | authoritative | CODE | dopeTask installation integrity checker (doctor command). | project-rails; install-integrity; prompt-surface | no |
| `src/dopetask/manifest/__init__.py` | manifest-plane | .py | supporting | CODE | Task packet manifest module. | manifest; replay-checks; command-log | no |
| `src/dopetask/manifest/manifest.py` | manifest-plane | .py | authoritative | CODE | Task packet manifest helpers for run auditability and replay checks. | manifest; replay-checks; command-log | no |
| `src/dopetask/obs/proof_aggregator.py` | proof-plane | .py | authoritative | CODE | Aggregator for Task Packet execution proofs. | artifacts; proof-bundle; audit-surface | no |
| `src/dopetask/obs/run_artifacts.py` | proof-plane | .py | authoritative | CODE | Canonical run artifact helpers for stateful dopeTask commands. | artifacts; proof-bundle; audit-surface | no |
| `src/dopetask/ops/tp_exec/__init__.py` | low-level-exec-plane | .py | supporting | CODE | Package marker for low-level Task Packet execution commands. | ExecutionResult; adapter-contract; low-level-exec | no |
| `src/dopetask/ops/tp_exec/cli.py` | low-level-exec-plane | .py | authoritative | CODE | CLI registration for dopetask tp exec command. | ExecutionResult; adapter-contract; low-level-exec | yes |
| `src/dopetask/ops/tp_exec/engine.py` | low-level-exec-plane | .py | authoritative | CODE | Reusable execution engine for JSON Task Packets. | ExecutionResult; adapter-contract; low-level-exec | yes |
| `src/dopetask/ops/tp_git/__init__.py` | manual-git-plane | .py | supporting | CODE | Task Packet git workflow package. | manual-git; dirty-main-guard; branch-isolation | no |
| `src/dopetask/ops/tp_git/cli.py` | manual-git-plane | .py | authoritative | CODE | CLI surface for dopetask tp git workflows. | manual-git; dirty-main-guard; branch-isolation | no |
| `src/dopetask/ops/tp_git/exec.py` | manual-git-plane | .py | authoritative | CODE | Command runners for TP git workflows. | manual-git; dirty-main-guard; branch-isolation | no |
| `src/dopetask/ops/tp_git/git_worktree.py` | manual-git-plane | .py | authoritative | CODE | Worktree lifecycle helpers for dopetask tp git commands. | manual-git; dirty-main-guard; branch-isolation | no |
| `src/dopetask/ops/tp_git/github.py` | manual-git-plane | .py | authoritative | CODE | GitHub integrations for dopetask tp git commands. | manual-git; dirty-main-guard; branch-isolation | no |
| `src/dopetask/ops/tp_git/guards.py` | manual-git-plane | .py | authoritative | CODE | Fail-closed guards for dopetask tp git commands. | manual-git; dirty-main-guard; branch-isolation | no |
| `src/dopetask/ops/tp_git/naming.py` | manual-git-plane | .py | authoritative | CODE | Deterministic naming helpers for dopetask tp git workflows. | manual-git; dirty-main-guard; branch-isolation | no |
| `src/dopetask/ops/tp_git/types.py` | manual-git-plane | .py | authoritative | CODE | Types for dopetask tp git workflow. | manual-git; dirty-main-guard; branch-isolation | no |
| `src/dopetask/ops/tp_series/__init__.py` | series-plane | .py | supporting | CODE | DAG-aware TP series workflow commands. | series-ledger; DAG-readiness; worktree-lifecycle | no |
| `src/dopetask/ops/tp_series/cli.py` | series-plane | .py | authoritative | CODE | CLI surface for DAG-aware TP series commands. | series-ledger; DAG-readiness; worktree-lifecycle | yes |
| `src/dopetask/ops/tp_series/logic.py` | series-plane | .py | authoritative | CODE | DAG-aware JSON Task Packet series orchestration. | series-ledger; DAG-readiness; worktree-lifecycle | yes |
| `src/dopetask/ops/tp_tmux/__init__.py` | tmux-plane | .py | supporting | CODE | Package marker for tmux-backed Task Packet session management. | tmux-session; operator-surface | no |
| `src/dopetask/ops/tp_tmux/cli.py` | tmux-plane | .py | authoritative | CODE | CLI registration for dopetask tmux commands. | tmux-session; operator-surface | no |
| `src/dopetask/ops/tp_tmux/tmux_manager.py` | tmux-plane | .py | authoritative | CODE | Tmux session manager for Task Packet isolation. | tmux-session; operator-surface | no |
| `src/dopetask/orchestrator/__init__.py` | orchestration-plane | .py | supporting | CODE | dopeTask orchestrator kernel entrypoints. | orchestrate-v0; handoff; run-artifacts | no |
| `src/dopetask/orchestrator/handoff.py` | orchestration-plane | .py | authoritative | CODE | Deterministic manual handoff chunk builder. | orchestrate-v0; handoff; run-artifacts | no |
| `src/dopetask/orchestrator/kernel.py` | orchestration-plane | .py | authoritative | CODE | dopeTask orchestrator v0 kernel. | orchestrate-v0; handoff; run-artifacts | yes |
| `src/dopetask/pipeline/task_runner/__init__.py` | execution-contract-plane | .py | supporting | CODE | Task runner module. | ExecutionResult; adapter-contract; low-level-exec | no |
| `src/dopetask/pipeline/task_runner/executor.py` | execution-contract-plane | .py | authoritative | CODE | Core task execution kernel. | ExecutionResult; adapter-contract; low-level-exec | yes |
| `src/dopetask/pipeline/task_runner/parser.py` | execution-contract-plane | .py | authoritative | CODE | Task packet parser. | ExecutionResult; adapter-contract; low-level-exec | no |
| `src/dopetask/pipeline/task_runner/runner.py` | execution-contract-plane | .py | authoritative | CODE | Task packet runner. | ExecutionResult; adapter-contract; low-level-exec | no |
| `src/dopetask/pipeline/task_runner/types.py` | execution-contract-plane | .py | authoritative | CODE | Task runner types. | ExecutionResult; adapter-contract; low-level-exec | no |
| `src/dopetask/project/__init__.py` | project-rails-plane | .py | supporting | CODE | Project initialization and directive pack toggles. | project-rails; install-integrity; prompt-surface | no |
| `src/dopetask/project/common.py` | project-rails-plane | .py | authoritative | CODE | Shared helpers for project init and directive pack toggles. | project-rails; install-integrity; prompt-surface | no |
| `src/dopetask/project/doctor.py` | project-rails-plane | .py | authoritative | CODE | Project readiness doctor for dopeTask/ChatX directive workflows. | project-rails; install-integrity; prompt-surface | no |
| `src/dopetask/project/init.py` | project-rails-plane | .py | authoritative | CODE | Project initialization for supervisor and LLM config files. | project-rails; install-integrity; prompt-surface | no |
| `src/dopetask/project/mode.py` | project-rails-plane | .py | authoritative | CODE | Master project mode toggle for dopeTask/ChatX directive packs. | project-rails; install-integrity; prompt-surface | no |
| `src/dopetask/project/shell.py` | project-rails-plane | .py | authoritative | CODE | Repo-local shell wiring helpers for dopeTask. | project-rails; install-integrity; prompt-surface | no |
| `src/dopetask/project/toggles.py` | project-rails-plane | .py | authoritative | CODE | Deterministic dopeTask/ChatX directive pack toggles. | project-rails; install-integrity; prompt-surface | no |
| `src/dopetask/project/upgrade.py` | project-rails-plane | .py | authoritative | CODE | Deterministic project upgrade orchestrator. | project-rails; install-integrity; prompt-surface | no |
| `src/dopetask/router/__init__.py` | routing-plane | .py | supporting | CODE | dopeTask assisted routing subsystem. | routing; route-plan; refusal | no |
| `src/dopetask/router/availability.py` | routing-plane | .py | authoritative | CODE | Load and validate router availability configuration. | routing; route-plan; refusal | no |
| `src/dopetask/router/handoff.py` | routing-plane | .py | authoritative | CODE | Handoff renderer for assisted routing plans. | routing; route-plan; refusal | no |
| `src/dopetask/router/planner.py` | routing-plane | .py | authoritative | CODE | Deterministic router planner. | routing; route-plan; refusal | yes |
| `src/dopetask/router/reporting.py` | routing-plane | .py | authoritative | CODE | Deterministic route report writers. | routing; route-plan; refusal | yes |
| `src/dopetask/router/scoring.py` | routing-plane | .py | authoritative | CODE | Deterministic candidate scoring for routing decisions. | routing; route-plan; refusal | no |
| `src/dopetask/router/types.py` | routing-plane | .py | authoritative | CODE | Router domain types for assisted routing v1. | routing; route-plan; refusal | no |
| `src/dopetask/runners/__init__.py` | runner-plane | .py | supporting | CODE | Runner adapters for dopeTask orchestrator. | runner-registry; orchestrator-runner | no |
| `src/dopetask/runners/base.py` | runner-plane | .py | authoritative | CODE | Runner adapter protocol for orchestrator execution. | runner-registry; orchestrator-runner | no |
| `src/dopetask/runners/claude_code.py` | runner-plane | .py | authoritative | CODE | Claude Code runner adapter (v0 deterministic refusal stub). | runner-registry; orchestrator-runner | no |
| `src/dopetask/runners/codex_cli.py` | runner-plane | .py | authoritative | CODE | Codex Desktop runner adapter (v0 deterministic refusal stub). | runner-registry; orchestrator-runner | no |
| `src/dopetask/runners/copilot_cli.py` | runner-plane | .py | authoritative | CODE | Copilot CLI runner adapter (v0 deterministic refusal stub). | runner-registry; orchestrator-runner | no |
| `src/dopetask/runners/google_jules.py` | runner-plane | .py | authoritative | CODE | Google Jules runner adapter (v0 deterministic refusal stub). | runner-registry; orchestrator-runner | no |
| `src/dopetask/schemas/__init__.py` | contract-schema-plane | .py | supporting | CODE | dopeTask schemas package. | TaskPacket-contract; schema-loading; parser-normalizer | no |
| `src/dopetask/schemas/validator.py` | contract-schema-plane | .py | authoritative | CODE | Schema validation utilities for dopeTask using package-data-only registry. | TaskPacket-contract; schema-loading; parser-normalizer | no |
| `src/dopetask/utils/schema_registry.py` | contract-schema-plane | .py | authoritative | CODE | Schema registry for dopeTask with package-data-only loading. | TaskPacket-contract; schema-loading; parser-normalizer | yes |
| `src/dopetask_adapters/__init__.py` | adapter-integration-plane | .py | supporting | CODE | dopeTask adapters for integrating with external systems. | integration-adapter; derived-envelope | no |
| `src/dopetask_adapters/base.py` | adapter-integration-plane | .py | authoritative | CODE | Base adapter interface for dopeTask integration adapters. | integration-adapter; derived-envelope | no |
| `src/dopetask_adapters/dopemux.py` | adapter-integration-plane | .py | authoritative | CODE | Dopemux adapter for dopeTask integration. | integration-adapter; derived-envelope | no |
| `src/dopetask_adapters/gemini/__init__.py` | adapter-integration-plane | .py | supporting | CODE | Gemini CLI execution adapter components. | Gemini-adapter; transitional-proof; shell-exec | no |
| `src/dopetask_adapters/gemini/executor.py` | adapter-integration-plane | .py | authoritative | CODE | Gemini adapter step executor that maps command runs into `ExecutionResult` records. | Gemini-adapter; transitional-proof; shell-exec | yes |
| `src/dopetask_adapters/gemini/prompts.py` | adapter-integration-plane | .py | authoritative | CODE | Multi-turn execution prompts for Gemini, Codex, and Vibe adapters. | Gemini-adapter; transitional-proof; shell-exec | no |
| `src/dopetask_adapters/gemini/proof_writer.py` | adapter-integration-plane | .py | authoritative | CODE | Transitional Gemini raw-proof writer for `<TP_ID>_PROOF.json` and `TRACE.log`. | Gemini-adapter; transitional-proof; shell-exec | yes |
| `src/dopetask_adapters/gemini/schema.py` | adapter-integration-plane | .py | authoritative | CODE | Gemini adapter typed schemas for prompts, steps, and execution proof structures. | Gemini-adapter; transitional-proof; shell-exec | no |
| `src/dopetask_adapters/gemini/step_runner.py` | adapter-integration-plane | .py | authoritative | CODE | Shell-backed Gemini step runner that executes step commands and captures outputs. | Gemini-adapter; transitional-proof; shell-exec | yes |
| `src/dopetask_adapters/gemini/validator.py` | adapter-integration-plane | .py | authoritative | CODE | Gemini adapter validation helpers for execution requests and proof shapes. | Gemini-adapter; transitional-proof; shell-exec | no |
| `src/dopetask_adapters/types.py` | adapter-integration-plane | .py | authoritative | CODE | Type definitions for dopeTask adapters. | integration-adapter; derived-envelope | no |
