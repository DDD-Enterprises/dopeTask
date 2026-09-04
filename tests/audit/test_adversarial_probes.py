"""Adversarial probes for TP-DT-G1-INDEPENDENT-L2-AUDIT-001.

Four mandatory probes plus additional edge cases:
1. Repository substring/normalization attack
2. Mismatched present worktree_binding.head_sha
3. Inconsistent provider/network/credential constraints
4. Schema-valid GOVERNED_DELIVERY_DISPATCH issuer
5. HTTPS vs SSH origin normalization
6. Substring attack with partial repo name
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
PACKET_ID = "TP-ADVERSARIAL-TEST"
ALLOWLIST = ["task-packets/TP-ADVERSARIAL-TEST.json", "src/dopetask/example.py"]


def _init_git_repo(path: Path, origin_url: str = ORIGIN_URL) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init"], cwd=path, check=True, capture_output=True, text=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"], cwd=path, check=True, capture_output=True, text=True
    )
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=path, check=True, capture_output=True, text=True)
    subprocess.run(["git", "remote", "add", "origin", origin_url], cwd=path, check=True, capture_output=True, text=True)
    return path


def _write_packet_file(path: Path, *, packet_id: str = PACKET_ID, salt: str = "") -> Path:
    path.write_text(json.dumps({"id": packet_id, "salt": salt}, indent=2) + "\n", encoding="utf-8")
    return path


def _packet_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _make_task_packet(*, packet_id: str = PACKET_ID, project_id: str = "dopetask") -> TaskPacket:
    return TaskPacket(
        id=packet_id,
        target="Adversarial test target",
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
    network_policy_class: str = "DENIED",
    credential_class: str = "RUNNER_HOST_DEFAULT",
    worktree_head_sha: str | None = None,
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
        "network_policy": {"class": network_policy_class},
        "credential_class": {"class": credential_class, "origin_id": "test"},
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
    if worktree_head_sha is not None:
        grant["worktree_binding"]["head_sha"] = worktree_head_sha
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


# ==============================================================================
# PROBE 1: Repository substring/normalization attack
# ==============================================================================

def test_probe_repository_substring_attack_short_string(scenario) -> None:
    """ATTACK: grant.repository is a short substring that matches origin URL."""
    grant = copy.deepcopy(scenario["grant"])
    grant["repository"] = "dopeTask"  # Short substring of "DDD-Enterprises/dopeTask"
    
    # CRITICAL FINDING: This is ACCEPTED because "dopeTask" IS a substring of
    # "git@github.com:DDD-Enterprises/dopeTask.git"
    # This is a KNOWN UNKNOWN (C02) - substring matching is the documented behavior
    decision = _admit(scenario, grant=grant)
    assert decision.effective_runner == "codex"
    # VULNERABILITY: An attacker could use "dopeTask" to match any repo containing that string


def test_probe_repository_substring_attack_case_variation(scenario) -> None:
    """ATTACK: grant.repository uses different case to bypass substring check."""
    grant = copy.deepcopy(scenario["grant"])
    grant["repository"] = "ddd-enterprises/dopetask"  # Different case
    
    # This SHOULD reject because the check is case-sensitive
    with pytest.raises(GovernedAdmissionError) as excinfo:
        _admit(scenario, grant=grant)
    assert excinfo.value.reason == "GRANT_REPOSITORY_MISMATCH"


def test_probe_repository_https_vs_ssh_normalization(tmp_path: Path) -> None:
    """ATTACK: Origin URL is HTTPS but grant uses SSH format (or vice versa)."""
    repo = _init_git_repo(tmp_path / "repo", origin_url="https://github.com/DDD-Enterprises/dopeTask.git")
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
        repository="git@github.com:DDD-Enterprises/dopeTask.git",  # SSH format
    )

    scenario = {
        "repo": repo,
        "packet_path": packet_path,
        "dcp_path": dcp_path,
        "grant": grant,
        "tp": _make_task_packet(),
    }

    # This SHOULD reject because SSH format is not a substring of HTTPS URL
    with pytest.raises(GovernedAdmissionError) as excinfo:
        _admit(scenario, grant=grant)
    assert excinfo.value.reason == "GRANT_REPOSITORY_MISMATCH"


# ==============================================================================
# PROBE 2: Mismatched present worktree_binding.head_sha
# ==============================================================================

def test_probe_worktree_head_sha_mismatched_but_ignored(scenario) -> None:
    """ATTACK: worktree_binding.head_sha is present but doesn't match current HEAD."""
    grant = copy.deepcopy(scenario["grant"])
    grant["worktree_binding"]["head_sha"] = "0" * 40  # Fake SHA that doesn't match
    
    # This SHOULD ACCEPT because head_sha is optional and not checked
    # This is a KNOWN UNKNOWN (C04) - the implementation intentionally ignores it
    decision = _admit(scenario, grant=grant)
    assert decision.effective_runner == "codex"


def test_probe_worktree_head_sha_replay_attack(scenario) -> None:
    """ATTACK: worktree_binding.head_sha matches an old commit, not current HEAD."""
    # Create initial commit
    (scenario["repo"] / "initial.txt").write_text("initial\n", encoding="utf-8")
    subprocess.run(["git", "add", "initial.txt"], cwd=scenario["repo"], check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "initial"], cwd=scenario["repo"], check=True, capture_output=True)
    
    # Get current HEAD SHA
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=scenario["repo"],
        check=True,
        capture_output=True,
        text=True,
    )
    old_sha = result.stdout.strip()
    
    # Create a new commit to change HEAD
    (scenario["repo"] / "dummy.txt").write_text("dummy\n", encoding="utf-8")
    subprocess.run(["git", "add", "dummy.txt"], cwd=scenario["repo"], check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "dummy"], cwd=scenario["repo"], check=True, capture_output=True)
    
    grant = copy.deepcopy(scenario["grant"])
    grant["worktree_binding"]["head_sha"] = old_sha  # Old SHA, not current HEAD
    
    # This SHOULD ACCEPT because head_sha is not checked (KNOWN UNKNOWN C04)
    decision = _admit(scenario, grant=grant)
    assert decision.effective_runner == "codex"


# ==============================================================================
# PROBE 3: Inconsistent provider/network/credential constraints
# ==============================================================================

def test_probe_network_policy_permissive_but_not_enforced(scenario) -> None:
    """ATTACK: network_policy is permissive but never enforced."""
    grant = copy.deepcopy(scenario["grant"])
    grant["network_policy"] = {"class": "LOCAL_PROFILE"}  # Valid but permissive network policy
    
    # This SHOULD ACCEPT because network_policy is schema-validated but not enforced
    # This is a KNOWN UNKNOWN (C03) - enforcement deferred to DT-G2
    decision = _admit(scenario, grant=grant)
    assert decision.effective_runner == "codex"


def test_probe_credential_class_privileged_but_not_enforced(scenario) -> None:
    """ATTACK: credential_class is privileged but never enforced."""
    grant = copy.deepcopy(scenario["grant"])
    grant["credential_class"] = {"class": "OPERATOR_PROVIDED_OPAQUE_HANDLE", "origin_id": "test"}
    
    # This SHOULD ACCEPT because credential_class is schema-validated but not enforced
    # This is a KNOWN UNKNOWN (C03) - enforcement deferred to DT-G2
    decision = _admit(scenario, grant=grant)
    assert decision.effective_runner == "codex"


# ==============================================================================
# PROBE 4: Schema-valid GOVERNED_DELIVERY_DISPATCH issuer
# ==============================================================================

def test_probe_governed_delivery_dispatch_issuer_schema_valid_but_rejected(scenario) -> None:
    """ATTACK: GOVERNED_DELIVERY_DISPATCH is schema-valid but should be rejected."""
    grant = copy.deepcopy(scenario["grant"])
    grant["issuer"]["class"] = "GOVERNED_DELIVERY_DISPATCH"
    
    # This SHOULD reject with GRANT_ISSUER_CLASS_UNACCEPTED
    # even though GOVERNED_DELIVERY_DISPATCH is in the schema enum
    with pytest.raises(GovernedAdmissionError) as excinfo:
        _admit(scenario, grant=grant)
    assert excinfo.value.reason == "GRANT_ISSUER_CLASS_UNACCEPTED"


# ==============================================================================
# PROBE 5: Additional edge cases
# ==============================================================================

def test_probe_empty_repository_string(scenario) -> None:
    """ATTACK: grant.repository is empty string."""
    grant = copy.deepcopy(scenario["grant"])
    grant["repository"] = ""
    
    # Schema validation rejects empty string (minLength: 1)
    with pytest.raises(GovernedAdmissionError) as excinfo:
        _admit(scenario, grant=grant)
    assert excinfo.value.reason == "GRANT_SCHEMA_INVALID"


def test_probe_repository_with_trailing_slash(scenario) -> None:
    """ATTACK: grant.repository has trailing slash to bypass substring check."""
    grant = copy.deepcopy(scenario["grant"])
    grant["repository"] = "DDD-Enterprises/dopeTask/"
    
    # This SHOULD reject because trailing slash doesn't match origin URL
    with pytest.raises(GovernedAdmissionError) as excinfo:
        _admit(scenario, grant=grant)
    assert excinfo.value.reason == "GRANT_REPOSITORY_MISMATCH"


def test_probe_worktree_path_with_symlink(scenario, tmp_path: Path) -> None:
    """ATTACK: worktree_binding.path uses symlink to bypass path check."""
    # Create a symlink to the repo
    symlink_path = tmp_path / "symlink_repo"
    symlink_path.symlink_to(scenario["repo"])
    
    grant = copy.deepcopy(scenario["grant"])
    grant["worktree_binding"]["path"] = str(symlink_path)
    
    # This SHOULD ACCEPT because Path.resolve() follows symlinks
    # This is correct behavior - symlinks are transparent
    decision = _admit(scenario, grant=grant)
    assert decision.effective_runner == "codex"


def test_probe_allowlist_empty_list(scenario) -> None:
    """ATTACK: grant.allowlist is empty but packet.allowlist is not."""
    grant = copy.deepcopy(scenario["grant"])
    grant["allowlist"] = []
    
    # Schema validation may reject empty list depending on schema
    with pytest.raises(GovernedAdmissionError) as excinfo:
        _admit(scenario, grant=grant)
    # Could be GRANT_SCHEMA_INVALID or ALLOWLIST_MISMATCH depending on schema
    assert excinfo.value.reason in ["GRANT_SCHEMA_INVALID", "ALLOWLIST_MISMATCH"]


def test_probe_allowlist_none(scenario) -> None:
    """ATTACK: grant.allowlist is None."""
    grant = copy.deepcopy(scenario["grant"])
    grant["allowlist"] = None
    
    # Schema validation rejects None (type: array)
    with pytest.raises(GovernedAdmissionError) as excinfo:
        _admit(scenario, grant=grant)
    assert excinfo.value.reason == "GRANT_SCHEMA_INVALID"
