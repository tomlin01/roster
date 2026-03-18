#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import statistics
import time
from pathlib import Path

from overlay_policy import load_overlay, manual_intervention_reasons, resolve_benchmark_kind

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_HOME = Path(__file__).resolve().parent


def resolve_published_source_workspace() -> Path | None:
    manifest_path = SCRIPT_HOME / "manifest.json"
    if not manifest_path.exists():
        return None
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    source_workspace = manifest.get("source_workspace")
    if not isinstance(source_workspace, str) or not source_workspace:
        return None
    return Path(source_workspace).expanduser().resolve()


if (SCRIPT_HOME / "global_agent_defaults.json").exists():
    POLICY_DIR = SCRIPT_HOME
    PUBLISHED_SOURCE = resolve_published_source_workspace()
    if PUBLISHED_SOURCE and (PUBLISHED_SOURCE / "contexts" / "agent_benchmark_cases.json").exists():
        DEFAULT_CASES_PATH = PUBLISHED_SOURCE / "contexts" / "agent_benchmark_cases.json"
    else:
        DEFAULT_CASES_PATH = Path.cwd() / "contexts" / "agent_benchmark_cases.json"
    DEFAULT_JSON_REPORT = Path.cwd() / "contexts" / "agent_benchmark_baseline.json"
    DEFAULT_MD_REPORT = Path.cwd() / "contexts" / "agent_benchmark_baseline.md"
else:
    POLICY_DIR = ROOT / "policy"
    DEFAULT_CASES_PATH = ROOT / "contexts" / "agent_benchmark_cases.json"
    DEFAULT_JSON_REPORT = ROOT / "contexts" / "agent_benchmark_baseline.json"
    DEFAULT_MD_REPORT = ROOT / "contexts" / "agent_benchmark_baseline.md"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run policy-level global vs workspace-overlay benchmark.")
    parser.add_argument("--scope", choices=("global", "workspace"), default="workspace")
    parser.add_argument(
        "--benchmark-kind",
        choices=("auto", "policy_simulation", "parsed_overlay"),
        default="auto",
        help="Benchmark evaluation mode. auto => parsed_overlay for workspace, policy_simulation for global.",
    )
    parser.add_argument("--workspace", help="Absolute workspace path for overlay evaluation.")
    parser.add_argument("--cases", default=str(DEFAULT_CASES_PATH), help="Benchmark case file path.")
    parser.add_argument("--only", nargs="*", default=None, help="Optional case IDs to run.")
    parser.add_argument("--json-report", default=str(DEFAULT_JSON_REPORT), help="JSON report output path.")
    parser.add_argument("--md-report", default=str(DEFAULT_MD_REPORT), help="Markdown report output path.")
    return parser.parse_args()


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def require_file(path: Path) -> None:
    if not path.exists():
        raise SystemExit(f"Missing required file: {path}")


def ensure_type(name: str, value: object, expected: type) -> None:
    if not isinstance(value, expected):
        raise SystemExit(f"{name} expected {expected.__name__}, got {type(value).__name__}")


def validate_schema_required(schema: dict, payload: dict, payload_name: str) -> None:
    required = schema.get("required", [])
    for field in required:
        if field not in payload:
            raise SystemExit(f"{payload_name} missing required field: {field}")


def validate_case(case: dict, schema: dict) -> None:
    validate_schema_required(schema, case, f"case[{case.get('id', '?')}]")
    ensure_type("case.id", case["id"], str)
    ensure_type("case.category", case["category"], str)
    ensure_type("case.prompt", case["prompt"], str)
    ensure_type("case.required_mode", case["required_mode"], str)
    ensure_type("case.expected_flow", case["expected_flow"], list)
    ensure_type("case.acceptance_checks", case["acceptance_checks"], list)
    ensure_type("case.network_needed", case["network_needed"], bool)
    ensure_type("case.workspace_sensitivity", case["workspace_sensitivity"], str)
    ensure_type("case.notes", case["notes"], str)
    if "workspace" in case:
        ensure_type("case.workspace", case["workspace"], str)


def compute_route_match(expected: list[str], actual: list[str]) -> bool:
    return expected == actual


def simulate_case(case: dict, global_defaults: dict, overlay: dict, scope: str, benchmark_kind: str) -> dict:
    start = time.perf_counter()
    global_flow = global_defaults["workflow_defaults"]["non_trivial_sequence"]
    trivial_flow = ["main"]
    required_mode = case["required_mode"]
    expected_flow = case["expected_flow"]

    if required_mode == "trivial":
        global_actual = trivial_flow
    else:
        global_actual = list(global_flow)

    overlay_actual = list(global_actual)
    intervention_reasons = manual_intervention_reasons(case, overlay, scope, benchmark_kind)
    manual_intervention = bool(intervention_reasons)

    elapsed = round(time.perf_counter() - start, 6)
    global_route_match = compute_route_match(expected_flow, global_actual)
    overlay_route_match = compute_route_match(expected_flow, overlay_actual)
    global_success = global_route_match
    overlay_success = overlay_route_match and not manual_intervention

    global_result = {
        "success": global_success,
        "route_match": global_route_match,
        "flow": global_actual,
        "wall_time_sec": elapsed,
        "tool_calls": len(global_actual),
        "manual_intervention": False,
    }
    overlay_result = {
        "success": overlay_success,
        "route_match": overlay_route_match,
        "flow": overlay_actual,
        "wall_time_sec": elapsed,
        "tool_calls": len(overlay_actual),
        "manual_intervention": manual_intervention,
        "manual_intervention_reasons": intervention_reasons,
        "overlay_depth": overlay["overlay_depth"],
        "has_agents_md": overlay["has_agents_md"],
        "has_principles_md": overlay["has_principles_md"],
        "parsed_signals": overlay["parsed_signals"],
        "signal_sources": overlay["signal_sources"],
        "strictness_score": overlay["strictness_score"],
    }
    delta = {
        "success_changed": global_result["success"] != overlay_result["success"],
        "route_changed": global_result["route_match"] != overlay_result["route_match"],
        "manual_intervention_changed": global_result["manual_intervention"] != overlay_result["manual_intervention"],
    }
    return {
        "id": case["id"],
        "category": case["category"],
        "workspace": case.get("workspace"),
        "required_mode": case["required_mode"],
        "global_default_result": global_result,
        "workspace_overlay_result": overlay_result,
        "delta": delta,
    }


def build_overlay_summary(results: list[dict], benchmark_kind: str) -> dict:
    summaries: dict[str, dict] = {}
    for item in results:
        workspace = item["workspace"]
        overlay_result = item["workspace_overlay_result"]
        if workspace not in summaries:
            summaries[workspace] = {
                "workspace": workspace,
                "has_agents_md": overlay_result["has_agents_md"],
                "has_principles_md": overlay_result["has_principles_md"],
                "overlay_depth": overlay_result["overlay_depth"],
                "strictness_score": overlay_result.get("strictness_score", 0),
                "parsed_signals": overlay_result.get("parsed_signals", []),
                "signal_sources": overlay_result.get("signal_sources", {}),
            }
    return {
        "mode": benchmark_kind,
        "workspaces": list(summaries.values()),
    }


def summarize(results: list[dict], scope: str, workspace: str, benchmark_kind: str) -> dict:
    result_key = "global_default_result" if scope == "global" else "workspace_overlay_result"
    passed = sum(1 for r in results if r[result_key]["success"])
    failed = len(results) - passed
    route_matches = sum(1 for r in results if r[result_key]["route_match"])
    manual_interventions = sum(1 for r in results if r[result_key]["manual_intervention"])
    wall_times = [r[result_key]["wall_time_sec"] for r in results] or [0.0]
    tool_calls = [r[result_key]["tool_calls"] for r in results] or [0]

    failure_counter: dict[str, int] = {}
    for item in results:
        if item[result_key]["success"]:
            continue
        if item[result_key]["manual_intervention"]:
            manual_reasons = item[result_key].get("manual_intervention_reasons", [])
            if manual_reasons:
                reason = "manual_intervention_required:" + "+".join(manual_reasons)
            else:
                reason = "manual_intervention_required"
        else:
            reason = "route_mismatch"
        failure_counter[reason] = failure_counter.get(reason, 0) + 1

    failure_reasons = [{"reason": key, "count": value} for key, value in sorted(failure_counter.items(), key=lambda kv: (-kv[1], kv[0]))]
    return {
        "timestamp": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "benchmark_kind": benchmark_kind,
        "suite_version": "1.1.0",
        "scope": scope,
        "workspace": workspace,
        "passed": passed,
        "failed": failed,
        "task_success_rate": round(passed / len(results), 6) if results else 0.0,
        "route_match_rate": round(route_matches / len(results), 6) if results else 0.0,
        "manual_intervention_rate": round(manual_interventions / len(results), 6) if results else 0.0,
        "median_wall_time_sec": round(float(statistics.median(wall_times)), 6),
        "avg_tool_calls": round(sum(tool_calls) / len(tool_calls), 6),
        "failure_reasons": failure_reasons,
        "case_results": results,
        "overlay_summary": build_overlay_summary(results, benchmark_kind),
    }


def validate_report(report: dict, schema: dict) -> None:
    validate_schema_required(schema, report, "benchmark report")


def to_markdown(report: dict) -> str:
    lines: list[str] = []
    lines.append("# Agent Benchmark Baseline")
    lines.append("")
    lines.append(f"- Timestamp: `{report['timestamp']}`")
    lines.append(f"- Benchmark kind: `{report['benchmark_kind']}`")
    lines.append(f"- Scope: `{report['scope']}`")
    lines.append(f"- Workspace: `{report['workspace']}`")
    lines.append(f"- Passed: `{report['passed']}`")
    lines.append(f"- Failed: `{report['failed']}`")
    lines.append(f"- task_success_rate: `{report['task_success_rate']}`")
    lines.append(f"- route_match_rate: `{report['route_match_rate']}`")
    lines.append(f"- manual_intervention_rate: `{report['manual_intervention_rate']}`")
    lines.append(f"- median_wall_time_sec: `{report['median_wall_time_sec']}`")
    lines.append(f"- avg_tool_calls: `{report['avg_tool_calls']}`")
    lines.append("")
    if "overlay_summary" in report:
        lines.append("## Overlay Summary")
        lines.append("| workspace | has_agents_md | has_principles_md | overlay_depth | strictness_score | parsed_signals |")
        lines.append("| --- | --- | --- | --- | --- | --- |")
        for item in report["overlay_summary"]["workspaces"]:
            signals = ", ".join(item.get("parsed_signals", [])) or "none"
            lines.append(
                f"| `{item['workspace']}` | `{item['has_agents_md']}` | `{item['has_principles_md']}` | "
                f"`{item['overlay_depth']}` | `{item.get('strictness_score', 0)}` | `{signals}` |"
            )
        lines.append("")
    lines.append("## Failure Reasons")
    if report["failure_reasons"]:
        for item in report["failure_reasons"]:
            lines.append(f"- `{item['reason']}`: `{item['count']}`")
    else:
        lines.append("- none")
    lines.append("")
    lines.append("## Case Summary")
    lines.append("| id | category | global_success | overlay_success | delta_success | delta_manual_intervention |")
    lines.append("| --- | --- | --- | --- | --- | --- |")
    for item in report["case_results"]:
        lines.append(
            f"| `{item['id']}` | `{item['category']}` | "
            f"`{item['global_default_result']['success']}` | "
            f"`{item['workspace_overlay_result']['success']}` | "
            f"`{item['delta']['success_changed']}` | "
            f"`{item['delta']['manual_intervention_changed']}` |"
        )
    lines.append("")
    return "\n".join(lines)


def resolve_case_workspace(case: dict, workspace_override: str | None) -> Path:
    if workspace_override:
        return Path(workspace_override).expanduser().resolve()
    if case.get("workspace"):
        return Path(case["workspace"]).expanduser().resolve()
    return ROOT


def main() -> int:
    args = parse_args()
    benchmark_kind = resolve_benchmark_kind(args.scope, args.benchmark_kind)

    global_defaults_path = POLICY_DIR / "global_agent_defaults.json"
    case_schema_path = POLICY_DIR / "benchmark_case_schema.json"
    report_schema_path = POLICY_DIR / "benchmark_report_schema.json"
    cases_path = Path(args.cases).expanduser().resolve()
    json_report_path = Path(args.json_report).expanduser().resolve()
    md_report_path = Path(args.md_report).expanduser().resolve()

    for path in (global_defaults_path, case_schema_path, report_schema_path, cases_path):
        require_file(path)

    global_defaults = load_json(global_defaults_path)
    case_schema = load_json(case_schema_path)
    report_schema = load_json(report_schema_path)
    cases = load_json(cases_path)
    ensure_type("cases payload", cases, list)
    for case in cases:
        ensure_type("case item", case, dict)
        validate_case(case, case_schema)

    selected = set(args.only or [])
    if selected:
        cases = [case for case in cases if case["id"] in selected]
        if not cases:
            raise SystemExit("No benchmark cases matched --only")

    results: list[dict] = []
    workspaces_seen: set[str] = set()
    for case in cases:
        case_workspace = resolve_case_workspace(case, args.workspace)
        overlay = load_overlay(case_workspace, benchmark_kind)
        results.append(simulate_case(case, global_defaults, overlay, args.scope, benchmark_kind))
        results[-1]["workspace"] = str(case_workspace)
        workspaces_seen.add(str(case_workspace))

    if args.workspace:
        workspace_label = str(Path(args.workspace).expanduser().resolve())
    elif len(workspaces_seen) == 1:
        workspace_label = next(iter(workspaces_seen))
    else:
        workspace_label = "per-case"

    report = summarize(results, args.scope, workspace_label, benchmark_kind)
    validate_report(report, report_schema)

    json_report_path.parent.mkdir(parents=True, exist_ok=True)
    md_report_path.parent.mkdir(parents=True, exist_ok=True)
    json_report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_report_path.write_text(to_markdown(report), encoding="utf-8")

    print(f"cases={len(cases)} passed={report['passed']} failed={report['failed']}")
    print(f"json_report={json_report_path}")
    print(f"md_report={md_report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
