# Architecture

Audience: Contributors, Maintainers
Status: Normative
Tone: Deterministic. Unapologetic.

This doc covers architecture planes across dopeTask as a whole.
It does not by itself define the default day-to-day operator workflow.
`tp series` is the default operator workflow; route/orchestrate remains an active but non-default architecture plane.

---

## 1. What dopeTask Is

dopeTask is a deterministic execution kernel.

It takes a structured packet and makes a decision.

That decision is binary:

- Plan and execute one path.
- Refuse with evidence.

There is no third state.
There is no "maybe."
There is no hidden recovery mode.

dopeTask does not guess.
dopeTask does not retry behind your back.
dopeTask does not perform invisible magic.

If it did not write an artifact, it did not happen.

---

## 2. Architecture Planes (Multi-Plane Runtime) 

dopeTask has multiple active execution planes.

dopeTask supports four distinct execution planes:

1. **Default Operator Plane (Series):** DAG-aware, worktree-isolated automation using `tp series`. This is the primary path for development.
2. **Reference Architecture Plane (Orchestrate):** Normative v0 implementation of route planning and refusal-with-evidence. Scoped as a reference implementation.
3. **Specialist/Low-Level Plane (Direct Exec):** Bypasses series logic to execute single packets via `tp exec`. Supports Gemini (transitional) and Codex (implementer).
4. **Legacy/Manual Plane:** Command-line tools for manual worktree and commit management (`commit-sequence`, `finish`).

The route/orchestrate plane remains active as a deterministic architecture surface.
It plans one path, refuses with evidence, and supports runner-or-handoff outcomes.
That plane is real, but it is not the only current execution story.

All mutating planes now perform repo identity preflight before worktree creation, commit staging, or PR mutation. Packets that declare `repo_binding.require_identity_match = true` must only run in the repo whose canonical identity matches the binding.

No side doors.
No background threads.
No secret tunnels.

Every active plane must still terminate in written evidence.

---

## 3. The Packet Is Law

The packet is the only input surface that matters.

It defines:

- What is being attempted
- In what mode
- In what order
- Under what policy

dopeTask does not read intent from:
- Environment variables (unless declared)
- Git state (unless declared)
- Prior runs
- "Common sense"

If the packet does not say it, dopeTask does not assume it.

Precision is power.

---

## 4. Validation: Fail Fast, Fail Clean

Validation is not polite.
Validation is protective.

If the packet is malformed or incomplete:

- Execution stops immediately.
- A structured refusal artifact is written.
- A stable exit code is returned.

No silent downgrades.
No partial execution.
No "best effort."

Refusal is controlled discipline, not failure.

---

## 5. Planning: One Path Only

The planner preserves order.
The planner selects exactly one runner.
The planner produces a deterministic route plan.

The planner does not execute code.
The planner does not improvise.

Given identical inputs, it must produce identical output.

If it does not, that is a defect.

---

## 6. Refusal Is a First-Class Outcome

Refusal is not embarrassment.
Refusal is integrity.

Refusal happens when:

- Policy is violated.
- A runner is unavailable.
- Required inputs are missing.
- Environment integrity fails.
- The packet asks for something unsafe.

Refusal produces:

- Deterministic reasoning.
- A structured artifact.
- A stable exit code.
- Zero side effects.

dopeTask would rather refuse than lie.

---

## 7. The Runner Model

In `auto` mode:

- Exactly one runner executes.
- No parallelism.
- No fallback runner.
- No implicit retry.
- No cascading attempts.

In `manual` mode:

- No runner executes.
- Structured handoff content is emitted.
- Artifacts are still written.

One invocation.
One path.
One outcome.

---

## 8. Artifact Law

Artifacts are the truth.

Console output is theater.
Artifacts are reality.

Every run must:

- Canonicalize output.
- Hash deterministically.
- Write before exit.
- Preserve structure.

Artifacts are not logs.
Artifacts are evidence.

If artifacts are incomplete or inconsistent, the run is invalid.

---

## 9. Determinism Is Non-Negotiable

For identical:

- Packet
- Declared inputs
- dopeTask version

Outputs must be byte-stable.

Allowed variability must be:

- Explicit.
- Documented.
- Recorded.

Implicit nondeterminism is a kernel violation.

Convenience never outranks determinism.

---

## 10. Boundaries: What dopeTask Refuses to Be

dopeTask does not:

- Schedule recurring jobs.
- Persist cross-run memory.
- Coordinate multiple packets.
- Orchestrate distributed state.
- Retry operations automatically.
- Perform undeclared network calls.
- Execute multiple runners.
- Mutate repositories implicitly.

Those are ecosystem concerns.

dopeTask stays small.
Small stays sharp.

---

## 11. Kernel vs Ecosystem

dopeTask is a deterministic kernel with multiple active surfaces.

Higher systems may:

- Generate packets.
- Maintain memory.
- Schedule execution.
- Aggregate results.
- Provide UX.
- Add orchestration.

dopeTask remains:

- Stateless between runs.
- Deterministic per invocation.
- Artifact-driven.
- Refusal-first.
- Single-path within a chosen plane.

If a feature requires ambiguity, it does not belong here.

---

## 12. Stability Model

dopeTask follows Semantic Versioning.

- Patch: bug fixes only.
- Minor: additive, backward-compatible.
- Major: contract-breaking.

The public contract lives in:

`11_PUBLIC_CONTRACT.md`

If determinism changes, the version changes.

No silent contract drift.

---

## Final Principle

dopeTask is not designed to be helpful.

It is designed to be correct.

And correctness is hotter than convenience.
