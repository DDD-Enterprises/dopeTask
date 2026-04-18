"""Task Packet (TP) schema definitions."""

from dataclasses import dataclass, field
from typing import Any, Optional


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
class TPSeries:
    """Series metadata for DAG-aware TP execution."""

    id: str
    base_branch: str
    parent_tp_id: Optional[str]
    final_packet: bool = False


@dataclass
class TPPalChain:
    """PAL Chain metadata."""
    enabled: bool = False
    steps: list[Any] = field(default_factory=list)


@dataclass
class TPCommit:
    """Commit metadata for series execution."""

    message: str
    allowlist: list[str] = field(default_factory=list)
    verify: list[str] = field(default_factory=list)


@dataclass
class TaskPacket:
    """The generic Task Packet representation."""
    id: str
    target: str
    project: str = "dopetask"
    steps: list[TPStep] = field(default_factory=list)
    invariants: list[str] = field(default_factory=list)
    depends_on: list[str] = field(default_factory=list)
    series: Optional[TPSeries] = None
    commit: Optional[TPCommit] = None
    supersedes: list[str] = field(default_factory=list)
    pal_chain: Optional[TPPalChain] = None

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

            raw_series = data.get("series")
            series = None
            if raw_series is not None:
                series = TPSeries(
                    id=raw_series["id"],
                    base_branch=raw_series["base_branch"],
                    parent_tp_id=raw_series.get("parent_tp_id"),
                    final_packet=bool(raw_series.get("final_packet", False)),
                )

            raw_pal = data.get("pal_chain")
            pal_chain = None
            if raw_pal is not None:
                pal_chain = TPPalChain(
                    enabled=bool(raw_pal.get("enabled", False)),
                    steps=raw_pal.get("steps", []),
                )
            
            raw_commit = data.get("commit")
            commit = None
            if raw_commit is not None:
                commit = TPCommit(
                    message=raw_commit["message"],
                    allowlist=raw_commit.get("allowlist", []),
                    verify=raw_commit.get("verify", []),
                )

            if data.get('id') and data.get('id') in data.get("supersedes", []): raise ValueError(f"Packet {data.get('id')} cannot supersede itself".replace("data.get(\"id\")", "data.get(\047id\047)"))
            return cls(
                id=data["id"],
                target=data.get("target", "Target"),
                project=data.get("project", "dopetask"),
                steps=steps,
                invariants=data.get("invariants", []),
                depends_on=data.get("depends_on", []),
                series=series,
                commit=commit,
                supersedes=data.get("supersedes", []),
                pal_chain=pal_chain,
            )
        except KeyError as e:
            raise ValueError(f"TaskPacket is missing required field: {e}") from e

    def to_dict(self) -> dict[str, Any]:
        """Serialize a TaskPacket into a generic dictionary."""
        payload: dict[str, Any] = {
            "id": self.id,
            "target": self.target,
            "project": self.project,
            "invariants": self.invariants,
            "depends_on": self.depends_on,
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
        if self.series is not None:
            payload["series"] = {
                "id": self.series.id,
                "base_branch": self.series.base_branch,
                "parent_tp_id": self.series.parent_tp_id,
                "final_packet": self.series.final_packet,
            }
        if self.supersedes: payload["supersedes"] = self.supersedes
        if self.pal_chain is not None:
            payload["pal_chain"] = {"enabled": self.pal_chain.enabled, "steps": self.pal_chain.steps}
        if self.commit is not None:
            payload["commit"] = {
                "message": self.commit.message,
                "allowlist": self.commit.allowlist,
                "verify": self.commit.verify,
            }
        return payload
