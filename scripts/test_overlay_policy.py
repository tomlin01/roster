#!/usr/bin/env python3
from __future__ import annotations

import tempfile
from pathlib import Path

from overlay_policy import load_overlay, manual_intervention_reasons, resolve_benchmark_kind

ROOT = Path("/Users/tom/Documents/PHD/codex_updat")
VIS_MATH = Path("/Users/tom/Documents/PHD/Vis_Math")
OBSIDIAN = Path("/Users/tom/Documents/GitHub/obsidian_tom")


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def test_resolve_benchmark_kind_auto() -> None:
    assert_true(resolve_benchmark_kind("workspace", "auto") == "parsed_overlay", "workspace auto should resolve to parsed_overlay")
    assert_true(resolve_benchmark_kind("global", "auto") == "policy_simulation", "global auto should resolve to policy_simulation")
    assert_true(resolve_benchmark_kind("workspace", "policy_simulation") == "policy_simulation", "explicit benchmark kind should be preserved")


def test_load_overlay_parsed_overlay_detects_repo_signals() -> None:
    overlay = load_overlay(ROOT, "parsed_overlay")
    assert_true(overlay["has_agents_md"], "repo should expose AGENTS.md")
    assert_true(overlay["has_principles_md"], "repo should expose PRINCIPLES.md")
    assert_true("discussion_before_high_impact_changes" in overlay["parsed_signals"], "repo should expose discussion signal")
    assert_true("non_trivial_task_locking" in overlay["parsed_signals"], "repo should expose task locking signal")
    assert_true(overlay["strictness_score"] >= 4, "repo strictness score should reflect parsed policy signals")


def test_load_overlay_parsed_overlay_ignores_unconfigured_workspaces() -> None:
    vismath = load_overlay(VIS_MATH, "parsed_overlay")
    obsidian = load_overlay(OBSIDIAN, "parsed_overlay")
    for name, overlay in (("Vis_Math", vismath), ("obsidian_tom", obsidian)):
        assert_true(not overlay["has_agents_md"], f"{name} should not expose AGENTS.md")
        assert_true(not overlay["has_principles_md"], f"{name} should not expose PRINCIPLES.md")
        assert_true(overlay["parsed_signals"] == [], f"{name} should not expose parsed signals")
        assert_true(overlay["strictness_score"] == 0, f"{name} should have zero strictness score")


def test_manual_intervention_reasons_policy_simulation() -> None:
    case = {"required_mode": "review", "workspace_sensitivity": "high"}
    overlay = {"overlay_depth": 2, "parsed_signals": []}
    reasons = manual_intervention_reasons(case, overlay, "workspace", "policy_simulation")
    assert_true(reasons == ["heuristic_overlay_depth_high"], "policy_simulation should use heuristic overlay depth")


def test_manual_intervention_reasons_parsed_overlay() -> None:
    case = {"required_mode": "review", "workspace_sensitivity": "high"}
    overlay = load_overlay(ROOT, "parsed_overlay")
    reasons = manual_intervention_reasons(case, overlay, "workspace", "parsed_overlay")
    assert_true(
        reasons == [
            "local_overlay_requires_discussion_for_high_impact_changes",
            "local_overlay_requires_task_lock_before_execution",
        ],
        "parsed_overlay should expose signal-based intervention reasons",
    )


def test_manual_intervention_reasons_skip_trivial_or_low_sensitivity() -> None:
    overlay = load_overlay(ROOT, "parsed_overlay")
    trivial = {"required_mode": "trivial", "workspace_sensitivity": "high"}
    low = {"required_mode": "review", "workspace_sensitivity": "low"}
    assert_true(manual_intervention_reasons(trivial, overlay, "workspace", "parsed_overlay") == [], "trivial tasks should not require intervention")
    assert_true(manual_intervention_reasons(low, overlay, "workspace", "parsed_overlay") == [], "low sensitivity tasks should not require intervention")


def test_load_overlay_from_temp_workspace() -> None:
    with tempfile.TemporaryDirectory(prefix="overlay-policy-") as tmp:
        ws = Path(tmp)
        (ws / "AGENTS.md").write_text("# AGENTS\n- 先進行短討論再執行。\n", encoding="utf-8")
        (ws / "PRINCIPLES.md").write_text("# PRINCIPLES\n- Start each non-trivial task by locking target outcome.\n", encoding="utf-8")
        overlay = load_overlay(ws, "parsed_overlay")
        assert_true(
            overlay["parsed_signals"] == [
                "discussion_before_high_impact_changes",
                "non_trivial_task_locking",
            ],
            "temp workspace should parse signals from both local files",
        )


def main() -> int:
    tests = [
        test_resolve_benchmark_kind_auto,
        test_load_overlay_parsed_overlay_detects_repo_signals,
        test_load_overlay_parsed_overlay_ignores_unconfigured_workspaces,
        test_manual_intervention_reasons_policy_simulation,
        test_manual_intervention_reasons_parsed_overlay,
        test_manual_intervention_reasons_skip_trivial_or_low_sensitivity,
        test_load_overlay_from_temp_workspace,
    ]
    for test in tests:
        test()
    print("overlay policy tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
