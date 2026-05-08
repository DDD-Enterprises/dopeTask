"""Artifact durability classification for read-only UI status surfaces."""

from __future__ import annotations

import subprocess
import tempfile
from enum import Enum
from pathlib import Path
from typing import Any, Optional, Union


class ArtifactDurability(str, Enum):
    """Durability classes for paths rendered by UI status."""

    TRACKED_IN_GIT = "tracked-in-git"
    LOCAL_ONLY_GITIGNORED = "local-only-gitignored"
    UNTRACKED_NOT_IGNORED = "untracked-not-ignored"
    MISSING = "missing"


class PathKind(str, Enum):
    """Path locality classes for rendered artifact paths."""

    REPO_RELATIVE = "repo-relative"
    ABSOLUTE_LOCAL = "absolute-local"
    TEMP_OR_FOREIGN = "temp-or-foreign"


def classify_artifact_path(
    repo_root: Path,
    path: Optional[Union[Path, str]],
) -> dict[str, Any]:
    """Classify a path using git tracking and ignore state where possible."""

    if path is None or str(path) == "":
        return _info(None, ArtifactDurability.MISSING, PathKind.TEMP_OR_FOREIGN, exists=False)

    resolved_repo_root = repo_root.resolve()
    raw_path = Path(path)
    absolute_path = raw_path.expanduser()
    if not absolute_path.is_absolute():
        absolute_path = resolved_repo_root / absolute_path
    absolute_path = absolute_path.resolve()
    path_kind = _path_kind(resolved_repo_root, absolute_path)
    display_path = _display_path(resolved_repo_root, absolute_path)

    if not absolute_path.exists():
        return _info(display_path, ArtifactDurability.MISSING, path_kind, exists=False)

    if _git_success(["git", "ls-files", "--error-unmatch", "--", str(absolute_path)], resolved_repo_root):
        durability = ArtifactDurability.TRACKED_IN_GIT
    elif _git_success(["git", "check-ignore", "-v", "--", str(absolute_path)], resolved_repo_root):
        durability = ArtifactDurability.LOCAL_ONLY_GITIGNORED
    else:
        durability = ArtifactDurability.UNTRACKED_NOT_IGNORED

    return _info(display_path, durability, path_kind, exists=True)


def _git_success(command: list[str], cwd: Path) -> bool:
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, check=False)
    return result.returncode == 0


def _path_kind(repo_root: Path, path: Path) -> PathKind:
    try:
        path.relative_to(repo_root)
    except ValueError:
        temp_root = Path(tempfile.gettempdir()).resolve()
        try:
            path.relative_to(temp_root)
        except ValueError:
            return PathKind.ABSOLUTE_LOCAL
        return PathKind.TEMP_OR_FOREIGN
    return PathKind.REPO_RELATIVE


def _display_path(repo_root: Path, path: Path) -> str:
    try:
        return path.relative_to(repo_root).as_posix()
    except ValueError:
        return str(path)


def _info(
    path: Optional[str],
    durability: ArtifactDurability,
    path_kind: PathKind,
    *,
    exists: bool,
) -> dict[str, Any]:
    return {
        "path": path,
        "durability": durability.value,
        "path_kind": path_kind.value,
        "exists": exists,
    }
