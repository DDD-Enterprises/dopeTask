"""Adversarial probe for TP-DT-G1-POST-SYNC-REPAIR-FINALITY-002-A1 (R1-R4).

Drives the REAL public governed entrypoints -- `execute_task_packet` and the
`dopetask tp exec` CLI -- not only guard helpers. That distinction is the whole
point: the previous repair's R2 fix was correct at the guard layer but
unreachable in production because `TPParser.parse_file` ran first.

Run against the canonical start head 1bf18dea to see the defects (RED), and
against the repaired head to see them closed (GREEN). Same file, both times.

    uv run --extra dev python proof/TP-DT-G1-POST-SYNC-REPAIR-FINALITY-002-A1/REPAIR_PROBE.py
"""

from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

_spec = importlib.util.spec_from_file_location(
    "_gov_fixtures", REPO_ROOT / "tests/unit/dopetask/test_tp_exec_governed.py"
)
assert _spec and _spec.loader
_fx = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_fx)

from typer.testing import CliRunner  # noqa: E402

from dopetask.cli import cli  # noqa: E402
from dopetask.guard.governed_execution import GovernedAdmissionError  # noqa: E402
from dopetask.ops.tp_exec.engine import execute_task_packet  # noqa: E402

RESULTS: list[tuple[str, bool, str]] = []


def record(name: str, ok: bool, detail: str = "") -> None:
    RESULTS.append((name, ok, detail))
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" -- {detail}" if detail else ""))


@contextlib.contextmanager
def sandbox():
    d = Path(tempfile.mkdtemp(prefix="dtg1probe-"))
    try:
        yield d
    finally:
        for p in d.rglob("*"):
            with contextlib.suppress(OSError):
                p.chmod(0o700)
        shutil.rmtree(d, ignore_errors=True)


def build(repo_parent: Path, *, allowlist: list[str] | None = None):
    allowlist = allowlist or ["generated.txt"]
    repo = _fx._init_repo(repo_parent / "repo")
    packet = _fx._write_json_packet(
        repo / "packet.json",
        allowlist=allowlist,
        expected_files=["generated.txt"],
        validation=["test -f generated.txt"],
    )
    grant_path, dcp_path = _fx._write_governed_fixture(repo, allowlist=allowlist, packet_path=packet)
    return repo, packet, grant_path, dcp_path


def rewrite_grant(grant_path: Path, **changes: Any) -> None:
    g = json.loads(grant_path.read_text())
    for k, v in changes.items():
        if isinstance(v, dict) and isinstance(g.get(k), dict):
            g[k] = {**g[k], **v}
        else:
            g[k] = v
    grant_path.write_text(json.dumps(g, indent=2) + "\n", encoding="utf-8")


def regrant(packet: Path, grant_path: Path) -> None:
    """Re-bind subject digest after the packet bytes change."""
    rewrite_grant(
        grant_path,
        subject={"task_packet_sha256": hashlib.sha256(packet.read_bytes()).hexdigest()},
    )


# --------------------------------------------------------------------------
# R2 -- every governed entrypoint refuses through GovernedAdmissionError
# --------------------------------------------------------------------------
def probe_r2() -> None:
    print("\nR2 -- governed entrypoint refusal contract (packet read/parse)")

    # R2a: engine entrypoint, packet deleted after grant construction.
    with sandbox() as d:
        repo, packet, grant_path, dcp_path = build(d)
        packet.unlink()
        try:
            execute_task_packet(
                packet, agent="codex", working_dir=repo, governed=True,
                grant_path=grant_path, dcp_route_authorization_path=dcp_path,
            )
            record("R2a engine missing-packet", False, "no exception raised")
        except GovernedAdmissionError as exc:
            record("R2a engine missing-packet", True, f"reason={exc.reason}")
        except OSError as exc:
            record("R2a engine missing-packet", False, f"RAW {type(exc).__name__} escaped")
        except Exception as exc:  # noqa: BLE001
            record("R2a engine missing-packet", False, f"non-governed {type(exc).__name__}")

    # R2b: engine entrypoint, packet present but unreadable.
    with sandbox() as d:
        repo, packet, grant_path, dcp_path = build(d)
        packet.chmod(0o000)
        try:
            execute_task_packet(
                packet, agent="codex", working_dir=repo, governed=True,
                grant_path=grant_path, dcp_route_authorization_path=dcp_path,
            )
            record("R2b engine unreadable-packet", False, "no exception raised")
        except GovernedAdmissionError as exc:
            record("R2b engine unreadable-packet", True, f"reason={exc.reason}")
        except OSError as exc:
            record("R2b engine unreadable-packet", False, f"RAW {type(exc).__name__} escaped")
        except Exception as exc:  # noqa: BLE001
            record("R2b engine unreadable-packet", False, f"non-governed {type(exc).__name__}")
        finally:
            with contextlib.suppress(OSError):
                packet.chmod(stat.S_IRUSR | stat.S_IWUSR)

    # R2c: engine entrypoint, malformed JSON.
    with sandbox() as d:
        repo, packet, grant_path, dcp_path = build(d)
        packet.write_text("{not json", encoding="utf-8")
        regrant(packet, grant_path)
        try:
            execute_task_packet(
                packet, agent="codex", working_dir=repo, governed=True,
                grant_path=grant_path, dcp_route_authorization_path=dcp_path,
            )
            record("R2c engine malformed-json", False, "no exception raised")
        except GovernedAdmissionError as exc:
            record("R2c engine malformed-json", True, f"reason={exc.reason}")
        except Exception as exc:  # noqa: BLE001
            record("R2c engine malformed-json", False, f"non-governed {type(exc).__name__}")

    # R2d / R2e / R2f: the CLI governed entrypoints.
    #
    # `tp_file` carries Typer/Click `Path(exists=True)`, and click.Path also
    # defaults to `readable=True`. A *missing* OR *unreadable* packet is
    # therefore pre-empted at the argument layer (exit 2, Click usage error)
    # and never reaches the read/parse contract at all. That is legacy CLI
    # behaviour preserved under section 11 and is recorded here as
    # argument-layer pre-emption, not as a governed refusal.
    #
    # The case that DOES reach the contract is an existing, readable packet
    # whose bytes do not parse -- that hits TPParser.parse_file, which at the
    # canonical start head runs before governed admission.
    for label, extra in (("R2d CLI dry-run malformed-json", ["--dry-run"]),
                         ("R2e CLI real malformed-json", [])):
        with sandbox() as d:
            repo, packet, grant_path, dcp_path = build(d)
            packet.write_text("{not json", encoding="utf-8")
            cwd = Path.cwd()
            try:
                os.chdir(repo)
                res = CliRunner().invoke(
                    cli,
                    ["tp", "exec", str(packet), "--agent", "codex", *extra, "--governed",
                     "--grant", str(grant_path), "--dcp-route-authorization", str(dcp_path)],
                )
                out = res.output or ""
                governed = "GOVERNED_MODE REFUSAL" in out
                compiled = "Compiled Profile" in out
                record(label, governed and not compiled and res.exit_code == 1,
                       f"exit={res.exit_code} governed={governed} compiled={compiled}")
            finally:
                os.chdir(cwd)

    # R2f: argument-layer pre-emption is expected and must stay intact.
    with sandbox() as d:
        repo, packet, grant_path, dcp_path = build(d)
        packet.unlink()
        cwd = Path.cwd()
        try:
            os.chdir(repo)
            res = CliRunner().invoke(
                cli,
                ["tp", "exec", str(packet), "--agent", "codex", "--governed",
                 "--grant", str(grant_path), "--dcp-route-authorization", str(dcp_path)],
            )
            record("R2f CLI missing-packet pre-empted by Click (exit 2)", res.exit_code == 2,
                   f"exit={res.exit_code}")
        finally:
            os.chdir(cwd)


# --------------------------------------------------------------------------
# R3 -- one governed execution performs exactly one of each resolution
# --------------------------------------------------------------------------
def probe_r3() -> None:
    print("\nR3 -- single admission / repository resolution")
    import dopetask.guard.governed_execution as guard_mod
    import dopetask.ops.tp_exec.engine as engine_mod
    import dopetask.ops.tp_git.guards as git_guards

    def instrument():
        counts: dict[str, int] = {}
        saved: list[tuple[Any, str, Any]] = []

        def wrap(mod, attr, key):
            orig = getattr(mod, attr)
            saved.append((mod, attr, orig))

            def counted(*a, **k):
                counts[key] = counts.get(key, 0) + 1
                return orig(*a, **k)

            setattr(mod, attr, counted)

        wrap(engine_mod, "load_repo_identity", "load_repo_identity")
        wrap(engine_mod, "assert_repo_identity", "assert_repo_identity")
        wrap(engine_mod, "assert_repo_binding", "assert_repo_binding")
        wrap(git_guards, "resolve_repo_root", "resolve_repo_root")
        wrap(guard_mod, "extract_origin_url", "extract_origin_url")
        return counts, saved

    def restore(saved):
        for mod, attr, orig in saved:
            setattr(mod, attr, orig)

    # real governed execution
    with sandbox() as d:
        repo, packet, grant_path, dcp_path = build(d)
        rewrite_grant(grant_path, authority_effect={
            "grants": ["TASK_PACKET_MUTATION_WITHIN_ALLOWLIST", "RUNNER_INVOCATION"]})
        counts, saved = instrument()
        orig_run = subprocess.run
        try:
            engine_mod.subprocess = subprocess  # noqa: B010
            import dopetask_adapters.codex.executor as codex_exec
            codex_exec.subprocess.run = _fx._fake_codex_run(repo)
            try:
                execute_task_packet(
                    packet, agent="codex", working_dir=repo, governed=True,
                    grant_path=grant_path, dcp_route_authorization_path=dcp_path,
                )
            except Exception as exc:  # noqa: BLE001
                print(f"       (real governed run raised {type(exc).__name__}: {str(exc)[:80]})")
            finally:
                codex_exec.subprocess.run = orig_run
        finally:
            restore(saved)
        ok = all(counts.get(k, 0) == 1 for k in
                 ("load_repo_identity", "assert_repo_identity", "assert_repo_binding", "extract_origin_url"))
        record("R3a real governed resolution counts", ok, json.dumps(counts, sort_keys=True))

    # governed dry-run through the CLI
    with sandbox() as d:
        repo, packet, grant_path, dcp_path = build(d)
        rewrite_grant(grant_path, authority_effect={
            "grants": ["TASK_PACKET_MUTATION_WITHIN_ALLOWLIST", "RUNNER_INVOCATION"]})
        counts, saved = instrument()
        cwd = Path.cwd()
        try:
            os.chdir(repo)
            CliRunner().invoke(
                cli,
                ["tp", "exec", str(packet), "--agent", "codex", "--dry-run", "--governed",
                 "--grant", str(grant_path), "--dcp-route-authorization", str(dcp_path)],
            )
        finally:
            os.chdir(cwd)
            restore(saved)
        ok = all(counts.get(k, 0) == 1 for k in
                 ("load_repo_identity", "assert_repo_identity", "assert_repo_binding", "extract_origin_url"))
        record("R3b dry-run governed resolution counts", ok, json.dumps(counts, sort_keys=True))

    # legacy path must never touch the governed resolver
    with sandbox() as d:
        repo, packet, grant_path, dcp_path = build(d)
        calls: list[str] = []
        orig_admit = guard_mod.admit_governed_execution
        orig_resolve = engine_mod.resolve_governed_admission
        orig_run = subprocess.run
        try:
            guard_mod.admit_governed_execution = lambda *_a, **_k: calls.append("admit")  # type: ignore[assignment]
            engine_mod.resolve_governed_admission = lambda *_a, **_k: calls.append("resolve")  # type: ignore[assignment]
            import dopetask_adapters.codex.executor as codex_exec
            codex_exec.subprocess.run = _fx._fake_codex_run(repo)
            try:
                execute_task_packet(packet, agent="codex", working_dir=repo)
            except Exception:  # noqa: BLE001
                pass
            finally:
                codex_exec.subprocess.run = orig_run
        finally:
            guard_mod.admit_governed_execution = orig_admit
            engine_mod.resolve_governed_admission = orig_resolve
        record("R3c legacy governed-resolver calls == 0", calls == [], f"calls={calls}")


# --------------------------------------------------------------------------
# R4 -- canonical owner/repository identity, exact equality
# --------------------------------------------------------------------------
def probe_r4() -> None:
    print("\nR4 -- canonical repository identity (no substring, no basename)")
    cases = [
        ("e", False), ("dopeTask", False), ("DDD-Enterprises", False), ("github.com", False),
        ("opeTask", False), ("wrong-owner/dopeTask", False), ("DDD-Enterprises/dopeTask-extra", False),
        ("DDD-Enterprises/dopeTask", True),
        ("https://github.com/DDD-Enterprises/dopeTask", True),
        ("https://github.com/DDD-Enterprises/dopeTask.git", True),
        ("git@github.com:DDD-Enterprises/dopeTask.git", True),
        ("https://evil.com/github.com/DDD-Enterprises/dopeTask", False),
    ]
    for repository, should_admit in cases:
        with sandbox() as d:
            repo, packet, grant_path, dcp_path = build(d)
            rewrite_grant(grant_path, repository=repository, authority_effect={
                "grants": ["TASK_PACKET_MUTATION_WITHIN_ALLOWLIST", "RUNNER_INVOCATION"]})
            from dopetask.core.tp_parser import TPParser
            from dopetask.ops.tp_exec.engine import resolve_governed_admission
            try:
                tp = TPParser.parse_file(packet)
                resolve_governed_admission(
                    packet, tp, agent="codex", model=None, grant_path=grant_path,
                    dcp_route_authorization_path=dcp_path, working_dir=repo,
                )
                admitted = True
                detail = "ADMITTED"
            except GovernedAdmissionError as exc:
                admitted = False
                detail = exc.reason
            except Exception as exc:  # noqa: BLE001
                admitted = False
                detail = f"{type(exc).__name__}"
            record(f"R4 repository={repository!r} -> {'admit' if should_admit else 'reject'}",
                   admitted == should_admit, detail)


# --------------------------------------------------------------------------
# R1 -- narrow under-grant check (operator amendment 01)
# --------------------------------------------------------------------------
def probe_r1() -> None:
    print("\nR1 -- RUNNER_INVOCATION under-grant check (amendment 01)")
    import dopetask.ops.tp_exec.engine as engine_mod

    # under-granted: must refuse, and must never construct a runner
    with sandbox() as d:
        repo, packet, grant_path, dcp_path = build(d)
        rewrite_grant(grant_path, authority_effect={"grants": ["TASK_PACKET_MUTATION_WITHIN_ALLOWLIST"]})
        constructed: list[str] = []
        orig_te = engine_mod.TaskExecutor
        try:
            def spy(*a, **k):
                constructed.append("TaskExecutor")
                return orig_te(*a, **k)
            engine_mod.TaskExecutor = spy  # type: ignore[assignment]
            try:
                execute_task_packet(
                    packet, agent="codex", working_dir=repo, governed=True,
                    grant_path=grant_path, dcp_route_authorization_path=dcp_path,
                )
                record("R1a under-grant refused", False, "ADMITTED -- runner ran without RUNNER_INVOCATION")
            except GovernedAdmissionError as exc:
                record("R1a under-grant refused", exc.reason == "AUTHORITY_UNDERGRANT_RUNNER_INVOCATION",
                       f"reason={exc.reason}")
            except Exception as exc:  # noqa: BLE001
                record("R1a under-grant refused", False, f"non-governed {type(exc).__name__}")
        finally:
            engine_mod.TaskExecutor = orig_te
        record("R1b runner calls == 0 when under-granted", constructed == [], f"constructed={constructed}")

    # correctly granted: the check must not block a well-formed grant
    with sandbox() as d:
        repo, packet, grant_path, dcp_path = build(d)
        rewrite_grant(grant_path, authority_effect={
            "grants": ["RUNNER_INVOCATION", "TASK_PACKET_MUTATION_WITHIN_ALLOWLIST"]})
        from dopetask.core.tp_parser import TPParser
        from dopetask.ops.tp_exec.engine import resolve_governed_admission
        try:
            tp = TPParser.parse_file(packet)
            resolve_governed_admission(
                packet, tp, agent="codex", model=None, grant_path=grant_path,
                dcp_route_authorization_path=dcp_path, working_dir=repo,
            )
            record("R1c correctly-granted admitted", True)
        except Exception as exc:  # noqa: BLE001
            record("R1c correctly-granted admitted", False, f"{type(exc).__name__}: {str(exc)[:90]}")

    # DCP cannot supply the missing authority.
    # NOTE: this is proved STRUCTURALLY, not end-to-end: the DCP schema's own
    # authority_effect.grants enum (ROUTE_ELIGIBILITY, ROUTE_ORDER, ...) is
    # disjoint from the grant's, so RUNNER_INVOCATION is not even expressible
    # in a DCPRouteAuthorization. An end-to-end "DCP grants RUNNER_INVOCATION"
    # probe would be schema-vacuous and is deliberately not written.
    with sandbox() as d:
        repo, packet, grant_path, dcp_path = build(d)
        rewrite_grant(grant_path, authority_effect={"grants": ["TASK_PACKET_MUTATION_WITHIN_ALLOWLIST"]})
        dcp = json.loads(dcp_path.read_text())
        enum_disjoint = "RUNNER_INVOCATION" not in json.dumps(dcp["authority_effect"]["grants"])
        from dopetask.core.tp_parser import TPParser
        from dopetask.ops.tp_exec.engine import resolve_governed_admission
        try:
            tp = TPParser.parse_file(packet)
            resolve_governed_admission(
                packet, tp, agent="codex", model=None, grant_path=grant_path,
                dcp_route_authorization_path=dcp_path, working_dir=repo,
            )
            refused = False
            detail = "ADMITTED"
        except GovernedAdmissionError as exc:
            refused = exc.reason == "AUTHORITY_UNDERGRANT_RUNNER_INVOCATION"
            detail = exc.reason
        except Exception as exc:  # noqa: BLE001
            refused = False
            detail = type(exc).__name__
        record("R1d valid DCP cannot supply RUNNER_INVOCATION", refused and enum_disjoint,
               f"{detail}; dcp_enum_disjoint={enum_disjoint}")


def main() -> int:
    print("=" * 78)
    print("TP-DT-G1-POST-SYNC-REPAIR-FINALITY-002-A1 -- adversarial entrypoint probe")
    print(f"repo: {REPO_ROOT}")
    print(f"head: {subprocess.run(['git','-C',str(REPO_ROOT),'rev-parse','HEAD'],capture_output=True,text=True).stdout.strip()}")
    print("=" * 78)
    for fn in (probe_r2, probe_r3, probe_r4, probe_r1):
        try:
            fn()
        except Exception as exc:  # noqa: BLE001
            record(f"{fn.__name__} CRASHED", False, f"{type(exc).__name__}: {exc}")
    passed = sum(1 for _, ok, _ in RESULTS if ok)
    total = len(RESULTS)
    print("\n" + "=" * 78)
    print(f"PROBE RESULT: {passed}/{total} passed, {total - passed} failed")
    for name, ok, detail in RESULTS:
        if not ok:
            print(f"  FAILING: {name} -- {detail}")
    print("=" * 78)
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
