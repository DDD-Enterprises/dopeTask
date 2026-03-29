"""Core task execution kernel."""

from __future__ import annotations

import typing
from typing import Any, Protocol

from dopetask.pipeline.task_runner.types import ExecutionResult


class Adapter(Protocol):
    """Protocol for task execution adapters."""

    def run_tp(self, tp: dict[str, Any]) -> list[ExecutionResult]:
        """Execute a full Task Packet and return results."""


class TaskExecutor:
    """Kernel component responsible for task execution and validation."""

    def __init__(self, adapter: Adapter) -> None:
        self.adapter = adapter

    def execute(self, tp: dict[str, Any]) -> list[ExecutionResult]:
        """Execute the task packet via the adapter and validate the results."""
        results = self.adapter.run_tp(tp)
        
        # Kernel validation of adapter output
        if not isinstance(results, list):
            raise TypeError(f"Adapter must return a list of ExecutionResult, got {type(results)}")
            
        for result in results:
            if not isinstance(result, ExecutionResult):
                raise TypeError(f"Invalid adapter output: expected ExecutionResult, got {type(result)}")
                
            # Fail-fast: Stop execution if a step failed
            if result.status == "failed":
                # In a real implementation, we would write proof artifacts here
                raise RuntimeError(f"Step {result.step_id} failed: {result.error}")
                
        return results
