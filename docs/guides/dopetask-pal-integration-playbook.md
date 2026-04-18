# Guide: PAL Integration Playbook for dopeTask

## 1. Overview: Thinking vs. Execution
- **PAL (The Thinking Partner):** Used for architectural analysis, complex planning, and hypothesis testing. PAL operates in a speculative "thinking" space.
- **dopeTask (The Execution Kernel):** Used for applying changes to the codebase with deterministic validation. dopeTask operates in the "doing" space.

## 2. Tool Inventory and Strategic Use
| Tool | Best Use Case | Implementation fit |
| :--- | :--- | :--- |
| `analyze` | Mapping codebase patterns and tech debt. | Research phase for a TP. |
| `planner` | Drafting multi-step implementation strategies. | Authoring a Task Packet (TP). |
| `challenge` | Sanity checking a proposal or a bug fix. | Pre-execution validation. |
| `thinkdeep` | Root cause analysis for complex bugs. | Debugging a failing TP step. |
| `consensus` | Evaluating architectural trade-offs. | High-level system refactoring. |
| `clink` | Injecting external CLI context into a session. | Syncing remote repo states. |

## 3. Integration Workflow: The Supervisor Cycle
1. **Research (PAL):** Use `analyze` or `thinkdeep` to understand the problem.
2. **Plan (PAL):** Use `planner` to draft a Task Packet. Use `challenge` to verify the steps.
3. **Author (dopeTask):** Convert the PAL plan into a JSON Task Packet.
4. **Execute (dopeTask):** Delegate implementation to the `TaskExecutor` via `tp series exec`.
5. **Verify (PAL/dopeTask):** Analyze the proof bundle. If it failed, use `thinkdeep` to diagnose.

## 4. Safe Chaining Patterns
- **Linear Chaining:** `analyze` -> `planner` -> `dopeTask TP Authoring`.
- **Validation Chaining:** `dopeTask Execution Failure` -> `thinkdeep` -> `Correction TP`.

## 5. Anti-Patterns to Avoid
- **Thinking in Execution:** DO NOT use PAL tools inside a dopeTask worktree to modify code directly. Use the Task Packet as the only source of truth.
- **Oversized Prompts:** Keep individual PAL tool prompts focused to avoid context window blowouts or timeouts.
- **Silent Failure:** Always check the `ExecutionResult` before moving to the next PAL thinking step.

## 6. Sizing and Performance
- **Context Management:** Use `clink` sparingly; it can significantly increase token costs.
- **Timeout Safety:** For complex architectural reviews, use `consensus` with no more than 3 models to stay within session time limits.
