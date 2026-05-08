"""Validate runtime artifact schemas against existing read-only fixtures."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator, FormatChecker

from dopetask.core.schema import TaskPacket
from dopetask.ops.tp_series.logic import _default_state
from dopetask.router.reporting import (
    render_route_plan_markdown,
    route_plan_from_dict,
    route_plan_to_dict,
)
from dopetask.router.types import PlannedStep, RefusalReason, RoutePlan, RoutePolicy, TopCandidate


REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_DIR = REPO_ROOT / "dopetask_schemas"

SCHEMA_FILES = {
    "series_state": SCHEMA_DIR / "series_state.schema.json",
    "exec_record": SCHEMA_DIR / "exec_record.schema.json",
    "exec_error": SCHEMA_DIR / "exec_error.schema.json",
    "series_context": SCHEMA_DIR / "series_context.schema.json",
    "route_plan": SCHEMA_DIR / "route_plan.schema.json",
}

FIXTURE_PATTERNS = {
    "series_state": ["out/tp_series/*/SERIES_STATE.json"],
    "exec_record": ["out/tp_series/*/packets/*/EXEC.json"],
    "exec_error": ["out/tp_series/*/packets/*/EXEC_ERROR.json"],
    "series_context": ["out/tp_series/*/packets/*/SERIES_CONTEXT.json"],
    "route_plan": ["out/dopetask_route/**/ROUTE_PLAN.json"],
}

# Keep explicit so any future tolerated fixture failure is auditable in code and proof.
EXPECTED_INCONSISTENCIES: dict[str, str] = {}


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _fixture_paths(artifact_type: str) -> list[Path]:
    paths: set[Path] = set()
    for pattern in FIXTURE_PATTERNS[artifact_type]:
        paths.update(REPO_ROOT.glob(pattern))
    return sorted(paths)


def _validator_for(artifact_type: str) -> Draft202012Validator:
    schema = _load_json(SCHEMA_FILES[artifact_type])
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FormatChecker())


@pytest.mark.parametrize("schema_path", sorted(SCHEMA_FILES.values()))
def test_schema_file_is_valid_json_schema(schema_path: Path) -> None:
    schema = _load_json(schema_path)
    Draft202012Validator.check_schema(schema)


@pytest.mark.parametrize("artifact_type", sorted(FIXTURE_PATTERNS))
def test_existing_runtime_artifacts_validate_when_present(artifact_type: str) -> None:
    fixture_paths = _fixture_paths(artifact_type)
    if not fixture_paths:
        patterns = ", ".join(FIXTURE_PATTERNS[artifact_type])
        pytest.skip(f"No {artifact_type} fixtures found for pattern(s): {patterns}")

    validator = _validator_for(artifact_type)
    failures: list[str] = []
    for path in fixture_paths:
        payload = _load_json(path)
        errors = sorted(validator.iter_errors(payload), key=lambda error: list(error.path))
        if not errors:
            continue

        relative_path = path.relative_to(REPO_ROOT).as_posix()
        expected_reason = EXPECTED_INCONSISTENCIES.get(relative_path)
        if expected_reason is not None:
            continue

        rendered_errors = "; ".join(
            f"{'/'.join(str(part) for part in error.path) or '<root>'}: {error.message}"
            for error in errors
        )
        failures.append(f"{relative_path}: {rendered_errors}")

    if failures:
        pytest.fail(
            "Runtime artifact schema validation failed without a documented expected "
            "inconsistency:\n" + "\n".join(failures)
        )


def test_series_state_schema_validates_runtime_default_state_projection() -> None:
    payload = _default_state(series_id="SERIES-EXAMPLE", base_branch="main")
    validator = _validator_for("series_state")

    errors = sorted(validator.iter_errors(payload), key=lambda error: list(error.path))

    assert errors == []


def test_route_plan_schema_validates_runtime_reporting_projection() -> None:
    plan = RoutePlan(
        status="refused",
        repo_root=REPO_ROOT,
        packet_path=REPO_ROOT / "task-packets" / "TP-DT-UI-CONTRACTS-0001.json",
        availability_path=REPO_ROOT / ".dopetask" / "runtime" / "availability.yaml",
        policy=RoutePolicy(
            require_explain=True,
            stop_on_ambiguity=True,
            max_cost_tier="medium",
            escalation_ladder=("gpt-5.1-mini", "gpt-5.3-codex"),
            max_escalations=1,
            min_total_score=50,
        ),
        refusal_reasons=(
            RefusalReason(
                reason_code="SCORE_THRESHOLD",
                message="Step `run-task` below score threshold: 40 < 50",
            ),
        ),
        steps=(
            PlannedStep(
                step="run-task",
                runner="codex_desktop",
                model="gpt-5.3-codex",
                confidence=0.4,
                scores={
                    "runner_fit": 20,
                    "model_fit": 20,
                    "cost_penalty": 0,
                    "confidence_penalty": 0,
                    "total": 40,
                },
                reasons=("fixture_projection",),
                candidates_top3=(
                    TopCandidate(runner="codex_desktop", model="gpt-5.3-codex", total=40),
                ),
            ),
        ),
    )
    payload = route_plan_to_dict(plan)
    validator = _validator_for("route_plan")

    errors = sorted(validator.iter_errors(payload), key=lambda error: list(error.path))
    restored = route_plan_from_dict(payload)
    rendered = render_route_plan_markdown(restored)

    assert errors == []
    assert restored.status == "refused"
    assert "| run-task | codex_desktop | gpt-5.3-codex | 0.40 | 40 |" in rendered


def test_task_packet_artifact_is_accepted_by_runtime_dataclass_parser() -> None:
    payload = _load_json(REPO_ROOT / "task-packets" / "TP-DT-UI-CONTRACTS-0001.json")

    parsed = TaskPacket.from_dict(payload)
    rendered = parsed.to_dict()

    assert rendered["id"] == "TP-DT-UI-CONTRACTS-0001"
    assert rendered["repo_binding"]["project_id"] == "dopetask.core"
    assert rendered["execution"]["agent"] == "codex"
    assert rendered["commit"]["message"] == "feat(schema): publish UI runtime artifact contracts"
