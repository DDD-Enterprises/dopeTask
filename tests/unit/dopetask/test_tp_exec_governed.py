"""GOVERNED_MODE vs LEGACY_LOCAL_MODE isolation coverage for tp exec.

Proves build_route_plan is never imported/called on a valid GOVERNED_MODE
admission path, legacy no-model behavior is unchanged, governed admission
fails closed before adapter construction, --tmux propagates governed flags,
and --dry-run --governed evaluates admission before claiming a compiled
governed execution.
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
from typer.testing import CliRunner

from dopetask.cli import cli
from dopetask.ops.tp_exec.engine import execute_task_packet

PACKET_ID = "TP-GOVERNED-EXEC-TEST"


def _init_repo(path: Path) -> Path:
    path.mkdir()
    subprocess.run(["git", "init"], cwd=path, check=True, capture_output=True, text=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"], cwd=path, check=True, capture_output=True, text=True
    )
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=path, check=True, capture_output=True, text=True)
    subprocess.run(
        ["git", "remote", "add", "origin", "git@github.com:DDD-Enterprises/dopeTask.git"],
        cwd=path,
        check=True,
        capture_output=True,
        text=True,
    )
    (path / ".dopetaskroot").write_text("", encoding="utf-8")
    (path / ".dopetask").mkdir(parents=True, exist_ok=True)
    (path / ".dopetask" / "project.json").write_text(
        json.dumps({"project_id": "dopetask"}, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    return path


def _write_json_packet(
    path: Path,
    *,
    packet_id: str = PACKET_ID,
    allowlist: list[str],
    expected_files: list[str] | None = None,
    validation: list[str] | None = None,
    commands: list[str] | None = None,
) -> Path:
    payload = {
        "id": packet_id,
        "target": "governed execution",
        "project": "dopetask",
        "repo_binding": {
            "project_id": "dopetask",
            "repo_marker": ".dopetaskroot",
            "require_identity_match": True,
        },
        "commit": {"message": "governed test", "allowlist": allowlist},
        "steps": [
            {
                "id": "S1",
                "task": "Create the expected file",
                "requirements": ["Use deterministic content."],
                "commands": commands or [],
                "expected_files": expected_files or [],
                "validation": validation or ["true"],
                "context_files": [],
            }
        ],
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


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
    allowlist: list[str],
    model_ceiling: str = "gpt-5.3-codex",
    issued_at: datetime | None = None,
    expires_at: datetime | None = None,
) -> dict[str, Any]:
    now = issued_at or datetime.now(timezone.utc)
    exp = expires_at or (now + timedelta(hours=1))
    return {
        "schema_version": "dopemux-macro-execution-authority-ref.v2",
        "family": "MacroExecutionAuthorityRef",
        "lineage_parent": "dopemux-macro-execution-authority-ref.v1",
        "migration_semantics": "FAMILY_SUCCESSOR_NOT_JSON_INSTANCE_BACKWARD_COMPATIBLE",
        "authority_id": "authority-test-0001",
        "issuer": {"class": "OPERATOR", "principal_ref": "operator:test"},
        "issued_at": now.isoformat().replace("+00:00", "Z"),
        "expires_at": exp.isoformat().replace("+00:00", "Z"),
        "nonce": "nonce-0001",
        "idempotency_key": "idem-0001",
        "project_id": "dopetask",
        "repository": "DDD-Enterprises/dopeTask",
        "worktree_binding": {"path": worktree_path},
        "subject": {"kind": "SINGLE_TASK_PACKET", "task_packet_id": task_packet_id, "task_packet_sha256": task_packet_sha256},
        "consumer": "dopetask",
        "allowlist": list(allowlist),
        "permitted_execution": {
            "mode": "GOVERNED_SINGLE_TP",
            "runner": "codex",
            "substitution_policy": "forbid",
            "max_attempts": 1,
            "model_ceiling": model_ceiling,
        },
        "dcp_route_authorization_digest": dcp_digest,
        "uag_profile": "none",
        "network_policy": {"class": "DENIED"},
        "credential_class": {"class": "RUNNER_HOST_DEFAULT", "origin_id": "test"},
        "repair": {"attempts_per_subject_max": 0, "successor_grant_required_for_repair": False},
        "git_control": {
            "worktree_provisioning_allowed": False,
            "branch_provisioning_allowed": False,
            "push_allowed": False,
            "pr_mutation_allowed": False,
        },
        "workflow": {"mode": "NONE", "to_mutation_allowed": False},
        "authority_effect": {
            "grants": ["TASK_PACKET_MUTATION_WITHIN_ALLOWLIST", "RUNNER_INVOCATION"],
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


def _write_governed_fixture(repo: Path, *, allowlist: list[str], packet_path: Path) -> tuple[Path, Path]:
    dcp = _valid_dcp_route_authorization()
    dcp_path = repo / "dcp_route_authorization.json"
    dcp_path.write_text(json.dumps(dcp, indent=2) + "\n", encoding="utf-8")
    dcp_digest = hashlib.sha256(dcp_path.read_bytes()).hexdigest()

    grant = _valid_grant(
        task_packet_id=PACKET_ID,
        task_packet_sha256=hashlib.sha256(packet_path.read_bytes()).hexdigest(),
        dcp_digest=dcp_digest,
        worktree_path=str(repo.resolve()),
        allowlist=allowlist,
    )
    grant_path = repo / "grant.json"
    grant_path.write_text(json.dumps(grant, indent=2) + "\n", encoding="utf-8")
    return grant_path, dcp_path


def _fake_codex_run(repo: Path):
    original_run = subprocess.run

    def fake_run(argv, *args, **kwargs):
        if isinstance(argv, list) and argv[:2] == ["codex", "exec"]:
            output_index = argv.index("-o") + 1
            Path(argv[output_index]).write_text("codex output\n", encoding="utf-8")
            (repo / "generated.txt").write_text("ok\n", encoding="utf-8")
            return subprocess.CompletedProcess(argv, 0, "codex ok\n", "")
        return original_run(argv, *args, **kwargs)

    return fake_run


def test_governed_mode_never_calls_build_route_plan(monkeypatch, tmp_path: Path) -> None:
    repo = _init_repo(tmp_path / "repo")
    allowlist = ["generated.txt"]
    packet = _write_json_packet(
        repo / "packet.json", allowlist=allowlist, expected_files=["generated.txt"], validation=["test -f generated.txt"]
    )
    grant_path, dcp_path = _write_governed_fixture(repo, allowlist=allowlist, packet_path=packet)

    def _raise(**_: Any) -> Any:
        raise AssertionError("build_route_plan must never be called in GOVERNED_MODE")

    monkeypatch.setattr("dopetask.router.planner.build_route_plan", _raise)
    monkeypatch.setattr("dopetask_adapters.codex.executor.subprocess.run", _fake_codex_run(repo))

    bundle_path = execute_task_packet(
        packet,
        agent="codex",
        working_dir=repo,
        governed=True,
        grant_path=grant_path,
        dcp_route_authorization_path=dcp_path,
    )

    proof = json.loads((repo / "proof" / f"{PACKET_ID}_PROOF.json").read_text(encoding="utf-8"))
    assert proof["effective_model"] == "gpt-5.3-codex"
    bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
    assert bundle["status"] == "VALIDATED"


def test_legacy_mode_still_calls_planner_when_no_model(monkeypatch, tmp_path: Path) -> None:
    repo = _init_repo(tmp_path / "repo")
    packet = _write_json_packet(
        repo / "packet.json",
        allowlist=["generated.txt"],
        expected_files=["generated.txt"],
        validation=["test -f generated.txt"],
    )
    calls: list[str] = []

    def spy_build_route_plan(**kwargs: Any):
        calls.append("called")
        from types import SimpleNamespace

        return SimpleNamespace(status="ok", steps=(SimpleNamespace(model="gpt-5.3-codex"),))

    monkeypatch.setattr("dopetask.router.planner.build_route_plan", spy_build_route_plan)
    monkeypatch.setattr("dopetask_adapters.codex.executor.subprocess.run", _fake_codex_run(repo))

    execute_task_packet(packet, agent="codex", working_dir=repo)

    assert calls == ["called"], "legacy no-model path must still consult build_route_plan"


def test_governed_missing_grant_and_auth_rejects_before_adapter(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path / "repo")
    packet = _write_json_packet(repo / "packet.json", allowlist=["generated.txt"])

    with pytest.raises(RuntimeError, match="requires both --grant and --dcp-route-authorization"):
        execute_task_packet(packet, agent="codex", working_dir=repo, governed=True)

    assert not (repo / "generated.txt").exists(), "adapter must never run when governed admission is missing paths"


def test_governed_cli_agent_runner_mismatch_rejects_before_adapter(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path / "repo")
    allowlist = ["generated.txt"]
    packet = _write_json_packet(repo / "packet.json", allowlist=allowlist)
    grant_path, dcp_path = _write_governed_fixture(repo, allowlist=allowlist, packet_path=packet)

    from dopetask.guard.governed_execution import GovernedAdmissionError

    with pytest.raises(GovernedAdmissionError, match="CLI_AGENT_RUNNER_MISMATCH"):
        execute_task_packet(
            packet,
            agent="gemini",
            working_dir=repo,
            governed=True,
            grant_path=grant_path,
            dcp_route_authorization_path=dcp_path,
        )

    assert not (repo / "generated.txt").exists(), "adapter must never run on a runner mismatch"


def test_governed_cli_model_override_rejects(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path / "repo")
    allowlist = ["generated.txt"]
    packet = _write_json_packet(repo / "packet.json", allowlist=allowlist)
    grant_path, dcp_path = _write_governed_fixture(repo, allowlist=allowlist, packet_path=packet)

    from dopetask.guard.governed_execution import GovernedAdmissionError

    with pytest.raises(GovernedAdmissionError, match="CLI_MODEL_MISMATCH_GRANT_CEILING"):
        execute_task_packet(
            packet,
            agent="codex",
            model="some-unlisted-model",
            working_dir=repo,
            governed=True,
            grant_path=grant_path,
            dcp_route_authorization_path=dcp_path,
        )


def test_tmux_command_preserves_governed_parameters(monkeypatch, tmp_path: Path) -> None:
    repo = _init_repo(tmp_path / "repo")
    allowlist = ["generated.txt"]
    packet = _write_json_packet(repo / "packet.json", allowlist=allowlist)
    grant_path, dcp_path = _write_governed_fixture(repo, allowlist=allowlist, packet_path=packet)

    captured: dict[str, object] = {}

    class FakeTmuxManager:
        def start_session(self, session_name: str, cwd: Path, cmd: str) -> bool:
            captured["session_name"] = session_name
            captured["cmd"] = cmd
            return True

    monkeypatch.setattr("dopetask.ops.tp_exec.cli.TmuxManager", FakeTmuxManager)
    monkeypatch.chdir(repo)

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "tp",
            "exec",
            str(packet),
            "--agent",
            "codex",
            "--tmux",
            "--governed",
            "--grant",
            str(grant_path),
            "--dcp-route-authorization",
            str(dcp_path),
        ],
    )

    assert result.exit_code == 0, result.stdout
    cmd = captured["cmd"]
    assert "--governed" in cmd
    assert f"--grant {grant_path.resolve()}" in cmd or str(grant_path.resolve()) in cmd
    assert str(dcp_path.resolve()) in cmd


def test_dry_run_governed_fails_closed_on_expired_grant(monkeypatch, tmp_path: Path) -> None:
    repo = _init_repo(tmp_path / "repo")
    allowlist = ["generated.txt"]
    packet = _write_json_packet(repo / "packet.json", allowlist=allowlist)
    grant_path, dcp_path = _write_governed_fixture(repo, allowlist=allowlist, packet_path=packet)

    grant = json.loads(grant_path.read_text(encoding="utf-8"))
    expired_grant = copy.deepcopy(grant)
    now = datetime.now(timezone.utc)
    expired_grant["issued_at"] = (now - timedelta(hours=2)).isoformat().replace("+00:00", "Z")
    expired_grant["expires_at"] = (now - timedelta(hours=1)).isoformat().replace("+00:00", "Z")
    grant_path.write_text(json.dumps(expired_grant, indent=2) + "\n", encoding="utf-8")

    monkeypatch.chdir(repo)
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "tp",
            "exec",
            str(packet),
            "--agent",
            "codex",
            "--dry-run",
            "--governed",
            "--grant",
            str(grant_path),
            "--dcp-route-authorization",
            str(dcp_path),
        ],
    )

    assert result.exit_code == 1
    assert "Compiled Profile" not in result.output
    assert "GRANT_EXPIRED" in result.output


def test_dry_run_governed_valid_grant_succeeds(monkeypatch, tmp_path: Path) -> None:
    repo = _init_repo(tmp_path / "repo")
    allowlist = ["generated.txt"]
    packet = _write_json_packet(repo / "packet.json", allowlist=allowlist)
    grant_path, dcp_path = _write_governed_fixture(repo, allowlist=allowlist, packet_path=packet)

    monkeypatch.chdir(repo)
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "tp",
            "exec",
            str(packet),
            "--agent",
            "codex",
            "--dry-run",
            "--governed",
            "--grant",
            str(grant_path),
            "--dcp-route-authorization",
            str(dcp_path),
        ],
    )

    assert result.exit_code == 0, result.stdout
    assert "Compiled Profile" in result.stdout


# ---------------------------------------------------------------------------
# R2 -- the governed refusal contract at the REAL public entrypoints.
#
# The previous repair guarded `_read_raw_bytes` inside the admission guard,
# which was correct but unreachable: `TPParser.parse_file` ran first in both
# `execute_task_packet` and the CLI, so a raw OSError still escaped. Tests that
# call `admit_governed_execution` directly cannot detect that. These drive the
# public entrypoints instead.
# ---------------------------------------------------------------------------


def test_engine_governed_missing_packet_refuses_as_governed_error(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path / "repo")
    allowlist = ["generated.txt"]
    packet = _write_json_packet(repo / "packet.json", allowlist=allowlist)
    grant_path, dcp_path = _write_governed_fixture(repo, allowlist=allowlist, packet_path=packet)
    packet.unlink()

    from dopetask.guard.governed_execution import GovernedAdmissionError

    with pytest.raises(GovernedAdmissionError) as excinfo:
        execute_task_packet(
            packet,
            agent="codex",
            working_dir=repo,
            governed=True,
            grant_path=grant_path,
            dcp_route_authorization_path=dcp_path,
        )
    assert excinfo.value.reason == "TASK_PACKET_UNREADABLE"


def test_engine_governed_unreadable_packet_refuses_as_governed_error(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path / "repo")
    allowlist = ["generated.txt"]
    packet = _write_json_packet(repo / "packet.json", allowlist=allowlist)
    grant_path, dcp_path = _write_governed_fixture(repo, allowlist=allowlist, packet_path=packet)
    packet.chmod(0o000)

    from dopetask.guard.governed_execution import GovernedAdmissionError

    try:
        with pytest.raises(GovernedAdmissionError) as excinfo:
            execute_task_packet(
                packet,
                agent="codex",
                working_dir=repo,
                governed=True,
                grant_path=grant_path,
                dcp_route_authorization_path=dcp_path,
            )
        assert excinfo.value.reason == "TASK_PACKET_UNREADABLE"
    finally:
        packet.chmod(0o600)


def test_engine_governed_malformed_packet_refuses_as_governed_error(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path / "repo")
    allowlist = ["generated.txt"]
    packet = _write_json_packet(repo / "packet.json", allowlist=allowlist)
    grant_path, dcp_path = _write_governed_fixture(repo, allowlist=allowlist, packet_path=packet)
    packet.write_text("{not json", encoding="utf-8")

    from dopetask.guard.governed_execution import GovernedAdmissionError

    with pytest.raises(GovernedAdmissionError) as excinfo:
        execute_task_packet(
            packet,
            agent="codex",
            working_dir=repo,
            governed=True,
            grant_path=grant_path,
            dcp_route_authorization_path=dcp_path,
        )
    assert excinfo.value.reason == "TASK_PACKET_PARSE_INVALID"


def test_legacy_malformed_packet_keeps_legacy_error(tmp_path: Path) -> None:
    """LEGACY_LOCAL_MODE behaviour is unchanged -- no governed contract there."""
    repo = _init_repo(tmp_path / "repo")
    packet = _write_json_packet(repo / "packet.json", allowlist=["generated.txt"])
    packet.write_text("{not json", encoding="utf-8")

    from dopetask.guard.governed_execution import GovernedAdmissionError

    with pytest.raises(json.JSONDecodeError) as excinfo:
        execute_task_packet(packet, agent="codex", working_dir=repo)
    assert not isinstance(excinfo.value, GovernedAdmissionError)


@pytest.mark.parametrize("dry_run", [True, False])
def test_cli_governed_malformed_packet_refuses_with_stable_reason(
    monkeypatch, tmp_path: Path, dry_run: bool
) -> None:
    repo = _init_repo(tmp_path / "repo")
    allowlist = ["generated.txt"]
    packet = _write_json_packet(repo / "packet.json", allowlist=allowlist)
    grant_path, dcp_path = _write_governed_fixture(repo, allowlist=allowlist, packet_path=packet)
    packet.write_text("{not json", encoding="utf-8")

    monkeypatch.chdir(repo)
    argv = ["tp", "exec", str(packet), "--agent", "codex"]
    if dry_run:
        argv.append("--dry-run")
    argv += ["--governed", "--grant", str(grant_path), "--dcp-route-authorization", str(dcp_path)]

    result = CliRunner().invoke(cli, argv)

    assert result.exit_code == 1
    assert "GOVERNED_MODE REFUSAL" in result.output
    assert "TASK_PACKET_PARSE_INVALID" in result.output
    assert "Compiled Profile" not in result.output


def test_cli_missing_packet_is_pre_empted_at_argument_layer(tmp_path: Path, monkeypatch) -> None:
    """`tp_file` uses click.Path(exists=True), which also implies readable=True.

    A missing (or unreadable) packet is therefore refused by the argument layer
    with exit code 2 and never reaches the read/parse contract. Recorded so the
    governed loader is not credited with a refusal Click actually produced.
    """
    repo = _init_repo(tmp_path / "repo")
    allowlist = ["generated.txt"]
    packet = _write_json_packet(repo / "packet.json", allowlist=allowlist)
    grant_path, dcp_path = _write_governed_fixture(repo, allowlist=allowlist, packet_path=packet)
    packet.unlink()

    monkeypatch.chdir(repo)
    result = CliRunner().invoke(
        cli,
        ["tp", "exec", str(packet), "--agent", "codex", "--governed",
         "--grant", str(grant_path), "--dcp-route-authorization", str(dcp_path)],
    )
    assert result.exit_code == 2


# ---------------------------------------------------------------------------
# R1 -- under-granted grants never reach a runner (operator amendment 01)
# ---------------------------------------------------------------------------


def test_undergranted_packet_never_constructs_a_runner(monkeypatch, tmp_path: Path) -> None:
    repo = _init_repo(tmp_path / "repo")
    allowlist = ["generated.txt"]
    packet = _write_json_packet(repo / "packet.json", allowlist=allowlist)
    grant_path, dcp_path = _write_governed_fixture(repo, allowlist=allowlist, packet_path=packet)

    grant = json.loads(grant_path.read_text(encoding="utf-8"))
    grant["authority_effect"]["grants"] = ["TASK_PACKET_MUTATION_WITHIN_ALLOWLIST"]
    grant_path.write_text(json.dumps(grant, indent=2) + "\n", encoding="utf-8")

    constructed: list[str] = []

    def spy_task_executor(*args: Any, **kwargs: Any):
        constructed.append("TaskExecutor")
        raise AssertionError("runner must never be constructed on an under-granted grant")

    monkeypatch.setattr("dopetask.ops.tp_exec.engine.TaskExecutor", spy_task_executor)

    from dopetask.guard.governed_execution import GovernedAdmissionError

    with pytest.raises(GovernedAdmissionError) as excinfo:
        execute_task_packet(
            packet,
            agent="codex",
            working_dir=repo,
            governed=True,
            grant_path=grant_path,
            dcp_route_authorization_path=dcp_path,
        )
    assert excinfo.value.reason == "AUTHORITY_UNDERGRANT_RUNNER_INVOCATION"
    assert constructed == []
    assert not (repo / "generated.txt").exists()


def test_undergranted_dry_run_refuses_identically(monkeypatch, tmp_path: Path) -> None:
    """Dry-run and real execution deliberately share one admission contract."""
    repo = _init_repo(tmp_path / "repo")
    allowlist = ["generated.txt"]
    packet = _write_json_packet(repo / "packet.json", allowlist=allowlist)
    grant_path, dcp_path = _write_governed_fixture(repo, allowlist=allowlist, packet_path=packet)

    grant = json.loads(grant_path.read_text(encoding="utf-8"))
    grant["authority_effect"]["grants"] = ["TASK_PACKET_MUTATION_WITHIN_ALLOWLIST"]
    grant_path.write_text(json.dumps(grant, indent=2) + "\n", encoding="utf-8")

    monkeypatch.chdir(repo)
    result = CliRunner().invoke(
        cli,
        ["tp", "exec", str(packet), "--agent", "codex", "--dry-run", "--governed",
         "--grant", str(grant_path), "--dcp-route-authorization", str(dcp_path)],
    )
    assert result.exit_code == 1
    assert "AUTHORITY_UNDERGRANT_RUNNER_INVOCATION" in result.output
    assert "Compiled Profile" not in result.output


# ---------------------------------------------------------------------------
# R3 -- exactly one authoritative resolution per governed entrypoint
# ---------------------------------------------------------------------------


def _install_resolution_counters(monkeypatch) -> dict[str, int]:
    """Count each authoritative resolution in the namespace where it is CALLED.

    `canonical_repository_identity` is deliberately not counted: it runs twice
    per admission by design, once for the grant and once for the origin URL.
    Two calls on two different inputs is not duplicated resolution.
    """
    import dopetask.guard.governed_execution as guard_mod
    import dopetask.ops.tp_exec.engine as engine_mod
    import dopetask.ops.tp_git.guards as git_guards

    counts: dict[str, int] = {}

    def wrap(mod: Any, attr: str) -> None:
        original = getattr(mod, attr)

        def counted(*args: Any, **kwargs: Any):
            counts[attr] = counts.get(attr, 0) + 1
            return original(*args, **kwargs)

        monkeypatch.setattr(mod, attr, counted)

    wrap(engine_mod, "load_repo_identity")
    wrap(engine_mod, "assert_repo_identity")
    wrap(engine_mod, "assert_repo_binding")
    wrap(git_guards, "resolve_repo_root")
    wrap(guard_mod, "extract_origin_url")
    return counts


_SINGLE = ("load_repo_identity", "assert_repo_identity", "assert_repo_binding", "extract_origin_url")


def test_real_governed_execution_resolves_exactly_once(monkeypatch, tmp_path: Path) -> None:
    repo = _init_repo(tmp_path / "repo")
    allowlist = ["generated.txt"]
    packet = _write_json_packet(
        repo / "packet.json", allowlist=allowlist, expected_files=["generated.txt"],
        validation=["test -f generated.txt"],
    )
    grant_path, dcp_path = _write_governed_fixture(repo, allowlist=allowlist, packet_path=packet)
    monkeypatch.setattr("dopetask_adapters.codex.executor.subprocess.run", _fake_codex_run(repo))
    counts = _install_resolution_counters(monkeypatch)

    execute_task_packet(
        packet, agent="codex", working_dir=repo, governed=True,
        grant_path=grant_path, dcp_route_authorization_path=dcp_path,
    )

    for name in _SINGLE:
        assert counts.get(name) == 1, f"{name} ran {counts.get(name)} times, expected exactly 1: {counts}"


def test_governed_dry_run_resolves_exactly_once(monkeypatch, tmp_path: Path) -> None:
    repo = _init_repo(tmp_path / "repo")
    allowlist = ["generated.txt"]
    packet = _write_json_packet(repo / "packet.json", allowlist=allowlist)
    grant_path, dcp_path = _write_governed_fixture(repo, allowlist=allowlist, packet_path=packet)
    monkeypatch.chdir(repo)
    counts = _install_resolution_counters(monkeypatch)

    result = CliRunner().invoke(
        cli,
        ["tp", "exec", str(packet), "--agent", "codex", "--dry-run", "--governed",
         "--grant", str(grant_path), "--dcp-route-authorization", str(dcp_path)],
    )

    assert result.exit_code == 0, result.output
    for name in _SINGLE:
        assert counts.get(name) == 1, f"{name} ran {counts.get(name)} times, expected exactly 1: {counts}"


def test_legacy_path_never_calls_the_governed_resolver(monkeypatch, tmp_path: Path) -> None:
    repo = _init_repo(tmp_path / "repo")
    packet = _write_json_packet(
        repo / "packet.json", allowlist=["generated.txt"], expected_files=["generated.txt"],
        validation=["test -f generated.txt"],
    )
    calls: list[str] = []
    monkeypatch.setattr(
        "dopetask.ops.tp_exec.engine.resolve_governed_admission",
        lambda *a, **k: calls.append("resolve"),
    )
    monkeypatch.setattr(
        "dopetask.guard.governed_execution.admit_governed_execution",
        lambda *a, **k: calls.append("admit"),
    )
    monkeypatch.setattr("dopetask_adapters.codex.executor.subprocess.run", _fake_codex_run(repo))

    execute_task_packet(packet, agent="codex", working_dir=repo)

    assert calls == []
