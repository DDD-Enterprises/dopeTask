"""Codex Desktop runner adapter."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any


class CodexCliAdapter:
    """Adapter for the codex_desktop runner."""

    runner_id = "codex_desktop"

    def prepare(self, packet: dict[str, Any], route_plan: dict[str, Any]) -> dict[str, Any]:
        route_payload = route_plan.get("route_plan", route_plan)
        selected = _select_step(route_plan, self.runner_id)
        return {
            "runner_id": self.runner_id,
            "step": selected.get("step"),
            "model_id": selected.get("model"),
            "packet_id": packet.get("id") or packet.get("task_id"),
            "packet_path": route_payload.get("packet_path"),
            "repo_root": route_payload.get("repo_root"),
            "run_dir": route_payload.get("run_dir"),
        }

    def run(self, runspec: dict[str, Any]) -> dict[str, Any]:
        packet_path = str(runspec.get("packet_path") or "")
        repo_root = Path(str(runspec.get("repo_root") or ".")).resolve()
        run_dir = Path(str(runspec.get("run_dir") or ".")).resolve()
        run_dir.mkdir(parents=True, exist_ok=True)
        last_message_path = run_dir / "CODEX_LAST_MESSAGE.txt"

        prompt = "\n".join(
            [
                "You are executing a deterministic dopeTask orchestrator step.",
                f"Packet: {packet_path}",
                f"Step: {runspec.get('step')}",
                f"Model: {runspec.get('model_id') or 'default'}",
                "Make only the requested repository changes and rely on local validation/artifacts.",
            ]
        )
        command = [
            "codex",
            "exec",
            "--skip-git-repo-check",
            "--sandbox",
            "workspace-write",
            "-C",
            str(repo_root),
            "-o",
            str(last_message_path),
            "-",
        ]
        if runspec.get("model_id"):
            command[2:2] = ["--model", str(runspec["model_id"])]

        before = _git_status_paths(repo_root)
        try:
            completed = subprocess.run(
                command,
                input=prompt,
                text=True,
                capture_output=True,
                check=False,
            )
        except FileNotFoundError:
            return {
                "status": "refused",
                "reason_code": "RUNNER_UNAVAILABLE",
                "runner_id": self.runner_id,
                "step": runspec.get("step"),
                "model_id": runspec.get("model_id"),
                "outputs": [],
                "stdout_text": "",
                "stderr_text": "codex executable not found",
            }

        after = _git_status_paths(repo_root)
        mutation_detected = bool(sorted(after - before))
        stdout_text = completed.stdout
        stderr_text = completed.stderr

        if completed.returncode != 0:
            return {
                "status": "error",
                "reason_code": "RUNNER_EXEC_FAILED",
                "runner_id": self.runner_id,
                "step": runspec.get("step"),
                "model_id": runspec.get("model_id"),
                "outputs": [str(last_message_path)] if last_message_path.exists() else [],
                "stdout_text": stdout_text,
                "stderr_text": stderr_text,
            }

        if not last_message_path.exists():
            return {
                "status": "error",
                "reason_code": "RUNNER_OUTPUT_MISSING_WITH_MUTATION" if mutation_detected else "RUNNER_OUTPUT_MISSING",
                "runner_id": self.runner_id,
                "step": runspec.get("step"),
                "model_id": runspec.get("model_id"),
                "outputs": [],
                "stdout_text": stdout_text,
                "stderr_text": stderr_text,
            }

        if not last_message_path.read_text(encoding="utf-8").strip():
            return {
                "status": "error",
                "reason_code": "RUNNER_OUTPUT_EMPTY_WITH_MUTATION" if mutation_detected else "RUNNER_OUTPUT_EMPTY",
                "runner_id": self.runner_id,
                "step": runspec.get("step"),
                "model_id": runspec.get("model_id"),
                "outputs": [str(last_message_path)],
                "stdout_text": stdout_text,
                "stderr_text": stderr_text,
            }

        return {
            "status": "ok",
            "reason_code": None,
            "runner_id": self.runner_id,
            "step": runspec.get("step"),
            "model_id": runspec.get("model_id"),
            "outputs": [str(last_message_path)],
            "stdout_text": stdout_text,
            "stderr_text": stderr_text,
        }

    def normalize(self, result: dict[str, Any]) -> dict[str, Any]:
        return {
            "status": str(result.get("status", "error")),
            "reason_code": result.get("reason_code"),
            "runner_id": result.get("runner_id", self.runner_id),
            "model_id": result.get("model_id"),
            "step": result.get("step"),
            "outputs": list(result.get("outputs", [])),
            "stdout_text": result.get("stdout_text"),
            "stderr_text": result.get("stderr_text"),
        }


def _select_step(route_plan: dict[str, Any], runner_id: str) -> dict[str, Any]:
    steps = route_plan.get("steps", [])
    for item in steps:
        if isinstance(item, dict) and item.get("runner") == runner_id:
            return item
    return steps[0] if steps else {}


def _git_status_paths(repo_root: Path) -> set[str]:
    completed = subprocess.run(
        ["git", "-C", str(repo_root), "status", "--porcelain", "-z", "--untracked-files=all"],
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        return set()

    changed: set[str] = set()
    items = iter(completed.stdout.split("\0"))
    for raw_item in items:
        if not raw_item:
            continue
        status_code = raw_item[:2]
        path_fragment = raw_item[3:]
        if "R" in status_code or "C" in status_code:
            try:
                changed.add(next(items))
            except StopIteration:
                changed.add(path_fragment)
        else:
            changed.add(path_fragment)
    return changed
