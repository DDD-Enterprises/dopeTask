"""GOVERNED_MODE admission guard for C0-R2 governed single-Task-Packet execution.

Consumes and validates an exact `MacroExecutionAuthorityRefV2` grant plus its
bound `DCPRouteAuthorization` artifact. Fails closed on any missing, invalid,
expired, or mismatched grant state. Never imports or calls
`dopetask.router.planner.build_route_plan` and never silently defaults an
agent or model. `DCPRouteAuthorization` is policy-only: it is schema-validated
and digest-checked but never consulted for routing/model decisions here.

Admission compares repository identity canonically (never by substring) and
requires the one positive capability a governed single-TP run actually
exercises: `RUNNER_INVOCATION`. Because that check lives in admission, a
governed *dry-run* refuses an under-granted grant exactly as a real governed
execution does -- dry-run and real execution deliberately share one contract.
Every refusal raised here is a `GovernedAdmissionError` carrying a stable
machine-readable `reason`; a raw `OSError` is never the public refusal contract.

This module adds no persistent authority store. Grant acceptance is
at-most-once by contract (`acceptance_semantics`); durable receipt/acceptance
state is out of scope and deferred to a successor packet.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional
from urllib.parse import urlsplit

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

# --- DT-G1 under-grant check (operator amendment 01) -------------------------
#
# `authority_effect.grants` is enum-narrowed by the ratified C0-R2 grant schema,
# but it carries `minItems: 1` and no `contains`, so a *fully schema-valid* grant
# may omit `RUNNER_INVOCATION` while GOVERNED_MODE goes on to construct a runner.
# Schema `const`/`enum` closes "the grant claims an authority it must not have";
# nothing in the schema closes "the grant omits an authority the code then
# exercises". This single positive capability check closes exactly that, and
# nothing else: no over-ceiling check, no prohibition re-assertion, no generic
# `authority_effect` validator.
_REQUIRED_RUNNER_GRANT = "RUNNER_INVOCATION"

# --- canonical repository identity -------------------------------------------
#
# Only hosts whose `owner/repository` identity can be proven from the identifier
# alone are supported. Anything else fails closed rather than being guessed at.
_CANONICAL_REPOSITORY_HOSTS = frozenset({"github.com"})
_CANONICAL_REPOSITORY_SCHEMES = frozenset({"https", "http", "ssh", "git"})
_CANONICAL_REPOSITORY_SEGMENT = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
_SCP_LIKE_REMOTE = re.compile(r"^(?:[^@/]+@)?(?P<host>[^:/@]+):(?P<path>.+)$")
_GIT_SUFFIX = ".git"


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


def _read_raw_bytes(path: Path, *, label: str, reject_reason: str) -> bytes:
    """Read a governed-admission input, converting every read failure to a refusal.

    File-not-found, permission, directory-instead-of-file and unreadable-bytes
    failures all surface as `GovernedAdmissionError` with a stable reason code;
    a raw `OSError` is never the public refusal contract.
    """
    try:
        return path.read_bytes()
    except OSError as exc:
        raise GovernedAdmissionError(reject_reason, f"{label} could not be read at {path}: {exc}") from exc


def _read_raw_and_parse(path: Path, *, label: str, reject_reason: str) -> tuple[bytes, Any]:
    raw = _read_raw_bytes(path, label=label, reject_reason=reject_reason)
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


def load_governed_task_packet(path: Path) -> tuple[bytes, TaskPacket]:
    """Read and parse a Task Packet under the governed refusal contract.

    This is the **single** governed packet loader. Every governed entrypoint --
    `execute_task_packet(governed=True)` and the `tp exec --governed` CLI, dry
    run or not -- must call it *before* any generic `TPParser.parse_file`, or a
    read/parse failure escapes as a raw `OSError`/`ValueError` and the governed
    refusal contract never applies. Guarding only the guard layer is not enough
    when an earlier unguarded parse on the same path can raise first.

    Returns the exact bytes that were parsed alongside the packet, so the
    subject digest is computed over the bytes admission actually saw rather
    than over a second, independent re-read.
    """
    from dopetask.core.tp_parser import TPParser

    raw = _read_raw_bytes(path, label="Task Packet", reject_reason="TASK_PACKET_UNREADABLE")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise GovernedAdmissionError(
            "TASK_PACKET_PARSE_INVALID", f"Task Packet at {path} is not valid JSON: {exc}"
        ) from exc
    try:
        return raw, TPParser.parse_dict(data)
    except GovernedAdmissionError:
        raise
    except Exception as exc:  # noqa: BLE001 - refusal contract must stay closed
        raise GovernedAdmissionError(
            "TASK_PACKET_PARSE_INVALID",
            f"Task Packet at {path} could not be parsed: {type(exc).__name__}: {exc}",
        ) from exc


def assert_runner_invocation_granted(authority_effect: Any) -> None:
    """Fail closed unless the grant confers the runner authority the run exercises.

    Scope is deliberately one positive capability. This does not police
    over-granting, does not re-assert `does_not_grant`, and does not validate
    `authority_effect` generally -- the ratified schema already closes those
    directions with a `const` prohibition list and a closed `grants` enum.

    Raises `GovernedAdmissionError`; returns `None` on acceptance.
    """
    grants = authority_effect.get("grants") if isinstance(authority_effect, dict) else None
    if not isinstance(grants, list) or _REQUIRED_RUNNER_GRANT not in grants:
        raise GovernedAdmissionError(
            "AUTHORITY_UNDERGRANT_RUNNER_INVOCATION",
            f"grant.authority_effect.grants {grants!r} does not confer "
            f"'{_REQUIRED_RUNNER_GRANT}'; GOVERNED_MODE would otherwise invoke a runner on "
            "authority the grant never conferred. A DCPRouteAuthorization cannot supply it: "
            "its own authority_effect vocabulary is disjoint and policy-only.",
        )


def canonical_repository_identity(value: Optional[str]) -> Optional[str]:
    """Map a supported repository identifier to a canonical `owner/repository`.

    Supported inputs, all resolving to the same canonical identity:

        https://github.com/DDD-Enterprises/dopeTask.git
        git@github.com:DDD-Enterprises/dopeTask.git
        ssh://git@github.com/DDD-Enterprises/dopeTask
        DDD-Enterprises/dopeTask

    The canonical form is lowercased: GitHub repository identity is
    case-insensitive, so an owner/repository differing only in case denotes the
    *same* repository and must not be read as a different one.

    Returns `None` -- never a guess -- when the identifier is empty, malformed,
    ambiguous (wrong segment count), or names a host whose `owner/repository`
    identity cannot be proven from the identifier alone. A host-in-path spoof
    such as `https://evil.com/github.com/owner/repo` therefore yields `None`
    because the real host is not allowlisted. Callers must treat `None` as
    fail-closed; this function never performs substring matching.
    """
    if not isinstance(value, str):
        return None
    text = value.strip()
    if not text:
        return None

    host: Optional[str]
    if "://" in text:
        try:
            parsed = urlsplit(text)
        except ValueError:
            return None
        if parsed.scheme.lower() not in _CANONICAL_REPOSITORY_SCHEMES:
            return None
        try:
            hostname = parsed.hostname
        except ValueError:
            return None
        host = (hostname or "").lower()
        path = parsed.path
    else:
        scp_match = _SCP_LIKE_REMOTE.match(text)
        if scp_match is not None:
            host = scp_match.group("host").lower()
            path = scp_match.group("path")
        elif "@" in text or ":" in text:
            # Credential-ish or transport-ish shape we cannot canonicalize.
            return None
        else:
            host = None
            path = text

    if host is not None and host not in _CANONICAL_REPOSITORY_HOSTS:
        return None

    path = path.strip("/")
    if path.endswith(_GIT_SUFFIX):
        path = path[: -len(_GIT_SUFFIX)]

    segments = path.split("/")
    if len(segments) != 2:
        return None
    owner, repository = segments
    if not _CANONICAL_REPOSITORY_SEGMENT.match(owner):
        return None
    if not _CANONICAL_REPOSITORY_SEGMENT.match(repository):
        return None
    return f"{owner.lower()}/{repository.lower()}"


def admit_governed_execution(
    *,
    grant_path: Path,
    dcp_route_authorization_path: Path,
    packet_path: Path,
    tp: TaskPacket,
    repo_root: Path,
    cli_agent: str,
    cli_model: Optional[str],
    packet_raw: Optional[bytes] = None,
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

    assert_runner_invocation_granted(grant.get("authority_effect"))

    if packet_raw is None:
        packet_raw = _read_raw_bytes(
            packet_path, label="Task Packet", reject_reason="TASK_PACKET_UNREADABLE"
        )
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

    # `grant.repository` is compared to the active repo's actual git remote by
    # canonical `owner/repository` identity and exact equality. Substring
    # matching is deliberately NOT used: it would admit a grant naming a bare
    # `dopeTask`, `DDD-Enterprises`, `github.com` or even `e`. The soft
    # substring warning in guard.identity.origin_hint_warning is a separate,
    # non-admission signal and is intentionally left unchanged.
    origin_url = extract_origin_url(repo_root)
    grant_repository = grant.get("repository")
    grant_repository_identity = canonical_repository_identity(grant_repository)
    origin_repository_identity = canonical_repository_identity(origin_url)
    if grant_repository_identity is None or origin_repository_identity is None:
        raise GovernedAdmissionError(
            "GRANT_REPOSITORY_UNCANONICALIZABLE",
            f"repository identity could not be canonicalized: grant.repository {grant_repository!r} -> "
            f"{grant_repository_identity!r}; origin URL {origin_url!r} -> {origin_repository_identity!r}. "
            "Admission fails closed rather than falling back to substring matching.",
        )
    if grant_repository_identity != origin_repository_identity:
        raise GovernedAdmissionError(
            "GRANT_REPOSITORY_MISMATCH",
            f"grant.repository '{grant_repository}' canonicalizes to '{grant_repository_identity}', which "
            f"is not the active repo's origin '{origin_url}' -> '{origin_repository_identity}'.",
        )

    worktree_binding = grant.get("worktree_binding") or {}
    resolved_repo_root = str(repo_root.resolve())
    grant_worktree_path = worktree_binding.get("path")
    resolved_grant_worktree: Optional[str] = None
    if isinstance(grant_worktree_path, str):
        try:
            resolved_grant_worktree = str(Path(grant_worktree_path).resolve())
        except (OSError, ValueError):
            resolved_grant_worktree = None
    if resolved_grant_worktree is None or resolved_grant_worktree != resolved_repo_root:
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
