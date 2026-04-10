# Doc Repair Rules

## Core framing rules

1. Describe **`tp series`** as the **default operator workflow**.
2. Describe **route/orchestrate** as an **active but non-default plane**.
3. Do **not** describe orchestrator v0 auto mode as currently operational in this checkout.
4. Treat orchestrator v0 as a **deterministic reference/manual-handoff-oriented surface** unless stronger evidence overturns that.
5. Preserve the fact that the repo has **multiple active execution planes**, not one single universal execution story. 

## Boundary rules

6. Do not conflate:
   - router artifacts
   - orchestrator run artifacts
   - proof bundles
   - TP series state/ledger artifacts
7. Do not conflate:
   - orchestrator v0
   - router
   - low-level `tp exec`
   - `tp series`
   - legacy/manual git-worktree flows
8. Public contract language must distinguish between:
   - **active public surfaces**
   - **default operator path**
   - **legacy/manual paths**

## Runtime-truth rules

9. When docs describe operational prerequisites, state them explicitly.
10. Missing `.dopetask/runtime/availability.yaml` must be described as a **hard operational prerequisite failure** for orchestrator v0 auto mode in the current checkout, because availability loading has no fallback in the audited runtime path.  [oai_citation:0‡ WORKING_NOTES:orchestrator-live-runtime-check.md](sediment://file_00000000c03c722f95554dd616ee87cb)
11. Do not imply Codex is a viable orchestrator v0 execution runner in current repo state; keep Codex framed as analysis-only unless runtime support changes.  [oai_citation:1‡ WORKING_NOTES:orchestrator-live-runtime-check.md](sediment://file_00000000c03c722f95554dd616ee87cb)
12. Do not generalize current checkout limitations into universal product truth unless supported by higher-authority docs/code.

## Editing rules

13. Prefer **framing corrections** over broad rewrites.
14. Preserve useful architecture concepts even when correcting default-workflow framing.
15. When a doc centers a non-default surface, label it clearly rather than deleting or demoting the surface into false legacy status.
16. Fix contradictions in this order:
   - default-workflow misstatements
   - public-contract ambiguity
   - active-plane boundary blur
   - minor consistency cleanup

## Style rules for repaired docs

17. Use explicit labels such as:
   - default
   - active non-default
   - specialist
   - legacy/manual
18. Make mode boundaries obvious in the opening section of each repaired doc.
19. Avoid universal wording like “the kernel does X” when the behavior actually belongs to only one plane.
20. Where helpful, add one short “This doc covers...” boundary note near the top.

## Current repair targets

1. `docs/10_ARCHITECTURE.md`
2. `docs/11_PUBLIC_CONTRACT.md`
3. `docs/12_ROUTER.md`
4. `docs/23_INTEGRATION_GUIDE.md`
5. `docs/22_WORKFLOW_GUIDE.md` for consistency cleanup only
