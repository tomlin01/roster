#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "run_agent_benchmark.py"
WRAPPER = ROOT / "scripts" / "run_agent_benchmark.sh"
PUBLISHER = ROOT / "scripts" / "publish_agent_policy.py"
CASE_FIXTURES = ROOT / "contexts" / "agent_benchmark_cases.json"


def run_command(cmd: list[str], cwd: Path | None = None, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    return subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True, env=merged_env)


def load_report(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def build_portable_case_file(tmpdir: Path) -> tuple[Path, Path]:
    vis_math = tmpdir / "Vis_Math"
    obsidian = tmpdir / "obsidian_tom"
    vis_math.mkdir()
    obsidian.mkdir()
    (vis_math / "AGENTS.md").write_text("# AGENTS\n- Local overlay only.\n", encoding="utf-8")

    source = json.loads(CASE_FIXTURES.read_text(encoding="utf-8"))
    portable_cases = []
    for case in source:
        cloned = dict(case)
        workspace = cloned.get("workspace")
        if workspace == "/Users/tom/Documents/PHD/codex_updat":
            cloned["workspace"] = str(ROOT.resolve())
        elif workspace == "/Users/tom/Documents/PHD/Vis_Math":
            cloned["workspace"] = str(vis_math.resolve())
        elif workspace == "/Users/tom/Documents/GitHub/obsidian_tom":
            cloned["workspace"] = str(obsidian.resolve())
        portable_cases.append(cloned)

    case_path = tmpdir / "agent_benchmark_cases.portable.json"
    case_path.write_text(json.dumps(portable_cases, indent=2), encoding="utf-8")
    return case_path, vis_math


def verify_parsed_overlay_mode(tmpdir: Path, case_path: Path) -> None:
    json_path = tmpdir / "workspace_parsed_overlay.json"
    md_path = tmpdir / "workspace_parsed_overlay.md"
    run_command(
        [
            sys.executable,
            str(RUNNER),
            "--scope",
            "workspace",
            "--benchmark-kind",
            "parsed_overlay",
            "--cases",
            str(case_path),
            "--only",
            "meta_contract_refresh",
            "vismath_quick_query",
            "obsidian_memory_review",
            "--json-report",
            str(json_path),
            "--md-report",
            str(md_path),
        ]
    )
    report = load_report(json_path)
    assert_true(report["benchmark_kind"] == "parsed_overlay", "workspace run should resolve to parsed_overlay")

    by_id = {item["id"]: item for item in report["case_results"]}
    meta_case = by_id["meta_contract_refresh"]["workspace_overlay_result"]
    vismath_case = by_id["vismath_quick_query"]["workspace_overlay_result"]
    obsidian_case = by_id["obsidian_memory_review"]["workspace_overlay_result"]

    assert_true(meta_case["manual_intervention"], "meta workspace high-sensitivity case should require intervention")
    assert_true(
        "local_overlay_requires_discussion_for_high_impact_changes" in meta_case["manual_intervention_reasons"],
        "parsed overlay should explain intervention via discussion signal",
    )
    assert_true(
        "local_overlay_requires_task_lock_before_execution" in meta_case["manual_intervention_reasons"],
        "parsed overlay should explain intervention via task lock signal",
    )
    assert_true(
        "discussion_before_high_impact_changes" in meta_case["parsed_signals"],
        "meta workspace should surface parsed discussion signal",
    )
    assert_true(
        "non_trivial_task_locking" in meta_case["parsed_signals"],
        "meta workspace should surface parsed task locking signal",
    )

    assert_true(vismath_case["has_agents_md"], "Vis_Math should expose its local AGENTS overlay")
    assert_true(not vismath_case["has_principles_md"], "Vis_Math should not have local PRINCIPLES overlay")
    assert_true(not vismath_case["manual_intervention"], "Vis_Math trivial case should not require intervention")
    assert_true(vismath_case["parsed_signals"] == [], "Vis_Math should keep an empty parsed signal set for this trivial case")

    assert_true(not obsidian_case["has_agents_md"], "obsidian_tom should not have local AGENTS overlay")
    assert_true(not obsidian_case["has_principles_md"], "obsidian_tom should not have local PRINCIPLES overlay")
    assert_true(not obsidian_case["manual_intervention"], "obsidian_tom should not require intervention without local overlay")
    assert_true(obsidian_case["parsed_signals"] == [], "obsidian_tom should not inherit codex_updat signals")


def verify_published_runner_portability(tmpdir: Path, case_path: Path, vis_math: Path) -> None:
    codex_home = tmpdir / "codex_home"
    json_path = tmpdir / "portable_global.json"
    md_path = tmpdir / "portable_global.md"
    run_command(
        [
            sys.executable,
            str(PUBLISHER),
            "--codex-home",
            str(codex_home),
        ]
    )
    run_command(
        [
            str(WRAPPER),
            "--scope",
            "global",
            "--benchmark-kind",
            "policy_simulation",
            "--cases",
            str(case_path),
            "--only",
            "vismath_quick_query",
            "--json-report",
            str(json_path),
            "--md-report",
            str(md_path),
        ],
        cwd=vis_math,
        env={"CODEX_HOME": str(codex_home)},
    )
    report = load_report(json_path)
    assert_true(report["benchmark_kind"] == "policy_simulation", "portable global run should stay policy_simulation")
    assert_true(report["passed"] == 1 and report["failed"] == 0, "portable global run should succeed")
    assert_true(report["workspace"] == str(vis_math.resolve()), "portable global run should preserve case workspace label")


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="agent-benchmark-test-") as tmp:
        tmpdir = Path(tmp)
        case_path, vis_math = build_portable_case_file(tmpdir)
        verify_parsed_overlay_mode(tmpdir, case_path)
        verify_published_runner_portability(tmpdir, case_path, vis_math)
    print("agent benchmark regression checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
