"""Core task execution kernel."""

from __future__ import annotations

from typing import Any, Protocol

from dopetask.pipeline.task_runner.types import ExecutionResult


class Adapter(Protocol):
    """Protocol for task execution adapters (Transitional V0)."""

    def run_tp(self, tp: dict[str, Any]) -> tuple[list[ExecutionResult], str]:
        """Execute a full Task Packet and return (results, legacy_proof_path)."""


class TaskExecutor:
    """Kernel component responsible for task execution and result-shape validation."""

    def __init__(self, adapter: Adapter) -> None:
        self.adapter = adapter

    def execute(self, tp: dict[str, Any]) -> tuple[list[ExecutionResult], str]:
        """Execute the task packet via the adapter and validate the results.

        Returns:
            A tuple of (execution_results, legacy_proof_path).
            The legacy_proof_path is retained for backward compatibility with
            Phase 1 aggregation logic.
        """
        results, legacy_proof_path = self.adapter.run_tp(tp)

        # Kernel validation of adapter output
        if not isinstance(results, list):
            raise TypeError(f"Adapter results must be a list of ExecutionResult, got {type(results)}")

        for result in results:
            if not isinstance(result, ExecutionResult):
                raise TypeError(f"Invalid adapter output: expected ExecutionResult, got {type(result)}")

        return results, legacy_proof_path
