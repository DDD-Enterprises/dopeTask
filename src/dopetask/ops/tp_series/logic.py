"""DAG-aware JSON Task Packet series orchestration."""

from __future__ import annotations

import fcntl
import fnmatch
import json
import shutil
import subprocess
import sys
from collections.abc import Iterator
from contextlib import contextmanager, suppress
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional, cast

from dopetask.core.schema import TaskPacket
from dopetask.core.tp_parser import TPParser
from dopetask.ops.tp_exec.engine import execute_task_packet
from dopetask.ops.tp_git.exec import run_command, run_git
from dopetask.ops.tp_git.guards import resolve_repo_root
from dopetask.ops.tp_git.naming import build_tp_branch, build_worktree_path, normalize_slug

STATE_FILENAME = "SERIES_STATE.json"
PR_FILENAME = "SERIES_PR.json"
CONTEXT_FILENAME = "SERIES_CONTEXT.json"


@dataclass(frozen=True)
class SeriesExecResult:
    """Outcome envelope for `dopetask tp series exec`."""

    repo_root: Path
    series_id: str
    tp_id: str
    branch: str
    worktree_path: Path
    run_dir: Path
    proof_bundle: Optional[Path]
    message: str


@dataclass(frozen=True)
class SeriesImportResult:
    """Outcome envelope for `dopetask tp series import`."""

    repo_root: Path
    series_id: str
    tp_id: str
    packet_path: Path
    validation: str
    message: str


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _series_dir(repo_root: Path, series_id: str) -> Path:
    return (repo_root / "out" / "tp_series" / series_id).resolve()


def _packet_run_dir(series_dir: Path, tp_id: str) -> Path:
    return (series_dir / "packets" / tp_id).resolve()


def _state_path(series_dir: Path) -> Path:
    return series_dir / STATE_FILENAME


def _pr_path(series_dir: Path) -> Path:
    return series_dir / PR_FILENAME


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"{json.dumps(payload, indent=2, sort_keys=True)}\n", encoding="utf-8")


def _read_json(path: Path) -> dict[str, Any]:
    return cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))


def _default_state(*, series_id: str, base_branch: str) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "series_id": series_id,
        "base_branch": base_branch,
        "created_at": _timestamp(),
        "updated_at": _timestamp(),
        "packets": {},
        "pr": None,
    }


@contextmanager
def _worktree_context(
    *, repo_root: Path, branch: str, worktree_path: Path, base_ref: str, force_cleanup: bool = False
) -> Iterator[None]:
    """Deterministic lifecycle for TP worktrees."""
    _start_worktree(
        repo_root=repo_root, branch=branch, worktree_path=worktree_path, base_ref=base_ref, force_cleanup=force_cleanup
    )
    try:
        yield
    finally:
        with suppress(Exception):
            _remove_worktree(repo_root=repo_root, worktree_path=worktree_path)


@contextmanager
def _locked_state(series_dir: Path) -> Iterator[tuple[dict[str, Any], Path]]:
    """Load and persist state under an exclusive file lock."""
    series_dir.mkdir(parents=True, exist_ok=True)
    lock_path = series_dir / ".state.lock"
    with lock_path.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        state_path = _state_path(series_dir)
        state = _read_json(state_path) if state_path.exists() else {}
        try:
            yield state, state_path
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def _status_summary(state: dict[str, Any]) -> dict[str, int]:
    counts = {"running": 0, "completed": 0, "failed": 0}
    for packet in state.get("packets", {}).values():
        status = str(packet.get("status", ""))
        if status in counts:
            counts[status] += 1
    return counts


def _relative_to_repo(repo_root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def _parse_status_paths(status_output: str) -> list[str]:
    """Parse NUL-terminated porcelain v1 output.

    Format: XY PATH\0 [PATH2\0]
    PATH2 is only present for Renames (R) and Copies (C).
    """
    changed: list[str] = []
    items = iter(status_output.split("\0"))
    for raw_item in items:
        if not raw_item:
            continue

        status_code = raw_item[:2]
        path_fragment = raw_item[3:]

        # If it's a rename (R) or copy (C), the next item is the destination path
        if "R" in status_code or "C" in status_code:
            try:
                dest_path = next(items)
                changed.append(dest_path)
            except StopIteration:
                # Should not happen with valid git output
                changed.append(path_fragment)
        else:
            changed.append(path_fragment)

    return changed


def _run_series_doctor(*, repo_root: Path) -> None:
    """Fail closed on dirty main while allowing series-owned artifacts."""
    branch_result = run_git(["symbolic-ref", "--quiet", "--short", "HEAD"], repo_root=repo_root, check=False)
    if branch_result.returncode != 0:
        raise RuntimeError(
            "doctor failed: detached HEAD state; check out main and create an initial commit before running "
            "tp series exec"
        )

    branch = branch_result.stdout.strip()
    if not branch:
        raise RuntimeError("doctor failed: unable to determine current branch")

    if branch != "main":
        raise RuntimeError(f"doctor failed: expected branch main, found {branch}")

    head_result = run_git(["rev-parse", "--verify", "HEAD"], repo_root=repo_root, check=False)
    if head_result.returncode != 0:
        raise RuntimeError(
            "doctor failed: repository has no commits yet; create an initial commit on main and push it with "
            "`git push -u origin main` before running tp series exec"
        )

    status_output = run_git(["status", "--porcelain", "-z"], repo_root=repo_root).stdout
    ignored_prefixes = ("out/", ".worktrees/")
    dirty_paths = [
        path
        for path in _parse_status_paths(status_output)
        if not path.startswith(ignored_prefixes)
    ]
    if dirty_paths:
        raise RuntimeError("doctor failed: main has uncommitted changes (git status --porcelain is non-empty)")

    stash_list = run_git(["stash", "list"], repo_root=repo_root).stdout
    if stash_list.strip():
        raise RuntimeError("doctor failed: git stash list is non-empty; stash workflow is forbidden")

    origin_main = run_git(
        ["show-ref", "--verify", "--quiet", "refs/remotes/origin/main"],
        repo_root=repo_root,
        check=False,
    )
    if origin_main.returncode == 0:
        run_git(["fetch", "--all", "--prune"], repo_root=repo_root)
        run_git(["pull", "--ff-only"], repo_root=repo_root)


def _root_packet_base_ref(*, repo_root: Path, base_branch: str) -> str:
    origin_main = run_git(
        ["show-ref", "--verify", "--quiet", f"refs/remotes/origin/{base_branch}"],
        repo_root=repo_root,
        check=False,
    )
    if origin_main.returncode == 0:
        return f"origin/{base_branch}"
    return base_branch


def _matches_allowlist(path: str, allowlist: list[str]) -> bool:
    return any(fnmatch.fnmatchcase(path, pattern) for pattern in allowlist)


def _run_shell_commands(commands: list[str], *, cwd: Path) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for command in commands:
        completed = subprocess.run(
            command,
            cwd=cwd,
            shell=True,
            capture_output=True,
            text=True,
            check=False,
        )
        payload = {
            "command": command,
            "returncode": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }
        results.append(payload)
        if completed.returncode != 0:
            raise RuntimeError(f"verify failed ({completed.returncode}): {command}")
    return results


def _cleanup_generated_files(worktree_path: Path) -> None:
    proof_dir = worktree_path / "proof"
    if proof_dir.exists():
        shutil.rmtree(proof_dir)
    context_path = worktree_path / ".dopetask" / CONTEXT_FILENAME
    if context_path.exists():
        context_path.unlink()
    dopetask_dir = context_path.parent
    if dopetask_dir.exists() and not any(dopetask_dir.iterdir()):
        dopetask_dir.rmdir()


def _copy_proof_artifacts(*, worktree_path: Path, run_dir: Path) -> Optional[Path]:
    proof_dir = worktree_path / "proof"
    if not proof_dir.exists():
        return None

    run_dir.mkdir(parents=True, exist_ok=True)
    copied_bundle: Optional[Path] = None
    for item in sorted(proof_dir.iterdir(), key=lambda entry: entry.name):
        if item.is_file():
            destination = run_dir / item.name
            shutil.copy2(item, destination)
            if item.name.endswith("_PROOF_BUNDLE.json"):
                copied_bundle = destination.resolve()
    return copied_bundle


def _ensure_series_packet(tp: TaskPacket) -> None:
    if tp.series is None:
        raise ValueError("tp series exec requires packet.series metadata")
    if tp.commit is None:
        raise ValueError("tp series exec requires packet.commit metadata")
    if not tp.commit.allowlist:
        raise ValueError("tp series exec requires packet.commit.allowlist to be non-empty")
    if tp.id in tp.depends_on:
        raise ValueError("packet.depends_on must not include the packet id itself")
    if tp.series.parent_tp_id is None and tp.depends_on:
        raise ValueError("series.parent_tp_id must be null only for root packets")
    if tp.series.parent_tp_id is not None and tp.series.parent_tp_id not in tp.depends_on:
        raise ValueError("series.parent_tp_id must also be present in depends_on")


def _ensure_series_import_packet(tp: TaskPacket) -> None:
    try:
        _ensure_series_packet(tp)
    except ValueError as exc:
        message = str(exc)
        if message == "tp series exec requires packet.series metadata":
            raise ValueError("tp series import requires packet.series metadata") from exc
        if message == "tp series exec requires packet.commit metadata":
            raise ValueError("tp series import requires packet.commit metadata") from exc
        if message == "tp series exec requires packet.commit.allowlist to be non-empty":
            raise ValueError("tp series import requires packet.commit.allowlist to be non-empty") from exc
        raise


def _validate_series_import_state(*, repo_root: Path, tp: TaskPacket, overwrite: bool = False) -> None:
    assert tp.series is not None
    state_path = _state_path(_series_dir(repo_root, tp.series.id))
    if not state_path.exists():
        return

    state = _read_json(state_path)
    if state.get("series_id") != tp.series.id:
        raise RuntimeError(f"series import failed: expected series_id {tp.series.id}, found {state.get('series_id')}")
    if state.get("base_branch") != tp.series.base_branch:
        raise RuntimeError(
            "series import failed: series base branch mismatch: "
            f"expected {state.get('base_branch')}, got {tp.series.base_branch}"
        )

    packets = state.get("packets", {})
    if tp.id in packets and not overwrite:
        raise RuntimeError(f"series import failed: packet already recorded in state: {tp.id}")


def _clipboard_backend_command(backend: str) -> list[str]:
    if backend == "pbpaste":
        return ["pbpaste"]
    if backend == "wl-paste":
        return ["wl-paste", "--no-newline"]
    if backend == "xclip":
        return ["xclip", "-selection", "clipboard", "-o"]
    if backend == "xsel":
        return ["xsel", "--clipboard", "--output"]
    raise RuntimeError(f"series import failed: unsupported clipboard backend: {backend}")


def _clipboard_install_hint(backend: str) -> str:
    if backend == "pbpaste":
        return "pbpaste is required on macOS"
    if backend == "wl-paste":
        return "install wl-clipboard to provide wl-paste"
    if backend == "xclip":
        return "install xclip to read the X11 clipboard"
    if backend == "xsel":
        return "install xsel to read the X11 clipboard"
    return f"install clipboard support for backend {backend}"


def _auto_clipboard_backends() -> list[str]:
    if sys.platform == "darwin":
        return ["pbpaste"]
    if sys.platform.startswith("linux"):
        return ["wl-paste", "xclip", "xsel"]
    raise RuntimeError(f"series import failed: unsupported platform for clipboard auto mode: {sys.platform}")


def _read_clipboard(*, backend: str) -> str:
    backends = _auto_clipboard_backends() if backend == "auto" else [backend]
    missing: list[str] = []
    last_error: Optional[str] = None

    for candidate in backends:
        command = _clipboard_backend_command(candidate)
        try:
            completed = subprocess.run(command, capture_output=True, text=True, check=False)
        except FileNotFoundError:
            missing.append(_clipboard_install_hint(candidate))
            continue

        if completed.returncode == 0:
            return completed.stdout

        detail = (completed.stderr or completed.stdout).strip()
        last_error = f"{candidate} failed: {detail or f'exit {completed.returncode}'}"

    if last_error is not None:
        raise RuntimeError(f"series import failed: unable to read clipboard: {last_error}")

    raise RuntimeError("series import failed: no supported clipboard backend available: " + "; ".join(missing))


def import_series_packet(
    *,
    out_dir: Optional[Path] = None,
    source_file: Optional[Path] = None,
    force: bool = False,
    overwrite: bool = False,
    clipboard_backend: str = "auto",
    repo: Optional[Path] = None,
) -> SeriesImportResult:
    """Import a JSON Task Packet into the current workspace.

    By default, reads from the clipboard. If source_file is provided, reads from that file instead.
    """
    repo_root = resolve_repo_root(repo)

    if source_file is not None:
        payload = json.loads(source_file.read_text(encoding="utf-8"))
    else:
        clipboard_text = _read_clipboard(backend=clipboard_backend)
        try:
            payload = json.loads(clipboard_text)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"series import failed: clipboard does not contain strict JSON: {exc}") from exc

    if not isinstance(payload, dict):
        raise RuntimeError("series import failed: JSON must be an object")

    tp = TPParser.parse_dict(payload)
    _ensure_series_import_packet(tp)
    _validate_series_import_state(repo_root=repo_root, tp=tp, overwrite=overwrite)
    assert tp.series is not None

    target_dir = (out_dir or Path.cwd()).resolve()
    target_dir.mkdir(parents=True, exist_ok=True)
    packet_path = target_dir / f"{tp.id}.json"
    if packet_path.exists() and not (force or overwrite):
        raise RuntimeError(f"series import failed: target file already exists: {packet_path}")

    packet_path.write_text(f"{json.dumps(tp.to_dict(), indent=2, sort_keys=True)}\n", encoding="utf-8")
    return SeriesImportResult(
        repo_root=repo_root,
        series_id=tp.series.id,
        tp_id=tp.id,
        packet_path=packet_path,
        validation="structural-ok",
        message=f"series packet imported: {tp.id}",
    )


def _packet_branch(tp: TaskPacket) -> str:
    return build_tp_branch(tp.id, normalize_slug(tp.target or tp.id))


def _dependency_records(state: dict[str, Any], depends_on: list[str]) -> dict[str, dict[str, Any]]:
    packets = state.get("packets", {})
    deps: dict[str, dict[str, Any]] = {}
    for dep_id in depends_on:
        dep_record = packets.get(dep_id)
        if not isinstance(dep_record, dict):
            raise RuntimeError(f"series dependency not found: {dep_id}")
        if dep_record.get("status") != "completed":
            raise RuntimeError(f"series dependency is not completed: {dep_id}")
        deps[dep_id] = dep_record
    return deps


def _write_series_context(
    *,
    repo_root: Path,
    worktree_path: Path,
    run_dir: Path,
    tp: TaskPacket,
    dependency_records: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    payload = {
        "schema_version": "1.0",
        "series_id": tp.series.id if tp.series is not None else None,
        "tp_id": tp.id,
        "parent_tp_id": tp.series.parent_tp_id if tp.series is not None else None,
        "depends_on": tp.depends_on,
        "dependencies": {
            dep_id: {
                "branch": record.get("branch"),
                "head_sha": record.get("head_sha"),
                "status": record.get("status"),
                "run_dir": record.get("run_dir"),
            }
            for dep_id, record in sorted(dependency_records.items())
        },
    }
    _write_json(run_dir / CONTEXT_FILENAME, payload)
    context_path = worktree_path / ".dopetask" / CONTEXT_FILENAME
    _write_json(context_path, payload)
    payload["worktree_context"] = _relative_to_repo(repo_root, context_path)
    return payload


def _start_worktree(
    *, repo_root: Path, branch: str, worktree_path: Path, base_ref: str, force_cleanup: bool = False
) -> None:
    if worktree_path.exists():
        if force_cleanup:
            _remove_worktree(repo_root=repo_root, worktree_path=worktree_path)
        else:
            raise RuntimeError(
                f"series exec failed: worktree already exists: {worktree_path}\n"
                f"Hint: Run `dopetask tp series cleanup --series-id <id>` or use `--force`."
            )

    existing = run_git(["show-ref", "--verify", "--quiet", f"refs/heads/{branch}"], repo_root=repo_root, check=False)
    if existing.returncode == 0:
        if force_cleanup:
            run_git(["branch", "-D", branch], repo_root=repo_root)
        else:
            raise RuntimeError(
                f"series exec failed: branch already exists: {branch}\n"
                f"Hint: Run `dopetask tp series cleanup --series-id <id>` or use `--force`."
            )

    worktree_path.parent.mkdir(parents=True, exist_ok=True)
    run_git(["worktree", "add", "-b", branch, str(worktree_path), base_ref], repo_root=repo_root)


def cleanup_series_artifacts(
    *, repo_root: Path, series_id: str, packet_id: Optional[str] = None, force: bool = False
) -> list[str]:
    """Purge stale worktrees and branches for a series."""
    series_dir = _series_dir(repo_root, series_id)
    state_path = _state_path(series_dir)
    if not state_path.exists():
        raise RuntimeError(f"cleanup failed: series state not found for {series_id}")

    state = _read_json(state_path)
    packets = state.get("packets", {})
    target_ids = [packet_id] if packet_id else list(packets.keys())

    cleaned = []
    for pid in target_ids:
        record = packets.get(pid)
        if not record:
            continue

        # Safety: do not auto-clean completed packets unless force is True
        if record.get("status") == "completed" and not force:
            continue

        branch = record.get("branch")
        worktree_path = Path(record.get("worktree_path", "")) if record.get("worktree_path") else None

        if worktree_path and worktree_path.exists():
            _remove_worktree(repo_root=repo_root, worktree_path=worktree_path)
            cleaned.append(f"worktree:{worktree_path}")

        if branch:
            existing = run_git(
                ["show-ref", "--verify", "--quiet", f"refs/heads/{branch}"], repo_root=repo_root, check=False
            )
            if existing.returncode == 0:
                run_git(["branch", "-D", branch], repo_root=repo_root)
                cleaned.append(f"branch:{branch}")

    return cleaned


def _stage_commit_changes(*, repo_root: Path, worktree_path: Path, tp: TaskPacket) -> tuple[str, list[str]]:
    assert tp.commit is not None
    status_output = run_git(
        ["-C", str(worktree_path), "status", "--porcelain", "-z", "--untracked-files=all"],
        repo_root=repo_root,
    ).stdout
    changed_files = sorted(set(_parse_status_paths(status_output)))
    if not changed_files:
        raise RuntimeError("series exec failed: packet produced no commit-eligible changes")

    disallowed = [path for path in changed_files if not _matches_allowlist(path, tp.commit.allowlist)]
    if disallowed:
        raise RuntimeError(
            "series exec failed: changes detected outside packet.commit.allowlist: "
            + ", ".join(disallowed)
        )

    run_git(["-C", str(worktree_path), "add", "--", *changed_files], repo_root=repo_root)
    run_git(["-C", str(worktree_path), "commit", "-m", tp.commit.message], repo_root=repo_root)
    head_sha = run_git(["-C", str(worktree_path), "rev-parse", "HEAD"], repo_root=repo_root).stdout.strip()
    return head_sha, changed_files


def _remove_worktree(*, repo_root: Path, worktree_path: Path) -> None:
    run_git(["worktree", "remove", "--force", str(worktree_path)], repo_root=repo_root)
    run_git(["worktree", "prune"], repo_root=repo_root)


def _mark_packet_state(
    *,
    series_dir: Path,
    packet_id: str,
    update: dict[str, Any],
) -> dict[str, Any]:
    with _locked_state(series_dir) as (state, state_path):
        packets = state.setdefault("packets", {})
        packet = packets.setdefault(packet_id, {})
        packet.update(update)
        state["updated_at"] = _timestamp()
        _write_json(state_path, state)
        return state


def exec_series_packet(
    *,
    tp_file: Path,
    agent: str = "gemini",
    force: bool = False,
    repo: Optional[Path] = None,
) -> SeriesExecResult:
    """Execute a JSON Task Packet inside a series-aware git workflow."""
    repo_root = resolve_repo_root(repo)
    _run_series_doctor(repo_root=repo_root)

    packet_path = tp_file.resolve()
    tp = TPParser.parse_file(packet_path)
    _ensure_series_packet(tp)
    assert tp.series is not None
    assert tp.commit is not None

    series_dir = _series_dir(repo_root, tp.series.id)
    run_dir = _packet_run_dir(series_dir, tp.id)
    branch = _packet_branch(tp)
    worktree_path = build_worktree_path(repo_root, tp.id)

    with _locked_state(series_dir) as (state, state_path):
        if not state:
            state = _default_state(series_id=tp.series.id, base_branch=tp.series.base_branch)
        packets = state.setdefault("packets", {})

        if state.get("series_id") != tp.series.id:
            raise RuntimeError(f"series state mismatch: expected {tp.series.id}, found {state.get('series_id')}")
        if state.get("base_branch") != tp.series.base_branch:
            raise RuntimeError(
                f"series base branch mismatch: expected {state.get('base_branch')}, got {tp.series.base_branch}"
            )

        existing_record = packets.get(tp.id)
        if isinstance(existing_record, dict) and existing_record.get("status") in {"running", "completed"} and not force:
            raise RuntimeError(f"series packet already recorded with status {existing_record.get('status')}: {tp.id}")

        dependency_records = _dependency_records(state, tp.depends_on)
        if tp.series.parent_tp_id is not None:
            parent_record = dependency_records[tp.series.parent_tp_id]
            base_ref = str(parent_record.get("branch"))
        else:
            base_ref = _root_packet_base_ref(repo_root=repo_root, base_branch=tp.series.base_branch)

        packets[tp.id] = {
            "tp_id": tp.id,
            "packet_path": str(packet_path),
            "branch": branch,
            "base_ref": base_ref,
            "depends_on": tp.depends_on,
            "parent_tp_id": tp.series.parent_tp_id,
            "final_packet": tp.series.final_packet,
            "status": "running",
            "worktree_path": str(worktree_path),
            "run_dir": str(run_dir),
            "started_at": _timestamp(),
            "updated_at": _timestamp(),
            "head_sha": None,
            "proof_bundle": None,
            "error": None,
        }
        state["updated_at"] = _timestamp()
        _write_json(state_path, state)

    dependency_records = _dependency_records(_read_json(_state_path(series_dir)), tp.depends_on)

    try:
        with _worktree_context(
            repo_root=repo_root,
            branch=branch,
            worktree_path=worktree_path,
            base_ref=base_ref,
            force_cleanup=force,
        ):
            context_payload = _write_series_context(
                repo_root=repo_root,
                worktree_path=worktree_path,
                run_dir=run_dir,
                tp=tp,
                dependency_records=dependency_records,
            )
            try:
                bundle_path = execute_task_packet(packet_path, agent=agent, working_dir=worktree_path)
            finally:
                proof_bundle = _copy_proof_artifacts(worktree_path=worktree_path, run_dir=run_dir)

            _cleanup_generated_files(worktree_path)

            verify_results = _run_shell_commands(tp.commit.verify, cwd=worktree_path)
            head_sha, committed_files = _stage_commit_changes(repo_root=repo_root, worktree_path=worktree_path, tp=tp)
            _write_json(
                run_dir / "EXEC.json",
                {
                    "schema_version": "1.0",
                    "series_id": tp.series.id,
                    "tp_id": tp.id,
                    "branch": branch,
                    "base_ref": base_ref,
                    "packet_path": str(packet_path),
                    "bundle_path": str(bundle_path),
                    "copied_proof_bundle": str(proof_bundle) if proof_bundle is not None else None,
                    "verify": verify_results,
                    "committed_files": committed_files,
                    "context": context_payload,
                    "head_sha": head_sha,
                },
            )
            _mark_packet_state(
                series_dir=series_dir,
                packet_id=tp.id,
                update={
                    "status": "completed",
                    "updated_at": _timestamp(),
                    "completed_at": _timestamp(),
                    "head_sha": head_sha,
                    "proof_bundle": str(proof_bundle) if proof_bundle is not None else None,
                    "committed_files": committed_files,
                    "error": None,
                },
            )
            return SeriesExecResult(
                repo_root=repo_root,
                series_id=tp.series.id,
                tp_id=tp.id,
                branch=branch,
                worktree_path=worktree_path,
                run_dir=run_dir,
                proof_bundle=proof_bundle,
                message=f"series packet completed: {tp.id}",
            )
    except Exception as exc:
        _write_json(
            run_dir / "EXEC_ERROR.json",
            {
                "schema_version": "1.0",
                "series_id": tp.series.id,
                "tp_id": tp.id,
                "branch": branch,
                "worktree_path": str(worktree_path),
                "error": str(exc),
            },
        )
        _mark_packet_state(
            series_dir=series_dir,
            packet_id=tp.id,
            update={
                "status": "failed",
                "updated_at": _timestamp(),
                "failed_at": _timestamp(),
                "error": str(exc),
            },
        )
        raise


def discover_next_runnable_tp(*, repo_root: Path) -> Optional[Path]:
    """Search for the next runnable JSON Task Packet in the workspace.

    It scans out/task_packets/*.json and checks SERIES_STATE.json to find
    a packet whose dependencies are met but is not yet completed/running.
    """
    packets_dir = repo_root / "out" / "task_packets"
    if not packets_dir.exists():
        return None

    # Get all candidate JSON packets
    candidates = sorted(packets_dir.glob("*.json"))
    if not candidates:
        return None

    for packet_path in candidates:
        try:
            tp = TPParser.parse_file(packet_path)
            if not tp.series:
                continue

            series_dir = _series_dir(repo_root, tp.series.id)
            state_path = _state_path(series_dir)
            if not state_path.exists():
                # If no state yet, the first packet in the series (no depends_on) is runnable
                if not tp.depends_on:
                    return packet_path
                continue

            state = _read_json(state_path)
            packets_state = state.get("packets", {})
            record = packets_state.get(tp.id)

            # If already completed or running, skip
            if record and record.get("status") in {"completed", "running"}:
                continue

            # Check if all dependencies are completed in the state
            deps_met = True
            for dep_id in tp.depends_on:
                dep_record = packets_state.get(dep_id)
                if not dep_record or dep_record.get("status") != "completed":
                    deps_met = False
                    break

            if deps_met:
                return packet_path

        except Exception:
            # Skip malformed packets during discovery
            continue

    return None


def get_series_status(*, series_id: str, repo: Optional[Path] = None) -> dict[str, Any]:
    """Return series status payload from the authoritative ledger."""
    repo_root = resolve_repo_root(repo)
    series_dir = _series_dir(repo_root, series_id)
    state_path = _state_path(series_dir)
    if not state_path.exists():
        raise RuntimeError(f"series status failed: state not found: {state_path}")
    state = _read_json(state_path)
    return {
        "repo_root": str(repo_root),
        "series_id": state.get("series_id"),
        "base_branch": state.get("base_branch"),
        "counts": _status_summary(state),
        "packets": state.get("packets", {}),
        "pr": state.get("pr"),
        "state_path": str(state_path),
    }


def _dependency_closure(state: dict[str, Any], start_tp_id: str) -> set[str]:
    packets = state.get("packets", {})
    closure: set[str] = set()
    stack = [start_tp_id]
    while stack:
        current = stack.pop()
        packet = packets.get(current)
        if not isinstance(packet, dict):
            raise RuntimeError(f"series finalize failed: packet missing from state: {current}")
        for dep in packet.get("depends_on", []):
            if dep not in closure:
                closure.add(dep)
                stack.append(dep)
    return closure


def _ensure_gh_auth(repo_root: Path) -> None:
    auth = run_command(["gh", "auth", "status"], cwd=repo_root, check=False)
    if auth.returncode != 0:
        detail = (auth.stderr or auth.stdout).strip()
        raise RuntimeError(f"gh auth failed: {detail}")


def finalize_series(
    *,
    series_id: str,
    title: str,
    body: Optional[str] = None,
    body_file: Optional[Path] = None,
    repo: Optional[Path] = None,
) -> dict[str, Any]:
    """Push the final packet branch and open a single PR for the series."""
    if body is not None and body_file is not None:
        raise RuntimeError("series finalize failed: pass either body or body_file, not both")

    repo_root = resolve_repo_root(repo)
    _run_series_doctor(repo_root=repo_root)
    series_dir = _series_dir(repo_root, series_id)

    with _locked_state(series_dir) as (state, state_path):
        if not state:
            raise RuntimeError(f"series finalize failed: no state found for {series_id}")

        packets = state.get("packets", {})
        final_packets = [packet for packet in packets.values() if packet.get("final_packet")]
        completed_final_packets = [packet for packet in final_packets if packet.get("status") == "completed"]
        if len(final_packets) != 1 or len(completed_final_packets) != 1:
            raise RuntimeError("series finalize failed: expected exactly one completed final packet")

        final_packet = completed_final_packets[0]
        final_tp_id = str(final_packet["tp_id"])
        closure = _dependency_closure(state, final_tp_id)

        for packet_id, packet in packets.items():
            if packet_id == final_tp_id:
                if packet.get("status") != "completed":
                    raise RuntimeError("series finalize failed: final packet is not completed")
                continue
            if packet_id not in closure:
                raise RuntimeError(
                    f"series finalize failed: packet {packet_id} is outside the final packet dependency closure"
                )
            if packet.get("status") != "completed":
                raise RuntimeError(
                    f"series finalize failed: dependency packet is not completed: {packet_id}"
                )

        branch = str(final_packet["branch"])
        base_branch = str(state["base_branch"])

        _ensure_gh_auth(repo_root)
        run_git(["push", "-u", "origin", branch], repo_root=repo_root)

        cmd = ["gh", "pr", "create", "--title", title, "--base", base_branch, "--head", branch]
        if body_file is not None:
            cmd.extend(["--body-file", str(body_file.resolve())])
        elif body is not None:
            cmd.extend(["--body", body])
        created = run_command(cmd, cwd=repo_root, check=False)
        detail = (created.stderr or created.stdout).strip()
        if created.returncode != 0 and "already exists" not in detail.lower():
            raise RuntimeError(f"series finalize failed: {detail}")

        viewed = run_command(
            ["gh", "pr", "view", branch, "--json", "url,state,mergeStateStatus,autoMergeRequest"],
            cwd=repo_root,
        )
        payload = json.loads(viewed.stdout)
        if not isinstance(payload, dict):
            raise RuntimeError("series finalize failed: gh pr view returned non-object JSON")

        payload.update(
            {
                "repo_root": str(repo_root),
                "series_id": series_id,
                "branch": branch,
                "base_branch": base_branch,
                "final_tp_id": final_tp_id,
            }
        )
        _write_json(_pr_path(series_dir), payload)
        state["pr"] = payload
        state["updated_at"] = _timestamp()
        _write_json(state_path, state)
        return payload
