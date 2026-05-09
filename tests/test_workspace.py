"""Workspace resolver tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from dopetask.workspace import (
    DEFAULT_DAS_ENV_VAR,
    WorkspaceConfigError,
    load_workspace_config,
    resolve_dope_agent_system_path,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPO_ROOT / "dopetask_schemas" / "workspace.schema.json"


def _write_workspace(repo_root: Path, text: str) -> None:
    workspace_path = repo_root / ".dopetask" / "workspace.yaml"
    workspace_path.parent.mkdir(parents=True, exist_ok=True)
    workspace_path.write_text(text, encoding="utf-8")


def test_workspace_schema_json_is_valid() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

    Draft202012Validator.check_schema(schema)


def test_missing_workspace_config_no_env_no_explicit_returns_none(tmp_path: Path) -> None:
    assert resolve_dope_agent_system_path(tmp_path, env={}) is None


def test_explicit_path_wins_over_env_and_config(tmp_path: Path) -> None:
    _write_workspace(tmp_path, "dope_agent_system_path: configured-das\n")

    result = resolve_dope_agent_system_path(
        tmp_path,
        explicit_path="explicit-das",
        env={DEFAULT_DAS_ENV_VAR: "env-das"},
    )

    assert result == (tmp_path / "explicit-das").resolve()


def test_default_env_var_wins_over_workspace_config(tmp_path: Path) -> None:
    _write_workspace(tmp_path, "dope_agent_system_path: configured-das\n")

    result = resolve_dope_agent_system_path(tmp_path, env={DEFAULT_DAS_ENV_VAR: "env-das"})

    assert result == (tmp_path / "env-das").resolve()


def test_workspace_primary_path_resolves_when_no_env_or_explicit(tmp_path: Path) -> None:
    _write_workspace(tmp_path, "dope_agent_system_path: configured-das\n")

    result = resolve_dope_agent_system_path(tmp_path, env={})

    assert result == (tmp_path / "configured-das").resolve()


def test_workspace_das_path_alias_resolves_when_primary_absent(tmp_path: Path) -> None:
    _write_workspace(tmp_path, "das_path: alias-das\n")

    result = resolve_dope_agent_system_path(tmp_path, env={})

    assert result == (tmp_path / "alias-das").resolve()


def test_relative_workspace_path_resolves_relative_to_repo_root(tmp_path: Path) -> None:
    _write_workspace(tmp_path, "dope_agent_system_path: ../das-reference\n")

    result = resolve_dope_agent_system_path(tmp_path, env={})

    assert result == (tmp_path / "../das-reference").resolve()


def test_tilde_expands(tmp_path: Path, monkeypatch) -> None:
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    monkeypatch.setenv("HOME", str(fake_home))

    result = resolve_dope_agent_system_path(tmp_path, explicit_path="~/das-reference", env={})

    assert result == (fake_home / "das-reference").resolve()


def test_custom_das_path_env_override_is_respected(tmp_path: Path) -> None:
    _write_workspace(
        tmp_path,
        "das_path_env_override: CUSTOM_DAS_PATH\n"
        "dope_agent_system_path: configured-das\n",
    )

    result = resolve_dope_agent_system_path(
        tmp_path,
        env={
            DEFAULT_DAS_ENV_VAR: "ignored-default-env-das",
            "CUSTOM_DAS_PATH": "custom-env-das",
        },
    )

    assert result == (tmp_path / "custom-env-das").resolve()


def test_conflicting_workspace_path_aliases_raise(tmp_path: Path) -> None:
    _write_workspace(
        tmp_path,
        "dope_agent_system_path: primary-das\n"
        "das_path: alias-das\n",
    )

    with pytest.raises(WorkspaceConfigError, match="conflict"):
        load_workspace_config(tmp_path)


def test_malformed_yaml_raises_workspace_config_error(tmp_path: Path) -> None:
    _write_workspace(tmp_path, "dope_agent_system_path: [unterminated\n")

    with pytest.raises(WorkspaceConfigError, match="parse error"):
        load_workspace_config(tmp_path)


def test_non_object_yaml_raises_workspace_config_error(tmp_path: Path) -> None:
    _write_workspace(tmp_path, "- not\n- a\n- mapping\n")

    with pytest.raises(WorkspaceConfigError, match="top-level mapping"):
        load_workspace_config(tmp_path)


def test_non_string_das_path_value_raises_workspace_config_error(tmp_path: Path) -> None:
    _write_workspace(tmp_path, "dope_agent_system_path: 42\n")

    with pytest.raises(WorkspaceConfigError, match="must be a string"):
        load_workspace_config(tmp_path)


def test_resolver_does_not_require_path_to_exist(tmp_path: Path) -> None:
    missing_path = tmp_path / "missing-das"

    result = resolve_dope_agent_system_path(tmp_path, explicit_path=missing_path, env={})

    assert result == missing_path.resolve()
    assert not missing_path.exists()


def test_no_workspace_cli_command_added() -> None:
    from dopetask.cli import cli

    top_level_commands = {command.name for command in cli.registered_commands}
    top_level_groups = {group.name for group in cli.registered_groups}

    assert "workspace" not in top_level_commands
    assert "workspace" not in top_level_groups


def test_workspace_source_and_tests_do_not_contain_machine_local_paths() -> None:
    checked_paths = [
        REPO_ROOT / "src" / "dopetask" / "workspace.py",
        Path(__file__),
    ]

    forbidden_prefix = "/" + "Users/"
    for path in checked_paths:
        text = path.read_text(encoding="utf-8")
        assert forbidden_prefix not in text
