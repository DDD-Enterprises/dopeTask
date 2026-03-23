# TP-CORE-002: TP Parser & Normalizer

## Objective
Create the Task Packet (TP) Parser and Normalization layer to ingest generic TPs and compile them down into distinct agent execution profiles: Gemini (STRICT_EXECUTOR), Codex (SMART_IMPLEMENTER), and Vibe (MICRO_TASK). Enforce strict validation and failure rails during parsing to prevent agent drift.

## Background & Motivation
Different LLMs require drastically different execution constraints, as evidenced during the implementation of TP-CORE-001. Gemini CLI functions best with rigid, single-step execution rails. Codex handles multi-file implementation. Vibe needs hyper-constrained micro-tasks. The parser must normalize a generic YAML/JSON TP into the specific prompt sequences and constraints optimized for each agent's execution model.

## Scope & Impact
This layer is the bridge between the generic task definition and the agent-specific execution adapters (like the Gemini adapter built in TP-CORE-001).
- Creates `src/dopetask/core/tp_parser.py` (or similar core location).
- Creates `src/dopetask/core/compilers/` (Gemini, Codex, Vibe).
- Directly feeds into the TP-CORE-001 Gemini adapter by generating the exact schema (`StepResult` expectations, expected files) and sequence it requires.

## Proposed Solution

### 1. Base TP Schema Definition (`schema.py`)
Define the generic data model for a Task Packet using Pydantic or dataclasses:
- Metadata (ID, Title, Target)
- List of Steps, where each step has:
  - Required Inputs (Context files)
  - Actions (Description of work)
  - Expected Outputs (Files to create/modify)
  - Validation Rules (Commands to verify success)

### 2. Parser & Normalizer Engine
The core engine that ingests the raw TP format (JSON/YAML):
- Validates that the generic TP contains all necessary fields against the Base Schema.
- Crucially, it **Fails the compilation (Fail-Closed)** if a step lacks explicit validation commands. This is a hard requirement for Gemini safety to prevent hallucinated success.

### 3. Profile Compilers

#### A. GeminiCompiler (STRICT_EXECUTOR)
Compiles the TP into a strict, multi-turn sequence tailored for `adapters/gemini/executor.py` (from TP-CORE-001).
- Formats the generic TP steps into the sequence expected by the `GeminiExecutor`.
- Ensures that every step mapped to Gemini has explicit, non-empty validation commands. If not, the compiler aborts.

#### B. CodexCompiler (SMART_IMPLEMENTER)
Compiles the TP into a larger context block for Codex.
- Groups all expected files and demands full file coverage at once.
- Strictly forbids TODOs or skipped logic by injecting constraints into the normalized output.

#### C. VibeCompiler (MICRO_TASK)
Slices the TP into tiny, isolated prompts per method/class.
- Forbids generalization or extra file creation.

## Implementation Steps
1. Create `schema.py` in the parser module defining the Base TP structure.
2. Implement the `TPParser` class to ingest JSON/YAML and validate it against the Base Schema.
3. Implement the `BaseCompiler` abstract class interface.
4. Implement `GeminiCompiler` focusing on generating the strict step structure required by TP-CORE-001, verifying that validation rules are present.
5. Implement `CodexCompiler` and `VibeCompiler` with their respective grouping/slicing strategies.
6. Implement a `TPNormalizer` factory to route a parsed TP through the appropriate compiler based on the requested agent profile.

## Verification & Testing
- **Validation Failure Test:** Feed a TP without validation commands to the parser; it MUST fail compilation for the Gemini profile.
- **Gemini Compilation Test:** Ensure `GeminiCompiler` produces an object that seamlessly integrates with TP-CORE-001's expected inputs (system frame constraints, step-by-step validation).
- **Codex Compilation Test:** Ensure `CodexCompiler` groups files correctly and injects full coverage constraints.
- **Vibe Compilation Test:** Ensure `VibeCompiler` slices the task into distinct micro-tasks.

## Migration & Rollback
Additive changes to core execution logic. Does not impact existing file structure outside of the new parser module. Rollback by removing the parser module.