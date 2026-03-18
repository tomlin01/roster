#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import plistlib
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import tomllib
from collections import Counter
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG_PATH = ROOT / "policy" / "system_hub.toml"
DEFAULT_WORK_MODES_PATH = ROOT / "policy" / "work_modes.toml"
HUB_VERSION = "1.6.0"
OVERALL_STATES = {"healthy", "degraded", "failed"}
WORK_MODE_NAMES = ("analysis", "writing", "math_check", "meeting", "course")
MEMORY_TRIAGE_WINDOWS = {
    "daily": {"days": 14, "top": 3},
    "weekly": {"days": 30, "top": 5},
}
SESSION_STALE_DAYS = 3
MEMORY_DEFAULT_LANE = "default"
DEFAULT_BRAIN_COMMANDS = (
    "refresh",
    "doctor",
    "status",
    "bootstrap",
    "intake",
    "overlay",
    "closeout",
    "skill-route",
    "skill-discover",
    "skill-review",
    "skill-promote",
    "skill-reject",
    "memory-triage",
    "session-gate",
    "capabilities",
    "review-loop",
    "reconcile",
)
INTAKE_SCAN_LIMIT = 400
HIGH_CONFIDENCE_THRESHOLD = 0.58
IGNORED_SCAN_DIRS = {
    ".git",
    ".hg",
    ".svn",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "venv",
    "node_modules",
    ".idea",
    ".vscode",
}
DATA_EXTENSIONS = {".csv", ".tsv", ".xlsx", ".xls", ".parquet", ".feather", ".jsonl"}
OUTPUT_HINT_KEYWORDS = {
    "output",
    "outputs",
    "result",
    "results",
    "report",
    "reports",
    "summary",
    "draft",
    "figure",
    "figures",
    "analysis",
    "deliverable",
    "presentation",
    "slides",
}
ARTIFACT_EXTENSION_HINTS = {
    "video": {".mp4", ".mov", ".m4v", ".avi", ".mkv", ".webm"},
    "pdf": {".pdf"},
    "slides": {".ppt", ".pptx", ".key", ".odp"},
    "doc": {".doc", ".docx"},
    "spreadsheet": {".csv", ".tsv", ".xls", ".xlsx", ".parquet", ".feather"},
    "notebook": {".ipynb"},
    "image": {".png", ".jpg", ".jpeg", ".svg", ".gif", ".webp"},
    "markdown": {".md"},
    "code": {".py", ".r", ".jl", ".m", ".tex", ".js", ".ts", ".tsx", ".jsx", ".html", ".css"},
}
ARTIFACT_TERM_HINTS = {
    "video": {"video", "mp4", "mov", "movie", "clip", "lecture video", "animation"},
    "pdf": {"pdf", "paper pdf", "rendered pdf"},
    "slides": {"slides", "slide", "deck", "ppt", "pptx", "presentation"},
    "doc": {"doc", "docx", "document", "word"},
    "spreadsheet": {"sheet", "spreadsheet", "csv", "xlsx", "table", "dataset"},
    "notebook": {"notebook", "ipynb", "jupyter"},
    "image": {"image", "figure", "screenshot", "png", "jpg"},
    "markdown": {"markdown", "md", "note", "notes", "manuscript", "draft", "paper", "section", "citation"},
    "code": {"code", "script", "module", "function", "repo"},
}
SKILL_ARTIFACT_HINTS = {
    "video": {"video", "mp4", "mov", "movie", "clip", "ffmpeg", "youtube"},
    "pdf": {"pdf", "render pdf", "pdfplumber", "pypdf"},
    "slides": {"slides", "slide", "deck", "ppt", "pptx", "presentation", "reveal.js"},
    "doc": {"doc", "docx", "document", "word"},
    "spreadsheet": {"spreadsheet", "csv", "xlsx", "xls", "table", "dataset"},
    "notebook": {"jupyter", "ipynb", "notebook"},
    "image": {"image", "screenshot", "png", "jpg", "jpeg", "visual"},
    "markdown": {"markdown file", "obsidian", "wikilinks", "callouts", "frontmatter"},
    "code": {"repo", "code", "script", "module", "function", "test-driven", "refactor"},
}
INTENT_CORRECTION_TERMS = {
    "adjust",
    "correct",
    "correction",
    "debug",
    "diagnose",
    "fix",
    "issue",
    "overlap",
    "patch",
    "problem",
    "readability",
    "repair",
    "resolve",
    "校正",
    "修正",
    "重疊",
    "錯誤",
}
INTENT_QA_TERMS = {
    "check",
    "inspect",
    "qa",
    "review",
    "validate",
    "verification",
    "verify",
    "look for",
    "檢查",
    "確認",
    "驗證",
}
INTENT_CREATION_TERMS = {
    "author",
    "build",
    "compose",
    "create",
    "draft",
    "generate",
    "make",
    "produce",
    "write",
    "建立",
    "產生",
    "製作",
    "生成",
}
INTENT_TRANSFORM_TERMS = {
    "convert",
    "encode",
    "export",
    "format",
    "ingest",
    "normalize",
    "render",
    "transform",
    "轉換",
    "匯出",
    "渲染",
}
INTENT_PLANNING_TERMS = {"plan", "outline", "route", "router", "workflow", "strategy", "規劃"}
ROUTER_GENERIC_HELPER_SKILLS = {
    "verification-loop",
    "visual-explainer",
    "eval-harness",
}
ROUTER_QA_HELPER_SKILLS = {
    "verification-loop",
    "visual-explainer",
    "eval-harness",
}
ROUTER_PHASE_MISMATCH_TERMS = {
    "pipeline",
    "router",
    "planning",
    "planner",
    "runner",
    "download",
    "downloader",
    "creator",
    "generator",
    "writer",
    "deploy",
    "ingest",
    "install",
    "brainstorm",
}
LOCAL_AGENT_FILE_NAMES = ("AGENTS.md", "Agent.md")
BOOTSTRAP_SCRATCH_TOKENS = {"tmp", "temp", "scratch", "sandbox", "test", "drafts"}
BOOTSTRAP_PROJECT_DIR_HINTS = {
    ".git",
    "src",
    "scripts",
    "data",
    "dataset",
    "datasets",
    "paper",
    "real_data",
    "sections",
    "assets",
    "scenes",
    "slides",
    "web",
    "notebooks",
    "reference",
    "references",
    "lecture1",
    "figures",
    "figure",
    "results",
    "output",
    "outputs",
}
BOOTSTRAP_PROJECT_FILE_HINTS = {
    "readme.md",
    "pyproject.toml",
    "requirements.txt",
    "makefile",
    ".rprofile",
    ".gitignore",
}
POLICY_REQUIRED_FILES = (
    "GLOBAL_OPERATING_MODEL.md",
    "RESOURCE_TAXONOMY.md",
    "global_agent_defaults.json",
    "agent_contract_schema.json",
    "benchmark_case_schema.json",
    "benchmark_report_schema.json",
)
CONTEXT_REQUIRED_FILES = ("research.md", "writing.md", "review.md")
ARCHIVE_CONTEXT_PREFIXES = ("skill_py_", "skill_slim_", "codex_system_status_")
ARCHIVE_CONTEXT_TOKENS = ("skill_router_regression_harness",)
CONFIG_ENV_MAP = {
    ("workspace", "root"): "SYSTEM_HUB_WORKSPACE_ROOT",
    ("paths", "policy_dir"): "SYSTEM_HUB_POLICY_DIR",
    ("paths", "contexts_dir"): "SYSTEM_HUB_CONTEXTS_DIR",
    ("paths", "scripts_dir"): "SYSTEM_HUB_SCRIPTS_DIR",
    ("paths", "codex_home"): "SYSTEM_HUB_CODEX_HOME",
    ("paths", "skill_roots"): "SYSTEM_HUB_SKILL_ROOTS",
    ("paths", "vault_path"): "SYSTEM_HUB_VAULT_PATH",
    ("paths", "checkpoint_root"): "SYSTEM_HUB_CHECKPOINT_ROOT",
    ("paths", "bridge_state"): "SYSTEM_HUB_BRIDGE_STATE",
    ("paths", "active_session_state"): "SYSTEM_HUB_ACTIVE_SESSION_STATE",
    ("paths", "automation_root"): "SYSTEM_HUB_AUTOMATION_ROOT",
    ("freshness", "system_hours"): "SYSTEM_HUB_FRESHNESS_SYSTEM_HOURS",
    ("freshness", "generated_hours"): "SYSTEM_HUB_FRESHNESS_GENERATED_HOURS",
    ("freshness", "report_hours"): "SYSTEM_HUB_FRESHNESS_REPORT_HOURS",
}
DEFAULT_DESKTOP_APP_PATH = Path("/Applications/Codex.app")
DEFAULT_DESKTOP_CLI_PATH = DEFAULT_DESKTOP_APP_PATH / "Contents/Resources/codex"
DEFAULT_DESKTOP_INFO_PLIST = DEFAULT_DESKTOP_APP_PATH / "Contents/Info.plist"
SEMVER_CORE_RE = re.compile(r"(\d+)\.(\d+)\.(\d+)")


class ConfigError(RuntimeError):
    pass


class HubRuntimeError(RuntimeError):
    pass


@dataclass(frozen=True)
class HubConfig:
    config_path: Path
    workspace_root: Path
    policy_dir: Path
    contexts_dir: Path
    scripts_dir: Path
    codex_home: Path
    skill_roots: tuple[Path, ...]
    vault_path: Path
    checkpoint_root: Path
    bridge_state: Path
    active_session_state: Path
    automation_root: Path
    codex_ckpt_cmd: Path | None
    session_ckpt_cmd: Path | None
    system_hours: int
    generated_hours: int
    report_hours: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "config_path": str(self.config_path),
            "workspace": {"root": str(self.workspace_root)},
            "paths": {
                "policy_dir": str(self.policy_dir),
                "contexts_dir": str(self.contexts_dir),
                "scripts_dir": str(self.scripts_dir),
                "codex_home": str(self.codex_home),
                "skill_roots": [str(path) for path in self.skill_roots],
                "vault_path": str(self.vault_path),
                "checkpoint_root": str(self.checkpoint_root),
                "bridge_state": str(self.bridge_state),
                "active_session_state": str(self.active_session_state),
                "automation_root": str(self.automation_root),
            },
            "freshness": {
                "system_hours": self.system_hours,
                "generated_hours": self.generated_hours,
                "report_hours": self.report_hours,
            },
        }


@dataclass(frozen=True)
class WorkMode:
    name: str
    extensions: tuple[str, ...]
    keywords: tuple[str, ...]
    path_keywords: tuple[str, ...]
    active_skills: tuple[str, ...]
    fallback_skills: tuple[str, ...]
    output_contract: tuple[str, ...]
    session_preamble: str
    escalation_triggers: tuple[str, ...]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Workspace coordination and refresh hub.")
    parser.add_argument(
        "--config",
        default=os.getenv("SYSTEM_HUB_CONFIG", str(DEFAULT_CONFIG_PATH)),
        help="Path to the repo-local system hub TOML config.",
    )
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("refresh", help="Run live checks, regenerate canonical outputs, and write status artifacts.")
    sub.add_parser("doctor", help="Run live checks without writing repo-tracked outputs.")
    sub.add_parser("status", help="Read the existing canonical status outputs without live checks.")
    bootstrap = sub.add_parser("bootstrap", help="Initialize a working folder with overlay context and optional local AGENTS scaffolding.")
    bootstrap.add_argument("path", nargs="?", default=".", help="Folder to bootstrap. Defaults to the current directory.")
    bootstrap.add_argument(
        "--write-agent",
        choices=("auto", "always", "never"),
        default="auto",
        help="Whether to write a minimal local AGENTS.md. `auto` writes only for project-like folders.",
    )
    bootstrap.add_argument("--thread-id", default=None, help="Optional Codex thread identifier used for session-gate advice.")
    bootstrap.add_argument("--cwd", default=None, help="Optional cwd override used for session-gate advice.")
    intake = sub.add_parser("intake", help="Scan a folder, predict the working mode, and suggest the next step.")
    intake.add_argument("path", nargs="?", default=".", help="Folder to inspect. Defaults to the current directory.")
    overlay = sub.add_parser("overlay", help="Generate a runtime overlay brief for a working folder.")
    overlay.add_argument("path", nargs="?", default=".", help="Folder to inspect. Defaults to the current directory.")
    closeout = sub.add_parser("closeout", help="Record task closeout notes and generate candidate skill proposals.")
    closeout.add_argument("path", nargs="?", default=".", help="Folder whose overlay brief should be used.")
    closeout.add_argument("--summary", required=True, help="Short task summary for the closeout artifact.")
    closeout.add_argument(
        "--used-skills",
        default="",
        help="Comma-separated installed skills used during the task. Candidate skills may generate proposals.",
    )
    closeout.add_argument(
        "--outcome",
        choices=("success", "partial", "fail"),
        default="partial",
        help="How well the skill-assisted workflow worked overall. Only successful reusable runs open promotion proposals.",
    )
    closeout.add_argument(
        "--reuse",
        choices=("yes", "no"),
        default="no",
        help="Whether you would reuse the same skill-assisted workflow again for this mode.",
    )
    route = sub.add_parser("skill-route", help="Plan a quality-aware skill workflow for the current task and folder.")
    route.add_argument("task", help="Task description used to plan the skill workflow.")
    route.add_argument("--path", default=".", help="Folder to route against. Defaults to the current directory.")
    discover = sub.add_parser("skill-discover", help="Search installed skills first, then optionally query remote skill catalogs.")
    discover.add_argument("query", help="Discovery query, capability gap, or workflow need to search for.")
    sub.add_parser("skill-review", help="List open skill proposals produced by closeout.")
    promote = sub.add_parser("skill-promote", help="Promote an open proposal into the mode's fallback lane.")
    promote.add_argument("proposal_id", help="Proposal identifier from skill-review.")
    reject = sub.add_parser("skill-reject", help="Reject an open skill proposal without changing work modes.")
    reject.add_argument("proposal_id", help="Proposal identifier from skill-review.")
    reject.add_argument("--reason", required=True, help="Why the proposal is being rejected.")
    memory_triage = sub.add_parser("memory-triage", help="Run memory triage on recent-memory output and write governance artifacts.")
    memory_triage.add_argument("--window", choices=tuple(MEMORY_TRIAGE_WINDOWS.keys()), required=True, help="Window preset to evaluate.")
    memory_triage.add_argument("--root", default=None, help="Optional root path passed to session_ckpt recent-memory.")
    session_gate = sub.add_parser("session-gate", help="Advise whether a thread should resume directly or start fresh with summary.")
    session_gate.add_argument("--thread-id", default=None, help="Codex thread identifier to evaluate.")
    session_gate.add_argument("--cwd", default=None, help="Optional override cwd used to find a matching runtime overlay.")
    sub.add_parser("capabilities", help="Show the currently available hub capabilities and active skill lanes.")
    review_loop = sub.add_parser("review-loop", help="Build a repo-native iteration packet for the review-fix-adjust-loop skill.")
    review_loop.add_argument("--path", default=".", help="Workspace to inspect. Defaults to the current directory.")
    review_loop.add_argument("--changed", nargs="*", default=[], help="Explicit changed files, relative or absolute.")
    review_loop.add_argument("--from-git", action="store_true", help="Infer changed files from git status when none are supplied.")
    review_loop.add_argument("--max-candidates", type=int, default=20, help="Maximum impacted candidates to consider.")
    review_loop.add_argument("--review-limit", type=int, default=8, help="Maximum files in the first review scope.")
    review_loop.add_argument("--json", action="store_true", help="Emit the raw iteration packet JSON.")
    sub.add_parser("reconcile", help="Scan this folder for system artifacts that are or are not integrated into the hub.")
    return parser.parse_args()


def load_config(config_path: Path) -> HubConfig:
    if not config_path.exists():
        raise ConfigError(f"Config not found: {config_path}")
    try:
        data = tomllib.loads(config_path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as exc:
        raise ConfigError(f"Invalid TOML in {config_path}: {exc}") from exc

    workspace = require_section(data, "workspace")
    paths = require_section(data, "paths")
    freshness = require_section(data, "freshness")

    config_base = config_path.parent.resolve()
    workspace_root = resolve_workspace_root(workspace.get("root"), config_base)

    policy_dir = resolve_path(workspace_root, with_override("paths", paths, "policy_dir"))
    contexts_dir = resolve_path(workspace_root, with_override("paths", paths, "contexts_dir"))
    scripts_dir = resolve_path(workspace_root, with_override("paths", paths, "scripts_dir"))
    codex_home = resolve_external_path(with_override("paths", paths, "codex_home"))
    skill_roots = tuple(resolve_external_path(item) for item in load_skill_roots(paths))
    vault_path = resolve_external_path(with_override("paths", paths, "vault_path"))
    checkpoint_root = resolve_external_path(with_override("paths", paths, "checkpoint_root"))
    bridge_state = resolve_external_path(with_override("paths", paths, "bridge_state"))
    active_session_state = resolve_external_path(with_override("paths", paths, "active_session_state"))
    automation_root = resolve_external_path(with_override("paths", paths, "automation_root"))
    codex_ckpt_cmd = optional_external_path(paths.get("codex_ckpt_cmd"))
    session_ckpt_cmd = optional_external_path(paths.get("session_ckpt_cmd"))

    system_hours = parse_positive_int(with_override("freshness", freshness, "system_hours"), "freshness.system_hours")
    generated_hours = parse_positive_int(with_override("freshness", freshness, "generated_hours"), "freshness.generated_hours")
    report_hours = parse_positive_int(with_override("freshness", freshness, "report_hours"), "freshness.report_hours")

    return HubConfig(
        config_path=config_path.resolve(),
        workspace_root=workspace_root,
        policy_dir=policy_dir,
        contexts_dir=contexts_dir,
        scripts_dir=scripts_dir,
        codex_home=codex_home,
        skill_roots=skill_roots,
        vault_path=vault_path,
        checkpoint_root=checkpoint_root,
        bridge_state=bridge_state,
        active_session_state=active_session_state,
        automation_root=automation_root,
        codex_ckpt_cmd=codex_ckpt_cmd,
        session_ckpt_cmd=session_ckpt_cmd,
        system_hours=system_hours,
        generated_hours=generated_hours,
        report_hours=report_hours,
    )


def require_section(data: dict[str, Any], key: str) -> dict[str, Any]:
    section = data.get(key)
    if not isinstance(section, dict):
        raise ConfigError(f"Missing required config section: {key}")
    return section


def resolve_workspace_root(raw: Any, config_base: Path) -> Path:
    env_value = os.getenv(CONFIG_ENV_MAP[("workspace", "root")])
    if env_value:
        raw = env_value
    if not isinstance(raw, str) or not raw.strip():
        raise ConfigError("workspace.root must be a non-empty string")
    return (config_base / raw).expanduser().resolve()


def with_override(section_name: str, section: dict[str, Any], key: str) -> Any:
    env_name = CONFIG_ENV_MAP[(section_name, key)]
    env_value = os.getenv(env_name)
    if env_value is not None:
        return env_value
    if key not in section:
        raise ConfigError(f"Missing required config field: {section_name}.{key}")
    return section[key]


def load_skill_roots(paths: dict[str, Any]) -> list[str]:
    raw = with_override("paths", paths, "skill_roots")
    if isinstance(raw, str):
        roots = [item for item in raw.split(os.pathsep) if item.strip()]
        if not roots:
            raise ConfigError("paths.skill_roots env override must include at least one root")
        return roots
    if not isinstance(raw, list) or not raw:
        raise ConfigError("paths.skill_roots must be a non-empty array")
    if not all(isinstance(item, str) and item.strip() for item in raw):
        raise ConfigError("paths.skill_roots must contain non-empty strings")
    return raw


def resolve_path(workspace_root: Path, raw: Any) -> Path:
    if not isinstance(raw, str) or not raw.strip():
        raise ConfigError("Expected a non-empty path string")
    candidate = Path(raw).expanduser()
    if candidate.is_absolute():
        return candidate.resolve()
    return (workspace_root / candidate).resolve()


def resolve_external_path(raw: Any) -> Path:
    if not isinstance(raw, str) or not raw.strip():
        raise ConfigError("Expected a non-empty external path string")
    return Path(raw).expanduser().resolve()


def optional_external_path(raw: Any) -> Path | None:
    if raw is None:
        return None
    if not isinstance(raw, str) or not raw.strip():
        raise ConfigError("Optional external path values must be non-empty strings")
    return Path(raw).expanduser().resolve()


def parse_positive_int(raw: Any, label: str) -> int:
    try:
        value = int(raw)
    except (TypeError, ValueError) as exc:
        raise ConfigError(f"{label} must be an integer") from exc
    if value <= 0:
        raise ConfigError(f"{label} must be > 0")
    return value


def default_work_mode_spec() -> dict[str, Any]:
    return {
        "mode": {
            "analysis": {
                "file_hints": {
                    "extensions": [".csv", ".tsv", ".xlsx", ".xls", ".parquet", ".ipynb", ".jsonl"],
                    "keywords": ["analysis", "dataset", "results", "model", "stat", "quality", "品保"],
                    "path_keywords": ["data", "dataset", "analysis", "results", "tables"],
                },
                "active_skills": ["spreadsheet", "xlsx", "polars", "statsmodels", "statistical-analysis"],
                "fallback_skills": ["scikit-learn", "scikit-survival", "matplotlib"],
                "output_contract": [
                    "State dataset assumptions and changed inputs explicitly.",
                    "Prefer concise statistical wording over ornate vocabulary.",
                    "Keep steps reproducible and scoped to the current dataset version.",
                ],
                "session_preamble": "Operate as an analysis-focused session. Prefer continuity over redesign, and keep the current dataset version explicit.",
                "escalation_triggers": [
                    "Method changes would break comparability with prior dataset versions.",
                    "The folder looks like a new dataset drop for an existing recurring pipeline.",
                    "The requested output would change the established analysis deliverable format.",
                ],
            },
            "writing": {
                "file_hints": {
                    "extensions": [".md", ".pdf", ".docx", ".tex", ".bib"],
                    "keywords": ["draft", "paper", "manuscript", "section", "outline", "writing", "review"],
                    "path_keywords": ["draft", "paper", "writing", "sections", "citations"],
                },
                "active_skills": ["research-assistant", "citation-management", "content-research-writer", "internal-comms"],
                "fallback_skills": ["draft-polisher", "humanizer", "obsidian-markdown"],
                "output_contract": [
                    "Use plain academic wording and avoid rare or showy vocabulary.",
                    "Keep claims close to the available source material.",
                    "Prefer short, easy-to-scan paragraphs and explicit next edits.",
                ],
                "session_preamble": "Operate as a writing session. Keep wording plain, keep claims close to sources, and prefer concrete revision steps over stylistic drift.",
                "escalation_triggers": [
                    "The request needs new sources or evidence that the current folder does not contain.",
                    "The requested writing voice conflicts with the current academic/plain-language contract.",
                    "The draft appears to belong to another paper or workspace and may need a separate session.",
                ],
            },
            "math_check": {
                "file_hints": {
                    "extensions": [".tex", ".ipynb", ".md", ".pdf", ".png", ".jpg"],
                    "keywords": ["math", "proof", "derivation", "equation", "kernel", "vis_math"],
                    "path_keywords": ["math", "derivation", "figures", "proofs"],
                },
                "active_skills": ["statistical-analysis", "statsmodels", "matplotlib", "verification-loop"],
                "fallback_skills": ["networkx", "research-assistant"],
                "output_contract": [
                    "Prefer checkable derivation steps over long prose.",
                    "Make notation explicit and verify what is visible on the page.",
                    "Call out mismatches between equations, figures, and text directly.",
                ],
                "session_preamble": "Operate as a math-check session. Favor explicit derivations, notation checks, and visible-page verification over narrative explanation.",
                "escalation_triggers": [
                    "Notation is inconsistent across equations, figures, or surrounding prose.",
                    "The request needs proof-level rigor beyond the visible derivation context.",
                    "A figure or rendered page appears inconsistent with the mathematical statement.",
                ],
            },
            "meeting": {
                "file_hints": {
                    "extensions": [".md", ".pdf", ".docx", ".pptx"],
                    "keywords": ["meeting", "agenda", "minutes", "prof", "conference", "admin"],
                    "path_keywords": ["meeting", "minutes", "agenda", "conference"],
                },
                "active_skills": ["obsidian-markdown", "internal-comms", "research-assistant"],
                "fallback_skills": ["docx", "pptx"],
                "output_contract": [
                    "Capture decisions, owners, and next steps explicitly.",
                    "Keep equations in math syntax: inline `$...$`, block `$$...$$`.",
                    "Separate factual notes from your interpretation.",
                ],
                "session_preamble": "Operate as a meeting session. Separate facts from interpretation and keep decisions, owners, and next steps explicit.",
                "escalation_triggers": [
                    "The note mixes multiple meetings or agendas that should be split.",
                    "Action items are missing owners or deadlines.",
                    "Math or technical notation is being written as code spans instead of TeX.",
                ],
            },
            "course": {
                "file_hints": {
                    "extensions": [".md", ".pdf", ".ipynb", ".pptx", ".docx"],
                    "keywords": ["course", "lecture", "class", "homework", "assignment", "machinelearning"],
                    "path_keywords": ["course", "lecture", "homework", "assignment", "syllabus"],
                },
                "active_skills": ["obsidian-markdown", "jupyter-notebook", "research-assistant", "spreadsheet"],
                "fallback_skills": ["docx", "pptx", "content-research-writer"],
                "output_contract": [
                    "Keep lecture notes, assignments, and references distinct.",
                    "Use `$...$` and `$$...$$` for math; never backticks for equations.",
                    "Summaries should preserve definitions, assumptions, and unresolved questions.",
                ],
                "session_preamble": "Operate as a course session. Keep lecture content, assignments, and references separate, and preserve unresolved questions explicitly.",
                "escalation_triggers": [
                    "Lecture notes, homework, and reference material are collapsing into one undifferentiated note.",
                    "Equation formatting is being mixed with code formatting.",
                    "The request spans multiple courses or semesters and should be split.",
                ],
            },
        },
        "inventory": {
            "cold_skills": [
                "competitive-ads-extractor",
                "domain-name-brainstormer",
                "raffle-winner-picker",
                "slack-gif-creator",
                "twitter-algorithm-optimizer",
                "youtube-downloader",
            ]
        },
    }


def load_work_modes(config: HubConfig) -> tuple[dict[str, WorkMode], dict[str, Any], list[dict[str, str]]]:
    defaults = default_work_mode_spec()
    modes_path = config.policy_dir / "work_modes.toml"
    findings: list[dict[str, str]] = []
    source = "policy_file"
    raw_data: dict[str, Any] = {}

    if modes_path.exists():
        try:
            raw_data = tomllib.loads(modes_path.read_text(encoding="utf-8"))
        except tomllib.TOMLDecodeError as exc:
            source = "built_in_fallback"
            findings.append(
                warning("policy", "invalid_work_modes", f"Invalid work_modes.toml; using built-in defaults ({exc})", modes_path)
            )
    else:
        source = "built_in_fallback"
        findings.append(warning("policy", "missing_work_modes", "Missing work_modes.toml; using built-in defaults", modes_path))

    raw_mode_section = raw_data.get("mode") if isinstance(raw_data.get("mode"), dict) else {}
    raw_inventory = raw_data.get("inventory") if isinstance(raw_data.get("inventory"), dict) else {}

    cold_skills = coerce_string_list(raw_inventory.get("cold_skills"), "inventory.cold_skills")
    if cold_skills is None:
        cold_skills = list(defaults["inventory"]["cold_skills"])
        if raw_inventory:
            findings.append(
                warning("policy", "invalid_cold_skills", "Invalid inventory.cold_skills; using built-in defaults", modes_path)
            )

    modes: dict[str, WorkMode] = {}
    default_modes = defaults["mode"]
    for name in WORK_MODE_NAMES:
        default_entry = default_modes[name]
        raw_entry = raw_mode_section.get(name)
        if raw_entry is None:
            if modes_path.exists():
                findings.append(warning("policy", "missing_work_mode", f"Missing work mode definition: {name}", modes_path))
            raw_entry = {}
        if not isinstance(raw_entry, dict):
            findings.append(warning("policy", "invalid_work_mode", f"Invalid work mode definition: {name}", modes_path))
            raw_entry = {}
        file_hints = raw_entry.get("file_hints")
        if not isinstance(file_hints, dict):
            if "file_hints" in raw_entry:
                findings.append(warning("policy", "invalid_file_hints", f"Invalid file_hints for mode: {name}", modes_path))
            file_hints = {}

        extensions = coerce_string_list(file_hints.get("extensions"), f"mode.{name}.file_hints.extensions")
        keywords = coerce_string_list(file_hints.get("keywords"), f"mode.{name}.file_hints.keywords")
        path_keywords = coerce_string_list(file_hints.get("path_keywords"), f"mode.{name}.file_hints.path_keywords")
        active_skills = coerce_string_list(raw_entry.get("active_skills"), f"mode.{name}.active_skills")
        fallback_skills = coerce_string_list(raw_entry.get("fallback_skills"), f"mode.{name}.fallback_skills")
        output_contract = coerce_string_list(raw_entry.get("output_contract"), f"mode.{name}.output_contract")
        session_preamble = coerce_string(raw_entry.get("session_preamble"), f"mode.{name}.session_preamble")
        escalation_triggers = coerce_string_list(raw_entry.get("escalation_triggers"), f"mode.{name}.escalation_triggers")

        if extensions is None:
            extensions = list(default_entry["file_hints"]["extensions"])
            if "extensions" in file_hints:
                findings.append(
                    warning("policy", "invalid_mode_field", f"Invalid extensions for mode: {name}; using defaults", modes_path)
                )
        if keywords is None:
            keywords = list(default_entry["file_hints"]["keywords"])
            if "keywords" in file_hints:
                findings.append(
                    warning("policy", "invalid_mode_field", f"Invalid keywords for mode: {name}; using defaults", modes_path)
                )
        if path_keywords is None:
            path_keywords = list(default_entry["file_hints"]["path_keywords"])
            if "path_keywords" in file_hints:
                findings.append(
                    warning("policy", "invalid_mode_field", f"Invalid path keywords for mode: {name}; using defaults", modes_path)
                )
        if active_skills is None:
            active_skills = list(default_entry["active_skills"])
            if "active_skills" in raw_entry:
                findings.append(
                    warning("policy", "invalid_mode_field", f"Invalid active_skills for mode: {name}; using defaults", modes_path)
                )
        if fallback_skills is None:
            fallback_skills = list(default_entry["fallback_skills"])
            if "fallback_skills" in raw_entry:
                findings.append(
                    warning("policy", "invalid_mode_field", f"Invalid fallback_skills for mode: {name}; using defaults", modes_path)
                )
        if output_contract is None:
            output_contract = list(default_entry["output_contract"])
            if "output_contract" in raw_entry:
                findings.append(
                    warning("policy", "invalid_mode_field", f"Invalid output_contract for mode: {name}; using defaults", modes_path)
                )
        if session_preamble is None:
            session_preamble = default_entry["session_preamble"]
            if "session_preamble" in raw_entry:
                findings.append(
                    warning("policy", "invalid_mode_field", f"Invalid session_preamble for mode: {name}; using defaults", modes_path)
                )
        if escalation_triggers is None:
            escalation_triggers = list(default_entry["escalation_triggers"])
            if "escalation_triggers" in raw_entry:
                findings.append(
                    warning("policy", "invalid_mode_field", f"Invalid escalation_triggers for mode: {name}; using defaults", modes_path)
                )

        modes[name] = WorkMode(
            name=name,
            extensions=tuple(normalize_extension(value) for value in extensions),
            keywords=tuple(normalize_token(value) for value in keywords),
            path_keywords=tuple(normalize_token(value) for value in path_keywords),
            active_skills=tuple(normalize_skill_name(value) for value in active_skills),
            fallback_skills=tuple(normalize_skill_name(value) for value in fallback_skills),
            output_contract=tuple(value.strip() for value in output_contract if value.strip()),
            session_preamble=session_preamble.strip(),
            escalation_triggers=tuple(value.strip() for value in escalation_triggers if value.strip()),
        )

    metadata = {
        "path": str(modes_path),
        "exists": modes_path.exists(),
        "source": source,
        "status": "healthy" if not findings else "degraded",
        "mode_names": list(modes.keys()),
        "cold_skills": sorted({normalize_skill_name(value) for value in cold_skills}),
    }
    return modes, metadata, findings


def coerce_string_list(raw: Any, _label: str) -> list[str] | None:
    if raw is None:
        return None
    if not isinstance(raw, list):
        return None
    values: list[str] = []
    for item in raw:
        if not isinstance(item, str) or not item.strip():
            return None
        values.append(item.strip())
    return values


def coerce_string(raw: Any, _label: str) -> str | None:
    if raw is None:
        return None
    if not isinstance(raw, str) or not raw.strip():
        return None
    return raw.strip()


def normalize_extension(value: str) -> str:
    value = value.strip().lower()
    if not value:
        return value
    return value if value.startswith(".") else f".{value}"


def normalize_token(value: str) -> str:
    return value.strip().lower()


def normalize_skill_name(value: str) -> str:
    return value.strip().strip("/")


def canonical_artifact_paths(config: HubConfig) -> dict[str, Path]:
    return {
        "agent_benchmark_json": config.contexts_dir / "agent_benchmark_baseline_workspace.json",
        "agent_benchmark_md": config.contexts_dir / "agent_benchmark_baseline_workspace.md",
        "agent_benchmark_global_json": config.contexts_dir / "agent_benchmark_baseline_global.json",
        "agent_benchmark_global_md": config.contexts_dir / "agent_benchmark_baseline_global.md",
        "router_regression_json": config.contexts_dir / "router_regression_latest.json",
        "skill_graph_md": config.contexts_dir / "skill_graph.md",
        "system_registry_json": config.contexts_dir / "system_registry.json",
        "system_status_md": config.contexts_dir / "system_status.md",
    }


def reconciliation_report_path(config: HubConfig) -> Path:
    return config.contexts_dir / "folder_hub_reconciliation.md"


def runtime_overlay_registry_path(config: HubConfig) -> Path:
    return config.contexts_dir / "runtime_overlay_registry.json"


def runtime_overlays_dir(config: HubConfig) -> Path:
    return config.contexts_dir / "runtime_overlays"


def skill_iteration_registry_path(config: HubConfig) -> Path:
    return config.contexts_dir / "skill_iteration_registry.json"


def skill_discovery_registry_path(config: HubConfig) -> Path:
    return config.contexts_dir / "skill_discovery_registry.json"


def skill_route_registry_path(config: HubConfig) -> Path:
    return config.contexts_dir / "skill_route_registry.json"


def skill_iteration_closeouts_dir(config: HubConfig) -> Path:
    return config.contexts_dir / "skill_iterations" / "closeouts"


def skill_iteration_proposals_dir(config: HubConfig) -> Path:
    return config.contexts_dir / "skill_iterations" / "proposals"


def memory_governance_registry_path(config: HubConfig) -> Path:
    return config.contexts_dir / "memory_governance_registry.json"


def memory_governance_status_path(config: HubConfig) -> Path:
    return config.contexts_dir / "memory_governance_status.md"


def codex_session_index_path(config: HubConfig) -> Path:
    return config.codex_home / "session_index.jsonl"


def codex_state_db_path(config: HubConfig) -> Path:
    return config.codex_home / "state_5.sqlite"


def overlay_target_slug(config: HubConfig, target: Path) -> str:
    try:
        raw = target.resolve().relative_to(config.workspace_root.resolve()).as_posix()
    except ValueError:
        raw = target.resolve().as_posix()
    slug = re.sub(r"[^a-z0-9]+", "-", raw.lower()).strip("-")
    if not slug:
        slug = "target"
    digest = hashlib.sha1(str(target.resolve()).encode("utf-8")).hexdigest()[:8]
    return f"{slug}-{digest}"


def new_record_id(prefix: str) -> str:
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d%H%M%S")
    digest = hashlib.sha1(f"{prefix}:{dt.datetime.now(dt.timezone.utc).isoformat(timespec='microseconds')}".encode("utf-8")).hexdigest()[:8]
    return f"{prefix}-{stamp}-{digest}"


def default_runtime_overlay_registry() -> dict[str, Any]:
    return {"schema_version": 1, "generated_at": None, "entries": []}


def default_skill_iteration_registry() -> dict[str, Any]:
    return {"schema_version": 1, "generated_at": None, "closeouts": [], "proposals": []}


def default_skill_discovery_registry() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "generated_at": None,
        "last_query": None,
        "status": "unknown",
        "local_matches": [],
        "remote_matches": [],
        "warnings": [],
    }


def default_skill_route_registry() -> dict[str, Any]:
    return {"schema_version": 1, "generated_at": None, "entries": []}


def load_json_file(path: Path, default: dict[str, Any]) -> dict[str, Any]:
    if not path.exists():
        return json.loads(json.dumps(default))
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return json.loads(json.dumps(default))


def load_json_file_strict(path: Path, default: dict[str, Any], label: str) -> dict[str, Any]:
    if not path.exists():
        return json.loads(json.dumps(default))
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise HubRuntimeError(f"Invalid {label} JSON: {path} ({exc})") from exc
    if not isinstance(payload, dict):
        raise HubRuntimeError(f"Invalid {label} payload: {path} must contain a JSON object.")
    return payload


def dump_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def default_memory_governance_registry() -> dict[str, Any]:
    return {
        "generated_at": None,
        "stale_session_days": SESSION_STALE_DAYS,
        "retrieval_mode": "semantic-lite",
        "window_runs": {"daily": None, "weekly": None},
        "durable_count": 0,
        "summary_only_count": 0,
        "archive_candidate_count": 0,
        "hot_count": 0,
        "warm_count": 0,
        "cool_count": 0,
        "entries": [],
    }


def parse_datetime_any(raw: Any) -> dt.datetime | None:
    if raw is None:
        return None
    if isinstance(raw, (int, float)):
        return dt.datetime.fromtimestamp(float(raw), tz=dt.timezone.utc)
    if not isinstance(raw, str) or not raw.strip():
        return None
    text = raw.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = dt.datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=dt.timezone.utc)
    return parsed.astimezone(dt.timezone.utc)


def canonicalize_path_text(raw: Any) -> str | None:
    if not isinstance(raw, str) or not raw.strip():
        return None
    try:
        return str(Path(raw).expanduser().resolve())
    except OSError:
        return str(Path(raw).expanduser())


def iso_utc(raw: Any) -> str | None:
    parsed = parse_datetime_any(raw)
    if parsed is None:
        return None
    return parsed.isoformat(timespec="seconds")


def age_hours(parsed: dt.datetime | None, *, now: dt.datetime | None = None) -> float | None:
    if parsed is None:
        return None
    current = now or dt.datetime.now(dt.timezone.utc)
    return max(0.0, (current - parsed).total_seconds() / 3600.0)


def parse_codex_cli_version(raw: str) -> str | None:
    text = raw.strip()
    if not text:
        return None
    match = re.search(r"codex-cli\s+([^\s]+)", text)
    if match:
        return match.group(1).strip()
    return text.splitlines()[0].strip() or None


def semver_core(version: str | None) -> tuple[int, int, int] | None:
    if not version:
        return None
    match = SEMVER_CORE_RE.search(version)
    if not match:
        return None
    return tuple(int(part) for part in match.groups())


def version_at_least(version: str | None, minimum: str) -> bool:
    current = semver_core(version)
    floor = semver_core(minimum)
    if current is None or floor is None:
        return False
    return current >= floor


def read_codex_cli_version(path: Path | None) -> str | None:
    if path is None or not path.exists():
        return None
    try:
        proc = subprocess.run([str(path), "--version"], capture_output=True, text=True, check=False)
    except OSError:
        return None
    output = proc.stdout or proc.stderr
    return parse_codex_cli_version(output)


def read_desktop_app_version(path: Path | None) -> str | None:
    if path is None or not path.exists():
        return None
    try:
        with path.open("rb") as handle:
            payload = plistlib.load(handle)
    except (OSError, ValueError, plistlib.InvalidFileException):
        return None
    value = payload.get("CFBundleShortVersionString")
    return str(value).strip() if value else None


def discover_runtime_environment(origin: str) -> dict[str, Any]:
    shell_path_raw = os.getenv("CODEX_RUNTIME_SHELL_PATH_OVERRIDE") or shutil.which("codex")
    shell_path = Path(shell_path_raw).expanduser() if shell_path_raw else None
    desktop_app_path_raw = os.getenv("CODEX_RUNTIME_DESKTOP_APP_PATH_OVERRIDE") or str(DEFAULT_DESKTOP_APP_PATH)
    desktop_app_path = Path(desktop_app_path_raw).expanduser()
    desktop_cli_path_raw = os.getenv("CODEX_RUNTIME_DESKTOP_PATH_OVERRIDE") or str(DEFAULT_DESKTOP_CLI_PATH)
    desktop_cli_path = Path(desktop_cli_path_raw).expanduser()
    desktop_info_path_raw = os.getenv("CODEX_RUNTIME_DESKTOP_INFO_OVERRIDE") or str(desktop_app_path / "Contents/Info.plist")
    desktop_info_path = Path(desktop_info_path_raw).expanduser()

    shell_version = os.getenv("CODEX_RUNTIME_SHELL_VERSION_OVERRIDE") or read_codex_cli_version(shell_path)
    desktop_cli_version = os.getenv("CODEX_RUNTIME_DESKTOP_VERSION_OVERRIDE") or read_codex_cli_version(desktop_cli_path)
    desktop_app_version = os.getenv("CODEX_RUNTIME_DESKTOP_APP_VERSION_OVERRIDE") or read_desktop_app_version(desktop_info_path)

    gui_origin = "desktop" in origin.lower()
    preferred_runtime = "desktop_bundled" if gui_origin and desktop_cli_version else "shell_cli" if shell_version else "unknown"
    preferred_version = desktop_cli_version if preferred_runtime == "desktop_bundled" else shell_version
    alignment_status = "unknown"
    if shell_version and desktop_cli_version:
        alignment_status = "aligned" if shell_version == desktop_cli_version else "mismatch"
    elif desktop_cli_version:
        alignment_status = "desktop_only"
    elif shell_version:
        alignment_status = "shell_only"

    hooks_ready = version_at_least(preferred_version, "0.114.0")
    return {
        "preferred_runtime": preferred_runtime,
        "alignment_status": alignment_status,
        "shell_cli": {
            "path": str(shell_path) if shell_path else None,
            "exists": bool(shell_path and shell_path.exists()),
            "version": shell_version,
        },
        "desktop_runtime": {
            "app_path": str(desktop_app_path),
            "app_exists": desktop_app_path.exists(),
            "app_version": desktop_app_version,
            "cli_path": str(desktop_cli_path),
            "cli_exists": desktop_cli_path.exists(),
            "cli_version": desktop_cli_version,
        },
        "native_features": {
            "hooks": "ready" if hooks_ready else "unknown",
            "code_mode": "ready" if hooks_ready else "unknown",
            "bundled_skill_controls": "ready" if hooks_ready else "unknown",
        },
    }


def resolve_memory_root(config: HubConfig, root_arg: str | None) -> Path:
    if root_arg:
        return Path(root_arg).expanduser().resolve()
    fallback = config.workspace_root.parent
    return fallback.resolve() if fallback.exists() else config.workspace_root.resolve()


def render_toml_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def render_toml_array(values: list[str], indent: str = "") -> str:
    if not values:
        return "[]"
    inner_indent = indent + "  "
    lines = ["["]
    for value in values:
        lines.append(f"{inner_indent}{render_toml_string(value)},")
    lines.append(f"{indent}]")
    return "\n".join(lines)


def serialize_work_modes_toml(work_modes: dict[str, WorkMode], cold_skills: list[str]) -> str:
    lines: list[str] = []
    for name in WORK_MODE_NAMES:
        mode = work_modes[name]
        lines.extend(
            [
                f"[mode.{name}.file_hints]",
                f"extensions = {render_toml_array(list(mode.extensions), indent='')}",
                f"keywords = {render_toml_array(list(mode.keywords), indent='')}",
                f"path_keywords = {render_toml_array(list(mode.path_keywords), indent='')}",
                "",
                f"[mode.{name}]",
                f"active_skills = {render_toml_array(list(mode.active_skills), indent='')}",
                f"fallback_skills = {render_toml_array(list(mode.fallback_skills), indent='')}",
                f"output_contract = {render_toml_array(list(mode.output_contract), indent='')}",
                f"session_preamble = {render_toml_string(mode.session_preamble)}",
                f"escalation_triggers = {render_toml_array(list(mode.escalation_triggers), indent='')}",
                "",
            ]
        )
    lines.extend(
        [
            "[inventory]",
            f"cold_skills = {render_toml_array([normalize_skill_name(value) for value in cold_skills], indent='')}",
            "",
        ]
    )
    return "\n".join(lines)


def write_work_modes_toml(config: HubConfig, work_modes: dict[str, WorkMode], cold_skills: list[str]) -> None:
    path = config.policy_dir / "work_modes.toml"
    ensure_repo_targets(config, {"work_modes_toml": path})
    path.write_text(serialize_work_modes_toml(work_modes, cold_skills), encoding="utf-8")


def patch_mode_fallback_skills(config: HubConfig, mode_name: str, fallback_skills: list[str]) -> None:
    path = config.policy_dir / "work_modes.toml"
    ensure_repo_targets(config, {"work_modes_toml": path})
    if not path.exists():
        raise HubRuntimeError(f"Missing work modes file: {path}")
    lines = path.read_text(encoding="utf-8").splitlines()
    section_header = f"[mode.{mode_name}]"
    start = next((idx for idx, line in enumerate(lines) if line.strip() == section_header), None)
    if start is None:
        raise HubRuntimeError(f"Could not find section {section_header} in {path}")
    end = len(lines)
    for idx in range(start + 1, len(lines)):
        if lines[idx].startswith("["):
            end = idx
            break
    field_start = None
    field_end = None
    for idx in range(start + 1, end):
        if lines[idx].startswith("fallback_skills"):
            field_start = idx
            field_end = idx
            if "[" in lines[idx] and "]" not in lines[idx]:
                for cursor in range(idx + 1, end):
                    field_end = cursor
                    if "]" in lines[cursor]:
                        break
                else:
                    raise HubRuntimeError(f"Could not find the end of fallback_skills in {path}")
            break
    if field_start is None or field_end is None:
        raise HubRuntimeError(f"Could not find fallback_skills inside section {section_header} in {path}")
    array_lines = render_toml_array(fallback_skills).splitlines()
    replacement = [f"fallback_skills = {array_lines[0]}"] + array_lines[1:]
    updated = lines[:field_start] + replacement + lines[field_end + 1 :]
    path.write_text("\n".join(updated) + "\n", encoding="utf-8")


def relative_path(config: HubConfig, path: Path) -> str:
    return path.resolve().relative_to(config.workspace_root.resolve()).as_posix()


def is_reconciliation_context_file(path: Path) -> bool:
    lower = path.name.lower()
    if lower in CONTEXT_REQUIRED_FILES:
        return True
    if lower == "folder_hub_reconciliation.md":
        return True
    if lower in {"runtime_overlay_registry.json", "skill_iteration_registry.json", "skill_discovery_registry.json", "skill_route_registry.json"}:
        return True
    return any(token in lower for token in ("system", "hub", "memory", "benchmark", "router", "skill"))


def is_reconciliation_root_file(path: Path) -> bool:
    return path.name.startswith("FOLDER_PROGRESS_") or path.name.startswith("FOLDER_CONTINUE_")


def is_archive_reconciliation_artifact(path: Path) -> bool:
    lower = path.name.lower()
    if is_reconciliation_root_file(path):
        return True
    if path.parent.name.lower() == "contexts":
        if lower.startswith(ARCHIVE_CONTEXT_PREFIXES):
            return True
        if any(token in lower for token in ARCHIVE_CONTEXT_TOKENS):
            return True
    return False


def collect_reconciliation_artifacts(config: HubConfig) -> list[Path]:
    artifacts: list[Path] = []
    for base in (config.policy_dir, config.scripts_dir):
        if not base.exists():
            continue
        for child in sorted(base.iterdir(), key=lambda item: item.name.lower()):
            if child.is_file() and not child.name.startswith("."):
                artifacts.append(child)
    if config.contexts_dir.exists():
        for child in sorted(config.contexts_dir.iterdir(), key=lambda item: item.name.lower()):
            if child.is_file() and is_reconciliation_context_file(child):
                artifacts.append(child)
    for base in (runtime_overlays_dir(config), skill_iteration_closeouts_dir(config), skill_iteration_proposals_dir(config)):
        if not base.exists():
            continue
        for child in sorted(base.rglob("*"), key=lambda item: item.as_posix().lower()):
            if child.is_file() and not child.name.startswith("."):
                artifacts.append(child)
    bridge = config.workspace_root / "obsidian_codex_bridge.py"
    if bridge.exists():
        artifacts.append(bridge)
    for child in sorted(config.workspace_root.iterdir(), key=lambda item: item.name.lower()):
        if child.is_file() and is_reconciliation_root_file(child):
            artifacts.append(child)
    deduped: dict[str, Path] = {}
    for artifact in artifacts:
        deduped[str(artifact.resolve())] = artifact
    return list(deduped.values())


def read_text_if_exists(path: Path) -> str:
    if not path.exists() or not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="ignore").lower()


def artifact_reference_tokens(config: HubConfig, path: Path) -> set[str]:
    rel = relative_path(config, path).lower()
    return {rel, path.name.lower(), path.stem.lower()}


def implemented_override_paths(config: HubConfig) -> set[str]:
    return {
        relative_path(config, config.scripts_dir / "system_hub.py"),
        relative_path(config, config.scripts_dir / "brain.sh"),
    }


def supporting_override_paths(config: HubConfig) -> dict[str, str]:
    mapping = {
        relative_path(config, config.workspace_root / "obsidian_codex_bridge.py"): "supporting_script",
        relative_path(config, config.contexts_dir / "research.md"): "supporting_script",
        relative_path(config, config.contexts_dir / "writing.md"): "supporting_script",
        relative_path(config, config.contexts_dir / "review.md"): "supporting_script",
        relative_path(config, config.scripts_dir / "test_system_hub.py"): "tested_only",
        relative_path(config, config.scripts_dir / "test_overlay_policy.py"): "tested_only",
    }
    return {key: value for key, value in mapping.items() if (config.workspace_root / key).exists()}


def runtime_writer_paths(config: HubConfig) -> set[str]:
    writer_paths = set()
    for path in canonical_artifact_paths(config).values():
        if path.exists():
            writer_paths.add(relative_path(config, path))
    for extra in (
        runtime_overlay_registry_path(config),
        skill_iteration_registry_path(config),
        skill_discovery_registry_path(config),
        skill_route_registry_path(config),
        memory_governance_registry_path(config),
        memory_governance_status_path(config),
    ):
        if extra.exists():
            writer_paths.add(relative_path(config, extra))
    for base in (runtime_overlays_dir(config), skill_iteration_closeouts_dir(config), skill_iteration_proposals_dir(config)):
        if not base.exists():
            continue
        for child in base.rglob("*"):
            if child.is_file():
                writer_paths.add(relative_path(config, child))
    writer_paths.add(relative_path(config, reconciliation_report_path(config)))
    return writer_paths


def load_reconciliation_sources(config: HubConfig) -> dict[str, str]:
    system_hub_text = read_text_if_exists(config.scripts_dir / "system_hub.py")
    brain_text = read_text_if_exists(config.scripts_dir / "brain.sh")
    benchmark_runtime_text = read_text_if_exists(config.scripts_dir / "run_agent_benchmark.py")
    benchmark_publish_text = read_text_if_exists(config.scripts_dir / "publish_agent_policy.py")
    bridge_text = read_text_if_exists(config.workspace_root / "obsidian_codex_bridge.py")
    test_text = read_text_if_exists(config.scripts_dir / "test_system_hub.py")
    overlay_test_text = read_text_if_exists(config.scripts_dir / "test_overlay_policy.py")
    benchmark_test_text = read_text_if_exists(config.scripts_dir / "test_run_agent_benchmark.py")
    registry_text = read_text_if_exists(canonical_artifact_paths(config)["system_registry_json"])
    status_text = read_text_if_exists(canonical_artifact_paths(config)["system_status_md"])
    return {
        "runtime": f"{system_hub_text}\n{brain_text}\n{benchmark_runtime_text}\n{benchmark_publish_text}",
        "support_bridge": bridge_text,
        "support_tests": f"{test_text}\n{overlay_test_text}\n{benchmark_test_text}",
        "canonical": f"{registry_text}\n{status_text}",
    }


def classify_reconciliation_artifact(config: HubConfig, path: Path, sources: dict[str, str]) -> dict[str, str]:
    rel = relative_path(config, path)
    tokens = artifact_reference_tokens(config, path)
    supporting_overrides = supporting_override_paths(config)
    if rel in supporting_overrides:
        evidence = supporting_overrides[rel]
        return {
            "path": rel,
            "category": "supporting",
            "evidence": evidence,
        }

    if rel in runtime_writer_paths(config):
        return {
            "path": rel,
            "category": "implemented",
            "evidence": "runtime_writer",
        }

    if rel in implemented_override_paths(config):
        return {
            "path": rel,
            "category": "implemented",
            "evidence": "runtime_reader",
        }

    runtime_hit = any(token in sources["runtime"] for token in tokens)
    canonical_hit = any(token in sources["canonical"] for token in tokens)
    bridge_hit = any(token in sources["support_bridge"] for token in tokens)
    if bridge_hit:
        return {
            "path": rel,
            "category": "supporting",
            "evidence": "supporting_script",
        }
    if runtime_hit or canonical_hit:
        return {
            "path": rel,
            "category": "implemented",
            "evidence": "runtime_reader",
        }
    if is_archive_reconciliation_artifact(path):
        return {
            "path": rel,
            "category": "archive",
            "evidence": "unreferenced",
        }
    return {
        "path": rel,
        "category": "folder_only",
        "evidence": "unreferenced",
    }


def build_reconciliation_entries(config: HubConfig) -> list[dict[str, str]]:
    sources = load_reconciliation_sources(config)
    entries = [classify_reconciliation_artifact(config, artifact, sources) for artifact in collect_reconciliation_artifacts(config)]
    category_order = {"implemented": 0, "supporting": 1, "archive": 2, "folder_only": 3}
    return sorted(entries, key=lambda entry: (category_order.get(entry["category"], 9), entry["path"]))


def recommended_promotion_paths(entries: list[dict[str, str]]) -> list[str]:
    candidates = []
    for entry in entries:
        if entry["category"] != "folder_only":
            continue
        lower = entry["path"].lower()
        if any(token in lower for token in ("system", "hub", "brain", "router", "benchmark", "skill", "folder_progress", "folder_continue", "reconciliation")):
            candidates.append(entry["path"])
    return candidates


def render_reconciliation_markdown(config: HubConfig, entries: list[dict[str, str]]) -> str:
    counts = Counter(entry["category"] for entry in entries)
    promotions = recommended_promotion_paths(entries)
    lines = [
        "# Folder Hub Reconciliation",
        "",
        f"- Generated at: `{dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')}`",
        f"- Workspace: `{config.workspace_root}`",
        f"- Folder-only artifacts: `{counts.get('folder_only', 0)}`",
        "",
        "## Summary",
        "",
        f"- Implemented: `{counts.get('implemented', 0)}`",
        f"- Supporting: `{counts.get('supporting', 0)}`",
        f"- Archive: `{counts.get('archive', 0)}`",
        f"- Folder-only: `{counts.get('folder_only', 0)}`",
        "",
    ]
    for heading, category in (
        ("Implemented Artifacts", "implemented"),
        ("Supporting Artifacts", "supporting"),
        ("Archive Artifacts", "archive"),
        ("Folder-only Artifacts", "folder_only"),
    ):
        lines.extend([f"## {heading}", ""])
        matching = [entry for entry in entries if entry["category"] == category]
        if matching:
            for entry in matching:
                lines.append(f"- `{entry['path']}` `evidence={entry['evidence']}`")
        else:
            lines.append("- none")
        lines.append("")
    lines.extend(["## Recommended Promotions", ""])
    if promotions:
        for path in promotions:
            lines.append(f"- `{path}`")
    else:
        lines.append("- none")
    lines.append("")
    return "\n".join(lines)

def ensure_repo_targets(config: HubConfig, targets: dict[str, Path]) -> None:
    for path in targets.values():
        if not is_within(config.workspace_root, path):
            raise HubRuntimeError(f"Refusing to write outside workspace: {path}")


def is_within(root: Path, path: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def run_command(
    cmd: list[str],
    *,
    cwd: Path,
    env: dict[str, str] | None = None,
    expected_outputs: list[Path] | None = None,
    raise_on_error: bool = True,
) -> dict[str, Any]:
    start = dt.datetime.now(dt.timezone.utc)
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, env=merged_env)
    duration = (dt.datetime.now(dt.timezone.utc) - start).total_seconds()
    outputs = expected_outputs or []
    record = {
        "command": cmd,
        "cwd": str(cwd),
        "exit_code": proc.returncode,
        "status": "passed" if proc.returncode == 0 else "failed",
        "duration_sec": round(duration, 6),
        "stdout_tail": tail_lines(proc.stdout),
        "stderr_tail": tail_lines(proc.stderr),
        "outputs": [str(path) for path in outputs],
    }
    if proc.returncode != 0 and raise_on_error:
        raise HubRuntimeError(f"Command failed ({proc.returncode}): {' '.join(cmd)}\n{tail_lines(proc.stderr or proc.stdout)}")
    return record


def tail_lines(text: str, count: int = 8) -> str:
    lines = [line for line in text.splitlines() if line.strip()]
    return "\n".join(lines[-count:])


def scan_installed_skills(skill_roots: tuple[Path, ...]) -> list[dict[str, str]]:
    seen: set[str] = set()
    skills: list[dict[str, str]] = []
    for root in skill_roots:
        if not root.exists() or not os.access(root, os.R_OK):
            continue
        for child in sorted(root.iterdir(), key=lambda item: item.name.lower()):
            if not child.is_dir():
                continue
            if child.name.startswith(".") or child.name == "_shared":
                continue
            skill_file = child / "SKILL.md"
            if not skill_file.exists():
                continue
            name = normalize_skill_name(child.name)
            if name in seen:
                continue
            seen.add(name)
            skills.append({"name": name, "path": str(child), "root": str(root)})
    return skills


def build_skill_inventory(
    installed_skills: list[dict[str, str]],
    work_modes: dict[str, WorkMode],
    cold_skills: list[str],
) -> dict[str, Any]:
    installed_names = sorted(skill["name"] for skill in installed_skills)
    active_configured = sorted({skill for mode in work_modes.values() for skill in mode.active_skills})
    fallback_configured = sorted({skill for mode in work_modes.values() for skill in mode.fallback_skills})
    cold_set = {normalize_skill_name(skill) for skill in cold_skills}
    installed_set = set(installed_names)
    active_installed = sorted(installed_set & set(active_configured))
    candidate_skills = sorted(installed_set - set(active_configured) - set(fallback_configured) - cold_set)
    cold_installed = sorted(installed_set & cold_set)
    missing_active = sorted(set(active_configured) - installed_set)
    missing_fallback = sorted(set(fallback_configured) - installed_set)
    return {
        "installed_count": len(installed_names),
        "installed_skills": installed_names,
        "installed_entries": installed_skills,
        "active_configured": active_configured,
        "active_installed": active_installed,
        "fallback_configured": fallback_configured,
        "candidate_skills": candidate_skills,
        "cold_skills": cold_installed,
        "cold_configured": sorted(cold_set),
        "missing_active_skills": missing_active,
        "missing_fallback_skills": missing_fallback,
        "new_candidate_skills": [],
    }


ANSI_ESCAPE_RE = re.compile(r"\x1b\[[0-9;]*m")


def normalize_search_terms(query: str) -> list[str]:
    return [token for token in re.findall(r"[a-z0-9][a-z0-9_-]*", query.lower()) if len(token) >= 2]


def skill_search_blob(skill: dict[str, str]) -> str:
    skill_file = Path(skill["path"]) / "SKILL.md"
    try:
        text = skill_file.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return skill["name"]
    lowered = text.lower()
    return "\n".join(lowered.splitlines()[:40])


def score_local_skill_match(skill: dict[str, str], query: str) -> dict[str, Any] | None:
    terms = normalize_search_terms(query)
    name = skill["name"]
    blob = skill_search_blob(skill)
    score = 0
    reasons: list[str] = []
    has_name_signal = False
    exact_phrase = query.strip().lower()
    if exact_phrase and exact_phrase in name:
        score += 10
        reasons.append("name_phrase")
        has_name_signal = True
    for term in terms:
        if term in name:
            score += 4
            reasons.append(f"name:{term}")
            has_name_signal = True
        elif term in blob:
            score += 1
            reasons.append(f"body:{term}")
    if score <= 0 or (not has_name_signal and score < 2):
        return None
    summary = ""
    for line in blob.splitlines():
        stripped = line.strip()
        if stripped and stripped != "---" and not stripped.startswith("#"):
            summary = stripped[:220]
            break
    return {
        "name": name,
        "path": skill["path"],
        "root": skill["root"],
        "score": score,
        "reasons": reasons[:6],
        "summary": summary,
        "installed": True,
    }


def discover_local_skills(installed_skills: list[dict[str, str]], query: str) -> list[dict[str, Any]]:
    matches = [match for skill in installed_skills if (match := score_local_skill_match(skill, query))]
    return sorted(matches, key=lambda item: (-item["score"], item["name"]))


def parse_remote_skill_find_output(text: str) -> list[dict[str, Any]]:
    stripped = ANSI_ESCAPE_RE.sub("", text)
    results: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for raw_line in stripped.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        package_match = re.match(r"^([A-Za-z0-9._-]+/[A-Za-z0-9._-]+@[A-Za-z0-9._-]+)(?:\s+(.*))?$", line)
        if package_match:
            package = package_match.group(1)
            remainder = (package_match.group(2) or "").strip()
            current = {
                "package": package,
                "score_hint": remainder or None,
                "url": None,
                "install_hint": f"npx skills add {package} -g",
            }
            results.append(current)
            continue
        if current and line.startswith("└ "):
            current["url"] = line.removeprefix("└ ").strip()
    return results


def discover_remote_skills(query: str) -> tuple[list[dict[str, Any]], list[str], str]:
    warnings: list[str] = []
    npx_path = shutil.which("npx")
    if not npx_path:
        warnings.append("Remote discovery unavailable: `npx` is not on PATH.")
        return [], warnings, "degraded"
    proc = subprocess.run(
        [npx_path, "--yes", "skills", "find", query],
        capture_output=True,
        text=True,
        check=False,
    )
    output = proc.stdout or proc.stderr
    if proc.returncode != 0:
        warnings.append(f"Remote discovery failed via `npx skills find` (exit={proc.returncode}).")
        return [], warnings, "degraded"
    matches = parse_remote_skill_find_output(output)
    if not matches:
        warnings.append("Remote discovery returned no parseable matches.")
        return [], warnings, "degraded"
    return matches, warnings, "healthy"


def load_runtime_overlay_state(config: HubConfig) -> tuple[dict[str, Any], list[dict[str, str]]]:
    findings: list[dict[str, str]] = []
    registry_path = runtime_overlay_registry_path(config)
    overlays_path = runtime_overlays_dir(config)
    payload = default_runtime_overlay_registry()
    status = "healthy"
    if registry_path.exists():
        try:
            payload = json.loads(registry_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            status = "degraded"
            findings.append(
                warning("overlay", "invalid_runtime_overlay_registry", f"Invalid runtime overlay registry JSON ({exc})", registry_path)
            )
            payload = default_runtime_overlay_registry()
    entries = payload.get("entries", [])
    if not isinstance(entries, list):
        status = "degraded"
        findings.append(
            warning("overlay", "invalid_runtime_overlay_entries", "Runtime overlay registry entries must be a list", registry_path)
        )
        entries = []
    brief_files = sorted(overlays_path.rglob("*.md")) if overlays_path.exists() else []
    latest_generated_at = payload.get("generated_at")
    for entry in entries:
        if isinstance(entry, dict) and isinstance(entry.get("generated_at"), str):
            latest_generated_at = max(latest_generated_at or "", entry["generated_at"])
    return {
        "status": status,
        "registry_path": str(registry_path),
        "registry_exists": registry_path.exists(),
        "brief_dir": str(overlays_path),
        "brief_dir_exists": overlays_path.exists(),
        "brief_count": len(brief_files),
        "latest_generated_at": latest_generated_at,
        "entries": entries,
    }, findings


def load_skill_iteration_state(config: HubConfig) -> tuple[dict[str, Any], list[dict[str, str]]]:
    findings: list[dict[str, str]] = []
    registry_path = skill_iteration_registry_path(config)
    closeouts_path = skill_iteration_closeouts_dir(config)
    proposals_path = skill_iteration_proposals_dir(config)
    payload = default_skill_iteration_registry()
    status = "healthy"
    if registry_path.exists():
        try:
            payload = json.loads(registry_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            status = "degraded"
            findings.append(
                warning("skills", "invalid_skill_iteration_registry", f"Invalid skill iteration registry JSON ({exc})", registry_path)
            )
            payload = default_skill_iteration_registry()
    closeouts = payload.get("closeouts", [])
    proposals = payload.get("proposals", [])
    if not isinstance(closeouts, list) or not isinstance(proposals, list):
        status = "degraded"
        findings.append(
            warning("skills", "invalid_skill_iteration_entries", "Skill iteration registry must contain list closeouts and proposals", registry_path)
        )
        closeouts = closeouts if isinstance(closeouts, list) else []
        proposals = proposals if isinstance(proposals, list) else []
    open_proposals = [entry for entry in proposals if isinstance(entry, dict) and entry.get("status") == "open"]
    promoted = [entry for entry in proposals if isinstance(entry, dict) and entry.get("status") == "promoted_to_fallback"]
    rejected = [entry for entry in proposals if isinstance(entry, dict) and entry.get("status") == "rejected"]
    latest_closeout_at = None
    for entry in closeouts:
        if isinstance(entry, dict) and isinstance(entry.get("generated_at"), str):
            latest_closeout_at = max(latest_closeout_at or "", entry["generated_at"])
    return {
        "status": status,
        "registry_path": str(registry_path),
        "registry_exists": registry_path.exists(),
        "closeouts_dir": str(closeouts_path),
        "proposals_dir": str(proposals_path),
        "closeout_count": len(closeouts),
        "proposal_count": len(proposals),
        "open_proposal_count": len(open_proposals),
        "promoted_count": len(promoted),
        "rejected_count": len(rejected),
        "latest_closeout_at": latest_closeout_at,
        "closeouts": closeouts,
        "proposals": proposals,
    }, findings


def load_skill_discovery_state(config: HubConfig) -> tuple[dict[str, Any], list[dict[str, str]]]:
    findings: list[dict[str, str]] = []
    registry_path = skill_discovery_registry_path(config)
    payload = default_skill_discovery_registry()
    status = "healthy"
    if registry_path.exists():
        try:
            payload = json.loads(registry_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            status = "degraded"
            findings.append(
                warning("skills", "invalid_skill_discovery_registry", f"Invalid skill discovery registry JSON ({exc})", registry_path)
            )
            payload = default_skill_discovery_registry()
    local_matches = payload.get("local_matches", [])
    remote_matches = payload.get("remote_matches", [])
    if not isinstance(local_matches, list) or not isinstance(remote_matches, list):
        status = "degraded"
        findings.append(
            warning("skills", "invalid_skill_discovery_entries", "Skill discovery registry must contain list local_matches and remote_matches", registry_path)
        )
        local_matches = local_matches if isinstance(local_matches, list) else []
        remote_matches = remote_matches if isinstance(remote_matches, list) else []
    warnings_list = payload.get("warnings", [])
    if not isinstance(warnings_list, list):
        warnings_list = []
    return {
        "status": status,
        "registry_path": str(registry_path),
        "registry_exists": registry_path.exists(),
        "generated_at": payload.get("generated_at"),
        "last_run_status": payload.get("status", "unknown"),
        "last_query": payload.get("last_query"),
        "local_match_count": len(local_matches),
        "remote_match_count": len(remote_matches),
        "local_matches": local_matches,
        "remote_matches": remote_matches,
        "warnings": warnings_list,
    }, findings


def load_skill_route_state(config: HubConfig) -> tuple[dict[str, Any], list[dict[str, str]]]:
    findings: list[dict[str, str]] = []
    registry_path = skill_route_registry_path(config)
    payload = default_skill_route_registry()
    status = "healthy"
    if registry_path.exists():
        try:
            payload = json.loads(registry_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            status = "degraded"
            findings.append(
                warning("skills", "invalid_skill_route_registry", f"Invalid skill route registry JSON ({exc})", registry_path)
            )
            payload = default_skill_route_registry()
    entries = payload.get("entries", [])
    if not isinstance(entries, list):
        status = "degraded"
        findings.append(
            warning("skills", "invalid_skill_route_entries", "Skill route registry must contain list field `entries`", registry_path)
        )
        entries = []
    latest_entry = None
    latest_generated_at = None
    gap_count = 0
    route_count = 0
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        route_count += 1
        if entry.get("gap_detected"):
            gap_count += 1
        generated_at = entry.get("generated_at")
        if isinstance(generated_at, str) and (latest_generated_at is None or generated_at > latest_generated_at):
            latest_generated_at = generated_at
            latest_entry = entry
    return {
        "status": status,
        "registry_path": str(registry_path),
        "registry_exists": registry_path.exists(),
        "route_count": route_count,
        "gap_count": gap_count,
        "latest_generated_at": latest_generated_at,
        "latest_task": latest_entry.get("task") if isinstance(latest_entry, dict) else None,
        "latest_mode": latest_entry.get("predicted_mode") if isinstance(latest_entry, dict) else None,
        "latest_need_skill": latest_entry.get("need_skill") if isinstance(latest_entry, dict) else None,
        "latest_gap_detected": latest_entry.get("gap_detected") if isinstance(latest_entry, dict) else None,
        "latest_primary_skills": latest_entry.get("primary_skills", []) if isinstance(latest_entry, dict) else [],
        "entries": entries,
    }, findings


def load_memory_governance_registry(config: HubConfig) -> dict[str, Any]:
    payload = load_json_file_strict(memory_governance_registry_path(config), default_memory_governance_registry(), "memory governance registry")
    if not isinstance(payload.get("window_runs", {}), dict) or not isinstance(payload.get("entries", []), list):
        raise HubRuntimeError("Memory governance registry must contain object `window_runs` and list `entries`.")
    return payload


def save_memory_governance_registry(config: HubConfig, payload: dict[str, Any]) -> None:
    path = memory_governance_registry_path(config)
    ensure_repo_targets(config, {"memory_governance_registry_json": path})
    dump_json(path, payload)


def load_memory_governance_state(config: HubConfig) -> tuple[dict[str, Any], list[dict[str, str]]]:
    findings: list[dict[str, str]] = []
    registry_path = memory_governance_registry_path(config)
    status_path = memory_governance_status_path(config)
    payload = default_memory_governance_registry()
    status = "healthy"
    if registry_path.exists():
        try:
            payload = json.loads(registry_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            status = "degraded"
            findings.append(
                warning("memory", "invalid_memory_governance_registry", f"Invalid memory governance registry JSON ({exc})", registry_path)
            )
            payload = default_memory_governance_registry()
    window_runs = payload.get("window_runs", {})
    entries = payload.get("entries", [])
    if not isinstance(window_runs, dict) or not isinstance(entries, list):
        status = "degraded"
        findings.append(
            warning("memory", "invalid_memory_governance_entries", "Memory governance registry must contain object window_runs and list entries", registry_path)
        )
        window_runs = {"daily": None, "weekly": None}
        entries = []
    latest_daily = window_runs.get("daily", {}) if isinstance(window_runs.get("daily"), dict) else {}
    latest_weekly = window_runs.get("weekly", {}) if isinstance(window_runs.get("weekly"), dict) else {}
    daily_generated_at = latest_daily.get("generated_at")
    weekly_generated_at = latest_weekly.get("generated_at")
    daily_age_hours = age_hours(parse_datetime_any(daily_generated_at))
    weekly_age_hours = age_hours(parse_datetime_any(weekly_generated_at))
    if registry_path.exists() and daily_generated_at and daily_age_hours is not None and daily_age_hours > float(config.report_hours):
        status = "degraded"
        findings.append(
            warning(
                "memory",
                "stale_daily_memory_governance",
                f"Daily memory governance is stale ({round(daily_age_hours, 2)}h old)",
                registry_path,
            )
        )
    weekly_threshold = max(float(config.report_hours) * 7.0, 168.0)
    if registry_path.exists() and weekly_generated_at and weekly_age_hours is not None and weekly_age_hours > weekly_threshold:
        status = "degraded"
        findings.append(
            warning(
                "memory",
                "stale_weekly_memory_governance",
                f"Weekly memory governance is stale ({round(weekly_age_hours, 2)}h old)",
                registry_path,
            )
        )
    return {
        "status": status,
        "registry_path": str(registry_path),
        "registry_exists": registry_path.exists(),
        "status_path": str(status_path),
        "status_exists": status_path.exists(),
        "retrieval_mode": payload.get("retrieval_mode", "semantic-lite"),
        "durable_count": payload.get("durable_count", 0),
        "summary_only_count": payload.get("summary_only_count", 0),
        "archive_candidate_count": payload.get("archive_candidate_count", 0),
        "hot_count": payload.get("hot_count", 0),
        "warm_count": payload.get("warm_count", 0),
        "cool_count": payload.get("cool_count", 0),
        "latest_daily_generated_at": daily_generated_at,
        "latest_weekly_generated_at": weekly_generated_at,
        "stale_session_days": payload.get("stale_session_days", SESSION_STALE_DAYS),
        "entries": entries,
    }, findings


def build_capability_snapshot(
    inventory: dict[str, Any],
    work_modes_meta: dict[str, Any],
    *,
    new_candidate_skills: list[str] | None = None,
    continuity_entrypoint: dict[str, Any] | None = None,
    benchmark_cases_exists: bool | None = None,
    benchmark_publish_chain_status: str | None = None,
    runtime_overlays: dict[str, Any] | None = None,
    skill_iteration: dict[str, Any] | None = None,
    skill_discovery: dict[str, Any] | None = None,
    skill_route: dict[str, Any] | None = None,
    memory_governance: dict[str, Any] | None = None,
) -> dict[str, Any]:
    origin = os.getenv("CODEX_INTERNAL_ORIGINATOR_OVERRIDE", "unknown")
    runtime_environment = discover_runtime_environment(origin)
    gui_surface = "available" if ("desktop" in origin.lower() or runtime_environment["desktop_runtime"]["app_exists"]) else "unknown"
    subagents = {
        "status": "available" if gui_surface == "available" else "unknown",
        "source": "runtime_hint",
    }
    commands = [{"name": name, "available": True} for name in DEFAULT_BRAIN_COMMANDS]
    return {
        "runtime_origin": origin,
        "runtime_environment": runtime_environment,
        "gui_surface": gui_surface,
        "subagents": subagents,
        "commands": commands,
        "active_modes": list(work_modes_meta["mode_names"]),
        "active_skill_count": len(inventory["active_installed"]),
        "installed_active_skills": inventory["active_installed"],
        "candidate_skill_count": len(inventory["candidate_skills"]),
        "new_candidate_skill_count": len(new_candidate_skills or []),
        "continuity_entrypoint": continuity_entrypoint or {"exists": False, "path": None},
        "benchmark_cases_exists": bool(benchmark_cases_exists),
        "benchmark_publish_chain_status": benchmark_publish_chain_status or "unknown",
        "overlay_runtime": {
            "status": (runtime_overlays or {}).get("status", "unknown"),
            "brief_count": (runtime_overlays or {}).get("brief_count", 0),
            "latest_generated_at": (runtime_overlays or {}).get("latest_generated_at"),
        },
        "skill_iteration_gate": {
            "status": (skill_iteration or {}).get("status", "unknown"),
            "closeout_count": (skill_iteration or {}).get("closeout_count", 0),
            "open_proposal_count": (skill_iteration or {}).get("open_proposal_count", 0),
            "latest_closeout_at": (skill_iteration or {}).get("latest_closeout_at"),
        },
        "skill_discovery": {
            "status": (skill_discovery or {}).get("status", "unknown"),
            "last_run_status": (skill_discovery or {}).get("last_run_status", "unknown"),
            "generated_at": (skill_discovery or {}).get("generated_at"),
            "last_query": (skill_discovery or {}).get("last_query"),
            "local_match_count": (skill_discovery or {}).get("local_match_count", 0),
            "remote_match_count": (skill_discovery or {}).get("remote_match_count", 0),
        },
        "skill_route": {
            "status": (skill_route or {}).get("status", "unknown"),
            "route_count": (skill_route or {}).get("route_count", 0),
            "gap_count": (skill_route or {}).get("gap_count", 0),
            "latest_generated_at": (skill_route or {}).get("latest_generated_at"),
            "latest_task": (skill_route or {}).get("latest_task"),
            "latest_mode": (skill_route or {}).get("latest_mode"),
            "latest_gap_detected": (skill_route or {}).get("latest_gap_detected"),
        },
        "memory_governance": {
            "status": (memory_governance or {}).get("status", "unknown"),
            "retrieval_mode": (memory_governance or {}).get("retrieval_mode", "semantic-lite"),
            "durable_count": (memory_governance or {}).get("durable_count", 0),
            "summary_only_count": (memory_governance or {}).get("summary_only_count", 0),
            "archive_candidate_count": (memory_governance or {}).get("archive_candidate_count", 0),
            "hot_count": (memory_governance or {}).get("hot_count", 0),
            "warm_count": (memory_governance or {}).get("warm_count", 0),
            "cool_count": (memory_governance or {}).get("cool_count", 0),
            "latest_daily_generated_at": (memory_governance or {}).get("latest_daily_generated_at"),
            "latest_weekly_generated_at": (memory_governance or {}).get("latest_weekly_generated_at"),
            "stale_session_days": (memory_governance or {}).get("stale_session_days", SESSION_STALE_DAYS),
        },
        "context_window": {
            "status": "model_dependent",
            "note": "Exact long-context limits depend on the active model and should be checked in the UI when needed.",
        },
        "gui_note": "GUI-specific affordances depend on the Codex Desktop runtime.",
    }


def build_overlay_runtime_check(sources: dict[str, Any]) -> dict[str, Any]:
    runtime = sources.get("overlay", {}).get("runtime_overlays", {})
    return {
        "status": runtime.get("status", "unknown"),
        "brief_count": runtime.get("brief_count", 0),
        "latest_generated_at": runtime.get("latest_generated_at"),
        "registry_path": runtime.get("registry_path"),
    }


def build_skill_iteration_check(sources: dict[str, Any]) -> dict[str, Any]:
    state = sources.get("skills", {}).get("iteration", {})
    return {
        "status": state.get("status", "unknown"),
        "closeout_count": state.get("closeout_count", 0),
        "open_proposal_count": state.get("open_proposal_count", 0),
        "promoted_count": state.get("promoted_count", 0),
        "rejected_count": state.get("rejected_count", 0),
        "latest_closeout_at": state.get("latest_closeout_at"),
        "registry_path": state.get("registry_path"),
    }


def build_skill_discovery_check(sources: dict[str, Any]) -> dict[str, Any]:
    state = sources.get("skills", {}).get("discovery", {})
    return {
        "status": state.get("status", "unknown"),
        "generated_at": state.get("generated_at"),
        "last_query": state.get("last_query"),
        "local_match_count": state.get("local_match_count", 0),
        "remote_match_count": state.get("remote_match_count", 0),
        "registry_path": state.get("registry_path"),
    }


def build_skill_route_check(sources: dict[str, Any]) -> dict[str, Any]:
    state = sources.get("skills", {}).get("routing", {})
    return {
        "status": state.get("status", "unknown"),
        "route_count": state.get("route_count", 0),
        "gap_count": state.get("gap_count", 0),
        "latest_generated_at": state.get("latest_generated_at"),
        "latest_task": state.get("latest_task"),
        "latest_mode": state.get("latest_mode"),
        "latest_need_skill": state.get("latest_need_skill"),
        "latest_gap_detected": state.get("latest_gap_detected"),
        "latest_primary_skills": state.get("latest_primary_skills", []),
        "registry_path": state.get("registry_path"),
    }


def build_memory_governance_check(sources: dict[str, Any]) -> dict[str, Any]:
    state = sources.get("memory", {}).get("governance", {})
    return {
        "status": state.get("status", "unknown"),
        "retrieval_mode": state.get("retrieval_mode", "semantic-lite"),
        "durable_count": state.get("durable_count", 0),
        "summary_only_count": state.get("summary_only_count", 0),
        "archive_candidate_count": state.get("archive_candidate_count", 0),
        "hot_count": state.get("hot_count", 0),
        "warm_count": state.get("warm_count", 0),
        "cool_count": state.get("cool_count", 0),
        "latest_daily_generated_at": state.get("latest_daily_generated_at"),
        "latest_weekly_generated_at": state.get("latest_weekly_generated_at"),
        "stale_daily": state.get("status") == "degraded" and bool(state.get("latest_daily_generated_at")),
        "stale_session_days": state.get("stale_session_days", SESSION_STALE_DAYS),
        "registry_path": state.get("registry_path"),
        "status_path": state.get("status_path"),
    }


def build_runtime_environment_check(capability_snapshot: dict[str, Any]) -> dict[str, Any]:
    runtime = capability_snapshot.get("runtime_environment", {})
    alignment_status = runtime.get("alignment_status", "unknown")
    return {
        "status": "healthy" if alignment_status in {"aligned", "desktop_only", "shell_only", "unknown"} else "drift",
        "alignment_status": alignment_status,
        "preferred_runtime": runtime.get("preferred_runtime", "unknown"),
        "shell_version": runtime.get("shell_cli", {}).get("version"),
        "desktop_cli_version": runtime.get("desktop_runtime", {}).get("cli_version"),
        "desktop_app_version": runtime.get("desktop_runtime", {}).get("app_version"),
        "hooks": runtime.get("native_features", {}).get("hooks", "unknown"),
        "code_mode": runtime.get("native_features", {}).get("code_mode", "unknown"),
        "bundled_skill_controls": runtime.get("native_features", {}).get("bundled_skill_controls", "unknown"),
    }


def scan_sources(config: HubConfig) -> tuple[dict[str, Any], list[dict[str, str]], dict[str, Any]]:
    findings: list[dict[str, str]] = []
    sources: dict[str, Any] = {}
    work_modes, work_modes_meta, work_mode_findings = load_work_modes(config)
    findings.extend(work_mode_findings)
    installed_skills = scan_installed_skills(config.skill_roots)
    inventory = build_skill_inventory(installed_skills, work_modes, work_modes_meta["cold_skills"])

    policy_files: dict[str, Any] = {}
    policy_missing = []
    for name in POLICY_REQUIRED_FILES:
        path = config.policy_dir / name
        exists = path.exists()
        policy_files[name] = {"path": str(path), "exists": exists}
        if not exists:
            policy_missing.append(name)
            findings.append(warning("policy", "missing_policy_file", f"Missing policy artifact: {name}", path))

    overlay_agents = config.workspace_root / "AGENTS.md"
    overlay_principles = config.workspace_root / "PRINCIPLES.md"
    overlay_missing = []
    for label, path in (("AGENTS.md", overlay_agents), ("PRINCIPLES.md", overlay_principles)):
        if not path.exists():
            overlay_missing.append(label)
            findings.append(warning("overlay", "missing_overlay_file", f"Missing overlay file: {label}", path))
    runtime_overlays, overlay_runtime_findings = load_runtime_overlay_state(config)
    findings.extend(overlay_runtime_findings)
    sources["overlay"] = {
        "status": "healthy" if not overlay_missing and runtime_overlays["status"] == "healthy" else "degraded",
        "agents_md": {"path": str(overlay_agents), "exists": overlay_agents.exists()},
        "principles_md": {"path": str(overlay_principles), "exists": overlay_principles.exists()},
        "runtime_overlays": runtime_overlays,
    }

    policy_scripts = {
        "run_agent_benchmark": config.scripts_dir / "run_agent_benchmark.py",
        "publish_agent_policy": config.scripts_dir / "publish_agent_policy.py",
        "run_agent_benchmark_wrapper": config.scripts_dir / "run_agent_benchmark.sh",
        "test_run_agent_benchmark": config.scripts_dir / "test_run_agent_benchmark.py",
    }
    skill_scripts = {
        "run_router_regression": config.scripts_dir / "run_router_regression.sh",
        "build_skill_graph": config.scripts_dir / "build_skill_graph.py",
    }
    memory_scripts = {
        "obsidian_bridge": config.workspace_root / "obsidian_codex_bridge.py",
    }
    missing_policy_scripts = []
    missing_skill_scripts = []
    script_entries: dict[str, Any] = {}
    for label, path in {**policy_scripts, **skill_scripts, **memory_scripts}.items():
        exists = path.exists()
        script_entries[label] = {"path": str(path), "exists": exists}
        if not exists:
            if label in policy_scripts:
                missing_policy_scripts.append(label)
                findings.append(warning("policy", "missing_script", f"Missing required script: {label}", path))
            elif label in skill_scripts:
                missing_skill_scripts.append(label)
                findings.append(warning("skills", "missing_script", f"Missing required script: {label}", path))
            else:
                findings.append(warning("memory", "missing_bridge_script", "Missing memory bridge script", path))

    sources["policy"] = {
        "path": str(config.policy_dir),
        "exists": config.policy_dir.exists(),
        "status": "healthy",
        "files": policy_files,
        "scripts": {
            "run_agent_benchmark": script_entries["run_agent_benchmark"],
            "publish_agent_policy": script_entries["publish_agent_policy"],
            "run_agent_benchmark_wrapper": script_entries["run_agent_benchmark_wrapper"],
            "test_run_agent_benchmark": script_entries["test_run_agent_benchmark"],
        },
        "work_modes": work_modes_meta,
    }
    benchmark_cases_path = config.contexts_dir / "agent_benchmark_cases.json"
    benchmark_cases_exists = benchmark_cases_path.exists()
    if not benchmark_cases_exists:
        findings.append(warning("policy", "missing_benchmark_cases", "Missing benchmark case input file", benchmark_cases_path))
    publish_chain_status = "healthy" if not missing_policy_scripts else "degraded"
    if missing_policy_scripts:
        findings.append(
            warning(
                "policy",
                "missing_publish_chain_script",
                "Benchmark publish and portability chain is incomplete",
                config.scripts_dir,
            )
        )
    sources["policy"]["benchmark_cases"] = {"path": str(benchmark_cases_path), "exists": benchmark_cases_exists}
    sources["policy"]["benchmark_publish_chain"] = {
        "status": publish_chain_status,
        "wrapper": script_entries["run_agent_benchmark_wrapper"],
        "publisher": script_entries["publish_agent_policy"],
        "portability_test": script_entries["test_run_agent_benchmark"],
    }
    sources["policy"]["status"] = (
        "healthy"
        if (
            not policy_missing
            and benchmark_cases_exists
            and publish_chain_status == "healthy"
            and config.policy_dir.exists()
            and work_modes_meta["status"] == "healthy"
        )
        else "degraded"
    )

    skill_roots = []
    missing_skill_roots = []
    for path in config.skill_roots:
        exists = path.exists()
        readable = exists and os.access(path, os.R_OK)
        skill_roots.append({"path": str(path), "exists": exists, "readable": readable})
        if not readable:
            missing_skill_roots.append(str(path))
            findings.append(warning("skills", "missing_skill_root", "Skill root missing or unreadable", path))
    sources["skills"] = {
        "status": "healthy" if not missing_skill_roots and not missing_skill_scripts else "degraded",
        "roots": skill_roots,
        "scripts": {
            "build_skill_graph": script_entries["build_skill_graph"],
            "run_router_regression": script_entries["run_router_regression"],
        },
        "inventory": inventory,
    }
    skill_iteration_state, skill_iteration_findings = load_skill_iteration_state(config)
    findings.extend(skill_iteration_findings)
    sources["skills"]["iteration"] = skill_iteration_state
    skill_discovery_state, skill_discovery_findings = load_skill_discovery_state(config)
    findings.extend(skill_discovery_findings)
    sources["skills"]["discovery"] = skill_discovery_state
    skill_route_state, skill_route_findings = load_skill_route_state(config)
    findings.extend(skill_route_findings)
    sources["skills"]["routing"] = skill_route_state
    if skill_iteration_state["status"] != "healthy":
        sources["skills"]["status"] = "degraded"
    if skill_discovery_state["status"] != "healthy":
        sources["skills"]["status"] = "degraded"
    if skill_route_state["status"] != "healthy":
        sources["skills"]["status"] = "degraded"

    template_entries: dict[str, Any] = {}
    missing_templates = []
    for name in CONTEXT_REQUIRED_FILES:
        path = config.contexts_dir / name
        exists = path.exists()
        template_entries[name] = {"path": str(path), "exists": exists}
        if not exists:
            missing_templates.append(name)
            findings.append(warning("memory", "missing_context_template", f"Missing memory context template: {name}", path))

    memory_checks = {
        "bridge_script": script_entries["obsidian_bridge"],
        "vault_path": path_state(config.vault_path),
        "checkpoint_root": path_state(config.checkpoint_root),
        "bridge_state": path_state(config.bridge_state),
        "active_session_state": path_state(config.active_session_state),
        "context_templates": template_entries,
        "state_alignment": {
            "status": "unknown",
            "relationship": None,
            "bridge_session_id": None,
            "active_session_id": None,
        },
    }
    if not config.vault_path.exists():
        findings.append(warning("memory", "missing_vault_path", "Obsidian vault path is missing", config.vault_path))
    if not config.checkpoint_root.exists():
        findings.append(warning("memory", "missing_checkpoint_root", "Checkpoint root is missing", config.checkpoint_root))
    if not config.bridge_state.exists():
        findings.append(warning("memory", "missing_bridge_state", "Bridge state not found; continuity is degraded", config.bridge_state))
    if not config.active_session_state.exists():
        findings.append(warning("memory", "missing_active_session_state", "Active session state not found; continuity is degraded", config.active_session_state))
    bridge_payload: dict[str, Any] | None = None
    active_payload: dict[str, Any] | None = None
    if config.bridge_state.exists():
        try:
            loaded = json.loads(config.bridge_state.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                bridge_payload = loaded
            else:
                findings.append(warning("memory", "invalid_bridge_state", "Bridge state must contain a JSON object", config.bridge_state))
        except json.JSONDecodeError:
            findings.append(warning("memory", "invalid_bridge_state", "Bridge state JSON is invalid", config.bridge_state))
    if config.active_session_state.exists():
        try:
            loaded = json.loads(config.active_session_state.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                active_payload = loaded
            else:
                findings.append(warning("memory", "invalid_active_session_state", "Active session state must contain a JSON object", config.active_session_state))
        except json.JSONDecodeError:
            findings.append(warning("memory", "invalid_active_session_state", "Active session state JSON is invalid", config.active_session_state))
    bridge_session_id = str(bridge_payload.get("session_id", "")).strip() if bridge_payload else ""
    active_session_id = str(active_payload.get("session_id", "")).strip() if active_payload else ""
    alignment_status = "unknown"
    alignment_relationship = None
    if bridge_payload is not None and active_payload is not None:
        if bridge_session_id and active_session_id and bridge_session_id == active_session_id:
            alignment_status = "healthy"
            alignment_relationship = "same_session"
        elif bridge_session_id or active_session_id:
            active_last_summary = str(active_payload.get("last_summary", "")).strip().lower() if active_payload else ""
            active_handoff_anchor = str(active_payload.get("handoff_anchor", "")).strip().lower() if active_payload else ""
            bridge_id_lower = bridge_session_id.lower()
            carryover_linked = bool(
                bridge_session_id
                and active_session_id
                and bridge_session_id != active_session_id
                and (
                    f"carry-over from {bridge_id_lower}" in active_last_summary
                    or bridge_id_lower in active_handoff_anchor
                )
            )
            if carryover_linked:
                alignment_status = "healthy"
                alignment_relationship = "carry_over_linked"
            else:
                alignment_status = "degraded"
                findings.append(
                    warning(
                        "memory",
                        "bridge_checkpoint_session_mismatch",
                        f"Bridge/active session mismatch detected (bridge={bridge_session_id or 'missing'}, active={active_session_id or 'missing'})",
                        config.bridge_state,
                    )
                )
    memory_checks["state_alignment"] = {
        "status": alignment_status,
        "relationship": alignment_relationship,
        "bridge_session_id": bridge_session_id or None,
        "active_session_id": active_session_id or None,
    }
    memory_governance_state, memory_governance_findings = load_memory_governance_state(config)
    findings.extend(memory_governance_findings)
    sources["memory"] = {
        "status": "healthy"
        if (
            config.vault_path.exists()
            and config.checkpoint_root.exists()
            and config.bridge_state.exists()
            and config.active_session_state.exists()
            and alignment_status != "degraded"
            and not missing_templates
            and script_entries["obsidian_bridge"]["exists"]
        )
        else "degraded",
        **memory_checks,
        "governance": memory_governance_state,
    }
    if memory_governance_state["status"] != "healthy":
        sources["memory"]["status"] = "degraded"

    automation_exists = config.automation_root.exists()
    automation_dirs = []
    if automation_exists:
        automation_dirs = sorted(path.name for path in config.automation_root.iterdir() if path.is_dir())
    else:
        findings.append(warning("automations", "missing_automation_root", "Automation root is missing", config.automation_root))
    sources["automations"] = {
        "path": str(config.automation_root),
        "exists": automation_exists,
        "status": "healthy" if automation_exists else "degraded",
        "entries": automation_dirs,
    }

    codex_ckpt = discover_command("CODEX_CKPT_CMD", "codex_ckpt", "/Users/tom/bin/codex_ckpt")
    session_ckpt = discover_command("SESSION_CKPT_CMD", "session_ckpt", "/Users/tom/bin/session_ckpt")
    if config.codex_ckpt_cmd is not None:
        codex_ckpt = command_from_path(config.codex_ckpt_cmd, "config")
    if config.session_ckpt_cmd is not None:
        session_ckpt = command_from_path(config.session_ckpt_cmd, "config")
    continuity_entrypoint_path = config.scripts_dir / "codex_continue_here"
    continuity_entrypoint = {
        "path": str(continuity_entrypoint_path),
        "exists": continuity_entrypoint_path.exists(),
        "executable": continuity_entrypoint_path.exists() and os.access(continuity_entrypoint_path, os.X_OK),
    }
    for label, command in (("codex_ckpt", codex_ckpt), ("session_ckpt", session_ckpt)):
        if not command["exists"]:
            findings.append(warning("commands", "missing_command", f"Command not found: {label}", Path(command["path"])))
    if not continuity_entrypoint["exists"] or not continuity_entrypoint["executable"]:
        findings.append(
            warning(
                "commands",
                "missing_continuity_entrypoint",
                "Continuity entrypoint is missing or not executable: scripts/codex_continue_here",
                continuity_entrypoint_path,
            )
        )
    sources["commands"] = {
        "status": "healthy"
        if codex_ckpt["exists"] and session_ckpt["exists"] and continuity_entrypoint["exists"] and continuity_entrypoint["executable"]
        else "degraded",
        "codex_ckpt": codex_ckpt,
        "session_ckpt": session_ckpt,
        "continuity_entrypoint": continuity_entrypoint,
    }

    capability_snapshot = build_capability_snapshot(
        inventory,
        work_modes_meta,
        continuity_entrypoint=continuity_entrypoint,
        benchmark_cases_exists=benchmark_cases_exists,
        benchmark_publish_chain_status=publish_chain_status,
        runtime_overlays=runtime_overlays,
        skill_iteration=skill_iteration_state,
        skill_discovery=skill_discovery_state,
        skill_route=skill_route_state,
        memory_governance=memory_governance_state,
    )
    return sources, findings, capability_snapshot


def path_state(path: Path) -> dict[str, Any]:
    return {"path": str(path), "exists": path.exists(), "readable": path.exists() and os.access(path, os.R_OK)}


def discover_command(env_name: str, label: str, default_path: str) -> dict[str, Any]:
    raw = os.getenv(env_name)
    source = "env" if raw else "default"
    if raw:
        path = Path(raw).expanduser()
    else:
        path = Path(default_path).expanduser()
    if not path.exists():
        which = shutil.which(label)
        if which:
            path = Path(which)
            source = "which"
    return {"path": str(path.resolve() if path.exists() else path), "exists": path.exists(), "source": source}


def command_from_path(path: Path, source: str) -> dict[str, Any]:
    return {"path": str(path.resolve() if path.exists() else path), "exists": path.exists(), "source": source}


def resolve_session_ckpt_command(config: HubConfig) -> Path:
    command = command_from_path(config.session_ckpt_cmd, "config") if config.session_ckpt_cmd is not None else discover_command(
        "SESSION_CKPT_CMD",
        "session_ckpt",
        "/Users/tom/bin/session_ckpt",
    )
    if not command["exists"]:
        raise HubRuntimeError(f"session_ckpt command not found: {command['path']}")
    return Path(command["path"])


def load_recall_payload(config: HubConfig, target: Path, lane: str) -> dict[str, Any] | None:
    try:
        session_ckpt = resolve_session_ckpt_command(config)
    except HubRuntimeError:
        return None
    cmd = [str(session_ckpt), "recall", "--dir", str(target), "--json"]
    if lane:
        cmd.extend(["--lane", lane])
    result = subprocess.run(
        cmd,
        cwd=config.workspace_root,
        capture_output=True,
        text=True,
        env=os.environ.copy(),
    )
    if result.returncode != 0:
        return None
    try:
        payload = json.loads(result.stdout or "{}")
    except json.JSONDecodeError:
        return None
    return payload if isinstance(payload, dict) else None


def extract_continuity_hint(payload: dict[str, Any] | None) -> dict[str, str] | None:
    if not isinstance(payload, dict):
        return None
    continuation = payload.get("continuation", {})
    if not isinstance(continuation, dict):
        return None
    selected = continuation.get("selected", {})
    if not isinstance(selected, dict):
        return None
    source = str(selected.get("source", "")).strip()
    if not source:
        return None
    summary = str(selected.get("summary", "")).strip()
    next_step = str(selected.get("next_step", "")).strip()
    source_path = str(selected.get("source_path", "")).strip()
    event_time = str(selected.get("event_time", "")).strip() or str(selected.get("updated_at", "")).strip()
    rank_explanation = str(selected.get("rank_explanation", "")).strip()
    return {
        "source": source,
        "source_path": source_path,
        "summary": summary,
        "next_step": next_step,
        "event_time": event_time,
        "rank_explanation": rank_explanation,
    }


def continuity_action(continuity: dict[str, str] | None) -> str | None:
    if not continuity:
        return None
    source = continuity.get("source", "")
    preview = continuity.get("next_step") or continuity.get("summary") or continuity.get("source_path") or "existing project memory"
    preview = re.sub(r"\s+", " ", preview).strip()
    if len(preview) > 140:
        preview = f"{preview[:137]}..."
    return f"Continue from the existing `{source}` memory before starting from scratch: {preview}"


def extract_recent_memory_report_paths(entry: dict[str, Any]) -> list[str]:
    candidates: list[str] = []
    sync = entry.get("sync", {})
    if isinstance(sync, dict):
        for key in ("report_path",):
            value = sync.get(key)
            if isinstance(value, str) and value.strip():
                candidates.append(value.strip())
        sync_entry = sync.get("entry", {})
        if isinstance(sync_entry, dict):
            for key in ("report_path", "daily_path", "source_path"):
                value = sync_entry.get(key)
                if isinstance(value, str) and value.strip() and "FOLDER_PROGRESS_" in value:
                    candidates.append(value.strip())
    return sorted(dict.fromkeys(candidates))


def latest_memory_window(payload: dict[str, Any]) -> tuple[str | None, dict[str, Any] | None]:
    window_runs = payload.get("window_runs", {})
    if not isinstance(window_runs, dict):
        return None, None
    best_window = None
    best_entry = None
    best_time = None
    for window in ("daily", "weekly"):
        entry = window_runs.get(window)
        if not isinstance(entry, dict):
            continue
        generated_at = parse_datetime_any(entry.get("generated_at"))
        if generated_at is None:
            continue
        if best_time is None or generated_at > best_time:
            best_time = generated_at
            best_window = window
            best_entry = entry
    return best_window, best_entry


def bucket_rank(bucket: str) -> int:
    return {"archive_candidate": 0, "summary_only": 1, "durable": 2}.get(bucket, -1)


def salience_level_for_score(score: float) -> str:
    if score >= 120:
        return "high"
    if score >= 60:
        return "medium"
    return "low"


def decay_state_for_timestamp(raw: Any, now: dt.datetime | None = None) -> str:
    parsed = parse_datetime_any(raw)
    if parsed is None:
        return "cool"
    current = now or dt.datetime.now(dt.timezone.utc)
    age_days = max(0.0, (current - parsed).total_seconds() / 86400.0)
    if age_days <= 7:
        return "hot"
    if age_days <= 30:
        return "warm"
    return "cool"


def aggregate_memory_governance_entries(window_runs: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, int]]:
    merged: dict[str, dict[str, Any]] = {}
    current = dt.datetime.now(dt.timezone.utc)
    for window, run in window_runs.items():
        if not isinstance(run, dict):
            continue
        entries = run.get("entries", [])
        if not isinstance(entries, list):
            continue
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            folder_path = entry.get("folder_path")
            bucket = entry.get("bucket", "archive_candidate")
            if not isinstance(folder_path, str) or not folder_path:
                continue
            existing = merged.get(folder_path)
            selected_context = entry.get("selected_count_context")
            if not isinstance(selected_context, dict):
                selected_context = {}
            if existing is None:
                merged[folder_path] = {
                    "folder_path": folder_path,
                    "bucket": bucket,
                    "reasons": list(entry.get("reasons", [])) if isinstance(entry.get("reasons", []), list) else [],
                    "report_paths": list(entry.get("report_paths", [])) if isinstance(entry.get("report_paths", []), list) else [],
                    "selected_count_context": dict(selected_context),
                    "appeared_in_previous_run": bool(entry.get("appeared_in_previous_run", False)),
                    "windows": [window],
                    "activity_score": float(entry.get("activity_score", 0.0) or 0.0),
                    "salience_score": float(entry.get("salience_score", 0.0) or 0.0),
                    "combined_score": float(entry.get("combined_score", 0.0) or 0.0),
                    "last_reinforced_at": iso_utc(entry.get("last_reinforced_at")) or iso_utc(run.get("generated_at")),
                    "last_retrieved_at": iso_utc(entry.get("last_retrieved_at")) or iso_utc(run.get("generated_at")),
                }
                continue
            if bucket_rank(bucket) > bucket_rank(existing["bucket"]):
                existing["bucket"] = bucket
            existing["reasons"] = sorted(dict.fromkeys(existing["reasons"] + list(entry.get("reasons", []))))
            existing["report_paths"] = sorted(dict.fromkeys(existing["report_paths"] + list(entry.get("report_paths", []))))
            existing["appeared_in_previous_run"] = existing["appeared_in_previous_run"] or bool(entry.get("appeared_in_previous_run", False))
            existing["windows"] = sorted(dict.fromkeys(existing["windows"] + [window]))
            existing["selected_count_context"].update(selected_context)
            existing["activity_score"] = max(float(existing.get("activity_score", 0.0) or 0.0), float(entry.get("activity_score", 0.0) or 0.0))
            existing["salience_score"] = max(float(existing.get("salience_score", 0.0) or 0.0), float(entry.get("salience_score", 0.0) or 0.0))
            existing["combined_score"] = max(float(existing.get("combined_score", 0.0) or 0.0), float(entry.get("combined_score", 0.0) or 0.0))
            for key in ("last_reinforced_at", "last_retrieved_at"):
                candidate_time = iso_utc(entry.get(key)) or iso_utc(run.get("generated_at"))
                if candidate_time and (not existing.get(key) or candidate_time > str(existing.get(key))):
                    existing[key] = candidate_time
    for entry in merged.values():
        entry["salience_level"] = salience_level_for_score(float(entry.get("salience_score", 0.0) or 0.0))
        entry["decay_state"] = decay_state_for_timestamp(entry.get("last_reinforced_at"), now=current)
    entries = sorted(merged.values(), key=lambda item: (-bucket_rank(item["bucket"]), -float(item.get("combined_score", 0.0)), item["folder_path"]))
    counts = {
        "durable": sum(1 for entry in entries if entry["bucket"] == "durable"),
        "summary_only": sum(1 for entry in entries if entry["bucket"] == "summary_only"),
        "archive_candidate": sum(1 for entry in entries if entry["bucket"] == "archive_candidate"),
        "hot": sum(1 for entry in entries if entry.get("decay_state") == "hot"),
        "warm": sum(1 for entry in entries if entry.get("decay_state") == "warm"),
        "cool": sum(1 for entry in entries if entry.get("decay_state") == "cool"),
    }
    return entries, counts


def build_memory_governance_registry_payload(
    config: HubConfig,
    *,
    window: str,
    root: Path,
    recent_memory: dict[str, Any],
    previous_payload: dict[str, Any],
    overlay_targets: set[str],
    closeout_targets: set[str],
) -> dict[str, Any]:
    if window not in MEMORY_TRIAGE_WINDOWS:
        raise HubRuntimeError(f"Unsupported memory triage window: {window}")
    previous_runs = previous_payload.get("window_runs", {})
    previous_window = previous_runs.get(window) if isinstance(previous_runs, dict) else None
    previous_entries = previous_window.get("entries", []) if isinstance(previous_window, dict) else []
    previous_by_folder = {
        canonicalize_path_text(entry.get("folder_path")) or entry["folder_path"]: entry
        for entry in previous_entries
        if isinstance(entry, dict) and isinstance(entry.get("folder_path"), str)
    }

    selected_folders = recent_memory.get("selected_folders", [])
    if not isinstance(selected_folders, list):
        raise HubRuntimeError("recent-memory JSON must contain list field `selected_folders`.")

    generated_at = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    run_entries: list[dict[str, Any]] = []
    for selected in selected_folders:
        if not isinstance(selected, dict):
            continue
        raw_folder_path = selected.get("folder")
        if not isinstance(raw_folder_path, str) or not raw_folder_path:
            continue
        folder_path = canonicalize_path_text(raw_folder_path) or raw_folder_path
        report_paths = extract_recent_memory_report_paths(selected)
        appeared_previous = folder_path in previous_by_folder
        has_overlay = folder_path in overlay_targets
        has_closeout = folder_path in closeout_targets
        activity = selected.get("activity", {})
        activity_score = 0.0
        salience_score = 0.0
        combined_score = 0.0
        if isinstance(activity, dict):
            activity_score = float(activity.get("activity_score", 0.0) or 0.0)
            salience_score = float(activity.get("salience_score", 0.0) or 0.0)
            combined_score = float(activity.get("combined_score", activity.get("score", 0.0)) or 0.0)
        if combined_score <= 0:
            combined_score = round(activity_score + salience_score, 2)
        reasons: list[str] = []
        if report_paths:
            reasons.append("generated_report_path")
        if appeared_previous:
            reasons.append("appeared_in_previous_run")
        if has_overlay:
            reasons.append("existing_overlay")
        if has_closeout:
            reasons.append("existing_closeout")
        has_report = bool(report_paths)
        durability_signals = sum(1 for value in (has_report, appeared_previous, has_overlay, has_closeout) if value)
        if durability_signals >= 2:
            bucket = "durable"
        elif durability_signals == 1:
            bucket = "summary_only"
        else:
            bucket = "archive_candidate"
        previous_entry = previous_by_folder.get(folder_path, {})
        previous_reinforced = previous_entry.get("last_reinforced_at") if isinstance(previous_entry, dict) else None
        previous_retrieved = previous_entry.get("last_retrieved_at") if isinstance(previous_entry, dict) else None
        salience_level = salience_level_for_score(salience_score)
        reinforced_at = generated_at if bucket in {"durable", "summary_only"} else iso_utc(previous_reinforced)
        run_entries.append(
            {
                "folder_path": folder_path,
                "bucket": bucket,
                "reasons": reasons,
                "report_paths": report_paths,
                "selected_count_context": {window: recent_memory.get("selected_count", 0)},
                "appeared_in_previous_run": appeared_previous,
                "windows": [window],
                "activity_score": round(activity_score, 2),
                "salience_score": round(salience_score, 2),
                "combined_score": round(combined_score, 2),
                "last_reinforced_at": reinforced_at,
                "last_retrieved_at": generated_at,
                "salience_level": salience_level,
                "decay_state": decay_state_for_timestamp(reinforced_at, now=dt.datetime.now(dt.timezone.utc)),
            }
        )

    run_counts = {
        "durable_count": sum(1 for entry in run_entries if entry["bucket"] == "durable"),
        "summary_only_count": sum(1 for entry in run_entries if entry["bucket"] == "summary_only"),
        "archive_candidate_count": sum(1 for entry in run_entries if entry["bucket"] == "archive_candidate"),
    }
    previous_durable = {
        entry["folder_path"]
        for entry in previous_entries
        if isinstance(entry, dict) and entry.get("bucket") == "durable" and isinstance(entry.get("folder_path"), str)
    }
    current_durable = {entry["folder_path"] for entry in run_entries if entry["bucket"] == "durable"}
    window_run = {
        "window": window,
        "generated_at": generated_at,
        "root": str(root),
        "days": recent_memory.get("days"),
        "top": recent_memory.get("top"),
        "selected_count": recent_memory.get("selected_count", 0),
        **run_counts,
        "durable_diff_added": sorted(current_durable - previous_durable),
        "durable_diff_removed": sorted(previous_durable - current_durable),
        "entries": run_entries,
    }
    window_runs = previous_payload.get("window_runs", {})
    if not isinstance(window_runs, dict):
        window_runs = {"daily": None, "weekly": None}
    window_runs[window] = window_run
    aggregate_entries, aggregate_counts = aggregate_memory_governance_entries(window_runs)
    return {
        "generated_at": generated_at,
        "stale_session_days": SESSION_STALE_DAYS,
        "retrieval_mode": "semantic-lite",
        "window_runs": {
            "daily": window_runs.get("daily"),
            "weekly": window_runs.get("weekly"),
        },
        "durable_count": aggregate_counts["durable"],
        "summary_only_count": aggregate_counts["summary_only"],
        "archive_candidate_count": aggregate_counts["archive_candidate"],
        "hot_count": aggregate_counts["hot"],
        "warm_count": aggregate_counts["warm"],
        "cool_count": aggregate_counts["cool"],
        "entries": aggregate_entries,
    }


def render_memory_governance_markdown(payload: dict[str, Any]) -> str:
    window_runs = payload.get("window_runs", {})
    daily = window_runs.get("daily", {}) if isinstance(window_runs, dict) and isinstance(window_runs.get("daily"), dict) else {}
    weekly = window_runs.get("weekly", {}) if isinstance(window_runs, dict) and isinstance(window_runs.get("weekly"), dict) else {}
    lines = [
        "# Memory Governance",
        "",
        f"- Generated at: `{payload.get('generated_at') or 'none'}`",
        f"- Stale session threshold: `{payload.get('stale_session_days', SESSION_STALE_DAYS)} days`",
        f"- Retrieval mode: `{payload.get('retrieval_mode', 'semantic-lite')}`",
        f"- Durable: `{payload.get('durable_count', 0)}`",
        f"- Summary only: `{payload.get('summary_only_count', 0)}`",
        f"- Archive candidates: `{payload.get('archive_candidate_count', 0)}`",
        f"- Decay: `hot={payload.get('hot_count', 0)}` `warm={payload.get('warm_count', 0)}` `cool={payload.get('cool_count', 0)}`",
        f"- Advisory: `{'no durable memory yet; prefer overlay + closeout or generated reports before long-gap resume' if payload.get('durable_count', 0) == 0 and payload.get('entries') else 'durable memory available'}`",
        "",
        "## Daily Triage",
        "",
        f"- Latest run: `{daily.get('generated_at') or 'none'}`",
        f"- selected_count: `{daily.get('selected_count', 0)}`",
        f"- durable=`{daily.get('durable_count', 0)}` summary_only=`{daily.get('summary_only_count', 0)}` archive_candidate=`{daily.get('archive_candidate_count', 0)}`",
        "",
        "## Weekly Triage",
        "",
        f"- Latest run: `{weekly.get('generated_at') or 'none'}`",
        f"- selected_count: `{weekly.get('selected_count', 0)}`",
        f"- durable=`{weekly.get('durable_count', 0)}` summary_only=`{weekly.get('summary_only_count', 0)}` archive_candidate=`{weekly.get('archive_candidate_count', 0)}`",
    ]
    added = weekly.get("durable_diff_added", []) if isinstance(weekly, dict) else []
    removed = weekly.get("durable_diff_removed", []) if isinstance(weekly, dict) else []
    lines.extend(["", "## Weekly Durable Drift", ""])
    lines.append(f"- Added: {', '.join(f'`{path}`' for path in added[:5]) if added else 'none'}")
    lines.append(f"- Removed: {', '.join(f'`{path}`' for path in removed[:5]) if removed else 'none'}")
    lines.extend(["", "## Durable Folders", ""])
    durable_entries = [entry for entry in payload.get("entries", []) if isinstance(entry, dict) and entry.get("bucket") == "durable"]
    if durable_entries:
        for entry in durable_entries[:10]:
            reason_preview = ", ".join(entry.get("reasons", [])) or "no explicit reasons"
            lines.append(
                f"- `{entry['folder_path']}` ({reason_preview}; salience=`{entry.get('salience_level', 'low')}` decay=`{entry.get('decay_state', 'cool')}`)"
            )
    else:
        lines.append("- none")
    lines.extend(["", "## Archive Candidates", ""])
    archive_entries = [entry for entry in payload.get("entries", []) if isinstance(entry, dict) and entry.get("bucket") == "archive_candidate"]
    if archive_entries:
        for entry in archive_entries[:10]:
            lines.append(f"- `{entry['folder_path']}`")
    else:
        lines.append("- none")
    lines.extend(["", "## Generated Report Paths", ""])
    report_paths = []
    for entry in payload.get("entries", []):
        if not isinstance(entry, dict):
            continue
        report_paths.extend(value for value in entry.get("report_paths", []) if isinstance(value, str) and value)
    report_paths = sorted(dict.fromkeys(report_paths))
    if report_paths:
        for path in report_paths[:20]:
            lines.append(f"- `{path}`")
    else:
        lines.append("- none")
    lines.extend(["", "## Decay Buckets", ""])
    for bucket in ("hot", "warm", "cool"):
        members = [
            entry for entry in payload.get("entries", [])
            if isinstance(entry, dict) and entry.get("decay_state") == bucket
        ]
        preview = ", ".join(f"`{entry['folder_path']}`" for entry in members[:5]) if members else "none"
        lines.append(f"- {bucket}: {preview}")
    lines.append("")
    return "\n".join(lines)


def load_session_index_map(config: HubConfig) -> dict[str, dict[str, Any]]:
    path = codex_session_index_path(config)
    if not path.exists():
        return {}
    records: dict[str, dict[str, Any]] = {}
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise HubRuntimeError(f"Invalid session index JSON at {path}:{lineno} ({exc})") from exc
        if isinstance(record, dict) and isinstance(record.get("id"), str):
            records[record["id"]] = record
    return records


def load_thread_row(config: HubConfig, thread_id: str) -> dict[str, Any] | None:
    path = codex_state_db_path(config)
    if not path.exists():
        return None
    try:
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT id, title, cwd, archived, updated_at, created_at FROM threads WHERE id = ?",
            (thread_id,),
        ).fetchone()
    except sqlite3.DatabaseError as exc:
        raise HubRuntimeError(f"Unable to read thread metadata from {path}: {exc}") from exc
    finally:
        if "conn" in locals():
            conn.close()
    return dict(row) if row is not None else None


def build_session_gate_result(config: HubConfig, thread_id: str | None, cwd_arg: str | None) -> dict[str, Any]:
    if not thread_id:
        state_payload = load_json_file(config.active_session_state, {})
        if not isinstance(state_payload, dict) or not state_payload:
            raise HubRuntimeError("session-gate requires --thread-id or a readable active session state.")
        updated_at = parse_datetime_any(state_payload.get("last_checkpoint_at")) or parse_datetime_any(state_payload.get("started_at"))
        if updated_at is None:
            raise HubRuntimeError("Active session state does not contain a usable timestamp for checkpoint-linked advisory.")
        cwd = cwd_arg or coerce_string(state_payload.get("cwd"), "cwd") or cwd_arg
        if cwd:
            cwd = str(Path(cwd).expanduser().resolve())
        brief_path = None
        overlay_registry = load_runtime_overlay_registry(config)
        if cwd:
            overlay_entry = overlay_entry_for_target(overlay_registry, Path(cwd))
            if overlay_entry:
                brief_path = overlay_entry.get("brief_path")
        memory_payload = load_memory_governance_registry(config) if memory_governance_registry_path(config).exists() else default_memory_governance_registry()
        latest_window, latest_window_entry = latest_memory_window(memory_payload)
        age_days = round((dt.datetime.now(dt.timezone.utc) - updated_at).total_seconds() / 86400, 3)
        return {
            "thread_id": "",
            "title": str(state_payload.get("topic", "")).strip(),
            "cwd": cwd,
            "updated_at": updated_at.isoformat(timespec="seconds"),
            "updated_at_sources": {
                "sqlite": None,
                "session_index": None,
            },
            "age_days": age_days,
            "archived": False,
            "archived_source": "active_checkpoint_state",
            "metadata_status": "checkpoint_only",
            "recommendation": "checkpoint_linked_advisory" if age_days <= SESSION_STALE_DAYS else "stale_new_session",
            "recommended_brief_path": brief_path,
            "recommended_memory_summary_path": str(memory_governance_status_path(config)) if memory_governance_status_path(config).exists() else None,
            "recommended_memory_window": latest_window,
            "recommended_memory_generated_at": latest_window_entry.get("generated_at") if isinstance(latest_window_entry, dict) else None,
        }

    index_map = load_session_index_map(config)
    index_entry = index_map.get(thread_id)
    thread_row = load_thread_row(config, thread_id)
    if index_entry is None and thread_row is None:
        raise HubRuntimeError(f"Unknown thread id: {thread_id}")

    title = None
    cwd = None
    archived = False
    archived_source = "unknown"
    metadata_status = "unknown"
    db_updated_at = None
    index_updated_at = None
    if isinstance(thread_row, dict):
        title = thread_row.get("title")
        cwd = thread_row.get("cwd")
        archived = bool(thread_row.get("archived"))
        archived_source = "sqlite"
        db_updated_at = parse_datetime_any(thread_row.get("updated_at"))
    if title is None and isinstance(index_entry, dict):
        title = index_entry.get("thread_name")
    if cwd_arg:
        cwd = str(Path(cwd_arg).expanduser().resolve())
    if isinstance(index_entry, dict):
        index_updated_at = parse_datetime_any(index_entry.get("updated_at"))
    available_timestamps = [value for value in (db_updated_at, index_updated_at) if value is not None]
    updated_at = max(available_timestamps) if available_timestamps else None
    if updated_at is None:
        raise HubRuntimeError(f"Could not determine updated_at for thread: {thread_id}")
    if thread_row is not None and index_entry is not None:
        metadata_status = "merged"
    elif thread_row is not None:
        metadata_status = "sqlite_only"
    else:
        metadata_status = "index_only"
    age_days = round((dt.datetime.now(dt.timezone.utc) - updated_at).total_seconds() / 86400, 3)
    if metadata_status == "index_only":
        recommendation = "stale_new_session"
    elif archived or age_days > SESSION_STALE_DAYS:
        recommendation = "stale_new_session"
    else:
        recommendation = "fresh_resume"

    brief_path = None
    overlay_registry = load_runtime_overlay_registry(config)
    if cwd:
        overlay_entry = overlay_entry_for_target(overlay_registry, Path(cwd))
        if overlay_entry:
            brief_path = overlay_entry.get("brief_path")

    memory_payload = load_memory_governance_registry(config) if memory_governance_registry_path(config).exists() else default_memory_governance_registry()
    latest_window, latest_window_entry = latest_memory_window(memory_payload)
    memory_summary_path = str(memory_governance_status_path(config)) if memory_governance_status_path(config).exists() else None
    return {
        "thread_id": thread_id,
        "title": title or "",
        "cwd": cwd,
        "updated_at": updated_at.isoformat(timespec="seconds"),
        "updated_at_sources": {
            "sqlite": db_updated_at.isoformat(timespec="seconds") if db_updated_at else None,
            "session_index": index_updated_at.isoformat(timespec="seconds") if index_updated_at else None,
        },
        "age_days": age_days,
        "archived": archived,
        "archived_source": archived_source,
        "metadata_status": metadata_status,
        "recommendation": recommendation,
        "recommended_brief_path": brief_path,
        "recommended_memory_summary_path": memory_summary_path,
        "recommended_memory_window": latest_window,
        "recommended_memory_generated_at": latest_window_entry.get("generated_at") if isinstance(latest_window_entry, dict) else None,
    }


def render_session_gate_markdown(result: dict[str, Any]) -> str:
    lines = [
        "# Session Gate",
        "",
        f"- Thread ID: `{result['thread_id']}`",
        f"- Title: {result['title'] or '`unknown`'}",
        f"- CWD: `{result['cwd'] or 'unknown'}`",
        f"- Updated at: `{result['updated_at']}`",
        f"- Updated-at sources: `sqlite={result['updated_at_sources'].get('sqlite') or 'none'}` `session_index={result['updated_at_sources'].get('session_index') or 'none'}`",
        f"- Age days: `{result['age_days']}`",
        f"- Archived: `{result['archived']}`",
        f"- Archived source: `{result['archived_source']}`",
        f"- Metadata status: `{result['metadata_status']}`",
        f"- Recommendation: `{result['recommendation']}`",
        f"- Recommended brief path: `{result['recommended_brief_path'] or 'none'}`",
        f"- Recommended memory summary: `{result['recommended_memory_summary_path'] or 'none'}`",
        f"- Recommended memory window: `{result['recommended_memory_window'] or 'none'}`",
        f"- Recommended memory generated at: `{result['recommended_memory_generated_at'] or 'none'}`",
    ]
    lines.append("")
    return "\n".join(lines)


def collect_overlay_targets(config: HubConfig) -> set[str]:
    path = runtime_overlay_registry_path(config)
    if not path.exists():
        return set()
    payload = load_runtime_overlay_registry(config)
    entries = payload.get("entries", [])
    if not isinstance(entries, list):
        return set()
    return {
        canonicalize_path_text(entry["target_path"]) or str(entry["target_path"])
        for entry in entries
        if isinstance(entry, dict) and isinstance(entry.get("target_path"), str) and entry.get("target_path")
    }


def collect_closeout_targets(config: HubConfig) -> set[str]:
    path = skill_iteration_registry_path(config)
    if not path.exists():
        return set()
    payload = load_skill_iteration_registry(config)
    closeouts = payload.get("closeouts", [])
    if not isinstance(closeouts, list):
        return set()
    return {
        canonicalize_path_text(entry["target_path"]) or str(entry["target_path"])
        for entry in closeouts
        if isinstance(entry, dict) and isinstance(entry.get("target_path"), str) and entry.get("target_path")
    }


def run_recent_memory(config: HubConfig, window: str, root: Path) -> dict[str, Any]:
    if window not in MEMORY_TRIAGE_WINDOWS:
        raise HubRuntimeError(f"Unsupported memory triage window: {window}")
    session_ckpt = resolve_session_ckpt_command(config)
    window_cfg = MEMORY_TRIAGE_WINDOWS[window]
    cmd = [
        str(session_ckpt),
        "recent-memory",
        "--root",
        str(root),
        "--lane",
        MEMORY_DEFAULT_LANE,
        "--days",
        str(window_cfg["days"]),
        "--top",
        str(window_cfg["top"]),
        "--json",
    ]
    result = subprocess.run(
        cmd,
        cwd=config.workspace_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise HubRuntimeError(
            f"session_ckpt recent-memory failed for `{window}` window (exit {result.returncode}): {result.stderr.strip() or result.stdout.strip()}"
        )
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise HubRuntimeError(f"Invalid JSON from session_ckpt recent-memory for `{window}` window ({exc})") from exc
    if not isinstance(payload, dict):
        raise HubRuntimeError("session_ckpt recent-memory must return a JSON object.")
    if not isinstance(payload.get("selected_folders", []), list):
        raise HubRuntimeError("recent-memory JSON must contain list field `selected_folders`.")
    return payload


def do_memory_triage(config: HubConfig, window: str, root_arg: str | None) -> int:
    root = resolve_memory_root(config, root_arg)
    previous_payload = load_memory_governance_registry(config) if memory_governance_registry_path(config).exists() else default_memory_governance_registry()
    recent_memory = run_recent_memory(config, window, root)
    overlay_targets = collect_overlay_targets(config)
    closeout_targets = collect_closeout_targets(config)
    payload = build_memory_governance_registry_payload(
        config,
        window=window,
        root=root,
        recent_memory=recent_memory,
        previous_payload=previous_payload,
        overlay_targets=overlay_targets,
        closeout_targets=closeout_targets,
    )
    save_memory_governance_registry(config, payload)
    status_path = memory_governance_status_path(config)
    ensure_repo_targets(config, {"memory_governance_status_md": status_path})
    status_path.write_text(render_memory_governance_markdown(payload), encoding="utf-8")
    print(status_path.read_text(encoding="utf-8"), end="")
    return 0


def do_session_gate(config: HubConfig, thread_id: str, cwd_arg: str | None) -> int:
    result = build_session_gate_result(config, thread_id, cwd_arg)
    print(render_session_gate_markdown(result), end="")
    if result["recommendation"] in {"fresh_resume", "checkpoint_linked_advisory"}:
        return 0
    if result["recommendation"] == "stale_new_session":
        return 2
    return 1


def warning(subsystem: str, code: str, message: str, path: Path) -> dict[str, str]:
    return {
        "severity": "warning",
        "subsystem": subsystem,
        "code": code,
        "message": message,
        "path": str(path),
    }


def run_live_checks(config: HubConfig, mode: str) -> tuple[dict[str, Any], dict[str, Path], list[dict[str, str]]]:
    if mode == "refresh":
        targets = canonical_artifact_paths(config)
        ensure_repo_targets(config, targets)
        config.contexts_dir.mkdir(parents=True, exist_ok=True)
        check_targets = {
            "agent_benchmark_json": targets["agent_benchmark_json"],
            "agent_benchmark_md": targets["agent_benchmark_md"],
            "agent_benchmark_global_json": targets["agent_benchmark_global_json"],
            "agent_benchmark_global_md": targets["agent_benchmark_global_md"],
            "router_regression_json": targets["router_regression_json"],
            "skill_graph_md": targets["skill_graph_md"],
        }
    else:
        tmpdir = Path(tempfile.mkdtemp(prefix="system-hub-doctor-"))
        check_targets = {
            "agent_benchmark_json": tmpdir / "agent_benchmark_baseline_workspace.json",
            "agent_benchmark_md": tmpdir / "agent_benchmark_baseline_workspace.md",
            "agent_benchmark_global_json": tmpdir / "agent_benchmark_baseline_global.json",
            "agent_benchmark_global_md": tmpdir / "agent_benchmark_baseline_global.md",
            "router_regression_json": tmpdir / "router_regression_latest.json",
            "skill_graph_md": tmpdir / "skill_graph.md",
        }
        targets = canonical_artifact_paths(config)

    env = {"CODEX_HOME": str(config.codex_home)}
    checks: dict[str, Any] = {}
    findings: list[dict[str, str]] = []
    checks["agent_benchmark"] = run_command(
        [
            sys.executable,
            str(config.scripts_dir / "run_agent_benchmark.py"),
            "--scope",
            "workspace",
            "--benchmark-kind",
            "parsed_overlay",
            "--cases",
            str(config.contexts_dir / "agent_benchmark_cases.json"),
            "--json-report",
            str(check_targets["agent_benchmark_json"]),
            "--md-report",
            str(check_targets["agent_benchmark_md"]),
        ],
        cwd=config.workspace_root,
        env=env,
        expected_outputs=[check_targets["agent_benchmark_json"], check_targets["agent_benchmark_md"]],
    )
    checks["agent_benchmark_global"] = run_command(
        [
            sys.executable,
            str(config.scripts_dir / "run_agent_benchmark.py"),
            "--scope",
            "global",
            "--benchmark-kind",
            "policy_simulation",
            "--cases",
            str(config.contexts_dir / "agent_benchmark_cases.json"),
            "--json-report",
            str(check_targets["agent_benchmark_global_json"]),
            "--md-report",
            str(check_targets["agent_benchmark_global_md"]),
        ],
        cwd=config.workspace_root,
        env=env,
        expected_outputs=[check_targets["agent_benchmark_global_json"], check_targets["agent_benchmark_global_md"]],
    )
    portability_check = run_command(
        [
            sys.executable,
            str(config.scripts_dir / "test_run_agent_benchmark.py"),
        ],
        cwd=config.workspace_root,
        env=env,
        raise_on_error=False,
    )
    checks["agent_benchmark_portability"] = portability_check
    if portability_check["exit_code"] != 0:
        findings.append(
            warning(
                "policy",
                "benchmark_portability_failed",
                "Benchmark portability check failed; publish/wrapper chain is degraded",
                config.scripts_dir / "test_run_agent_benchmark.py",
            )
        )
    router_check = run_command(
        [
            str(config.scripts_dir / "run_router_regression.sh"),
            "--json-report",
            str(check_targets["router_regression_json"]),
        ],
        cwd=config.workspace_root,
        env=env,
        expected_outputs=[check_targets["router_regression_json"]],
        raise_on_error=False,
    )
    if router_check["exit_code"] == 0:
        checks["router_regression"] = router_check
    elif router_check["exit_code"] == 2 and "Runner not found" in f"{router_check['stderr_tail']}\n{router_check['stdout_tail']}":
        router_check["status"] = "degraded"
        checks["router_regression"] = router_check
        findings.append(
            warning(
                "skills",
                "router_runner_missing",
                "Router regression runner is missing; route checks are degraded",
                config.codex_home / "skills" / "requirement-skill-router" / "scripts" / "run_router_regression.py",
            )
        )
    else:
        raise HubRuntimeError(
            f"Command failed ({router_check['exit_code']}): {' '.join(router_check['command'])}\n"
            f"{router_check['stderr_tail'] or router_check['stdout_tail']}"
        )
    skill_cmd = [
        sys.executable,
        str(config.scripts_dir / "build_skill_graph.py"),
        "--output",
        str(check_targets["skill_graph_md"]),
        "--no-mirror",
    ]
    for root in config.skill_roots:
        skill_cmd.extend(["--skill-root", str(root)])
    checks["skill_graph"] = run_command(
        skill_cmd,
        cwd=config.workspace_root,
        env=env,
        expected_outputs=[check_targets["skill_graph_md"]],
    )
    return checks, targets, findings


def scan_artifacts(config: HubConfig, targets: dict[str, Path]) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, str]]]:
    artifacts: dict[str, Any] = {}
    findings: list[dict[str, str]] = []
    stale_artifacts = []
    missing_artifacts = []
    now = dt.datetime.now(dt.timezone.utc)

    for name, path in targets.items():
        kind = artifact_kind(name)
        threshold = freshness_threshold(config, kind)
        entry = {
            "path": str(path),
            "kind": kind,
            "exists": path.exists(),
            "status": "missing",
            "updated_at": None,
            "age_hours": None,
            "freshness_hours": threshold,
            "is_stale": False,
        }
        if path.exists():
            updated_at = dt.datetime.fromtimestamp(path.stat().st_mtime, tz=dt.timezone.utc)
            age_hours = round((now - updated_at).total_seconds() / 3600, 3)
            is_stale = age_hours > threshold
            entry.update(
                {
                    "updated_at": updated_at.isoformat(timespec="seconds"),
                    "age_hours": age_hours,
                    "status": "stale" if is_stale else "fresh",
                    "is_stale": is_stale,
                }
            )
            if is_stale:
                stale_artifacts.append(name)
                findings.append(warning("artifacts", "stale_artifact", f"Artifact is stale: {name}", path))
        else:
            missing_artifacts.append(name)
            findings.append(warning("artifacts", "missing_artifact", f"Artifact is missing: {name}", path))
        artifacts[name] = entry

    freshness = {
        "system_hours": config.system_hours,
        "generated_hours": config.generated_hours,
        "report_hours": config.report_hours,
        "stale_artifacts": stale_artifacts,
        "missing_artifacts": missing_artifacts,
    }
    return artifacts, freshness, findings


def artifact_kind(name: str) -> str:
    if name.startswith("system_"):
        return "system"
    if name.endswith("_json"):
        return "generated"
    return "report"


def freshness_threshold(config: HubConfig, kind: str) -> int:
    if kind == "system":
        return config.system_hours
    if kind == "generated":
        return config.generated_hours
    return config.report_hours


def build_registry(
    config: HubConfig,
    mode: str,
    sources: dict[str, Any],
    checks: dict[str, Any],
    artifacts: dict[str, Any],
    freshness: dict[str, Any],
    findings: list[dict[str, str]],
    previous_registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    recommended_actions = suggest_actions(findings, sources, checks, previous_registry)
    overall_status = determine_overall_status(findings)
    registry = {
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "workspace": str(config.workspace_root),
        "hub_version": HUB_VERSION,
        "mode": mode,
        "config": config.to_dict(),
        "sources": sources,
        "checks": checks,
        "artifacts": artifacts,
        "freshness": freshness,
        "findings": findings,
        "recommended_actions": recommended_actions,
        "overall_status": overall_status,
    }
    if registry["overall_status"] not in OVERALL_STATES:
        raise HubRuntimeError(f"Invalid overall_status: {registry['overall_status']}")
    return registry


def determine_overall_status(findings: list[dict[str, str]]) -> str:
    return "degraded" if findings else "healthy"


def suggest_actions(
    findings: list[dict[str, str]],
    sources: dict[str, Any],
    checks: dict[str, Any],
    previous_registry: dict[str, Any] | None,
) -> list[str]:
    actions: list[str] = []
    subsystems = {finding["subsystem"] for finding in findings}
    codes = {finding["code"] for finding in findings}
    inventory = sources.get("skills", {}).get("inventory", {})
    candidate_skills = inventory.get("candidate_skills", [])
    previous_candidates = previous_registry_candidate_skills(previous_registry)
    new_candidates = sorted(set(candidate_skills) - previous_candidates)
    inventory["new_candidate_skills"] = new_candidates

    capability_snapshot = checks.get("capability_snapshot", {})
    runtime_environment = checks.get("runtime_environment", {})
    overlay_runtime = sources.get("overlay", {}).get("runtime_overlays", {})
    skill_iteration = sources.get("skills", {}).get("iteration", {})
    skill_discovery = sources.get("skills", {}).get("discovery", {})
    skill_route = sources.get("skills", {}).get("routing", {})
    memory_governance = sources.get("memory", {}).get("governance", {})
    if new_candidates:
        preview = ", ".join(f"`{name}`" for name in new_candidates[:5])
        suffix = " ..." if len(new_candidates) > 5 else ""
        actions.append(
            f"Review `policy/work_modes.toml`; newly installed skills are still unmapped to active lanes: {preview}{suffix}"
        )
    if inventory.get("missing_active_skills"):
        preview = ", ".join(f"`{name}`" for name in inventory["missing_active_skills"][:4])
        suffix = " ..." if len(inventory["missing_active_skills"]) > 4 else ""
        actions.append(f"Install or remap missing active lane skills in `policy/work_modes.toml`: {preview}{suffix}")
    if {"missing_artifact", "stale_artifact"} & codes:
        actions.append("Run `./scripts/brain.sh refresh` to rebuild the canonical workspace artifacts.")
    if "skills" in subsystems:
        actions.append("Verify `paths.skill_roots` in `policy/system_hub.toml` and restore any missing skill directories.")
    if "memory" in subsystems:
        actions.append("Verify the Obsidian and checkpoint paths in `policy/system_hub.toml` and restore missing continuity state.")
    if "missing_benchmark_cases" in codes or "missing_publish_chain_script" in codes:
        actions.append("Restore `contexts/agent_benchmark_cases.json` and the benchmark publish/portability scripts before trusting benchmark automation.")
    if "benchmark_portability_failed" in codes:
        actions.append("Run `python3 scripts/test_run_agent_benchmark.py` and repair the publish/wrapper chain until portability passes.")
    if "commands" in subsystems:
        actions.append("Install or reconfigure `codex_ckpt` and `session_ckpt`, or set `CODEX_CKPT_CMD` / `SESSION_CKPT_CMD`.")
    if "missing_continuity_entrypoint" in codes:
        actions.append("Restore `scripts/codex_continue_here` so folder-first checkpoint continuity stays discoverable.")
    if "automations" in subsystems:
        actions.append("Verify `paths.automation_root` or create the expected automation directory.")
    if "policy" in subsystems or "overlay" in subsystems:
        actions.append("Repair missing policy or overlay artifacts before trusting future refresh results.")
    if skill_iteration.get("open_proposal_count", 0):
        actions.append("Review open skill proposals with `./scripts/brain.sh skill-review` and promote or reject them explicitly.")
    if candidate_skills and not skill_discovery.get("last_query"):
        actions.append("Use `./scripts/brain.sh skill-discover \"<need>\"` before adding more skills manually; keep discovery explicit and query-driven.")
    if skill_discovery.get("last_run_status") == "degraded":
        actions.append("The latest skill discovery run degraded; rerun `./scripts/brain.sh skill-discover \"<need>\"` after checking `npx skills` availability.")
    if skill_route.get("latest_gap_detected"):
        actions.append("The latest skill route still has a workflow gap; rerun `./scripts/brain.sh skill-route \"<task>\" --path <folder>` after discovery or candidate install.")
    if overlay_runtime.get("brief_count", 0) == 0:
        actions.append("Generate a runtime brief with `./scripts/brain.sh overlay <folder>` before starting a fresh functional session.")
    if not memory_governance.get("latest_daily_generated_at") or not memory_governance.get("latest_weekly_generated_at"):
        actions.append("Run `./scripts/brain.sh memory-triage --window daily|weekly` to populate memory governance summaries before relying on stale-session advice.")
    if capability_snapshot.get("gui_surface") == "unknown":
        actions.append("Run the hub inside Codex Desktop when you want the most complete GUI and sub-agent experience.")
    if runtime_environment.get("alignment_status") == "mismatch":
        actions.append("Align shell `codex` with the Codex Desktop bundled runtime so session behavior and native features stay predictable.")
    deduped = list(dict.fromkeys(actions))
    if not deduped:
        deduped.append("No action required; the workspace hub is healthy.")
    return deduped


def previous_registry_candidate_skills(previous_registry: dict[str, Any] | None) -> set[str]:
    if not isinstance(previous_registry, dict):
        return set()
    sources = previous_registry.get("sources")
    if not isinstance(sources, dict):
        return set()
    skills = sources.get("skills")
    if not isinstance(skills, dict):
        return set()
    inventory = skills.get("inventory")
    if not isinstance(inventory, dict):
        return set()
    values = inventory.get("candidate_skills", [])
    if not isinstance(values, list):
        return set()
    return {normalize_skill_name(value) for value in values if isinstance(value, str)}


def render_status_markdown(registry: dict[str, Any]) -> str:
    generated_at = registry["generated_at"]
    overall_status = registry["overall_status"]
    stale = registry["freshness"]["stale_artifacts"]
    findings = registry["findings"]
    degraded = [finding for finding in findings if finding["subsystem"] != "artifacts"]
    capability_snapshot = registry.get("checks", {}).get("capability_snapshot", {})
    overlay_runtime = registry.get("checks", {}).get("overlay_runtime", {})
    skill_iteration = registry.get("checks", {}).get("skill_iteration", {})
    skill_discovery = registry.get("checks", {}).get("skill_discovery", {})
    skill_route = registry.get("checks", {}).get("skill_route", {})
    memory_governance = registry.get("checks", {}).get("memory_governance", {})

    lines = [
        "# System Status",
        "",
        f"- Generated at: `{generated_at}`",
        f"- Mode: `{registry['mode']}`",
        f"- Overall status: `{overall_status}`",
        "",
        "## Summary",
        "",
        f"- Findings: `{len(findings)}`",
        f"- Stale artifacts: `{len(stale)}`",
        f"- Recommended actions: `{len(registry['recommended_actions'])}`",
        "",
        "## Subsystem Status",
        "",
        "| subsystem | status | notes |",
        "| --- | --- | --- |",
    ]

    for name in ("policy", "overlay", "skills", "memory", "automations", "commands"):
        source = registry["sources"][name]
        notes = subsystem_note(name, source)
        lines.append(f"| `{name}` | `{source['status']}` | {notes} |")

    lines.extend(["", "## Stale Artifacts", ""])
    if stale:
        for name in stale:
            lines.append(f"- `{name}`")
    else:
        lines.append("- none")

    lines.extend(["", "## Degraded Dependencies", ""])
    if degraded:
        for finding in degraded:
            lines.append(
                f"- `{finding['subsystem']}` `{finding['code']}`: {finding['message']} (`{finding['path']}`)"
            )
    else:
        lines.append("- none")

    lines.extend(["", "## Capability Snapshot", ""])
    if capability_snapshot:
        command_names = ", ".join(f"`{entry['name']}`" for entry in capability_snapshot["commands"])
        active_modes = ", ".join(f"`{name}`" for name in capability_snapshot["active_modes"])
        active_skills = capability_snapshot["installed_active_skills"]
        runtime_environment = capability_snapshot.get("runtime_environment", {})
        shell_runtime = runtime_environment.get("shell_cli", {})
        desktop_runtime = runtime_environment.get("desktop_runtime", {})
        native_features = runtime_environment.get("native_features", {})
        skill_preview = ", ".join(f"`{name}`" for name in active_skills[:8]) or "none"
        if len(active_skills) > 8:
            skill_preview = f"{skill_preview} ..."
        command_source = registry.get("sources", {}).get("commands", {})
        policy_source = registry.get("sources", {}).get("policy", {})
        continuity_entrypoint = command_source.get("continuity_entrypoint", {}).get("exists", "unknown")
        benchmark_cases_exists = policy_source.get("benchmark_cases", {}).get("exists", "unknown")
        publish_chain_status = policy_source.get("benchmark_publish_chain", {}).get("status", "unknown")
        lines.extend(
            [
                f"- Runtime origin: `{capability_snapshot['runtime_origin']}`",
                f"- Runtime alignment: `{runtime_environment.get('alignment_status', 'unknown')}` preferred=`{runtime_environment.get('preferred_runtime', 'unknown')}`",
                f"- Shell CLI version: `{shell_runtime.get('version') or 'unknown'}`",
                f"- Desktop runtime version: `{desktop_runtime.get('cli_version') or 'unknown'}` app=`{desktop_runtime.get('app_version') or 'unknown'}`",
                f"- GUI surface: `{capability_snapshot['gui_surface']}`",
                f"- Sub-agent support: `{capability_snapshot['subagents']['status']}`",
                f"- Native hooks/code mode/skill controls: `hooks={native_features.get('hooks', 'unknown')}` `code_mode={native_features.get('code_mode', 'unknown')}` `skill_controls={native_features.get('bundled_skill_controls', 'unknown')}`",
                f"- Available commands: {command_names}",
                f"- Active modes: {active_modes}",
                f"- Installed active skills: {skill_preview} (`{capability_snapshot['active_skill_count']}` total)",
                f"- Candidate skills: `{capability_snapshot['candidate_skill_count']}`",
                f"- Continuity entrypoint: `{continuity_entrypoint}`",
                f"- Benchmark cases wired: `{benchmark_cases_exists}`",
                f"- Benchmark publish chain: `{publish_chain_status}`",
                f"- Memory governance: `durable={capability_snapshot['memory_governance']['durable_count']}` summary_only=`{capability_snapshot['memory_governance']['summary_only_count']}` archive=`{capability_snapshot['memory_governance']['archive_candidate_count']}`",
                f"- Memory decay: `hot={capability_snapshot['memory_governance'].get('hot_count', 0)}` `warm={capability_snapshot['memory_governance'].get('warm_count', 0)}` `cool={capability_snapshot['memory_governance'].get('cool_count', 0)}` mode=`{capability_snapshot['memory_governance'].get('retrieval_mode', 'semantic-lite')}`",
                f"- Stale session threshold: `{capability_snapshot['memory_governance']['stale_session_days']} days`",
                f"- Long context: {capability_snapshot['context_window']['note']}",
            ]
        )
    else:
        lines.append("- unavailable")

    lines.extend(["", "## Overlay Runtime", ""])
    lines.append(f"- Runtime overlays: `{overlay_runtime.get('brief_count', 0)}`")
    lines.append(f"- Latest overlay: `{overlay_runtime.get('latest_generated_at') or 'none'}`")
    lines.append(f"- Open skill proposals: `{skill_iteration.get('open_proposal_count', 0)}`")
    lines.append(f"- Latest closeout: `{skill_iteration.get('latest_closeout_at') or 'none'}`")
    lines.append(
        f"- Latest skill discovery: `{skill_discovery.get('last_query') or 'none'}` "
        f"local=`{skill_discovery.get('local_match_count', 0)}` "
        f"remote=`{skill_discovery.get('remote_match_count', 0)}`"
    )
    lines.append(
        f"- Latest skill route: `{skill_route.get('latest_task') or 'none'}` "
        f"mode=`{skill_route.get('latest_mode') or 'none'}` "
        f"gap=`{str(bool(skill_route.get('latest_gap_detected'))).lower()}`"
    )

    lines.extend(["", "## Memory Governance", ""])
    lines.append(f"- Latest daily triage: `{memory_governance.get('latest_daily_generated_at') or 'none'}`")
    lines.append(f"- Latest weekly triage: `{memory_governance.get('latest_weekly_generated_at') or 'none'}`")
    lines.append(
        f"- Durable=`{memory_governance.get('durable_count', 0)}` Summary only=`{memory_governance.get('summary_only_count', 0)}` Archive candidates=`{memory_governance.get('archive_candidate_count', 0)}`"
    )
    lines.append(
        f"- Decay=`hot:{memory_governance.get('hot_count', 0)} warm:{memory_governance.get('warm_count', 0)} cool:{memory_governance.get('cool_count', 0)}` Retrieval mode=`{memory_governance.get('retrieval_mode', 'semantic-lite')}`"
    )
    lines.append(f"- Stale session threshold: `{memory_governance.get('stale_session_days', SESSION_STALE_DAYS)} days`")

    lines.extend(["", "## Recommended Next Actions", ""])
    for action in registry["recommended_actions"]:
        lines.append(f"- {action}")
    lines.append("")
    return "\n".join(lines)


def subsystem_note(name: str, source: dict[str, Any]) -> str:
    if name == "skills":
        roots = source["roots"]
        ready = sum(1 for root in roots if root["exists"])
        inventory = source.get("inventory", {})
        iteration = source.get("iteration", {})
        discovery = source.get("discovery", {})
        return (
            f"{ready}/{len(roots)} roots available; active=`{len(inventory.get('active_installed', []))}` "
            f"candidate=`{len(inventory.get('candidate_skills', []))}` open_proposals=`{iteration.get('open_proposal_count', 0)}` "
            f"last_discovery=`{discovery.get('last_query') or 'none'}`"
        )
    if name == "memory":
        governance = source.get("governance", {})
        return (
            f"vault=`{source['vault_path']['exists']}` checkpoint=`{source['checkpoint_root']['exists']}` "
            f"durable=`{governance.get('durable_count', 0)}` stale_days=`{governance.get('stale_session_days', SESSION_STALE_DAYS)}`"
        )
    if name == "automations":
        return f"entries=`{len(source.get('entries', []))}`"
    if name == "commands":
        continuity = source.get("continuity_entrypoint", {})
        return (
            f"codex_ckpt=`{source['codex_ckpt']['exists']}` "
            f"session_ckpt=`{source['session_ckpt']['exists']}` "
            f"continue_here=`{continuity.get('exists', 'unknown')}`"
        )
    if name == "overlay":
        runtime = source.get("runtime_overlays", {})
        return (
            f"AGENTS=`{source['agents_md']['exists']}` PRINCIPLES=`{source['principles_md']['exists']}` "
            f"briefs=`{runtime.get('brief_count', 0)}`"
        )
    if name == "policy":
        missing = [key for key, entry in source["files"].items() if not entry["exists"]]
        work_modes = source.get("work_modes", {})
        benchmark_cases = source.get("benchmark_cases", {})
        publish_chain = source.get("benchmark_publish_chain", {})
        prefix = "all required files present" if not missing else f"missing `{', '.join(missing)}`"
        return (
            f"{prefix}; work_modes=`{work_modes.get('status', 'unknown')}`; "
            f"benchmark_cases=`{benchmark_cases.get('exists', 'unknown')}`; "
            f"publish_chain=`{publish_chain.get('status', 'unknown')}`"
        )
    return "-"


def write_outputs(registry: dict[str, Any], targets: dict[str, Path]) -> None:
    registry_path = targets["system_registry_json"]
    status_path = targets["system_status_md"]
    registry_path.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    status_path.write_text(render_status_markdown(registry), encoding="utf-8")


def predicted_system_artifact(path: Path, config: HubConfig) -> dict[str, Any]:
    return {
        "path": str(path),
        "kind": "system",
        "exists": True,
        "status": "fresh",
        "updated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "age_hours": 0.0,
        "freshness_hours": config.system_hours,
        "is_stale": False,
    }


def command_exit_code(overall_status: str) -> int:
    if overall_status == "healthy":
        return 0
    if overall_status == "degraded":
        return 2
    return 1


def load_previous_registry(config: HubConfig) -> dict[str, Any] | None:
    path = canonical_artifact_paths(config)["system_registry_json"]
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def do_refresh(config: HubConfig) -> int:
    previous_registry = load_previous_registry(config)
    sources, findings, capability_snapshot = scan_sources(config)
    checks, _targets, live_findings = run_live_checks(config, "refresh")
    inventory = sources["skills"]["inventory"]
    inventory["new_candidate_skills"] = sorted(set(inventory["candidate_skills"]) - previous_registry_candidate_skills(previous_registry))
    checks["overlay_runtime"] = build_overlay_runtime_check(sources)
    checks["skill_iteration"] = build_skill_iteration_check(sources)
    checks["skill_discovery"] = build_skill_discovery_check(sources)
    checks["skill_route"] = build_skill_route_check(sources)
    checks["memory_governance"] = build_memory_governance_check(sources)
    checks["capability_snapshot"] = build_capability_snapshot(
        inventory,
        sources["policy"]["work_modes"],
        new_candidate_skills=inventory["new_candidate_skills"],
        continuity_entrypoint=sources["commands"]["continuity_entrypoint"],
        benchmark_cases_exists=sources["policy"]["benchmark_cases"]["exists"],
        benchmark_publish_chain_status=sources["policy"]["benchmark_publish_chain"]["status"],
        runtime_overlays=sources["overlay"]["runtime_overlays"],
        skill_iteration=sources["skills"]["iteration"],
        skill_discovery=sources["skills"]["discovery"],
        skill_route=sources["skills"]["routing"],
        memory_governance=sources["memory"]["governance"],
    )
    checks["runtime_environment"] = build_runtime_environment_check(checks["capability_snapshot"])
    canonical_targets = canonical_artifact_paths(config)
    generated_targets = {name: path for name, path in canonical_targets.items() if not name.startswith("system_")}
    artifacts, freshness, artifact_findings = scan_artifacts(config, generated_targets)
    artifacts["system_registry_json"] = predicted_system_artifact(canonical_targets["system_registry_json"], config)
    artifacts["system_status_md"] = predicted_system_artifact(canonical_targets["system_status_md"], config)
    provisional_findings = findings + live_findings + artifact_findings
    provisional_registry = build_registry(
        config,
        "refresh",
        sources,
        checks,
        artifacts,
        freshness,
        provisional_findings,
        previous_registry=previous_registry,
    )
    write_outputs(provisional_registry, canonical_targets)

    final_artifacts, final_freshness, final_artifact_findings = scan_artifacts(config, canonical_targets)
    final_registry = build_registry(
        config,
        "refresh",
        sources,
        checks,
        final_artifacts,
        final_freshness,
        findings + live_findings + final_artifact_findings,
        previous_registry=previous_registry,
    )
    write_outputs(final_registry, canonical_targets)
    print(render_status_markdown(final_registry))
    return command_exit_code(final_registry["overall_status"])


def do_doctor(config: HubConfig) -> int:
    previous_registry = load_previous_registry(config)
    sources, findings, capability_snapshot = scan_sources(config)
    inventory = sources["skills"]["inventory"]
    inventory["new_candidate_skills"] = sorted(set(inventory["candidate_skills"]) - previous_registry_candidate_skills(previous_registry))
    checks, _targets, live_findings = run_live_checks(config, "doctor")
    checks["overlay_runtime"] = build_overlay_runtime_check(sources)
    checks["skill_iteration"] = build_skill_iteration_check(sources)
    checks["skill_discovery"] = build_skill_discovery_check(sources)
    checks["skill_route"] = build_skill_route_check(sources)
    checks["memory_governance"] = build_memory_governance_check(sources)
    checks["capability_snapshot"] = build_capability_snapshot(
        inventory,
        sources["policy"]["work_modes"],
        new_candidate_skills=inventory["new_candidate_skills"],
        continuity_entrypoint=sources["commands"]["continuity_entrypoint"],
        benchmark_cases_exists=sources["policy"]["benchmark_cases"]["exists"],
        benchmark_publish_chain_status=sources["policy"]["benchmark_publish_chain"]["status"],
        runtime_overlays=sources["overlay"]["runtime_overlays"],
        skill_iteration=sources["skills"]["iteration"],
        skill_discovery=sources["skills"]["discovery"],
        skill_route=sources["skills"]["routing"],
        memory_governance=sources["memory"]["governance"],
    )
    checks["runtime_environment"] = build_runtime_environment_check(checks["capability_snapshot"])
    artifacts, freshness, artifact_findings = scan_artifacts(config, canonical_artifact_paths(config))
    registry = build_registry(
        config,
        "doctor",
        sources,
        checks,
        artifacts,
        freshness,
        findings + live_findings + artifact_findings,
        previous_registry=previous_registry,
    )
    print(render_status_markdown(registry))
    return command_exit_code(registry["overall_status"])


def do_status(config: HubConfig) -> int:
    targets = canonical_artifact_paths(config)
    registry_path = targets["system_registry_json"]
    status_path = targets["system_status_md"]
    if not registry_path.exists() or not status_path.exists():
        print("Canonical system status outputs are missing; run `./scripts/brain.sh refresh` first.", file=sys.stderr)
        return 1
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    overall_status = registry.get("overall_status")
    if overall_status not in OVERALL_STATES:
        print(f"Invalid overall_status in {registry_path}: {overall_status}", file=sys.stderr)
        return 1
    print(status_path.read_text(encoding="utf-8"), end="")
    return command_exit_code(overall_status)


def do_capabilities(config: HubConfig) -> int:
    sources, findings, capability_snapshot = scan_sources(config)
    inventory = sources["skills"]["inventory"]
    inventory["new_candidate_skills"] = sorted(set(inventory["candidate_skills"]) - previous_registry_candidate_skills(load_previous_registry(config)))
    capability_snapshot = build_capability_snapshot(
        inventory,
        sources["policy"]["work_modes"],
        new_candidate_skills=inventory["new_candidate_skills"],
        continuity_entrypoint=sources["commands"]["continuity_entrypoint"],
        benchmark_cases_exists=sources["policy"]["benchmark_cases"]["exists"],
        benchmark_publish_chain_status=sources["policy"]["benchmark_publish_chain"]["status"],
        runtime_overlays=sources["overlay"]["runtime_overlays"],
        skill_iteration=sources["skills"]["iteration"],
        skill_discovery=sources["skills"]["discovery"],
        skill_route=sources["skills"]["routing"],
        memory_governance=sources["memory"]["governance"],
    )
    print(render_capabilities_markdown(capability_snapshot, sources, findings))
    return 0


def review_fix_adjust_skill_script(config: HubConfig) -> Path:
    path = config.codex_home / "skills" / "review-fix-adjust-loop" / "scripts" / "build_iteration_packet.py"
    if not path.exists():
        raise HubRuntimeError(f"Missing review-fix-adjust-loop script: {path}")
    return path


def render_review_loop_markdown(payload: dict[str, Any]) -> str:
    review_scope = payload.get("review_scope", [])
    route_hints = payload.get("route_hints", [])
    loop_policy = payload.get("loop_policy", {})
    convergence_states = payload.get("convergence_states", [])
    lines = [
        "# Review Loop Packet",
        "",
        f"- Workspace: `{payload.get('workspace', '')}`",
        f"- Suggested mode: `{payload.get('suggested_mode', 'unknown')}`",
        "",
        "## Changed Files",
        "",
    ]
    changed_files = payload.get("changed_files", [])
    if changed_files:
        for item in changed_files:
            lines.append(f"- `{item}`")
    else:
        lines.append("- none")
    lines.extend(["", "## Review Scope", ""])
    if review_scope:
        for item in review_scope:
            lines.append(f"- `{item['path']}` ({item['role']}, score={item['score']})")
    else:
        lines.append("- none")
    lines.extend(["", "## Route Hints", ""])
    if route_hints:
        for item in route_hints:
            lines.append(f"- `{item}`")
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "## Loop Policy",
            "",
            f"- max_loops: `{loop_policy.get('max_loops', 'unknown')}`",
            f"- min_loops_before_convergence_check: `{loop_policy.get('min_loops_before_convergence_check', 'unknown')}`",
            f"- preferred_convergence_check: `{loop_policy.get('preferred_convergence_check', 'unknown')}`",
            f"- hard_stop: `{loop_policy.get('hard_stop', 'unknown')}`",
            "",
            "## Convergence States",
            "",
        ]
    )
    if convergence_states:
        for item in convergence_states:
            lines.append(f"- `{item}`")
    else:
        lines.append("- none")
    lines.append("")
    return "\n".join(lines)


def do_review_loop(
    config: HubConfig,
    path_arg: str,
    changed: list[str],
    from_git: bool,
    max_candidates: int,
    review_limit: int,
    emit_json: bool,
) -> int:
    target = Path(path_arg).expanduser().resolve()
    if not target.exists():
        print(f"Target path does not exist: {target}", file=sys.stderr)
        return 1
    if not target.is_dir():
        print(f"Target path must be a directory: {target}", file=sys.stderr)
        return 1

    script_path = review_fix_adjust_skill_script(config)
    cmd = [
        sys.executable,
        str(script_path),
        "--workspace",
        str(target),
        "--max-candidates",
        str(max_candidates),
        "--review-limit",
        str(review_limit),
        "--json",
    ]
    if changed:
        cmd.extend(["--changed", *changed])
    if from_git or not changed:
        cmd.append("--from-git")

    result = subprocess.run(
        cmd,
        cwd=target,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        print(result.stderr.strip() or result.stdout.strip(), file=sys.stderr)
        return result.returncode
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        print(f"Invalid JSON from review-fix-adjust-loop script: {exc}", file=sys.stderr)
        return 1

    if emit_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(render_review_loop_markdown(payload), end="")
    return 0


def do_reconcile(config: HubConfig) -> int:
    report_path = reconciliation_report_path(config)
    ensure_repo_targets(config, {"folder_hub_reconciliation_md": report_path})
    entries = build_reconciliation_entries(config)
    report = render_reconciliation_markdown(config, entries)
    report_path.write_text(report, encoding="utf-8")
    print(report, end="")
    has_folder_only = any(entry["category"] == "folder_only" for entry in entries)
    return 2 if has_folder_only else 0


def render_capabilities_markdown(capability_snapshot: dict[str, Any], sources: dict[str, Any], findings: list[dict[str, str]]) -> str:
    inventory = sources["skills"]["inventory"]
    active_skills = inventory["active_installed"]
    candidate_skills = inventory["candidate_skills"]
    runtime_environment = capability_snapshot.get("runtime_environment", {})
    shell_runtime = runtime_environment.get("shell_cli", {})
    desktop_runtime = runtime_environment.get("desktop_runtime", {})
    native_features = runtime_environment.get("native_features", {})
    command_preview = ", ".join(f"`{entry['name']}`" for entry in capability_snapshot["commands"])
    mode_preview = ", ".join(f"`{name}`" for name in capability_snapshot["active_modes"])
    lines = [
        "# Capability Snapshot",
        "",
        f"- Runtime origin: `{capability_snapshot['runtime_origin']}`",
        f"- Runtime alignment: `{runtime_environment.get('alignment_status', 'unknown')}` preferred=`{runtime_environment.get('preferred_runtime', 'unknown')}`",
        f"- Shell CLI version: `{shell_runtime.get('version') or 'unknown'}`",
        f"- Desktop runtime version: `{desktop_runtime.get('cli_version') or 'unknown'}` app=`{desktop_runtime.get('app_version') or 'unknown'}`",
        f"- GUI surface: `{capability_snapshot['gui_surface']}`",
        f"- Sub-agent support: `{capability_snapshot['subagents']['status']}`",
        f"- Native hooks/code mode/skill controls: `hooks={native_features.get('hooks', 'unknown')}` `code_mode={native_features.get('code_mode', 'unknown')}` `skill_controls={native_features.get('bundled_skill_controls', 'unknown')}`",
        f"- Available commands: {command_preview}",
        f"- Active modes: {mode_preview}",
        f"- Installed active skills: `{len(active_skills)}`",
        f"- Candidate skills: `{len(candidate_skills)}`",
        f"- Continuity entrypoint: `{capability_snapshot['continuity_entrypoint']['exists']}`",
        f"- Benchmark cases wired: `{capability_snapshot['benchmark_cases_exists']}`",
        f"- Benchmark publish chain: `{capability_snapshot['benchmark_publish_chain_status']}`",
        f"- Runtime overlay briefs: `{capability_snapshot['overlay_runtime']['brief_count']}`",
        f"- Skill iteration gate: `open={capability_snapshot['skill_iteration_gate']['open_proposal_count']}` closeouts=`{capability_snapshot['skill_iteration_gate']['closeout_count']}`",
        f"- Skill discovery: `query={capability_snapshot['skill_discovery'].get('last_query') or 'none'}` local=`{capability_snapshot['skill_discovery'].get('local_match_count', 0)}` remote=`{capability_snapshot['skill_discovery'].get('remote_match_count', 0)}` last_run=`{capability_snapshot['skill_discovery'].get('last_run_status', 'unknown')}`",
        f"- Skill router: `routes={capability_snapshot['skill_route'].get('route_count', 0)}` latest_gap=`{str(bool(capability_snapshot['skill_route'].get('latest_gap_detected'))).lower()}` latest_task=`{capability_snapshot['skill_route'].get('latest_task') or 'none'}`",
        f"- Memory governance: `durable={capability_snapshot['memory_governance']['durable_count']}` summary_only=`{capability_snapshot['memory_governance']['summary_only_count']}` archive=`{capability_snapshot['memory_governance']['archive_candidate_count']}`",
        f"- Memory decay: `hot={capability_snapshot['memory_governance'].get('hot_count', 0)}` `warm={capability_snapshot['memory_governance'].get('warm_count', 0)}` `cool={capability_snapshot['memory_governance'].get('cool_count', 0)}` mode=`{capability_snapshot['memory_governance'].get('retrieval_mode', 'semantic-lite')}`",
        f"- Stale session threshold: `{capability_snapshot['memory_governance']['stale_session_days']} days`",
        f"- Long context: {capability_snapshot['context_window']['note']}",
        "",
        "## Active Skill Lanes",
        "",
    ]
    for mode_name in capability_snapshot["active_modes"]:
        lines.append(f"- `{mode_name}`")
    lines.extend(["", "## Active Skills", ""])
    if active_skills:
        for skill in active_skills:
            lines.append(f"- `{skill}`")
    else:
        lines.append("- none")
    lines.extend(["", "## Candidate Skills", ""])
    if candidate_skills:
        preview = candidate_skills[:20]
        for skill in preview:
            lines.append(f"- `{skill}`")
        if len(candidate_skills) > len(preview):
            lines.append(f"- ... `{len(candidate_skills) - len(preview)}` more")
    else:
        lines.append("- none")
    lines.extend(["", "## Notes", ""])
    lines.append(f"- Work modes source: `{sources['policy']['work_modes']['source']}`")
    lines.append(f"- New unmapped skills since last refresh: `{capability_snapshot['new_candidate_skill_count']}`")
    if findings:
        lines.append(f"- Warnings: `{len(findings)}`")
    else:
        lines.append("- Warnings: `0`")
    lines.append("")
    return "\n".join(lines)


def load_runtime_overlay_registry(config: HubConfig) -> dict[str, Any]:
    payload = load_json_file_strict(runtime_overlay_registry_path(config), default_runtime_overlay_registry(), "runtime overlay registry")
    entries = payload.get("entries", [])
    if not isinstance(entries, list):
        raise HubRuntimeError("Runtime overlay registry entries must be a list.")
    return payload


def save_runtime_overlay_registry(config: HubConfig, payload: dict[str, Any]) -> None:
    path = runtime_overlay_registry_path(config)
    ensure_repo_targets(config, {"runtime_overlay_registry_json": path})
    payload.setdefault("schema_version", 1)
    dump_json(path, payload)


def load_skill_iteration_registry(config: HubConfig) -> dict[str, Any]:
    payload = load_json_file_strict(
        skill_iteration_registry_path(config),
        default_skill_iteration_registry(),
        "skill iteration registry",
    )
    if not isinstance(payload.get("closeouts", []), list) or not isinstance(payload.get("proposals", []), list):
        raise HubRuntimeError("Skill iteration registry must contain list fields `closeouts` and `proposals`.")
    return payload


def save_skill_iteration_registry(config: HubConfig, payload: dict[str, Any]) -> None:
    path = skill_iteration_registry_path(config)
    ensure_repo_targets(config, {"skill_iteration_registry_json": path})
    payload.setdefault("schema_version", 1)
    dump_json(path, payload)


def load_skill_discovery_registry(config: HubConfig) -> dict[str, Any]:
    payload = load_json_file_strict(skill_discovery_registry_path(config), default_skill_discovery_registry(), "skill discovery registry")
    if not isinstance(payload.get("local_matches", []), list) or not isinstance(payload.get("remote_matches", []), list):
        raise HubRuntimeError("Skill discovery registry must contain list fields `local_matches` and `remote_matches`.")
    return payload


def save_skill_discovery_registry(config: HubConfig, payload: dict[str, Any]) -> None:
    path = skill_discovery_registry_path(config)
    ensure_repo_targets(config, {"skill_discovery_registry_json": path})
    payload.setdefault("schema_version", 1)
    dump_json(path, payload)


def load_skill_route_registry(config: HubConfig) -> dict[str, Any]:
    payload = load_json_file_strict(skill_route_registry_path(config), default_skill_route_registry(), "skill route registry")
    if not isinstance(payload.get("entries", []), list):
        raise HubRuntimeError("Skill route registry must contain list field `entries`.")
    return payload


def save_skill_route_registry(config: HubConfig, payload: dict[str, Any]) -> None:
    path = skill_route_registry_path(config)
    ensure_repo_targets(config, {"skill_route_registry_json": path})
    payload.setdefault("schema_version", 1)
    dump_json(path, payload)


def parse_used_skills(raw: str) -> list[str]:
    if not raw.strip():
        return []
    return [normalize_skill_name(item) for item in raw.split(",") if item.strip()]


def require_entry_fields(entry: dict[str, Any], fields: tuple[str, ...], label: str) -> None:
    missing = [field for field in fields if field not in entry or entry.get(field) in (None, "")]
    if missing:
        preview = ", ".join(missing)
        raise HubRuntimeError(f"Invalid {label}: missing required fields {preview}.")


def overlay_entry_for_target(payload: dict[str, Any], target: Path) -> dict[str, Any] | None:
    entries = payload.get("entries", [])
    if not isinstance(entries, list):
        return None
    target_path = str(target.resolve())
    for entry in entries:
        if isinstance(entry, dict) and entry.get("target_path") == target_path:
            require_entry_fields(entry, ("target_path", "brief_path", "generated_at", "mode"), "overlay entry")
            return entry
    return None


def upsert_overlay_entry(payload: dict[str, Any], entry: dict[str, Any]) -> dict[str, Any]:
    entries = payload.get("entries", [])
    if not isinstance(entries, list):
        entries = []
    kept = [item for item in entries if not (isinstance(item, dict) and item.get("target_path") == entry["target_path"])]
    kept.append(entry)
    kept.sort(key=lambda item: item.get("target_path", ""))
    payload["generated_at"] = entry["generated_at"]
    payload["entries"] = kept
    return payload


def local_agent_candidates(target: Path) -> list[Path]:
    return [target / name for name in LOCAL_AGENT_FILE_NAMES]


def existing_local_agent_file(target: Path) -> Path | None:
    for candidate in local_agent_candidates(target):
        if candidate.exists() and candidate.is_file():
            return candidate
    return None


def inherited_agent_paths(target: Path) -> list[Path]:
    found: list[Path] = []
    current = target.resolve().parent
    while True:
        existing = existing_local_agent_file(current)
        if existing:
            found.append(existing)
        if current.parent == current:
            break
        current = current.parent
    return found


def safe_dir_listing(target: Path) -> tuple[set[str], set[str]]:
    dir_names: set[str] = set()
    file_names: set[str] = set()
    try:
        for child in target.iterdir():
            name = child.name.lower()
            if child.is_dir():
                dir_names.add(name)
            elif child.is_file():
                file_names.add(name)
    except OSError:
        return set(), set()
    return dir_names, file_names


def is_scratch_like_folder(target: Path) -> bool:
    parts = {part.lower() for part in target.parts}
    name = target.name.lower()
    return bool(parts & BOOTSTRAP_SCRATCH_TOKENS) or name in BOOTSTRAP_SCRATCH_TOKENS


def assess_bootstrap_local_agent_need(target: Path, intake: dict[str, Any]) -> dict[str, Any]:
    dir_names, file_names = safe_dir_listing(target)
    score = 0
    reasons: list[str] = []
    if ".git" in dir_names:
        score += 2
        reasons.append("git_repo")
    hinted_dirs = sorted(dir_names & BOOTSTRAP_PROJECT_DIR_HINTS)
    if hinted_dirs:
        score += 1
        reasons.append(f"project_dirs={','.join(hinted_dirs[:4])}")
    hinted_files = sorted(file_names & BOOTSTRAP_PROJECT_FILE_HINTS)
    if hinted_files:
        score += 1
        reasons.append(f"project_files={','.join(hinted_files[:4])}")
    if intake["reuse_pipeline"]:
        score += 2
        reasons.append("recurring_pipeline")
    if intake["files_scanned"] >= 5:
        score += 1
        reasons.append("multi_file_folder")
    if intake["confidence"] >= HIGH_CONFIDENCE_THRESHOLD:
        score += 1
        reasons.append("high_confidence_mode")
    if is_scratch_like_folder(target):
        score -= 2
        reasons.append("scratch_like_name")
    project_like = score >= 2
    return {
        "score": score,
        "reasons": reasons,
        "project_like": project_like,
        "scratch_like": is_scratch_like_folder(target),
    }


def bootstrap_mode_verification(mode_name: str) -> list[str]:
    if mode_name == "analysis":
        return [
            "Verify dataset/version assumptions before changing methods.",
            "Prefer a small reproducible check before long reruns.",
        ]
    if mode_name == "writing":
        return [
            "Keep edits surgical and source-bounded.",
            "Use anchor checks or targeted diff review before closeout.",
        ]
    if mode_name == "math_check":
        return [
            "Check notation, derivations, and visible-page consistency explicitly.",
            "Call out mismatches between equations, figures, and prose directly.",
        ]
    if mode_name == "meeting":
        return [
            "Separate decisions, owners, and next steps from interpretation.",
            "Keep math in TeX syntax instead of code spans.",
        ]
    if mode_name == "course":
        return [
            "Keep lecture notes, assignments, and references distinct.",
            "Preserve unresolved questions and definitions explicitly.",
        ]
    return [
        "Verify the visible target artifact before declaring completion.",
        "Keep edits scoped to the current folder objective.",
    ]


def render_minimal_local_agent_markdown(target: Path, intake: dict[str, Any], inherited_paths: list[Path]) -> str:
    mode_name = intake["predicted_mode"]
    active_lane = ", ".join(f"`{skill}`" for skill in intake["active_lane"][:5]) or "`none`"
    inherited_preview = ", ".join(f"`{path}`" for path in inherited_paths[:3]) or "`none`"
    lines = [
        "# AGENTS.md",
        "",
        "## Scope",
        f"- This file applies to `{target}`.",
        "- Treat this as the local project contract for this folder.",
        f"- Inherited higher-level guidance in scope: {inherited_preview}",
        "",
        "## Default Mode",
        f"- Default working mode: `{mode_name}`",
        f"- Preferred active lane: {active_lane}",
        "",
        "## Default Workflow",
        "- Start with folder-first continuity before major edits.",
        "- Keep the active objective explicit and avoid dragging unrelated old chat context into the task.",
        "- If the objective changes materially, rebuild context from current files and durable artifacts before editing.",
        "",
        "## Memory-Driven Iteration",
        "- Memory is assistant-operated, not user-operated.",
        "- Treat `> 3 days` as stale-by-default unless the task is clearly continuous and low-risk.",
        "- End every non-trivial task with a short memory receipt: what changed, what was validated, unresolved risks, and next step.",
        "- Repeated corrections or recurring workarounds should tighten this local workflow or become reusable scripts/checks.",
        "",
        "## Output Contract",
    ]
    for item in intake["output_contract"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Verification", ""])
    for item in bootstrap_mode_verification(mode_name):
        lines.append(f"- {item}")
    lines.extend([
        "",
        "## Done Means",
        "- The active target is explicit.",
        "- Relevant continuity was consulted before major edits.",
        "- Verification matched the folder objective.",
        "- The next session can resume from structured continuity instead of raw chat carry-over.",
        "",
    ])
    return "\n".join(lines)


def write_minimal_local_agent(target: Path, intake: dict[str, Any], inherited_paths: list[Path]) -> Path:
    path = target / "AGENTS.md"
    path.write_text(render_minimal_local_agent_markdown(target, intake, inherited_paths), encoding="utf-8")
    return path


def render_bootstrap_markdown(
    target: Path,
    intake: dict[str, Any],
    overlay_entry: dict[str, Any],
    local_agent_status: str,
    local_agent_path: Path | None,
    local_agent_reason: str | None,
    inherited_paths: list[Path],
    session_gate: dict[str, Any] | None,
    findings: list[dict[str, str]],
) -> str:
    file_types = intake["detected_file_types"]
    type_preview = ", ".join(f"`{ext}` x{count}" for ext, count in file_types[:6]) or "none"
    if len(file_types) > 6:
        type_preview = f"{type_preview} ..."
    inherited_preview = ", ".join(f"`{path}`" for path in inherited_paths[:3]) or "none"
    lines = [
        "# Folder Bootstrap",
        "",
        f"- Target: `{target}`",
        f"- Predicted mode: `{intake['predicted_mode']}`",
        f"- Confidence: `{intake['confidence']}`",
        f"- Files scanned: `{intake['files_scanned']}`",
        f"- Detected file types: {type_preview}",
        f"- Overlay brief: `{overlay_entry['brief_path']}`",
        f"- Local agent status: `{local_agent_status}`",
        f"- Local agent path: `{str(local_agent_path) if local_agent_path else 'none'}`",
        f"- Local agent rationale: {local_agent_reason or 'none'}",
        f"- Inherited agent chain: {inherited_preview}",
        "",
        "## Continuity Hint",
        "",
    ]
    continuity = intake.get("continuity")
    if isinstance(continuity, dict) and continuity.get("source"):
        lines.extend(
            [
                f"- Source: `{continuity['source']}`",
                f"- Event time: `{continuity.get('event_time', '') or 'unknown'}`",
                f"- Summary: {continuity.get('summary', '') or 'none'}",
                f"- Next step: {continuity.get('next_step', '') or 'none'}",
                "",
            ]
        )
    else:
        lines.extend(["- none", ""])
    if session_gate:
        lines.extend(
            [
                "## Session Gate",
                "",
                f"- Recommendation: `{session_gate['recommendation']}`",
                f"- Updated at: `{session_gate['updated_at']}`",
                f"- Age days: `{session_gate['age_days']}`",
                f"- Recommended brief path: `{session_gate.get('recommended_brief_path') or 'none'}`",
                f"- Recommended memory summary: `{session_gate.get('recommended_memory_summary_path') or 'none'}`",
                "",
            ]
        )
    if findings:
        lines.extend(["## Warnings", ""])
        for item in findings:
            lines.append(f"- `{item['code']}`: {item['message']}")
        lines.append("")
    lines.extend(["## Recommended Next Actions", ""])
    for action in intake["next_actions"]:
        lines.append(f"- {action}")
    lines.append("")
    return "\n".join(lines)


def render_overlay_markdown(overlay: dict[str, Any]) -> str:
    lines = [
        "# Runtime Overlay Brief",
        "",
        f"- Target: `{overlay['target_path']}`",
        f"- Brief path: `{overlay['brief_path']}`",
        f"- Generated at: `{overlay['generated_at']}`",
        f"- Predicted mode: `{overlay['mode']}`",
        f"- Confidence: `{overlay['confidence']}`",
        f"- Route strategy: `{overlay['route_strategy']}`",
        f"- Reuse pipeline: `{str(overlay['reuse_pipeline']).lower()}`",
        "",
        "## Continuity Context",
        "",
    ]
    continuity = overlay.get("continuity")
    if isinstance(continuity, dict) and continuity.get("source"):
        lines.extend(
            [
                f"- Source: `{continuity['source']}`",
                f"- Event time: `{continuity.get('event_time', '') or 'unknown'}`",
                f"- Path: `{continuity.get('source_path', '') or 'n/a'}`",
                f"- Summary: {continuity.get('summary', '') or 'none'}",
                f"- Next step: {continuity.get('next_step', '') or 'none'}",
                f"- Rank explanation: `{continuity.get('rank_explanation', 'n/a')}`",
                "",
            ]
        )
    else:
        lines.extend(["- none", ""])
    lines.extend([
        "## Session Preamble",
        "",
        overlay["session_preamble"],
        "",
        "## Active Lane",
        "",
    ])
    if overlay["active_lane"]:
        for skill in overlay["active_lane"]:
            lines.append(f"- `{skill}`")
    else:
        lines.append("- none")
    lines.extend(["", "## Fallback Lane", ""])
    if overlay["fallback_lane"]:
        for skill in overlay["fallback_lane"]:
            lines.append(f"- `{skill}`")
    else:
        lines.append("- none")
    lines.extend(["", "## Output Contract", ""])
    for item in overlay["output_contract"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Escalation Triggers", ""])
    for item in overlay["escalation_triggers"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Recommended Next Actions", ""])
    for action in overlay["next_actions"]:
        lines.append(f"- {action}")
    lines.append("")
    return "\n".join(lines)


def create_overlay_brief(
    config: HubConfig,
    target: Path,
    intake: dict[str, Any],
    mode: WorkMode,
) -> tuple[dict[str, Any], str]:
    slug = overlay_target_slug(config, target)
    brief_path = runtime_overlays_dir(config) / f"{slug}.md"
    overlay = {
        "target_path": str(target.resolve()),
        "brief_path": str(brief_path),
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "mode": intake["predicted_mode"],
        "confidence": intake["confidence"],
        "route_strategy": intake["route_strategy"],
        "reuse_pipeline": intake["reuse_pipeline"],
        "active_lane": intake["active_lane"],
        "fallback_lane": intake["fallback_lane"],
        "output_contract": intake["output_contract"],
        "next_actions": intake["next_actions"],
        "session_preamble": mode.session_preamble,
        "escalation_triggers": list(mode.escalation_triggers),
        "continuity": intake.get("continuity"),
    }
    brief = render_overlay_markdown(overlay)
    ensure_repo_targets(config, {"runtime_overlay_brief": brief_path})
    brief_path.parent.mkdir(parents=True, exist_ok=True)
    brief_path.write_text(brief, encoding="utf-8")
    return overlay, brief


def render_skill_review_markdown(payload: dict[str, Any]) -> str:
    proposals = payload.get("proposals", [])
    open_proposals: list[dict[str, Any]] = []
    for entry in proposals:
        if not isinstance(entry, dict) or entry.get("status") != "open":
            continue
        require_entry_fields(entry, ("id", "skill_name", "mode", "source_target_path", "closeout_summary", "created_at"), "skill proposal")
        open_proposals.append(entry)
    lines = [
        "# Skill Proposal Review",
        "",
        f"- Open proposals: `{len(open_proposals)}`",
        "",
    ]
    if not open_proposals:
        lines.append("- none")
        lines.append("")
        return "\n".join(lines)
    lines.extend(["## Open Proposals", ""])
    for entry in sorted(open_proposals, key=lambda item: item.get("created_at", "")):
        recommendation = "promote to the fallback lane if the workflow looks reusable."
        if entry.get("proposal_type") == "improve_skill":
            recommendation = "inspect the failure/workaround and route this through skill-creator for an update proposal."
        if entry.get("proposal_type") == "discover_or_create":
            recommendation = "run skill-discover, then create or install a candidate skill before promotion."
        lines.extend(
            [
                f"- Proposal: `{entry['id']}`",
                f"  Skill: `{entry['skill_name']}`",
                f"  Type: `{entry.get('proposal_type', 'promote_candidate')}`",
                f"  Mode: `{entry['mode']}`",
                f"  Target: `{entry['source_target_path']}`",
                f"  Summary: {entry['closeout_summary']}",
                f"  Outcome/reuse: `{entry.get('outcome', 'unknown')}` / `{entry.get('reuse', 'unknown')}`",
                f"  Recommended action: {recommendation}",
            ]
        )
    lines.append("")
    return "\n".join(lines)


def render_proposal_markdown(entry: dict[str, Any]) -> str:
    lines = [
        "# Skill Proposal",
        "",
        f"- Proposal ID: `{entry['id']}`",
        f"- Skill: `{entry['skill_name']}`",
        f"- Proposal type: `{entry.get('proposal_type', 'promote_candidate')}`",
        f"- Mode: `{entry['mode']}`",
        f"- Status: `{entry['status']}`",
        f"- Source closeout: `{entry['source_closeout_id']}`",
        f"- Source target: `{entry['source_target_path']}`",
        f"- Created at: `{entry['created_at']}`",
    ]
    if entry.get("resolved_at"):
        lines.append(f"- Resolved at: `{entry['resolved_at']}`")
    if entry.get("resolution_reason"):
        lines.append(f"- Resolution reason: {entry['resolution_reason']}")
    lines.extend(
        [
            "",
            "## Closeout Summary",
            "",
            entry["closeout_summary"],
            "",
            "## Suggested Promotion",
            "",
            f"- Outcome: `{entry.get('outcome', 'unknown')}` reuse=`{entry.get('reuse', 'unknown')}`",
            "- First promotion target: fallback lane only",
            "- No direct change to active lane or SKILL.md in v1",
            "",
        ]
    )
    return "\n".join(lines)


def find_proposal(payload: dict[str, Any], proposal_id: str) -> dict[str, Any] | None:
    proposals = payload.get("proposals", [])
    if not isinstance(proposals, list):
        return None
    for entry in proposals:
        if isinstance(entry, dict) and entry.get("id") == proposal_id:
            require_entry_fields(
                entry,
                ("id", "skill_name", "mode", "source_closeout_id", "source_target_path", "status", "created_at", "proposal_path", "closeout_summary"),
                "skill proposal",
            )
            return entry
    return None


def write_all_proposal_files(config: HubConfig, payload: dict[str, Any]) -> None:
    for entry in payload.get("proposals", []):
        if not isinstance(entry, dict):
            continue
        require_entry_fields(
            entry,
            ("id", "skill_name", "mode", "source_closeout_id", "source_target_path", "status", "created_at", "proposal_path", "closeout_summary"),
            "skill proposal",
        )
        proposal_path = Path(entry["proposal_path"])
        ensure_repo_targets(config, {f"proposal_{entry['id']}": proposal_path})
        proposal_path.parent.mkdir(parents=True, exist_ok=True)
        proposal_path.write_text(render_proposal_markdown(entry), encoding="utf-8")


def do_bootstrap(
    config: HubConfig,
    target_arg: str,
    write_agent: str,
    thread_id: str | None,
    cwd_arg: str | None,
) -> int:
    work_modes, work_modes_meta, findings = load_work_modes(config)
    installed_skills = scan_installed_skills(config.skill_roots)
    inventory = build_skill_inventory(installed_skills, work_modes, work_modes_meta["cold_skills"])
    target = Path(target_arg).expanduser().resolve()
    if not target.exists():
        print(f"Target path does not exist: {target}", file=sys.stderr)
        return 1
    if not target.is_dir():
        print(f"Target path must be a directory: {target}", file=sys.stderr)
        return 1

    intake = inspect_folder(config, target, work_modes, inventory)
    overlay_entry, _brief = create_overlay_brief(config, target, intake, work_modes[intake["predicted_mode"]])
    payload = load_runtime_overlay_registry(config)
    payload = upsert_overlay_entry(payload, overlay_entry)
    save_runtime_overlay_registry(config, payload)

    inherited_paths = inherited_agent_paths(target)
    existing_local_agent = existing_local_agent_file(target)
    local_agent_status = "existing" if existing_local_agent else "not_created"
    local_agent_path: Path | None = existing_local_agent
    local_agent_reason: str | None = None
    bootstrap_assessment = assess_bootstrap_local_agent_need(target, intake)

    if existing_local_agent and existing_local_agent.name == "Agent.md":
        findings.append(
            warning(
                "bootstrap",
                "legacy_agent_filename",
                "Found `Agent.md` instead of `AGENTS.md`; keeping it, but pickup behavior may be inconsistent across tools.",
                existing_local_agent,
            )
        )
        local_agent_status = "legacy_present"
        local_agent_reason = "existing Agent.md detected"
    elif existing_local_agent:
        local_agent_reason = "local AGENTS.md already exists"
    else:
        should_write = False
        if write_agent == "always":
            should_write = True
            local_agent_reason = "explicit --write-agent=always"
        elif write_agent == "auto" and bootstrap_assessment["project_like"]:
            should_write = True
            local_agent_reason = "project-like folder under auto bootstrap"
        elif write_agent == "never":
            local_agent_reason = "explicit --write-agent=never"
        else:
            local_agent_reason = "folder looks scratch-like or under-specified; no local AGENTS.md written"

        if should_write:
            local_agent_path = write_minimal_local_agent(target, intake, inherited_paths)
            local_agent_status = "created"
        else:
            local_agent_status = "recommended_only" if bootstrap_assessment["project_like"] else "not_needed"

    session_gate_result = None
    if thread_id or cwd_arg:
        try:
            session_gate_result = build_session_gate_result(config, thread_id, cwd_arg or str(target))
        except HubRuntimeError as exc:
            findings.append(warning("bootstrap", "session_gate_unavailable", str(exc), config.active_session_state))

    print(
        render_bootstrap_markdown(
            target=target,
            intake=intake,
            overlay_entry=overlay_entry,
            local_agent_status=local_agent_status,
            local_agent_path=local_agent_path,
            local_agent_reason=local_agent_reason,
            inherited_paths=inherited_paths,
            session_gate=session_gate_result,
            findings=findings,
        ),
        end="",
    )
    return 0


def do_overlay(config: HubConfig, target_arg: str) -> int:
    work_modes, work_modes_meta, findings = load_work_modes(config)
    installed_skills = scan_installed_skills(config.skill_roots)
    inventory = build_skill_inventory(installed_skills, work_modes, work_modes_meta["cold_skills"])
    target = Path(target_arg).expanduser().resolve()
    if not target.exists():
        print(f"Target path does not exist: {target}", file=sys.stderr)
        return 1
    if not target.is_dir():
        print(f"Target path must be a directory: {target}", file=sys.stderr)
        return 1
    intake = inspect_folder(config, target, work_modes, inventory)
    overlay_entry, brief = create_overlay_brief(config, target, intake, work_modes[intake["predicted_mode"]])
    payload = load_runtime_overlay_registry(config)
    payload = upsert_overlay_entry(payload, overlay_entry)
    save_runtime_overlay_registry(config, payload)
    print(brief, end="")
    return 0


def do_closeout(
    config: HubConfig,
    target_arg: str,
    summary: str,
    used_skills_raw: str,
    outcome: str,
    reuse: str,
) -> int:
    target = Path(target_arg).expanduser().resolve()
    if not summary.strip():
        print("--summary must be non-empty.", file=sys.stderr)
        return 1
    if not target.exists():
        print(f"Target path does not exist: {target}", file=sys.stderr)
        return 1
    if not target.is_dir():
        print(f"Target path must be a directory: {target}", file=sys.stderr)
        return 1

    overlay_registry = load_runtime_overlay_registry(config)
    overlay_entry = overlay_entry_for_target(overlay_registry, target)
    if not overlay_entry:
        print("No overlay brief exists for this target; run `./scripts/brain.sh overlay <folder>` first.", file=sys.stderr)
        return 1

    work_modes, work_modes_meta, _findings = load_work_modes(config)
    installed_skills = scan_installed_skills(config.skill_roots)
    inventory = build_skill_inventory(installed_skills, work_modes, work_modes_meta["cold_skills"])
    used_skills = parse_used_skills(used_skills_raw)
    invalid_skills = [skill for skill in used_skills if skill not in inventory["installed_skills"]]
    valid_used_skills = [skill for skill in used_skills if skill in inventory["installed_skills"]]
    discovery_hint_query = ", ".join(invalid_skills) if invalid_skills else None

    payload = load_skill_iteration_registry(config)
    closeouts = payload.get("closeouts", [])
    if not isinstance(closeouts, list):
        closeouts = []
    proposals = payload.get("proposals", [])
    if not isinstance(proposals, list):
        proposals = []

    closeout_id = new_record_id("closeout")
    closeout_path = skill_iteration_closeouts_dir(config) / f"{closeout_id}.json"
    ensure_repo_targets(config, {"skill_iteration_closeout_json": closeout_path})
    closeout_path.parent.mkdir(parents=True, exist_ok=True)
    closeout = {
        "id": closeout_id,
        "target_path": str(target),
        "overlay_brief_path": overlay_entry["brief_path"],
        "overlay_generated_at": overlay_entry["generated_at"],
        "summary": summary.strip(),
        "used_skills": valid_used_skills,
        "invalid_skills": invalid_skills,
        "outcome": outcome,
        "reuse": reuse,
        "discovery_hint_query": discovery_hint_query,
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "mode": overlay_entry["mode"],
    }
    closeouts.append(closeout)
    payload["closeouts"] = closeouts

    created_ids: list[str] = []
    current_proposals = [entry for entry in proposals if isinstance(entry, dict)]
    for skill in valid_used_skills:
        if skill not in inventory["candidate_skills"]:
            continue
        if outcome != "success" or reuse != "yes":
            continue
        existing_open = next(
            (
                entry
                for entry in current_proposals
                if entry.get("skill_name") == skill
                and entry.get("mode") == overlay_entry["mode"]
                and entry.get("source_target_path") == str(target)
                and entry.get("status") == "open"
            ),
            None,
        )
        if existing_open:
            continue
        proposal_id = new_record_id(f"proposal-{skill}")
        proposal_path = skill_iteration_proposals_dir(config) / f"{proposal_id}.md"
        proposal = {
            "id": proposal_id,
            "skill_name": skill,
            "proposal_type": "promote_candidate",
            "source_closeout_id": closeout_id,
            "source_target_path": str(target),
            "mode": overlay_entry["mode"],
            "status": "open",
            "created_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
            "resolved_at": None,
            "resolution_reason": None,
            "closeout_summary": summary.strip(),
            "outcome": outcome,
            "reuse": reuse,
            "proposal_path": str(proposal_path),
        }
        current_proposals.append(proposal)
        created_ids.append(proposal_id)

    payload["proposals"] = current_proposals
    payload["generated_at"] = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    dump_json(closeout_path, closeout)
    save_skill_iteration_registry(config, payload)
    write_all_proposal_files(config, payload)

    lines = [
        "# Skill Iteration Closeout",
        "",
        f"- Target: `{target}`",
        f"- Closeout ID: `{closeout_id}`",
        f"- Overlay brief: `{overlay_entry['brief_path']}`",
        f"- Used skills: {', '.join(f'`{skill}`' for skill in valid_used_skills) if valid_used_skills else 'none'}",
        f"- Outcome: `{outcome}` reuse=`{reuse}`",
        f"- Created proposals: `{len(created_ids)}`",
    ]
    if invalid_skills:
        lines.append(f"- Invalid/uninstalled skills: {', '.join(f'`{skill}`' for skill in invalid_skills)}")
        lines.append(
            f"- Discovery suggestion: `./scripts/brain.sh skill-discover \"{discovery_hint_query}\"`"
        )
    if valid_used_skills and not created_ids and (outcome != "success" or reuse != "yes"):
        lines.append("- Proposal gate: no promotion proposal opened because outcome/reuse did not clear the success gate.")
    for proposal_id in created_ids:
        lines.append(f"- Proposal ID: `{proposal_id}`")
    lines.append("")
    print("\n".join(lines))
    return 0


def render_skill_discover_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Skill Discovery",
        "",
        f"- Query: `{payload.get('last_query') or ''}`",
        f"- Generated at: `{payload.get('generated_at') or 'unknown'}`",
        f"- Status: `{payload.get('status', 'unknown')}`",
        f"- Local matches: `{len(payload.get('local_matches', []))}`",
        f"- Remote matches: `{len(payload.get('remote_matches', []))}`",
        "",
        "## Local Matches",
        "",
    ]
    local_matches = payload.get("local_matches", [])
    if local_matches:
        for entry in local_matches[:8]:
            lines.append(
                f"- `{entry['name']}` score=`{entry['score']}` reasons=`{', '.join(entry.get('reasons', []))}` path=`{entry['path']}`"
            )
            if entry.get("summary"):
                lines.append(f"  Summary: {entry['summary']}")
    else:
        lines.append("- none")
    lines.extend(["", "## Remote Matches", ""])
    remote_matches = payload.get("remote_matches", [])
    if remote_matches:
        for entry in remote_matches[:8]:
            lines.append(f"- `{entry['package']}`")
            if entry.get("url"):
                lines.append(f"  URL: `{entry['url']}`")
            if entry.get("install_hint"):
                lines.append(f"  Install: `{entry['install_hint']}`")
    else:
        lines.append("- none")
    warnings_list = payload.get("warnings", [])
    if warnings_list:
        lines.extend(["", "## Notes", ""])
        for note in warnings_list:
            lines.append(f"- {note}")
    lines.append("")
    return "\n".join(lines)


def do_skill_discover(config: HubConfig, query: str) -> int:
    work_modes, work_modes_meta, _findings = load_work_modes(config)
    installed_skills = scan_installed_skills(config.skill_roots)
    inventory = build_skill_inventory(installed_skills, work_modes, work_modes_meta["cold_skills"])
    local_matches = discover_local_skills(installed_skills, query)
    remote_matches, warnings_list, remote_status = discover_remote_skills(query)
    payload = default_skill_discovery_registry()
    payload.update(
        {
            "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
            "last_query": query.strip(),
            "status": "healthy" if remote_status == "healthy" or not warnings_list else "degraded",
            "local_matches": local_matches,
            "remote_matches": remote_matches,
            "warnings": warnings_list,
            "candidate_skill_count": len(inventory["candidate_skills"]),
        }
    )
    save_skill_discovery_registry(config, payload)
    print(render_skill_discover_markdown(payload), end="")
    return 0 if payload["status"] == "healthy" else 2


def normalize_path_string(value: str | Path | None) -> str | None:
    if value in (None, ""):
        return None
    try:
        return str(Path(value).expanduser().resolve())
    except OSError:
        return str(Path(value))


def build_skill_quality_signals(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    summary: dict[str, dict[str, Any]] = {}
    for entry in payload.get("closeouts", []):
        if not isinstance(entry, dict):
            continue
        mode = normalize_token(str(entry.get("mode", ""))) or None
        target_path = normalize_path_string(entry.get("target_path"))
        generated_at = entry.get("generated_at")
        outcome = str(entry.get("outcome", "partial"))
        reuse = str(entry.get("reuse", "no"))
        for raw_skill in entry.get("used_skills", []):
            if not isinstance(raw_skill, str):
                continue
            skill_name = normalize_skill_name(raw_skill)
            state = summary.setdefault(
                skill_name,
                {
                    "use_count": 0,
                    "success_count": 0,
                    "partial_count": 0,
                    "fail_count": 0,
                    "reuse_yes_count": 0,
                    "reuse_no_count": 0,
                    "last_used_at": None,
                    "last_success_at": None,
                    "mode_counts": {},
                    "folder_counts": {},
                },
            )
            state["use_count"] += 1
            if outcome == "success":
                state["success_count"] += 1
                if isinstance(generated_at, str) and (state["last_success_at"] is None or generated_at > state["last_success_at"]):
                    state["last_success_at"] = generated_at
            elif outcome == "fail":
                state["fail_count"] += 1
            else:
                state["partial_count"] += 1
            if reuse == "yes":
                state["reuse_yes_count"] += 1
            else:
                state["reuse_no_count"] += 1
            if isinstance(generated_at, str) and (state["last_used_at"] is None or generated_at > state["last_used_at"]):
                state["last_used_at"] = generated_at
            if mode:
                mode_counts = state["mode_counts"]
                mode_counts[mode] = int(mode_counts.get(mode, 0)) + 1
            if target_path:
                folder_counts = state["folder_counts"]
                folder_counts[target_path] = int(folder_counts.get(target_path, 0)) + 1
    return summary


def classify_artifact_counts(file_types: list[tuple[str, int]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for extension, count in file_types:
        for artifact_type, extensions in ARTIFACT_EXTENSION_HINTS.items():
            if extension in extensions:
                counts[artifact_type] = counts.get(artifact_type, 0) + int(count)
                break
    return counts


def latest_skill_route_entry_for_target(entries: list[Any], target_path: str) -> dict[str, Any] | None:
    for entry in reversed(entries):
        if isinstance(entry, dict) and normalize_path_string(entry.get("target_path")) == target_path:
            return entry
    return None


def score_intent_term_hits(lowered: str, terms: set[str]) -> int:
    score = 0
    for term in terms:
        if hint_in_text(lowered, term):
            score += 1
    return score


def hint_in_text(lowered: str, hint: str) -> bool:
    if not hint:
        return False
    if any(char in hint for char in (" ", "/", ".", "-")):
        return hint in lowered
    return bool(re.search(rf"(?<![a-z0-9_]){re.escape(hint)}(?![a-z0-9_])", lowered))


def parse_intent_phase(lowered: str) -> tuple[str, list[str]]:
    signals: list[str] = []
    correction_hits = score_intent_term_hits(lowered, INTENT_CORRECTION_TERMS)
    qa_hits = score_intent_term_hits(lowered, INTENT_QA_TERMS)
    creation_hits = score_intent_term_hits(lowered, INTENT_CREATION_TERMS)
    transform_hits = score_intent_term_hits(lowered, INTENT_TRANSFORM_TERMS)
    planning_hits = score_intent_term_hits(lowered, INTENT_PLANNING_TERMS)
    if correction_hits:
        signals.append(f"correction_terms={correction_hits}")
        return "correction", signals
    if qa_hits:
        signals.append(f"qa_terms={qa_hits}")
        return "qa", signals
    if creation_hits:
        signals.append(f"creation_terms={creation_hits}")
        return "creation", signals
    if transform_hits:
        signals.append(f"transform_terms={transform_hits}")
        return "transform", signals
    if planning_hits:
        signals.append(f"planning_terms={planning_hits}")
        return "planning", signals
    return "execution", signals


def infer_task_artifact_type(lowered: str, artifact_counts: dict[str, int], recent_intent: dict[str, Any] | None) -> tuple[str | None, list[str]]:
    task_scores: dict[str, int] = {}
    signals: list[str] = []
    for artifact_type, hints in ARTIFACT_TERM_HINTS.items():
        hits = sum(1 for hint in hints if hint_in_text(lowered, hint))
        if hits:
            task_scores[artifact_type] = task_scores.get(artifact_type, 0) + hits
            signals.append(f"task_artifact={artifact_type}:{hits}")
    if task_scores:
        ranked = sorted(task_scores.items(), key=lambda item: (-item[1], item[0]))
        return ranked[0][0], signals
    if artifact_counts:
        ranked = sorted(artifact_counts.items(), key=lambda item: (-item[1], item[0]))
        top_artifact, top_count = ranked[0]
        if top_count > 0:
            signals.append(f"folder_artifact={top_artifact}:{top_count}")
            return top_artifact, signals
    if isinstance(recent_intent, dict) and recent_intent.get("artifact_type"):
        artifact_type = str(recent_intent["artifact_type"])
        signals.append(f"recent_artifact={artifact_type}")
        return artifact_type, signals
    return None, signals


def infer_artifact_state(task_phase: str, artifact_type: str | None, artifact_counts: dict[str, int]) -> str:
    if task_phase == "creation":
        return "new"
    if artifact_type and artifact_counts.get(artifact_type, 0) > 0:
        return "existing"
    if task_phase in {"qa", "correction", "transform"} and artifact_counts:
        return "existing"
    return "unknown"


def infer_router_intent(task: str, intake: dict[str, Any], route_registry: dict[str, Any]) -> dict[str, Any]:
    lowered = task.strip().lower()
    task_phase, phase_signals = parse_intent_phase(lowered)
    artifact_counts = classify_artifact_counts(intake.get("detected_file_types", []))
    recent_entry = latest_skill_route_entry_for_target(route_registry.get("entries", []), intake["target"])
    recent_intent = recent_entry.get("intent") if isinstance(recent_entry, dict) else None
    artifact_type, artifact_signals = infer_task_artifact_type(lowered, artifact_counts, recent_intent if isinstance(recent_intent, dict) else None)
    artifact_state = infer_artifact_state(task_phase, artifact_type, artifact_counts)
    intent_verb = {
        "qa": "inspect",
        "correction": "fix",
        "creation": "create",
        "transform": "transform",
        "planning": "plan",
    }.get(task_phase, "execute")
    recent_phase = recent_intent.get("task_phase") if isinstance(recent_intent, dict) else None
    signals = [*phase_signals, *artifact_signals]
    if recent_phase:
        signals.append(f"recent_phase={recent_phase}")
    confidence = 0.2
    if task_phase != "execution":
        confidence += 0.3
    if artifact_type:
        confidence += 0.25
    if artifact_state != "unknown":
        confidence += 0.15
    if recent_phase:
        confidence += 0.1
    return {
        "intent_verb": intent_verb,
        "artifact_type": artifact_type,
        "artifact_state": artifact_state,
        "task_phase": task_phase,
        "domain_mode": intake["predicted_mode"],
        "recent_task_phase": recent_phase,
        "confidence": round(min(confidence, 0.95), 3),
        "signals": signals[:8],
    }


def infer_skill_artifact_affinities(skill: dict[str, str]) -> set[str]:
    lowered = f"{skill['name'].lower()}\n{skill_search_blob(skill)}"
    affinities: set[str] = set()
    for artifact_type, hints in SKILL_ARTIFACT_HINTS.items():
        if any(hint_in_text(lowered, hint) for hint in hints):
            affinities.add(artifact_type)
    if any(hint_in_text(lowered, term) for term in ("verify", "validation", "inspect", "review", "check")):
        affinities.add("qa_helper")
    if any(
        hint_in_text(lowered, term)
        for term in ("author", "compose", "create", "creator", "deploy", "generate", "generation", "generator", "produce", "writer")
    ):
        affinities.add("creation_helper")
    return affinities


def skill_quality_note(skill_name: str, signal: dict[str, Any], predicted_mode: str, target_path: str) -> str | None:
    parts: list[str] = []
    if signal.get("success_count"):
        parts.append(f"success={signal['success_count']}")
    if signal.get("reuse_yes_count"):
        parts.append(f"reuse_yes={signal['reuse_yes_count']}")
    mode_count = signal.get("mode_counts", {}).get(predicted_mode)
    if mode_count:
        parts.append(f"mode={predicted_mode}:{mode_count}")
    folder_count = signal.get("folder_counts", {}).get(target_path)
    if folder_count:
        parts.append(f"folder_hits={folder_count}")
    if not parts:
        return None
    return f"`{skill_name}` quality={', '.join(parts)}"


def skill_route_need(task: str, intake: dict[str, Any], local_matches: list[dict[str, Any]], intent: dict[str, Any]) -> tuple[bool, str]:
    lowered = task.strip().lower()
    terms = normalize_search_terms(task)
    if not lowered:
        return False, "Empty task description."
    if intent["task_phase"] in {"qa", "correction"} and intent["artifact_state"] == "existing":
        artifact_label = intent.get("artifact_type") or "artifact"
        return True, f"Task is a corrective pass on an existing `{artifact_label}` artifact."
    workflow_terms = {"workflow", "pipeline", "route", "router", "skill", "combine", "extract", "verify", "ingest", "normalize"}
    if any(term in lowered for term in workflow_terms):
        return True, "Task explicitly asks for a workflow or tool route."
    if local_matches:
        return True, "Task has direct matches against installed skill descriptions."
    if intake["files_scanned"] >= 3 and len(terms) >= 3:
        return True, "Folder scope and task length suggest a reusable multi-step workflow."
    if len(terms) <= 2 and intake["files_scanned"] <= 2:
        return False, "Task looks small enough to handle directly."
    return bool(intake["active_lane"] or intake["fallback_lane"]), "Mode lane is available for the current folder."


def score_skill_route_candidate(
    skill: dict[str, str],
    task_matches: dict[str, dict[str, Any]],
    quality_signals: dict[str, dict[str, Any]],
    intake: dict[str, Any],
    inventory: dict[str, Any],
    intent: dict[str, Any],
) -> dict[str, Any] | None:
    name = skill["name"]
    score = 0
    reasons: list[str] = []
    artifact_fit = False
    phase_fit = False
    specialized_fit = False
    if name in intake["active_lane"]:
        score += 35
        reasons.append("active_lane")
    elif name in intake["fallback_lane"]:
        score += 22
        reasons.append("fallback_lane")
    elif name in inventory["candidate_skills"]:
        score += 8
        reasons.append("candidate_lane")

    match = task_matches.get(name)
    if match:
        match_score = min(24, int(match["score"]) * 3)
        score += match_score
        reasons.append(f"task_match={match_score}")

    signal = quality_signals.get(name)
    if signal:
        success_bonus = min(24, int(signal.get("success_count", 0)) * 8)
        partial_penalty = min(6, int(signal.get("partial_count", 0)) * 2)
        fail_penalty = min(12, int(signal.get("fail_count", 0)) * 4)
        reuse_bonus = min(12, int(signal.get("reuse_yes_count", 0)) * 4)
        reuse_penalty = min(6, int(signal.get("reuse_no_count", 0)) * 2)
        mode_bonus = min(12, int(signal.get("mode_counts", {}).get(intake["predicted_mode"], 0)) * 5)
        folder_bonus = min(18, int(signal.get("folder_counts", {}).get(intake["target"], 0)) * 12)
        sticky_folder_bonus = 0
        if folder_bonus and success_bonus and reuse_bonus:
            sticky_folder_bonus = 16
        score += success_bonus + reuse_bonus + mode_bonus + folder_bonus + sticky_folder_bonus
        score -= partial_penalty + fail_penalty + reuse_penalty
        if success_bonus:
            reasons.append(f"success_history={success_bonus}")
        if reuse_bonus:
            reasons.append(f"reuse_history={reuse_bonus}")
        if mode_bonus:
            reasons.append(f"mode_history={mode_bonus}")
        if folder_bonus:
            reasons.append(f"folder_history={folder_bonus}")
        if sticky_folder_bonus:
            reasons.append(f"sticky_folder={sticky_folder_bonus}")
        if partial_penalty:
            reasons.append(f"partial_penalty={partial_penalty}")
        if fail_penalty:
            reasons.append(f"fail_penalty={fail_penalty}")

    affinities = infer_skill_artifact_affinities(skill)
    artifact_type = intent.get("artifact_type")
    task_phase = intent.get("task_phase")
    lowered_skill = f"{skill['name'].lower()}\n{skill_search_blob(skill)}"
    if artifact_type:
        if artifact_type in affinities:
            artifact_fit = True
            score += 22
            reasons.append(f"artifact_fit={artifact_type}")
        elif name in ROUTER_GENERIC_HELPER_SKILLS or (task_phase in {"qa", "correction"} and name in ROUTER_QA_HELPER_SKILLS):
            score += 4
            reasons.append("generic_helper")
        elif task_phase in {"qa", "correction"} and intent.get("artifact_state") == "existing":
            score -= 38
            reasons.append(f"artifact_mismatch={artifact_type}")
    if task_phase in {"qa", "correction"}:
        if name in ROUTER_QA_HELPER_SKILLS or "qa_helper" in affinities:
            phase_fit = True
            score += 10
            reasons.append("qa_helper")
        elif "creation_helper" in affinities:
            score -= 12
            reasons.append("phase_mismatch=creation_helper")
        if any(hint_in_text(lowered_skill, term) for term in ROUTER_PHASE_MISMATCH_TERMS):
            score -= 30
            reasons.append("phase_mismatch=acquisition_or_creation")
        if artifact_fit and (phase_fit or "qa_helper" in affinities):
            specialized_fit = True
    elif artifact_fit:
        specialized_fit = True

    if score <= 0:
        return None
    if (
        task_phase in {"qa", "correction"}
        and intent.get("artifact_state") == "existing"
        and (
            "phase_mismatch=acquisition_or_creation" in reasons
            or ("generic_helper" in reasons and not artifact_fit)
            or not specialized_fit
        )
    ):
        reasons.append("primary_blocked_for_existing_correction")
    return {
        "name": name,
        "score": score,
        "reasons": reasons[:8],
        "match": match,
        "quality": signal or {},
        "path": skill["path"],
        "artifact_fit": artifact_fit,
        "phase_fit": phase_fit,
        "specialized_fit": specialized_fit,
        "affinities": sorted(affinities),
        "primary_blocked": "primary_blocked_for_existing_correction" in reasons,
    }


def select_skill_route_plan(
    installed_skills: list[dict[str, str]],
    inventory: dict[str, Any],
    intake: dict[str, Any],
    task: str,
    quality_signals: dict[str, dict[str, Any]],
    intent: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[str], list[dict[str, Any]]]:
    local_matches = discover_local_skills(installed_skills, task)
    task_matches = {entry["name"]: entry for entry in local_matches}
    candidates = [
        scored
        for skill in installed_skills
        if (scored := score_skill_route_candidate(skill, task_matches, quality_signals, intake, inventory, intent))
    ]
    candidates.sort(key=lambda item: (-item["score"], item["name"]))
    primary: list[dict[str, Any]] = []
    fallback: list[dict[str, Any]] = []
    for candidate in candidates:
        if candidate.get("primary_blocked"):
            if candidate["score"] >= 14 and len(fallback) < 4:
                fallback.append(candidate)
            continue
        if candidate["score"] >= 28 and len(primary) < 3:
            primary.append(candidate)
        elif candidate["score"] >= 14 and len(fallback) < 4:
            fallback.append(candidate)
    if not primary and candidates:
        unblocked = [candidate for candidate in candidates if not candidate.get("primary_blocked")]
        primary = unblocked[: min(2, len(unblocked))]
        remaining = [candidate for candidate in candidates if candidate not in primary]
        if not fallback:
            fallback = remaining[:4]
    quality_notes: list[str] = []
    for entry in primary[:3]:
        note = skill_quality_note(entry["name"], entry.get("quality", {}), intake["predicted_mode"], intake["target"])
        if note:
            quality_notes.append(note)
    return primary, fallback, quality_notes, local_matches


def run_skill_discovery_for_route(
    config: HubConfig,
    query: str,
    inventory: dict[str, Any],
    installed_skills: list[dict[str, str]],
) -> dict[str, Any]:
    local_matches = discover_local_skills(installed_skills, query)
    remote_matches, warnings_list, remote_status = discover_remote_skills(query)
    payload = default_skill_discovery_registry()
    payload.update(
        {
            "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
            "last_query": query.strip(),
            "status": "healthy" if remote_status == "healthy" or not warnings_list else "degraded",
            "local_matches": local_matches,
            "remote_matches": remote_matches,
            "warnings": warnings_list,
            "candidate_skill_count": len(inventory["candidate_skills"]),
        }
    )
    save_skill_discovery_registry(config, payload)
    return payload


def render_skill_route_markdown(route: dict[str, Any]) -> str:
    lines = [
        "# Skill Route",
        "",
        f"- Task: `{route['task']}`",
        f"- Target path: `{route['target_path']}`",
        f"- Predicted mode: `{route['predicted_mode']}`",
        f"- Need skill: `{str(route['need_skill']).lower()}`",
        f"- Route strategy: `{route['route_strategy']}`",
        f"- Gap detected: `{str(route['gap_detected']).lower()}`",
        f"- Discovery recommended: `{str(route['discovery_recommended']).lower()}`",
        "",
        "## Parsed Intent",
        "",
        f"- Verb: `{route['intent']['intent_verb']}`",
        f"- Task phase: `{route['intent']['task_phase']}`",
        f"- Artifact type: `{route['intent'].get('artifact_type') or 'unknown'}`",
        f"- Artifact state: `{route['intent']['artifact_state']}`",
        f"- Confidence: `{route['intent']['confidence']}`",
        "",
        "## Primary Skills",
        "",
    ]
    if route["primary_skills"]:
        for skill in route["primary_skills"]:
            lines.append(f"- `{skill}`")
    else:
        lines.append("- none")
    lines.extend(["", "## Fallback Skills", ""])
    if route["fallback_skills"]:
        for skill in route["fallback_skills"]:
            lines.append(f"- `{skill}`")
    else:
        lines.append("- none")
    lines.extend(["", "## Do Without Skill", ""])
    if route["do_without_skill"]:
        for item in route["do_without_skill"]:
            lines.append(f"- {item}")
    else:
        lines.append("- none")
    lines.extend(["", "## Route Reason", ""])
    for item in route["route_reason"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Quality Notes", ""])
    if route["quality_notes"]:
        for item in route["quality_notes"]:
            lines.append(f"- {item}")
    else:
        lines.append("- none")
    lines.extend(["", "## Discovery / Install", ""])
    if route["install_candidates"]:
        for item in route["install_candidates"]:
            lines.append(f"- `{item['package']}` -> `{item.get('install_hint') or 'n/a'}`")
    else:
        lines.append("- none")
    lines.extend(["", "## Expected Handoff", ""])
    lines.append(f"- {route['expected_handoff']}")
    lines.append("")
    return "\n".join(lines)


def do_skill_route(config: HubConfig, task: str, target_arg: str) -> int:
    work_modes, work_modes_meta, _findings = load_work_modes(config)
    installed_skills = scan_installed_skills(config.skill_roots)
    inventory = build_skill_inventory(installed_skills, work_modes, work_modes_meta["cold_skills"])
    target = Path(target_arg).expanduser().resolve()
    if not target.exists():
        print(f"Target path does not exist: {target}", file=sys.stderr)
        return 1
    if not target.is_dir():
        print(f"Target path must be a directory: {target}", file=sys.stderr)
        return 1

    intake = inspect_folder(config, target, work_modes, inventory)
    route_registry = load_skill_route_registry(config)
    intent = infer_router_intent(task, intake, route_registry)
    quality_signals = build_skill_quality_signals(load_skill_iteration_registry(config))
    primary_candidates, fallback_candidates, quality_notes, local_matches = select_skill_route_plan(
        installed_skills,
        inventory,
        intake,
        task,
        quality_signals,
        intent,
    )
    need_skill, need_reason = skill_route_need(task, intake, local_matches, intent)
    strong_primary = any(
        entry["artifact_fit"]
        or entry["phase_fit"]
        or entry["match"]
        or intake["target"] in entry.get("quality", {}).get("folder_counts", {})
        for entry in primary_candidates
    )
    specialized_artifact_gap = bool(
        need_skill
        and intent["artifact_state"] == "existing"
        and intent["task_phase"] in {"qa", "correction"}
        and intent.get("artifact_type")
        and not any(entry["specialized_fit"] for entry in primary_candidates)
    )
    gap_detected = bool(
        need_skill
        and (
            not primary_candidates
            or (intake["route_strategy"] == "full_skill_scan" and not strong_primary)
            or specialized_artifact_gap
        )
    )
    install_candidates: list[dict[str, Any]] = []
    if gap_detected:
        discovery_payload = run_skill_discovery_for_route(config, task, inventory, installed_skills)
        install_candidates = discovery_payload.get("remote_matches", [])[:3]
        if discovery_payload.get("warnings"):
            quality_notes.extend([f"discovery_note={note}" for note in discovery_payload["warnings"][:2]])

    if not need_skill:
        primary_skills: list[str] = []
        fallback_skills: list[str] = []
        do_without_skill = [
            "Proceed directly and keep the acceptance target explicit.",
            "Escalate to skill discovery only if the manual path becomes repetitive or brittle.",
        ]
        expected_handoff = "Direct execution should be faster than skill orchestration for this task."
    else:
        primary_skills = [entry["name"] for entry in primary_candidates[:3]]
        fallback_skills = [entry["name"] for entry in fallback_candidates[:4] if entry["name"] not in primary_skills]
        do_without_skill = []
        if primary_skills:
            expected_handoff = "Use the primary lane first, keep the fallback lane ready, and only expand to discovery if the route stalls."
        elif gap_detected:
            expected_handoff = "No primary skill currently fits this correction workflow; review discovery candidates or proceed manually with the fallback helpers."
        else:
            expected_handoff = "No primary skill was selected; use the fallback lane or proceed directly with a manual workflow."

    route_reason = [need_reason]
    if primary_candidates:
        route_reason.append(
            "Top route: "
            + ", ".join(
                f"`{entry['name']}` ({'; '.join(entry['reasons'][:3])})"
                for entry in primary_candidates[:3]
            )
        )
    if gap_detected:
        route_reason.append("Current active/fallback lanes do not provide a strong task-specific fit; discovery is recommended.")
    if specialized_artifact_gap:
        route_reason.append(
            f"Existing `{intent['artifact_type']}` correction/QA work outranks the default `{intake['predicted_mode']}` lane; no artifact-fit skill is installed yet."
        )

    entry = {
        "id": new_record_id("route"),
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "task": task.strip(),
        "target_path": str(target),
        "predicted_mode": intake["predicted_mode"],
        "confidence": intake["confidence"],
        "route_strategy": intake["route_strategy"],
        "need_skill": need_skill,
        "primary_skills": primary_skills,
        "fallback_skills": fallback_skills,
        "do_without_skill": do_without_skill,
        "gap_detected": gap_detected,
        "discovery_recommended": gap_detected,
        "install_candidates": install_candidates,
        "route_reason": route_reason,
        "quality_notes": quality_notes[:6],
        "expected_handoff": expected_handoff,
        "local_match_count": len(local_matches),
        "remote_match_count": len(install_candidates),
        "intent": intent,
    }
    payload = route_registry
    entries = payload.get("entries", [])
    if not isinstance(entries, list):
        entries = []
    entries.append(entry)
    payload["generated_at"] = entry["generated_at"]
    payload["entries"] = entries[-25:]
    save_skill_route_registry(config, payload)
    print(render_skill_route_markdown(entry), end="")
    return 0 if not gap_detected else 2


def do_skill_review(config: HubConfig) -> int:
    payload = load_skill_iteration_registry(config)
    print(render_skill_review_markdown(payload), end="")
    return 0


def do_skill_promote(config: HubConfig, proposal_id: str) -> int:
    payload = load_skill_iteration_registry(config)
    proposal = find_proposal(payload, proposal_id)
    if not proposal:
        print(f"Unknown proposal: {proposal_id}", file=sys.stderr)
        return 1
    if proposal.get("status") == "promoted_to_fallback":
        print(f"Proposal `{proposal_id}` is already promoted to the fallback lane.")
        return 0
    if proposal.get("status") == "rejected":
        print(f"Proposal `{proposal_id}` was rejected and cannot be promoted.", file=sys.stderr)
        return 1

    work_modes, work_modes_meta, _findings = load_work_modes(config)
    installed_skills = scan_installed_skills(config.skill_roots)
    inventory = build_skill_inventory(installed_skills, work_modes, work_modes_meta["cold_skills"])
    skill_name = proposal["skill_name"]
    mode_name = proposal["mode"]
    if mode_name not in work_modes:
        print(f"Unknown work mode in proposal: {mode_name}", file=sys.stderr)
        return 1
    if skill_name not in inventory["installed_skills"]:
        print(f"Skill is no longer installed: {skill_name}", file=sys.stderr)
        return 1
    if skill_name not in inventory["candidate_skills"]:
        if skill_name in work_modes[mode_name].fallback_skills or skill_name in work_modes[mode_name].active_skills:
            print(
                f"Skill `{skill_name}` is no longer a candidate in `{mode_name}`; resolve or reject proposal `{proposal_id}` instead of promoting it.",
                file=sys.stderr,
            )
            return 1
        print(f"Skill `{skill_name}` is no longer in the candidate lane.", file=sys.stderr)
        return 1

    mode = work_modes[mode_name]
    fallback_skills = list(mode.fallback_skills)
    if skill_name not in fallback_skills and skill_name not in mode.active_skills:
        fallback_skills.append(skill_name)
        work_modes[mode_name] = replace(mode, fallback_skills=tuple(fallback_skills))
        patch_mode_fallback_skills(config, mode_name, fallback_skills)

    proposal["status"] = "promoted_to_fallback"
    proposal["resolved_at"] = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    proposal["resolution_reason"] = "Promoted to fallback lane."
    payload["generated_at"] = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    save_skill_iteration_registry(config, payload)
    write_all_proposal_files(config, payload)
    print(f"Promoted `{skill_name}` into `{mode_name}` fallback lane via proposal `{proposal_id}`.")
    return 0


def do_skill_reject(config: HubConfig, proposal_id: str, reason: str) -> int:
    payload = load_skill_iteration_registry(config)
    proposal = find_proposal(payload, proposal_id)
    if not proposal:
        print(f"Unknown proposal: {proposal_id}", file=sys.stderr)
        return 1
    if proposal.get("status") == "rejected":
        print(f"Proposal `{proposal_id}` is already rejected.")
        return 0
    if proposal.get("status") == "promoted_to_fallback":
        print(f"Proposal `{proposal_id}` is already promoted and cannot be rejected.", file=sys.stderr)
        return 1
    proposal["status"] = "rejected"
    proposal["resolved_at"] = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    proposal["resolution_reason"] = reason.strip()
    payload["generated_at"] = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    save_skill_iteration_registry(config, payload)
    write_all_proposal_files(config, payload)
    print(f"Rejected proposal `{proposal_id}`.")
    return 0


def do_intake(config: HubConfig, target_arg: str) -> int:
    work_modes, work_modes_meta, findings = load_work_modes(config)
    installed_skills = scan_installed_skills(config.skill_roots)
    inventory = build_skill_inventory(installed_skills, work_modes, work_modes_meta["cold_skills"])
    target = Path(target_arg).expanduser().resolve()
    if not target.exists():
        print(f"Target path does not exist: {target}", file=sys.stderr)
        return 1
    if not target.is_dir():
        print(f"Target path must be a directory: {target}", file=sys.stderr)
        return 1
    intake = inspect_folder(config, target, work_modes, inventory)
    print(render_intake_markdown(intake, findings))
    return 0


def inspect_folder(config: HubConfig, target: Path, work_modes: dict[str, WorkMode], inventory: dict[str, Any]) -> dict[str, Any]:
    files: list[Path] = []
    truncated = False
    for candidate in target.rglob("*"):
        if any(part in IGNORED_SCAN_DIRS for part in candidate.parts):
            continue
        if candidate.is_file():
            files.append(candidate)
            if len(files) >= INTAKE_SCAN_LIMIT:
                truncated = True
                break

    extension_counts: Counter[str] = Counter()
    keyword_counts: Counter[str] = Counter()
    path_keyword_counts: Counter[str] = Counter()
    signal_breakdown: dict[str, dict[str, Any]] = {}

    lower_file_names = [path.name.lower() for path in files]
    lower_relative_paths = [path.relative_to(target).as_posix().lower() for path in files]
    for path in files:
        suffix = path.suffix.lower()
        if suffix:
            extension_counts[suffix] += 1

    for name, mode in work_modes.items():
        ext_score = 0
        keyword_hits = 0
        path_hits = 0
        ext_matches: list[str] = []
        keyword_matches: list[str] = []
        path_matches: list[str] = []
        for ext in mode.extensions:
            if extension_counts[ext]:
                ext_score += extension_counts[ext] * 3
                ext_matches.append(f"{ext} x{extension_counts[ext]}")
        for keyword in mode.keywords:
            hits = sum(1 for value in lower_file_names if keyword in value)
            if hits:
                keyword_hits += hits * 2
                keyword_matches.append(f"{keyword} x{hits}")
                keyword_counts[keyword] += hits
        for keyword in mode.path_keywords:
            hits = sum(1 for value in lower_relative_paths if keyword in value)
            if hits:
                path_hits += hits
                path_matches.append(f"{keyword} x{hits}")
                path_keyword_counts[keyword] += hits
        if name == "analysis" and any(ext in extension_counts for ext in DATA_EXTENSIONS):
            ext_score += 2
        if name == "writing" and extension_counts[".pdf"] and extension_counts[".md"]:
            ext_score += 2
        if name in {"meeting", "course"} and any(keyword in "/".join(lower_relative_paths) for keyword in mode.path_keywords):
            path_hits += 2
        total = ext_score + keyword_hits + path_hits
        signal_breakdown[name] = {
            "score": total,
            "ext_matches": ext_matches,
            "keyword_matches": keyword_matches,
            "path_matches": path_matches,
        }

    ranked = sorted(signal_breakdown.items(), key=lambda item: item[1]["score"], reverse=True)
    predicted_mode = ranked[0][0] if ranked else "writing"
    top_score = ranked[0][1]["score"] if ranked else 0
    second_score = ranked[1][1]["score"] if len(ranked) > 1 else 0
    if top_score <= 0:
        confidence = 0.0
    else:
        confidence = round(top_score / (top_score + second_score + 1), 3)

    active_lane = [skill for skill in work_modes[predicted_mode].active_skills if skill in inventory["active_installed"]]
    fallback_lane = [skill for skill in work_modes[predicted_mode].fallback_skills if skill in inventory["installed_skills"]]
    route_strategy = "active_lane" if confidence >= HIGH_CONFIDENCE_THRESHOLD and active_lane else "full_skill_scan"

    output_like = sum(
        1 for value in lower_relative_paths for keyword in OUTPUT_HINT_KEYWORDS if keyword in value
    )
    reuse_pipeline = predicted_mode == "analysis" and bool(
        sum(extension_counts[ext] for ext in DATA_EXTENSIONS if ext in extension_counts) and output_like
    )

    file_types = sorted(extension_counts.items(), key=lambda item: (-item[1], item[0]))
    next_actions = build_intake_actions(predicted_mode, route_strategy, reuse_pipeline, work_modes[predicted_mode], active_lane, fallback_lane)
    intake = {
        "target": str(target),
        "files_scanned": len(files),
        "scan_truncated": truncated,
        "detected_file_types": file_types,
        "predicted_mode": predicted_mode,
        "confidence": confidence,
        "route_strategy": route_strategy,
        "router_fallback_recommended": route_strategy != "active_lane",
        "reuse_pipeline": reuse_pipeline,
        "active_lane": active_lane,
        "fallback_lane": fallback_lane,
        "output_contract": list(work_modes[predicted_mode].output_contract),
        "signals": signal_breakdown[predicted_mode],
        "next_actions": next_actions,
        "continuity": None,
    }
    recall_payload = load_recall_payload(config, target, predicted_mode)
    continuity = extract_continuity_hint(recall_payload)
    if continuity:
        intake["continuity"] = continuity
        action = continuity_action(continuity)
        if action:
            intake["next_actions"] = list(dict.fromkeys([action, *intake["next_actions"]]))
    return intake


def build_intake_actions(
    predicted_mode: str,
    route_strategy: str,
    reuse_pipeline: bool,
    mode: WorkMode,
    active_lane: list[str],
    fallback_lane: list[str],
) -> list[str]:
    actions: list[str] = []
    if route_strategy == "active_lane":
        lane_preview = ", ".join(f"`{skill}`" for skill in active_lane[:5]) or "the mode lane"
        actions.append(f"Start from the `{predicted_mode}` lane with {lane_preview}.")
    else:
        fallback_preview = ", ".join(f"`{skill}`" for skill in fallback_lane[:5]) or "a broader skill scan"
        actions.append(f"Confidence is low; review {fallback_preview} before expanding to the full skill inventory.")
    if reuse_pipeline:
        actions.append("Treat this as a new dataset version of an existing pipeline before changing methods or outputs.")
    actions.extend(mode.output_contract[:2])
    return list(dict.fromkeys(actions))


def render_intake_markdown(intake: dict[str, Any], findings: list[dict[str, str]]) -> str:
    file_types = intake["detected_file_types"]
    type_preview = ", ".join(f"`{ext}` x{count}" for ext, count in file_types[:8]) or "none"
    if len(file_types) > 8:
        type_preview = f"{type_preview} ..."
    signal_parts = intake["signals"]["ext_matches"] + intake["signals"]["keyword_matches"] + intake["signals"]["path_matches"]
    signal_preview = ", ".join(signal_parts[:8]) or "weak signal"
    lines = [
        "# Folder Intake",
        "",
        f"- Target: `{intake['target']}`",
        f"- Files scanned: `{intake['files_scanned']}`",
        f"- Scan truncated: `{intake['scan_truncated']}`",
        f"- Detected file types: {type_preview}",
        f"- Predicted mode: `{intake['predicted_mode']}`",
        f"- Confidence: `{intake['confidence']}`",
        f"- Route strategy: `{intake['route_strategy']}`",
        f"- Reuse pipeline: `{str(intake['reuse_pipeline']).lower()}`",
        f"- Router fallback recommended: `{str(intake['router_fallback_recommended']).lower()}`",
        "",
        "## Signals",
        "",
        f"- {signal_preview}",
        "",
        "## Continuity Hint",
        "",
    ]
    continuity = intake.get("continuity")
    if isinstance(continuity, dict) and continuity.get("source"):
        lines.extend(
            [
                f"- Source: `{continuity['source']}`",
                f"- Event time: `{continuity.get('event_time', '') or 'unknown'}`",
                f"- Path: `{continuity.get('source_path', '') or 'n/a'}`",
                f"- Summary: {continuity.get('summary', '') or 'none'}",
                f"- Next step: {continuity.get('next_step', '') or 'none'}",
                f"- Rank explanation: `{continuity.get('rank_explanation', 'n/a')}`",
                "",
            ]
        )
    else:
        lines.extend(["- none", ""])
    lines.extend([
        "## Active Lane",
        "",
    ])
    if intake["active_lane"]:
        for skill in intake["active_lane"]:
            lines.append(f"- `{skill}`")
    else:
        lines.append("- none")
    lines.extend(["", "## Output Contract", ""])
    for item in intake["output_contract"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Recommended Next Actions", ""])
    for action in intake["next_actions"]:
        lines.append(f"- {action}")
    if findings:
        lines.extend(["", "## Mode Config Notes", ""])
        for finding in findings[:5]:
            lines.append(f"- `{finding['code']}`: {finding['message']}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    try:
        config = load_config(Path(args.config).expanduser().resolve())
        if args.command == "refresh":
            return do_refresh(config)
        if args.command == "doctor":
            return do_doctor(config)
        if args.command == "status":
            return do_status(config)
        if args.command == "bootstrap":
            return do_bootstrap(config, args.path, args.write_agent, args.thread_id, args.cwd)
        if args.command == "overlay":
            return do_overlay(config, args.path)
        if args.command == "closeout":
            return do_closeout(config, args.path, args.summary, args.used_skills, args.outcome, args.reuse)
        if args.command == "skill-route":
            return do_skill_route(config, args.task, args.path)
        if args.command == "skill-discover":
            return do_skill_discover(config, args.query)
        if args.command == "skill-review":
            return do_skill_review(config)
        if args.command == "skill-promote":
            return do_skill_promote(config, args.proposal_id)
        if args.command == "skill-reject":
            return do_skill_reject(config, args.proposal_id, args.reason)
        if args.command == "memory-triage":
            return do_memory_triage(config, args.window, args.root)
        if args.command == "session-gate":
            return do_session_gate(config, args.thread_id, args.cwd)
        if args.command == "capabilities":
            return do_capabilities(config)
        if args.command == "review-loop":
            return do_review_loop(config, args.path, args.changed, args.from_git, args.max_candidates, args.review_limit, args.json)
        if args.command == "reconcile":
            return do_reconcile(config)
        return do_intake(config, args.path)
    except ConfigError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except HubRuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
