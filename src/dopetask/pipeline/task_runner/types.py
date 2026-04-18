"""Task runner types."""

from __future__ import annotations

import typing
from dataclasses import dataclass, field
from typing import TypedDict


class NormalizedOutput(TypedDict):
    """Standardized adapter execution summary."""
    files_created: list[str]
    changed_files: list[str]
    commands_run: list[str]
    validation_passed: bool

ExecutionMetrics = dict[str, typing.Any]

@dataclass
class ProjectIdentity:
    """Task packet project identity declaration."""

    project_id: str
    intended_repo: typing.Optional[str] = None


@dataclass
class CommitStep:
    """Single commit step from optional COMMIT PLAN section."""

    step_id: str
    message: str
    allowlist: list[str]
    verify: typing.Optional[list[str]]


@dataclass
class TaskPacketInfo:
    """Parsed task packet information."""

    id: str
    title: str
    path: str
    sha256: str
    allowlist: list[str]
    sources: list[str]
    verification_commands: list[str]
    commit_plan: typing.Optional[list[CommitStep]]
    sections: dict[str, str]
    project_identity: typing.Optional[ProjectIdentity] = None


@dataclass
class RunWorkspace:
    """Run workspace information."""

    root: str
    files: list[dict[str, str]]


@dataclass
class ExecutionResult:
    """Standardized outcome of a task step execution."""

    step_id: str
    status: typing.Literal["pending", "running", "succeeded", "failed"]
    execution_mode: typing.Literal["shell", "agent"]
    raw_output: str
    normalized_output: NormalizedOutput
    metrics: ExecutionMetrics = field(default_factory=dict)
    error: typing.Optional[str] = None

