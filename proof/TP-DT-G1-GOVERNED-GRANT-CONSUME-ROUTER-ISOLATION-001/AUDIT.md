# TP-DT-G1-INDEPENDENT-L2-AUDIT-001 — independent L2 audit return

**Subject:** `DDD-Enterprises/dopeTask` PR #92, frozen post-sync head
`2b020f14cebfd277ae3ec1f462fe80141283fb16` (tree `834f7fbc34f723556a0770c1736be9d93d923f50`),
base `ff8044a842a000d75d859d420f00f247faca9a61`.

**Governing packet:** `TP-DT-G1-POST-BASELINE-SYNC-FINAL-AUDIT-001`
**Parent packet:** `TP-DT-G1-GOVERNED-GRANT-CONSUME-ROUTER-ISOLATION-001`
**Risk lane:** L2_MATERIAL

## Auditor

| field | value |
| --- | --- |
| runner | AGY (Google Antigravity CLI) v1.1.26 |
| model | `gemini-3.1-pro-high` — Gemini 3.1 Pro (High) |
| provider | Google |
| conversation | `c0ed62d7-55a2-4658-98d8-2580e401934a` |
| independence | PROVEN |
| fresh context | PROVEN |
| duration | 394s, 1 turn, 204,503 tokens |

The auditor is non-Anthropic and is neither the implementer (Claude Sonnet 5) nor the
synchronizer (Claude Opus 5). The route was live-probed for model identity immediately
before dispatch; there was no silent substitution.

## Verdict

```text
AUDIT_VERDICT=PASS_WITH_RISKS
DT_G1_MERGE_ELIGIBLE=YES
SUBSTANTIVE_REPAIR_REQUIRED=NO
PROOF_ONLY_AUDIT_BINDING_REQUIRED=YES
BLOCKING_FINDINGS=NONE
NONBLOCKING_RISKS=CX2_UNSTRUCTURED_OSERROR, CX3_DUPLICATED_ADMISSION_CALL, C02_REPO_SUBSTRING_MATCH
NEXT_GATE=PR_STEWARD_AND_OPERATOR_MERGE_DECISION

MERGE_AUTHORIZED=NO
RELEASE_AUTHORIZED=NO
PIN_UPDATE_AUTHORIZED=NO
ACTIVATION_AUTHORIZED=NO
```

`DT_G1_MERGE_ELIGIBLE=YES` is an eligibility finding, **not** an authorization. All four
authorization flags remain NO. The merge decision is operator-only.

## Auditor-authored adversarial probes (4 required, 4 delivered + 2 extra)

The auditor wrote and executed its own probe script against the real
`admit_governed_execution`; it is preserved verbatim as `AUDITOR_PROBE.py`.

| probe | result |
| --- | --- |
| repository substring/normalization attack | `grant.repository="opeTask"` → **ADMITTED** (risk C02) |
| mismatched present `worktree_binding.head_sha` | `head_sha="b"*40` → **ADMITTED**; value parsed, never compared |
| inconsistent network/credential constraints | `network_policy.class="DENIED"` → **ADMITTED**; schema-validated, not environment-enforced (declared DT-G2 boundary) |
| schema-valid `GOVERNED_DELIVERY_DISPATCH` issuer | **REFUSED** `GRANT_ISSUER_CLASS_UNACCEPTED` — passes the Draft-07 enum, fails closed on the explicit Python guard |
| legacy path retention | `build_route_plan` bypassed when `governed=True`, preserved when `False` |
| revocation without resolver | **REFUSED** `GRANT_REVOCATION_REF_PRESENT_NO_RESOLVER` — fail-closed confirmed |

## Disposition of the three automated PR-review findings

- **CX1 — `authority_effect`/`does_not_grant` required by schema but never read by the guard.**
  Ruled **NOT BLOCKING**, and independently re-confirmed by the synchronizer against the schema
  bytes: `does_not_grant` is a JSON Schema **`const`** (a frozen exact array) in *both*
  `macro_execution_authority_ref_v2` and `dcp_route_authorization`, and `grants` is a **closed
  enum** under `additionalProperties: false` whose value space does not contain `MERGE`,
  `ACTIVATION` or `ALLOWLIST_WIDENING` at all. An over-authoritative grant is therefore
  **not constructible**, not merely unenforced. The original review finding was incorrect:
  enforcement lives in the schema, and delegating to `Draft7Validator` is sufficient here.
- **CX2 — raw `OSError` on unreadable packet.** Non-blocking risk. Breaks the machine-checkable
  `reason` contract, but is inherently fail-closed: the exception terminates the path before admission.
- **CX3 — admission logic duplicated at `engine.py:123`.** Non-blocking risk. Argument construction
  is identical on both paths, so execution and dry-run cannot diverge logically.

## Risks disclosed in the return block but absent from the roll-up line

Recorded here so `NONBLOCKING_RISKS` is not mistaken for the complete risk set:

- `WORKTREE_HEAD_SHA_NOT_CHECKED=PROVEN` — demonstrated by probe 2.
- `NETWORK_CREDENTIAL_CLASS_ENFORCEMENT_DEPTH=NONE` — demonstrated by probe 3; this is the
  declared DT-G2 staging boundary, which the parent packet already acknowledges.
- `GRANT_REPOSITORY_SEMANTICS=SUBSTRING_MATCH` and `AUTHORITY_EFFECT_ENFORCEMENT=SCHEMA_ONLY`
  are statements of fact about the implementation, not requested repairs.

## Exactly-one-audit attestation

The only earlier attempt at this audit (AGY conversation
`38ba0886-98dd-4804-a2e6-3189d1366fe4`) terminated on HTTP 429 `QUOTA_EXHAUSTED`
(reset `2026-09-04T09:20:28Z`) **before emitting any finding or verdict**. No prior verdict on
the DT-G1 implementation exists. This run is the first and only completed audit of the subject,
and it audited the post-sync head only — the obsolete pre-sync head `1ee07dc5` was not audited.

## Custody and residue

`git rev-parse HEAD` was re-verified as `2b020f14…` after the audit run: the auditor mutated no
tracked file. It did author `probe.py` as an untracked file in the mounted worktree; that file was
captured verbatim as `AUDITOR_PROBE.py` and removed, leaving `git status` clean before this commit.

`AUDIT_PROMPT.md` is the exact prompt bytes; `AUDIT_STAGING_SHA256SUMS.txt` records everything
exposed to the auditor. The operator's `~/Downloads` handoff documents, all prior audit verdicts,
every project-memory store and the `dopemux-mvp` repository were deliberately **not** mounted, and
the prompt said so explicitly so the auditor would not report UNKNOWN for want of them.
