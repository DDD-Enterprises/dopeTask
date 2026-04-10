# dopeTask Architecture Canon: Planes, Boundaries, and Invariants

[CODE] Scope: this architecture canon covers **95** in-scope source and documentation files across routing, orchestration, TP series, low-level TP execution, manual git/worktree flows, project rails, artifact/proof surfaces, schema loading, and adapter/integration boundaries.

[CODE] Authority order for this bundle is: runtime code and runtime help, typed/schema contracts, artifact writers and guards, then architecture/operator docs, then plans and historical design notes. When prose conflicts with code-backed behavior, the code-backed behavior is treated as current architecture truth.

[DOCS/PLANS] Documentation inputs include `docs/10_ARCHITECTURE.md`, `docs/KERNEL_PRINCIPLES.md`, `docs/11_PUBLIC_CONTRACT.md`, `docs/12_ROUTER.md`, `docs/22_WORKFLOW_GUIDE.md`, `docs/23_INTEGRATION_GUIDE.md`, `docs/24_UPGRADE_GUIDE.md`, `docs/26_SUPERVISOR_PROMPTS.md`, the transitional architecture spec under `docs/architecture/`, and the selected implementation/recovery plans under `docs/plans/` and `llm-plans/`.

[CODE] Verification inputs include `pyproject.toml`, `src/dopetask/core/schema.py`, `src/dopetask/core/tp_parser.py`, `src/dopetask/utils/schema_registry.py`, `src/dopetask/router/*`, `src/dopetask/orchestrator/*`, `src/dopetask/ops/tp_series/*`, `src/dopetask/ops/tp_exec/*`, `src/dopetask/ops/tp_git/*`, `src/dopetask/project/*`, `src/dopetask/artifacts/*`, `src/dopetask/manifest/*`, `src/dopetask/obs/*`, `src/dopetask/runners/*`, `src/dopetask_adapters/*`, and verified CLI help output from `python -m dopetask ... --help` surfaces.

## Authority Model and Architecture Scope

[CODE] dopeTask does not currently have one single execution architecture. It has several active planes that coexist: router v1, orchestrator v0, JSON TP series execution, low-level `tp exec`, legacy/manual git/worktree flows, project/install rails, and a derived integration layer for Dopemux.

[DOCS/PLANS] The terse kernel docs describe a narrow deterministic kernel with refusal and artifact-first behavior. The broader architecture and plan docs describe a transition toward a supervisor/executor/adapter architecture with `ExecutionResult`, tmux support, and proof aggregation. Both are useful, but they describe different levels of maturity.

[CODE] For this bundle, “architecture” means the actual ownership boundaries between those active planes, the canonical writers/readers of their shared artifacts, and the invariants the code currently enforces.

## System Planes

[CODE] **Supervisor/prompt plane.** `docs/26_SUPERVISOR_PROMPTS.md`, `docs/llm/SUPERVISOR_SYSTEM_PROMPT.md`, and `src/dopetask/project/*` define repo instruction surfaces and generated prompt/config blocks that shape how supervisors author work. These surfaces constrain task intent and project rails, but they do not execute packets directly.

[CODE] **Contract/schema plane.** `src/dopetask/core/schema.py`, `src/dopetask/core/tp_parser.py`, `src/dopetask/schemas/validator.py`, and `src/dopetask/utils/schema_registry.py` form the canonical Task Packet contract path. `TaskPacket`, `TPStep`, `TPSeries`, and `TPCommit` are the in-memory contract; `validate_data(..., "task_packet")` loads schemas through the package-data registry from `dopetask_schemas`, not from `docs/schemas`.

[CODE] **Routing plane.** `src/dopetask/router/availability.py`, `src/dopetask/router/scoring.py`, `src/dopetask/router/planner.py`, `src/dopetask/router/types.py`, `src/dopetask/router/reporting.py`, and `src/dopetask/router/handoff.py` define deterministic route planning. This plane owns availability loading from `.dopetask/runtime/availability.yaml`, deterministic candidate scoring, refusal reasons, route plan serialization, and standalone routing/handoff artifacts under `out/dopetask_route/`.

[CODE] **Orchestration plane.** `src/dopetask/orchestrator/kernel.py` consumes JSON packets, builds route plans, resolves one runnable step, dispatches through `RUNNER_ADAPTERS`, and writes run-local artifacts through `src/dopetask/artifacts/writer.py`. This plane is separate from TP series and does not own git worktree lifecycle.

[CODE] **Series execution plane.** `src/dopetask/ops/tp_series/logic.py` and `src/dopetask/ops/tp_series/cli.py` own the JSON TP DAG model: import/exec/status/finalize semantics, `SERIES_STATE.json`, `SERIES_PR.json`, per-packet directories, readiness/dependency checks, worktree creation and removal, allowlist commit flow, and one final PR per completed series.

[CODE] **Low-level execution plane.** `src/dopetask/ops/tp_exec/cli.py`, `src/dopetask/ops/tp_exec/engine.py`, `src/dopetask/pipeline/task_runner/executor.py`, `src/dopetask/pipeline/task_runner/types.py`, and `src/dopetask_adapters/gemini/*` define the lower-level packet execution path. This plane parses a Task Packet, compiles it to an agent profile, executes it through an adapter, validates adapter output type/failed-step status, and then aggregates a canonical proof bundle.

[CODE] **Legacy/manual git plane.** `src/dopetask/ops/tp_git/*`, plus the top-level `wt`, `commit-sequence`, and `finish` command families documented in `docs/20_WORKTREES_COMMIT_SEQUENCING.md` and `docs/TP_GIT_WORKFLOW.md`, form a separate manual execution control plane built around clean-main, no-stash, deterministic worktrees, and explicit merge/cleanup commands.

[CODE] **Artifact/evidence plane.** `src/dopetask/artifacts/*`, `src/dopetask/manifest/*`, `src/dopetask/obs/*`, and `src/dopetask/obs/run_artifacts.py` own canonical JSON output, route/run artifact indexes, manifests, command logs, and proof bundles/archives. This plane is where auditability becomes machine-readable.

[CODE] **Project/install plane.** `src/dopetask/doctor.py` and `src/dopetask/project/*` form the installation/project readiness plane. These modules own installation integrity checks, project instruction pack generation/fix-up, mode toggling, shell init, and deterministic project upgrade reports.

[CODE] **Integration/derived plane.** `src/dopetask_adapters/dopemux.py`, `src/dopetask_adapters/base.py`, `src/dopetask_adapters/types.py`, and `docs/integrations/dopetask/ADAPTER_SCHEMA.md` define consumer-side integration boundaries. This plane detects or maps external project layouts and derives normalized envelopes from canonical dopeTask artifacts, but it does not replace those canonical artifacts.

## Boundaries and Ownership

[CODE] **Supervisor vs kernel.** Supervisor/prompt surfaces decide task intent and author packet structure. Kernel/runtime surfaces enforce parsing, routing, guards, execution, and artifact writing. The prompt plane is upstream policy and authoring context, not the runtime authority for execution state.

[CODE] **Router vs execution.** The routing plane selects deterministic runner/model pairs and refusal reasons; it does not execute work. Execution begins only in `orchestrator/kernel.py`, `ops/tp_exec/engine.py`, or `ops/tp_series/logic.py`, each of which consumes route or packet state differently.

[CODE] **Series logic vs low-level executor.** `ops/tp_series/logic.py` owns DAG readiness, `depends_on` enforcement, series state, worktree lifecycle, allowlist commit flow, and finalization. `ops/tp_exec/engine.py` owns the low-level parse/compile/adapter/proof aggregation path. Series execution delegates into the low-level executor but does not collapse into it.

[CODE] **Executor vs adapter.** `pipeline/task_runner/executor.py` currently validates that adapter output is a list of `ExecutionResult` objects and fails fast on a step marked `failed`. It does not own full packet lifecycle, worktree state, or status transitions beyond that narrow validation role. `src/dopetask_adapters/gemini/executor.py` still performs the actual step loop, raw result mapping, and legacy raw proof emission.

[CODE] **Canonical artifacts vs derived artifacts.** Route plans, run reports, manifests, proof bundles, archives, and series ledgers are canonical dopeTask outputs. The Dopemux adapter envelope documented in `docs/integrations/dopetask/ADAPTER_SCHEMA.md` is explicitly derived from those artifacts and is not itself the authoritative execution record.

[CODE] **Package schema surface vs repo copies.** Runtime validation loads schemas via `SchemaRegistry` from package data in `dopetask_schemas`. Repo-local schema copies and docs references are secondary documentation or packaging aids unless code explicitly points to them.

## Canonical Writers and Readers

[CODE] The architecture currently has several distinct canonical writers rather than one global artifact writer.

| Contract or artifact | Canonical writer | Primary readers | Notes |
| --- | --- | --- | --- |
| `TaskPacket` dataclass shape | `src/dopetask/core/schema.py` | parser, normalizer, series logic, docs | In-memory contract for JSON TP execution |
| JSON schema for task packet validation | package data via `src/dopetask/utils/schema_registry.py` and `src/dopetask/schemas/validator.py` | parser, doctor, packaging checks | Runtime registry is package-data-only |
| `out/dopetask_route/ROUTE_PLAN.json/.md` and `HANDOFF.md` | `src/dopetask/router/reporting.py` | routing CLI, operators | Standalone routing plane artifacts |
| `out/runs/.../ROUTE_PLAN.json`, `RUN_REPORT.json` or `REFUSAL_REPORT.json`, `ARTIFACT_INDEX.json` | `src/dopetask/artifacts/writer.py` | orchestrator callers and operators | Orchestrator v0 run-local artifacts |
| `TASK_PACKET_MANIFEST.json` and command logs | `src/dopetask/manifest/manifest.py` | stateful run/audit flows | Manifest plane is separate from proof bundle aggregation |
| `proof/<TP_ID>_PROOF.json` and `TRACE.log` | `src/dopetask_adapters/gemini/proof_writer.py` | low-level exec engine transitional flow | Raw/transitional Gemini proof, not the final canonical bundle |
| `proof/<TP_ID>_PROOF_BUNDLE.json` and `_PROOF_ARCHIVE.zip` | `src/dopetask/obs/proof_aggregator.py` | integrations, proof review, series flow | Canonical proof bundle layer |
| `out/tp_series/<series>/SERIES_STATE.json` and `SERIES_PR.json` | `src/dopetask/ops/tp_series/logic.py` | `tp series status`, `tp series finalize`, integrations | Authoritative series ledger |
| Dopemux normalized envelope | integration-side build process documented in `docs/integrations/dopetask/ADAPTER_SCHEMA.md` | Dopemux consumers | Derived object built from canonical artifacts |

## Invariant Catalog

[CODE] **Determinism invariants.** Routing sorts models and runners before scoring, computes fixed integer totals, and rounds confidence deterministically. Artifact writers emit canonical JSON with sorted keys or stable field ordering. Route-plan writers use fixed filenames. Run and manifest helpers provide deterministic timestamp modes and stable run-id conventions when deterministic mode is selected.

[CODE] **Fail-closed invariants.** Manual and series git paths enforce clean-main and no-stash rules through `ops/tp_git/guards.py` and `_run_series_doctor(...)`. Packet parsing refuses malformed JSON or schema-invalid task packets. Router refusal returns structured refusal reasons instead of silent fallback. `TaskExecutor` rejects non-`ExecutionResult` adapter output and aborts on a failed step instead of continuing.

[CODE] **Isolation invariants.** Series and manual git flows isolate work in dedicated worktrees and refuse dirty reuse or cleanup when the worktree is dirty. Series execution creates one committed unit per packet. Cleanup paths prune worktrees deliberately instead of mutating main state implicitly.

[CODE] **Contract invariants.** `ExecutionResult` currently requires `step_id`, `status`, `execution_mode`, `raw_output`, `normalized_output`, `metrics`, and optional `error`. Route plans always contain policy, steps, refusal reasons, and deterministic score components. Manifest helpers keep command indices ordered and redact sensitive values. Derived integration envelopes are documented as non-canonical.

[CODE] **Lifecycle invariants.** The active runtime surfaces all preserve “one invocation, one path” semantics in their own way: router plans without execution, orchestrator selects one runnable step or manual handoff, low-level `tp exec` stops at first failed step, series flow creates one worktree/commit per packet and one final PR per series, and manual git flows require explicit phase progression without silent stash-pop or fallback behavior.

## Active Execution Paths and Coexistence Model

[CODE] `route` and `orchestrate` remain active architecture, not dead history. `python -m dopetask route --help` and `python -m dopetask orchestrate --help` both expose live surfaces, and `orchestrator/kernel.py` still routes through `RUNNER_ADAPTERS` defined in `src/dopetask/runners/__init__.py`.

[CODE] JSON TP series is the active default operator model. `python -m dopetask tp series --help` exposes `exec`, `status`, and `finalize`, and the surrounding docs position this as the default path for new supervised work. This plane is more operationally complete than the low-level executor because it owns DAG state, worktrees, and PR lifecycle.

[CODE] Low-level `tp exec` is a distinct execution plane, not just a thin alias for series execution. It compiles a packet into a profile-specific shape, can dry-run or spawn tmux, and writes proof output through the low-level engine. It is currently narrower and more transitional than the series plane.

[CODE] Legacy/manual git and worktree flows remain part of the architecture. `python -m dopetask tp git --help` exposes manual git subcommands, and the top-level CLI still exposes `wt`, `commit-sequence`, and `finish`. These paths matter because they preserve a separate manual control model rather than being fully subsumed by JSON TP series.

[CODE] Project/doctor/install rails also remain active architecture. `python -m dopetask doctor --help` and `python -m dopetask project upgrade --help` show that installation integrity and project instruction-pack stabilization are first-class subsystems, not just setup notes.

## Artifact, Manifest, Proof, and Derived-Envelope Boundaries

[CODE] The repo has more than one artifact family, and each family has a different owner and trust level. Route artifacts describe decisions. Orchestrator run artifacts describe one routed run. Manifests describe command execution and replay/audit state for stateful run directories. Proof bundles describe packet execution evidence. Series ledgers describe packet DAG/PR state. Dopemux envelopes describe integration-side normalization over those canonical sources.

[CODE] Raw Gemini proof output (`<TP_ID>_PROOF.json` plus `TRACE.log`) is not the final architecture endpoint. The low-level engine reads that raw proof path and then aggregates a canonical proof bundle/zip through `ProofAggregator`. Any architecture write-up that treats the raw Gemini proof as the canonical final proof surface is overstating the transition that has already happened.

[CODE] The manifest plane is also separate from proof aggregation. `src/dopetask/manifest/manifest.py` manages `TASK_PACKET_MANIFEST.json`, command log capture, artifact expected/found tracking, and redaction. `src/dopetask/obs/proof_aggregator.py` manages proof bundles and archives. They are complementary audit surfaces, not one file family.

## Schema, Config, Prompt, and Project Rails

[CODE] Schema loading is package-data-based and fail-closed. `SchemaRegistry` enumerates available `.schema.json` files from the installed `dopetask_schemas` package, and `validate_data` uses that registry directly. This means runtime schema truth is independent of current working directory and independent of repo-local docs copies.

[CODE] Router config is repo-local and explicit. `availability_path_for_repo(repo_root)` resolves to `.dopetask/runtime/availability.yaml`, `route init` writes the deterministic template, and router loading refuses missing or malformed config instead of guessing availability.

[CODE] Prompt/project rails are repo-managed but architecture-external to execution state. Project doctor/init/mode/upgrade operate on instruction files, generated reports, shell setup, and identity rails such as `.dopetaskroot` and `.dopetask/project.json`. They shape the operator environment and repo discipline, but they do not replace packet parsing or runtime artifact authority.

## Transitional Seams and Architectural Drift

[DOCS/PLANS] The terse kernel docs describe a single spine of packet -> validation -> planning -> route plan/refusal -> runner/handoff -> artifacts. That captures the ethos, but it collapses several active subsystems that now exist in parallel.

[CODE] The most important runtime seam is the adapter/executor transition. `TaskExecutor` currently validates `ExecutionResult` output and stops on failed status, but the Gemini adapter still executes commands, maps raw results, writes the raw proof file, and exposes a transitional `legacy_proof_path`. The low-level engine then aggregates the canonical proof bundle from that raw proof. The architecture is therefore partly kernel-normalized and partly adapter-owned.

[CODE] A second seam is the coexistence of route/orchestrate and series execution. Route/orchestrate remains live and runner-based. Series execution is JSON TP and worktree/commit/PR based. Both are valid current architecture, but they are not the same path.

[CODE] A third seam is runtime exposure mismatch. `src/dopetask/ops/tp_series/cli.py` defines an `import` subcommand, and `src/dopetask/cli.py` defines a top-level `execute` command, but runtime help currently does not expose those surfaces. `python -m dopetask tp series import --help` and `python -m dopetask execute --help` both fail, so any architecture prose that treats them as live operator entrypoints is ahead of runtime reality.

[CODE] A fourth seam is low-level agent support. `python -m dopetask tp exec --help` advertises `gemini`, `codex`, and `vibe`, and the parser/normalizer includes compilers for those profiles, but `ops/tp_exec/engine.py` only constructs `GeminiAdapter` and raises for other agents. The low-level execution plane is therefore multi-profile in compilation but Gemini-only in actual runtime execution.

[CODE] A fifth seam is docs/schema duplication. Some docs still refer to repo-local schema copies such as `docs/schemas/task_packet.schema.json`, while runtime validation uses the package-data registry. This is a documentation and packaging boundary, not a runtime fallback ladder.

## [INFERRED] Cleanup and Consolidation Recommendations

[INFERRED] Keep the architecture docs split between philosophy and current-state mapping, but mark them differently. `docs/10_ARCHITECTURE.md` should remain a doctrine document; current-state operational ownership belongs in an architecture map like this bundle or a future rewritten canonical architecture doc.

[INFERRED] Normalize runtime exposure before tightening prose: either wire up `tp series import` and `execute` in runtime help, or remove them from architecture/operator flows until they are actually surfaced.

[INFERRED] Reframe low-level `tp exec` as “Gemini runtime path with multi-profile compilation scaffolding” until non-Gemini execution exists. That wording matches the current architecture more closely than “plug-and-play multi-provider executor.”

[INFERRED] Preserve route/orchestrate, series, and manual git/worktree flows as distinct architecture planes in future docs. Collapsing them into one story loses real boundary information and creates drift.

[INFERRED] Make package-data schema loading explicit wherever public docs name schema files. That reduces the recurring ambiguity between `dopetask_schemas`, `schemas/`, and `docs/schemas/`.
