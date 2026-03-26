"""Task Packet (TP) schema definitions."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class TPStep:
    """A single execution step in a Task Packet."""
    id: str
    task: str
    requirements: list[str] = field(default_factory=list)
    commands: list[str] = field(default_factory=list)
    expected_files: list[str] = field(default_factory=list)
    validation: list[str] = field(default_factory=list)
    context_files: list[str] = field(default_factory=list)


@dataclass
class TaskPacket:
    """The generic Task Packet representation."""
    id: str
    target: str
    project: str = "dopetask"
    steps: list[TPStep] = field(default_factory=list)
    invariants: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TaskPacket":
        """Deserialize a TaskPacket from a generic dictionary."""
        try:
            steps_data = data.get("steps", [])
            steps = []
            for step_data in steps_data:
                steps.append(
                    TPStep(
                        id=step_data["id"],
                        task=step_data.get("task", ""),
                        requirements=step_data.get("requirements", []),
                        commands=step_data.get("commands", []),
                        expected_files=step_data.get("expected_files", []),
                        validation=step_data.get("validation", []),
                        context_files=step_data.get("context_files", [])
                    )
                )

            return cls(
                id=data["id"],
                target=data.get("target", "Target"),
                project=data.get("project", "dopetask"),
                steps=steps,
                invariants=data.get("invariants", [])
            )
        except KeyError as e:
            raise ValueError(f"TaskPacket is missing required field: {e}") from e

    def to_dict(self) -> dict[str, Any]:
        """Serialize a TaskPacket into a generic dictionary."""
        return {
            "id": self.id,
            "target": self.target,
            "project": self.project,
            "invariants": self.invariants,
            "steps": [
                {
                    "id": step.id,
                    "task": step.task,
                    "requirements": step.requirements,
                    "commands": step.commands,
                    "expected_files": step.expected_files,
                    "validation": step.validation,
                    "context_files": step.context_files
                }
                for step in self.steps
            ]
        }
