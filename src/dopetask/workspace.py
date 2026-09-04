"""Read-only workspace configuration resolver."""

from __future__ import annotations

import os
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Optional, Union

import yaml  # type: ignore[import-untyped]

WORKSPACE_FILENAME = "workspace.yaml"
DEFAULT_DAS_ENV_VAR = "DOPE_AGENT_SYSTEM_PATH"

_WORKSPACE_CONFIG_KEYS = {
    "schema_version",
    "dope_agent_system_path",
    "das_path",
    "das_path_env_override",
}
_DAS_PATH_KEYS = ("dope_agent_system_path", "das_path")


class WorkspaceConfigError(ValueError):
    """Workspace configuration cannot be parsed or normalized safely."""


def workspace_path_for_repo(repo_root: Path) -> Path:
    """Return the canonical workspace config path for a repository."""
    return repo_root.resolve() / ".dopetask" / WORKSPACE_FILENAME


def load_workspace_config(repo_root: Path) -> dict[str, Any]:
    """Load and validate optional repository workspace config."""
    config_path = workspace_path_for_repo(repo_root)
    if not config_path.exists():
        return {}

    try:
        raw = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise WorkspaceConfigError(f"{WORKSPACE_FILENAME} parse error: {exc}") from exc

    if not isinstance(raw, dict):
        raise WorkspaceConfigError(f"{WORKSPACE_FILENAME} must contain a top-level mapping")

    unknown_keys = sorted(str(key) for key in raw if key not in _WORKSPACE_CONFIG_KEYS)
    if unknown_keys:
        raise WorkspaceConfigError(
            f"{WORKSPACE_FILENAME} contains unsupported top-level keys: {', '.join(unknown_keys)}"
        )

    for key in _DAS_PATH_KEYS:
        value = raw.get(key)
        if value is not None and not isinstance(value, str):
            raise WorkspaceConfigError(f"{WORKSPACE_FILENAME} field `{key}` must be a string")

    env_override = raw.get("das_path_env_override")
    if env_override is not None:
        if not isinstance(env_override, str):
            raise WorkspaceConfigError(
                f"{WORKSPACE_FILENAME} field `das_path_env_override` must be a string"
            )
        if not env_override.strip():
            raise WorkspaceConfigError(
                f"{WORKSPACE_FILENAME} field `das_path_env_override` must not be empty"
            )

    primary_path = raw.get("dope_agent_system_path")
    alias_path = raw.get("das_path")
    if primary_path is not None and alias_path is not None and primary_path != alias_path:
        raise WorkspaceConfigError(
            f"{WORKSPACE_FILENAME} fields `dope_agent_system_path` and `das_path` conflict"
        )

    return raw


def resolve_dope_agent_system_path(
    repo_root: Path,
    *,
    explicit_path: Optional[Union[Path, str]] = None,
    env: Optional[Mapping[str, str]] = None,
) -> Optional[Path]:
    """Resolve the configured dope-agent-system path without checking existence."""
    if explicit_path is not None:
        return _normalize_path(repo_root, explicit_path)

    config = load_workspace_config(repo_root)
    env_mapping = os.environ if env is None else env
    env_var_name = config.get("das_path_env_override", DEFAULT_DAS_ENV_VAR)

    env_path = env_mapping.get(env_var_name)
    if env_path:
        return _normalize_path(repo_root, env_path)

    for key in _DAS_PATH_KEYS:
        configured_path = config.get(key)
        if configured_path:
            return _normalize_path(repo_root, configured_path)

    return None


def _normalize_path(repo_root: Path, value: Union[Path, str]) -> Path:
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = repo_root / path
    return path.resolve()
