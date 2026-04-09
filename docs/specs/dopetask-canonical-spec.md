# dopeTask Canonical Spec (Current State)

## Scope and Provenance

- [CODE] This spec is grounded in **402 tracked files** discovered via `git ls-files`, plus verified runtime help output from `python -m dopetask --help`, `python -m dopetask route --help`, `python -m dopetask tp series --help`, `python -m dopetask tp exec --help`, and `python -m dopetask orchestrate --help`.
- [CODE] Runtime code, packaged schemas, tests, and verified CLI output are treated as the current-state authority (`pyproject.toml`, `src/dopetask/*`, `src/dopetask_adapters/*`, `dopetask_schemas/*`, `tests/*`).
- [DOCS/PLANS] README, numbered docs, guides, plans, checked-in proof bundles, and checked-in reports are treated as claims, historical intent, or examples unless code or runtime proves them (`README.md`, `docs/*`, `proof/*`, `IMPLEMENTER_REPORT_*.json`, `TP-AUDIT-*.json`).
- [INFERRED] Recommendations are isolated in the final section and are not presented as current runtime truth.

## Repository Composition

- [CODE] Tracked file mix at generation time: `402` total, `221` Python files, `87` Markdown files, `44` JSON files, `21` shell scripts, and `14` YAML files.
- [CODE] Major tracked roots: `.claude`=2, `.cursor`=1, `.dopetask`=1, `.dopetaskroot`=1, `.github`=13, `.gitignore`=1, `.vibe`=2, `AGENTS.md`=1, `CHANGELOG.md`=1, `CLAUDE.md`=1, `CODEX.md`=1, `CONTRIBUTING.md`=1, `DOPETASK_INTEGRATION_GUIDE.md`=1, `DOPETASK_MIGRATION_GUIDE.md`=1, `DOPETASK_VERSION.lock`=1, `Dockerfile`=1, `GEMINI.md`=1, `IMPLEMENTER_REPORT_0001_0002.json`=1, `IMPLEMENTER_REPORT_0003_0004.json`=1, `LICENSE`=1, `README.md`=1, `README_DOPETASK_INSTALL.md`=1, `SECURITY.md`=1, `TP-AUDIT-057B-PROMPT-PIPELINE.json`=1, `TP-AUDIT-057C-PROMPT-PIPELINE.json`=1, `TP-AUDIT-057D-PROMPT-PIPELINE.json`=1, `TP-AUDIT-057E-PROMPT-PIPELINE.json`=1, `config`=1, `docs`=51, `dopetask_bundle.yaml`=1, `dopetask_schemas`=13, `llm-plans`=5, `ops`=10, `proof`=4, `pyproject.toml`=1, `reorganize_dopetask.py`=1, `schemas`=20, `scripts`=30, `src`=155, `tests`=68, `uv.lock`=1.
- [CODE] The repo is multi-era rather than single-surface: current JSON TP series code coexists with route/orchestrate subsystems, legacy worktree/commit sequencing, operator prompt tooling, case-bundle auditing, and proof-contract standards (`src/dopetask/cli.py`, `src/dopetask/router/*`, `src/dopetask/ops/tp_series/*`, `src/dopetask/git/*`, `src/dopetask/ops/*`, `src/dopetask/pipeline/*`).

## Product Identity and Authority Layers

- [CODE] Package metadata identifies `dopetask` as version `0.5.7`, a deterministic task-packet execution kernel with proof bundles, worktree isolation, and series-based PR workflows (`pyproject.toml`).
- [DOCS/PLANS] README and overview docs frame the product as artifact-first, refusal-first, deterministic, and single-path (`README.md`, `docs/00_OVERVIEW.md`, `docs/10_ARCHITECTURE.md`).
- [CODE] The runtime authority stack is split across executable code, packaged schemas, and tests: CLI registration (`src/dopetask/cli.py`), validation and schema loading (`src/dopetask/schemas/validator.py`, `src/dopetask/utils/schema_registry.py`), workflow implementations (`src/dopetask/ops/*`, `src/dopetask/git/*`, `src/dopetask/router/*`, `src/dopetask/orchestrator/*`), and regression tests (`tests/*`).
- [CODE] Formal proof-contract schemas live under `proof/standards/*.json` and are enforced by tests rather than runtime loading (`proof/standards/PROOF_BUNDLE_SCHEMA.json`, `tests/unit/obs/test_proof_contract_assets.py`).
- [DOCS/PLANS] The repo also carries several claim layers that are not runtime-enforced by themselves: numbered docs, architecture/spec plans, beginner guides, root instruction files, and integration examples (`docs/*`, `AGENTS.md`, `CLAUDE.md`, `CODEX.md`, `GEMINI.md`).

## Public CLI Surface

- [CODE] The installed CLI entrypoint is `dopetask = "dopetask.cli:cli"` (`pyproject.toml`).
- [CODE] Verified top-level runtime command families are: `worship` (console-only cosmetic easter egg), `init` (repo bootstrap), `compile-tasks` (legacy pipeline task compilation), `run-task` (legacy run-workspace execution), `collect-evidence` (legacy evidence collection), `gate-allowlist` (legacy compliance gating), `promote-run` (legacy promotion token issuance), `commit-run` (legacy commit artifact flow), `spec-feedback` (legacy feedback generation), `loop` (legacy full lifecycle loop), `commit-sequence` (legacy markdown packet commit sequencing), `finish` (legacy task-branch finalize flow), `orchestrate` (orchestrator v0 run path), `doctor` (repo and install diagnostics), `upgrade` (repo upgrade flow), `ci-gate` (combined CI/doctor checks), `ops` (operator prompt and instruction management), `neon` (console cosmetics), `metrics` (local usage metrics toggles), `tp` (task packet execution family), `tmux` (tmux isolation helpers), `manifest` (run-manifest lifecycle), `wt` (worktree lifecycle), `docs` (docs maintenance helpers), `route` (deterministic routing), `pr` (assisted PR flow), `dopemux` (Dopemux integration), `project` (repo file initialization and mode toggles), `bundle` (case-bundle management), `case` (case auditing) (`python -m dopetask --help`, `src/dopetask/cli.py`).
- [CODE] Verified `route` subcommands are `init`, `plan`, `handoff`, and `explain` (`python -m dopetask route --help`, `src/dopetask/cli.py`, `src/dopetask/router/*`).
- [CODE] Verified `tp series` subcommands are only `exec`, `status`, and `finalize` at runtime (`python -m dopetask tp series --help`, `src/dopetask/ops/tp_series/cli.py`).
- [CODE] Verified `tp exec` is present as a low-level JSON packet executor and currently advertises `--agent gemini|codex|vibe` even though only Gemini is implemented (`python -m dopetask tp exec --help`, `src/dopetask/ops/tp_exec/cli.py`, `src/dopetask/ops/tp_exec/engine.py`).
- [CODE] Verified `orchestrate` remains a public command and is explicitly labeled `orchestrator v0` (`python -m dopetask orchestrate --help`, `src/dopetask/cli.py`, `src/dopetask/orchestrator/kernel.py`).
- [CODE] `execute` and `tp series import` are drifted surfaces: both are referenced in source or docs, but neither is invokable in the runtime checked here (`src/dopetask/cli.py`, `src/dopetask/ops/tp_series/cli.py`, runtime command checks summarized in the drift matrix).

## Task Packet Contract

- [CODE] The runtime packet parser is `TPParser`, which validates against the packaged `task_packet` schema before constructing a `TaskPacket` dataclass (`src/dopetask/core/tp_parser.py`, `src/dopetask/core/schema.py`, `src/dopetask/schemas/validator.py`, `dopetask_schemas/task_packet.schema.json`).
- [CODE] Required top-level packet fields are `id`, `target`, and `steps`; series metadata and commit metadata are optional in the generic schema but become mandatory when using `tp series` (`dopetask_schemas/task_packet.schema.json`, `src/dopetask/ops/tp_series/logic.py`).
- [CODE] Each step carries `id`, `task`, `validation`, and optional `requirements`, `commands`, `expected_files`, and `context_files` in the generic representation (`dopetask_schemas/task_packet.schema.json`, `src/dopetask/core/schema.py`).
- [CODE] The Gemini compiler preserves only `id`, `task`, `requirements`, `commands`, `expected_files`, and `validation`, and fail-closes if any step lacks validation (`src/dopetask/core/compilers/gemini.py`).
- [CODE] `tp series` imposes stronger structural rules than the base schema: `series` metadata, `commit` metadata, non-empty `commit.allowlist`, valid dependency relationships, and root/parent consistency (`src/dopetask/ops/tp_series/logic.py`).
- [DOCS/PLANS] The numbered packet docs correctly describe the modern JSON packet fields and validation expectations, but they coexist with older or duplicate packet surfaces in router docs, legacy commit-sequence docs, and schema mirrors (`docs/13_TASK_PACKET_FORMAT.md`, `docs/12_ROUTER.md`, `docs/20_WORKTREES_COMMIT_SEQUENCING.md`, `docs/schemas/task_packet.schema.json`).

## Execution Models

### 1. Low-Level JSON Packet Execution (`tp exec`)

- [CODE] `tp exec` parses JSON, compiles the requested profile, and sends the compiled packet through `execute_task_packet()` (`src/dopetask/ops/tp_exec/cli.py`, `src/dopetask/ops/tp_exec/engine.py`).
- [CODE] In the current runtime, only the `gemini` profile is implemented in `execute_task_packet()`; other advertised agent names raise `ValueError` (`src/dopetask/ops/tp_exec/engine.py`).
- [CODE] The current Gemini adapter is shell-command-driven, not provider-session-driven: it compiles prompt text, but `StepRunner.run_step()` executes `commands` and `validation` locally via `subprocess.run(shell=True)` (`src/dopetask_adapters/gemini/executor.py`, `src/dopetask_adapters/gemini/step_runner.py`).
- [CODE] `TaskExecutor` currently validates the adapter return type and raises immediately on failed `ExecutionResult` items; it does not manage full state transitions described in the architecture plan (`src/dopetask/pipeline/task_runner/executor.py`, `src/dopetask/pipeline/task_runner/types.py`).
- [CODE] The low-level proof path is raw proof + trace via `ProofWriter`, then canonical bundle/archive aggregation via `ProofAggregator` (`src/dopetask_adapters/gemini/proof_writer.py`, `src/dopetask/obs/proof_aggregator.py`).

### 2. DAG-Aware Series Execution (`tp series`)

- [CODE] `tp series` adds repo-doctor checks, DAG dependency tracking, isolated worktree branches, allowlist-checked commits, state ledgers, and PR finalization on top of the low-level executor (`src/dopetask/ops/tp_series/logic.py`, `src/dopetask/ops/tp_git/guards.py`).
- [CODE] The series doctor hard-refuses unless the primary repo is on `main`, has no uncommitted changes outside ignored series paths, has no stash entries, and can fast-forward/pull `origin/main` when it exists (`src/dopetask/ops/tp_series/logic.py`, `src/dopetask/ops/tp_git/guards.py`).
- [CODE] The authoritative series ledger is `out/tp_series/<series-id>/SERIES_STATE.json`, with per-packet artifact directories under `out/tp_series/<series-id>/packets/<tp-id>/` and PR metadata in `SERIES_PR.json` after finalize (`src/dopetask/ops/tp_series/logic.py`, `docs/24_UPGRADE_GUIDE.md`).
- [DOCS/PLANS] `README.md`, `docs/22_WORKFLOW_GUIDE.md`, and `docs/24_UPGRADE_GUIDE.md` all treat this as the current default supervisor path.

### 3. Router and Orchestrator Paths

- [CODE] Router v1 is still a live, public subsystem. It loads `.dopetask/runtime/availability.yaml`, scores runner/model candidates for a deterministic set of lifecycle steps, and writes `out/dopetask_route/ROUTE_PLAN.json`, `ROUTE_PLAN.md`, and optionally `HANDOFF.md` (`src/dopetask/router/types.py`, `src/dopetask/router/availability.py`, `src/dopetask/router/planner.py`, `src/dopetask/router/reporting.py`).
- [CODE] Router planning still reads shallow `ROUTER_HINTS` from packet text rather than from the JSON task-packet dataclass (`src/dopetask/router/planner.py`).
- [CODE] The separate `orchestrate` command executes `orchestrator v0`: it reads a packet JSON, builds a route plan, selects a single runner or emits a manual handoff, and writes deterministic run artifacts through `src/dopetask/artifacts/writer.py` (`src/dopetask/orchestrator/kernel.py`, `src/dopetask/artifacts/writer.py`).
- [DOCS/PLANS] This route/orchestrate family is still described as normative in older contract docs (`docs/11_PUBLIC_CONTRACT.md`, `docs/12_ROUTER.md`, `docs/10_ARCHITECTURE.md`), even though current default-flow docs emphasize JSON series execution.

### 4. Legacy Manual Git/Worktree Paths

- [CODE] The repo still ships `wt start`, `commit-sequence`, and `finish` flows, backed by `src/dopetask/git/*`, `src/dopetask/obs/run_artifacts.py`, and `src/dopetask/manifest/*`.
- [DOCS/PLANS] `docs/20_WORKTREES_COMMIT_SEQUENCING.md` explicitly marks this family as legacy/manual and positions JSON series as the preferred new-work path.

## Adapters, Runners, and Model Surfaces

- [CODE] Two execution abstractions coexist. The low-level `tp exec` path uses `src/dopetask_adapters/gemini/*`; the route/orchestrate family uses runner adapters under `src/dopetask/runners/*` (`claude_code`, `codex_cli`, `copilot_cli`, `google_jules`).
- [CODE] Router availability defaults enumerate model names such as `gpt-5.4`, `gpt-5.3-codex`, `sonnet-4.6`, and `haiku-4.5`, plus runner availability for `claude_code`, `codex_desktop`, `copilot_cli`, and `google_jules` (`src/dopetask/router/availability.py`, `src/dopetask/router/types.py`).
- [CODE] The low-level executor does not currently connect those router runner definitions to actual non-Gemini execution in `tp exec`; the surfaces are parallel rather than unified (`src/dopetask/ops/tp_exec/engine.py`, `src/dopetask/router/*`, `src/dopetask/runners/*`).
- [DOCS/PLANS] The architecture and plan docs describe a broader adapter-executor transition that is only partially realized in code (`docs/architecture/dopetask-supervisor-executor-adapter-spec.md`, `docs/plans/dopetask-multi-mode-execution-plan.md`, `docs/plans/dopeTask_higher_level_recovery_plan.md`).

## Artifact, Proof, and Ledger Contracts

- [CODE] Low-level execution proof creation is two-stage: `ProofWriter` writes a raw `*_PROOF.json` plus `*_TRACE.log`, and `ProofAggregator` packages those with referenced files into `*_PROOF_BUNDLE.json` plus `*_PROOF_ARCHIVE.zip` (`src/dopetask_adapters/gemini/proof_writer.py`, `src/dopetask/obs/proof_aggregator.py`).
- [CODE] The checked-in proof standard schema requires `tp_id`, `status`, `packet_family`, `lane`, `summary`, `acceptance_checks`, `validation`, `artifacts`, and `manifest` (`proof/standards/PROOF_BUNDLE_SCHEMA.json`, `tests/unit/obs/test_proof_contract_assets.py`).
- [DOCS/PLANS] `docs/proof/PROOF_BUNDLE_CONTRACT.md` correctly treats the JSON proof bundle as the canonical review object and the archive as secondary drill-down evidence.
- [CODE] Orchestrator runs write a different artifact family: `ROUTE_PLAN.json`, `RUN_REPORT.json` or `REFUSAL_REPORT.json`, optional stdout/stderr logs, and `ARTIFACT_INDEX.json` (`src/dopetask/artifacts/writer.py`).
- [CODE] Series execution adds another authoritative artifact layer: `SERIES_STATE.json`, per-packet packet directories, and copied proof artifacts from packet execution (`src/dopetask/ops/tp_series/logic.py`).
- [CODE] Manifest helpers exist for run-level command/audit logging with deterministic or wallclock timestamp modes and redaction logic, but manifest usage is not uniform across every execution family (`src/dopetask/manifest/manifest.py`).

## Schema and Contract Surfaces

- [CODE] The only runtime schema-loading path inspected here is package-data-based: `src/dopetask/utils/schema_registry.py` discovers schemas from the installed `dopetask_schemas` package, and `src/dopetask/schemas/validator.py` validates against that registry with no current-working-directory fallback.
- [CODE] `dopetask_schemas/` contains the packaged runtime schema copies for task packets, proof-adjacent objects, case bundles, promotion tokens, and series/report artifacts.
- [CODE] `schemas/` is another tracked formal-schema surface used by code, scripts, docs, and tests for non-packaged or broader repo contracts.
- [DOCS/PLANS] `docs/schemas/task_packet.schema.json` is a documentation mirror rather than the runtime registry authority.
- [CODE] Checked-in tests explicitly exercise schema-registry availability and schema loading, reinforcing `dopetask_schemas` as the packet-validation authority (`tests/unit/test_schema_registry.py`, `tests/unit/utils/test_schema_loading_new.py`).

## Project Bootstrap, Prompt Management, and Repo Guards

- [CODE] `ops init/export/preview/apply/doctor` compile and inject operator instruction blocks from `ops/operator_profile.yaml` and template assets under `ops/templates/` (`src/dopetask/ops/cli.py`, `ops/operator_profile.yaml`, `ops/templates/*`).
- [DOCS/PLANS] `docs/26_SUPERVISOR_PROMPTS.md` is the main operator guide for prompt export and installation, and it consistently tells supervisors to stay packet-oriented and delegate through series execution.
- [CODE] `project`-family commands create or update managed instruction files and bundle templates from package assets (`src/dopetask/project/init.py`, `src/dopetask/project/common.py`, `src/dopetask/assets/templates/*`).
- [CODE] Repo identity and run identity rails exist under `src/dopetask/guard/identity.py`; they bind a repo to `.dopetask/project.json`, `RUN_IDENTITY.json`, branch naming, and origin-hint checks.
- [CODE] `.dopetaskroot` is the lightweight repo marker checked into the tree, while `.dopetask` is an empty tracked file in this repo snapshot and should not be confused with the runtime `.dopetask/` directory used by several commands (`.dopetaskroot`, `src/dopetask/router/availability.py`, `src/dopetask/guard/identity.py`).

## Security, Refusal, and Determinism Rules

- [CODE] Packet validation fail-closes before execution through the JSON schema layer (`src/dopetask/core/tp_parser.py`, `src/dopetask/schemas/validator.py`).
- [CODE] Series doctor fail-closes on non-`main` branch state, dirty working trees, non-empty stash lists, and sync failures (`src/dopetask/ops/tp_series/logic.py`, `src/dopetask/ops/tp_git/guards.py`).
- [CODE] Route planning fail-closes by emitting refused plans with structured refusal reasons when availability is missing, invalid, or below threshold (`src/dopetask/router/planner.py`, `src/dopetask/router/availability.py`).
- [CODE] Current step execution uses `subprocess.run(shell=True)` both in the low-level Gemini path and in series verify-command execution (`src/dopetask_adapters/gemini/step_runner.py`, `src/dopetask/ops/tp_series/logic.py`).
- [CODE] Deterministic JSON writing is explicit in several artifact surfaces via stable sort order and canonical dumps, but some artifacts still embed wallclock timestamps (`src/dopetask/artifacts/canonical_json.py`, `src/dopetask/artifacts/writer.py`, `src/dopetask/manifest/manifest.py`, `src/dopetask/obs/proof_aggregator.py`, `src/dopetask/git/worktree.py`).
- [DOCS/PLANS] The repo’s prose consistently values refusal-first, artifact-first, and deterministic behavior, but the exact scope of byte-stability differs across subsystems and should be read per artifact family rather than as one universal runtime guarantee (`README.md`, `docs/10_ARCHITECTURE.md`, `docs/11_PUBLIC_CONTRACT.md`, `docs/14_PROJECT_DOCTOR.md`).

## Deprecated, Transitional, and Multi-Era Surfaces

- [CODE] The runtime still ships legacy/manual worktree commands, route/orchestrate families, low-level `tp exec`, and the newer `tp series` family side by side (`src/dopetask/cli.py`).
- [DOCS/PLANS] `docs/20_WORKTREES_COMMIT_SEQUENCING.md` and `docs/24_UPGRADE_GUIDE.md` explicitly acknowledge that coexistence by calling some surfaces legacy/manual and others the current default.
- [DOCS/PLANS] The architecture, multi-mode, and recovery-plan documents describe ongoing or unfinished transitions around adapters, executor responsibilities, and broader multi-provider support (`docs/architecture/dopetask-supervisor-executor-adapter-spec.md`, `docs/plans/dopetask-multi-mode-execution-plan.md`, `docs/plans/dopeTask_higher_level_recovery_plan.md`).
- [CODE] The current runtime therefore has to be understood as a layered, transitional toolchain rather than a single fully-converged execution kernel.

## Drift Snapshot

- [CODE] High-impact drift verified during generation includes hidden/unavailable commands (`D001`, `D002`), agent-help overstatement (`D003`), and a schema-authority split between docs and package data (`D005`, `D006`).
- [CODE] Medium-impact drift centers on product positioning versus runtime coexistence (`D004`, `D010`, `D011`) and on architecture docs outrunning current executor behavior (`D007`, `D008`, `D013`).
- [DOCS/PLANS] Historical implementation plans remain useful context but are not current capability statements (`D012`).
- [CODE] The complete evidence-backed list is in `docs/specs/dopetask-drift-matrix.md`.

## [INFERRED] Recommendations

- [INFERRED] Publish an explicit authority policy that names `dopetask_schemas` as the runtime packet/schema source, `schemas/` as formal repo-level contracts, and `docs/schemas/` as mirrors or generated views only if kept in lockstep.
- [INFERRED] Resolve command-registration drift before further documentation cleanup: `tp series import`, `execute`, and low-level agent help are currently the highest-value operator confusions.
- [INFERRED] Separate documentation for the three live execution families: `tp series`, `tp exec`, and `route/orchestrate`. The current docs often describe one while the runtime still exposes all three.
- [INFERRED] Document the present `gemini` runtime honestly as a transitional/local shell executor unless and until a real provider session is wired into the execution path.
- [INFERRED] Tighten architecture docs so they describe current executor responsibilities precisely, then layer future-state plans in a separate roadmap document rather than in the current-state spec.

