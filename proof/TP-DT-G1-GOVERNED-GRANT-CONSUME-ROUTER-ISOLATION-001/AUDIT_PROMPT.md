# TP-DT-G1-INDEPENDENT-L2-AUDIT-001 (subject rebound to post-sync frozen head)

You are the sole independent Tier-1 L2 auditor for this subject. You are NOT the implementer
and NOT the synchronizer. Both of those were Anthropic Claude sessions; you are not.
No repair, no file mutation, no git mutation, no GitHub mutation, no merge. Audit only.

## Mounted directories

1. `/private/tmp/claude-501/-Users-hue-code-dopemux-mvp/be3ee453-e357-40a6-8245-68c7c0fb174f/scratchpad/dtg1-audit`
   — the audit bundle. Read every file in it. `STAGING_SHA256SUMS.txt` records exactly what was exposed to you.
2. `/Users/hue/code/dopeTask/.worktrees/dt-g1-governed-grant-001`
   — a real git worktree of `DDD-Enterprises/dopeTask` whose HEAD **is** the frozen subject head.
   You have real tool access. USE IT: read the actual source, recompute hashes, run git commands,
   and run the test suite (`uv run pytest ...`, `uv run ruff check ...`, `uv run mypy ...`).
   Do not mutate tracked files. Writing throwaway fixtures under `/tmp` is allowed and encouraged.

## Frozen subject — audit THIS head and only this head

```text
REPOSITORY=DDD-Enterprises/dopeTask
PR=92
BASE_SHA=ff8044a842a000d75d859d420f00f247faca9a61
BASE_TREE=49667c258768c1dcf67e237de30f6da837966b2a
HEAD_SHA=2b020f14cebfd277ae3ec1f462fe80141283fb16
HEAD_TREE=834f7fbc34f723556a0770c1736be9d93d923f50
CHANGED_FILES=8
RISK_LANE=L2_MATERIAL
IMPLEMENTER=Claude Code CLI / claude-sonnet-5 / Anthropic
```

`1ee07dc521bad372f57378e63f8bcdbf8b10b2ac` is the **obsolete pre-sync head**. The governing
packet forbids auditing it. It appears here only so you can verify the synchronizer's claim
that the merge changed no DT-G1 semantic byte. First action: confirm `git rev-parse HEAD` in the
worktree equals `HEAD_SHA` above and that `git rev-parse HEAD^{tree}` equals `HEAD_TREE`. If it does
not, STOP and return `CUSTODY=FAIL`.

## What changed since the original audit packet was written

The original packet (`TP-DT-G1-INDEPENDENT-L2-AUDIT-001.json`, in the bundle) pinned the pre-sync
head against base `7ce24ae1`. Since then PR #93 landed on `main` and the DT-G1 branch was merged
forward. The governing successor packet is `TP-DT-G1-POST-BASELINE-SYNC-FINAL-AUDIT-001.json`,
also in the bundle. Where the two disagree on the subject head, the successor wins.
Everything else in the original packet — the challenge matrix, the required probes, the required
return block — still binds you.

## Read as claims, not as truth

`out/implementation/TP-DT-G1-GOVERNED-GRANT-CONSUME-ROUTER-ISOLATION-001/PROOF.json`,
`task-packets/TP-DT-G1-GOVERNED-GRANT-CONSUME-ROUTER-ISOLATION-001.json`, and
`03_SYNC_CLAIMS_TO_FALSIFY.md` are all claims by interested parties. Falsify them.

## Mandatory challenge

1. C0-R2 authority fidelity.
2. `DCPRouteAuthorization` remains policy-only and never grants execution authority.
3. `MacroExecutionAuthorityRefV2` exact grant consumption.
4. GOVERNED_MODE cannot call `build_route_plan` and cannot silently default runner/model.
   Prove reachability, do not just trust the existing monkeypatch test.
5. LEGACY_LOCAL_MODE compatibility (planner behavior preserved).
6. Exact task/repo/project/worktree/allowlist/digest/expiry binding, including
   **exact ordered allowlist equality** and **model-ceiling narrowing-only**.
7. The carried UNKNOWNs: `project_id` semantics, `repository` substring semantics,
   network/credential enforcement depth, ignored optional `worktree_binding.head_sha`.
8. Staging boundary: governed mode already reaches real Codex execution while
   provider/network/credential/mutation/receipt enforcement is deferred to DT-G2.
9. Proof/test truthfulness. **Note the baseline changed**: the implementer's
   "1 pre-existing failure" alibi no longer exists post-#93. Re-derive the base and head suite
   results yourself.
10. No DT-G2 / release / pin / activation scope creep.
11. Revocation without a resolver must be fail-closed. Prove it.
12. Schema registry substitution: can a caller substitute a permissive `$id`-colliding schema?
13. Dry-run semantics and tmux propagation of `--grant` / `--dcp-route-authorization`.
14. Forbidden-path closure: verify the changed set vs `BASE_SHA` really is exactly the 8 files.
15. The three CX items in `03_SYNC_CLAIMS_TO_FALSIFY.md`. CX1 in particular
    (`authority_effect` / `does_not_grant` required by schema but never read by the guard) —
    build a fixture, run it, and rule on whether it is blocking.

Detailed notes for C01–C10 are in `02_REQUIRED_CHALLENGES.md`. Read them.

## Author at least four NEW adversarial probes of your own

At minimum: a repository substring/normalization attack; a mismatched present
`worktree_binding.head_sha`; inconsistent provider/network/credential constraints; and a
schema-valid `GOVERNED_DELIVERY_DISPATCH` issuer. Actually execute them against the real code
and report what happened, not what you expect would happen.

## Required final block — emit verbatim with values filled in, as the last thing you output

```text
AUDIT_ID=TP-DT-G1-INDEPENDENT-L2-AUDIT-001
AUDITOR_RUNNER=
AUDITOR_MODEL=
AUDITOR_PROVIDER=
INDEPENDENCE=PROVEN|LIMITED|FAIL
FRESH_CONTEXT=PROVEN|LIMITED|FAIL

SUBJECT_PR=92
SUBJECT_BASE_SHA=ff8044a842a000d75d859d420f00f247faca9a61
SUBJECT_HEAD_SHA=2b020f14cebfd277ae3ec1f462fe80141283fb16
SUBJECT_HEAD_TREE=834f7fbc34f723556a0770c1736be9d93d923f50
CUSTODY=PASS|FAIL
POST_SYNC_SEMANTIC_DELTA_FROM_PRE_SYNC=NONE|CHANGED|UNKNOWN

MIRROR_10_OF_10=
CHANGED_FILE_ALLOWLIST=
C0_AUTHORITY_FIDELITY=
DCP_ROUTE_POLICY_ONLY=
GRANT_CONSUME_NO_WIDENING=
GOVERNED_PLANNER_CALLS=
LEGACY_REGRESSION=
DT_G2_BOUNDARY=

GRANT_PROJECT_ID_SEMANTICS=
GRANT_REPOSITORY_SEMANTICS=
NETWORK_CREDENTIAL_CLASS_ENFORCEMENT_DEPTH=
WORKTREE_HEAD_SHA_NOT_CHECKED=
AUTHORITY_EFFECT_ENFORCEMENT=
REVOCATION_FAIL_CLOSED=
SCHEMA_REGISTRY_SUBSTITUTION=

AUDITOR_AUTHORED_PROBES=
FOCUSED_TESTS=
RELEVANT_COMPLETE_SUITES=
FULL_SUITE_BASE=
FULL_SUITE_HEAD=
PREEXISTING_FAILURE_PROVEN=
PROOF_TRUTHFULNESS=
FORBIDDEN_PATH_DRIFT=

BLOCKING_FINDINGS=
NONBLOCKING_RISKS=

AUDIT_VERDICT=PASS|PASS_WITH_RISKS|FAIL|NEEDS_SUPERVISOR
DT_G1_MERGE_ELIGIBLE=YES|NO
SUBSTANTIVE_REPAIR_REQUIRED=YES|NO
PROOF_ONLY_AUDIT_BINDING_REQUIRED=YES|NO

MERGE_AUTHORIZED=NO
RELEASE_AUTHORIZED=NO
PIN_UPDATE_AUTHORIZED=NO
ACTIVATION_AUTHORIZED=NO

NEXT_GATE=
```

`NEXT_GATE` is one of `PR_STEWARD_AND_OPERATOR_MERGE_DECISION`, `BOUNDED_DT_G1_REPAIR`,
or `NEEDS_SUPERVISOR`.

Before the final block, write your full findings: every probe you ran, the exact command, the
exact observed output, and your ruling. A finding with no executed evidence behind it must be
labeled `UNVERIFIED`.
