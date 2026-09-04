"""GOVERNED_MODE admission guard for C0-R2 governed single-Task-Packet execution.

Consumes and validates an exact `MacroExecutionAuthorityRefV2` grant plus its
bound `DCPRouteAuthorization` artifact. Fails closed on any missing, invalid,
expired, or mismatched grant state. Never imports or calls
`dopetask.router.planner.build_route_plan` and never silently defaults an
agent or model. `DCPRouteAuthorization` is policy-only: it is schema-validated
and digest-checked but never consulted for routing/model decisions here.

This module adds no persistent authority store. Grant acceptance is
at-most-once by contract (`acceptance_semantics`); durable receipt/acceptance
state is out of scope and deferred to a successor packet.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from jsonschema import Draft7Validator
from jsonschema.exceptions import ValidationError
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT7

from dopetask.core.schema import TaskPacket
from dopetask.guard.identity import extract_origin_url
from dopetask.utils.schema_registry import SchemaRegistry

_SCHEMA_NAMES = (
    "common_defs",
    "dcp_route_authorization",
    "dopetask_governed_execution_profile",
    "governed_execution_receipt",
    "macro_execution_authority_ref_v2",
    "model_transport_receipt",
    "tool_intent",
    "uag_compatibility_certification",
    "uag_transport_request",
    "uag_transport_result",
)

_GRANT_SCHEMA = "macro_execution_authority_ref_v2"
_DCP_ROUTE_AUTHORIZATION_SCHEMA = "dcp_route_authorization"

# V1 governed single-TP fixed values (dopemux-macro-execution-authority-ref.v2,
# v1_governed_single_tp_defaults / GOVERNED_SINGLE_TP allOf branch).
_REQUIRED_PERMITTED_MODE = "GOVERNED_SINGLE_TP"
_REQUIRED_CONSUMER = "dopetask"
_REQUIRED_RUNNER = "codex"
_REQUIRED_MAX_ATTEMPTS = 1
_REQUIRED_SUBSTITUTION_POLICY = "forbid"
_REQUIRED_SUBJECT_KIND = "SINGLE_TASK_PACKET"

# GOVERNED_DELIVERY_DISPATCH is a schema-valid issuer.class enum member (v1/GD006
# family lineage) but is explicitly "not authorized by C0" per the grant schema's
# own field description. DT-G1 narrows by refusing it rather than accepting it.
_ACCEPTED_ISSUER_CLASSES = frozenset({"OPERATOR", "CONTROL_TOWER"})


class GovernedAdmissionError(RuntimeError):
    """Raised when GOVERNED_MODE admission fails closed for any reason.

    `reason` is a short machine-checkable code; the exception message is the
    human-readable REFUSAL text. Both are always present together.
    """

    def __init__(self, reason: str, message: str) -> None:
        super().__init__(f"GOVERNED_MODE REFUSAL [{reason}]: {message}")
        self.reason = reason


@dataclass(frozen=True)
class GovernedAdmissionDecision:
    """Result of a successful (ACCEPT) governed-grant admission evaluation."""

    grant: dict[str, Any]
    dcp_route_authorization: dict[str, Any]
    effective_runner: str
    effective_model: Optional[str]
    model_source: str
    grant_authority_id: str


def _load_registry(registry_schemas: SchemaRegistry) -> tuple[Registry, dict[str, dict[str, Any]]]:
    docs = {name: registry_schemas.get_json(name) for name in _SCHEMA_NAMES}
    resources = {doc["$id"]: Resource.from_contents(doc, default_specification=DRAFT7) for doc in docs.values()}
    registry = Registry().with_resources(resources.items())
    return registry, docs


def _validate_against_schema(
    *,
    instance: Any,
    schema_name: str,
    registry: Registry,
    docs: dict[str, dict[str, Any]],
    reject_reason: str,
    artifact_label: str,
) -> None:
    schema = docs[schema_name]
    validator = Draft7Validator(schema, registry=registry)
    try:
        validator.validate(instance)
    except ValidationError as exc:
        raise GovernedAdmissionError(
            reject_reason,
            f"{artifact_label} failed Draft-07 validation against {schema_name}: {exc.message} "
            f"(path: {list(exc.absolute_path)})",
        ) from exc


def _read_raw_and_parse(path: Path, *, label: str, reject_reason: str) -> tuple[bytes, Any]:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise GovernedAdmissionError(reject_reason, f"{label} could not be read at {path}: {exc}") from exc
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise GovernedAdmissionError(reject_reason, f"{label} at {path} is not valid JSON: {exc}") from exc
    return raw, parsed


def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _parse_iso8601(value: str, *, field: str) -> datetime:
    try:
        text = value[:-1] + "+00:00" if value.endswith("Z") else value
        parsed = datetime.fromisoformat(text)
    except ValueError as exc:
        raise GovernedAdmissionError(
            "GRANT_TIMESTAMP_INVALID", f"grant.{field} '{value}' is not a valid ISO-8601 timestamp: {exc}"
        ) from exc
    if parsed.tzinfo is None:
        raise GovernedAdmissionError(
            "GRANT_TIMESTAMP_INVALID", f"grant.{field} '{value}' has no timezone offset."
        )
    return parsed.astimezone(timezone.utc)


def admit_governed_execution(
    *,
    grant_path: Path,
    dcp_route_authorization_path: Path,
    packet_path: Path,
    tp: TaskPacket,
    repo_root: Path,
    cli_agent: str,
    cli_model: Optional[str],
    now: Optional[datetime] = None,
) -> GovernedAdmissionDecision:
    """Evaluate GOVERNED_MODE admission for one Task Packet.

    Raises `GovernedAdmissionError` (fail closed) on the first violation.
    Returns a `GovernedAdmissionDecision` only when every check passes.
    """
    current_time = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)

    schema_registry = SchemaRegistry()
    registry, docs = _load_registry(schema_registry)

    grant_raw, grant = _read_raw_and_parse(grant_path, label="grant", reject_reason="GRANT_UNREADABLE")
    if not isinstance(grant, dict):
        raise GovernedAdmissionError("GRANT_SCHEMA_INVALID", "grant JSON root is not an object.")
    _validate_against_schema(
        instance=grant,
        schema_name=_GRANT_SCHEMA,
        registry=registry,
        docs=docs,
        reject_reason="GRANT_SCHEMA_INVALID",
        artifact_label="grant",
    )

    dcp_raw, dcp = _read_raw_and_parse(
        dcp_route_authorization_path,
        label="DCPRouteAuthorization",
        reject_reason="DCP_ROUTE_AUTHORIZATION_UNREADABLE",
    )
    if not isinstance(dcp, dict):
        raise GovernedAdmissionError(
            "DCP_ROUTE_AUTHORIZATION_SCHEMA_INVALID", "DCPRouteAuthorization JSON root is not an object."
        )
    _validate_against_schema(
        instance=dcp,
        schema_name=_DCP_ROUTE_AUTHORIZATION_SCHEMA,
        registry=registry,
        docs=docs,
        reject_reason="DCP_ROUTE_AUTHORIZATION_SCHEMA_INVALID",
        artifact_label="DCPRouteAuthorization",
    )

    # DCPRouteAuthorization is policy-only and is never treated as execution
    # authority beyond this digest binding: no field of `dcp` is read again
    # below to influence runner/model/routing decisions.
    dcp_digest = _sha256_hex(dcp_raw)
    if dcp_digest != grant.get("dcp_route_authorization_digest"):
        raise GovernedAdmissionError(
            "DCP_ROUTE_AUTHORIZATION_DIGEST_MISMATCH",
            f"sha256({dcp_route_authorization_path}) = {dcp_digest} does not equal "
            f"grant.dcp_route_authorization_digest = {grant.get('dcp_route_authorization_digest')!r}.",
        )

    issuer = grant.get("issuer") or {}
    issuer_class = issuer.get("class")
    if issuer_class not in _ACCEPTED_ISSUER_CLASSES:
        raise GovernedAdmissionError(
            "GRANT_ISSUER_CLASS_UNACCEPTED",
            f"grant.issuer.class '{issuer_class}' is not one of {sorted(_ACCEPTED_ISSUER_CLASSES)} "
            "for V1 governed single-TP admission.",
        )

    issued_at = _parse_iso8601(grant["issued_at"], field="issued_at")
    expires_at = _parse_iso8601(grant["expires_at"], field="expires_at")
    if expires_at <= issued_at:
        raise GovernedAdmissionError(
            "GRANT_TIMESTAMP_INVALID",
            f"grant.expires_at ({grant['expires_at']}) is not after grant.issued_at ({grant['issued_at']}).",
        )
    if current_time < issued_at:
        raise GovernedAdmissionError(
            "GRANT_NOT_YET_VALID",
            f"current time {current_time.isoformat()} is before grant.issued_at {grant['issued_at']}.",
        )
    if current_time >= expires_at:
        raise GovernedAdmissionError(
            "GRANT_EXPIRED",
            f"current time {current_time.isoformat()} is at/after grant.expires_at {grant['expires_at']}.",
        )

    if grant.get("revocation_ref") is not None:
        raise GovernedAdmissionError(
            "GRANT_REVOCATION_REF_PRESENT_NO_RESOLVER",
            "grant.revocation_ref is present but no authoritative revocation resolver exists; "
            "refusing rather than inventing one.",
        )

    subject = grant.get("subject") or {}
    if subject.get("kind") != _REQUIRED_SUBJECT_KIND:
        raise GovernedAdmissionError(
            "GRANT_SUBJECT_KIND_UNSUPPORTED",
            f"grant.subject.kind '{subject.get('kind')}' is not '{_REQUIRED_SUBJECT_KIND}'; "
            "MACRO_PLAN subjects are out of scope for this admission path.",
        )

    packet_raw = packet_path.read_bytes()
    packet_sha256 = _sha256_hex(packet_raw)
    if subject.get("task_packet_id") != tp.id:
        raise GovernedAdmissionError(
            "TASK_PACKET_ID_MISMATCH",
            f"grant.subject.task_packet_id '{subject.get('task_packet_id')}' does not equal packet id '{tp.id}'.",
        )
    if subject.get("task_packet_sha256") != packet_sha256:
        raise GovernedAdmissionError(
            "TASK_PACKET_SHA256_MISMATCH",
            f"grant.subject.task_packet_sha256 '{subject.get('task_packet_sha256')}' does not equal "
            f"sha256({packet_path}) = '{packet_sha256}'.",
        )

    if grant.get("consumer") != _REQUIRED_CONSUMER:
        raise GovernedAdmissionError(
            "GRANT_CONSUMER_MISMATCH", f"grant.consumer '{grant.get('consumer')}' is not '{_REQUIRED_CONSUMER}'."
        )

    permitted = grant.get("permitted_execution") or {}
    if permitted.get("mode") != _REQUIRED_PERMITTED_MODE:
        raise GovernedAdmissionError(
            "GRANT_PERMITTED_EXECUTION_MISMATCH",
            f"grant.permitted_execution.mode '{permitted.get('mode')}' is not '{_REQUIRED_PERMITTED_MODE}'.",
        )
    if permitted.get("runner") != _REQUIRED_RUNNER:
        raise GovernedAdmissionError(
            "GRANT_PERMITTED_EXECUTION_MISMATCH",
            f"grant.permitted_execution.runner '{permitted.get('runner')}' is not '{_REQUIRED_RUNNER}'.",
        )
    if permitted.get("max_attempts") != _REQUIRED_MAX_ATTEMPTS:
        raise GovernedAdmissionError(
            "GRANT_PERMITTED_EXECUTION_MISMATCH",
            f"grant.permitted_execution.max_attempts {permitted.get('max_attempts')!r} is not "
            f"{_REQUIRED_MAX_ATTEMPTS}.",
        )
    if permitted.get("substitution_policy") != _REQUIRED_SUBSTITUTION_POLICY:
        raise GovernedAdmissionError(
            "GRANT_PERMITTED_EXECUTION_MISMATCH",
            f"grant.permitted_execution.substitution_policy '{permitted.get('substitution_policy')}' "
            f"is not '{_REQUIRED_SUBSTITUTION_POLICY}'.",
        )

    if cli_agent != permitted.get("runner"):
        raise GovernedAdmissionError(
            "CLI_AGENT_RUNNER_MISMATCH",
            f"--agent '{cli_agent}' does not match grant.permitted_execution.runner "
            f"'{permitted.get('runner')}'; CLI may only check the grant, never widen it.",
        )
    if tp.execution is not None and tp.execution.agent != permitted.get("runner"):
        raise GovernedAdmissionError(
            "PACKET_AGENT_RUNNER_MISMATCH",
            f"packet execution.agent '{tp.execution.agent}' does not match grant.permitted_execution.runner "
            f"'{permitted.get('runner')}'; packet execution.agent may only check the grant, never widen it.",
        )

    model_ceiling = permitted.get("model_ceiling")
    if not model_ceiling:
        raise GovernedAdmissionError(
            "GRANT_MODEL_CEILING_ABSENT",
            "grant.permitted_execution.model_ceiling is absent/null; GOVERNED_MODE cannot silently default "
            "a model and the CLI/packet may not supply one the grant did not authorize.",
        )
    if cli_model is not None and cli_model != model_ceiling:
        raise GovernedAdmissionError(
            "CLI_MODEL_MISMATCH_GRANT_CEILING",
            f"--model '{cli_model}' does not equal grant.permitted_execution.model_ceiling "
            f"'{model_ceiling}'; CLI may only check the grant's model ceiling, never widen or substitute it.",
        )

    repo_binding = tp.repo_binding
    expected_project_id = repo_binding.project_id if repo_binding is not None else tp.project
    if grant.get("project_id") != expected_project_id:
        raise GovernedAdmissionError(
            "GRANT_PROJECT_MISMATCH",
            f"grant.project_id '{grant.get('project_id')}' does not equal packet project_id "
            f"'{expected_project_id}'.",
        )

    # `grant.repository` is checked against the active repo's actual git
    # remote, reusing the same hint-substring semantics as
    # guard.identity.origin_hint_warning (repo_binding.origin_hint), but
    # enforced fail-closed here rather than as a soft warning.
    origin_url = extract_origin_url(repo_root)
    grant_repository = grant.get("repository")
    if not grant_repository or origin_url is None or grant_repository not in origin_url:
        raise GovernedAdmissionError(
            "GRANT_REPOSITORY_MISMATCH",
            f"grant.repository '{grant_repository}' is not found in the active repo's origin URL "
            f"'{origin_url}'.",
        )

    worktree_binding = grant.get("worktree_binding") or {}
    resolved_repo_root = str(repo_root.resolve())
    grant_worktree_path = worktree_binding.get("path")
    if grant_worktree_path is None or str(Path(grant_worktree_path).resolve()) != resolved_repo_root:
        raise GovernedAdmissionError(
            "GRANT_WORKTREE_MISMATCH",
            f"grant.worktree_binding.path '{grant_worktree_path}' does not resolve to the active repo root "
            f"'{resolved_repo_root}'.",
        )

    grant_allowlist = grant.get("allowlist")
    packet_allowlist = tp.commit.allowlist if tp.commit is not None else []
    if not isinstance(grant_allowlist, list) or list(grant_allowlist) != list(packet_allowlist):
        raise GovernedAdmissionError(
            "ALLOWLIST_MISMATCH",
            f"grant.allowlist {grant_allowlist!r} is not exactly ordered-equal to packet.commit.allowlist "
            f"{packet_allowlist!r}; no subset/superset widening is permitted.",
        )

    return GovernedAdmissionDecision(
        grant=grant,
        dcp_route_authorization=dcp,
        effective_runner=permitted["runner"],
        effective_model=model_ceiling,
        model_source="GRANT_CEILING",
        grant_authority_id=grant["authority_id"],
    )
