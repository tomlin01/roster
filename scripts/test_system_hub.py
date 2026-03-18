#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import json
import os
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
