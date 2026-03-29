"""Reusable execution engine for JSON Task Packets."""

from __future__ import annotations

import contextlib
import json
import os
from collections.abc import Iterator
from pathlib import Path
from typing import Optional

from dopetask.core.tp_parser import TPNormalizer, TPParser
from dopetask.obs.proof_aggregator import ProofAggregator
from dopetask.pipeline.task_runner.executor import TaskExecutor
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
    working_dir: Optional[Path] = None,
) -> Path:
    """Parse, execute, and aggregate a JSON Task Packet."""
    resolved_tp_file = tp_file.resolve()

    from dopetask.ops.tp_git.guards import resolve_repo_root
    from dopetask.router.planner import build_route_plan

    repo_root = resolve_repo_root(working_dir or Path.cwd())

    with _pushd(working_dir):
        tp = TPParser.parse_file(resolved_tp_file)
        compiled_tp = TPNormalizer.compile(tp, agent)

        model: Optional[str] = None
        if agent == "gemini":
            # Attempt to resolve the best Gemini model via the router
            try:
                plan = build_route_plan(repo_root=repo_root, packet_path=resolved_tp_file)
                if plan.status == "ok" and plan.steps:
                    # Pick the model from the first step as the representative for the whole packet
                    model = plan.steps[0].model
                    import typer

                    if model:
                        typer.echo(f"Resolved Gemini model: [bold cyan]{model}[/bold cyan]")
            except Exception:
                # Fallback to default behavior if router fails
                pass

            adapter = GeminiAdapter(model=model)
        else:
            raise ValueError(f"Agent profile '{agent}' not yet fully implemented in executor.")

        # Kernel-side TaskExecutor handles adapter validation and fail-fast logic.
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
            for created_file in step.get("files_created", []):
                artifact_files.append(Path(created_file))

        final_bundle_path = aggregator.aggregate(execution_result, artifact_files).resolve()

        # Fail closed if any step was unsuccessful, but now the proof bundle is safely archived.
        if any(not step.get("validation_passed") for step in execution_result.get("steps", [])):
            raise RuntimeError(f"Task Packet {tp.id} failed one or more steps.")

        return final_bundle_path
