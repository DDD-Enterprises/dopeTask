"""Task Packet (TP) schema definitions."""

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class TPRepoBinding:
    """Repo-binding metadata for strict packet execution."""

    project_id: str
    repo_marker: str
    require_identity_match: bool = False
    origin_hint: Optional[str] = None


@dataclass
class TPExecution:
    """Execution-scoped metadata for a packet run."""

    agent: str
    branch: Optional[str] = None


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
    repo_binding: Optional[TPRepoBinding] = None
    series: Optional[TPSeries] = None
    execution: Optional[TPExecution] = None
    commit: Optional[TPCommit] = None
    pr: Optional[dict[str, Any]] = None
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

            raw_binding = data.get("repo_binding")
            repo_binding = None
            if raw_binding is not None:
                repo_binding = TPRepoBinding(
                    project_id=raw_binding["project_id"],
                    repo_marker=raw_binding["repo_marker"],
                    origin_hint=raw_binding.get("origin_hint"),
                    require_identity_match=bool(raw_binding.get("require_identity_match", False)),
                )

            raw_execution = data.get("execution")
            execution = None
            if raw_execution is not None:
                execution = TPExecution(
                    agent=raw_execution["agent"],
                    branch=raw_execution.get("branch"),
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
                repo_binding=repo_binding,
                series=series,
                execution=execution,
                commit=commit,
                pr=data.get("pr"),
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
        if self.repo_binding is not None:
            repo_binding_payload: dict[str, Any] = {
                "project_id": self.repo_binding.project_id,
                "repo_marker": self.repo_binding.repo_marker,
                "require_identity_match": self.repo_binding.require_identity_match,
            }
            if self.repo_binding.origin_hint is not None:
                repo_binding_payload["origin_hint"] = self.repo_binding.origin_hint
            payload["repo_binding"] = repo_binding_payload
        if self.series is not None:
            payload["series"] = {
                "id": self.series.id,
                "base_branch": self.series.base_branch,
                "parent_tp_id": self.series.parent_tp_id,
                "final_packet": self.series.final_packet,
            }
        if self.execution is not None:
            execution_payload: dict[str, Any] = {
                "agent": self.execution.agent,
            }
            if self.execution.branch is not None:
                execution_payload["branch"] = self.execution.branch
            payload["execution"] = execution_payload
        if self.supersedes: payload["supersedes"] = self.supersedes
        if self.pal_chain is not None:
            payload["pal_chain"] = {"enabled": self.pal_chain.enabled, "steps": self.pal_chain.steps}
        if self.commit is not None:
            payload["commit"] = {
                "message": self.commit.message,
                "allowlist": self.commit.allowlist,
                "verify": self.commit.verify,
            }
        if self.pr is not None:
            payload["pr"] = self.pr
        return payload
