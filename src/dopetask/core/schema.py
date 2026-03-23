"""Task Packet (TP) schema definitions."""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field

@dataclass
class TPStep:
    """A single execution step in a Task Packet."""
    id: str
    task: str
    requirements: List[str] = field(default_factory=list)
    commands: List[str] = field(default_factory=list)
    expected_files: List[str] = field(default_factory=list)
    validation: List[str] = field(default_factory=list)
    context_files: List[str] = field(default_factory=list)


@dataclass
class TaskPacket:
    """The generic Task Packet representation."""
    id: str
    target: str
    project: str = "dopetask"
    steps: List[TPStep] = field(default_factory=list)
    invariants: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskPacket":
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
            raise ValueError(f"TaskPacket is missing required field: {e}")

    def to_dict(self) -> Dict[str, Any]:
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
