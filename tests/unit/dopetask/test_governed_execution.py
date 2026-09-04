"""Adversarial admission matrix for GOVERNED_MODE grant consumption.

Exercises `dopetask.guard.governed_execution.admit_governed_execution`
directly against fixture MacroExecutionAuthorityRefV2 grants and
DCPRouteAuthorization artifacts built from the mirrored C0-R2 schemas.
"""

from __future__ import annotations

import copy
import hashlib
import json
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pytest

from dopetask.core.schema import TaskPacket, TPCommit, TPRepoBinding
from dopetask.guard.governed_execution import GovernedAdmissionError, admit_governed_execution

ORIGIN_URL = "git@github.com:DDD-Enterprises/dopeTask.git"
PACKET_ID = "TP-GOVERNED-TEST"
ALLOWLIST = ["task-packets/TP-GOVERNED-TEST.json", "src/dopetask/example.py"]


def _init_git_repo(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init"], cwd=path, check=True, capture_output=True, text=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"], cwd=path, check=True, capture_output=True, text=True
    )
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=path, check=True, capture_output=True, text=True)
    subprocess.run(["git", "remote", "add", "origin", ORIGIN_URL], cwd=path, check=True, capture_output=True, text=True)
    return path


def _write_packet_file(path: Path, *, packet_id: str = PACKET_ID, salt: str = "") -> Path:
    path.write_text(json.dumps({"id": packet_id, "salt": salt}, indent=2) + "\n", encoding="utf-8")
    return path


def _packet_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _make_task_packet(*, packet_id: str = PACKET_ID, project_id: str = "dopetask") -> TaskPacket:
    return TaskPacket(
        id=packet_id,
        target="Governed test target",
        project=project_id,
        repo_binding=TPRepoBinding(project_id=project_id, repo_marker=".dopetaskroot", require_identity_match=True),
        commit=TPCommit(message="test", allowlist=list(ALLOWLIST)),
    )


def _valid_dcp_route_authorization() -> dict[str, Any]:
    now = datetime.now(timezone.utc)
    exp = now + timedelta(hours=1)
    return {
        "schema_version": "dopemux-dcp-route-authorization.v1",
        "authorization_id": "dcp-auth-0001",
        "authority_class": "POLICY_ROUTE_AUTHORIZATION",
        "execution_authority": "NONE",
        "issuer": {"system": "DCP_CONTROL_PLANE", "principal_ref": "dcp:test"},
        "issued_at": now.isoformat().replace("+00:00", "Z"),
        "expires_at": exp.isoformat().replace("+00:00", "Z"),
        "policy_digest": "0" * 64,
        "project_workspace_request_binding": {
            "project_id": "dopetask",
            "workspace_ref": "ws-0001",
            "request_id": "req-0001",
        },
        "ordered_allowed_route_profiles": [{"route_profile_id": "route-1", "model_ceiling": "gpt-5.3-codex"}],
        "runner_provider_model_eligibility": {
            "allowed_runners": ["codex"],
            "allowed_providers": ["openai"],
            "allowed_models": ["gpt-5.3-codex"],
        },
        "reasoning_policy": {"class": "NONE"},
        "retry_policy": {
            "max_visible_attempts": 1,
            "sent_acceptance_unknown_retry": "NOT_EQUIVALENT_TO_PRE_STATE_SAFE_RETRY",
        },
        "fallback_policy": {"authorized": False, "may_be_invented_by_consumer": False},
        "network_policy": {"class": "DENIED"},
        "cost_usage_ceilings": {
            "currency": "USD",
            "max_cost": 1.0,
            "max_input_tokens": 1000,
            "max_output_tokens": 1000,
        },
        "tool_contract_refs": [],
        "minimum_conformance_status": "VERIFIED",
        "identity_evidence_requirement": {"minimum_posture": "ORDINARY_RUNTIME_TRANSPORT"},
        "audit_independence_requirement": {"required": False},
        "authority_effect": {
            "grants": ["ROUTE_ELIGIBILITY"],
            "does_not_grant": [
                "REPOSITORY_MUTATION",
                "TOOL_EXECUTION",
                "WORKFLOW_TRANSITION",
                "MERGE",
                "ACTIVATION",
                "CREDENTIAL_CHANGE",
                "PRODUCTION_AUTHORITY",
                "EXECUTION_GRANT",
                "UAG_PROFILE_PROMOTION",
                "EXACTLY_ONCE_EXTERNAL_EFFECT",
            ],
            "provider_private_state_permitted": False,
        },
    }


def _valid_grant(
    *,
    task_packet_id: str,
    task_packet_sha256: str,
    dcp_digest: str,
    worktree_path: str,
    project_id: str = "dopetask",
    repository: str = "DDD-Enterprises/dopeTask",
    allowlist: list[str] | None = None,
    model_ceiling: str | None = "gpt-5.3-codex",
    issuer_class: str = "OPERATOR",
    mode: str = "GOVERNED_SINGLE_TP",
    runner: str = "codex",
    max_attempts: int = 1,
    substitution_policy: str = "forbid",
    consumer: str = "dopetask",
    subject_kind: str = "SINGLE_TASK_PACKET",
    issued_at: datetime | None = None,
    expires_at: datetime | None = None,
    revocation_ref: str | None = None,
) -> dict[str, Any]:
    now = issued_at or datetime.now(timezone.utc)
    exp = expires_at or (now + timedelta(hours=1))
    permitted_execution: dict[str, Any] = {
        "mode": mode,
        "runner": runner,
        "substitution_policy": substitution_policy,
        "max_attempts": max_attempts,
    }
    if model_ceiling is not None:
        permitted_execution["model_ceiling"] = model_ceiling

    subject: dict[str, Any] = {"kind": subject_kind}
    if subject_kind == "SINGLE_TASK_PACKET":
        subject["task_packet_id"] = task_packet_id
        subject["task_packet_sha256"] = task_packet_sha256
    else:
        subject["macro_id"] = "macro-0001"
        subject["macro_sha256"] = "1" * 64
        subject["plan_id"] = "plan-0001"
        subject["plan_sha256"] = "2" * 64
        subject["child_bindings"] = [{"tp_id": task_packet_id, "tp_sha256": task_packet_sha256}]

    grant: dict[str, Any] = {
        "schema_version": "dopemux-macro-execution-authority-ref.v2",
        "family": "MacroExecutionAuthorityRef",
        "lineage_parent": "dopemux-macro-execution-authority-ref.v1",
        "migration_semantics": "FAMILY_SUCCESSOR_NOT_JSON_INSTANCE_BACKWARD_COMPATIBLE",
        "authority_id": "authority-test-0001",
        "issuer": {"class": issuer_class, "principal_ref": "operator:test"},
        "issued_at": now.isoformat().replace("+00:00", "Z"),
        "expires_at": exp.isoformat().replace("+00:00", "Z"),
        "nonce": "nonce-0001",
        "idempotency_key": "idem-0001",
        "project_id": project_id,
        "repository": repository,
        "worktree_binding": {"path": worktree_path},
        "subject": subject,
        "consumer": consumer,
        "allowlist": list(allowlist if allowlist is not None else ALLOWLIST),
        "permitted_execution": permitted_execution,
        "dcp_route_authorization_digest": dcp_digest,
        "uag_profile": "none",
        "network_policy": {"class": "DENIED"},
        "credential_class": {"class": "RUNNER_HOST_DEFAULT", "origin_id": "test"},
        "repair": {"attempts_per_subject_max": 0, "successor_grant_required_for_repair": False},
        "authority_effect": {
            "grants": ["TASK_PACKET_MUTATION_WITHIN_ALLOWLIST"],
            "does_not_grant": [
                "WORKFLOW_LEGALITY",
                "MERGE",
                "ACTIVATION",
                "PRODUCTION_AUTHORITY",
                "CREDENTIAL_CHANGE",
                "POLICY_ROUTE_INVENTION",
                "UAG_PROFILE_PROMOTION",
                "EXACTLY_ONCE_EXTERNAL_EFFECT",
                "ALLOWLIST_WIDENING",
                "SELF_ISSUANCE",
            ],
        },
        "exactly_once_claim": "FORBIDDEN",
        "acceptance_semantics": "AT_MOST_ONCE_GRANT_ACCEPT",
    }
    if mode == "GOVERNED_SINGLE_TP":
        grant["git_control"] = {
            "worktree_provisioning_allowed": False,
            "branch_provisioning_allowed": False,
            "push_allowed": False,
            "pr_mutation_allowed": False,
        }
        grant["workflow"] = {"mode": "NONE", "to_mutation_allowed": False}
    if revocation_ref is not None:
        grant["revocation_ref"] = revocation_ref
    return grant


@pytest.fixture
def scenario(tmp_path: Path):
    repo = _init_git_repo(tmp_path / "repo")
    packet_path = _write_packet_file(repo / "packet.json")
    packet_sha256 = _packet_sha256(packet_path)
    dcp = _valid_dcp_route_authorization()
    dcp_path = repo / "dcp_route_authorization.json"
    dcp_path.write_text(json.dumps(dcp, indent=2) + "\n", encoding="utf-8")
    dcp_digest = hashlib.sha256(dcp_path.read_bytes()).hexdigest()

    grant = _valid_grant(
        task_packet_id=PACKET_ID,
        task_packet_sha256=packet_sha256,
        dcp_digest=dcp_digest,
        worktree_path=str(repo.resolve()),
    )

    return {
        "repo": repo,
        "packet_path": packet_path,
        "packet_sha256": packet_sha256,
        "dcp_path": dcp_path,
        "dcp_digest": dcp_digest,
        "grant": grant,
        "tp": _make_task_packet(),
    }


def _write_grant(path: Path, grant: dict[str, Any]) -> Path:
    path.write_text(json.dumps(grant, indent=2) + "\n", encoding="utf-8")
    return path


def _admit(scenario: dict[str, Any], *, grant: dict[str, Any] | None = None, cli_agent="codex", cli_model=None):
    grant_path = scenario["repo"] / "grant.json"
    _write_grant(grant_path, grant if grant is not None else scenario["grant"])
    return admit_governed_execution(
        grant_path=grant_path,
        dcp_route_authorization_path=scenario["dcp_path"],
        packet_path=scenario["packet_path"],
        tp=scenario["tp"],
        repo_root=scenario["repo"],
        cli_agent=cli_agent,
        cli_model=cli_model,
    )


def test_valid_exact_grant_accepts(scenario) -> None:
    decision = _admit(scenario)
    assert decision.effective_runner == "codex"
    assert decision.effective_model == "gpt-5.3-codex"
    assert decision.model_source == "GRANT_CEILING"
    assert decision.grant_authority_id == "authority-test-0001"


def test_dcp_route_authorization_digest_mismatch_rejects(scenario) -> None:
    grant = copy.deepcopy(scenario["grant"])
    grant["dcp_route_authorization_digest"] = "f" * 64
    with pytest.raises(GovernedAdmissionError) as excinfo:
        _admit(scenario, grant=grant)
    assert excinfo.value.reason == "DCP_ROUTE_AUTHORIZATION_DIGEST_MISMATCH"


@pytest.mark.parametrize(
    ("mode", "runner", "consumer", "max_attempts", "substitution_policy"),
    [
        ("TRANSITIONAL_DIRECT_RUNNER", "codex", "dopetask", 1, "forbid"),
        ("GOVERNED_SINGLE_TP", "codex", "dopetask", 1, "grant_listed_only"),
    ],
)
def test_wrong_permitted_execution_shape_rejects(
    scenario, mode, runner, consumer, max_attempts, substitution_policy
) -> None:
    grant = _valid_grant(
        task_packet_id=PACKET_ID,
        task_packet_sha256=scenario["packet_sha256"],
        dcp_digest=scenario["dcp_digest"],
        worktree_path=str(scenario["repo"].resolve()),
        mode=mode,
        runner=runner,
        consumer=consumer,
        max_attempts=max_attempts,
        substitution_policy=substitution_policy,
    )
    with pytest.raises(GovernedAdmissionError):
        _admit(scenario, grant=grant)


def test_issuer_governed_delivery_dispatch_rejects(scenario) -> None:
    grant = copy.deepcopy(scenario["grant"])
    grant["issuer"]["class"] = "GOVERNED_DELIVERY_DISPATCH"
    with pytest.raises(GovernedAdmissionError) as excinfo:
        _admit(scenario, grant=grant)
    assert excinfo.value.reason == "GRANT_ISSUER_CLASS_UNACCEPTED"


def test_issuer_dcp_class_rejects_schema_invalid(scenario) -> None:
    grant = copy.deepcopy(scenario["grant"])
    grant["issuer"]["class"] = "DCP"
    with pytest.raises(GovernedAdmissionError) as excinfo:
        _admit(scenario, grant=grant)
    assert excinfo.value.reason == "GRANT_SCHEMA_INVALID"


def test_expired_grant_rejects(scenario) -> None:
    now = datetime.now(timezone.utc)
    grant = _valid_grant(
        task_packet_id=PACKET_ID,
        task_packet_sha256=scenario["packet_sha256"],
        dcp_digest=scenario["dcp_digest"],
        worktree_path=str(scenario["repo"].resolve()),
        issued_at=now - timedelta(hours=2),
        expires_at=now - timedelta(hours=1),
    )
    with pytest.raises(GovernedAdmissionError) as excinfo:
        _admit(scenario, grant=grant)
    assert excinfo.value.reason == "GRANT_EXPIRED"


def test_not_yet_valid_grant_rejects(scenario) -> None:
    now = datetime.now(timezone.utc)
    grant = _valid_grant(
        task_packet_id=PACKET_ID,
        task_packet_sha256=scenario["packet_sha256"],
        dcp_digest=scenario["dcp_digest"],
        worktree_path=str(scenario["repo"].resolve()),
        issued_at=now + timedelta(hours=1),
        expires_at=now + timedelta(hours=2),
    )
    with pytest.raises(GovernedAdmissionError) as excinfo:
        _admit(scenario, grant=grant)
    assert excinfo.value.reason == "GRANT_NOT_YET_VALID"


def test_task_packet_id_mismatch_rejects(scenario) -> None:
    grant = copy.deepcopy(scenario["grant"])
    grant["subject"]["task_packet_id"] = "TP-SOME-OTHER-PACKET"
    with pytest.raises(GovernedAdmissionError) as excinfo:
        _admit(scenario, grant=grant)
    assert excinfo.value.reason == "TASK_PACKET_ID_MISMATCH"


def test_task_packet_sha256_mismatch_rejects(scenario) -> None:
    grant = copy.deepcopy(scenario["grant"])
    grant["subject"]["task_packet_sha256"] = "a" * 64
    with pytest.raises(GovernedAdmissionError) as excinfo:
        _admit(scenario, grant=grant)
    assert excinfo.value.reason == "TASK_PACKET_SHA256_MISMATCH"


def test_project_mismatch_rejects(scenario) -> None:
    grant = copy.deepcopy(scenario["grant"])
    grant["project_id"] = "some-other-project"
    with pytest.raises(GovernedAdmissionError) as excinfo:
        _admit(scenario, grant=grant)
    assert excinfo.value.reason == "GRANT_PROJECT_MISMATCH"


def test_repository_mismatch_rejects(scenario) -> None:
    grant = copy.deepcopy(scenario["grant"])
    grant["repository"] = "someone-else/unrelated-repo"
    with pytest.raises(GovernedAdmissionError) as excinfo:
        _admit(scenario, grant=grant)
    assert excinfo.value.reason == "GRANT_REPOSITORY_MISMATCH"


def test_worktree_mismatch_rejects(scenario, tmp_path: Path) -> None:
    grant = copy.deepcopy(scenario["grant"])
    grant["worktree_binding"]["path"] = str(tmp_path / "not-the-repo")
    with pytest.raises(GovernedAdmissionError) as excinfo:
        _admit(scenario, grant=grant)
    assert excinfo.value.reason == "GRANT_WORKTREE_MISMATCH"


def test_allowlist_mismatch_rejects_on_order(scenario) -> None:
    grant = copy.deepcopy(scenario["grant"])
    grant["allowlist"] = list(reversed(ALLOWLIST))
    with pytest.raises(GovernedAdmissionError) as excinfo:
        _admit(scenario, grant=grant)
    assert excinfo.value.reason == "ALLOWLIST_MISMATCH"


def test_allowlist_mismatch_rejects_on_superset(scenario) -> None:
    grant = copy.deepcopy(scenario["grant"])
    grant["allowlist"] = [*ALLOWLIST, "src/dopetask/extra_widened_file.py"]
    with pytest.raises(GovernedAdmissionError) as excinfo:
        _admit(scenario, grant=grant)
    assert excinfo.value.reason == "ALLOWLIST_MISMATCH"


def test_revocation_ref_present_rejects(scenario) -> None:
    grant = copy.deepcopy(scenario["grant"])
    grant["revocation_ref"] = "revocation-0001"
    with pytest.raises(GovernedAdmissionError) as excinfo:
        _admit(scenario, grant=grant)
    assert excinfo.value.reason == "GRANT_REVOCATION_REF_PRESENT_NO_RESOLVER"


def test_model_ceiling_absent_rejects(scenario) -> None:
    grant = copy.deepcopy(scenario["grant"])
    del grant["permitted_execution"]["model_ceiling"]
    with pytest.raises(GovernedAdmissionError) as excinfo:
        _admit(scenario, grant=grant)
    assert excinfo.value.reason == "GRANT_MODEL_CEILING_ABSENT"


def test_cli_model_override_forbidden_rejects(scenario) -> None:
    with pytest.raises(GovernedAdmissionError) as excinfo:
        _admit(scenario, cli_model="some-other-model")
    assert excinfo.value.reason == "CLI_MODEL_MISMATCH_GRANT_CEILING"


def test_cli_model_matching_ceiling_accepts(scenario) -> None:
    decision = _admit(scenario, cli_model="gpt-5.3-codex")
    assert decision.effective_model == "gpt-5.3-codex"


def test_cli_agent_runner_mismatch_rejects(scenario) -> None:
    with pytest.raises(GovernedAdmissionError) as excinfo:
        _admit(scenario, cli_agent="gemini")
    assert excinfo.value.reason == "CLI_AGENT_RUNNER_MISMATCH"


def test_subject_kind_macro_plan_unsupported_rejects(scenario) -> None:
    grant = _valid_grant(
        task_packet_id=PACKET_ID,
        task_packet_sha256=scenario["packet_sha256"],
        dcp_digest=scenario["dcp_digest"],
        worktree_path=str(scenario["repo"].resolve()),
        mode="TRANSITIONAL_DIRECT_RUNNER",
        subject_kind="MACRO_PLAN",
    )
    with pytest.raises(GovernedAdmissionError) as excinfo:
        _admit(scenario, grant=grant)
    assert excinfo.value.reason == "GRANT_SUBJECT_KIND_UNSUPPORTED"


def test_malformed_grant_json_rejects(scenario) -> None:
    grant_path = scenario["repo"] / "grant.json"
    grant_path.write_text("{not valid json", encoding="utf-8")
    with pytest.raises(GovernedAdmissionError) as excinfo:
        admit_governed_execution(
            grant_path=grant_path,
            dcp_route_authorization_path=scenario["dcp_path"],
            packet_path=scenario["packet_path"],
            tp=scenario["tp"],
            repo_root=scenario["repo"],
            cli_agent="codex",
            cli_model=None,
        )
    assert excinfo.value.reason == "GRANT_UNREADABLE"


def test_missing_grant_file_rejects(scenario) -> None:
    missing_path = scenario["repo"] / "does_not_exist.json"
    with pytest.raises(GovernedAdmissionError) as excinfo:
        admit_governed_execution(
            grant_path=missing_path,
            dcp_route_authorization_path=scenario["dcp_path"],
            packet_path=scenario["packet_path"],
            tp=scenario["tp"],
            repo_root=scenario["repo"],
            cli_agent="codex",
            cli_model=None,
        )
    assert excinfo.value.reason == "GRANT_UNREADABLE"
