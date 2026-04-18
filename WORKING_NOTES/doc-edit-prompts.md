# Doc Edit Prompts

## 1. docs/10_ARCHITECTURE.md

Rewrite prompt:
Revise `docs/10_ARCHITECTURE.md` to preserve its architecture-plane value while correcting default-workflow framing.

Requirements:
- Add a short opening boundary note stating that this doc covers architecture planes across dopeTask as a whole
- Explicitly state that `tp series` is the default operator workflow
- Keep route/orchestrate as an active but non-default architecture plane
- Preserve determinism, refusal-first, artifact-first, and kernel-boundary concepts
- Remove or weaken wording that implies one universal current execution spine
- Do not imply orchestrator v0 auto mode is currently operational in this checkout
- Do not delete route/orchestrate as a real plane
- Keep the tone normative and compact

Output:
- revised doc text only

---

## 2. docs/11_PUBLIC_CONTRACT.md

Rewrite prompt:
Revise `docs/11_PUBLIC_CONTRACT.md` so it distinguishes public contract surfaces from the default operator workflow.

Requirements:
- Add a short opening boundary note stating that not all public surfaces are the default operator path
- State that `tp series` is the default operator workflow
- Keep route/orchestrate artifacts and availability config as real public contract surfaces, but not the sole/main current operator story
- Clarify active public surfaces vs default operator path vs specialist/non-default paths
- Preserve deterministic input/output/refusal framing
- Remove or weaken wording that over-centers route/orchestrate as the dominant workflow
- Do not imply `.dopetask/runtime/availability.yaml` is the main prerequisite for the default operator workflow

Output:
- revised doc text only

---

## 3. docs/12_ROUTER.md

Rewrite prompt:
Revise `docs/12_ROUTER.md` for boundary clarity without demoting the router plane.

Requirements:
- Add a short opening boundary note stating that router is an active, non-default planning/handoff surface
- Explicitly state that router is not the default operator execution workflow
- Preserve router determinism, route artifacts, and handoff outputs
- Clarify separation between route planning and packet execution
- Clarify separation between route artifacts and run/proof/series artifacts
- Do not imply router is obsolete
- Do not imply router planning equals execution

Output:
- revised doc text only

---

## 4. docs/23_INTEGRATION_GUIDE.md

Rewrite prompt:
Revise `docs/23_INTEGRATION_GUIDE.md` to sharpen execution-surface boundaries while preserving current integration guidance.

Requirements:
- Add a short opening boundary note stating that `tp series` is the default integration path for new work
- Preserve low-level and non-default surfaces as separate planes
- Clarify the distinction between `tp series`, low-level `tp exec`, route/orchestrate surfaces, and proof/state artifacts
- Preserve proof bundles and series state as key integration artifacts
- Do not imply all execution surfaces are equally recommended
- Do not imply runtime support broader than what is currently proven

Output:
- revised doc text only

---

## 5. docs/22_WORKFLOW_GUIDE.md

Rewrite prompt:
Revise `docs/22_WORKFLOW_GUIDE.md` only for consistency with repaired architecture/public-contract framing.

Requirements:
- Add or tighten a short opening boundary note stating this doc covers the default modern `tp series` operator workflow
- Preserve `tp series` as the canonical modern operator workflow
- Preserve explicit distinction from older/manual paths
- Do not imply other active surfaces are fake or gone
- Do not universalize `tp series` semantics across every execution plane
- Keep changes minimal compared with the other docs

Output:
- revised doc text only
