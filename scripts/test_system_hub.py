#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import json
import os
import shlex
import shutil
import sqlite3
import subprocess
import tempfile
import time
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def write_file(path: Path, text: str, executable: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    if executable:
        path.chmod(0o755)


def require_hub_runtime() -> tuple[Path, Path]:
    system_hub = ROOT / "scripts" / "system_hub.py"
    brain = ROOT / "scripts" / "brain.sh"
    assert_true(system_hub.exists(), f"Missing required runtime: {system_hub}")
    assert_true(brain.exists(), f"Missing required runtime: {brain}")
    return system_hub, brain


def stub_run_agent_benchmark() -> str:
    return """#!/usr/bin/env python3
import json, pathlib, sys
args = sys.argv[1:]
def val(flag, default):
    if flag in args:
        i = args.index(flag)
        if i + 1 < len(args):
            return args[i + 1]
    return default
json_path = pathlib.Path(val("--json-report", "contexts/agent_benchmark_baseline_workspace.json"))
md_path = pathlib.Path(val("--md-report", "contexts/agent_benchmark_baseline_workspace.md"))
json_path.parent.mkdir(parents=True, exist_ok=True)
md_path.parent.mkdir(parents=True, exist_ok=True)
json_path.write_text(json.dumps({"ok": True}, ensure_ascii=False), encoding="utf-8")
md_path.write_text("# benchmark\\n", encoding="utf-8")
print("stub benchmark done")
"""


def stub_run_router_regression() -> str:
    return """#!/usr/bin/env python3
import json, pathlib, sys
args = sys.argv[1:]
out = pathlib.Path("contexts/router_regression_latest.json")
if "--json-report" in args:
    i = args.index("--json-report")
    if i + 1 < len(args):
        out = pathlib.Path(args[i + 1])
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps({"summary": "11/11"}, ensure_ascii=False), encoding="utf-8")
print("stub router done")
"""


def stub_build_skill_graph() -> str:
    return """#!/usr/bin/env python3
import pathlib, sys
args = sys.argv[1:]
def val(flag, default):
    if flag in args:
        i = args.index(flag)
        if i + 1 < len(args):
            return args[i + 1]
    return default
primary = pathlib.Path(val("--output", "contexts/skill_graph_primary.md"))
mirror = pathlib.Path(val("--mirror-output", "contexts/skill_graph.md"))
primary.parent.mkdir(parents=True, exist_ok=True)
mirror.parent.mkdir(parents=True, exist_ok=True)
primary.write_text("# skill graph\\n", encoding="utf-8")
mirror.write_text("# skill graph\\n", encoding="utf-8")
print("entries=5 unique=5")
"""


def stub_publish_agent_policy() -> str:
    return """#!/usr/bin/env python3
import argparse, json, pathlib
parser = argparse.ArgumentParser()
parser.add_argument("--codex-home", default="")
parser.add_argument("--dry-run", action="store_true")
args = parser.parse_args()
target_dir = pathlib.Path(args.codex_home or pathlib.Path.home() / ".codex") / "agent_policy"
manifest = {"target_dir": str(target_dir), "dry_run": args.dry_run}
if args.dry_run:
    print(json.dumps(manifest, ensure_ascii=False))
else:
    target_dir.mkdir(parents=True, exist_ok=True)
    (target_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
    print(f"published_to={target_dir}")
"""


def stub_test_run_agent_benchmark() -> str:
    return """#!/usr/bin/env python3
print("agent benchmark regression checks passed")
"""


def stub_continuity_entrypoint() -> str:
    return """#!/usr/bin/env bash
set -euo pipefail
echo "codex_continue_here"
"""


def stub_session_ckpt(daily_payload_path: Path, weekly_payload_path: Path) -> str:
    return f"""#!/usr/bin/env python3
import json, pathlib, sys

args = sys.argv[1:]
if not args:
    sys.exit(0)
cmd = args[0]
if cmd == "recent-memory":
    days = 14
    if "--days" in args:
        i = args.index("--days")
        if i + 1 < len(args):
            days = int(args[i + 1])
    payload_path = pathlib.Path({json.dumps(str(daily_payload_path))})
    if days >= 30:
        payload_path = pathlib.Path({json.dumps(str(weekly_payload_path))})
    sys.stdout.write(payload_path.read_text(encoding="utf-8"))
    sys.exit(0)
if cmd == "recall":
    target = pathlib.Path(".").resolve()
    lane = ""
    if "--dir" in args:
        i = args.index("--dir")
        if i + 1 < len(args):
            target = pathlib.Path(args[i + 1]).resolve()
    if "--lane" in args:
        i = args.index("--lane")
        if i + 1 < len(args):
            lane = args[i + 1]
    overlay_registry = pathlib.Path("contexts/runtime_overlay_registry.json")
    skill_registry = pathlib.Path("contexts/skill_iteration_registry.json")
    selected = {{}}
    candidates = []
    if overlay_registry.exists():
        payload = json.loads(overlay_registry.read_text(encoding="utf-8"))
        for entry in payload.get("entries", []):
            if isinstance(entry, dict) and entry.get("target_path") == str(target):
                selected = {{
                    "source": "overlay",
                    "source_path": entry.get("brief_path", ""),
                    "summary": f"Continue the existing {{entry.get('mode', 'analysis')}} overlay.",
                    "next_step": "Use the existing runtime overlay as the starting brief.",
                    "event_time": entry.get("generated_at", ""),
                    "updated_at": entry.get("generated_at", ""),
                    "rank_explanation": "intent=200, salience=60, recency=80, source_priority=4",
                    "lane": entry.get("mode", lane or "analysis"),
                }}
                candidates.append(selected)
                break
    if skill_registry.exists():
        payload = json.loads(skill_registry.read_text(encoding="utf-8"))
        closeouts = payload.get("closeouts", [])
        if isinstance(closeouts, list):
            for entry in reversed(closeouts):
                if isinstance(entry, dict) and entry.get("target_path") == str(target):
                    candidates.append({{
                        "source": "closeout",
                        "source_path": entry.get("overlay_brief_path", ""),
                        "summary": entry.get("summary", ""),
                        "next_step": entry.get("summary", ""),
                        "event_time": entry.get("generated_at", ""),
                        "updated_at": entry.get("generated_at", ""),
                        "rank_explanation": "intent=120, salience=50, recency=80, source_priority=4",
                        "lane": entry.get("mode", lane or "analysis"),
                    }})
                    break
    payload = {{
        "scope": {{"current_dir": str(target), "lane": lane or "default"}},
        "workspace_memory": {{}},
        "project_worklog": {{}},
        "intent_context": {{"requested_lane": lane or "default", "mode": lane or "analysis", "closeout_summary": ""}},
        "continuation": {{"selected": selected, "candidates": candidates}},
        "evidence": [],
    }}
    sys.stdout.write(json.dumps(payload, ensure_ascii=False))
    sys.exit(0)
sys.exit(0)
"""


def benchmark_cases_payload() -> str:
    return json.dumps(
        [
            {
                "id": "meta_contract_refresh",
                "category": "meta-workspace",
                "prompt": "Refresh benchmark outputs.",
                "required_mode": "review",
                "expected_flow": ["explorer", "worker", "reviewer", "main"],
                "acceptance_checks": ["report files generated"],
                "network_needed": False,
                "workspace_sensitivity": "high",
                "notes": "fixture",
                "workspace": "/tmp/workspace",
            }
        ],
        ensure_ascii=False,
        indent=2,
    ) + "\n"


def team_alias_registry_payload() -> str:
    return json.dumps(
        {
            "version": "test",
            "aliases": [
                {
                    "id": "roster",
                    "aliases": ["Roster", "@roster"],
                    "entity_type": "artifact_coordination_surface",
                    "status": "active_local_alias",
                    "target_route": "artifact_harness_workflow",
                    "workflow_stage": "Artifact Harness SPEC",
                },
                {
                    "id": "project_manager_alias",
                    "aliases": ["PM"],
                    "entity_type": "natural_language_alias",
                    "status": "active_local_alias",
                    "target_route": "artifact_harness_workflow",
                    "workflow_stage": "Artifact Harness SPEC",
                    "requires_leading_invocation": True,
                    "requires_artifact_context": True,
                },
                {
                    "id": "human_resources",
                    "aliases": ["HR", "Human Resources", "ask HR", "route to HR"],
                    "entity_type": "team_surface",
                    "status": "active_local_alias",
                }
            ],
            "keyword_families": [
                {
                    "id": "artifact_harness_workflow",
                    "keywords": ["packet form", "Artifact Harness", "Harness SPEC", "requirement form", "form fill", "artifact packet", "artifact mission"],
                    "entrypoint": "scripts/brain.sh artifact-harness",
                    "target_workflow": "user mission -> Artifact Harness SPEC -> HR staffing -> Team Operating Packet -> Capability Access Packet -> runtime mapping -> verification/review",
                    "packet_root": "contexts/artifact_harness_runs",
                    "status": "active_local_keyword_family",
                },
                {
                    "id": "team_architect_packet",
                    "keywords": ["Team Architect", "Team Operating Packet", "operating packet", "task graph", "collaboration pattern"],
                    "target_workflow_stage": "Team Operating Packet",
                    "status": "active_local_keyword_family",
                },
                {
                    "id": "capability_access_packet",
                    "keywords": ["Capability Access Packet", "CAP", "tool authorization", "skill authorization", "plugin authorization", "approval gates", "runtime allowlist"],
                    "target_workflow_stage": "Capability Access Packet",
                    "status": "active_local_keyword_family",
                },
                {
                    "id": "runtime_mapping",
                    "keywords": ["runtime mapping", "runTasks mapping", "open-multi-agent mapping", "runtime adapter"],
                    "target_workflow_stage": "runtime mapping",
                    "status": "active_local_keyword_family",
                },
            ],
        },
        ensure_ascii=False,
        indent=2,
    ) + "\n"


def recent_memory_payload(root: Path, *, days: int, top: int, folders: list[dict[str, object]] | None = None) -> dict:
    if folders is None:
        selected = [
            {
                "folder": str((root / "analysis_runtime").resolve()),
                "activity": {"updated_at": "2026-03-11T10:00:00+00:00"},
                "sync": {
                    "entry": {
                        "report_path": str((root / "FOLDER_PROGRESS_analysis_runtime_20260311-100000.md").resolve())
                    }
                },
            },
            {
                "folder": str((root / "writing_case").resolve()),
                "activity": {"updated_at": "2026-03-11T09:30:00+00:00"},
                "sync": {},
            },
            {
                "folder": str((root / "meeting_case").resolve()),
                "activity": {"updated_at": "2026-03-11T09:00:00+00:00"},
                "sync": {},
            },
        ]
    else:
        selected = folders
    return {
        "root": str(root.resolve()),
        "days": days,
        "top": top,
        "lane": "default",
        "selected_count": len(selected),
        "selected_folders": selected,
        "dry_run": False,
    }


def write_recent_memory_fixture(ws: Path, window: str, payload: dict) -> None:
    codex_home = ws.parent / "external" / "codex_home"
    target = codex_home / "recent_memory" / f"{window}.json"
    write_file(target, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def seed_thread(ws: Path, thread_id: str, *, title: str, cwd: Path, updated_at_epoch: int, archived: bool = False) -> None:
    codex_home = ws.parent / "external" / "codex_home"
    index_path = codex_home / "session_index.jsonl"
    records = []
    if index_path.exists():
        for line in index_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                records.append(json.loads(line))
    records = [record for record in records if record.get("id") != thread_id]
    records.append(
        {
            "id": thread_id,
            "thread_name": title,
            "updated_at": updated_at_epoch,
        }
    )
    records.sort(key=lambda item: item["id"])
    write_file(index_path, "\n".join(json.dumps(record, ensure_ascii=False) for record in records) + "\n")

    db_path = codex_home / "state_5.sqlite"
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS threads (
                id TEXT PRIMARY KEY,
                title TEXT,
                cwd TEXT,
                archived INTEGER,
                updated_at INTEGER,
                created_at INTEGER
            )
            """
        )
        conn.execute("DELETE FROM threads WHERE id = ?", (thread_id,))
        conn.execute(
            "INSERT INTO threads (id, title, cwd, archived, updated_at, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (thread_id, title, str(cwd.resolve()), 1 if archived else 0, updated_at_epoch, updated_at_epoch - 3600),
        )
        conn.commit()
    finally:
        conn.close()


def write_session_index_only(ws: Path, thread_id: str, *, title: str, updated_at_epoch: int) -> None:
    codex_home = ws.parent / "external" / "codex_home"
    index_path = codex_home / "session_index.jsonl"
    records = []
    if index_path.exists():
        for line in index_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                records.append(json.loads(line))
    records = [record for record in records if record.get("id") != thread_id]
    records.append(
        {
            "id": thread_id,
            "thread_name": title,
            "updated_at": updated_at_epoch,
        }
    )
    records.sort(key=lambda item: item["id"])
    write_file(index_path, "\n".join(json.dumps(record, ensure_ascii=False) for record in records) + "\n")


def work_modes_config() -> str:
    return """
[mode.analysis.file_hints]
extensions = [".csv", ".tsv", ".xlsx", ".xls", ".parquet", ".ipynb", ".jsonl"]
keywords = ["analysis", "dataset", "results", "model", "stat", "quality", "品保"]
path_keywords = ["data", "dataset", "analysis", "results", "tables"]

[mode.analysis]
active_skills = ["spreadsheet", "xlsx", "polars", "statsmodels", "statistical-analysis"]
fallback_skills = ["scikit-learn", "scikit-survival", "matplotlib"]
output_contract = [
  "State dataset assumptions and changed inputs explicitly.",
  "Prefer concise statistical wording over ornate vocabulary.",
  "Keep steps reproducible and scoped to the current dataset version."
]
session_preamble = "Operate as an analysis-focused session. Prefer continuity over redesign, and keep the current dataset version explicit."
escalation_triggers = [
  "Method changes would break comparability with prior dataset versions.",
  "The folder looks like a new dataset drop for an existing recurring pipeline.",
  "The requested output would change the established analysis deliverable format."
]

[mode.writing.file_hints]
extensions = [".md", ".pdf", ".docx", ".tex", ".bib"]
keywords = ["draft", "paper", "manuscript", "section", "outline", "writing", "review"]
path_keywords = ["draft", "paper", "writing", "sections", "citations"]

[mode.writing]
active_skills = ["research-assistant", "citation-management", "content-research-writer", "internal-comms"]
fallback_skills = ["draft-polisher", "humanizer", "obsidian-markdown"]
output_contract = [
  "Use plain academic wording and avoid rare or showy vocabulary.",
  "Keep claims close to the available source material.",
  "Prefer short, easy-to-scan paragraphs and explicit next edits."
]
session_preamble = "Operate as a writing session. Keep wording plain, keep claims close to sources, and prefer concrete revision steps over stylistic drift."
escalation_triggers = [
  "The request needs new sources or evidence that the current folder does not contain.",
  "The requested writing voice conflicts with the current academic/plain-language contract.",
  "The draft appears to belong to another paper or workspace and may need a separate session."
]

[mode.math_check.file_hints]
extensions = [".tex", ".ipynb", ".md", ".pdf", ".png", ".jpg"]
keywords = ["math", "proof", "derivation", "equation", "kernel", "vis_math"]
path_keywords = ["math", "derivation", "figures", "proofs"]

[mode.math_check]
active_skills = ["statistical-analysis", "statsmodels", "matplotlib", "verification-loop"]
fallback_skills = ["networkx", "research-assistant"]
output_contract = [
  "Prefer checkable derivation steps over long prose.",
  "Make notation explicit and verify what is visible on the page.",
  "Call out mismatches between equations, figures, and text directly."
]
session_preamble = "Operate as a math-check session. Favor explicit derivations, notation checks, and visible-page verification over narrative explanation."
escalation_triggers = [
  "Notation is inconsistent across equations, figures, or surrounding prose.",
  "The request needs proof-level rigor beyond the visible derivation context.",
  "A figure or rendered page appears inconsistent with the mathematical statement."
]

[mode.meeting.file_hints]
extensions = [".md", ".pdf", ".docx", ".pptx"]
keywords = ["meeting", "agenda", "minutes", "prof", "conference", "admin"]
path_keywords = ["meeting", "minutes", "agenda", "conference"]

[mode.meeting]
active_skills = ["obsidian-markdown", "internal-comms", "research-assistant"]
fallback_skills = ["docx", "pptx"]
output_contract = [
  "Capture decisions, owners, and next steps explicitly.",
  "Keep equations in math syntax: inline `$...$`, block `$$...$$`.",
  "Separate factual notes from your interpretation."
]
session_preamble = "Operate as a meeting session. Separate facts from interpretation and keep decisions, owners, and next steps explicit."
escalation_triggers = [
  "The note mixes multiple meetings or agendas that should be split.",
  "Action items are missing owners or deadlines.",
  "Math or technical notation is being written as code spans instead of TeX."
]

[mode.course.file_hints]
extensions = [".md", ".pdf", ".ipynb", ".pptx", ".docx"]
keywords = ["course", "lecture", "class", "homework", "assignment", "machinelearning"]
path_keywords = ["course", "lecture", "homework", "assignment", "syllabus"]

[mode.course]
active_skills = ["obsidian-markdown", "jupyter-notebook", "research-assistant", "spreadsheet"]
fallback_skills = ["docx", "pptx", "content-research-writer"]
output_contract = [
  "Keep lecture notes, assignments, and references distinct.",
  "Use `$...$` and `$$...$$` for math; never backticks for equations.",
  "Summaries should preserve definitions, assumptions, and unresolved questions."
]
session_preamble = "Operate as a course session. Keep lecture content, assignments, and references separate, and preserve unresolved questions explicitly."
escalation_triggers = [
  "Lecture notes, homework, and reference material are collapsing into one undifferentiated note.",
  "Equation formatting is being mixed with code formatting.",
  "The request spans multiple courses or semesters and should be split."
]

[inventory]
cold_skills = ["youtube-downloader", "slack-gif-creator"]
""".strip() + "\n"


def make_skill(root: Path, name: str) -> None:
    write_file(root / name / "SKILL.md", f"# {name}\n")


def make_workspace(
    tmp: Path,
    *,
    missing_bridge_state: bool = False,
    missing_vault_checkpoint: bool = False,
    missing_skill_root: bool = False,
    invalid_toml: bool = False,
    include_folder_only_artifact: bool = False,
    seed_canonical_outputs: bool = False,
) -> Path:
    ws = tmp / "ws"
    scripts_dir = ws / "scripts"
    policy_dir = ws / "policy"
    contexts_dir = ws / "contexts"
    ext = tmp / "external"

    scripts_dir.mkdir(parents=True, exist_ok=True)
    policy_dir.mkdir(parents=True, exist_ok=True)
    contexts_dir.mkdir(parents=True, exist_ok=True)

    system_hub, brain = require_hub_runtime()
    shutil.copy2(system_hub, scripts_dir / "system_hub.py")
    shutil.copy2(brain, scripts_dir / "brain.sh")
    test_runtime = ROOT / "scripts" / "test_system_hub.py"
    if test_runtime.exists():
        shutil.copy2(test_runtime, scripts_dir / "test_system_hub.py")
    roster_skill_source = ROOT / "skills" / "roster"
    if roster_skill_source.exists():
        shutil.copytree(roster_skill_source, ws / "skills" / "roster")
    (scripts_dir / "brain.sh").chmod(0o755)
    (scripts_dir / "system_hub.py").chmod(0o755)

    write_file(scripts_dir / "run_agent_benchmark.py", stub_run_agent_benchmark(), executable=True)
    write_file(
        scripts_dir / "run_agent_benchmark.sh",
        "#!/usr/bin/env bash\nset -euo pipefail\npython3 \"$(dirname \"$0\")/run_agent_benchmark.py\" \"$@\"\n",
        executable=True,
    )
    write_file(scripts_dir / "publish_agent_policy.py", stub_publish_agent_policy(), executable=True)
    write_file(scripts_dir / "test_run_agent_benchmark.py", stub_test_run_agent_benchmark(), executable=True)
    write_file(scripts_dir / "codex_continue_here", stub_continuity_entrypoint(), executable=True)
    write_file(scripts_dir / "build_skill_graph.py", stub_build_skill_graph(), executable=True)
    write_file(scripts_dir / "run_router_regression.py", stub_run_router_regression(), executable=True)
    write_file(
        scripts_dir / "run_router_regression.sh",
        "#!/usr/bin/env bash\nset -euo pipefail\npython3 \"$(dirname \"$0\")/run_router_regression.py\" \"$@\"\n",
        executable=True,
    )

    write_file(ws / "AGENTS.md", "# AGENTS\n")
    write_file(ws / "PRINCIPLES.md", "# PRINCIPLES\n")
    write_file(ws / "obsidian_codex_bridge.py", "# bridge\n")
    write_file(contexts_dir / "research.md", "# research\n")
    write_file(contexts_dir / "writing.md", "# writing\n")
    write_file(contexts_dir / "review.md", "# review\n")
    write_file(contexts_dir / "agent_benchmark_cases.json", benchmark_cases_payload())
    write_file(contexts_dir / "team_alias_registry.json", team_alias_registry_payload())
    write_file(policy_dir / "work_modes.toml", work_modes_config())
    for name in (
        "GLOBAL_OPERATING_MODEL.md",
        "RESOURCE_TAXONOMY.md",
        "global_agent_defaults.json",
        "agent_contract_schema.json",
        "benchmark_case_schema.json",
        "benchmark_report_schema.json",
    ):
        payload = "{}\n" if name.endswith(".json") else f"# {name}\n"
        write_file(policy_dir / name, payload)

    codex_home = ext / "codex_home"
    skill_codex = codex_home / "skills"
    skill_agents = ext / "agents_skills"
    vault = ext / "vault"
    checkpoint_root = vault / "00_system" / "checkpoints"
    state_dir = checkpoint_root / ".state"
    automation_root = codex_home / "automations"
    bridge_state = state_dir / "codex_bridge_state.json"
    active_state = state_dir / "active_session.json"
    codex_ckpt = ext / "bin" / "codex_ckpt"
    session_ckpt = ext / "bin" / "session_ckpt"
    recent_memory_dir = codex_home / "recent_memory"

    if not missing_skill_root:
        skill_codex.mkdir(parents=True, exist_ok=True)
        skill_agents.mkdir(parents=True, exist_ok=True)
    else:
        skill_codex.mkdir(parents=True, exist_ok=True)

    for name in (
        "spreadsheet",
        "xlsx",
        "polars",
        "statsmodels",
        "statistical-analysis",
        "research-assistant",
        "citation-management",
        "content-research-writer",
        "internal-comms",
        "obsidian-markdown",
        "jupyter-notebook",
        "matplotlib",
        "verification-loop",
        "docx",
        "pptx",
    ):
        make_skill(skill_codex, name)
    if not missing_skill_root:
        make_skill(skill_agents, "data-engineering-data-pipeline")

    if not missing_vault_checkpoint:
        state_dir.mkdir(parents=True, exist_ok=True)
        if not missing_bridge_state:
            write_file(bridge_state, "{}\n")
        write_file(active_state, "{}\n")
    automation_root.mkdir(parents=True, exist_ok=True)
    recent_memory_dir.mkdir(parents=True, exist_ok=True)
    write_recent_memory_fixture(ws, "daily", recent_memory_payload(ws, days=14, top=3))
    write_recent_memory_fixture(
        ws,
        "weekly",
        recent_memory_payload(
            ws,
            days=30,
            top=5,
            folders=[
                {
                    "folder": str((ws / "analysis_runtime").resolve()),
                    "activity": {"updated_at": "2026-03-11T10:00:00+00:00"},
                    "sync": {
                        "entry": {
                            "report_path": str((ws / "FOLDER_PROGRESS_analysis_runtime_20260311-100000.md").resolve())
                        }
                    },
                },
                {
                    "folder": str((ws / "writing_case").resolve()),
                    "activity": {"updated_at": "2026-03-10T09:30:00+00:00"},
                    "sync": {},
                },
                {
                    "folder": str((ws / "meeting_case").resolve()),
                    "activity": {"updated_at": "2026-03-09T09:00:00+00:00"},
                    "sync": {},
                },
                {
                    "folder": str((ws / "course_case").resolve()),
                    "activity": {"updated_at": "2026-03-08T09:00:00+00:00"},
                    "sync": {},
                },
                {
                    "folder": str((ws / "archive_case").resolve()),
                    "activity": {"updated_at": "2026-03-07T09:00:00+00:00"},
                    "sync": {},
                },
            ],
        ),
    )
    write_file(
        automation_root / "phd-daily-memory" / "automation.toml",
        'name = "Daily memory"\nprompt = "Run `./scripts/brain.sh memory-triage --window daily --root /Users/tom/Documents/PHD`. Summarize selected_count, bucket counts, durable folders, archive candidates, and generated report paths. If selected_count is 0, say that explicitly."\n',
    )
    write_file(
        automation_root / "phd-weekly-memory" / "automation.toml",
        'name = "Weekly memory"\nprompt = "Run `./scripts/brain.sh memory-triage --window weekly --root /Users/tom/Documents/PHD`. Summarize selected_count, bucket counts, durable folders, archive candidates, generated report paths, and weekly durable-set drift."\n',
    )
    write_file(codex_ckpt, "#!/usr/bin/env bash\nexit 0\n", executable=True)
    write_file(session_ckpt, stub_session_ckpt(recent_memory_dir / "daily.json", recent_memory_dir / "weekly.json"), executable=True)
    write_file(codex_home / "session_index.jsonl", "")
    conn = sqlite3.connect(codex_home / "state_5.sqlite")
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS threads (
                id TEXT PRIMARY KEY,
                title TEXT,
                cwd TEXT,
                archived INTEGER,
                updated_at INTEGER,
                created_at INTEGER
            )
            """
        )
        conn.commit()
    finally:
        conn.close()

    if invalid_toml:
        write_file(policy_dir / "system_hub.toml", "[workspace\nroot = \"broken\"\n")
    else:
        config = f"""
[workspace]
root = "{ws}"

[paths]
policy_dir = "{policy_dir}"
contexts_dir = "{contexts_dir}"
scripts_dir = "{scripts_dir}"
codex_home = "{codex_home}"
skill_roots = ["{skill_codex}", "{skill_agents}"]
vault_path = "{vault}"
checkpoint_root = "{checkpoint_root}"
bridge_state = "{bridge_state}"
active_session_state = "{active_state}"
automation_root = "{automation_root}"
codex_ckpt_cmd = "{codex_ckpt}"
session_ckpt_cmd = "{session_ckpt}"

[freshness]
system_hours = 24
generated_hours = 24
report_hours = 24

[routing]
team_alias_registry = "{contexts_dir / "team_alias_registry.json"}"
prefer_named_team_aliases = true
artifact_harness_entrypoint = "artifact-harness"
packet_route_entrypoint = "packet-route"
artifact_harness_packet_root = "contexts/artifact_harness_runs"
artifact_harness_keywords = ["packet form", "artifact harness", "harness spec"]
"""
        write_file(policy_dir / "system_hub.toml", config.strip() + "\n")

    if seed_canonical_outputs:
        write_file(contexts_dir / "system_registry.json", "{\"sentinel\": true}\n")
        write_file(contexts_dir / "system_status.md", "# sentinel status\n")
    if include_folder_only_artifact:
        write_file(contexts_dir / "codex_system_status_20260310.md", "# draft system status\n")
        write_file(contexts_dir / "system_gap_notes.md", "# not integrated yet\n")
        write_file(ws / "FOLDER_PROGRESS_ws_20260311-000000.md", "# folder progress\n")

    write_file(ext / "SENTINEL.txt", "do-not-touch\n")
    return ws


def run_brain(ws: Path, *args: str, extra_env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["CODEX_HOME"] = str((ws.parent / "external" / "codex_home").resolve())
    env["CODEX_INTERNAL_ORIGINATOR_OVERRIDE"] = "Codex Desktop"
    env.setdefault("CODEX_RUNTIME_SHELL_VERSION_OVERRIDE", "0.115.0-alpha.4")
    env.setdefault("CODEX_RUNTIME_DESKTOP_VERSION_OVERRIDE", "0.115.0-alpha.4")
    env.setdefault("CODEX_RUNTIME_DESKTOP_APP_VERSION_OVERRIDE", "26.309.31024")
    if extra_env:
        env.update(extra_env)
    return subprocess.run(
        ["bash", "scripts/brain.sh", *args],
        cwd=ws,
        text=True,
        capture_output=True,
        check=False,
        env=env,
    )


def load_registry(ws: Path) -> dict:
    return json.loads((ws / "contexts" / "system_registry.json").read_text(encoding="utf-8"))


def load_reconciliation_report(ws: Path) -> str:
    return (ws / "contexts" / "folder_hub_reconciliation.md").read_text(encoding="utf-8")


def load_runtime_overlay_registry(ws: Path) -> dict:
    return json.loads((ws / "contexts" / "runtime_overlay_registry.json").read_text(encoding="utf-8"))


def load_skill_iteration_registry(ws: Path) -> dict:
    return json.loads((ws / "contexts" / "skill_iteration_registry.json").read_text(encoding="utf-8"))


def load_skill_discovery_registry(ws: Path) -> dict:
    return json.loads((ws / "contexts" / "skill_discovery_registry.json").read_text(encoding="utf-8"))


def load_skill_route_registry(ws: Path) -> dict:
    return json.loads((ws / "contexts" / "skill_route_registry.json").read_text(encoding="utf-8"))


def load_artifact_harness_registry(ws: Path) -> dict:
    return json.loads((ws / "contexts" / "artifact_harness_registry.json").read_text(encoding="utf-8"))


def set_artifact_harness_packet_root(ws: Path, packet_root: Path) -> None:
    config_path = ws / "policy" / "system_hub.toml"
    original = config_path.read_text(encoding="utf-8")
    config_path.write_text(
        original.replace(
            'artifact_harness_packet_root = "contexts/artifact_harness_runs"',
            f'artifact_harness_packet_root = "{packet_root}"',
            1,
        ),
        encoding="utf-8",
    )


def load_memory_governance_registry(ws: Path) -> dict:
    return json.loads((ws / "contexts" / "memory_governance_registry.json").read_text(encoding="utf-8"))


def load_memory_governance_status(ws: Path) -> str:
    return (ws / "contexts" / "memory_governance_status.md").read_text(encoding="utf-8")


def test_refresh_success_writes_registry_and_status() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-ok-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        result = run_brain(ws, "refresh")
        assert_true(result.returncode == 0, f"refresh expected 0, got {result.returncode}, stderr={result.stderr}")
        assert_true((ws / "contexts" / "system_registry.json").exists(), "refresh should write contexts/system_registry.json")
        assert_true((ws / "contexts" / "system_status.md").exists(), "refresh should write contexts/system_status.md")
        assert_true((ws / "contexts" / "agent_benchmark_baseline_global.json").exists(), "refresh should write global benchmark json")
        assert_true((ws / "contexts" / "agent_benchmark_baseline_global.md").exists(), "refresh should write global benchmark md")
        registry = load_registry(ws)
        assert_true(registry.get("overall_status") == "healthy", "refresh success should produce healthy status")
        assert_true("capability_snapshot" in registry.get("checks", {}), "refresh should include capability snapshot")
        assert_true("agent_benchmark_global" in registry.get("checks", {}), "refresh should include global benchmark check")
        assert_true("agent_benchmark_portability" in registry.get("checks", {}), "refresh should include portability check")
        assert_true(registry["sources"]["policy"]["benchmark_cases"]["exists"], "refresh should track benchmark input cases")
        assert_true(
            registry["sources"]["policy"]["benchmark_publish_chain"]["status"] == "healthy",
            "refresh should track a healthy benchmark publish chain",
        )
        assert_true(
            registry["sources"]["commands"]["continuity_entrypoint"]["exists"],
            "refresh should track the continuity entrypoint",
        )


def test_degraded_skill_root_returns_2() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-skill-degraded-") as tmp_s:
        ws = make_workspace(Path(tmp_s), missing_skill_root=True)
        result = run_brain(ws, "refresh")
        assert_true(result.returncode == 2, f"missing skill root should degrade to exit 2, got {result.returncode}")
        registry = load_registry(ws)
        assert_true(registry.get("overall_status") == "degraded", "missing skill root should mark degraded")


def test_degraded_vault_checkpoint_returns_2_in_doctor() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-vault-degraded-") as tmp_s:
        ws = make_workspace(Path(tmp_s), missing_vault_checkpoint=True)
        result = run_brain(ws, "doctor")
        assert_true(result.returncode == 2, f"missing vault/checkpoint should degrade doctor to 2, got {result.returncode}")


def test_invalid_toml_returns_1() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-invalid-toml-") as tmp_s:
        ws = make_workspace(Path(tmp_s), invalid_toml=True)
        result = run_brain(ws, "doctor")
        assert_true(result.returncode == 1, f"invalid TOML should fail with exit 1, got {result.returncode}")


def test_status_reads_existing_registry_without_live_checks() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-status-only-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        registry_path = ws / "contexts" / "system_registry.json"
        status_path = ws / "contexts" / "system_status.md"
        write_file(registry_path, json.dumps({"overall_status": "healthy", "mode": "status"}, ensure_ascii=False))
        write_file(status_path, "# status\n")
        shutil.rmtree(ws / "scripts")
        (ws / "scripts").mkdir(parents=True, exist_ok=True)
        write_file(
            ws / "scripts" / "brain.sh",
            "#!/usr/bin/env bash\nset -euo pipefail\nROOT_DIR=\"$(cd \"$(dirname \"${BASH_SOURCE[0]}\")/..\" && pwd)\"\nexec python3 \"$ROOT_DIR/scripts/system_hub.py\" \"$@\"\n",
            executable=True,
        )
        shutil.copy2(ROOT / "scripts" / "system_hub.py", ws / "scripts" / "system_hub.py")
        result = run_brain(ws, "status")
        assert_true(result.returncode == 0, f"status should not run live checks, got {result.returncode}")


def test_missing_bridge_state_degrades_not_crash() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-bridge-degraded-") as tmp_s:
        ws = make_workspace(Path(tmp_s), missing_bridge_state=True)
        result = run_brain(ws, "doctor")
        assert_true(result.returncode == 2, f"missing bridge state should degrade with 2, got {result.returncode}")


def test_refresh_does_not_write_outside_repo() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-boundary-") as tmp_s:
        tmp = Path(tmp_s)
        ws = make_workspace(tmp)
        external = tmp / "external"
        before = sorted(p.relative_to(external).as_posix() for p in external.rglob("*") if p.is_file())
        result = run_brain(ws, "refresh")
        assert_true(result.returncode == 0, f"refresh expected 0, got {result.returncode}")
        after = sorted(p.relative_to(external).as_posix() for p in external.rglob("*") if p.is_file())
        assert_true(before == after, "refresh should not create or modify files outside workspace")


def test_intake_works_without_init_and_no_repo_write() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-intake-noinit-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        folder = ws / "incoming"
        folder.mkdir(parents=True, exist_ok=True)
        write_file(folder / "dataset.csv", "x,y\n1,2\n")
        registry_path = ws / "contexts" / "system_registry.json"
        status_path = ws / "contexts" / "system_status.md"
        result = run_brain(ws, "intake", str(folder))
        assert_true(result.returncode == 0, f"intake expected 0, got {result.returncode}, stderr={result.stderr}")
        assert_true("Predicted mode:" in result.stdout, "intake should produce a human-readable summary")
        assert_true(not registry_path.exists(), "intake should not write system_registry.json")
        assert_true(not status_path.exists(), "intake should not write system_status.md")


def test_intake_mode_detection_analysis_folder() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-intake-analysis-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        folder = ws / "analysis_case"
        folder.mkdir(parents=True, exist_ok=True)
        write_file(folder / "dataset.csv", "x,y\n1,2\n")
        write_file(folder / "results.xlsx", "placeholder\n")
        write_file(folder / "output_summary.md", "# summary\n")
        result = run_brain(ws, "intake", str(folder))
        assert_true(result.returncode == 0, f"analysis intake expected 0, got {result.returncode}")
        assert_true("Predicted mode: `analysis`" in result.stdout, "analysis folder should map to analysis mode")
        assert_true("Route strategy: `active_lane`" in result.stdout, "high-confidence analysis should use active lane")


def test_intake_mode_detection_writing_folder() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-intake-writing-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        folder = ws / "writing_case"
        folder.mkdir(parents=True, exist_ok=True)
        write_file(folder / "draft.md", "# draft\n")
        write_file(folder / "paper_review.pdf", "pdf\n")
        result = run_brain(ws, "intake", str(folder))
        assert_true(result.returncode == 0, f"writing intake expected 0, got {result.returncode}")
        assert_true("Predicted mode: `writing`" in result.stdout, "writing folder should map to writing mode")


def test_intake_mode_detection_meeting_folder() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-intake-meeting-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        folder = ws / "prof_meeting_notes"
        folder.mkdir(parents=True, exist_ok=True)
        write_file(folder / "meeting_minutes.md", "# notes\n")
        write_file(folder / "agenda.docx", "docx\n")
        result = run_brain(ws, "intake", str(folder))
        assert_true(result.returncode == 0, f"meeting intake expected 0, got {result.returncode}")
        assert_true("Predicted mode: `meeting`" in result.stdout, "meeting folder should map to meeting mode")


def test_intake_surfaces_continuity_hint_from_runtime_memory() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-intake-continuity-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        folder = ws / "analysis_runtime"
        folder.mkdir(parents=True, exist_ok=True)
        write_file(folder / "dataset.csv", "x,y\n1,2\n")
        brief = ws / "contexts" / "runtime_overlays" / "existing-analysis.md"
        write_file(brief, "# existing overlay\n")
        write_file(
            ws / "contexts" / "runtime_overlay_registry.json",
            json.dumps(
                {
                    "generated_at": "2026-03-12T07:00:00+00:00",
                    "entries": [
                        {
                            "target_path": str(folder.resolve()),
                            "brief_path": str(brief.resolve()),
                            "generated_at": "2026-03-12T07:00:00+00:00",
                            "mode": "analysis",
                            "confidence": 0.91,
                            "route_strategy": "active_lane",
                            "reuse_pipeline": True,
                        }
                    ],
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
        )
        result = run_brain(ws, "intake", str(folder))
        assert_true(result.returncode == 0, f"continuity intake expected 0, got {result.returncode}, stderr={result.stderr}")
        assert_true("## Continuity Hint" in result.stdout, "intake should render a continuity hint section")
        assert_true("Source: `overlay`" in result.stdout, "intake should surface runtime memory continuity")
        assert_true("Continue from the existing `overlay` memory before starting from scratch:" in result.stdout, "continuity should influence recommended actions")


def test_refresh_adds_candidate_skill_recommendation() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-candidate-skill-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        extra_root = Path(tmp_s) / "external" / "codex_home" / "skills"
        make_skill(extra_root, "custom-unmapped-skill")
        result = run_brain(ws, "refresh")
        assert_true(result.returncode == 0, f"refresh with candidate skill expected 0, got {result.returncode}")
        registry = load_registry(ws)
        actions = registry.get("recommended_actions", [])
        assert_true(
            any("newly installed skills" in action for action in actions),
            "refresh should recommend mapping newly installed candidate skills",
        )


def test_capabilities_reports_new_commands_and_active_skills() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-capabilities-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        result = run_brain(ws, "capabilities")
        assert_true(result.returncode == 0, f"capabilities expected 0, got {result.returncode}")
        assert_true("`intake`" in result.stdout, "capabilities should list intake command")
        assert_true("`roster-install`" in result.stdout, "capabilities should list roster-install command")
        assert_true("`roster-health`" in result.stdout, "capabilities should list roster-health command")
        assert_true("`capabilities`" in result.stdout, "capabilities should list capabilities command")
        assert_true("## Active Skills" in result.stdout, "capabilities should report active skills")
        assert_true("Continuity entrypoint: `True`" in result.stdout, "capabilities should report continuity entrypoint")
        assert_true("Benchmark cases wired: `True`" in result.stdout, "capabilities should report benchmark cases")
        assert_true("Benchmark publish chain: `healthy`" in result.stdout, "capabilities should report benchmark chain health")


def test_capabilities_reports_runtime_versions_and_native_readiness() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-runtime-capabilities-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        result = run_brain(ws, "capabilities")
        assert_true(result.returncode == 0, "capabilities should succeed")
        assert_true("Runtime alignment: `aligned` preferred=`desktop_bundled`" in result.stdout, "capabilities should report aligned desktop runtime")
        assert_true("Shell CLI version: `0.115.0-alpha.4`" in result.stdout, "capabilities should report shell codex version")
        assert_true("Desktop runtime version: `0.115.0-alpha.4` app=`26.309.31024`" in result.stdout, "capabilities should report bundled desktop runtime version")
        assert_true("Native hooks/code mode/skill controls: `hooks=ready` `code_mode=ready` `skill_controls=ready`" in result.stdout, "capabilities should report native runtime readiness")


def test_refresh_surfaces_runtime_mismatch_as_action_not_failure() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-runtime-mismatch-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        result = run_brain(
            ws,
            "refresh",
            extra_env={
                "CODEX_RUNTIME_SHELL_VERSION_OVERRIDE": "0.114.0",
                "CODEX_RUNTIME_DESKTOP_VERSION_OVERRIDE": "0.115.0-alpha.4",
                "CODEX_RUNTIME_DESKTOP_APP_VERSION_OVERRIDE": "26.309.31024",
            },
        )
        assert_true(result.returncode == 0, f"refresh with runtime mismatch should stay healthy, got {result.returncode}")
        registry = load_registry(ws)
        runtime_check = registry.get("checks", {}).get("runtime_environment", {})
        assert_true(runtime_check.get("alignment_status") == "mismatch", "runtime_environment check should record mismatched versions")
        actions = registry.get("recommended_actions", [])
        assert_true(any("Align shell `codex` with the Codex Desktop bundled runtime" in action for action in actions), "refresh should recommend aligning mismatched runtimes")


def test_capabilities_do_not_require_desktop_origin_override_when_desktop_runtime_exists() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-runtime-origin-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        fake_app = ws / "fake" / "Codex.app"
        fake_info = fake_app / "Contents" / "Info.plist"
        write_file(fake_info, "<?xml version=\"1.0\" encoding=\"UTF-8\"?><plist version=\"1.0\"><dict><key>CFBundleShortVersionString</key><string>26.309.31024</string></dict></plist>")
        result = run_brain(
            ws,
            "capabilities",
            extra_env={
                "CODEX_INTERNAL_ORIGINATOR_OVERRIDE": "",
                "CODEX_RUNTIME_DESKTOP_APP_PATH_OVERRIDE": str(fake_app),
                "CODEX_RUNTIME_DESKTOP_INFO_OVERRIDE": str(fake_info),
            },
        )
        assert_true(result.returncode == 0, "capabilities should succeed without desktop origin override")
        assert_true("GUI surface: `available`" in result.stdout, "desktop runtime presence should make GUI surface visible")


def test_bootstrap_creates_overlay_and_local_agent_for_project_like_folder() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-bootstrap-project-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        folder = ws / "analysis_project"
        folder.mkdir(parents=True, exist_ok=True)
        (folder / ".git").mkdir()
        (folder / "scripts").mkdir()
        write_file(folder / "dataset.csv", "x,y\n1,2\n")
        write_file(folder / "results.xlsx", "placeholder\n")
        result = run_brain(ws, "bootstrap", str(folder))
        assert_true(result.returncode == 0, f"bootstrap project folder expected 0, got {result.returncode}, stderr={result.stderr}")
        assert_true("# Folder Bootstrap" in result.stdout, "bootstrap should print a bootstrap summary")
        assert_true("Local agent status: `created`" in result.stdout, "project-like bootstrap should create a local AGENTS.md")
        local_agent = folder / "AGENTS.md"
        assert_true(local_agent.exists(), "project-like bootstrap should write local AGENTS.md")
        text = local_agent.read_text(encoding="utf-8")
        assert_true("## Memory-Driven Iteration" in text, "generated local agent should include memory iteration guidance")
        registry = load_runtime_overlay_registry(ws)
        assert_true(any(entry["target_path"] == str(folder.resolve()) for entry in registry.get("entries", [])), "bootstrap should write runtime overlay registry entry")


def test_bootstrap_skips_local_agent_for_scratch_folder() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-bootstrap-scratch-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        folder = ws / "tmp"
        folder.mkdir(parents=True, exist_ok=True)
        write_file(folder / "notes.md", "# scratch\n")
        result = run_brain(ws, "bootstrap", str(folder))
        assert_true(result.returncode == 0, f"bootstrap scratch expected 0, got {result.returncode}, stderr={result.stderr}")
        assert_true(not (folder / "AGENTS.md").exists(), "scratch bootstrap should not create local AGENTS.md")
        assert_true("Local agent status: `not_needed`" in result.stdout, "scratch bootstrap should report that local agent is not needed")


def test_bootstrap_preserves_existing_local_agent() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-bootstrap-existing-agent-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        folder = ws / "writing_case"
        folder.mkdir(parents=True, exist_ok=True)
        write_file(folder / "AGENTS.md", "# existing local agent\n")
        write_file(folder / "draft.md", "# draft\n")
        result = run_brain(ws, "bootstrap", str(folder))
        assert_true(result.returncode == 0, f"bootstrap existing agent expected 0, got {result.returncode}, stderr={result.stderr}")
        assert_true("Local agent status: `existing`" in result.stdout, "bootstrap should report existing local AGENTS.md")
        assert_true((folder / "AGENTS.md").read_text(encoding="utf-8") == "# existing local agent\n", "bootstrap should not overwrite an existing local AGENTS.md")


def test_bootstrap_warns_on_legacy_agent_filename() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-bootstrap-legacy-agent-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        folder = ws / "legacy_case"
        folder.mkdir(parents=True, exist_ok=True)
        write_file(folder / "Agent.md", "# legacy agent\n")
        write_file(folder / "paper.tex", "\\section{Draft}\n")
        result = run_brain(ws, "bootstrap", str(folder))
        assert_true(result.returncode == 0, f"bootstrap legacy agent expected 0, got {result.returncode}, stderr={result.stderr}")
        assert_true("Local agent status: `legacy_present`" in result.stdout, "bootstrap should surface legacy Agent.md status")
        assert_true("legacy_agent_filename" in result.stdout, "bootstrap should warn about Agent.md casing mismatch")
        assert_true(not (folder / "AGENTS.md").exists(), "bootstrap should not create AGENTS.md when Agent.md already exists")


def test_overlay_writes_brief_and_registry() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-overlay-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        folder = ws / "analysis_runtime"
        folder.mkdir(parents=True, exist_ok=True)
        write_file(folder / "dataset.csv", "x,y\n1,2\n")
        write_file(folder / "results.xlsx", "placeholder\n")
        write_file(folder / "output_summary.md", "# summary\n")
        result = run_brain(ws, "overlay", str(folder))
        assert_true(result.returncode == 0, f"overlay expected 0, got {result.returncode}, stderr={result.stderr}")
        registry_path = ws / "contexts" / "runtime_overlay_registry.json"
        brief_dir = ws / "contexts" / "runtime_overlays"
        assert_true(registry_path.exists(), "overlay should write runtime_overlay_registry.json")
        assert_true(brief_dir.exists(), "overlay should create runtime_overlays directory")
        briefs = sorted(brief_dir.glob("*.md"))
        assert_true(len(briefs) == 1, "overlay should create exactly one brief for the target")
        assert_true("Predicted mode: `analysis`" in result.stdout, "overlay brief should include the predicted mode")
        assert_true("## Session Preamble" in result.stdout, "overlay brief should include session preamble")
        assert_true("## Escalation Triggers" in result.stdout, "overlay brief should include escalation triggers")
        assert_true(not (ws / "contexts" / "system_registry.json").exists(), "overlay should not write system_registry.json")
        assert_true(not (ws / "contexts" / "system_status.md").exists(), "overlay should not write system_status.md")
        registry = load_runtime_overlay_registry(ws)
        entries = registry.get("entries", [])
        assert_true(len(entries) == 1, "overlay registry should contain one entry")
        assert_true(entries[0]["target_path"] == str(folder.resolve()), "overlay registry should track the target path")
        assert_true(entries[0]["route_strategy"] == "active_lane", "high-confidence analysis overlay should use active lane")


def test_overlay_carries_forward_runtime_memory_context() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-overlay-continuity-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        folder = ws / "analysis_runtime"
        folder.mkdir(parents=True, exist_ok=True)
        write_file(folder / "dataset.csv", "x,y\n1,2\n")
        brief = ws / "contexts" / "runtime_overlays" / "existing-analysis.md"
        write_file(brief, "# existing overlay\n")
        write_file(
            ws / "contexts" / "runtime_overlay_registry.json",
            json.dumps(
                {
                    "generated_at": "2026-03-12T07:00:00+00:00",
                    "entries": [
                        {
                            "target_path": str(folder.resolve()),
                            "brief_path": str(brief.resolve()),
                            "generated_at": "2026-03-12T07:00:00+00:00",
                            "mode": "analysis",
                            "confidence": 0.91,
                            "route_strategy": "active_lane",
                            "reuse_pipeline": True,
                        }
                    ],
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
        )
        result = run_brain(ws, "overlay", str(folder))
        assert_true(result.returncode == 0, f"overlay continuity expected 0, got {result.returncode}, stderr={result.stderr}")
        assert_true("## Continuity Context" in result.stdout, "overlay brief should expose continuity context")
        assert_true("Source: `overlay`" in result.stdout, "overlay should carry forward runtime memory source")


def test_closeout_requires_overlay_first() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-closeout-needs-overlay-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        folder = ws / "analysis_runtime"
        folder.mkdir(parents=True, exist_ok=True)
        write_file(folder / "dataset.csv", "x,y\n1,2\n")
        result = run_brain(ws, "closeout", str(folder), "--summary", "closeout without overlay")
        assert_true(result.returncode == 1, f"closeout without overlay should fail, got {result.returncode}")
        assert_true("run `./scripts/brain.sh overlay <folder>` first" in result.stderr, "closeout should require overlay first")


def test_closeout_creates_open_proposal_for_candidate_skill() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-closeout-candidate-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        extra_root = Path(tmp_s) / "external" / "codex_home" / "skills"
        make_skill(extra_root, "custom-unmapped-skill")
        folder = ws / "analysis_runtime"
        folder.mkdir(parents=True, exist_ok=True)
        write_file(folder / "dataset.csv", "x,y\n1,2\n")
        write_file(folder / "results.xlsx", "placeholder\n")
        write_file(folder / "output_summary.md", "# summary\n")
        overlay = run_brain(ws, "overlay", str(folder))
        assert_true(overlay.returncode == 0, f"overlay should succeed before closeout, got {overlay.returncode}")
        result = run_brain(
            ws,
            "closeout",
            str(folder),
            "--summary",
            "Validated candidate skill on recurring analysis workflow.",
            "--used-skills",
            "custom-unmapped-skill",
            "--outcome",
            "success",
            "--reuse",
            "yes",
        )
        assert_true(result.returncode == 0, f"closeout with candidate skill expected 0, got {result.returncode}, stderr={result.stderr}")
        payload = load_skill_iteration_registry(ws)
        assert_true(len(payload.get("closeouts", [])) == 1, "closeout should register exactly one closeout entry")
        proposals = payload.get("proposals", [])
        assert_true(len(proposals) == 1, "candidate skill closeout should create one proposal")
        proposal = proposals[0]
        assert_true(proposal["status"] == "open", "new candidate proposal should be open")
        assert_true(proposal["skill_name"] == "custom-unmapped-skill", "proposal should target the used candidate skill")
        assert_true(proposal["mode"] == "analysis", "proposal should inherit the overlay mode")
        proposal_path = Path(proposal["proposal_path"])
        assert_true(proposal_path.exists(), "proposal markdown file should be written")
        assert_true("## Suggested Promotion" in proposal_path.read_text(encoding="utf-8"), "proposal file should include promotion guidance")


def test_closeout_candidate_skill_needs_success_and_reuse() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-closeout-candidate-gating-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        extra_root = Path(tmp_s) / "external" / "codex_home" / "skills"
        make_skill(extra_root, "custom-unmapped-skill")
        folder = ws / "analysis_runtime"
        folder.mkdir(parents=True, exist_ok=True)
        write_file(folder / "dataset.csv", "x,y\n1,2\n")
        write_file(folder / "results.xlsx", "placeholder\n")
        write_file(folder / "output_summary.md", "# summary\n")
        assert_true(run_brain(ws, "overlay", str(folder)).returncode == 0, "overlay should succeed before gated closeout")
        result = run_brain(
            ws,
            "closeout",
            str(folder),
            "--summary",
            "Candidate skill helped partially but is not reusable yet.",
            "--used-skills",
            "custom-unmapped-skill",
            "--outcome",
            "partial",
            "--reuse",
            "no",
        )
        assert_true(result.returncode == 0, f"gated closeout expected 0, got {result.returncode}, stderr={result.stderr}")
        payload = load_skill_iteration_registry(ws)
        assert_true(len(payload.get("closeouts", [])) == 1, "closeout should still be recorded")
        assert_true(len(payload.get("proposals", [])) == 0, "partial/non-reusable closeout should not open a proposal")


def test_skill_discover_writes_local_and_remote_registry() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-skill-discover-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        fake_bin = Path(tmp_s) / "fake-bin"
        fake_bin.mkdir(parents=True, exist_ok=True)
        write_file(
            fake_bin / "npx",
            "#!/usr/bin/env bash\n"
            "if [[ \"$1\" == \"--yes\" && \"$2\" == \"skills\" && \"$3\" == \"find\" ]]; then\n"
            "  echo 'demo-owner/demo-pack@self-improving-agent 123 installs'\n"
            "  echo '└ https://skills.sh/demo-owner/demo-pack/self-improving-agent'\n"
            "  exit 0\n"
            "fi\n"
            "exit 1\n",
            executable=True,
        )
        result = run_brain(
            ws,
            "skill-discover",
            "obsidian markdown",
            extra_env={"PATH": f"{fake_bin}:{os.environ['PATH']}"},
        )
        assert_true(result.returncode == 0, f"skill-discover expected 0, got {result.returncode}, stderr={result.stderr}")
        assert_true("`obsidian-markdown`" in result.stdout, "skill-discover should surface local matches")
        assert_true("`demo-owner/demo-pack@self-improving-agent`" in result.stdout, "skill-discover should surface remote matches")
        registry = load_skill_discovery_registry(ws)
        assert_true(registry["last_query"] == "obsidian markdown", "skill-discover should persist the query")
        assert_true(len(registry["local_matches"]) >= 1, "skill-discover should persist local matches")
        assert_true(len(registry["remote_matches"]) == 1, "skill-discover should persist remote matches")


def test_skill_discover_degrades_without_npx() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-skill-discover-no-npx-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        result = run_brain(
            ws,
            "skill-discover",
            "obsidian markdown",
            extra_env={"PATH": "/bin:/usr/bin"},
        )
        assert_true(result.returncode == 2, f"skill-discover without npx should degrade, got {result.returncode}")
        assert_true("Remote discovery unavailable" in result.stdout, "skill-discover should explain missing npx")
        registry = load_skill_discovery_registry(ws)
        assert_true(registry["status"] == "degraded", "skill-discover should persist degraded status when remote discovery is unavailable")


def test_skill_route_writes_workflow_registry() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-skill-route-basic-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        folder = ws / "analysis_runtime"
        folder.mkdir(parents=True, exist_ok=True)
        write_file(folder / "dataset.csv", "x,y\n1,2\n")
        write_file(folder / "results.xlsx", "placeholder\n")
        write_file(folder / "output_summary.md", "# summary\n")
        result = run_brain(ws, "skill-route", "analyze spreadsheet dataset and run regression checks", "--path", str(folder))
        assert_true(result.returncode == 0, f"skill-route expected 0, got {result.returncode}, stderr={result.stderr}")
        assert_true("# Skill Route" in result.stdout, "skill-route should render a route summary")
        assert_true("Need skill: `true`" in result.stdout, "analysis workflow should need skills")
        registry = load_skill_route_registry(ws)
        assert_true(len(registry.get("entries", [])) == 1, "skill-route should persist one route entry")
        entry = registry["entries"][0]
        assert_true(entry["predicted_mode"] == "analysis", "skill-route should inherit the folder mode")
        assert_true(entry["primary_skills"], "skill-route should select at least one primary skill")


def test_artifact_harness_writes_packet_chain() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-artifact-harness-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        folder = ws / "artifact_case"
        folder.mkdir(parents=True, exist_ok=True)
        result = run_brain(
            ws,
            "artifact-harness",
            "Draft a review-ready methods appendix",
            "--path",
            str(folder),
            "--artifact",
            "output/methods_appendix.md",
        )
        assert_true(result.returncode == 0, f"artifact-harness expected 0, got {result.returncode}, stderr={result.stderr}")
        assert_true("# Artifact Harness Packet Chain" in result.stdout, "artifact-harness should render a packet summary")
        assert_true("artifact_harness_spec" in result.stdout, "summary should include the SPEC packet")
        registry_path = folder / "contexts" / "artifact_harness_registry.json"
        assert_true(registry_path.exists(), "artifact-harness should write a registry")
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        assert_true(len(registry.get("entries", [])) == 1, "artifact-harness should persist one registry entry")
        entry = registry["entries"][0]
        run_dir = folder / entry["run_dir"]
        assert_true(run_dir.exists(), "artifact-harness should write a deterministic run directory")
        status_path = folder / entry["status_path"]
        assert_true(status_path.exists(), "artifact-harness should write lifecycle metadata")
        status_payload = json.loads(status_path.read_text(encoding="utf-8"))
        assert_true(status_payload["status"] == "draft", "new artifact-harness runs should start as draft")
        assert_true(entry["status"] == "draft", "registry should expose initial lifecycle status")
        for key in (
            "artifact_harness_spec",
            "hr_staffing_packet",
            "team_operating_packet",
            "capability_access_packet",
            "runtime_mapping",
            "manifest",
        ):
            assert_true((folder / entry["packets"][key]).exists(), f"artifact-harness should write {key}")
        spec_text = (folder / entry["packets"]["artifact_harness_spec"]).read_text(encoding="utf-8")
        assert_true("[source: user phrase]" in spec_text, "SPEC should include field-level source hints")
        assert_true("method [source: user phrase or verification owner]" in spec_text, "SPEC acceptance checks should keep method source hints")
        assert_true("owner [source: verification/review]" in spec_text, "SPEC acceptance checks should keep owner source hints")
        assert_true("pass condition [source: user phrase or open question]" in spec_text, "SPEC acceptance checks should keep pass-condition source hints")
        assert_true("staffing target [source: workflow default]" in spec_text, "SPEC handoff should keep staffing source hints")
        assert_true("Team Architect target [source: workflow default]" in spec_text, "SPEC handoff should keep Team Architect source hints")
        assert_true("verification or review target [source: workflow default]" in spec_text, "SPEC handoff should keep verification source hints")
        template_text = (ROOT / "templates" / "artifact_harness" / "artifact_harness_spec.template.md").read_text(encoding="utf-8")
        assert_true("method [source: user phrase, verification owner, repo evidence, or open question]" in template_text, "canonical SPEC template should keep acceptance method source hints")
        assert_true("staffing target [source: workflow policy]" in template_text, "canonical SPEC template should keep handoff source hints")
        assert_true("verification or review target [source: workflow policy, user phrase, or open question]" in template_text, "canonical SPEC template should keep verification handoff source hints")
        top_text = (folder / entry["packets"]["team_operating_packet"]).read_text(encoding="utf-8")
        assert_true(entry["packets"]["hr_staffing_packet"] in top_text, "generated TOP should link source_hr_staffing_packet")
        manifest = json.loads((folder / entry["packets"]["manifest"]).read_text(encoding="utf-8"))
        assert_true(
            manifest["workflow"]
            == [
                "user mission",
                "Artifact Harness SPEC",
                "HR staffing",
                "Team Operating Packet",
                "Capability Access Packet",
                "runtime mapping",
                "verification/review",
            ],
            "manifest should preserve the packet chain",
        )
        assert_true("hr_staffing_packet" in manifest["packets"], "manifest should include hr_staffing_packet")
        assert_true(manifest["lifecycle"]["status"] == "draft", "manifest should link initial lifecycle status")
        assert_true(manifest["lifecycle"]["status_path"] == entry["status_path"], "manifest and registry should agree on lifecycle status path")


def test_artifact_harness_refuses_rerun_without_force() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-artifact-rerun-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        folder = ws / "artifact_case"
        folder.mkdir(parents=True, exist_ok=True)
        first = run_brain(ws, "artifact-harness", "Draft a review-ready methods appendix", "--path", str(folder), "--id", "stable-run")
        assert_true(first.returncode == 0, f"first artifact-harness run should succeed, got {first.returncode}, stderr={first.stderr}")
        registry_path = folder / "contexts" / "artifact_harness_registry.json"
        registry_before = registry_path.read_text(encoding="utf-8")
        entry = load_artifact_harness_registry(folder)["entries"][0]
        spec_path = folder / entry["packets"]["artifact_harness_spec"]
        spec_path.write_text(spec_path.read_text(encoding="utf-8") + "\nSENTINEL_DO_NOT_OVERWRITE\n", encoding="utf-8")

        second = run_brain(ws, "artifact-harness", "Draft a review-ready methods appendix", "--path", str(folder), "--id", "stable-run")
        assert_true(second.returncode != 0, "artifact-harness rerun without force should fail")
        assert_true("Artifact Harness packet run already exists" in second.stderr, "rerun failure should explain the existing run directory")
        assert_true("--id <new-id>" in second.stderr and "--force" in second.stderr, "rerun failure should suggest new id or explicit force")
        assert_true("SENTINEL_DO_NOT_OVERWRITE" in spec_path.read_text(encoding="utf-8"), "rerun without force should preserve filled packet content")
        assert_true(registry_path.read_text(encoding="utf-8") == registry_before, "rerun without force should not update registry")

        forced = run_brain(ws, "artifact-harness", "Draft a review-ready methods appendix", "--path", str(folder), "--id", "stable-run", "--force")
        assert_true(forced.returncode == 0, f"artifact-harness --force should overwrite, got {forced.returncode}, stderr={forced.stderr}")
        assert_true("SENTINEL_DO_NOT_OVERWRITE" not in spec_path.read_text(encoding="utf-8"), "force should allow packet overwrite")


def test_artifact_harness_json_from_temp_cwd_writes_target_workspace() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-artifact-json-") as tmp_s:
        tmp = Path(tmp_s)
        cwd = tmp / "cwd"
        target = tmp / "target_workspace"
        cwd.mkdir(parents=True, exist_ok=True)
        target.mkdir(parents=True, exist_ok=True)
        brain = ROOT / "scripts" / "brain.sh"
        result = subprocess.run(
            [
                str(brain),
                "artifact-harness",
                "Draft a review-ready methods appendix",
                "--path",
                str(target),
                "--id",
                "json-entrypoint",
                "--json",
            ],
            cwd=cwd,
            text=True,
            capture_output=True,
            check=False,
        )
        assert_true(result.returncode == 0, f"absolute artifact-harness --json expected 0, got {result.returncode}, stderr={result.stderr}")
        payload = json.loads(result.stdout)
        assert_true(payload["created"] is True and payload["refused"] is False, "artifact-harness JSON should expose creation state")
        assert_true(Path(payload["run_dir"]).resolve() == (target / "contexts" / "artifact_harness_runs" / "json-entrypoint").resolve(), "--path should define packet output workspace")
        assert_true(Path(payload["registry_path"]).resolve() == (target / "contexts" / "artifact_harness_registry.json").resolve(), "registry should live in the target workspace contexts")
        assert_true(Path(payload["packets"]["artifact_harness_spec"]).exists(), "JSON packet path should be directly usable")
        assert_true(Path(payload["packets"]["hr_staffing_packet"]).exists(), "JSON packet output should include hr_staffing_packet")
        assert_true(payload["status"] == "draft", "artifact-harness JSON should expose initial lifecycle status")
        assert_true(Path(payload["status_path"]).exists(), "artifact-harness JSON should expose lifecycle metadata path")


def test_artifact_harness_lifecycle_status_mark_resume() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-artifact-lifecycle-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        folder = ws / "artifact_case"
        folder.mkdir(parents=True, exist_ok=True)
        create = run_brain(ws, "artifact-harness", "Draft a review-ready methods appendix", "--path", str(folder), "--id", "lifecycle-run", "--json")
        assert_true(create.returncode == 0, f"artifact-harness create should succeed, got {create.returncode}, stderr={create.stderr}")
        create_payload = json.loads(create.stdout)
        spec_path = Path(create_payload["packets"]["artifact_harness_spec"])
        original_spec = spec_path.read_text(encoding="utf-8")
        sentinel = "\nSENTINEL_LIFECYCLE_SHOULD_NOT_TOUCH_MARKDOWN\n"
        spec_path.write_text(original_spec + sentinel, encoding="utf-8")

        human_status = run_brain(ws, "artifact-harness", "status", "--path", str(folder), "--id", "lifecycle-run")
        assert_true(human_status.returncode == 0, f"artifact-harness status should succeed, got {human_status.returncode}, stderr={human_status.stderr}")
        assert_true("Status: `draft`" in human_status.stdout, "human status should report draft")

        status_json = run_brain(ws, "artifact-harness", "status", "--path", str(folder), "--id", "lifecycle-run", "--json")
        assert_true(status_json.returncode == 0, f"artifact-harness status --json should succeed, got {status_json.returncode}, stderr={status_json.stderr}")
        status_payload = json.loads(status_json.stdout)
        assert_true(status_payload["status"] == "draft", "status JSON should report draft")
        assert_true(status_payload["refused"] is False, "status JSON should expose refused=false on success")

        mark_json = run_brain(
            ws,
            "artifact-harness",
            "mark",
            "--path",
            str(folder),
            "--id",
            "lifecycle-run",
            "--status",
            "filled",
            "--note",
            "SPEC and staffing packet filled",
            "--json",
        )
        assert_true(mark_json.returncode == 0, f"artifact-harness mark --json should succeed, got {mark_json.returncode}, stderr={mark_json.stderr}")
        mark_payload = json.loads(mark_json.stdout)
        assert_true(mark_payload["status"] == "filled", "mark JSON should report the new status")
        assert_true(mark_payload["status_note"] == "SPEC and staffing packet filled", "mark JSON should retain the note")
        assert_true("SENTINEL_LIFECYCLE_SHOULD_NOT_TOUCH_MARKDOWN" in spec_path.read_text(encoding="utf-8"), "mark should not rewrite packet Markdown")

        resume_json = run_brain(ws, "artifact-harness", "resume", "--path", str(folder), "--id", "lifecycle-run", "--json")
        assert_true(resume_json.returncode == 0, f"artifact-harness resume --json should succeed, got {resume_json.returncode}, stderr={resume_json.stderr}")
        resume_payload = json.loads(resume_json.stdout)
        assert_true(resume_payload["status"] == "filled", "resume JSON should report current status")
        assert_true(resume_payload["next_inspection"] == "team_operating_packet", "resume should recommend a packet to inspect next")
        assert_true("resume_json" in resume_payload["commands"], "resume JSON should provide safe command forms")
        assert_true("SENTINEL_LIFECYCLE_SHOULD_NOT_TOUCH_MARKDOWN" in spec_path.read_text(encoding="utf-8"), "resume should not rewrite packet Markdown")

        registry = load_artifact_harness_registry(folder)
        entry = registry["entries"][0]
        assert_true(entry["status"] == "filled", "registry should track marked lifecycle status")
        status_sidecar = json.loads((folder / entry["status_path"]).read_text(encoding="utf-8"))
        assert_true(status_sidecar["status"] == "filled", "status sidecar should track marked lifecycle status")
        assert_true(entry["status_updated_at"] == status_sidecar["updated_at"], "registry and status sidecar should agree on status update time")


def test_artifact_harness_lifecycle_json_refusal_is_parseable() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-artifact-lifecycle-refusal-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        folder = ws / "artifact_case"
        folder.mkdir(parents=True, exist_ok=True)
        missing = run_brain(ws, "artifact-harness", "resume", "--path", str(folder), "--id", "missing-run", "--json")
        assert_true(missing.returncode != 0, "artifact-harness resume --json should fail for a missing run")
        payload = json.loads(missing.stdout)
        assert_true(payload["refused"] is True, "lifecycle refusal JSON should expose refused=true")
        assert_true(payload["reason"] == "missing_packet_run", "lifecycle refusal JSON should identify missing run")

        create = run_brain(ws, "artifact-harness", "Draft a review-ready methods appendix", "--path", str(folder), "--id", "bad-status")
        assert_true(create.returncode == 0, f"artifact-harness create should succeed before invalid-status check, got {create.returncode}")
        invalid = run_brain(ws, "artifact-harness", "mark", "--path", str(folder), "--id", "bad-status", "--status", "secret-approved", "--json")
        assert_true(invalid.returncode != 0, "artifact-harness mark --json should fail for an invalid status")
        invalid_payload = json.loads(invalid.stdout)
        assert_true(invalid_payload["refused"] is True, "invalid mark status should emit refusal JSON")
        assert_true(invalid_payload["reason"] == "invalid_status", "invalid mark status should identify invalid_status")


def test_artifact_harness_replay_writes_evidence_and_preserves_markdown() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-artifact-replay-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        folder = ws / "artifact_case"
        folder.mkdir(parents=True, exist_ok=True)
        create = run_brain(ws, "artifact-harness", "Draft a replay-ready methods appendix", "--path", str(folder), "--id", "replay-run", "--json")
        assert_true(create.returncode == 0, f"artifact-harness create should succeed, got {create.returncode}, stderr={create.stderr}")
        create_payload = json.loads(create.stdout)
        spec_path = Path(create_payload["packets"]["artifact_harness_spec"])
        spec_path.write_text(spec_path.read_text(encoding="utf-8") + "\nSENTINEL_REPLAY_SHOULD_NOT_TOUCH_MARKDOWN\n", encoding="utf-8")

        replay = run_brain(ws, "artifact-harness", "replay", "--path", str(folder), "--id", "replay-run", "--json")
        assert_true(replay.returncode == 0, f"artifact-harness replay --json should succeed, got {replay.returncode}, stderr={replay.stderr}")
        payload = json.loads(replay.stdout)
        assert_true(payload["refused"] is False, "replay JSON should expose refused=false")
        assert_true(payload["status"] == "draft", "replay JSON should include lifecycle status")
        assert_true(payload["id"] == "replay-run", "replay JSON should include packet id")
        evidence_path = Path(payload["evidence_path"])
        assert_true(evidence_path.exists(), "replay should write evidence inside the packet run directory")
        assert_true(evidence_path.parent == Path(payload["run_dir"]), "replay evidence should live in the packet run directory")
        evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
        assert_true(evidence["id"] == "replay-run", "evidence JSON should record packet id")
        assert_true(evidence["mission"] == "Draft a replay-ready methods appendix", "evidence JSON should record the tested mission")
        assert_true(evidence["registry_status"] == "draft", "evidence JSON should record registry lifecycle status")
        assert_true(evidence["packets"]["artifact_harness_spec"]["exists"] is True, "evidence should record packet presence")
        assert_true(evidence["field_completion_summary"]["existing_packet_count"] >= 6, "evidence should count existing packet artifacts")
        assert_true("empty_bullet_fields" in evidence["heuristics"], "evidence should record transparent field heuristics")
        assert_true("SENTINEL_REPLAY_SHOULD_NOT_TOUCH_MARKDOWN" in spec_path.read_text(encoding="utf-8"), "replay should not rewrite packet Markdown")

        human = run_brain(ws, "artifact-harness", "replay", "--path", str(folder), "--id", "replay-run")
        assert_true(human.returncode == 0, f"artifact-harness replay human mode should succeed, got {human.returncode}, stderr={human.stderr}")
        assert_true("# Artifact Harness Replay Evidence" in human.stdout, "human replay should render a summary")


def test_artifact_harness_replay_json_refusal_is_parseable() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-artifact-replay-refusal-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        folder = ws / "artifact_case"
        folder.mkdir(parents=True, exist_ok=True)
        replay = run_brain(ws, "artifact-harness", "replay", "--path", str(folder), "--id", "missing-replay", "--json")
        assert_true(replay.returncode != 0, "artifact-harness replay --json should fail for a missing run")
        payload = json.loads(replay.stdout)
        assert_true(payload["refused"] is True, "replay refusal JSON should expose refused=true")
        assert_true(payload["reason"] == "missing_packet_run", "replay refusal should identify missing run")
        assert_true(payload["evidence_path"].endswith("/artifact_replay_evidence.json"), "replay refusal should include attempted evidence path")
        assert_true(not Path(payload["evidence_path"]).exists(), "missing-run replay should not write evidence")


def test_artifact_harness_provenance_writes_ledger_and_preserves_markdown() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-artifact-provenance-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        folder = ws / "artifact_case"
        folder.mkdir(parents=True, exist_ok=True)
        create = run_brain(ws, "artifact-harness", "Draft a provenance-ready methods appendix", "--path", str(folder), "--id", "provenance-run", "--json")
        assert_true(create.returncode == 0, f"artifact-harness create should succeed, got {create.returncode}, stderr={create.stderr}")
        create_payload = json.loads(create.stdout)
        spec_path = Path(create_payload["packets"]["artifact_harness_spec"])
        spec_path.write_text(spec_path.read_text(encoding="utf-8") + "\nSENTINEL_PROVENANCE_SHOULD_NOT_TOUCH_MARKDOWN\n", encoding="utf-8")

        replay = run_brain(ws, "artifact-harness", "replay", "--path", str(folder), "--id", "provenance-run", "--json")
        assert_true(replay.returncode == 0, f"artifact-harness replay should succeed before provenance, got {replay.returncode}, stderr={replay.stderr}")
        provenance = run_brain(ws, "artifact-harness", "provenance", "--path", str(folder), "--id", "provenance-run", "--json")
        assert_true(provenance.returncode == 0, f"artifact-harness provenance --json should succeed, got {provenance.returncode}, stderr={provenance.stderr}")
        payload = json.loads(provenance.stdout)
        assert_true(payload["refused"] is False, "provenance JSON should expose refused=false")
        assert_true(payload["id"] == "provenance-run", "provenance JSON should include packet id")
        assert_true(payload["status"] == "draft", "provenance JSON should include lifecycle status")
        ledger_path = Path(payload["provenance_ledger_path"])
        assert_true(ledger_path.exists(), "provenance should write a ledger inside the packet run directory")
        assert_true(ledger_path.parent == Path(payload["run_dir"]), "provenance ledger should live in the packet run directory")
        ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
        assert_true(ledger["ledger_type"] == "artifact_harness_provenance_ledger", "ledger should identify its type")
        assert_true("user_mission" in ledger["source_categories"], "ledger should list user_mission source category")
        assert_true("packet_reference" in ledger["source_categories"], "ledger should list packet_reference source category")
        assert_true("approval_required" in ledger["source_categories"], "ledger should list approval_required source category")
        assert_true(ledger["field_provenance"]["mission"]["source_category"] == "user_mission", "mission should be sourced from user_mission")
        assert_true(ledger["packet_chain_provenance"]["runtime_mapping"]["source_capability_access_packet"]["source_category"] == "packet_reference", "runtime mapping should trace to CAP")
        assert_true(ledger["packet_chain_provenance"]["capability_access_packet"]["approval_gates"]["source_category"] == "approval_required", "CAP approval gates should require approval")
        assert_true(ledger["packet_chain_provenance"]["replay_evidence"]["evidence_source"]["source_category"] == "repo_evidence", "existing replay evidence should be recorded as repo evidence")
        assert_true("SENTINEL_PROVENANCE_SHOULD_NOT_TOUCH_MARKDOWN" in spec_path.read_text(encoding="utf-8"), "provenance should not rewrite packet Markdown")

        human = run_brain(ws, "artifact-harness", "provenance", "--path", str(folder), "--id", "provenance-run")
        assert_true(human.returncode == 0, f"artifact-harness provenance human mode should succeed, got {human.returncode}, stderr={human.stderr}")
        assert_true("# Artifact Harness Provenance Ledger" in human.stdout, "human provenance should render a summary")


def test_artifact_harness_provenance_json_refusal_is_parseable() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-artifact-provenance-refusal-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        folder = ws / "artifact_case"
        folder.mkdir(parents=True, exist_ok=True)
        provenance = run_brain(ws, "artifact-harness", "provenance", "--path", str(folder), "--id", "missing-provenance", "--json")
        assert_true(provenance.returncode != 0, "artifact-harness provenance --json should fail for a missing run")
        payload = json.loads(provenance.stdout)
        assert_true(payload["refused"] is True, "provenance refusal JSON should expose refused=true")
        assert_true(payload["reason"] == "missing_packet_run", "provenance refusal should identify missing run")
        assert_true(payload["provenance_ledger_path"].endswith("/packet_provenance_ledger.json"), "provenance refusal should include attempted ledger path")
        assert_true(not Path(payload["provenance_ledger_path"]).exists(), "missing-run provenance should not write a ledger")


def test_artifact_harness_provenance_refuses_manifest_packet_outside_target() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-artifact-provenance-boundary-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        folder = ws / "artifact_case"
        folder.mkdir(parents=True, exist_ok=True)
        create = run_brain(ws, "artifact-harness", "Draft a boundary-safe provenance packet", "--path", str(folder), "--id", "provenance-boundary-run", "--json")
        assert_true(create.returncode == 0, f"artifact-harness create should succeed, got {create.returncode}, stderr={create.stderr}")
        create_payload = json.loads(create.stdout)

        provenance_ok = run_brain(ws, "artifact-harness", "provenance", "--path", str(folder), "--id", "provenance-boundary-run", "--json")
        assert_true(provenance_ok.returncode == 0, f"initial provenance should succeed, got {provenance_ok.returncode}, stderr={provenance_ok.stderr}")
        ledger_path = Path(json.loads(provenance_ok.stdout)["provenance_ledger_path"])
        ledger_before = ledger_path.read_text(encoding="utf-8")

        outside_secret = ws / "outside_secret.md"
        write_file(outside_secret, "SECRET_PROVENANCE_OPEN_QUESTION\n- stolen_field:\n")
        manifest_path = Path(create_payload["manifest"])
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["packets"]["artifact_harness_spec"] = "../outside_secret.md"
        write_file(manifest_path, json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")

        provenance = run_brain(ws, "artifact-harness", "provenance", "--path", str(folder), "--id", "provenance-boundary-run", "--json")
        assert_true(provenance.returncode != 0, "provenance should refuse a manifest packet path outside the target workspace")
        payload = json.loads(provenance.stdout)
        assert_true(payload["refused"] is True, "outside manifest path refusal should expose refused=true")
        assert_true(payload["reason"] == "manifest_packet_path_outside_target_workspace", "outside manifest path refusal should use the expected reason")
        assert_true(payload["offending_packet_key"] == "artifact_harness_spec", "refusal should identify the offending packet key")
        assert_true(Path(payload["attempted_path"]).resolve() == outside_secret.resolve(), "refusal should identify the attempted outside path")
        assert_true("SECRET_PROVENANCE_OPEN_QUESTION" not in provenance.stdout, "provenance refusal should not leak outside file content")
        assert_true("field_provenance" not in provenance.stdout, "provenance refusal should not emit field provenance from outside content")
        assert_true(ledger_path.read_text(encoding="utf-8") == ledger_before, "provenance refusal should not rewrite existing ledger")


def test_artifact_harness_runtime_check_default_is_conservative() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-artifact-runtime-check-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        folder = ws / "artifact_case"
        folder.mkdir(parents=True, exist_ok=True)
        create = run_brain(ws, "artifact-harness", "Draft a runtime readiness packet", "--path", str(folder), "--id", "runtime-run", "--json")
        assert_true(create.returncode == 0, f"artifact-harness create should succeed, got {create.returncode}, stderr={create.stderr}")
        create_payload = json.loads(create.stdout)
        runtime_path = Path(create_payload["packets"]["runtime_mapping"])
        runtime_path.write_text(runtime_path.read_text(encoding="utf-8") + "\nSENTINEL_RUNTIME_CHECK_SHOULD_NOT_TOUCH_MARKDOWN\n", encoding="utf-8")

        runtime_check = run_brain(ws, "artifact-harness", "runtime-check", "--path", str(folder), "--id", "runtime-run", "--json")
        assert_true(runtime_check.returncode == 0, f"runtime-check --json should succeed, got {runtime_check.returncode}, stderr={runtime_check.stderr}")
        payload = json.loads(runtime_check.stdout)
        assert_true(payload["refused"] is False, "runtime-check JSON should expose refused=false")
        assert_true(payload["runtime_invocation_ready"] is False, "default scaffold should not be runtime-ready")
        assert_true(payload["execution_authorized"] is False, "runtime-check must not grant execution authorization")
        assert_true(payload["approval_gates_required"] is True, "unresolved approval gates should be treated conservatively")
        assert_true(payload["checks"]["declares_source_cap"] is True, "default scaffold should declare CAP trace")
        assert_true(payload["checks"]["declares_source_team_operating_packet"] is True, "default scaffold should declare TOP trace")
        assert_true(any(finding["code"] == "authorized_capabilities_unresolved" for finding in payload["blocking_findings"]), "default scaffold should flag unresolved authorized capabilities")
        report_path = Path(payload["runtime_readiness_report_path"])
        assert_true(report_path.exists(), "runtime-check should write a report inside the packet run directory")
        assert_true(report_path.parent == Path(payload["run_dir"]), "runtime readiness report should live in the packet run directory")
        report = json.loads(report_path.read_text(encoding="utf-8"))
        assert_true(report["report_type"] == "artifact_harness_runtime_readiness", "report should identify its type")
        assert_true("SENTINEL_RUNTIME_CHECK_SHOULD_NOT_TOUCH_MARKDOWN" in runtime_path.read_text(encoding="utf-8"), "runtime-check should not rewrite packet Markdown")

        human = run_brain(ws, "artifact-harness", "runtime-check", "--path", str(folder), "--id", "runtime-run")
        assert_true(human.returncode == 0, f"runtime-check human mode should succeed, got {human.returncode}, stderr={human.stderr}")
        assert_true("# Artifact Harness Runtime Readiness" in human.stdout, "human runtime-check should render a summary")


def test_artifact_harness_runtime_check_json_refusal_is_parseable() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-artifact-runtime-refusal-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        folder = ws / "artifact_case"
        folder.mkdir(parents=True, exist_ok=True)
        runtime_check = run_brain(ws, "artifact-harness", "runtime-check", "--path", str(folder), "--id", "missing-runtime", "--json")
        assert_true(runtime_check.returncode != 0, "runtime-check --json should fail for a missing run")
        payload = json.loads(runtime_check.stdout)
        assert_true(payload["refused"] is True, "runtime-check refusal JSON should expose refused=true")
        assert_true(payload["reason"] == "missing_packet_run", "runtime-check refusal should identify missing run")
        assert_true(payload["runtime_readiness_report_path"].endswith("/runtime_readiness_report.json"), "runtime-check refusal should include attempted report path")
        assert_true(not Path(payload["runtime_readiness_report_path"]).exists(), "missing-run runtime-check should not write a report")


def test_artifact_harness_runtime_check_blocks_approval_gate_cli_conflict() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-artifact-runtime-cli-conflict-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        folder = ws / "artifact_case"
        folder.mkdir(parents=True, exist_ok=True)
        create = run_brain(ws, "artifact-harness", "Draft a gated runtime packet", "--path", str(folder), "--id", "runtime-gated", "--json")
        assert_true(create.returncode == 0, f"artifact-harness create should succeed, got {create.returncode}, stderr={create.stderr}")
        create_payload = json.loads(create.stdout)
        runtime_path = Path(create_payload["packets"]["runtime_mapping"])
        text = runtime_path.read_text(encoding="utf-8")
        text = text.replace("- approval gates required: yes/no", "- approval gates required: yes")
        text = text.replace("- authorized skills:", "- authorized skills: artifact-builder")
        text = text.replace("- authorized plugins:", "- authorized plugins: none")
        text = text.replace("- authorized tools:", "- authorized tools: bash")
        text = text.replace("- denied or withheld capabilities:", "- denied or withheld capabilities: network")
        text = text.replace("- CAP approval gates:", "- CAP approval gates: human approval before runtime execution")
        text = text.replace("- CLI allowed:", "- CLI allowed: yes")
        runtime_path.write_text(text, encoding="utf-8")

        runtime_check = run_brain(ws, "artifact-harness", "runtime-check", "--path", str(folder), "--id", "runtime-gated", "--json")
        assert_true(runtime_check.returncode == 0, f"runtime-check should complete as preflight even when not ready, got {runtime_check.returncode}, stderr={runtime_check.stderr}")
        payload = json.loads(runtime_check.stdout)
        finding_codes = [finding["code"] for finding in payload["blocking_findings"]]
        assert_true("approval_gate_requires_enforceable_api" in finding_codes, "approval-gated CLI execution should be blocked")
        assert_true(payload["runtime_invocation_ready"] is False, "approval-gated CLI conflict should fail readiness")
        assert_true(payload["execution_authorized"] is False, "runtime-check should not grant execution authorization")
        assert_true(payload["required_execution_surface"] == "typescript_api_runTasks_with_approval_callbacks", "gated execution should require TypeScript API callbacks")


def test_artifact_harness_runtime_check_allows_cli_when_no_approval_gate_without_authorizing_execution() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-artifact-runtime-cli-nogate-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        folder = ws / "artifact_case"
        folder.mkdir(parents=True, exist_ok=True)
        create = run_brain(ws, "artifact-harness", "Draft a no-gate runtime packet", "--path", str(folder), "--id", "runtime-nogate", "--json")
        assert_true(create.returncode == 0, f"artifact-harness create should succeed, got {create.returncode}, stderr={create.stderr}")
        create_payload = json.loads(create.stdout)
        runtime_path = Path(create_payload["packets"]["runtime_mapping"])
        text = runtime_path.read_text(encoding="utf-8")
        text = text.replace("- approval gates required: yes/no", "- approval gates required: no")
        text = text.replace("- authorized skills:", "- authorized skills: none")
        text = text.replace("- authorized plugins:", "- authorized plugins: none")
        text = text.replace("- authorized tools:", "- authorized tools: local shell")
        text = text.replace("- denied or withheld capabilities:", "- denied or withheld capabilities: network")
        text = text.replace("- CAP approval gates:", "- CAP approval gates: none")
        text = text.replace("- CLI allowed:", "- CLI allowed: yes")
        runtime_path.write_text(text, encoding="utf-8")

        runtime_check = run_brain(ws, "artifact-harness", "runtime-check", "--path", str(folder), "--id", "runtime-nogate", "--json")
        assert_true(runtime_check.returncode == 0, f"runtime-check should succeed, got {runtime_check.returncode}, stderr={runtime_check.stderr}")
        payload = json.loads(runtime_check.stdout)
        finding_codes = [finding["code"] for finding in payload["blocking_findings"]]
        assert_true("approval_gate_requires_enforceable_api" not in finding_codes, "CLI allowed should not conflict when approval gates are explicitly not required")
        assert_true(payload["checks"]["cli_execution_allowed"] is True, "runtime-check should detect CLI allowance")
        assert_true(payload["approval_gates_required"] is False, "runtime-check should detect no approval gates")
        assert_true(payload["execution_authorized"] is False, "explicit no-gate CLI allowance still should not grant execution authorization")


def test_artifact_harness_runtime_check_refuses_manifest_packet_outside_target() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-artifact-runtime-boundary-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        folder = ws / "artifact_case"
        folder.mkdir(parents=True, exist_ok=True)
        create = run_brain(ws, "artifact-harness", "Draft a boundary-safe runtime packet", "--path", str(folder), "--id", "runtime-boundary-run", "--json")
        assert_true(create.returncode == 0, f"artifact-harness create should succeed, got {create.returncode}, stderr={create.stderr}")
        create_payload = json.loads(create.stdout)

        runtime_ok = run_brain(ws, "artifact-harness", "runtime-check", "--path", str(folder), "--id", "runtime-boundary-run", "--json")
        assert_true(runtime_ok.returncode == 0, f"initial runtime-check should succeed, got {runtime_ok.returncode}, stderr={runtime_ok.stderr}")
        report_path = Path(json.loads(runtime_ok.stdout)["runtime_readiness_report_path"])
        report_before = report_path.read_text(encoding="utf-8")

        outside_secret = ws / "outside_secret.md"
        write_file(outside_secret, "SECRET_RUNTIME_OPEN_QUESTION\n- stolen_field:\n")
        manifest_path = Path(create_payload["manifest"])
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["packets"]["runtime_mapping"] = "../outside_secret.md"
        write_file(manifest_path, json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")

        runtime_check = run_brain(ws, "artifact-harness", "runtime-check", "--path", str(folder), "--id", "runtime-boundary-run", "--json")
        assert_true(runtime_check.returncode != 0, "runtime-check should refuse a manifest packet path outside the target workspace")
        payload = json.loads(runtime_check.stdout)
        assert_true(payload["refused"] is True, "outside manifest path refusal should expose refused=true")
        assert_true(payload["reason"] == "manifest_packet_path_outside_target_workspace", "outside manifest path refusal should use the expected reason")
        assert_true(payload["offending_packet_key"] == "runtime_mapping", "refusal should identify the offending packet key")
        assert_true(Path(payload["attempted_path"]).resolve() == outside_secret.resolve(), "refusal should identify the attempted outside path")
        assert_true("SECRET_RUNTIME_OPEN_QUESTION" not in runtime_check.stdout, "runtime-check refusal should not leak outside file content")
        assert_true("checks" in payload and payload["checks"] == {}, "runtime-check refusal should not emit checks from outside content")
        assert_true(report_path.read_text(encoding="utf-8") == report_before, "runtime-check refusal should not rewrite existing report")


def configure_runtime_mapping_for_invocation(
    runtime_path: Path,
    *,
    approval_gates_required: bool = True,
    cli_allowed: bool = False,
    authorized_tools: str = "bash, network",
    denied_capabilities: str = "network",
) -> None:
    text = runtime_path.read_text(encoding="utf-8")
    text = text.replace("- approval gates required: yes/no", f"- approval gates required: {'yes' if approval_gates_required else 'no'}")
    text = text.replace("- authorized skills:", "- authorized skills: artifact-builder")
    text = text.replace("- authorized plugins:", "- authorized plugins: none")
    text = text.replace("- authorized tools:", f"- authorized tools: {authorized_tools}")
    text = text.replace("- denied or withheld capabilities:", f"- denied or withheld capabilities: {denied_capabilities}")
    text = text.replace("- CAP approval gates:", "- CAP approval gates: runtime_execution requires explicit approval")
    text = text.replace("- CLI allowed:", f"- CLI allowed: {'yes' if cli_allowed else 'no'}")
    runtime_path.write_text(text, encoding="utf-8")


def create_runtime_invocation_ready_packet(ws: Path, folder: Path, packet_id: str) -> dict[str, object]:
    create = run_brain(ws, "artifact-harness", "Draft an invocation-ready runtime packet", "--path", str(folder), "--id", packet_id, "--json")
    assert_true(create.returncode == 0, f"artifact-harness create should succeed, got {create.returncode}, stderr={create.stderr}")
    create_payload = json.loads(create.stdout)
    configure_runtime_mapping_for_invocation(Path(create_payload["packets"]["runtime_mapping"]))
    runtime_check = run_brain(ws, "artifact-harness", "runtime-check", "--path", str(folder), "--id", packet_id, "--json")
    assert_true(runtime_check.returncode == 0, f"runtime-check should succeed for invocation-ready packet, got {runtime_check.returncode}, stderr={runtime_check.stderr}")
    readiness_payload = json.loads(runtime_check.stdout)
    assert_true(readiness_payload["runtime_invocation_ready"] is True, "configured runtime mapping should pass readiness")
    return {"create": create_payload, "readiness": readiness_payload}


def record_runtime_approval(ws: Path, folder: Path, packet_id: str, decision: str = "approved") -> dict[str, object]:
    approval = run_brain(
        ws,
        "artifact-harness",
        "approval",
        "--path",
        str(folder),
        "--id",
        packet_id,
        "--gate",
        "runtime_execution",
        "--decision",
        decision,
        "--approver",
        "test-reviewer",
        "--note",
        f"{decision} for regression test",
        "--json",
    )
    assert_true(approval.returncode == 0, f"approval command should succeed, got {approval.returncode}, stderr={approval.stderr}")
    return json.loads(approval.stdout)


def test_artifact_harness_approval_records_evidence_and_preserves_markdown() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-artifact-approval-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        folder = ws / "artifact_case"
        folder.mkdir(parents=True, exist_ok=True)
        create = run_brain(ws, "artifact-harness", "Draft an approval evidence packet", "--path", str(folder), "--id", "approval-run", "--json")
        assert_true(create.returncode == 0, f"artifact-harness create should succeed, got {create.returncode}, stderr={create.stderr}")
        create_payload = json.loads(create.stdout)
        spec_path = Path(create_payload["packets"]["artifact_harness_spec"])
        spec_path.write_text(spec_path.read_text(encoding="utf-8") + "\nSENTINEL_APPROVAL_SHOULD_NOT_TOUCH_MARKDOWN\n", encoding="utf-8")
        before = spec_path.read_text(encoding="utf-8")

        payload = record_runtime_approval(ws, folder, "approval-run")
        approval_path = Path(payload["approval_evidence_path"])
        assert_true(approval_path.exists(), "approval command should write approval evidence")
        evidence = json.loads(approval_path.read_text(encoding="utf-8"))
        assert_true(evidence["latest_decisions"]["runtime_execution"]["decision"] == "approved", "latest approval decision should be recorded")
        assert_true(spec_path.read_text(encoding="utf-8") == before, "approval command should not rewrite packet Markdown")


def test_artifact_harness_approval_latest_deny_overrides_earlier_approval() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-artifact-approval-deny-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        folder = ws / "artifact_case"
        folder.mkdir(parents=True, exist_ok=True)
        create = run_brain(ws, "artifact-harness", "Draft an approval override packet", "--path", str(folder), "--id", "approval-deny-run", "--json")
        assert_true(create.returncode == 0, f"artifact-harness create should succeed, got {create.returncode}, stderr={create.stderr}")
        record_runtime_approval(ws, folder, "approval-deny-run", "approved")
        payload = record_runtime_approval(ws, folder, "approval-deny-run", "denied")
        assert_true(payload["latest_decisions"]["runtime_execution"]["decision"] == "denied", "latest deny should override earlier approval")


def test_artifact_harness_runtime_invoke_refuses_readiness_blockers() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-artifact-invoke-blocked-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        folder = ws / "artifact_case"
        folder.mkdir(parents=True, exist_ok=True)
        create = run_brain(ws, "artifact-harness", "Draft a blocked invocation packet", "--path", str(folder), "--id", "invoke-blocked", "--json")
        assert_true(create.returncode == 0, f"artifact-harness create should succeed, got {create.returncode}, stderr={create.stderr}")
        invoke = run_brain(ws, "artifact-harness", "runtime-invoke", "--path", str(folder), "--id", "invoke-blocked", "--adapter", "open-multi-agent", "--surface", "typescript-runTasks", "--dry-run", "--json")
        assert_true(invoke.returncode != 0, "runtime-invoke should refuse when runtime readiness has blocking findings")
        payload = json.loads(invoke.stdout)
        assert_true(payload["reason"] == "runtime_readiness_blocking_findings", "runtime-invoke should expose readiness blocking reason")
        assert_true(payload["execution_performed"] is False, "runtime-invoke must not execute adapters")
        assert_true(Path(payload["runtime_invocation_report_path"]).exists(), "runtime-invoke refusal should write a report when run state is valid")


def test_artifact_harness_runtime_invoke_requires_approval_evidence() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-artifact-invoke-no-approval-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        folder = ws / "artifact_case"
        folder.mkdir(parents=True, exist_ok=True)
        create_runtime_invocation_ready_packet(ws, folder, "invoke-no-approval")
        invoke = run_brain(ws, "artifact-harness", "runtime-invoke", "--path", str(folder), "--id", "invoke-no-approval", "--adapter", "open-multi-agent", "--surface", "typescript-runTasks", "--dry-run", "--json")
        assert_true(invoke.returncode != 0, "runtime-invoke should refuse gated invocation without approval evidence")
        payload = json.loads(invoke.stdout)
        assert_true(payload["reason"] == "missing_required_approval_evidence", "runtime-invoke should require explicit approval evidence")
        assert_true(payload["execution_performed"] is False, "runtime-invoke should remain non-executing")


def test_artifact_harness_runtime_invoke_forbids_cli_when_approval_gated() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-artifact-invoke-cli-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        folder = ws / "artifact_case"
        folder.mkdir(parents=True, exist_ok=True)
        create_runtime_invocation_ready_packet(ws, folder, "invoke-cli")
        record_runtime_approval(ws, folder, "invoke-cli")
        invoke = run_brain(ws, "artifact-harness", "runtime-invoke", "--path", str(folder), "--id", "invoke-cli", "--adapter", "open-multi-agent", "--surface", "cli", "--dry-run", "--json")
        assert_true(invoke.returncode != 0, "runtime-invoke should refuse CLI when approval gates are required")
        payload = json.loads(invoke.stdout)
        assert_true(payload["reason"] == "approval_gated_cli_forbidden", "runtime-invoke should identify gated CLI refusal")


def test_artifact_harness_runtime_invoke_dry_run_with_approval_filters_denied_capabilities() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-artifact-invoke-pass-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        folder = ws / "artifact_case"
        folder.mkdir(parents=True, exist_ok=True)
        setup = create_runtime_invocation_ready_packet(ws, folder, "invoke-pass")
        spec_path = Path(setup["create"]["packets"]["artifact_harness_spec"])  # type: ignore[index]
        spec_path.write_text(spec_path.read_text(encoding="utf-8") + "\nSENTINEL_INVOKE_SHOULD_NOT_TOUCH_MARKDOWN\n", encoding="utf-8")
        spec_before = spec_path.read_text(encoding="utf-8")
        readiness_path = Path(setup["readiness"]["runtime_readiness_report_path"])  # type: ignore[index]
        readiness_before = readiness_path.read_text(encoding="utf-8")
        approval_payload = record_runtime_approval(ws, folder, "invoke-pass")
        approval_path = Path(approval_payload["approval_evidence_path"])
        approval_before = approval_path.read_text(encoding="utf-8")
        run_dir = readiness_path.parent
        before_files = {path.name for path in run_dir.iterdir()}

        invoke = run_brain(ws, "artifact-harness", "runtime-invoke", "--path", str(folder), "--id", "invoke-pass", "--adapter", "open-multi-agent", "--surface", "typescript-runTasks", "--dry-run", "--json")
        assert_true(invoke.returncode == 0, f"runtime-invoke dry-run should pass with approval, got {invoke.returncode}, stderr={invoke.stderr}")
        payload = json.loads(invoke.stdout)
        report_path = Path(payload["runtime_invocation_report_path"])
        assert_true(report_path.exists(), "runtime-invoke should write invocation report")
        assert_true(payload["runtime_invocation_allowed"] is True, "guard should allow dry-run envelope")
        assert_true(payload["would_execute"] is True, "guard should mark would_execute only on passing dry-run")
        assert_true(payload["execution_performed"] is False, "runtime-invoke must never execute in this round")
        assert_true("network" not in [item.lower() for item in payload["exposed_capabilities"]], "denied capability should not be exposed")
        assert_true("network" in [item.lower() for item in payload["withheld_capabilities"]], "denied capability should remain withheld")
        assert_true(spec_path.read_text(encoding="utf-8") == spec_before, "runtime-invoke should not rewrite packet Markdown")
        assert_true(readiness_path.read_text(encoding="utf-8") == readiness_before, "runtime-invoke should not rewrite existing readiness report")
        assert_true(approval_path.read_text(encoding="utf-8") == approval_before, "runtime-invoke should not rewrite approval evidence")
        after_files = {path.name for path in run_dir.iterdir()}
        assert_true(after_files == before_files | {"runtime_invocation_report.json"}, "passing dry-run should add only runtime_invocation_report.json")

        second = run_brain(ws, "artifact-harness", "runtime-invoke", "--path", str(folder), "--id", "invoke-pass", "--adapter", "open-multi-agent", "--surface", "typescript-runTasks", "--dry-run", "--json")
        assert_true(second.returncode == 0, f"second dry-run should stay idempotent, got {second.returncode}, stderr={second.stderr}")
        assert_true({path.name for path in run_dir.iterdir()} == after_files, "second dry-run should not add extra files")


def test_artifact_harness_runtime_invoke_latest_deny_blocks_invocation() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-artifact-invoke-denied-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        folder = ws / "artifact_case"
        folder.mkdir(parents=True, exist_ok=True)
        create_runtime_invocation_ready_packet(ws, folder, "invoke-denied")
        record_runtime_approval(ws, folder, "invoke-denied", "approved")
        record_runtime_approval(ws, folder, "invoke-denied", "denied")
        invoke = run_brain(ws, "artifact-harness", "runtime-invoke", "--path", str(folder), "--id", "invoke-denied", "--adapter", "open-multi-agent", "--surface", "typescript-runTasks", "--dry-run", "--json")
        assert_true(invoke.returncode != 0, "runtime-invoke should refuse when latest required gate decision is denied")
        payload = json.loads(invoke.stdout)
        assert_true(payload["reason"] == "approval_denied", "latest denied gate should block invocation")
        assert_true("runtime_execution" in payload["denied_gates"], "denied gate should be listed")


def test_artifact_harness_approval_and_runtime_invoke_missing_run_refusals_are_parseable() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-artifact-invoke-missing-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        folder = ws / "artifact_case"
        folder.mkdir(parents=True, exist_ok=True)
        approval = run_brain(ws, "artifact-harness", "approval", "--path", str(folder), "--id", "missing-run", "--gate", "runtime_execution", "--decision", "approved", "--approver", "test-reviewer", "--json")
        assert_true(approval.returncode != 0, "approval should refuse a missing packet run")
        approval_payload = json.loads(approval.stdout)
        assert_true(approval_payload["reason"] == "missing_packet_run", "approval missing-run refusal should identify missing run")

        invoke = run_brain(ws, "artifact-harness", "runtime-invoke", "--path", str(folder), "--id", "missing-run", "--adapter", "open-multi-agent", "--surface", "typescript-runTasks", "--dry-run", "--json")
        assert_true(invoke.returncode != 0, "runtime-invoke should refuse a missing packet run")
        invoke_payload = json.loads(invoke.stdout)
        assert_true(invoke_payload["reason"] == "missing_packet_run", "runtime-invoke missing-run refusal should identify missing run")
        assert_true(not Path(invoke_payload["runtime_invocation_report_path"]).exists(), "missing-run runtime-invoke should not write a report")


def test_artifact_harness_runtime_invoke_refuses_manifest_packet_outside_target() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-artifact-invoke-boundary-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        folder = ws / "artifact_case"
        folder.mkdir(parents=True, exist_ok=True)
        setup = create_runtime_invocation_ready_packet(ws, folder, "invoke-boundary")
        outside_secret = ws / "outside_secret.md"
        write_file(outside_secret, "SECRET_INVOKE_OPEN_QUESTION\n- stolen_field:\n")
        manifest_path = Path(setup["create"]["manifest"])  # type: ignore[index]
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["packets"]["runtime_mapping"] = "../outside_secret.md"
        write_file(manifest_path, json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")

        invoke = run_brain(ws, "artifact-harness", "runtime-invoke", "--path", str(folder), "--id", "invoke-boundary", "--adapter", "open-multi-agent", "--surface", "typescript-runTasks", "--dry-run", "--json")
        assert_true(invoke.returncode != 0, "runtime-invoke should refuse a manifest packet path outside the target workspace")
        payload = json.loads(invoke.stdout)
        assert_true(payload["reason"] == "manifest_packet_path_outside_target_workspace", "runtime-invoke should preserve outside-target refusal reason")
        assert_true(payload["offending_packet_key"] == "runtime_mapping", "runtime-invoke refusal should identify offending packet key")
        assert_true("SECRET_INVOKE_OPEN_QUESTION" not in invoke.stdout, "runtime-invoke refusal should not leak outside file content")


def test_artifact_harness_schema_check_current_run_and_missing_optional_reports() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-artifact-schema-current-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        folder = ws / "artifact_case"
        folder.mkdir(parents=True, exist_ok=True)
        create = run_brain(ws, "artifact-harness", "Draft a schema-current packet", "--path", str(folder), "--id", "schema-current", "--json")
        assert_true(create.returncode == 0, f"artifact-harness create should succeed, got {create.returncode}, stderr={create.stderr}")
        create_payload = json.loads(create.stdout)
        spec_path = Path(create_payload["packets"]["artifact_harness_spec"])
        spec_path.write_text(spec_path.read_text(encoding="utf-8") + "\nSENTINEL_SCHEMA_CHECK_SHOULD_NOT_TOUCH_MARKDOWN\n", encoding="utf-8")
        before = spec_path.read_text(encoding="utf-8")

        schema_check = run_brain(ws, "artifact-harness", "schema-check", "--path", str(folder), "--id", "schema-current", "--json")
        assert_true(schema_check.returncode == 0, f"schema-check --json should succeed, got {schema_check.returncode}, stderr={schema_check.stderr}")
        payload = json.loads(schema_check.stdout)
        assert_true(payload["command"] == "artifact-harness schema-check", "schema-check JSON should expose command envelope")
        assert_true(payload["schema_version"] == 1, "schema-check JSON should expose command schema version")
        assert_true(payload["ok"] is True and payload["refused"] is False, "current schema-check should be ok")
        assert_true(payload["compatible"] is True, "current run should be compatible")
        assert_true(payload["migration_required"] is False, "new current run should not require migration")
        assert_true(payload["current_schema_version"] == 1 and payload["supported_schema_version"] == 1, "schema versions should be explicit")
        assert_true(payload["missing_files"] == [], "current run should not miss required files")
        assert_true(payload["blocking_findings"] == [], "current run should not have blocking schema findings")
        assert_true(Path(payload["schema_metadata_path"]).exists(), "current run should include schema metadata sidecar")
        warning_codes = [warning["code"] for warning in payload["warnings"]]
        assert_true("missing_optional_generated_report" in warning_codes, "missing optional generated reports should warn, not block")
        checked_keys = [item["key"] for item in payload["checked_files"]]
        assert_true(
            {"replay_evidence", "runtime_readiness_report", "approval_evidence", "runtime_invocation_report", "repair_plan"}.issubset(set(checked_keys)),
            "schema-check should inspect optional report locations",
        )
        assert_true("migrate_json" in payload["commands"], "schema-check JSON should provide migrate command")
        assert_true("approval_json" in payload["commands"] and "runtime_invoke_json" in payload["commands"], "schema-check JSON should provide approval and runtime-invoke commands")
        assert_true(spec_path.read_text(encoding="utf-8") == before, "schema-check should not rewrite packet Markdown")


def test_artifact_harness_migrate_safe_older_run_is_idempotent_and_preserves_markdown() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-artifact-schema-migrate-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        folder = ws / "artifact_case"
        folder.mkdir(parents=True, exist_ok=True)
        create = run_brain(ws, "artifact-harness", "Draft an older schema packet", "--path", str(folder), "--id", "schema-old", "--json")
        assert_true(create.returncode == 0, f"artifact-harness create should succeed, got {create.returncode}, stderr={create.stderr}")
        create_payload = json.loads(create.stdout)
        spec_path = Path(create_payload["packets"]["artifact_harness_spec"])
        spec_path.write_text(spec_path.read_text(encoding="utf-8") + "\nSENTINEL_MIGRATE_SHOULD_NOT_TOUCH_MARKDOWN\n", encoding="utf-8")
        spec_before = spec_path.read_text(encoding="utf-8")

        manifest_path = Path(create_payload["manifest"])
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest.pop("schema_version", None)
        manifest.pop("schema_contract", None)
        write_file(manifest_path, json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
        schema_metadata_path = Path(create_payload["schema_metadata_path"])
        schema_metadata_path.unlink()
        registry_path = Path(create_payload["registry_path"])
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        registry.pop("schema_version", None)
        for entry in registry.get("entries", []):
            if isinstance(entry, dict) and entry.get("id") == "schema-old":
                entry.pop("schema_version", None)
                entry.pop("schema_metadata_path", None)
                entry.pop("manifest_schema_version", None)
        write_file(registry_path, json.dumps(registry, ensure_ascii=False, indent=2) + "\n")

        schema_check = run_brain(ws, "artifact-harness", "schema-check", "--path", str(folder), "--id", "schema-old", "--json")
        assert_true(schema_check.returncode == 0, f"older schema-check should succeed, got {schema_check.returncode}, stderr={schema_check.stderr}")
        check_payload = json.loads(schema_check.stdout)
        assert_true(check_payload["compatible"] is True, "safe older run should remain compatible")
        assert_true(check_payload["migration_required"] is True, "safe older run should require migration")

        migrate = run_brain(ws, "artifact-harness", "migrate", "--path", str(folder), "--id", "schema-old", "--json")
        assert_true(migrate.returncode == 0, f"migrate --json should succeed, got {migrate.returncode}, stderr={migrate.stderr}")
        payload = json.loads(migrate.stdout)
        assert_true(payload["command"] == "artifact-harness migrate", "migrate JSON should expose command envelope")
        assert_true(payload["ok"] is True and payload["refused"] is False, "migrate should complete for safe older run")
        assert_true(payload["compatible"] is True, "migrated run should be compatible")
        assert_true(payload["migration_required"] is False, "migrated run should no longer require migration")
        assert_true(str(manifest_path) in payload["changed_files"], "migrate should update manifest compatibility fields")
        assert_true(str(schema_metadata_path) in payload["changed_files"], "migrate should create schema metadata sidecar")
        assert_true(str(registry_path) in payload["changed_files"], "migrate should update registry compatibility fields")
        assert_true(spec_path.read_text(encoding="utf-8") == spec_before, "migrate should not rewrite packet Markdown")
        manifest_after = json.loads(manifest_path.read_text(encoding="utf-8"))
        assert_true(manifest_after["schema_version"] == 1, "migrate should restore manifest schema_version")
        assert_true(manifest_after["schema_contract"]["schema_metadata_path"].endswith("/packet_schema_metadata.json"), "migrate should record schema metadata path in manifest")
        assert_true(json.loads(schema_metadata_path.read_text(encoding="utf-8"))["metadata_type"] == "artifact_harness_schema_metadata", "schema metadata should identify its type")

        second = run_brain(ws, "artifact-harness", "migrate", "--path", str(folder), "--id", "schema-old", "--json")
        assert_true(second.returncode == 0, f"second migrate should be idempotent, got {second.returncode}, stderr={second.stderr}")
        second_payload = json.loads(second.stdout)
        assert_true(second_payload["changed_files"] == [], "second migrate should not rewrite already-current schema metadata")
        registry_after = json.loads(registry_path.read_text(encoding="utf-8"))
        assert_true(sum(1 for entry in registry_after["entries"] if isinstance(entry, dict) and entry.get("id") == "schema-old") == 1, "migrate should not create duplicate registry entries")
        assert_true(spec_path.read_text(encoding="utf-8") == spec_before, "second migrate should still preserve packet Markdown")


def test_artifact_harness_migrate_refuses_missing_required_packet() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-artifact-schema-missing-packet-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        folder = ws / "artifact_case"
        folder.mkdir(parents=True, exist_ok=True)
        create = run_brain(ws, "artifact-harness", "Draft a missing packet schema case", "--path", str(folder), "--id", "schema-missing-packet", "--json")
        assert_true(create.returncode == 0, f"artifact-harness create should succeed, got {create.returncode}, stderr={create.stderr}")
        create_payload = json.loads(create.stdout)
        missing_packet = Path(create_payload["packets"]["hr_staffing_packet"])
        missing_packet.unlink()

        schema_check = run_brain(ws, "artifact-harness", "schema-check", "--path", str(folder), "--id", "schema-missing-packet", "--json")
        assert_true(schema_check.returncode == 0, f"schema-check should report missing packet without refusing inspection, got {schema_check.returncode}, stderr={schema_check.stderr}")
        check_payload = json.loads(schema_check.stdout)
        assert_true(check_payload["compatible"] is False, "missing required packet should make run incompatible")
        assert_true(any(item["key"] == "hr_staffing_packet" for item in check_payload["missing_files"]), "schema-check should report missing HR packet")

        migrate = run_brain(ws, "artifact-harness", "migrate", "--path", str(folder), "--id", "schema-missing-packet", "--json")
        assert_true(migrate.returncode != 0, "migrate should refuse when a required packet file is missing")
        payload = json.loads(migrate.stdout)
        assert_true(payload["refused"] is True, "migrate missing-packet refusal should expose refused=true")
        assert_true(payload["reason"] == "schema_migration_blocked", "migrate missing-packet refusal should identify blocked migration")
        assert_true(any(finding["code"] == "missing_required_file" for finding in payload["blocking_findings"]), "migrate refusal should include missing_required_file finding")


def test_artifact_harness_schema_check_refuses_manifest_packet_outside_target() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-artifact-schema-boundary-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        folder = ws / "artifact_case"
        folder.mkdir(parents=True, exist_ok=True)
        create = run_brain(ws, "artifact-harness", "Draft a schema boundary packet", "--path", str(folder), "--id", "schema-boundary", "--json")
        assert_true(create.returncode == 0, f"artifact-harness create should succeed, got {create.returncode}, stderr={create.stderr}")
        create_payload = json.loads(create.stdout)

        outside_secret = ws / "outside_secret.md"
        write_file(outside_secret, "SECRET_SCHEMA_OUTSIDE_CONTENT\n")
        manifest_path = Path(create_payload["manifest"])
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["packets"]["artifact_harness_spec"] = "../outside_secret.md"
        write_file(manifest_path, json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")

        schema_check = run_brain(ws, "artifact-harness", "schema-check", "--path", str(folder), "--id", "schema-boundary", "--json")
        assert_true(schema_check.returncode != 0, "schema-check should refuse manifest packet path outside target workspace")
        payload = json.loads(schema_check.stdout)
        assert_true(payload["refused"] is True, "schema-check outside-path refusal should expose refused=true")
        assert_true(payload["reason"] == "manifest_packet_path_outside_target_workspace", "schema-check should use manifest outside-path refusal reason")
        assert_true(payload["offending_packet_key"] == "artifact_harness_spec", "schema-check should identify offending packet key")
        assert_true("SECRET_SCHEMA_OUTSIDE_CONTENT" not in schema_check.stdout, "schema-check should not read or leak outside file content")

        migrate = run_brain(ws, "artifact-harness", "migrate", "--path", str(folder), "--id", "schema-boundary", "--json")
        assert_true(migrate.returncode != 0, "migrate should refuse manifest packet path outside target workspace")
        migrate_payload = json.loads(migrate.stdout)
        assert_true(migrate_payload["reason"] == "manifest_packet_path_outside_target_workspace", "migrate should share manifest outside-path refusal reason")
        assert_true("SECRET_SCHEMA_OUTSIDE_CONTENT" not in migrate.stdout, "migrate should not read or leak outside file content")


def test_artifact_harness_repair_plan_writes_plan_and_preserves_markdown() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-artifact-repair-open-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        folder = ws / "artifact_case"
        folder.mkdir(parents=True, exist_ok=True)
        create = run_brain(ws, "artifact-harness", "Draft a repair-plan packet", "--path", str(folder), "--id", "repair-open", "--json")
        assert_true(create.returncode == 0, f"artifact-harness create should succeed, got {create.returncode}, stderr={create.stderr}")
        create_payload = json.loads(create.stdout)
        spec_path = Path(create_payload["packets"]["artifact_harness_spec"])
        spec_path.write_text(spec_path.read_text(encoding="utf-8") + "\nSENTINEL_REPAIR_SHOULD_NOT_TOUCH_MARKDOWN\n", encoding="utf-8")
        spec_before = spec_path.read_text(encoding="utf-8")
        run_dir = Path(create_payload["run_dir"])
        before_files = {path.name for path in run_dir.iterdir()}

        repair = run_brain(ws, "artifact-harness", "repair-plan", "--path", str(folder), "--id", "repair-open", "--json")
        assert_true(repair.returncode == 0, f"repair-plan --json should succeed, got {repair.returncode}, stderr={repair.stderr}")
        payload = json.loads(repair.stdout)
        repair_path = Path(payload["repair_plan_path"])
        assert_true(payload["command"] == "artifact-harness repair-plan", "repair-plan JSON should expose command envelope")
        assert_true(payload["refused"] is False, "repair-plan should not refuse an existing run")
        assert_true(payload["needs_repair"] is True, "draft scaffold with open fields should need repair")
        assert_true(repair_path.exists(), "repair-plan should write repair_plan.json")
        assert_true(any(item["code"] == "packet_open_items_detected" for item in payload["repair_items"]), "repair-plan should surface open packet fields")
        assert_true("repair_plan_json" in payload["commands"], "repair-plan should expose a stable rerun command")
        assert_true(spec_path.read_text(encoding="utf-8") == spec_before, "repair-plan should not rewrite packet Markdown")
        assert_true({path.name for path in run_dir.iterdir()} == before_files | {"repair_plan.json"}, "repair-plan should add only repair_plan.json")

        schema_check = run_brain(ws, "artifact-harness", "schema-check", "--path", str(folder), "--id", "repair-open", "--json")
        assert_true(schema_check.returncode == 0, f"schema-check after repair-plan should succeed, got {schema_check.returncode}, stderr={schema_check.stderr}")
        schema_payload = json.loads(schema_check.stdout)
        repair_checked = [item for item in schema_payload["checked_files"] if item["key"] == "repair_plan"]
        assert_true(repair_checked and repair_checked[0]["schema_version"] == 1, "schema-check should inspect repair_plan schema version when present")


def test_artifact_harness_repair_plan_surfaces_blocked_lifecycle_and_denied_approval() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-artifact-repair-blocked-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        folder = ws / "artifact_case"
        folder.mkdir(parents=True, exist_ok=True)
        create = run_brain(ws, "artifact-harness", "Draft a blocked repair packet", "--path", str(folder), "--id", "repair-blocked", "--json")
        assert_true(create.returncode == 0, f"artifact-harness create should succeed, got {create.returncode}, stderr={create.stderr}")
        mark = run_brain(ws, "artifact-harness", "mark", "--path", str(folder), "--id", "repair-blocked", "--status", "blocked", "--note", "missing source evidence", "--json")
        assert_true(mark.returncode == 0, f"mark blocked should succeed, got {mark.returncode}, stderr={mark.stderr}")
        record_runtime_approval(ws, folder, "repair-blocked", "denied")

        repair = run_brain(ws, "artifact-harness", "repair-plan", "--path", str(folder), "--id", "repair-blocked", "--json")
        assert_true(repair.returncode == 0, f"repair-plan should succeed for blocked run, got {repair.returncode}, stderr={repair.stderr}")
        payload = json.loads(repair.stdout)
        codes = {item["code"] for item in payload["repair_items"]}
        assert_true("lifecycle_blocked" in codes, "repair-plan should surface blocked lifecycle status")
        assert_true("approval_gate_denied" in codes, "repair-plan should surface denied approval gates")
        assert_true(payload["ready_to_continue"] is False, "blocked/denied repair plan should not be ready to continue")


def test_artifact_harness_repair_plan_surfaces_runtime_invocation_refusal() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-artifact-repair-invoke-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        folder = ws / "artifact_case"
        folder.mkdir(parents=True, exist_ok=True)
        create_runtime_invocation_ready_packet(ws, folder, "repair-invoke")
        invoke = run_brain(ws, "artifact-harness", "runtime-invoke", "--path", str(folder), "--id", "repair-invoke", "--adapter", "open-multi-agent", "--surface", "typescript-runTasks", "--dry-run", "--json")
        assert_true(invoke.returncode != 0, "runtime-invoke should refuse gated invocation without approval evidence")

        repair = run_brain(ws, "artifact-harness", "repair-plan", "--path", str(folder), "--id", "repair-invoke", "--json")
        assert_true(repair.returncode == 0, f"repair-plan should succeed after invocation refusal, got {repair.returncode}, stderr={repair.stderr}")
        payload = json.loads(repair.stdout)
        codes = {item["code"] for item in payload["repair_items"]}
        assert_true("missing_required_approval_evidence" in codes, "repair-plan should surface missing approval evidence")
        assert_true("runtime_invocation_refused" in codes, "repair-plan should surface latest invocation refusal")
        assert_true(payload["summary"]["runtime_invocation_report_present"] is True, "repair summary should note invocation report presence")


def test_artifact_harness_repair_plan_missing_run_refusal_is_parseable() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-artifact-repair-missing-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        folder = ws / "artifact_case"
        folder.mkdir(parents=True, exist_ok=True)
        repair = run_brain(ws, "artifact-harness", "repair-plan", "--path", str(folder), "--id", "missing-run", "--json")
        assert_true(repair.returncode != 0, "repair-plan should refuse a missing packet run")
        payload = json.loads(repair.stdout)
        assert_true(payload["command"] == "artifact-harness repair-plan", "repair-plan refusal should expose command envelope")
        assert_true(payload["refused"] is True, "repair-plan missing-run refusal should expose refused=true")
        assert_true(payload["reason"] == "missing_packet_run", "repair-plan missing-run refusal should identify missing run")
        assert_true(not Path(payload["repair_plan_path"]).exists(), "missing-run repair-plan should not write repair_plan.json")


def test_artifact_harness_replay_refuses_manifest_packet_outside_target() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-artifact-replay-boundary-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        folder = ws / "artifact_case"
        folder.mkdir(parents=True, exist_ok=True)
        create = run_brain(ws, "artifact-harness", "Draft a boundary-safe replay packet", "--path", str(folder), "--id", "boundary-run", "--json")
        assert_true(create.returncode == 0, f"artifact-harness create should succeed, got {create.returncode}, stderr={create.stderr}")
        create_payload = json.loads(create.stdout)

        replay_ok = run_brain(ws, "artifact-harness", "replay", "--path", str(folder), "--id", "boundary-run", "--json")
        assert_true(replay_ok.returncode == 0, f"initial replay should succeed, got {replay_ok.returncode}, stderr={replay_ok.stderr}")
        evidence_path = Path(json.loads(replay_ok.stdout)["evidence_path"])
        evidence_before = evidence_path.read_text(encoding="utf-8")

        outside_secret = ws / "outside_secret.md"
        write_file(outside_secret, "SECRET_OPEN_QUESTION\n- stolen_field:\n")
        manifest_path = Path(create_payload["manifest"])
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["packets"]["artifact_harness_spec"] = "../outside_secret.md"
        write_file(manifest_path, json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")

        replay = run_brain(ws, "artifact-harness", "replay", "--path", str(folder), "--id", "boundary-run", "--json")
        assert_true(replay.returncode != 0, "replay should refuse a manifest packet path outside the target workspace")
        payload = json.loads(replay.stdout)
        assert_true(payload["refused"] is True, "outside manifest path refusal should expose refused=true")
        assert_true(payload["reason"] == "manifest_packet_path_outside_target_workspace", "outside manifest path refusal should use the expected reason")
        assert_true(payload["offending_packet_key"] == "artifact_harness_spec", "refusal should identify the offending packet key")
        assert_true(Path(payload["attempted_path"]).resolve() == outside_secret.resolve(), "refusal should identify the attempted outside path")
        assert_true("SECRET_OPEN_QUESTION" not in replay.stdout, "replay refusal should not leak outside file content")
        assert_true("heuristic_open_items" not in replay.stdout, "replay refusal should not report outside file heuristics")
        assert_true(evidence_path.read_text(encoding="utf-8") == evidence_before, "replay refusal should not rewrite existing evidence")

        status = run_brain(ws, "artifact-harness", "status", "--path", str(folder), "--id", "boundary-run", "--json")
        assert_true(status.returncode != 0, "status should also refuse a manifest packet path outside the target workspace")
        status_payload = json.loads(status.stdout)
        assert_true(status_payload["reason"] == "manifest_packet_path_outside_target_workspace", "status refusal should share the manifest path boundary reason")


def test_artifact_harness_json_refuses_packet_root_outside_target_workspace() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-artifact-json-refusal-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        folder = ws / "artifact_case"
        folder.mkdir(parents=True, exist_ok=True)
        outside_packet_root = ws / "outside_packet_root"
        set_artifact_harness_packet_root(ws, outside_packet_root)
        result = run_brain(
            ws,
            "artifact-harness",
            "Draft a review-ready methods appendix",
            "--path",
            str(folder),
            "--id",
            "outside-root",
            "--json",
        )
        assert_true(result.returncode != 0, "artifact-harness --json should fail when packet root is outside target workspace")
        payload = json.loads(result.stdout)
        assert_true(payload["created"] is False and payload["refused"] is True, "refusal JSON should expose created/refused state")
        assert_true(payload["reason"] == "packet_root_outside_target_workspace", "refusal JSON should identify packet root boundary failure")
        assert_true(payload["target_path"] == str(folder.resolve()), "refusal JSON should include target path")
        assert_true(Path(payload["packet_root"]).resolve() == outside_packet_root.resolve(), "refusal JSON should include attempted packet root")
        assert_true(Path(payload["run_dir"]).resolve() == (outside_packet_root / "outside-root").resolve(), "refusal JSON should include attempted run directory")
        assert_true(Path(payload["registry_path"]).resolve() == (ws / "artifact_harness_registry.json").resolve(), "refusal JSON should include attempted registry path")
        assert_true("outside target workspace" in result.stderr, "refusal should retain human stderr diagnostics")
        assert_true(not outside_packet_root.exists(), "refusal should not create packet root outside target workspace")


def test_repo_does_not_carry_smoke_artifact_harness_outputs() -> None:
    smoke_dir = ROOT / "contexts" / "artifact_harness_runs" / "smoke-artifact-harness"
    assert_true(not smoke_dir.exists(), "repo should not carry smoke-artifact-harness run output")
    registry_path = ROOT / "contexts" / "artifact_harness_registry.json"
    if registry_path.exists():
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        entries = registry.get("entries", [])
        assert_true(
            not any(isinstance(entry, dict) and entry.get("id") == "smoke-artifact-harness" for entry in entries),
            "repo artifact harness registry should not retain smoke-artifact-harness entries",
        )


def test_packet_route_keyword_routes_to_artifact_harness() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-packet-route-hit-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        folder = ws / "artifact_case"
        folder.mkdir(parents=True, exist_ok=True)
        result = run_brain(ws, "packet-route", "please packet form this methods appendix", "--path", str(folder))
        assert_true(result.returncode == 0, f"packet-route hit expected 0, got {result.returncode}, stderr={result.stderr}")
        assert_true("# Packet Route" in result.stdout, "packet-route should render a route summary")
        assert_true("Matched: `true`" in result.stdout, "packet-route should match the fixture keyword")
        assert_true("Route: `artifact_harness_workflow`" in result.stdout, "packet-route should target Artifact Harness workflow")
        assert_true("/scripts/brain.sh artifact-harness" in result.stdout, "packet-route should show the executable artifact-harness command")
        assert_true(not (folder / "contexts" / "artifact_harness_registry.json").exists(), "packet-route without --create should not write packets")


def test_packet_route_natural_artifact_missions_are_create_ready() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-packet-route-natural-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        folder = ws / "artifact_case"
        folder.mkdir(parents=True, exist_ok=True)
        cases = [
            ("make a review-ready methods appendix", "methods appendix"),
            ("make this lecture slide task organized", "slide"),
            ("幫我整理這個投影片任務", "投影片"),
        ]
        for utterance, expected_deliverable in cases:
            result = run_brain(ws, "packet-route", utterance, "--path", str(folder), "--json")
            assert_true(result.returncode == 0, f"natural route expected 0 for {utterance!r}, got {result.returncode}, stderr={result.stderr}")
            payload = json.loads(result.stdout)
            assert_true(payload["matched"] is True, f"natural artifact route should match for {utterance!r}")
            assert_true(payload["recommended_route"] == "artifact_harness_workflow", "natural artifact route should recommend Artifact Harness")
            assert_true(payload["user_intent"] == "artifact_production", "natural artifact route should expose artifact-production intent")
            assert_true(payload["create_allowed"] is True, "natural artifact route should allow packet creation")
            assert_true(payload["needs_clarification"] is False, "create-ready natural route should not require clarification")
            assert_true(expected_deliverable in payload["natural_triggers"]["deliverables"], "natural route should expose deliverable trigger")
            command_parts = shlex.split(payload["recommended_command"])
            assert_true(Path(command_parts[0]).is_absolute() and command_parts[0].endswith("/scripts/brain.sh"), "natural route command should use absolute brain.sh path")
        assert_true(not (folder / "contexts" / "artifact_harness_registry.json").exists(), "natural route without --create should not write packets")


def test_packet_route_roster_aliases_route_to_artifact_harness() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-packet-route-roster-aliases-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        folder = ws / "artifact_case"
        folder.mkdir(parents=True, exist_ok=True)
        cases = [
            ("@roster 幫我把這個 slide 任務安排好", "roster", "@roster"),
            ("Roster, set up the team and task boundary for this artifact", "roster", "Roster"),
            ("PM, organize this artifact task", "project_manager_alias", "PM"),
        ]
        for utterance, expected_front_door, expected_keyword in cases:
            result = run_brain(ws, "packet-route", utterance, "--path", str(folder), "--json")
            assert_true(result.returncode == 0, f"roster alias route expected 0 for {utterance!r}, got {result.returncode}, stderr={result.stderr}")
            payload = json.loads(result.stdout)
            assert_true(payload["matched"] is True, f"roster alias route should match for {utterance!r}")
            assert_true(expected_front_door in payload["recognized_front_doors"], f"{expected_front_door} should be recorded as a front door")
            assert_true(payload["recommended_route"] == "artifact_harness_workflow", "Roster aliases should route to Artifact Harness workflow")
            assert_true(payload["chain_start"] == "Artifact Harness SPEC", "Roster aliases should keep artifact production SPEC-first")
            assert_true(payload["user_intent"] == "artifact_production", "Roster aliases should expose artifact-production intent")
            assert_true(payload["create_allowed"] is True, "concrete Roster alias routes should allow packet-chain creation")
            assert_true(payload["recommended_command"] is not None, "concrete Roster alias routes should expose a create command")
            assert_true(expected_keyword in payload["matched_keywords"], f"{expected_keyword} should be reported as a matched alias")
            assert_true(
                any(candidate.get("matched_id") == expected_front_door and candidate.get("route") == "artifact_harness_workflow" for candidate in payload["candidate_routes"]),
                "alias candidate should point at the Artifact Harness workflow",
            )
            assert_true(payload["boundaries"]["human_resources"] == "staffing and role design only", "Roster aliases must not transfer coordination ownership to HR")
            assert_true(payload["boundaries"]["capability_access_packet"].startswith("skill/plugin/tool authorization"), "Roster aliases must preserve CAP authorization boundary")
        assert_true(not (folder / "contexts" / "artifact_harness_registry.json").exists(), "route aliases without --create should not write packets")


def test_packet_route_roster_quality_direction_is_plain_self_check() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-packet-route-roster-quality-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        folder = ws / "quality_case"
        folder.mkdir(parents=True, exist_ok=True)
        cases = [
            ("Roster，幫我看 Lecture1 的 Quality 要怎麼設定", "Quality"),
            ("Roster，幫我檢查 Lecture1 的品質", "品質"),
            ("Roster，幫我做自我檢查", "自我檢查"),
        ]
        for utterance, expected_quality_term in cases:
            result = run_brain(ws, "packet-route", utterance, "--path", str(folder), "--json")
            assert_true(result.returncode == 0, f"Roster Quality route expected 0 for {utterance!r}, got {result.returncode}, stderr={result.stderr}")
            payload = json.loads(result.stdout)
            assert_true(payload["matched"] is True, "Roster Quality prompt should match the Roster front door")
            assert_true(payload["recommended_route"] == "roster_quality_direction", "Quality direction should not become a packet-creation route")
            assert_true(payload["user_intent"] == "quality_direction", "Quality prompt should expose quality_direction intent")
            assert_true(payload["create_allowed"] is False, "Quality direction should answer directly without creating packets")
            assert_true(payload["recommended_command"] is None, "Quality direction should not emit an Artifact Harness create command")
            assert_true(payload["quality_direction"]["detected"] is True, "Quality direction details should be structured")
            assert_true(expected_quality_term in payload["quality_direction"]["quality_terms"], "Quality term should be recorded")
            assert_true(payload["quality_direction"]["short_term_focus"], "Quality direction should include short-term self-check focus")
            assert_true(payload["quality_direction"]["long_term_focus"], "Quality direction should include long-term improvement focus")
        assert_true(not (folder / "contexts" / "artifact_harness_registry.json").exists(), "Quality direction route should not write packet output")


def test_packet_route_roster_quality_attached_artifact_is_spec_first() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-packet-route-roster-quality-artifact-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        folder = ws / "artifact_case"
        folder.mkdir(parents=True, exist_ok=True)
        utterance = "Roster, create a review-ready methods appendix with Quality settings"
        result = run_brain(ws, "packet-route", utterance, "--path", str(folder), "--json")
        assert_true(result.returncode == 0, f"Roster Quality artifact route expected 0, got {result.returncode}, stderr={result.stderr}")
        payload = json.loads(result.stdout)
        assert_true(payload["matched"] is True, "Roster Quality artifact prompt should match")
        assert_true(payload["recommended_route"] == "artifact_harness_workflow", "artifact production with Quality should remain SPEC-first")
        assert_true(payload["user_intent"] == "artifact_production", "artifact production with Quality should expose artifact-production intent")
        assert_true(payload["create_allowed"] is True, "artifact production with Quality should allow packet creation")
        assert_true(payload["chain_start"] == "Artifact Harness SPEC", "artifact production with Quality should start at SPEC")
        assert_true(payload["quality_direction"]["detected"] is True, "Quality direction should remain attached as advisory context")
        assert_true("Quality" in payload["quality_direction"]["quality_terms"], "Quality advisory context should record the Quality term")
        assert_true(payload["recommended_command"] is not None, "artifact production with Quality should emit a create command")
        assert_true(not (folder / "contexts" / "artifact_harness_registry.json").exists(), "route without --create should not write packet output")


def test_packet_route_roster_visual_quality_loop_attaches_to_production() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-packet-route-roster-visual-loop-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        folder = ws / "artifact_case"
        folder.mkdir(parents=True, exist_ok=True)
        utterance = "Roster, create a review-ready Lecture1 slide with CV quality check"
        result = run_brain(ws, "packet-route", utterance, "--path", str(folder), "--json")
        assert_true(result.returncode == 0, f"Roster visual quality loop route expected 0, got {result.returncode}, stderr={result.stderr}")
        payload = json.loads(result.stdout)
        assert_true(payload["recommended_route"] == "artifact_harness_workflow", "visual artifact production with Quality loop should remain SPEC-first")
        assert_true(payload["create_allowed"] is True, "visual artifact production should allow packet creation")
        assert_true(payload["quality_loop"]["detected"] is True, "visual artifact production should attach quality loop guidance")
        assert_true(payload["quality_loop"]["artifact_mode"] == "visual", "quality loop should identify visual artifact mode")
        assert_true(payload["quality_loop"]["recommended_iterations"] == "2-3", "quality loop should recommend 2-3 bounded iterations")
        assert_true(payload["quality_loop"]["cv_inspection"]["requested"] is True, "visual artifact production should request CV inspection")
        assert_true("screenshot_capture" in payload["quality_loop"]["cv_inspection"]["capability_requests"], "CV inspection should request screenshot capture")
        assert_true("vision_model_review" in payload["quality_loop"]["cv_inspection"]["capability_requests"], "CV inspection should request vision review")
        ladder = payload["quality_loop"]["cv_inspection"]["activation_ladder"]
        assert_true(len(ladder) >= 5, "CV inspection should expose an activation ladder")
        assert_true(ladder[0]["step"] == "use_existing_visual_evidence", "CV ladder should prefer existing visual evidence")
        assert_true(ladder[-1]["step"] == "ask_user_for_screenshot_or_frame", "CV ladder should ask the user for screenshots/frames only last")
        assert_true(ladder[-1]["fallback"] is True, "final CV ladder step should be marked as fallback")
        assert_true(payload["quality_loop"]["cv_inspection"]["evidence_required_for_visual_acceptance"] is True, "visual acceptance should require inspected evidence")


def test_packet_route_roster_visual_quality_only_uses_quality_direction() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-packet-route-roster-visual-quality-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        folder = ws / "quality_case"
        folder.mkdir(parents=True, exist_ok=True)
        utterance = "Roster，幫我用CV檢查 Lecture1 影片畫面品質"
        result = run_brain(ws, "packet-route", utterance, "--path", str(folder), "--json")
        assert_true(result.returncode == 0, f"Roster visual quality route expected 0, got {result.returncode}, stderr={result.stderr}")
        payload = json.loads(result.stdout)
        assert_true(payload["recommended_route"] == "roster_quality_direction", "visual quality-only prompt should route to Quality direction")
        assert_true(payload["create_allowed"] is False, "visual quality-only prompt should not create packets")
        assert_true(payload["quality_loop"]["detected"] is True, "visual quality-only prompt should include quality loop guidance")
        targets = payload["quality_loop"]["inspection_targets"]
        assert_true("text occlusion" in targets, "visual quality loop should inspect text occlusion")
        assert_true("contrast/readability" in targets, "visual quality loop should inspect readability")
        assert_true("layout overlap" in targets, "visual quality loop should inspect overlap")
        assert_true(payload["quality_loop"]["cv_inspection"]["requested"] is True, "visual quality-only prompt should request CV inspection")
        assert_true("vision_model_review" in payload["quality_loop"]["cv_inspection"]["capability_requests"], "quality-only CV request should include vision review capability")
        ladder = payload["quality_loop"]["cv_inspection"]["activation_ladder"]
        assert_true(ladder[-1]["step"] == "ask_user_for_screenshot_or_frame", "quality-only CV ladder should keep user screenshots as final fallback")
        assert_true(payload["quality_loop"]["cv_inspection"]["no_visual_evidence_policy"], "quality-only CV route should include a no-visual-evidence policy")


def test_packet_route_visual_cv_create_carries_request_into_packet_scaffolds() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-packet-route-roster-cv-create-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        folder = ws / "artifact_case"
        folder.mkdir(parents=True, exist_ok=True)
        utterance = "Roster, create a review-ready Lecture1 slide with CV quality check"
        result = run_brain(ws, "packet-route", utterance, "--path", str(folder), "--id", "smoke-cv-quality", "--create", "--json")
        assert_true(result.returncode == 0, f"CV visual packet creation expected 0, got {result.returncode}, stderr={result.stderr}")
        payload = json.loads(result.stdout)
        assert_true(payload["artifact_harness"]["created"] is True, "CV visual packet route should create the packet chain")
        packets = {key: Path(value) for key, value in payload["artifact_harness"]["packets"].items()}
        spec_text = packets["artifact_harness_spec"].read_text(encoding="utf-8")
        top_text = packets["team_operating_packet"].read_text(encoding="utf-8")
        cap_text = packets["capability_access_packet"].read_text(encoding="utf-8")
        runtime_text = packets["runtime_mapping"].read_text(encoding="utf-8")
        assert_true("Visual / CV Inspection Targets" in spec_text, "SPEC should carry CV inspection targets")
        assert_true("text occlusion" in spec_text and "slide/render/video mismatch" in spec_text, "SPEC should list visual inspection acceptance targets")
        assert_true("visual acceptance requires inspected visual evidence" in spec_text, "SPEC should require inspected visual evidence for visual acceptance")
        assert_true("only non-visual, text, or structure checks can be marked complete" in spec_text, "SPEC should limit completion when visual evidence is missing")
        assert_true("actionable visual finding shape" in spec_text, "SPEC should carry the visual finding output contract")
        assert_true("Visual Inspect-And-Correct Loop" in top_text, "TOP should include the bounded visual inspection loop")
        assert_true("quality reviewer / visual inspector" in top_text, "TOP should mention optional visual inspector role")
        assert_true("activation ladder task procedure" in top_text, "TOP should include the activation ladder as procedure")
        assert_true("inspect -> finding -> fix -> recheck loop" in top_text, "TOP should include an inspect/fix/recheck loop")
        assert_true("ask the user for a screenshot or frame only as the final fallback" in top_text, "TOP should make user screenshots the final fallback")
        assert_true("structured finding shape" in top_text, "TOP should include the actionable finding shape")
        assert_true("CV Inspection Capability Request" in cap_text, "CAP should include a CV inspection capability request")
        assert_true("render_export_visual_evidence" in cap_text and "screenshot_capture" in cap_text and "vision_model_review" in cap_text, "CAP should request render/export, screenshot, and vision review capabilities")
        assert_true("user evidence fallback" in cap_text, "CAP should keep user-provided evidence as fallback")
        assert_true("CAP authorizes tools and gates only" in cap_text, "CAP should preserve authorization-only boundary")
        assert_true("CV Inspection Runtime Trace" in runtime_text, "runtime mapping should carry a CAP-derived CV trace")
        assert_true("expose visual inspection steps to runtime only if CAP explicitly authorizes" in runtime_text, "runtime mapping should not own CV authorization")
        assert_true("runtime boundary" in runtime_text and "does not own authorization" in runtime_text, "runtime mapping should preserve execution-layer boundary")


def test_packet_route_pm_alias_requires_artifact_context() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-packet-route-pm-ambiguous-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        folder = ws / "ordinary_case"
        folder.mkdir(parents=True, exist_ok=True)
        for utterance in ("what time is the meeting at 5 PM tomorrow", "PM, can you join the meeting at 5 PM?"):
            result = run_brain(ws, "packet-route", utterance, "--path", str(folder), "--json")
            assert_true(result.returncode == 0, f"ambiguous PM route expected 0 for {utterance!r}, got {result.returncode}, stderr={result.stderr}")
            payload = json.loads(result.stdout)
            assert_true(payload["matched"] is False, f"ambiguous PM text should not match for {utterance!r}")
            assert_true(payload["recommended_route"] == "none", "ambiguous PM text should remain an ordinary miss")
            assert_true(payload["refused"] is False, "JSON miss should remain parseable and non-refusal")
        assert_true(not (folder / "contexts" / "artifact_harness_registry.json").exists(), "ambiguous PM miss should not write packets")


def test_packet_route_underspecified_artifact_hint_refuses_create() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-packet-route-clarify-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        folder = ws / "artifact_case"
        folder.mkdir(parents=True, exist_ok=True)
        result = run_brain(ws, "packet-route", "can you help with this artifact?", "--path", str(folder), "--create", "--json")
        assert_true(result.returncode != 0, "underspecified artifact --create should refuse")
        payload = json.loads(result.stdout)
        assert_true(payload["matched"] is True, "underspecified artifact hint should still be recognized")
        assert_true(payload["recommended_route"] == "artifact_harness_workflow", "underspecified artifact hint should point to Artifact Harness")
        assert_true(payload["user_intent"] == "artifact_hint", "underspecified artifact hint should expose artifact_hint intent")
        assert_true(payload["needs_clarification"] is True, "underspecified artifact hint should require clarification")
        assert_true(payload["create_allowed"] is False, "underspecified artifact hint should not allow create")
        assert_true(payload["reason"] == "needs_clarification", "underspecified artifact create refusal should identify clarification need")
        assert_true(payload["clarifying_questions"], "underspecified artifact route should return clarifying questions")
        assert_true(not (folder / "contexts" / "artifact_harness_registry.json").exists(), "underspecified create refusal should not write packet output")


def test_packet_route_front_door_hr_artifact_is_spec_first() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-packet-route-hr-artifact-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        folder = ws / "artifact_case"
        folder.mkdir(parents=True, exist_ok=True)
        result = run_brain(ws, "packet-route", "HR, help me design roles for this artifact", "--path", str(folder), "--json")
        assert_true(result.returncode == 0, f"HR artifact route expected 0, got {result.returncode}, stderr={result.stderr}")
        payload = json.loads(result.stdout)
        assert_true(payload["matched"] is True, "HR artifact route should match")
        assert_true("human_resources" in payload["recognized_front_doors"], "HR should be recorded as the recognized front door")
        assert_true(payload["recommended_route"] == "artifact_harness_workflow", "artifact production should start with Artifact Harness workflow")
        assert_true(payload["chain_start"] == "Artifact Harness SPEC", "artifact production should remain SPEC-first")
        assert_true(payload["handoff_target"] == "HR staffing", "HR front door should be recorded as downstream handoff")
        assert_true(payload["create_allowed"] is True, "artifact mission should allow packet-chain creation")
        assert_true(payload["boundaries"]["human_resources"] == "staffing and role design only", "route JSON should preserve HR boundary")
        assert_true(not (folder / "contexts" / "artifact_harness_registry.json").exists(), "route without --create should not write packets")


def test_packet_route_front_door_hr_only_does_not_create_packets() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-packet-route-hr-only-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        folder = ws / "staffing_case"
        folder.mkdir(parents=True, exist_ok=True)
        result = run_brain(ws, "packet-route", "HR, do we have the right roles?", "--path", str(folder), "--json")
        assert_true(result.returncode == 0, f"HR-only route expected 0, got {result.returncode}, stderr={result.stderr}")
        payload = json.loads(result.stdout)
        assert_true(payload["recommended_route"] == "human_resources", "HR-only request should route to HR team surface")
        assert_true(payload["user_intent"] == "hr_staffing", "HR-only request should expose HR staffing intent")
        assert_true(payload["create_allowed"] is False, "HR-only request should not allow packet creation")
        assert_true(payload["recommended_command"] is None, "HR-only route should not emit an Artifact Harness create command")
        assert_true(not (folder / "contexts" / "artifact_harness_registry.json").exists(), "HR-only route should not write packets")

        ask = run_brain(ws, "packet-route", "ask HR to check staffing", "--path", str(folder), "--json")
        assert_true(ask.returncode == 0, f"ask HR route expected 0, got {ask.returncode}, stderr={ask.stderr}")
        ask_payload = json.loads(ask.stdout)
        assert_true("human_resources" in ask_payload["recognized_front_doors"], "standalone HR phrase should match the HR front door")
        assert_true(ask_payload["recommended_route"] == "human_resources", "staffing-only HR phrase should stay HR-only")
        assert_true(ask_payload["create_allowed"] is False, "staffing-only HR phrase should not allow packet creation")

        create = run_brain(ws, "packet-route", "HR, do we have the right roles?", "--path", str(folder), "--create", "--json")
        assert_true(create.returncode != 0, "HR-only --create should refuse rather than create a misleading packet chain")
        create_payload = json.loads(create.stdout)
        assert_true(create_payload["refused"] is True, "HR-only --create should emit refusal JSON")
        assert_true(not (folder / "contexts" / "artifact_harness_registry.json").exists(), "HR-only --create refusal should not write packets")


def test_packet_route_requirement_form_create_writes_packet_chain() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-packet-route-requirement-create-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        folder = ws / "artifact_case"
        folder.mkdir(parents=True, exist_ok=True)
        result = run_brain(ws, "packet-route", "fill requirement form for methods appendix", "--path", str(folder), "--create", "--json")
        assert_true(result.returncode == 0, f"requirement form --create expected 0, got {result.returncode}, stderr={result.stderr}")
        payload = json.loads(result.stdout)
        assert_true(payload["recommended_route"] == "artifact_harness_workflow", "requirement form should route to Artifact Harness workflow")
        assert_true(payload["create_allowed"] is True, "requirement form should allow create")
        assert_true(payload["artifact_harness"]["created"] is True, "packet-route --create should create Artifact Harness packet chain")
        registry = load_artifact_harness_registry(folder)
        assert_true("artifact_harness_spec" in registry["entries"][0]["packets"], "created chain should include SPEC packet")


def test_packet_route_roster_create_from_temp_cwd_writes_target_workspace() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-packet-route-roster-create-") as tmp_s:
        tmp = Path(tmp_s)
        cwd = tmp / "cwd"
        target = tmp / "target_workspace"
        cwd.mkdir(parents=True, exist_ok=True)
        target.mkdir(parents=True, exist_ok=True)
        brain = ROOT / "scripts" / "brain.sh"
        result = subprocess.run(
            [
                str(brain),
                "packet-route",
                "@roster 幫我把這個 slide 任務安排好",
                "--path",
                str(target),
                "--create",
                "--json",
            ],
            cwd=cwd,
            text=True,
            capture_output=True,
            check=False,
        )
        assert_true(result.returncode == 0, f"@roster packet-route --create expected 0, got {result.returncode}, stderr={result.stderr}")
        payload = json.loads(result.stdout)
        assert_true(payload["matched"] is True, "@roster create route should match")
        assert_true(payload["recommended_route"] == "artifact_harness_workflow", "@roster create should target Artifact Harness")
        assert_true(payload["artifact_harness"]["created"] is True, "@roster create should write an Artifact Harness chain")
        assert_true(Path(payload["artifact_harness"]["registry_path"]).resolve() == (target / "contexts" / "artifact_harness_registry.json").resolve(), "registry should live under the target workspace")
        assert_true((target / "contexts" / "artifact_harness_registry.json").exists(), "target workspace should receive packet registry")
        assert_true(not (cwd / "contexts" / "artifact_harness_registry.json").exists(), "calling cwd should not receive packet registry")


def test_packet_route_downstream_front_doors_are_spec_first_without_id() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-packet-route-downstream-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        folder = ws / "artifact_case"
        folder.mkdir(parents=True, exist_ok=True)

        team = run_brain(ws, "packet-route", "Team Architect for this artifact production task", "--path", str(folder), "--json")
        assert_true(team.returncode == 0, f"Team Architect route expected 0, got {team.returncode}, stderr={team.stderr}")
        team_payload = json.loads(team.stdout)
        assert_true(team_payload["recognized_front_doors"] == ["team_architect_packet"], "Team Architect should be distinguished as a front door")
        assert_true(team_payload["recommended_route"] == "artifact_harness_workflow", "Team Architect artifact request should start SPEC-first")
        assert_true(team_payload["handoff_target"] == "Team Operating Packet", "Team Architect handoff should be recorded")

        cap = run_brain(ws, "packet-route", "create CAP for this artifact task", "--path", str(folder), "--json")
        assert_true(cap.returncode == 0, f"CAP route expected 0, got {cap.returncode}, stderr={cap.stderr}")
        cap_payload = json.loads(cap.stdout)
        assert_true(cap_payload["recognized_front_doors"] == ["capability_access_packet"], "CAP should be distinguished as a front door")
        assert_true(cap_payload["recommended_route"] == "artifact_harness_workflow", "CAP artifact request should start SPEC-first")
        assert_true(cap_payload["handoff_target"] == "Capability Access Packet", "CAP handoff should be recorded")
        assert_true(cap_payload["boundaries"]["capability_access_packet"].endswith("runtime allowlist only"), "CAP route should remain capability authorization only")

        runtime = run_brain(ws, "packet-route", "runtime mapping for this packet", "--path", str(folder), "--json")
        assert_true(runtime.returncode == 0, f"runtime mapping route expected 0, got {runtime.returncode}, stderr={runtime.stderr}")
        runtime_payload = json.loads(runtime.stdout)
        assert_true(runtime_payload["recognized_front_doors"] == ["runtime_mapping"], "runtime mapping should be distinguished as a front door")
        assert_true(runtime_payload["recommended_route"] == "artifact_harness_workflow", "downstream-only runtime request should point back to SPEC-first chain")
        assert_true(runtime_payload["user_intent"] == "downstream_packet_reference", "downstream-only runtime request should expose downstream packet intent")
        assert_true(runtime_payload["create_allowed"] is False, "downstream-only runtime request without artifact mission or id should not create")
        assert_true(runtime_payload["boundaries"]["runtime_mapping"].startswith("execution mapping only"), "runtime route should not imply execution")


def test_packet_route_short_alias_does_not_match_inside_words() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-packet-route-boundary-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        folder = ws / "artifact_case"
        folder.mkdir(parents=True, exist_ok=True)

        runtime = run_brain(ws, "packet-route", "walk me through runtime mapping", "--path", str(folder), "--json")
        assert_true(runtime.returncode == 0, f"runtime boundary route expected 0, got {runtime.returncode}, stderr={runtime.stderr}")
        runtime_payload = json.loads(runtime.stdout)
        assert_true(runtime_payload["recognized_front_doors"] == ["runtime_mapping"], "HR must not match inside the word 'through'")
        assert_true("human_resources" not in runtime_payload["recognized_front_doors"], "short HR alias should require a standalone boundary")
        assert_true(runtime_payload["recommended_route"] == "artifact_harness_workflow", "downstream runtime request should still point back to the SPEC-first chain")
        assert_true(runtime_payload["create_allowed"] is False, "downstream-only runtime request should not allow packet creation")
        assert_true(not (folder / "contexts" / "artifact_harness_registry.json").exists(), "boundary route without --create should not write packets")

        requirement = run_brain(ws, "packet-route", "walk through the requirement form", "--path", str(folder), "--json")
        assert_true(requirement.returncode == 0, f"requirement boundary route expected 0, got {requirement.returncode}, stderr={requirement.stderr}")
        requirement_payload = json.loads(requirement.stdout)
        assert_true("human_resources" not in requirement_payload["recognized_front_doors"], "HR must not match inside 'through' for requirement-form utterances")
        assert_true(requirement_payload["recommended_route"] == "artifact_harness_workflow", "requirement-form keyword should route to Artifact Harness workflow")
        assert_true(requirement_payload["create_allowed"] is True, "requirement-form keyword should allow packet creation")
        assert_true("requirement form" in [keyword.lower() for keyword in requirement_payload["matched_keywords"]], "requirement-form keyword should be reported")
        assert_true(not (folder / "contexts" / "artifact_harness_registry.json").exists(), "requirement route without --create should not write packets")


def test_packet_route_existing_id_routes_to_safe_existing_packet_command() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-packet-route-existing-id-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        folder = ws / "artifact_case"
        folder.mkdir(parents=True, exist_ok=True)
        create = run_brain(ws, "artifact-harness", "Draft an existing packet route target", "--path", str(folder), "--id", "existing-route-run", "--json")
        assert_true(create.returncode == 0, f"artifact-harness create should succeed, got {create.returncode}, stderr={create.stderr}")

        cap = run_brain(ws, "packet-route", "create CAP for this artifact task", "--path", str(folder), "--id", "existing-route-run", "--json")
        assert_true(cap.returncode == 0, f"CAP existing-id route expected 0, got {cap.returncode}, stderr={cap.stderr}")
        cap_payload = json.loads(cap.stdout)
        assert_true(cap_payload["recommended_route"] == "capability_access_packet", "CAP request with existing id should route to existing CAP inspection")
        assert_true(cap_payload["command_action"] == "resume", "CAP existing-id route should recommend a safe resume command")
        assert_true("artifact-harness resume" in cap_payload["recommended_command"], "CAP existing-id command should use artifact-harness resume")

        runtime = run_brain(ws, "packet-route", "runtime mapping for packet existing-route-run", "--path", str(folder), "--id", "existing-route-run", "--json")
        assert_true(runtime.returncode == 0, f"runtime existing-id route expected 0, got {runtime.returncode}, stderr={runtime.stderr}")
        runtime_payload = json.loads(runtime.stdout)
        assert_true(runtime_payload["recommended_route"] == "runtime_mapping", "runtime request with existing id should route to existing runtime inspection")
        assert_true(runtime_payload["command_action"] == "runtime-check", "runtime existing-id route should recommend runtime-check")
        assert_true("artifact-harness runtime-check" in runtime_payload["recommended_command"], "runtime existing-id command should use artifact-harness runtime-check")


def test_packet_route_json_from_temp_cwd_uses_absolute_next_command() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-packet-route-json-") as tmp_s:
        tmp = Path(tmp_s)
        cwd = tmp / "cwd"
        target = tmp / "target_workspace"
        cwd.mkdir(parents=True, exist_ok=True)
        target.mkdir(parents=True, exist_ok=True)
        brain = ROOT / "scripts" / "brain.sh"
        result = subprocess.run(
            [str(brain), "packet-route", "please Artifact Harness this methods appendix", "--path", str(target), "--json"],
            cwd=cwd,
            text=True,
            capture_output=True,
            check=False,
        )
        assert_true(result.returncode == 0, f"absolute packet-route --json expected 0, got {result.returncode}, stderr={result.stderr}")
        payload = json.loads(result.stdout)
        assert_true(payload["matched"] is True, "packet-route JSON should expose matched=true")
        assert_true(payload["route"] == "artifact_harness_workflow", "packet-route JSON should expose the target route")
        assert_true(payload["matched_keywords"], "packet-route JSON should expose matched keywords")
        assert_true(payload["create"] is False and payload["force"] is False, "packet-route JSON should expose create/force flags")
        command_parts = shlex.split(payload["command"])
        assert_true(command_parts[0] == str(brain), "packet-route next command should use an absolute brain.sh path")
        next_result = subprocess.run(command_parts, cwd=cwd, text=True, capture_output=True, check=False)
        assert_true(next_result.returncode == 0, f"packet-route next command should be executable, got {next_result.returncode}, stderr={next_result.stderr}")
        assert_true((target / "contexts" / "artifact_harness_registry.json").exists(), "next command should write packets into the target workspace")


def test_packet_route_create_json_refuses_packet_root_outside_target_workspace() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-packet-route-json-refusal-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        folder = ws / "artifact_case"
        folder.mkdir(parents=True, exist_ok=True)
        outside_packet_root = ws / "outside_packet_root"
        set_artifact_harness_packet_root(ws, outside_packet_root)
        result = run_brain(
            ws,
            "packet-route",
            "please packet form this methods appendix",
            "--path",
            str(folder),
            "--create",
            "--json",
        )
        assert_true(result.returncode != 0, "packet-route --create --json should fail when packet root is outside target workspace")
        payload = json.loads(result.stdout)
        assert_true(payload["matched"] is True and payload["create"] is True, "route JSON should still expose route state")
        artifact_payload = payload.get("artifact_harness", {})
        assert_true(artifact_payload.get("created") is False and artifact_payload.get("refused") is True, "route JSON should include nested artifact refusal")
        assert_true(artifact_payload.get("reason") == "packet_root_outside_target_workspace", "nested refusal should identify packet root boundary failure")
        assert_true(Path(artifact_payload["packet_root"]).resolve() == outside_packet_root.resolve(), "nested refusal should include attempted packet root")
        assert_true(Path(artifact_payload["run_dir"]).resolve().parent == outside_packet_root.resolve(), "nested refusal should include attempted run directory")
        assert_true("outside target workspace" in result.stderr, "packet-route refusal should retain human stderr diagnostics")
        assert_true(not outside_packet_root.exists(), "packet-route refusal should not create packet root outside target workspace")


def test_packet_route_create_writes_artifact_harness_chain() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-packet-route-create-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        folder = ws / "artifact_case"
        folder.mkdir(parents=True, exist_ok=True)
        result = run_brain(ws, "packet-route", "please packet form this methods appendix", "--path", str(folder), "--create")
        assert_true(result.returncode == 0, f"packet-route create expected 0, got {result.returncode}, stderr={result.stderr}")
        assert_true("Matched: `true`" in result.stdout, "packet-route create should report a match")
        assert_true("# Artifact Harness Packet Chain" in result.stdout, "packet-route --create should write the packet chain")
        assert_true((folder / "contexts" / "artifact_harness_registry.json").exists(), "packet-route --create should write artifact harness registry")
        registry = load_artifact_harness_registry(folder)
        assert_true("hr_staffing_packet" in registry["entries"][0]["packets"], "registry should include hr_staffing_packet after packet-route create")


def test_packet_route_create_refuses_rerun_without_force() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-packet-route-rerun-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        folder = ws / "artifact_case"
        folder.mkdir(parents=True, exist_ok=True)
        utterance = "please packet form this methods appendix"
        first = run_brain(ws, "packet-route", utterance, "--path", str(folder), "--create")
        assert_true(first.returncode == 0, f"first packet-route --create should succeed, got {first.returncode}, stderr={first.stderr}")
        registry_path = folder / "contexts" / "artifact_harness_registry.json"
        registry_before = registry_path.read_text(encoding="utf-8")
        entry = load_artifact_harness_registry(folder)["entries"][0]
        spec_path = folder / entry["packets"]["artifact_harness_spec"]
        spec_path.write_text(spec_path.read_text(encoding="utf-8") + "\nSENTINEL_DO_NOT_OVERWRITE\n", encoding="utf-8")

        second = run_brain(ws, "packet-route", utterance, "--path", str(folder), "--create")
        assert_true(second.returncode != 0, "packet-route --create rerun without force should fail")
        assert_true("Artifact Harness packet run already exists" in second.stderr, "packet-route rerun should surface artifact-harness overwrite guard")
        assert_true("SENTINEL_DO_NOT_OVERWRITE" in spec_path.read_text(encoding="utf-8"), "packet-route rerun without force should preserve filled packet content")
        assert_true(registry_path.read_text(encoding="utf-8") == registry_before, "packet-route rerun without force should not update registry")

        forced = run_brain(ws, "packet-route", utterance, "--path", str(folder), "--create", "--force")
        assert_true(forced.returncode == 0, f"packet-route --create --force should overwrite, got {forced.returncode}, stderr={forced.stderr}")
        assert_true("SENTINEL_DO_NOT_OVERWRITE" not in spec_path.read_text(encoding="utf-8"), "packet-route --force should allow packet overwrite")


def test_packet_route_non_artifact_phrase_does_not_route() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-packet-route-miss-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        folder = ws / "ordinary_case"
        folder.mkdir(parents=True, exist_ok=True)
        result = run_brain(ws, "packet-route", "what time is the meeting tomorrow", "--path", str(folder))
        assert_true(result.returncode == 0, f"packet-route miss expected 0, got {result.returncode}, stderr={result.stderr}")
        assert_true("Matched: `false`" in result.stdout, "packet-route should not match non-artifact phrases")
        assert_true("Route: `none`" in result.stdout, "packet-route miss should not name an artifact route")
        assert_true(not (folder / "contexts" / "artifact_harness_registry.json").exists(), "packet-route miss should not write artifact harness registry")


def test_roster_health_smoke_json_reports_missing_provider_and_target_packet_output() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-roster-health-smoke-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        cwd = Path(tmp_s) / "cwd"
        target = Path(tmp_s) / "target_workspace"
        cwd.mkdir(parents=True, exist_ok=True)
        target.mkdir(parents=True, exist_ok=True)
        brain = ROOT / "scripts" / "brain.sh"
        result = subprocess.run(
            [
                str(brain),
                "roster-health",
                "--path",
                str(target),
                "--id",
                "roster-health-smoke",
                "--json",
            ],
            cwd=cwd,
            text=True,
            capture_output=True,
            check=False,
            env={
                **os.environ,
                "SYSTEM_HUB_CONFIG": str(ws / "policy" / "system_hub.toml"),
                "ROSTER_LLM_PROVIDER": "",
                "OPENAI_API_KEY": "",
            },
        )
        assert_true(result.returncode == 2, f"roster-health should return degraded with structured missing-provider diagnostics, got {result.returncode}, stderr={result.stderr}")
        payload = json.loads(result.stdout)
        assert_true(payload["report_type"] == "roster_install_register_health", "health JSON should identify report type")
        assert_true(payload["overall_status"] == "degraded", "missing provider should degrade rather than hide diagnostics")
        assert_true(payload["verified_invocation_mechanism"]["status"] == "visible", "Roster alias should be visible through packet-route")
        assert_true(payload["verified_invocation_mechanism"]["name"] == "scripts/brain.sh packet-route", "health should name the verified invocation mechanism")
        assert_true(payload["verified_invocation_mechanism"]["current_codex_surface"]["mention_at_roster"] == "product_target_unverified_as_installed_codex_mention", "health must not claim installed @roster mention support")
        assert_true(payload["packet_output"]["status"] == "success", "health should write a packet through the verified route")
        assert_true(Path(payload["packet_output"]["run_dir"]).resolve() == (target / "contexts" / "artifact_harness_runs" / "roster-health-smoke").resolve(), "health packet run should live under target workspace")
        assert_true(Path(payload["packet_output"]["registry_path"]).resolve() == (target / "contexts" / "artifact_harness_registry.json").resolve(), "health registry should live under target workspace")
        assert_true(payload["packet_output"]["under_target_workspace"] is True, "health JSON should verify packet paths are under the target workspace")
        assert_true(payload["llm_provider"]["status"] == "missing_provider", "provider absence should be structured")
        assert_true("cv_inspection_capability" in payload, "health JSON should include CV inspection capability diagnostics")
        assert_true(payload["cv_inspection_capability"]["status"] == "not_configured", "absent CV provider should be reported without becoming a packet-output failure")
        assert_true("screenshot" in payload["cv_inspection_capability"]["supported_local_input_modes"], "CV health should list screenshot input support")
        assert_true("OCR/readability review" in payload["cv_inspection_capability"]["supported_local_input_modes"], "CV health should list OCR/readability support")
        assert_true(payload["cv_inspection_capability"]["remote_call_attempted"] is False, "CV health should not make remote calls")
        assert_true(payload["cv_inspection_capability"]["visual_evidence_acquisition"]["status"] == "available_as_capability_plan", "CV health should report evidence acquisition availability")
        assert_true(payload["cv_inspection_capability"]["user_evidence_fallback"]["status"] == "last_fallback", "CV health should report user screenshots/frames as final fallback")
        assert_true(payload["cv_inspection_capability"]["no_visual_evidence_policy"], "CV health should include the no-visual-evidence policy")
        assert_true(payload["cv_inspection_capability"]["default_health_blocked"] is False, "default health should not be blocked by missing CV provider auth")
        assert_true(payload["runtime_dependency_check"]["persistent_server_required"] is False, "health should not require a persistent server")
        assert_true(payload["runtime_dependency_check"]["daemon_required"] is False, "health should not require a daemon")
        assert_true(payload["runtime_dependency_check"]["database_required"] is False, "health should not require a database")
        assert_true(payload["runtime_dependency_check"]["external_control_plane_required"] is False, "health should not require a hidden control plane")
        assert_true(payload["packet_output"]["cleanup"]["status"] == "success", "default health check should clean up packet output after verification")
        assert_true(payload["packet_output"]["cleanup"]["run_dir_removed"] is True, "default health check should remove the smoke run directory")
        assert_true(payload["packet_output"]["cleanup"]["registry_removed"] is True, "default health check should remove a health-created registry")
        assert_true(not (target / "contexts" / "artifact_harness_registry.json").exists(), "default health check should not leave a target registry")
        assert_true(not (target / "contexts" / "artifact_harness_runs").exists(), "default health check should not leave target packet runs")
        assert_true(not (cwd / "contexts" / "artifact_harness_registry.json").exists(), "calling cwd should not receive health packet output")


def test_roster_health_provider_missing_auth_and_configured_auth_are_structured_without_secret_leak() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-roster-health-provider-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        folder = ws / "artifact_case"
        folder.mkdir(parents=True, exist_ok=True)
        missing_auth = run_brain(
            ws,
            "roster-health",
            "--path",
            str(folder),
            "--id",
            "roster-health-provider-missing-auth",
            "--provider",
            "openai",
            "--json",
            extra_env={"OPENAI_API_KEY": "", "ROSTER_LLM_PROVIDER": ""},
        )
        assert_true(missing_auth.returncode == 2, f"roster-health missing-auth diagnostics should be parseable as degraded, got {missing_auth.returncode}, stderr={missing_auth.stderr}")
        missing_payload = json.loads(missing_auth.stdout)
        assert_true(missing_payload["overall_status"] == "degraded", "missing auth should degrade health")
        assert_true(missing_payload["llm_provider"]["status"] == "missing_auth", "missing provider env should be structured as missing_auth")
        assert_true(missing_payload["llm_provider"]["auth_env_var"] == "OPENAI_API_KEY", "openai default auth env should be named exactly")
        assert_true(missing_payload["llm_provider"]["secret_material"] == "not_read_or_reported", "missing-auth diagnostics should not read or report secrets")
        assert_true(missing_payload["packet_output"]["cleanup"]["status"] == "success", "missing-auth health check should still clean smoke output")

        configured = run_brain(
            ws,
            "roster-health",
            "--path",
            str(folder),
            "--id",
            "roster-health-provider-configured",
            "--provider",
            "openai",
            "--json",
            extra_env={"OPENAI_API_KEY": "placeholder-roster-health-token", "ROSTER_LLM_PROVIDER": ""},
        )
        assert_true(configured.returncode == 0, f"roster-health configured provider should pass local env check, got {configured.returncode}, stderr={configured.stderr}")
        configured_payload = json.loads(configured.stdout)
        assert_true(configured_payload["overall_status"] == "healthy", "auth env presence should make the local provider path healthy")
        assert_true(configured_payload["llm_provider"]["status"] == "configured", "provider env presence should be reported as configured")
        assert_true(configured_payload["llm_provider"]["auth_env_present"] is True, "health should expose env presence as boolean")
        assert_true(configured_payload["llm_provider"]["remote_call_attempted"] is False, "health should not pretend to make a remote model call")
        assert_true(configured_payload["cv_inspection_capability"]["status"] == "not_configured", "CV auth absence should not degrade configured LLM health when not explicitly requested")
        assert_true(configured_payload["cv_inspection_capability"]["explicit_check_requested"] is False, "CV check should be optional without --cv-provider or --cv-auth-env")
        assert_true("placeholder-roster-health-token" not in configured.stdout, "health output must not print provider secrets")
        assert_true(not (folder / "contexts" / "artifact_harness_registry.json").exists(), "roster-health should clean smoke registry after provider checks")

        cv_missing = run_brain(
            ws,
            "roster-health",
            "--path",
            str(folder),
            "--id",
            "roster-health-cv-missing-auth",
            "--provider",
            "local-test",
            "--auth-env",
            "ROSTER_TEST_API_KEY",
            "--cv-provider",
            "openai",
            "--json",
            extra_env={"ROSTER_TEST_API_KEY": "placeholder-roster-test-token", "OPENAI_API_KEY": "", "ROSTER_LLM_PROVIDER": ""},
        )
        assert_true(cv_missing.returncode == 2, f"explicit CV provider check should degrade when auth is missing, got {cv_missing.returncode}, stderr={cv_missing.stderr}")
        cv_missing_payload = json.loads(cv_missing.stdout)
        assert_true(cv_missing_payload["overall_status"] == "degraded", "missing explicit CV auth should degrade health")
        assert_true(cv_missing_payload["cv_inspection_capability"]["status"] == "missing_auth", "explicit CV provider check should report missing auth")
        assert_true(cv_missing_payload["cv_inspection_capability"]["auth_env_var"] == "OPENAI_API_KEY", "CV provider default auth env should be named")
        assert_true(cv_missing_payload["cv_inspection_capability"]["remote_call_attempted"] is False, "CV missing-auth check should stay local-only")
        assert_true("placeholder-roster-test-token" not in cv_missing.stdout, "CV health output must not print provider secrets")


def test_roster_health_missing_target_json_refusal_is_parseable() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-roster-health-missing-target-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        missing_target = ws / "missing_target"
        result = run_brain(ws, "roster-health", "--path", str(missing_target), "--json")
        assert_true(result.returncode != 0, "roster-health should fail for a missing target")
        payload = json.loads(result.stdout)
        assert_true(payload["refused"] is True, "missing target should emit refusal JSON")
        assert_true(payload["reason"] == "missing_target", "missing target refusal should identify missing_target")
        assert_true(payload["overall_status"] == "failed", "missing target should fail health")


def test_roster_install_temp_codex_home_and_health_detects_skill() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-roster-install-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        codex_home = Path(tmp_s) / "fresh_codex_home"
        target = Path(tmp_s) / "target_workspace"
        target.mkdir(parents=True, exist_ok=True)

        install = run_brain(ws, "roster-install", "--codex-home", str(codex_home), "--json")
        assert_true(install.returncode == 0, f"roster-install should succeed in temp Codex home, got {install.returncode}, stderr={install.stderr}")
        install_payload = json.loads(install.stdout)
        skill_path = codex_home / "skills" / "roster"
        manifest_path = skill_path / "references" / "install_manifest.json"
        assert_true(install_payload["installed"] is True, "install JSON should report installed=true")
        assert_true(Path(install_payload["skill_path"]).resolve() == skill_path.resolve(), "install JSON should point to temp Codex home skill")
        assert_true((skill_path / "SKILL.md").exists(), "roster-install should copy SKILL.md")
        assert_true(manifest_path.exists(), "roster-install should write install manifest")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        assert_true(manifest["skill_name"] == "roster", "install manifest should identify roster skill")
        assert_true(manifest["current_user_invocation"] == "Roster, <task>", "install manifest should name truthful current invocation")
        assert_true(manifest["at_roster_status"] == "product_target_unverified_as_installed_codex_mention", "install manifest must not claim @roster")

        duplicate = run_brain(ws, "roster-install", "--codex-home", str(codex_home), "--json")
        duplicate_payload = json.loads(duplicate.stdout)
        assert_true(duplicate.returncode != 0, "roster-install should refuse existing skill without --force")
        assert_true(duplicate_payload["reason"] == "existing_roster_skill", "duplicate install should identify existing skill")

        health = run_brain(
            ws,
            "roster-health",
            "--codex-home",
            str(codex_home),
            "--path",
            str(target),
            "--id",
            "roster-install-health-smoke",
            "--provider",
            "local-test",
            "--auth-env",
            "ROSTER_TEST_API_KEY",
            "--json",
            extra_env={"ROSTER_TEST_API_KEY": "placeholder-roster-test-token", "ROSTER_LLM_PROVIDER": ""},
        )
        assert_true(health.returncode == 0, f"roster-health should pass with installed skill and local provider env, got {health.returncode}, stderr={health.stderr}")
        health_payload = json.loads(health.stdout)
        assert_true(health_payload["overall_status"] == "healthy", "installed-skill health should be healthy with local provider env")
        assert_true(health_payload["installed_skill"]["status"] == "installed", "health should detect installed roster skill")
        assert_true(health_payload["verified_invocation_mechanism"]["current_codex_surface"]["skill"] == "installed", "health surface should report skill installed")
        assert_true(health_payload["packet_output"]["cleanup"]["status"] == "success", "health should clean smoke packet output")
        assert_true("placeholder-roster-test-token" not in health.stdout, "health output must not print provider secrets")
        assert_true(not (target / "contexts" / "artifact_harness_registry.json").exists(), "health should clean target registry")
        assert_true(not (target / "contexts" / "artifact_harness_runs").exists(), "health should clean target packet runs")


def test_skill_route_gap_triggers_discovery() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-skill-route-gap-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        fake_bin = Path(tmp_s) / "fake-bin"
        fake_bin.mkdir(parents=True, exist_ok=True)
        write_file(
            fake_bin / "npx",
            "#!/usr/bin/env bash\n"
            "if [[ \"$1\" == \"--yes\" && \"$2\" == \"skills\" && \"$3\" == \"find\" ]]; then\n"
            "  echo 'demo-owner/demo-pack@astro-telemetry-skill 12 installs'\n"
            "  echo '└ https://skills.sh/demo-owner/demo-pack/astro-telemetry-skill'\n"
            "  exit 0\n"
            "fi\n"
            "exit 1\n",
            executable=True,
        )
        folder = ws / "misc_case"
        folder.mkdir(parents=True, exist_ok=True)
        write_file(folder / "notes.txt", "misc\n")
        result = run_brain(
            ws,
            "skill-route",
            "operate the proprietary astro telemetry cubing workflow",
            "--path",
            str(folder),
            extra_env={"PATH": f"{fake_bin}:{os.environ['PATH']}"},
        )
        assert_true(result.returncode == 2, f"skill-route gap should degrade to 2, got {result.returncode}, stderr={result.stderr}")
        assert_true("Gap detected: `true`" in result.stdout, "skill-route should surface workflow gaps")
        assert_true("`demo-owner/demo-pack@astro-telemetry-skill`" in result.stdout, "skill-route should surface install candidates from discovery")
        discovery = load_skill_discovery_registry(ws)
        assert_true(discovery["last_query"] == "operate the proprietary astro telemetry cubing workflow", "gap routing should persist discovery query")


def test_skill_route_uses_closeout_quality_signals() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-skill-route-quality-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        extra_root = Path(tmp_s) / "external" / "codex_home" / "skills"
        make_skill(extra_root, "custom-unmapped-skill")
        folder = ws / "analysis_runtime"
        folder.mkdir(parents=True, exist_ok=True)
        write_file(folder / "dataset.csv", "x,y\n1,2\n")
        write_file(folder / "results.xlsx", "placeholder\n")
        write_file(folder / "output_summary.md", "# summary\n")
        assert_true(run_brain(ws, "overlay", str(folder)).returncode == 0, "overlay should succeed before closeout")
        assert_true(
            run_brain(
                ws,
                "closeout",
                str(folder),
                "--summary",
                "Custom skill worked well for this recurring analysis route.",
                "--used-skills",
                "custom-unmapped-skill",
                "--outcome",
                "success",
                "--reuse",
                "yes",
            ).returncode
            == 0,
            "closeout should succeed before quality-aware routing",
        )
        result = run_brain(ws, "skill-route", "recurring analysis workflow for this folder", "--path", str(folder))
        assert_true(result.returncode == 0, f"quality-aware skill-route expected 0, got {result.returncode}, stderr={result.stderr}")
        registry = load_skill_route_registry(ws)
        entry = registry["entries"][0]
        assert_true("custom-unmapped-skill" in entry["primary_skills"], "successful reusable closeout should rerank the candidate skill into the primary route")
        assert_true(any("custom-unmapped-skill" in note for note in entry["quality_notes"]), "route should emit quality notes for the reranked skill")


def test_skill_route_existing_video_correction_detects_gap() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-skill-route-video-gap-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        folder = ws / "vis_math_lecture_case"
        folder.mkdir(parents=True, exist_ok=True)
        write_file(folder / "Lecture1_Unit7_Event.mp4", "placeholder\n")
        result = run_brain(
            ws,
            "skill-route",
            "inspect and correct overlapping text at the end of the existing lecture video",
            "--path",
            str(folder),
        )
        assert_true(result.returncode == 2, f"video correction route should detect a gap, got {result.returncode}, stderr={result.stderr}")
        assert_true("Task phase: `correction`" in result.stdout, "route output should expose corrective intent")
        assert_true("Artifact type: `video`" in result.stdout, "route output should expose video artifact intent")
        registry = load_skill_route_registry(ws)
        entry = registry["entries"][0]
        assert_true(entry["intent"]["task_phase"] == "correction", "intent parser should classify corrective video work")
        assert_true(entry["intent"]["artifact_type"] == "video", "intent parser should detect existing video artifacts")
        assert_true(entry["intent"]["artifact_state"] == "existing", "video correction should treat the artifact as existing")
        assert_true(entry["gap_detected"] is True, "existing video correction should escalate to discovery when no video-fit skill exists")
        assert_true(
            not any(
                skill in {"matplotlib", "statistical-analysis", "statsmodels", "jupyter-notebook", "spreadsheet"}
                for skill in entry["primary_skills"]
            ),
            "video correction should not route to domain-only math or course skills",
        )


def test_skill_route_existing_markdown_correction_avoids_analysis_lane() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-skill-route-markdown-correction-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        folder = ws / "kernel_manuscript_case"
        folder.mkdir(parents=True, exist_ok=True)
        write_file(folder / "draft.md", "# Draft\n\n[@smith2024]\n")
        result = run_brain(
            ws,
            "skill-route",
            "verify and correct citation formatting in the existing manuscript draft",
            "--path",
            str(folder),
        )
        assert_true(result.returncode == 2, f"markdown correction route should surface a discovery gap, got {result.returncode}, stderr={result.stderr}")
        assert_true("Task phase: `correction`" in result.stdout, "route output should expose corrective intent")
        assert_true("Artifact type: `markdown`" in result.stdout, "route output should expose markdown artifact intent")
        registry = load_skill_route_registry(ws)
        entry = registry["entries"][0]
        assert_true(entry["intent"]["task_phase"] == "correction", "intent parser should classify manuscript correction as corrective work")
        assert_true(entry["intent"]["artifact_type"] == "markdown", "intent parser should detect markdown manuscript artifacts")
        assert_true(
            not any(skill in {"spreadsheet", "xlsx", "pdf-single-ingest-obsidian"} for skill in entry["primary_skills"]),
            "existing manuscript correction should not route to analysis or ingest-first skills",
        )
        assert_true(
            entry["gap_detected"] is True,
            "existing manuscript correction should escalate when no strong editing-specific skill is installed",
        )
        assert_true(
            entry["primary_skills"] == [],
            "existing manuscript correction should leave the primary lane empty when only fallback/discovery paths fit",
        )
        assert_true(
            not any(skill in {"visual-explainer", "mermaid-visualizer", "eval-harness"} for skill in entry["primary_skills"]),
            "generic helpers should not occupy the primary lane for existing manuscript correction",
        )


def test_closeout_skips_existing_fallback_or_active_skill() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-closeout-existing-lane-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        folder = ws / "analysis_runtime"
        folder.mkdir(parents=True, exist_ok=True)
        write_file(folder / "dataset.csv", "x,y\n1,2\n")
        write_file(folder / "results.xlsx", "placeholder\n")
        write_file(folder / "output_summary.md", "# summary\n")
        overlay = run_brain(ws, "overlay", str(folder))
        assert_true(overlay.returncode == 0, f"overlay should succeed before closeout, got {overlay.returncode}")
        result = run_brain(
            ws,
            "closeout",
            str(folder),
            "--summary",
            "Used an already configured fallback-only skill.",
            "--used-skills",
            "docx",
        )
        assert_true(result.returncode == 0, f"closeout with mapped skill expected 0, got {result.returncode}")
        payload = load_skill_iteration_registry(ws)
        assert_true(len(payload.get("closeouts", [])) == 1, "closeout should still be recorded for mapped skills")
        assert_true(len(payload.get("proposals", [])) == 0, "mapped active/fallback skills should not create proposals")


def test_closeout_records_unknown_skill_as_discovery_hint() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-closeout-unknown-skill-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        folder = ws / "analysis_runtime"
        folder.mkdir(parents=True, exist_ok=True)
        write_file(folder / "dataset.csv", "x,y\n1,2\n")
        write_file(folder / "results.xlsx", "placeholder\n")
        write_file(folder / "output_summary.md", "# summary\n")
        overlay = run_brain(ws, "overlay", str(folder))
        assert_true(overlay.returncode == 0, f"overlay should succeed before closeout, got {overlay.returncode}")
        result = run_brain(
            ws,
            "closeout",
            str(folder),
            "--summary",
            "Tried an unknown skill.",
            "--used-skills",
            "not-installed-skill",
        )
        assert_true(result.returncode == 0, f"closeout with unknown skill should still record closeout, got {result.returncode}, stderr={result.stderr}")
        assert_true("Discovery suggestion" in result.stdout, "unknown skill should turn into a discovery hint")
        payload = load_skill_iteration_registry(ws)
        assert_true(len(payload.get("closeouts", [])) == 1, "unknown skill should still write a closeout")
        closeout = payload["closeouts"][0]
        assert_true(closeout["invalid_skills"] == ["not-installed-skill"], "closeout should preserve invalid skills for later discovery")
        assert_true(len(payload.get("proposals", [])) == 0, "unknown skill should not create promotion proposals")


def test_skill_review_lists_open_proposals() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-skill-review-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        extra_root = Path(tmp_s) / "external" / "codex_home" / "skills"
        make_skill(extra_root, "custom-unmapped-skill")
        folder = ws / "analysis_runtime"
        folder.mkdir(parents=True, exist_ok=True)
        write_file(folder / "dataset.csv", "x,y\n1,2\n")
        write_file(folder / "results.xlsx", "placeholder\n")
        write_file(folder / "output_summary.md", "# summary\n")
        assert_true(run_brain(ws, "overlay", str(folder)).returncode == 0, "overlay should succeed before review setup")
        assert_true(
            run_brain(
                ws,
                "closeout",
                str(folder),
                "--summary",
                "Created open proposal.",
                "--used-skills",
                "custom-unmapped-skill",
                "--outcome",
                "success",
                "--reuse",
                "yes",
            ).returncode
            == 0,
            "closeout should succeed before review",
        )
        payload = load_skill_iteration_registry(ws)
        proposal_id = payload["proposals"][0]["id"]
        review = run_brain(ws, "skill-review")
        assert_true(review.returncode == 0, f"skill-review expected 0, got {review.returncode}")
        assert_true(proposal_id in review.stdout, "skill-review should list the open proposal id")
        assert_true("custom-unmapped-skill" in review.stdout, "skill-review should list the proposal skill")


def test_skill_promote_adds_skill_to_fallback_and_updates_status() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-skill-promote-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        extra_root = Path(tmp_s) / "external" / "codex_home" / "skills"
        make_skill(extra_root, "custom-unmapped-skill")
        folder = ws / "analysis_runtime"
        folder.mkdir(parents=True, exist_ok=True)
        write_file(folder / "dataset.csv", "x,y\n1,2\n")
        write_file(folder / "results.xlsx", "placeholder\n")
        write_file(folder / "output_summary.md", "# summary\n")
        assert_true(run_brain(ws, "overlay", str(folder)).returncode == 0, "overlay should succeed before promotion setup")
        assert_true(
            run_brain(
                ws,
                "closeout",
                str(folder),
                "--summary",
                "Candidate skill is reusable.",
                "--used-skills",
                "custom-unmapped-skill",
                "--outcome",
                "success",
                "--reuse",
                "yes",
            ).returncode
            == 0,
            "closeout should succeed before promotion",
        )
        payload = load_skill_iteration_registry(ws)
        proposal_id = payload["proposals"][0]["id"]
        promote = run_brain(ws, "skill-promote", proposal_id)
        assert_true(promote.returncode == 0, f"skill-promote expected 0, got {promote.returncode}, stderr={promote.stderr}")
        updated = load_skill_iteration_registry(ws)
        proposal = updated["proposals"][0]
        assert_true(proposal["status"] == "promoted_to_fallback", "skill-promote should update proposal status")
        work_modes = tomllib.loads((ws / "policy" / "work_modes.toml").read_text(encoding="utf-8"))
        fallback_skills = work_modes["mode"]["analysis"]["fallback_skills"]
        assert_true("custom-unmapped-skill" in fallback_skills, "skill-promote should add the skill to analysis fallback lane")


def test_skill_promote_is_idempotent_when_repeated() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-skill-promote-repeat-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        extra_root = Path(tmp_s) / "external" / "codex_home" / "skills"
        make_skill(extra_root, "custom-unmapped-skill")
        folder = ws / "analysis_runtime"
        folder.mkdir(parents=True, exist_ok=True)
        write_file(folder / "dataset.csv", "x,y\n1,2\n")
        write_file(folder / "results.xlsx", "placeholder\n")
        write_file(folder / "output_summary.md", "# summary\n")
        assert_true(run_brain(ws, "overlay", str(folder)).returncode == 0, "overlay should succeed before idempotence test")
        assert_true(
            run_brain(
                ws,
                "closeout",
                str(folder),
                "--summary",
                "Candidate skill is reusable.",
                "--used-skills",
                "custom-unmapped-skill",
                "--outcome",
                "success",
                "--reuse",
                "yes",
            ).returncode
            == 0,
            "closeout should succeed before repeated promotion",
        )
        proposal_id = load_skill_iteration_registry(ws)["proposals"][0]["id"]
        first = run_brain(ws, "skill-promote", proposal_id)
        second = run_brain(ws, "skill-promote", proposal_id)
        assert_true(first.returncode == 0, "first promotion should succeed")
        assert_true(second.returncode == 0, "second promotion should stay idempotent")
        assert_true("already promoted" in second.stdout, "second promotion should report idempotence explicitly")


def test_skill_promote_rejects_if_skill_is_no_longer_candidate() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-skill-promote-non-candidate-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        extra_root = Path(tmp_s) / "external" / "codex_home" / "skills"
        make_skill(extra_root, "custom-unmapped-skill")
        folder = ws / "analysis_runtime"
        folder.mkdir(parents=True, exist_ok=True)
        write_file(folder / "dataset.csv", "x,y\n1,2\n")
        write_file(folder / "results.xlsx", "placeholder\n")
        write_file(folder / "output_summary.md", "# summary\n")
        assert_true(run_brain(ws, "overlay", str(folder)).returncode == 0, "overlay should succeed before non-candidate promotion test")
        assert_true(
            run_brain(
                ws,
                "closeout",
                str(folder),
                "--summary",
                "Candidate skill is reusable.",
                "--used-skills",
                "custom-unmapped-skill",
                "--outcome",
                "success",
                "--reuse",
                "yes",
            ).returncode
            == 0,
            "closeout should succeed before non-candidate promotion test",
        )
        work_modes_path = ws / "policy" / "work_modes.toml"
        original = work_modes_path.read_text(encoding="utf-8")
        work_modes_path.write_text(
            original.replace('fallback_skills = ["docx"]', 'fallback_skills = ["docx", "custom-unmapped-skill"]', 1),
            encoding="utf-8",
        )
        proposal_id = load_skill_iteration_registry(ws)["proposals"][0]["id"]
        result = run_brain(ws, "skill-promote", proposal_id)
        assert_true(result.returncode == 1, "skill-promote should reject proposals whose skill is no longer a candidate")
        assert_true("no longer a candidate" in result.stderr, "skill-promote should explain the candidate guard failure")


def test_skill_reject_updates_status_without_work_mode_change() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-skill-reject-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        extra_root = Path(tmp_s) / "external" / "codex_home" / "skills"
        make_skill(extra_root, "custom-unmapped-skill")
        folder = ws / "analysis_runtime"
        folder.mkdir(parents=True, exist_ok=True)
        write_file(folder / "dataset.csv", "x,y\n1,2\n")
        write_file(folder / "results.xlsx", "placeholder\n")
        write_file(folder / "output_summary.md", "# summary\n")
        assert_true(run_brain(ws, "overlay", str(folder)).returncode == 0, "overlay should succeed before rejection setup")
        assert_true(
            run_brain(
                ws,
                "closeout",
                str(folder),
                "--summary",
                "Candidate skill is not worth promoting.",
                "--used-skills",
                "custom-unmapped-skill",
                "--outcome",
                "success",
                "--reuse",
                "yes",
            ).returncode
            == 0,
            "closeout should succeed before rejection",
        )
        proposal_id = load_skill_iteration_registry(ws)["proposals"][0]["id"]
        before = (ws / "policy" / "work_modes.toml").read_text(encoding="utf-8")
        reject = run_brain(ws, "skill-reject", proposal_id, "--reason", "Too narrow to add to the fallback lane.")
        assert_true(reject.returncode == 0, f"skill-reject expected 0, got {reject.returncode}, stderr={reject.stderr}")
        after = (ws / "policy" / "work_modes.toml").read_text(encoding="utf-8")
        assert_true(before == after, "skill-reject should not modify work_modes.toml")
        proposal = load_skill_iteration_registry(ws)["proposals"][0]
        assert_true(proposal["status"] == "rejected", "skill-reject should update proposal status")
        assert_true(proposal["resolution_reason"] == "Too narrow to add to the fallback lane.", "skill-reject should persist the reason")


def test_closeout_fails_on_invalid_registry_without_resetting_it() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-closeout-invalid-registry-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        extra_root = Path(tmp_s) / "external" / "codex_home" / "skills"
        make_skill(extra_root, "custom-unmapped-skill")
        folder = ws / "analysis_runtime"
        folder.mkdir(parents=True, exist_ok=True)
        write_file(folder / "dataset.csv", "x,y\n1,2\n")
        write_file(folder / "results.xlsx", "placeholder\n")
        write_file(folder / "output_summary.md", "# summary\n")
        assert_true(run_brain(ws, "overlay", str(folder)).returncode == 0, "overlay should succeed before invalid-registry test")
        registry_path = ws / "contexts" / "skill_iteration_registry.json"
        registry_path.write_text("{broken", encoding="utf-8")
        result = run_brain(
            ws,
            "closeout",
            str(folder),
            "--summary",
            "Registry corruption should fail cleanly.",
            "--used-skills",
            "custom-unmapped-skill",
            "--outcome",
            "success",
            "--reuse",
            "yes",
        )
        assert_true(result.returncode == 1, f"closeout with invalid registry should fail, got {result.returncode}")
        assert_true("Invalid skill iteration registry JSON" in result.stderr, "invalid registry error should be explicit")
        assert_true(registry_path.read_text(encoding="utf-8") == "{broken", "invalid registry should not be silently reset")
        closeout_dir = ws / "contexts" / "skill_iterations" / "closeouts"
        lingering = sorted(closeout_dir.glob("*.json")) if closeout_dir.exists() else []
        assert_true(not lingering, "closeout should not leave orphan closeout files when the registry is invalid")


def test_skill_promote_preserves_custom_work_mode_content() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-skill-promote-preserve-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        extra_root = Path(tmp_s) / "external" / "codex_home" / "skills"
        make_skill(extra_root, "custom-unmapped-skill")
        folder = ws / "analysis_runtime"
        folder.mkdir(parents=True, exist_ok=True)
        write_file(folder / "dataset.csv", "x,y\n1,2\n")
        write_file(folder / "results.xlsx", "placeholder\n")
        write_file(folder / "output_summary.md", "# summary\n")
        assert_true(run_brain(ws, "overlay", str(folder)).returncode == 0, "overlay should succeed before preservation test")
        assert_true(
            run_brain(
                ws,
                "closeout",
                str(folder),
                "--summary",
                "Candidate skill is reusable.",
                "--used-skills",
                "custom-unmapped-skill",
                "--outcome",
                "success",
                "--reuse",
                "yes",
            ).returncode
            == 0,
            "closeout should succeed before promotion",
        )
        work_modes_path = ws / "policy" / "work_modes.toml"
        original = work_modes_path.read_text(encoding="utf-8")
        work_modes_path.write_text(original + "\n# custom comment\n[mode.custom]\nnotes = [\"keep me\"]\n", encoding="utf-8")
        proposal_id = load_skill_iteration_registry(ws)["proposals"][0]["id"]
        result = run_brain(ws, "skill-promote", proposal_id)
        assert_true(result.returncode == 0, f"skill-promote should preserve custom content, got {result.returncode}")
        updated = work_modes_path.read_text(encoding="utf-8")
        assert_true("# custom comment" in updated, "promotion should preserve trailing comments")
        assert_true("[mode.custom]" in updated, "promotion should preserve unknown custom sections")
        assert_true("notes = [\"keep me\"]" in updated, "promotion should preserve custom metadata")


def test_refresh_status_capabilities_and_reconcile_include_overlay_and_skill_iteration() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-overlay-refresh-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        extra_root = Path(tmp_s) / "external" / "codex_home" / "skills"
        make_skill(extra_root, "custom-unmapped-skill")
        folder = ws / "analysis_runtime"
        folder.mkdir(parents=True, exist_ok=True)
        write_file(folder / "dataset.csv", "x,y\n1,2\n")
        write_file(folder / "results.xlsx", "placeholder\n")
        write_file(folder / "output_summary.md", "# summary\n")
        assert_true(run_brain(ws, "overlay", str(folder)).returncode == 0, "overlay should succeed before refresh")
        assert_true(
            run_brain(
                ws,
                "closeout",
                str(folder),
                "--summary",
                "Candidate skill is reusable.",
                "--used-skills",
                "custom-unmapped-skill",
                "--outcome",
                "success",
                "--reuse",
                "yes",
            ).returncode
            == 0,
            "closeout should succeed before refresh",
        )
        assert_true(
            run_brain(ws, "skill-route", "recurring analysis workflow for this folder", "--path", str(folder)).returncode == 0,
            "skill-route should succeed before refresh",
        )
        refresh = run_brain(ws, "refresh")
        assert_true(refresh.returncode == 0, f"refresh with overlay/skill iteration expected 0, got {refresh.returncode}, stderr={refresh.stderr}")
        registry = load_registry(ws)
        overlay_source = registry["sources"]["overlay"]["runtime_overlays"]
        skill_iteration = registry["sources"]["skills"]["iteration"]
        skill_route = registry["sources"]["skills"]["routing"]
        assert_true(overlay_source["brief_count"] >= 1, "refresh should report runtime overlay brief count")
        assert_true(skill_iteration["open_proposal_count"] == 1, "refresh should report open skill proposal count")
        assert_true(skill_route["route_count"] == 1, "refresh should report persisted skill route count")
        assert_true("overlay_runtime" in registry["checks"], "refresh should include overlay runtime check")
        assert_true("skill_iteration" in registry["checks"], "refresh should include skill iteration check")
        assert_true("skill_route" in registry["checks"], "refresh should include skill route check")
        status_text = (ws / "contexts" / "system_status.md").read_text(encoding="utf-8")
        assert_true("## Overlay Runtime" in status_text, "status should include overlay runtime summary")
        assert_true("Open skill proposals: `1`" in status_text, "status should include open proposal count")
        assert_true("Latest skill route:" in status_text, "status should include latest skill route summary")
        capabilities = run_brain(ws, "capabilities")
        assert_true(capabilities.returncode == 0, "capabilities should still succeed after overlay/closeout")
        assert_true("`overlay`" in capabilities.stdout, "capabilities should list overlay command")
        assert_true("`closeout`" in capabilities.stdout, "capabilities should list closeout command")
        assert_true("`skill-route`" in capabilities.stdout, "capabilities should list skill-route command")
        assert_true("`skill-review`" in capabilities.stdout, "capabilities should list skill-review command")
        assert_true("Runtime overlay briefs: `1`" in capabilities.stdout, "capabilities should report overlay brief count")
        assert_true("Skill iteration gate: `open=1` closeouts=`1`" in capabilities.stdout, "capabilities should report skill iteration counts")
        assert_true("Skill router: `routes=1`" in capabilities.stdout, "capabilities should report skill route counts")
        reconcile = run_brain(ws, "reconcile")
        assert_true(reconcile.returncode == 0, f"reconcile should not treat new runtime artifacts as folder-only, got {reconcile.returncode}")
        report = load_reconciliation_report(ws)
        assert_true("`contexts/runtime_overlay_registry.json` `evidence=runtime_writer`" in report, "overlay registry should be implemented in reconcile")
        assert_true("`contexts/skill_iteration_registry.json` `evidence=runtime_writer`" in report, "skill iteration registry should be implemented in reconcile")
        assert_true("`contexts/skill_route_registry.json` `evidence=runtime_writer`" in report, "skill route registry should be implemented in reconcile")
        assert_true("`contexts/runtime_overlays/" in report, "overlay brief should be reconciled as implemented")
        assert_true("`contexts/skill_iterations/closeouts/" in report, "closeout artifact should be reconciled as implemented")
        assert_true("`contexts/skill_iterations/proposals/" in report, "proposal artifact should be reconciled as implemented")


def test_reconcile_writes_report_only_and_preserves_canonical_outputs() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-reconcile-report-") as tmp_s:
        ws = make_workspace(Path(tmp_s), include_folder_only_artifact=True, seed_canonical_outputs=True)
        registry_path = ws / "contexts" / "system_registry.json"
        status_path = ws / "contexts" / "system_status.md"
        registry_before = registry_path.read_text(encoding="utf-8")
        status_before = status_path.read_text(encoding="utf-8")
        result = run_brain(ws, "reconcile")
        assert_true(result.returncode == 2, f"reconcile with folder-only artifacts should return 2, got {result.returncode}")
        report_path = ws / "contexts" / "folder_hub_reconciliation.md"
        assert_true(report_path.exists(), "reconcile should write contexts/folder_hub_reconciliation.md")
        assert_true(registry_path.read_text(encoding="utf-8") == registry_before, "reconcile should not rewrite system_registry.json")
        assert_true(status_path.read_text(encoding="utf-8") == status_before, "reconcile should not rewrite system_status.md")


def test_reconcile_classifies_implemented_supporting_and_folder_only() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-reconcile-classify-") as tmp_s:
        ws = make_workspace(Path(tmp_s), include_folder_only_artifact=True, seed_canonical_outputs=True)
        result = run_brain(ws, "reconcile")
        assert_true(result.returncode == 2, f"reconcile with folder-only artifacts should return 2, got {result.returncode}")
        report = load_reconciliation_report(ws)
        assert_true("## Implemented Artifacts" in report, "reconcile report should include implemented section")
        assert_true("## Supporting Artifacts" in report, "reconcile report should include supporting section")
        assert_true("## Archive Artifacts" in report, "reconcile report should include archive section")
        assert_true("## Folder-only Artifacts" in report, "reconcile report should include folder-only section")
        assert_true("`policy/system_hub.toml` `evidence=runtime_reader`" in report, "system_hub.toml should be runtime-integrated")
        assert_true("`contexts/system_registry.json` `evidence=runtime_writer`" in report, "system_registry.json should be runtime-written")
        assert_true("`contexts/agent_benchmark_cases.json` `evidence=runtime_reader`" in report, "benchmark cases should be integrated")
        assert_true("`scripts/run_agent_benchmark.sh` `evidence=runtime_reader`" in report, "benchmark wrapper should be integrated")
        assert_true("`scripts/publish_agent_policy.py` `evidence=runtime_reader`" in report, "publisher should be integrated")
        assert_true("`scripts/codex_continue_here` `evidence=runtime_reader`" in report, "continuity entrypoint should be integrated")
        assert_true("`obsidian_codex_bridge.py` `evidence=supporting_script`" in report, "bridge should be supporting")
        assert_true("`contexts/research.md` `evidence=supporting_script`" in report, "research template should be supporting")
        assert_true("`contexts/codex_system_status_20260310.md` `evidence=unreferenced`" in report, "historical status should still be reconciled")
        assert_true("`contexts/system_gap_notes.md` `evidence=unreferenced`" in report, "system gap note should remain folder-only")


def test_reconcile_classifies_history_snapshots_as_archive() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-reconcile-archive-") as tmp_s:
        ws = make_workspace(Path(tmp_s), include_folder_only_artifact=True, seed_canonical_outputs=True)
        result = run_brain(ws, "reconcile")
        assert_true(result.returncode == 2, f"reconcile with archive and folder-only artifacts should return 2, got {result.returncode}")
        report = load_reconciliation_report(ws)
        assert_true("- Archive: `2`" in report, "archive count should include historical files")
        assert_true("`contexts/codex_system_status_20260310.md` `evidence=unreferenced`" in report, "historical status should be present")
        assert_true("`FOLDER_PROGRESS_ws_20260311-000000.md` `evidence=unreferenced`" in report, "progress snapshot should be present")
        assert_true("## Recommended Promotions" in report, "report should include recommendations section")
        assert_true("`contexts/codex_system_status_20260310.md`" not in report.split("## Recommended Promotions", 1)[1], "archive artifacts should not be recommended for promotion")


def test_reconcile_exit_0_in_minimal_fully_referenced_fixture() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-reconcile-clean-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        result = run_brain(ws, "reconcile")
        assert_true(result.returncode == 0, f"reconcile in minimal referenced fixture should return 0, got {result.returncode}, stderr={result.stderr}")
        report = load_reconciliation_report(ws)
        assert_true("- Folder-only: `0`" in report, "minimal fixture should report zero folder-only artifacts")


def test_memory_triage_daily_writes_registry_and_status() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-memory-triage-daily-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        result = run_brain(ws, "memory-triage", "--window", "daily", "--root", str(ws))
        assert_true(result.returncode == 0, f"memory-triage daily expected 0, got {result.returncode}, stderr={result.stderr}")
        registry = load_memory_governance_registry(ws)
        status = load_memory_governance_status(ws)
        assert_true(registry["retrieval_mode"] == "semantic-lite", "memory governance should expose semantic-lite retrieval mode")
        assert_true(registry["window_runs"]["daily"]["selected_count"] == 3, "daily triage should capture selected_count")
        assert_true("## Daily Triage" in status, "memory governance status should include daily triage section")
        assert_true("## Decay Buckets" in status, "memory governance status should include decay bucket section")
        assert_true(
            registry["durable_count"] + registry["summary_only_count"] + registry["archive_candidate_count"] == len(registry["entries"]),
            "memory governance counts should reconcile with aggregated entries",
        )
        assert_true(
            registry["hot_count"] + registry["warm_count"] + registry["cool_count"] == len(registry["entries"]),
            "decay counts should reconcile with aggregated entries",
        )


def test_memory_triage_selected_count_zero_is_empty_not_error() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-memory-triage-empty-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        write_recent_memory_fixture(ws, "daily", recent_memory_payload(ws, days=14, top=3, folders=[]))
        result = run_brain(ws, "memory-triage", "--window", "daily", "--root", str(ws))
        assert_true(result.returncode == 0, f"memory-triage empty daily expected 0, got {result.returncode}, stderr={result.stderr}")
        registry = load_memory_governance_registry(ws)
        daily = registry["window_runs"]["daily"]
        assert_true(daily["selected_count"] == 0, "empty daily triage should preserve selected_count=0")
        assert_true(daily["durable_count"] == 0 and daily["summary_only_count"] == 0 and daily["archive_candidate_count"] == 0, "empty daily triage should keep all buckets at zero")


def test_memory_triage_repeated_report_folder_becomes_durable() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-memory-triage-repeat-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        folder = ws / "analysis_runtime"
        first_payload = recent_memory_payload(
            ws,
            days=14,
            top=3,
            folders=[
                {
                    "folder": str(folder.resolve()),
                    "activity": {"updated_at": "2026-03-11T10:00:00+00:00"},
                    "sync": {"entry": {"report_path": str((ws / "FOLDER_PROGRESS_repeat_1.md").resolve())}},
                }
            ],
        )
        write_recent_memory_fixture(ws, "daily", first_payload)
        first = run_brain(ws, "memory-triage", "--window", "daily", "--root", str(ws))
        assert_true(first.returncode == 0, "first daily triage should succeed")
        second_payload = recent_memory_payload(
            ws,
            days=14,
            top=3,
            folders=[
                {
                    "folder": str(folder.resolve()),
                    "activity": {"updated_at": "2026-03-12T10:00:00+00:00"},
                    "sync": {"entry": {"report_path": str((ws / "FOLDER_PROGRESS_repeat_2.md").resolve())}},
                }
            ],
        )
        write_recent_memory_fixture(ws, "daily", second_payload)
        second = run_brain(ws, "memory-triage", "--window", "daily", "--root", str(ws))
        assert_true(second.returncode == 0, "second daily triage should succeed")
        registry = load_memory_governance_registry(ws)
        entries = registry["window_runs"]["daily"]["entries"]
        assert_true(len(entries) == 1, "repeated triage should keep one entry for one folder")
        assert_true(entries[0]["bucket"] == "durable", "report path plus repeated appearance should classify as durable")
        assert_true(entries[0]["appeared_in_previous_run"], "second run should record previous appearance")


def test_memory_triage_report_only_becomes_summary_only() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-memory-triage-report-only-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        folder = ws / "analysis_runtime"
        write_recent_memory_fixture(
            ws,
            "daily",
            recent_memory_payload(
                ws,
                days=14,
                top=3,
                folders=[
                    {
                        "folder": str(folder.resolve()),
                        "activity": {
                            "updated_at": "2026-03-11T10:00:00+00:00",
                            "activity_score": 40,
                            "salience_score": 20,
                            "combined_score": 60,
                        },
                        "sync": {"entry": {"report_path": str((ws / "FOLDER_PROGRESS_report_only.md").resolve())}},
                    }
                ],
            ),
        )
        result = run_brain(ws, "memory-triage", "--window", "daily", "--root", str(ws))
        assert_true(result.returncode == 0, "report-only triage should succeed")
        registry = load_memory_governance_registry(ws)
        entry = registry["window_runs"]["daily"]["entries"][0]
        assert_true(entry["bucket"] == "summary_only", "report-only memory should not promote directly to durable")


def test_memory_triage_overlay_closeout_path_normalization_promotes_durable() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-memory-triage-overlay-closeout-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        folder = ws / "analysis_runtime"
        folder.mkdir(parents=True, exist_ok=True)
        write_file(folder / "dataset.csv", "x,y\n1,2\n")
        assert_true(run_brain(ws, "overlay", str(folder)).returncode == 0, "overlay should succeed before closeout")
        assert_true(
            run_brain(ws, "closeout", str(folder), "--summary", "used existing lane", "--used-skills", "obsidian-markdown").returncode == 0,
            "closeout should succeed before triage",
        )
        raw_folder_path = f"{folder.parent}/analysis_runtime/../analysis_runtime"
        write_recent_memory_fixture(
            ws,
            "daily",
            recent_memory_payload(
                ws,
                days=14,
                top=3,
                folders=[
                    {
                        "folder": raw_folder_path,
                        "activity": {"updated_at": "2026-03-11T10:00:00+00:00"},
                        "sync": {},
                    }
                ],
            ),
        )
        result = run_brain(ws, "memory-triage", "--window", "daily", "--root", str(ws))
        assert_true(result.returncode == 0, "triage should normalize folder paths without failing")
        registry = load_memory_governance_registry(ws)
        entry = registry["window_runs"]["daily"]["entries"][0]
        assert_true(entry["folder_path"] == str(folder.resolve()), "triage should normalize folder_path before writing registry")
        assert_true(entry["bucket"] == "durable", "overlay + closeout continuity should promote durable memory even without report path")


def test_memory_triage_without_report_or_repeat_becomes_archive_candidate() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-memory-triage-archive-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        folder = ws / "archive_only_case"
        write_recent_memory_fixture(
            ws,
            "daily",
            recent_memory_payload(
                ws,
                days=14,
                top=3,
                folders=[
                    {
                        "folder": str(folder.resolve()),
                        "activity": {"updated_at": "2026-03-11T08:00:00+00:00"},
                        "sync": {},
                    }
                ],
            ),
        )
        result = run_brain(ws, "memory-triage", "--window", "daily", "--root", str(ws))
        assert_true(result.returncode == 0, "archive-candidate daily triage should succeed")
        registry = load_memory_governance_registry(ws)
        entry = registry["window_runs"]["daily"]["entries"][0]
        assert_true(entry["bucket"] == "archive_candidate", "folders without report or repeat evidence should be archive candidates")


def test_session_gate_fresh_thread_returns_0() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-session-gate-fresh-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        folder = ws / "analysis_runtime"
        folder.mkdir(parents=True, exist_ok=True)
        write_file(folder / "dataset.csv", "x,y\n1,2\n")
        write_file(folder / "results.xlsx", "placeholder\n")
        write_file(folder / "output_summary.md", "# summary\n")
        assert_true(run_brain(ws, "overlay", str(folder)).returncode == 0, "overlay should succeed before fresh session gate")
        assert_true(run_brain(ws, "memory-triage", "--window", "daily", "--root", str(ws)).returncode == 0, "daily triage should succeed before fresh session gate")
        seed_thread(ws, "thread-fresh", title="Fresh thread", cwd=folder, updated_at_epoch=int(time.time()) - 3600)
        result = run_brain(ws, "session-gate", "--thread-id", "thread-fresh", "--cwd", str(folder))
        assert_true(result.returncode == 0, f"fresh session gate should return 0, got {result.returncode}, stderr={result.stderr}")
        assert_true("Recommendation: `fresh_resume`" in result.stdout, "fresh session should recommend direct resume")
        assert_true("Recommended brief path: `" in result.stdout and "none" not in result.stdout.split("Recommended brief path:", 1)[1].splitlines()[0], "fresh session should surface overlay brief path")
        assert_true("memory_governance_status.md" in result.stdout, "fresh session should surface memory governance summary path")


def test_session_gate_stale_thread_returns_2() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-session-gate-stale-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        assert_true(run_brain(ws, "memory-triage", "--window", "weekly", "--root", str(ws)).returncode == 0, "weekly triage should succeed before stale session gate")
        seed_thread(ws, "thread-stale", title="Stale thread", cwd=ws, updated_at_epoch=int(time.time()) - (5 * 86400))
        result = run_brain(ws, "session-gate", "--thread-id", "thread-stale", "--cwd", str(ws))
        assert_true(result.returncode == 2, f"stale session gate should return 2, got {result.returncode}, stderr={result.stderr}")
        assert_true("Recommendation: `stale_new_session`" in result.stdout, "stale session should recommend a new session")


def test_session_gate_prefers_newest_timestamp_across_sqlite_and_index() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-session-gate-merged-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        seed_thread(ws, "thread-merged", title="Merged timestamps", cwd=ws, updated_at_epoch=int(time.time()) - (5 * 86400))
        write_session_index_only(ws, "thread-merged", title="Merged timestamps", updated_at_epoch=int(time.time()) - 1800)
        result = run_brain(ws, "session-gate", "--thread-id", "thread-merged", "--cwd", str(ws))
        assert_true(result.returncode == 0, f"merged session gate should return 0 when index is newer, got {result.returncode}")
        assert_true("Recommendation: `fresh_resume`" in result.stdout, "newer session_index timestamp should keep the thread fresh")
        assert_true("Metadata status: `merged`" in result.stdout, "session gate should surface merged metadata status")


def test_session_gate_archived_thread_is_stale() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-session-gate-archived-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        seed_thread(ws, "thread-archived", title="Archived thread", cwd=ws, updated_at_epoch=int(time.time()) - 3600, archived=True)
        result = run_brain(ws, "session-gate", "--thread-id", "thread-archived", "--cwd", str(ws))
        assert_true(result.returncode == 2, f"archived session gate should return 2, got {result.returncode}")
        assert_true("Archived: `True`" in result.stdout, "archived thread should be reported as archived")
        assert_true("Recommendation: `stale_new_session`" in result.stdout, "archived thread should not recommend direct resume")


def test_session_gate_index_only_threads_are_conservative_stale() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-session-gate-index-only-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        write_session_index_only(ws, "thread-index-only", title="Index only thread", updated_at_epoch=int(time.time()) - 600)
        result = run_brain(ws, "session-gate", "--thread-id", "thread-index-only", "--cwd", str(ws))
        assert_true(result.returncode == 2, f"index-only session gate should return 2, got {result.returncode}")
        assert_true("Metadata status: `index_only`" in result.stdout, "session gate should show index-only metadata state")
        assert_true("Recommendation: `stale_new_session`" in result.stdout, "index-only threads should default to a new session")


def test_session_gate_missing_thread_returns_1() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-session-gate-missing-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        result = run_brain(ws, "session-gate", "--thread-id", "missing-thread", "--cwd", str(ws))
        assert_true(result.returncode == 1, f"missing thread should fail with 1, got {result.returncode}")
        assert_true("Unknown thread id" in result.stderr, "missing thread error should be explicit")


def test_session_gate_without_thread_id_uses_checkpoint_linked_advisory() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-session-gate-checkpoint-only-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        folder = ws / "analysis_runtime"
        folder.mkdir(parents=True, exist_ok=True)
        state_dir = ws.parent / "external" / "vault" / "00_system" / "checkpoints" / ".state"
        write_file(
            state_dir / "active_session.json",
            json.dumps(
                {
                    "topic": "Checkpoint-linked continuity",
                    "last_checkpoint_at": (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=1)).isoformat(timespec="seconds"),
                    "cwd": str(folder.resolve()),
                },
                ensure_ascii=False,
            )
            + "\n",
        )
        assert_true(run_brain(ws, "overlay", str(folder)).returncode == 0, "overlay should exist for checkpoint-linked advisory")
        result = run_brain(ws, "session-gate", "--cwd", str(folder))
        assert_true(result.returncode == 0, "checkpoint-linked advisory should return 0")
        assert_true("Recommendation: `checkpoint_linked_advisory`" in result.stdout, "session-gate should emit checkpoint-linked advisory without a thread id")
        assert_true("Metadata status: `checkpoint_only`" in result.stdout, "session-gate should expose checkpoint-only metadata status")


def test_session_gate_without_thread_id_respects_stale_threshold() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-session-gate-checkpoint-stale-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        folder = ws / "analysis_runtime"
        folder.mkdir(parents=True, exist_ok=True)
        state_dir = ws.parent / "external" / "vault" / "00_system" / "checkpoints" / ".state"
        write_file(
            state_dir / "active_session.json",
            json.dumps(
                {
                    "topic": "Old checkpoint-linked continuity",
                    "last_checkpoint_at": (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=5)).isoformat(timespec="seconds"),
                    "cwd": str(folder.resolve()),
                },
                ensure_ascii=False,
            )
            + "\n",
        )
        assert_true(run_brain(ws, "overlay", str(folder)).returncode == 0, "overlay should exist before stale checkpoint-only gate")
        result = run_brain(ws, "session-gate", "--cwd", str(folder))
        assert_true(result.returncode == 2, f"stale checkpoint-only gate should return 2, got {result.returncode}")
        assert_true("Recommendation: `stale_new_session`" in result.stdout, "stale checkpoint-only gate should not recommend direct advisory")


def test_refresh_status_capabilities_include_memory_governance_summary() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-memory-refresh-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        assert_true(run_brain(ws, "memory-triage", "--window", "daily", "--root", str(ws)).returncode == 0, "daily triage should succeed")
        assert_true(run_brain(ws, "memory-triage", "--window", "weekly", "--root", str(ws)).returncode == 0, "weekly triage should succeed")
        refresh = run_brain(ws, "refresh")
        assert_true(refresh.returncode == 0, f"refresh after memory triage expected 0, got {refresh.returncode}, stderr={refresh.stderr}")
        registry = load_registry(ws)
        assert_true("memory_governance" in registry["checks"], "refresh should include memory_governance check")
        status_text = (ws / "contexts" / "system_status.md").read_text(encoding="utf-8")
        assert_true("## Memory Governance" in status_text, "status should include memory governance section")
        assert_true("Latest daily triage:" in status_text, "status should show latest daily triage")
        assert_true("Retrieval mode=`semantic-lite`" in status_text, "status should expose retrieval mode")
        capabilities = run_brain(ws, "capabilities")
        assert_true(capabilities.returncode == 0, "capabilities should succeed after memory triage")
        assert_true("Stale session threshold: `3 days`" in capabilities.stdout, "capabilities should report stale threshold")
        assert_true("Memory governance: `durable=" in capabilities.stdout, "capabilities should report memory governance counts")
        assert_true("Memory decay: `hot=" in capabilities.stdout, "capabilities should report memory decay counts")


def test_doctor_flags_stale_memory_governance_registry() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-memory-stale-registry-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        assert_true(run_brain(ws, "memory-triage", "--window", "daily", "--root", str(ws)).returncode == 0, "daily triage should succeed")
        assert_true(run_brain(ws, "memory-triage", "--window", "weekly", "--root", str(ws)).returncode == 0, "weekly triage should succeed")
        registry_path = ws / "contexts" / "memory_governance_registry.json"
        payload = json.loads(registry_path.read_text(encoding="utf-8"))
        payload["window_runs"]["daily"]["generated_at"] = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=2)).isoformat(timespec="seconds")
        payload["window_runs"]["weekly"]["generated_at"] = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=10)).isoformat(timespec="seconds")
        write_file(registry_path, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
        result = run_brain(ws, "doctor")
        assert_true(result.returncode == 2, f"doctor should degrade on stale memory governance, got {result.returncode}, stderr={result.stderr}")
        assert_true("stale_daily_memory_governance" in result.stdout or "stale_weekly_memory_governance" in result.stdout, "doctor should surface stale memory governance findings")


def test_refresh_flags_bridge_active_session_mismatch() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-memory-mismatch-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        state_dir = ws.parent / "external" / "vault" / "00_system" / "checkpoints" / ".state"
        write_file(state_dir / "codex_bridge_state.json", json.dumps({"session_id": "bridge-123"}, ensure_ascii=False) + "\n")
        write_file(state_dir / "active_session.json", json.dumps({"session_id": "active-456"}, ensure_ascii=False) + "\n")
        result = run_brain(ws, "refresh")
        assert_true(result.returncode == 2, f"mismatched bridge/active state should degrade refresh, got {result.returncode}")
        registry = load_registry(ws)
        findings = registry.get("findings", [])
        codes = {item.get("code") for item in findings if isinstance(item, dict)}
        assert_true("bridge_checkpoint_session_mismatch" in codes, "refresh should surface bridge/active mismatch finding")
        assert_true(registry["sources"]["memory"]["state_alignment"]["status"] == "degraded", "memory state alignment should be degraded when session ids diverge")


def test_refresh_accepts_carryover_linked_bridge_state() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-memory-carryover-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        state_dir = ws.parent / "external" / "vault" / "00_system" / "checkpoints" / ".state"
        write_file(state_dir / "codex_bridge_state.json", json.dumps({"session_id": "bridge-123"}, ensure_ascii=False) + "\n")
        write_file(
            state_dir / "active_session.json",
            json.dumps(
                {
                    "session_id": "active-456",
                    "last_summary": "Carry-over from bridge-123, previous_usage=0",
                    "handoff_anchor": "[[00_system/checkpoints/2026/02/example-bridge-123.md|carry-over]]",
                },
                ensure_ascii=False,
            )
            + "\n",
        )
        result = run_brain(ws, "refresh")
        assert_true(result.returncode == 0, f"carry-over-linked state should remain healthy, got {result.returncode}, stderr={result.stderr}")
        registry = load_registry(ws)
        assert_true(registry["sources"]["memory"]["state_alignment"]["status"] == "healthy", "carry-over-linked bridge state should be treated as healthy")
        assert_true(
            registry["sources"]["memory"]["state_alignment"]["relationship"] == "carry_over_linked",
            "carry-over-linked bridge state should expose the relationship for diagnostics",
        )


def test_reconcile_treats_memory_governance_artifacts_as_implemented() -> None:
    with tempfile.TemporaryDirectory(prefix="system-hub-memory-reconcile-") as tmp_s:
        ws = make_workspace(Path(tmp_s))
        assert_true(run_brain(ws, "memory-triage", "--window", "daily", "--root", str(ws)).returncode == 0, "daily triage should succeed before reconcile")
        result = run_brain(ws, "reconcile")
        assert_true(result.returncode == 0, f"reconcile after memory triage should stay 0, got {result.returncode}, stderr={result.stderr}")
        report = load_reconciliation_report(ws)
        assert_true("`contexts/memory_governance_registry.json` `evidence=runtime_writer`" in report, "memory governance registry should be runtime-writer integrated")
        assert_true("`contexts/memory_governance_status.md` `evidence=runtime_writer`" in report, "memory governance status should be runtime-writer integrated")


def main() -> int:
    tests = [
        test_refresh_success_writes_registry_and_status,
        test_degraded_skill_root_returns_2,
        test_degraded_vault_checkpoint_returns_2_in_doctor,
        test_invalid_toml_returns_1,
        test_status_reads_existing_registry_without_live_checks,
        test_missing_bridge_state_degrades_not_crash,
        test_refresh_does_not_write_outside_repo,
        test_intake_works_without_init_and_no_repo_write,
        test_intake_mode_detection_analysis_folder,
        test_intake_mode_detection_writing_folder,
        test_intake_mode_detection_meeting_folder,
        test_intake_surfaces_continuity_hint_from_runtime_memory,
        test_refresh_adds_candidate_skill_recommendation,
        test_capabilities_reports_new_commands_and_active_skills,
        test_capabilities_reports_runtime_versions_and_native_readiness,
        test_capabilities_do_not_require_desktop_origin_override_when_desktop_runtime_exists,
        test_refresh_surfaces_runtime_mismatch_as_action_not_failure,
        test_overlay_writes_brief_and_registry,
        test_bootstrap_creates_overlay_and_local_agent_for_project_like_folder,
        test_bootstrap_skips_local_agent_for_scratch_folder,
        test_bootstrap_preserves_existing_local_agent,
        test_bootstrap_warns_on_legacy_agent_filename,
        test_overlay_carries_forward_runtime_memory_context,
        test_closeout_requires_overlay_first,
        test_closeout_creates_open_proposal_for_candidate_skill,
        test_closeout_skips_existing_fallback_or_active_skill,
        test_closeout_records_unknown_skill_as_discovery_hint,
        test_skill_route_writes_workflow_registry,
        test_artifact_harness_writes_packet_chain,
        test_artifact_harness_refuses_rerun_without_force,
        test_artifact_harness_json_from_temp_cwd_writes_target_workspace,
        test_artifact_harness_lifecycle_status_mark_resume,
        test_artifact_harness_lifecycle_json_refusal_is_parseable,
        test_artifact_harness_replay_writes_evidence_and_preserves_markdown,
        test_artifact_harness_replay_json_refusal_is_parseable,
        test_artifact_harness_provenance_writes_ledger_and_preserves_markdown,
        test_artifact_harness_provenance_json_refusal_is_parseable,
        test_artifact_harness_provenance_refuses_manifest_packet_outside_target,
        test_artifact_harness_runtime_check_default_is_conservative,
        test_artifact_harness_runtime_check_json_refusal_is_parseable,
        test_artifact_harness_runtime_check_blocks_approval_gate_cli_conflict,
        test_artifact_harness_runtime_check_allows_cli_when_no_approval_gate_without_authorizing_execution,
        test_artifact_harness_runtime_check_refuses_manifest_packet_outside_target,
        test_artifact_harness_approval_records_evidence_and_preserves_markdown,
        test_artifact_harness_approval_latest_deny_overrides_earlier_approval,
        test_artifact_harness_runtime_invoke_refuses_readiness_blockers,
        test_artifact_harness_runtime_invoke_requires_approval_evidence,
        test_artifact_harness_runtime_invoke_forbids_cli_when_approval_gated,
        test_artifact_harness_runtime_invoke_dry_run_with_approval_filters_denied_capabilities,
        test_artifact_harness_runtime_invoke_latest_deny_blocks_invocation,
        test_artifact_harness_approval_and_runtime_invoke_missing_run_refusals_are_parseable,
        test_artifact_harness_runtime_invoke_refuses_manifest_packet_outside_target,
        test_artifact_harness_schema_check_current_run_and_missing_optional_reports,
        test_artifact_harness_migrate_safe_older_run_is_idempotent_and_preserves_markdown,
        test_artifact_harness_migrate_refuses_missing_required_packet,
        test_artifact_harness_schema_check_refuses_manifest_packet_outside_target,
        test_artifact_harness_repair_plan_writes_plan_and_preserves_markdown,
        test_artifact_harness_repair_plan_surfaces_blocked_lifecycle_and_denied_approval,
        test_artifact_harness_repair_plan_surfaces_runtime_invocation_refusal,
        test_artifact_harness_repair_plan_missing_run_refusal_is_parseable,
        test_artifact_harness_replay_refuses_manifest_packet_outside_target,
        test_artifact_harness_json_refuses_packet_root_outside_target_workspace,
        test_repo_does_not_carry_smoke_artifact_harness_outputs,
        test_packet_route_keyword_routes_to_artifact_harness,
        test_packet_route_natural_artifact_missions_are_create_ready,
        test_packet_route_roster_aliases_route_to_artifact_harness,
        test_packet_route_roster_quality_direction_is_plain_self_check,
        test_packet_route_roster_quality_attached_artifact_is_spec_first,
        test_packet_route_roster_visual_quality_loop_attaches_to_production,
        test_packet_route_roster_visual_quality_only_uses_quality_direction,
        test_packet_route_visual_cv_create_carries_request_into_packet_scaffolds,
        test_packet_route_pm_alias_requires_artifact_context,
        test_packet_route_underspecified_artifact_hint_refuses_create,
        test_packet_route_front_door_hr_artifact_is_spec_first,
        test_packet_route_front_door_hr_only_does_not_create_packets,
        test_packet_route_requirement_form_create_writes_packet_chain,
        test_packet_route_roster_create_from_temp_cwd_writes_target_workspace,
        test_packet_route_downstream_front_doors_are_spec_first_without_id,
        test_packet_route_short_alias_does_not_match_inside_words,
        test_packet_route_existing_id_routes_to_safe_existing_packet_command,
        test_packet_route_json_from_temp_cwd_uses_absolute_next_command,
        test_packet_route_create_json_refuses_packet_root_outside_target_workspace,
        test_packet_route_create_writes_artifact_harness_chain,
        test_packet_route_create_refuses_rerun_without_force,
        test_packet_route_non_artifact_phrase_does_not_route,
        test_roster_health_smoke_json_reports_missing_provider_and_target_packet_output,
        test_roster_health_provider_missing_auth_and_configured_auth_are_structured_without_secret_leak,
        test_roster_health_missing_target_json_refusal_is_parseable,
        test_roster_install_temp_codex_home_and_health_detects_skill,
        test_skill_route_gap_triggers_discovery,
        test_skill_route_uses_closeout_quality_signals,
        test_skill_review_lists_open_proposals,
        test_skill_promote_adds_skill_to_fallback_and_updates_status,
        test_skill_promote_is_idempotent_when_repeated,
        test_skill_reject_updates_status_without_work_mode_change,
        test_closeout_fails_on_invalid_registry_without_resetting_it,
        test_skill_promote_preserves_custom_work_mode_content,
        test_refresh_status_capabilities_and_reconcile_include_overlay_and_skill_iteration,
        test_reconcile_writes_report_only_and_preserves_canonical_outputs,
        test_reconcile_classifies_implemented_supporting_and_folder_only,
        test_reconcile_classifies_history_snapshots_as_archive,
        test_reconcile_exit_0_in_minimal_fully_referenced_fixture,
        test_memory_triage_daily_writes_registry_and_status,
        test_memory_triage_selected_count_zero_is_empty_not_error,
        test_memory_triage_repeated_report_folder_becomes_durable,
        test_memory_triage_report_only_becomes_summary_only,
        test_memory_triage_overlay_closeout_path_normalization_promotes_durable,
        test_memory_triage_without_report_or_repeat_becomes_archive_candidate,
        test_session_gate_fresh_thread_returns_0,
        test_session_gate_stale_thread_returns_2,
        test_session_gate_prefers_newest_timestamp_across_sqlite_and_index,
        test_session_gate_archived_thread_is_stale,
        test_session_gate_index_only_threads_are_conservative_stale,
        test_session_gate_missing_thread_returns_1,
        test_session_gate_without_thread_id_uses_checkpoint_linked_advisory,
        test_session_gate_without_thread_id_respects_stale_threshold,
        test_refresh_status_capabilities_include_memory_governance_summary,
        test_doctor_flags_stale_memory_governance_registry,
        test_refresh_flags_bridge_active_session_mismatch,
        test_refresh_accepts_carryover_linked_bridge_state,
        test_reconcile_treats_memory_governance_artifacts_as_implemented,
    ]
    for test in tests:
        test()
    print("system hub test harness checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
