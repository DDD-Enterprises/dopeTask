# dopeTask Documentation Canon: Architecture + Product Docs

[DOCS/PLANS] Scope: this bundle covers the 38 tracked documentation and plan files selected in the implementation plan for architecture, product, onboarding, integration, prompt, and design-history analysis. It excludes `docs/specs/*`, proof-only docs, schema-only docs, release/audit artifact docs, archive docs, and untracked local guides.

[CODE] Verification basis: documentation claims in this bundle are checked against `pyproject.toml`, `src/dopetask/cli.py`, `src/dopetask/ops/tp_series/cli.py`, `src/dopetask/ops/tp_series/logic.py`, `src/dopetask/ops/tp_exec/engine.py`, `src/dopetask/pipeline/task_runner/executor.py`, `src/dopetask_adapters/gemini/step_runner.py`, `src/dopetask/utils/schema_registry.py`, runtime help output from `python -m dopetask ... --help`, and targeted tests covering schema registry, routing, orchestration, doctor, upgrade, project CLI, PR flow, integration envelope, and TP series CLI behavior.

[INFERRED] Read this document as the documentation-side companion to `docs/specs/dopetask-canonical-spec.md`. The earlier code-first canon remains the runtime/source-of-truth reference; this bundle explains how the documentation set is structured, what it claims, and where it drifts from runtime reality.

## Documentation Planes and Audience Model

[DOCS/PLANS] The top-level docs split into several planes rather than one uniform reference set.

| Plane | Audience | Primary files | Intended role |
| --- | --- | --- | --- |
| Core/operator canon | Current operators and contributors | `docs/00_OVERVIEW.md`, `docs/01_SETUP.md`, `docs/10_ARCHITECTURE.md`, `docs/11_PUBLIC_CONTRACT.md`, `docs/13_TASK_PACKET_FORMAT.md`, `docs/22_WORKFLOW_GUIDE.md`, `docs/23_INTEGRATION_GUIDE.md`, `docs/24_UPGRADE_GUIDE.md`, `docs/26_SUPERVISOR_PROMPTS.md`, `docs/KERNEL_PRINCIPLES.md` | Normative/current documentation path |
| Command and workflow references | Operators and maintainers | `docs/12_ROUTER.md`, `docs/14_PROJECT_DOCTOR.md`, `docs/25_CONSUMER_INSTALL.md`, `docs/PR_FLOW.md`, `docs/REFUSAL_PHILOSOPHY.md`, `docs/integrations/dopetask/ADAPTER_SCHEMA.md` | Command-specific and integration-specific guidance |
| Legacy/manual references | Maintainers doing manual recovery or older flows | `docs/20_WORKTREES_COMMIT_SEQUENCING.md`, `docs/21_CASE_BUNDLES.md`, `docs/TP_GIT_WORKFLOW.md` | Preserved non-default/manual paths |
| Onboarding and product positioning | Beginners and non-specialist users | `docs/beginner/*`, `docs/00_OVERVIEW.md` | Tutorial and narrative framing |
| Prompt and operator assets | Web supervisors and coding agents | `docs/26_SUPERVISOR_PROMPTS.md`, `docs/llm/*` | Prompt generation, application, and fallback source prompt |
| Design history and transitional intent | Maintainers/recovery work | `docs/plans/*`, selected `llm-plans/*`, `docs/architecture/dopetask-supervisor-executor-adapter-spec.md` | Historical implementation intent, not live runtime authority |

[DOCS/PLANS] `docs/00_OVERVIEW.md` explicitly separates current operator docs, supporting reference docs, beginner onboarding, legacy/manual docs, proof-contract docs, and audit artifact docs, so the repo already models documentation as layered rather than flat.

[INFERRED] The documentation set is healthiest when read with an authority stack: core/operator canon first, command references second, beginner/tutorial material third, prompt assets fourth, and plans/history last.

## Architecture Narrative and Kernel Philosophy

[DOCS/PLANS] `docs/10_ARCHITECTURE.md`, `docs/KERNEL_PRINCIPLES.md`, `docs/REFUSAL_PHILOSOPHY.md`, and `docs/00_OVERVIEW.md` present a consistent core story: dopeTask is a deterministic execution kernel; packets are the central declared input; refusal is a first-class integrity boundary; artifacts are the execution record; implicit retries, hidden fallbacks, and undeclared side effects are non-goals.

[DOCS/PLANS] `docs/26_SUPERVISOR_PROMPTS.md` and `docs/llm/SUPERVISOR_SYSTEM_PROMPT.md` extend that architecture into an operator model where supervisors author JSON Task Packets and delegate execution rather than implementing code directly.

[CODE] Runtime supports the broad philosophy but exposes a wider product surface than the simplest architecture narrative suggests. `python -m dopetask --help` shows top-level families including `tp`, `route`, `orchestrate`, `wt`, `commit-sequence`, `finish`, `pr`, `tmux`, `project`, `dopemux`, `bundle`, and `case`, so the live CLI is broader than a single packet-to-runner-to-artifact spine.

[CODE] `pyproject.toml` currently reports `version = "0.5.7"` and `requires-python = ">=3.9"`, which aligns with the setup/install docs on the Python floor and package identity.

[CODE] The strict “packet is the only input surface that matters” wording in `docs/10_ARCHITECTURE.md` does not fully match the live execution rules. `src/dopetask/ops/tp_series/logic.py` and `src/dopetask/ops/tp_git/guards.py` inspect repository cleanliness, branch state, worktree state, stash state, and repo-root identity before execution or PR flows proceed.

[INFERRED] The architecture docs are strongest when read as philosophy and operator doctrine. They are weaker when read as a complete implementation map for worktree, status, and execution responsibility boundaries.

## Public and Operator Workflow Narrative

[DOCS/PLANS] `docs/13_TASK_PACKET_FORMAT.md`, `docs/22_WORKFLOW_GUIDE.md`, and `docs/24_UPGRADE_GUIDE.md` define the current default workflow as JSON Task Packets executed through `dopetask tp series exec`, monitored through `dopetask tp series status`, and finalized through `dopetask tp series finalize`.

[DOCS/PLANS] `docs/01_SETUP.md` and `docs/26_SUPERVISOR_PROMPTS.md` connect that workflow to repo setup and supervisor prompt lifecycle. The intended operator path is: install/configure, generate or apply a supervisor prompt, author JSON packets, execute a series, inspect proof and state, and finalize the series PR.

[CODE] Runtime confirms the major command families those docs depend on: `python -m dopetask tp series --help`, `python -m dopetask route --help`, `python -m dopetask doctor --help`, `python -m dopetask project upgrade --help`, `python -m dopetask ops --help`, `python -m dopetask pr open --help`, and `python -m dopetask tmux --help` all succeed.

[CODE] The documented workflow has a material mismatch around packet import. `src/dopetask/ops/tp_series/cli.py` defines an `import` subcommand, and both `docs/13_TASK_PACKET_FORMAT.md` and `docs/22_WORKFLOW_GUIDE.md` instruct operators to use `dopetask tp series import`, but runtime help omits that command and `python -m dopetask tp series import --help` fails with “No such command 'import'”.

[DOCS/PLANS] `docs/11_PUBLIC_CONTRACT.md` and `docs/12_ROUTER.md` still foreground route plan artifacts and route availability config as the public contract surface, while `docs/22_WORKFLOW_GUIDE.md` and `docs/24_UPGRADE_GUIDE.md` frame TP series state and proof bundles as the present default operator path.

[INFERRED] The workflow docs no longer describe one single public surface. They describe at least three: JSON TP series, route planning/handoff, and legacy/manual git/worktree flows. The docs bundle should therefore preserve those as separate planes rather than implying one has fully replaced the others.

## Onboarding and Product Positioning Narrative

[DOCS/PLANS] `docs/beginner/00_WELCOME.md`, `docs/beginner/00A_HOW_DOPETASK_WORKS.md`, `docs/beginner/01_CONCEPTS.md`, `docs/beginner/02_INSTALLATION.md`, `docs/beginner/03_WEB_LLM_SETUP.md`, and `docs/beginner/04_WORKFLOW.md` package dopeTask as a safety system for AI-assisted development: isolate work in worktrees, force structured packets, validate before merge, and review proof bundles instead of trusting conversational output.

[DOCS/PLANS] The beginner docs deliberately point readers back to top-level docs for canon. `docs/beginner/02_INSTALLATION.md` delegates canonical setup to `docs/01_SETUP.md`, and `docs/beginner/04_WORKFLOW.md` delegates canonical workflow to `docs/22_WORKFLOW_GUIDE.md`.

[DOCS/PLANS] The onboarding narrative also pitches broad agent portability. `docs/beginner/00A_HOW_DOPETASK_WORKS.md` names Codex, Gemini CLI, Claude Code, and Copilot CLI as implementer examples, while `docs/26_SUPERVISOR_PROMPTS.md` covers supervisor prompt application across ChatGPT, Claude, Codex CLI, Gemini CLI, Copilot CLI, Cursor, and Vibe.

[CODE] Runtime execution support is not symmetrical with that product story. `python -m dopetask tp exec --help` advertises `gemini`, `codex`, and `vibe`, but `src/dopetask/ops/tp_exec/engine.py` only constructs a `GeminiAdapter` and raises `ValueError` for other agents. `src/dopetask_adapters/gemini/step_runner.py` executes declared shell commands with `subprocess.run(shell=True)` rather than a provider-native multi-agent orchestration layer.

[INFERRED] The beginner and product docs are most accurate when they promise supervisor portability and process discipline. They overpromise when they imply current parity across implementer agents.

## Integration, Install, Upgrade, and Prompt Surfaces

[DOCS/PLANS] `docs/01_SETUP.md`, `docs/25_CONSUMER_INSTALL.md`, and `docs/DISTRIBUTION_GUIDE.md` cover three different install personas: maintainers working in the source repo, downstream consumer repos installing dopeTask, and release maintainers shipping to PyPI.

[DOCS/PLANS] `docs/23_INTEGRATION_GUIDE.md` and `docs/integrations/dopetask/ADAPTER_SCHEMA.md` define integration-facing surfaces: CI invocation patterns, proof bundle consumption, series state consumption, and a derived Dopemux envelope that explicitly is not the canonical dopeTask artifact.

[DOCS/PLANS] `docs/26_SUPERVISOR_PROMPTS.md`, `docs/llm/SUPERVISOR_SYSTEM_PROMPT.md`, and `docs/llm/DOPETASK_OPERATOR_SYSTEM.md` define the prompt lifecycle: manual fallback prompt in repo, generated/exported prompt artifacts in `ops/`, and repo instruction-file application through `dopetask ops`.

[CODE] Runtime exposes both top-level and project-scoped stabilization commands. `python -m dopetask --help` shows top-level `init` and `upgrade`, while `python -m dopetask project upgrade --help` shows a separate project-mode stabilization flow. The documentation set does not yet present one clearly dominant bootstrap/stabilization boundary between those surfaces.

[CODE] `python -m dopetask ops --help` confirms `init`, `export`, `preview`, `apply`, `manual`, `doctor`, `diff`, and `handoff`. That aligns with the prompt-installation narrative, but the version tables in `docs/26_SUPERVISOR_PROMPTS.md` are time-bound external claims, not facts the repo can verify on its own.

[INFERRED] The install/integration/prompt docs are useful but persona-mixed. A future cleanup should make the boundary between “repo maintainer”, “downstream consumer”, “operator prompt admin”, and “package releaser” explicit in headings and navigation.

## Legacy and Manual Workflow Surfaces

[DOCS/PLANS] `docs/20_WORKTREES_COMMIT_SEQUENCING.md` and `docs/TP_GIT_WORKFLOW.md` preserve the manual/legacy packet paths: markdown packets, explicit worktree lifecycle commands, commit sequencing, `tp git` doctor/start/pr/merge/sync-main/cleanup, and deterministic dirty-state rails.

[DOCS/PLANS] `docs/21_CASE_BUNDLES.md` and `docs/PR_FLOW.md` extend the operational story into auditing and assisted PR creation, including case-bundle vocabulary, supervisor review artifacts, PR refusal rails, restore semantics, and deterministic PR reports.

[CODE] Those surfaces are not just historical prose. `python -m dopetask --help` still exposes `wt`, `commit-sequence`, `finish`, `pr`, `route`, `orchestrate`, and `tp` as first-class runtime commands, so the legacy/manual ecosystem remains active even while the newer docs position JSON TP series as the default path.

[INFERRED] The docs are more accurate when they say “default vs manual/legacy” than when they imply older surfaces are effectively gone.

## Plan and History Surfaces

[DOCS/PLANS] `docs/architecture/dopetask-supervisor-executor-adapter-spec.md`, `docs/plans/dopeTask_higher_level_recovery_plan.md`, `docs/plans/dopetask-multi-mode-execution-plan.md`, and the selected `llm-plans/*` files capture transitional design intent: adapter-executor architecture, parser normalization, proof aggregation, tmux operator UX, recovery discipline, and phased implementation goals.

[CODE] Some of those ideas landed partially. `src/dopetask/pipeline/task_runner/executor.py` exists, proof aggregation exists, `src/dopetask/ops/tp_tmux/cli.py` is live, and the low-level executor path exists. Other planned pieces remain absent or partial: there is no `src/dopetask_adapters/shell/` tree, non-Gemini agents are not yet implemented in the engine, and the current engine still unpacks a transitional `legacy_proof_path` alongside `ExecutionResult` data.

[CODE] `docs/llm/DOPETASK_OPERATOR_SYSTEM.md` is also a point-in-time generated asset rather than a stable narrative doc. Its embedded git commit (`97bc168810bae3b0add5cc6036cb320d582d2f26`) does not match the current repository `HEAD` inspected during this pass.

[INFERRED] These plan/history docs are useful for reconstructing why the repo says different things in different places. They should not be treated as current public contract without explicit rebasing onto runtime truth.

## Cross-Document Contradictions

[DOCS/PLANS] The docs set contains two main contradiction classes: doc-vs-code contradictions and doc-vs-doc contradictions.

| Topic | Documentation stance | Verified reality |
| --- | --- | --- |
| `tp series import` | `docs/13_TASK_PACKET_FORMAT.md` and `docs/22_WORKFLOW_GUIDE.md` instruct operators to import clipboard JSON before execution. | `src/dopetask/ops/tp_series/cli.py` defines `import`, but runtime help omits it and direct invocation fails. |
| Public contract center | `docs/11_PUBLIC_CONTRACT.md` and `docs/12_ROUTER.md` center route artifacts and route availability. | `docs/22_WORKFLOW_GUIDE.md` and `docs/24_UPGRADE_GUIDE.md` center series state and proof bundles; runtime exposes both worlds. |
| Packet-only input law | `docs/10_ARCHITECTURE.md` says the packet is the only input surface that matters unless declared. | Series and git guards inspect repo state, branch, stash, worktrees, and repo identity. |
| TaskExecutor authority | `docs/architecture/dopetask-supervisor-executor-adapter-spec.md` assigns status and worktree authority to `TaskExecutor`. | Current code splits responsibilities between `TaskExecutor`, series logic, proof aggregation, and adapter shims. |
| Multi-agent support | Beginner docs, prompt docs, and several plans imply broad implementer portability. | Engine implementation is still Gemini-only in the live low-level executor path. |
| Bootstrap surface | Setup/install docs mention top-level `init`/`upgrade`; runtime also exposes `project init`/`project upgrade`. | The repo has overlapping bootstrap/stabilization surfaces without one clearly normalized doc boundary. |
| Versioned external recommendations | `docs/26_SUPERVISOR_PROMPTS.md` includes current-model/version tables. | The repo cannot validate those external version claims by itself; they age independently of code. |
| Generated operator prompt asset | `docs/llm/DOPETASK_OPERATOR_SYSTEM.md` reads like a current prompt file. | It is pinned to a historical commit and should be treated as generated point-in-time output. |

## [INFERRED] Consolidation Recommendations

[INFERRED] Establish an explicit documentation authority order in `docs/00_OVERVIEW.md`: core/operator canon, command references, beginner/tutorial docs, prompt assets, then plans/history.

[INFERRED] Either restore runtime exposure for `tp series import` or remove it from all operator-facing docs until the runtime surface matches the prose.

[INFERRED] Reframe product/onboarding copy around “supervisor portability and process discipline” instead of implying equal execution support for every named coding agent.

[INFERRED] Normalize bootstrap language by choosing whether top-level `init`/`upgrade` or `project init`/`project upgrade` is the preferred user path in each persona-specific doc.

[INFERRED] Move time-bound external model/version tables out of canonical operator docs, or stamp them as advisory snapshots that require off-repo verification.

[INFERRED] Mark `docs/architecture/dopetask-supervisor-executor-adapter-spec.md`, `docs/plans/*`, and selected `llm-plans/*` with a visible “historical implementation intent” banner unless and until they are rebased onto current runtime behavior.
