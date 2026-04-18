"""Reusable execution engine for JSON Task Packets."""

from __future__ import annotations

import contextlib
import json
import os
from collections.abc import Iterator
from pathlib import Path
from typing import Optional

from dopetask.core.tp_parser import TPNormalizer, TPParser
from dopetask.guard.identity import assert_repo_binding, assert_repo_identity, load_repo_identity
from dopetask.obs.proof_aggregator import ProofAggregator
from dopetask.pipeline.task_runner.executor import Adapter, TaskExecutor
from dopetask_adapters.codex.executor import CodexExecutor
from dopetask_adapters.gemini.executor import GeminiAdapter


@contextlib.contextmanager
def _pushd(path: Optional[Path]) -> Iterator[None]:
    """Temporarily change the working directory when requested."""
    if path is None:
        yield
        return

    previous = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(previous)


def execute_task_packet(
    tp_file: Path,
    *,
    agent: str = "gemini",
    model: Optional[str] = None,
    working_dir: Optional[Path] = None,
) -> Path:
    """Parse, execute, and aggregate a JSON Task Packet."""
    resolved_tp_file = tp_file.resolve()

    from dopetask.ops.tp_git.guards import resolve_repo_root

    repo_root = resolve_repo_root(working_dir or Path.cwd())
    repo_identity = load_repo_identity(repo_root)

    with _pushd(working_dir):
        tp = TPParser.parse_file(resolved_tp_file)
        assert_repo_identity(repo_root)
        assert_repo_binding(repo_identity, repo_root, tp.repo_binding)
        if tp.execution is not None and tp.execution.agent != agent:
            raise RuntimeError(
                f"Task Packet execution.agent '{tp.execution.agent}' does not match selected agent '{agent}'."
            )
        compiled_tp = TPNormalizer.compile(tp, agent)

        effective_model, effective_model_source = _resolve_effective_model(
            repo_root=repo_root,
            packet_path=resolved_tp_file,
            requested_model=model,
        )

        adapter: Adapter
        if agent == "gemini":
            adapter = GeminiAdapter(
                model=effective_model,
                requested_model=model,
                effective_model_source=effective_model_source,
            )
        elif agent == "codex":
            adapter = CodexExecutor(
                model=effective_model,
                requested_model=model,
                effective_model_source=effective_model_source,
            )
        else:
            raise ValueError(f"Agent profile '{agent}' not yet fully implemented in executor.")

        # Kernel-side TaskExecutor validates adapter output shape.
        kernel_executor = TaskExecutor(adapter)

        # Transitional Phase 1: Unpack the new ExecutionResult stream while
        # still using the legacy_proof_path for backward compatibility.
        results, raw_proof_path_str = kernel_executor.execute(compiled_tp)
        raw_proof_path = Path(raw_proof_path_str).resolve()

        aggregator = ProofAggregator(tp.id)

        with raw_proof_path.open(encoding="utf-8") as handle:
            execution_result = json.load(handle)

        trace_log_path = raw_proof_path.parent / f"{tp.id}_TRACE.log"
        artifact_files = [raw_proof_path, resolved_tp_file]
        if trace_log_path.exists():
            artifact_files.append(trace_log_path)

        for step in execution_result.get("steps", []):
            for key in ("files_created", "changed_files"):
                for path_str in step.get(key, []):
                    candidate = Path(path_str)
                    if candidate.exists():
                        artifact_files.append(candidate.resolve())

        final_bundle_path = aggregator.aggregate(execution_result, artifact_files).resolve()

        # Fail closed if any step was unsuccessful, but now the proof bundle is safely archived.
        if any(not step.get("validation_passed") for step in execution_result.get("steps", [])):
            raise RuntimeError(f"Task Packet {tp.id} failed one or more steps.")

        return final_bundle_path


def _resolve_effective_model(
    *,
    repo_root: Path,
    packet_path: Path,
    requested_model: Optional[str],
) -> tuple[Optional[str], str]:
    if requested_model:
        return requested_model, "explicit_override"

    try:
        from dopetask.router.planner import build_route_plan

        plan = build_route_plan(repo_root=repo_root, packet_path=packet_path)
        if plan.status == "ok" and plan.steps and plan.steps[0].model:
            return plan.steps[0].model, "route_plan"
    except Exception:
        pass

    return None, "agent_default"
