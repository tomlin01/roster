#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

OVERLAY_SIGNAL_RULES = (
    (
        "discussion_before_high_impact_changes",
        2,
        (
            r"discuss assumptions and acceptance criteria first",
            r"依難度決定是否先討論",
            r"先進行短討論再執行",
        ),
    ),
    (
        "non_trivial_task_locking",
        2,
        (
            r"start each non-trivial task by locking",
            r"先定義可驗證的成功條件",
            r"target outcome",
        ),
    ),
    (
        "visual_first_verification",
        1,
        (
            r"visual-first verification",
            r"validate the rendered outcome",
            r"markdown preview",
        ),
    ),
    (
        "closeout_definition_of_done",
        1,
        (
            r"before closing, confirm",
            r"closeout assist",
            r"收案流程",
        ),
    ),
    (
        "correctness_priority",
        1,
        (
            r"correctness\s*>\s*speed",
            r"decision priority",
            r"正確\s*>\s*速度",
        ),
    ),
)


def resolve_benchmark_kind(scope: str, requested: str) -> str:
    if requested != "auto":
        return requested
    if scope == "workspace":
        return "parsed_overlay"
    return "policy_simulation"


def read_text_if_exists(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def parse_overlay_signals(file_texts: dict[str, str]) -> dict:
    parsed_signals: list[str] = []
    signal_sources: dict[str, list[str]] = {}
    strictness_score = 0

    for signal_name, weight, patterns in OVERLAY_SIGNAL_RULES:
        matched_files: list[str] = []
        for file_label, text in file_texts.items():
            if not text:
                continue
            if any(re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE) for pattern in patterns):
                matched_files.append(file_label)
        if matched_files:
            parsed_signals.append(signal_name)
            signal_sources[signal_name] = matched_files
            strictness_score += weight

    return {
        "parsed_signals": parsed_signals,
        "signal_sources": signal_sources,
        "strictness_score": strictness_score,
    }


def load_overlay(workspace: Path, benchmark_kind: str) -> dict:
    agents = workspace / "AGENTS.md"
    principles = workspace / "PRINCIPLES.md"
    agents_text = read_text_if_exists(agents)
    principles_text = read_text_if_exists(principles)
    overlay = {
        "workspace": str(workspace),
        "has_agents_md": agents.exists(),
        "has_principles_md": principles.exists(),
        "overlay_depth": 0,
        "benchmark_kind": benchmark_kind,
        "parsed_signals": [],
        "signal_sources": {},
        "strictness_score": 0,
    }
    if overlay["has_agents_md"]:
        overlay["overlay_depth"] += 1
    if overlay["has_principles_md"]:
        overlay["overlay_depth"] += 1
    if benchmark_kind == "parsed_overlay":
        overlay.update(
            parse_overlay_signals(
                {
                    "AGENTS.md": agents_text,
                    "PRINCIPLES.md": principles_text,
                }
            )
        )
    return overlay


def manual_intervention_reasons(case: dict, overlay: dict, scope: str, benchmark_kind: str) -> list[str]:
    if scope != "workspace" or case["required_mode"] == "trivial":
        return []

    if benchmark_kind == "policy_simulation":
        if overlay["overlay_depth"] > 1 and case["workspace_sensitivity"] == "high":
            return ["heuristic_overlay_depth_high"]
        return []

    if case["workspace_sensitivity"] != "high":
        return []

    reasons: list[str] = []
    parsed_signals = set(overlay["parsed_signals"])
    if "discussion_before_high_impact_changes" in parsed_signals:
        reasons.append("local_overlay_requires_discussion_for_high_impact_changes")
    if "non_trivial_task_locking" in parsed_signals:
        reasons.append("local_overlay_requires_task_lock_before_execution")
    return reasons
