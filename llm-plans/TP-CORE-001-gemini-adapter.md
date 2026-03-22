# TP-CORE-001: Gemini CLI Execution Adapter (V2)

## Objective
Create a deterministic execution wrapper (adapter layer) for the Gemini CLI so it can execute Task Packets (TPs) rigidly, without drifting, and produce structured, audit-safe proof bundles. Furthermore, this adapter must codify the multi-turn prompt systems for Gemini (STRICT_EXECUTOR), Codex (SMART_IMPLEMENTER), and Mistral Vibe (MICRO_TASK) to ensure the LLM receives the exact, constrained instructions it needs to succeed.

## Key Files & Context
Files to be created/updated in `src/dopetask_adapters/gemini/`:
- `schema.py`: Execution state schema (`StepResult`, `TPProofBundle`).
- `step_runner.py`: Atomic step execution engine (now updated to use explicit prompts).
- `proof_writer.py`: Generates the final audit proof bundle.
- `validator.py`: Fail-closed enforcer.
- `executor.py`: Orchestrator that combines these parts.
- `prompts.py` (NEW): Contains the multi-turn execution prompt templates for TP-CORE-001-A (Gemini), TP-CORE-001-B (Codex), and TP-CORE-001-C (Vibe).

## Implementation Steps

### 1. Define Execution Schema (`schema.py`)
- Implement `StepResult` class tracking `step_id`, `files_created`, `commands_run`, `validation_passed`, and `errors`.
- Implement `TPProofBundle` class tracking `tp_id` and a list of `StepResult`.

### 2. Multi-Turn Execution Prompts (`prompts.py`)
Implement the string templates for the three execution models:
- **Gemini (STRICT_EXECUTOR):**
  - TURN 1: System Frame (strict rules, fail conditions, mandatory JSON output format).
  - TURN 2: Context Load (project, target, invariant requirements).
  - TURN 3+: Step definition (requirements, validation, atomic execution).
- **Codex (SMART_IMPLEMENTER):**
  - TURN 1: System (implementation agent, full file coverage, no TODOs).
  - TURN 2: Task (files to implement, execution constraints, post-implementation proof requirements).
- **Mistral Vibe (MICRO_TASK):**
  - TURN 1: System (micro-task, do not generalize).
  - TURN 2+: Specific class/method creation (only code output).

### 3. Update Step Runner (`step_runner.py`)
- Instead of just stubbing `# subprocess execution here`, the runner must compile the relevant prompt sequence from `prompts.py` based on the step data, execute the CLI/agent tool (or output the prompt script for the agent to ingest), and strictly validate the JSON response.
- If the response is not valid JSON or if `validation` is false, it logs errors and halts.

### 4. Implement Proof Writer (`proof_writer.py`)
- Write `ProofWriter` to output `proof/{tp_id}_PROOF.json`.

### 5. Implement Validator (`validator.py`)
- `Validator.validate(step_result)` must raise exceptions if `validation_passed` is false or if `errors` exist (fail-closed constraint).

### 6. Implement Executor (`executor.py`)
- `GeminiExecutor.run_tp(tp, mode="gemini")` iterates over steps, selects the correct prompt sequence based on mode, runs the step, validates it, and writes the final proof bundle.

## Verification & Testing
- Ensure the prompt templates in `prompts.py` exactly match the provided `TP-CORE-001-A`, `TP-CORE-001-B`, and `TP-CORE-001-C` specifications.
- Ensure the `step_runner.py` is capable of injecting step data into these templates.
- Ensure the fail-closed validator stops execution immediately on prompt or validation failure.

## Migration & Rollback
Additive changes. Rollback involves reverting or removing the `src/dopetask_adapters/gemini/` directory. No existing components will be modified.