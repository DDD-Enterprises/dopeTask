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
from dopetask_adapters.gemini.executor import GeminiExecutor


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

    with _pushd(working_dir):
        tp = TPParser.parse_file(resolved_tp_file)
        compiled_tp = TPNormalizer.compile(tp, agent)

        if agent == "gemini":
            executor = GeminiExecutor()
        else:
            raise ValueError(f"Agent profile '{agent}' not yet fully implemented in executor.")

        raw_proof_path = Path(executor.run_tp(compiled_tp)).resolve()
        aggregator = ProofAggregator(tp.id)

        with raw_proof_path.open(encoding="utf-8") as handle:
            execution_result = json.load(handle)

        artifact_files = [raw_proof_path, resolved_tp_file]
        for step in execution_result.get("steps", []):
            for created_file in step.get("files_created", []):
                artifact_files.append(Path(created_file))

        return aggregator.aggregate(execution_result, artifact_files).resolve()
