import json
from pathlib import Path
from datetime import datetime, timezone, timedelta
from dopetask.guard.governed_execution import admit_governed_execution, GovernedAdmissionError
from dopetask.core.tp_parser import TPParser
import hashlib
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

repo_root = Path("/Users/hue/code/dopeTask/.worktrees/dt-g1-governed-grant-001")
packet_path = repo_root / "task-packets/TP-DT-G1-GOVERNED-GRANT-CONSUME-ROUTER-ISOLATION-001.json"
tp = TPParser.parse_file(packet_path)
dcp_path = Path("/tmp/dcp.json")
grant_path = Path("/tmp/grant.json")

dcp_base = {
    "schema_version": "dopemux-dcp-route-authorization.v1",
    "authorization_id": "auth123",
    "authority_class": "POLICY_ROUTE_AUTHORIZATION",
    "execution_authority": "NONE",
    "issuer": {"system": "DCP_CONTROL_PLANE", "principal_ref": "dcp"},
    "issued_at": datetime.now(timezone.utc).isoformat(),
    "expires_at": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
    "policy_digest": "a"*64,
    "project_workspace_request_binding": {
        "project_id": "p1", "workspace_ref": "w1", "request_id": "r1"
    },
    "ordered_allowed_route_profiles": [],
    "runner_provider_model_eligibility": {
        "allowed_runners": ["a"], "allowed_providers": ["b"], "allowed_models": ["c"]
    },
    "reasoning_policy": {"class": "NONE"},
    "retry_policy": {
        "max_visible_attempts": 0, "sent_acceptance_unknown_retry": "NOT_EQUIVALENT_TO_PRE_STATE_SAFE_RETRY"
    },
    "fallback_policy": {
        "authorized": False, "may_be_invented_by_consumer": False
    },
    "network_policy": {"class": "DENIED"},
    "cost_usage_ceilings": {
        "currency": "USD", "max_cost": 1.0, "max_input_tokens": 10, "max_output_tokens": 10
    },
    "tool_contract_refs": [],
    "minimum_conformance_status": "VERIFIED",
    "identity_evidence_requirement": {"minimum_posture": "ORDINARY_RUNTIME_TRANSPORT"},
    "audit_independence_requirement": {"required": False},
    "authority_effect": {
        "grants": ["ROUTE_ELIGIBILITY"],
        "does_not_grant": [
            "REPOSITORY_MUTATION", "TOOL_EXECUTION", "WORKFLOW_TRANSITION",
            "MERGE", "ACTIVATION", "CREDENTIAL_CHANGE", "PRODUCTION_AUTHORITY",
            "EXECUTION_GRANT", "UAG_PROFILE_PROMOTION", "EXACTLY_ONCE_EXTERNAL_EFFECT"
        ],
        "provider_private_state_permitted": False
    }
}
dcp_path.write_text(json.dumps(dcp_base))

grant = {
    "schema_version": "dopemux-macro-execution-authority-ref.v2",
    "family": "MacroExecutionAuthorityRef",
    "lineage_parent": "dopemux-macro-execution-authority-ref.v1",
    "migration_semantics": "FAMILY_SUCCESSOR_NOT_JSON_INSTANCE_BACKWARD_COMPATIBLE",
    "authority_id": "auth-1",
    "issuer": {"class": "OPERATOR", "principal_ref": "test"},
    "issued_at": datetime.now(timezone.utc).isoformat(),
    "expires_at": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
    "nonce": "nonce123",
    "idempotency_key": "idemp123",
    "subject": {
        "kind": "SINGLE_TASK_PACKET",
        "task_packet_id": tp.id,
        "task_packet_sha256": sha(packet_path)
    },
    "consumer": "dopetask",
    "permitted_execution": {
        "mode": "GOVERNED_SINGLE_TP",
        "runner": "codex",
        "max_attempts": 1,
        "substitution_policy": "forbid",
        "model_ceiling": "claude-3-sonnet"
    },
    "project_id": "dopetask",
    "repository": "dopeTask",
    "worktree_binding": {
        "path": str(repo_root.resolve()),
        "head_sha": "a"*40
    },
    "allowlist": tp.commit.allowlist,
    "dcp_route_authorization_digest": sha(dcp_path),
    "authority_effect": {
        "grants": ["RUNNER_INVOCATION"],
        "does_not_grant": [
            "WORKFLOW_LEGALITY", "MERGE", "ACTIVATION", "PRODUCTION_AUTHORITY",
            "CREDENTIAL_CHANGE", "POLICY_ROUTE_INVENTION", "UAG_PROFILE_PROMOTION",
            "EXACTLY_ONCE_EXTERNAL_EFFECT", "ALLOWLIST_WIDENING", "SELF_ISSUANCE"
        ]
    },
    "uag_profile": "none",
    "network_policy": {"class": "DENIED"},
    "credential_class": {"class": "UNKNOWN", "origin_id": "test"},
    "repair": {
        "attempts_per_subject_max": 1,
        "successor_grant_required_for_repair": True
    },
    "exactly_once_claim": "FORBIDDEN",
    "acceptance_semantics": "AT_MOST_ONCE_GRANT_ACCEPT",
    "git_control": {
        "worktree_provisioning_allowed": False,
        "branch_provisioning_allowed": False,
        "push_allowed": False,
        "pr_mutation_allowed": False
    },
    "workflow": {
        "mode": "NONE",
        "to_mutation_allowed": False
    },
    "revocation_ref": "some-ref"
}
grant_path.write_text(json.dumps(grant))

try:
    admit_governed_execution(
        grant_path=grant_path, dcp_route_authorization_path=dcp_path,
        packet_path=packet_path, tp=tp, repo_root=repo_root,
        cli_agent="codex", cli_model="claude-3-sonnet"
    )
    print("REVOCATION: ADMITTED")
except GovernedAdmissionError as e:
    print(f"REVOCATION: REFUSED - {e.reason}")
