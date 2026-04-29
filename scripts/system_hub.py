#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import plistlib
import re
import shlex
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
ARTIFACT_HARNESS_DEFAULT_KEYWORDS = (
    "artifact harness",
    "harness spec",
    "requirement form",
    "packet init",
    "form fill",
    "artifact packet",
    "artifact mission",
)
ARTIFACT_HARNESS_STATUSES = (
    "draft",
    "filled",
    "reviewed",
    "approved",
    "blocked",
    "executed",
    "verified",
    "superseded",
    "archived",
)
ARTIFACT_HARNESS_PROVENANCE_CATEGORIES = (
    "user_mission",
    "template_default",
    "generated_scaffold",
    "packet_reference",
    "repo_evidence",
    "agent_inference",
    "runtime_output",
    "test_result",
    "human_approval",
    "approval_required",
    "unresolved",
    "unknown",
)
ARTIFACT_HARNESS_SCHEMA_VERSION = 1
ARTIFACT_HARNESS_COMMAND_SCHEMA_VERSION = 1
ARTIFACT_HARNESS_REQUIRED_PACKET_KEYS = (
    "artifact_harness_spec",
    "hr_staffing_packet",
    "team_operating_packet",
    "capability_access_packet",
    "runtime_mapping",
)
ARTIFACT_HARNESS_OPTIONAL_REPORT_KEYS = (
    "replay_evidence",
    "provenance_ledger",
    "runtime_readiness_report",
    "approval_evidence",
    "runtime_invocation_report",
    "repair_plan",
)
ARTIFACT_HARNESS_SCHEMA_METADATA_FILENAME = "packet_schema_metadata.json"
ARTIFACT_HARNESS_APPROVAL_EVIDENCE_FILENAME = "approval_evidence.json"
ARTIFACT_HARNESS_RUNTIME_INVOCATION_REPORT_FILENAME = "runtime_invocation_report.json"
ARTIFACT_HARNESS_REPAIR_PLAN_FILENAME = "repair_plan.json"
ARTIFACT_HARNESS_RUNTIME_APPROVAL_GATE_ID = "runtime_execution"
ARTIFACT_HARNESS_SUPPORTED_RUNTIME_ADAPTERS = ("open-multi-agent",)
ARTIFACT_HARNESS_SUPPORTED_EXECUTION_SURFACES = ("typescript-runTasks", "cli")
ROSTER_PRODUCT_TARGET = "@roster"
ROSTER_VERIFIED_INVOCATION_MECHANISM = "scripts/brain.sh packet-route"
ROSTER_SKILL_NAME = "roster"
ROSTER_SKILL_SOURCE_DIR = ROOT / "skills" / ROSTER_SKILL_NAME
ROSTER_CURRENT_USER_INVOCATION = "Roster, <task>"
ROSTER_HEALTH_DEFAULT_ID = "roster-health-smoke"
ROSTER_HEALTH_VISIBILITY_UTTERANCE = "@roster"
ROSTER_HEALTH_PACKET_UTTERANCE = "@roster make a review-ready Roster health-check report artifact"
ROSTER_PREFERENCES_FILENAME = "roster_preferences.json"
ROSTER_PREFERENCES_SCHEMA_VERSION = 1
ROSTER_PREFERENCES_MAX_ACTIVE = 12
ROSTER_PROVIDER_AUTH_ENV_DEFAULTS = {
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "gemini": "GEMINI_API_KEY",
    "google": "GOOGLE_API_KEY",
    "deepseek": "DEEPSEEK_API_KEY",
    "grok": "XAI_API_KEY",
    "xai": "XAI_API_KEY",
    "minimax": "MINIMAX_API_KEY",
    "qiniu": "QINIU_ACCESS_KEY",
}
PACKET_ROUTE_NATURAL_PRODUCTION_CUES = (
    "make",
    "create",
    "draft",
    "write",
    "prepare",
    "produce",
    "generate",
    "build",
    "assemble",
    "compose",
    "design",
    "edit",
    "revise",
    "polish",
    "organize",
    "organized",
    "finish",
    "complete",
    "repair",
    "render",
    "做",
    "製作",
    "生成",
    "產生",
    "寫",
    "撰寫",
    "草擬",
    "整理",
    "組",
    "組好",
    "完成",
    "修改",
    "潤飾",
    "準備",
)
PACKET_ROUTE_NATURAL_QUALITY_CUES = (
    "review-ready",
    "publication-ready",
    "final",
    "polished",
    "complete",
    "finished",
    "verified",
    "ready",
    "可審查",
    "審查",
    "完成版",
    "可用",
    "整理好",
)
ROSTER_QUALITY_DIRECTION_TERMS = (
    "quality loop",
    "Quality",
    "quality direction",
    "quality setting",
    "quality settings",
    "self-check",
    "self check",
    "selfcheck",
    "QA",
    "品質",
    "品質方向",
    "品保",
    "自檢",
    "自我檢查",
    "檢核",
    "驗收",
)
ROSTER_QUALITY_DIRECTION_ACTION_TERMS = (
    "loop",
    "iteration",
    "iterations",
    "check",
    "set",
    "setting",
    "settings",
    "define",
    "configure",
    "direction",
    "review",
    "inspect",
    "run",
    "CV檢查",
    "用CV檢查",
    "vision review",
    "做",
    "設定",
    "怎麼",
    "如何",
    "要怎麼",
    "檢查",
    "檢視",
    "幫我看",
    "看",
    "安排",
    "規劃",
    "循環",
    "迭代",
)
ROSTER_VISUAL_ARTIFACT_TERMS = (
    "visual artifact",
    "visual",
    "slide deck",
    "lecture slides",
    "lecture video",
    "slides",
    "slide",
    "deck",
    "presentation",
    "video",
    "scene",
    "render",
    "screenshot",
    "image",
    "frame",
    "ui",
    "interface",
    "dashboard",
    "figure",
    "chart",
    "plot",
    "視覺",
    "投影片",
    "簡報",
    "影片",
    "場景",
    "渲染",
    "截圖",
    "圖片",
    "圖像",
    "畫面",
    "介面",
    "圖表",
)
ROSTER_VISUAL_QUALITY_LOOP_TERMS = (
    "CV",
    "computer vision",
    "vision review",
    "vision-model review",
    "quality loop",
    "visual quality",
    "visual check",
    "quality check",
    "playback check",
    "render check",
    "screenshot check",
    "occlusion",
    "overlap",
    "readability",
    "contrast",
    "mismatch",
    "畫面品質",
    "播放檢查",
    "截圖檢查",
    "遮住",
    "遮擋",
    "重疊",
    "可讀",
    "對比",
    "不一致",
    "CV檢查",
    "視覺檢查",
)
ROSTER_CV_INSPECTION_ROUTE_INPUTS = (
    "rendered image",
    "screenshot",
    "exported video frame",
    "video frame",
)
ROSTER_CV_INSPECTION_SUPPORTED_LOCAL_INPUT_MODES = (
    "existing rendered/exported visual file",
    "local render/export",
    "screenshot",
    "image",
    "rendered frame",
    "video frame",
    "playback/frame sampling",
    "OCR/readability review",
)
ROSTER_CV_INSPECTION_CHECKS = (
    "text occlusion",
    "key element occlusion",
    "layout overlap",
    "contrast/readability",
    "missing expected content",
    "slide/render/video mismatch",
)
ROSTER_CV_INSPECTION_CAPABILITY_REQUESTS = (
    "render_export_visual_evidence",
    "screenshot_capture",
    "playback_or_frame_sampling",
    "computer_use_or_app_playback",
    "ocr_text_readability",
    "vision_model_review",
)
ROSTER_CV_NO_VISUAL_EVIDENCE_POLICY = "visual quality is limited until a screenshot, render, frame, or playback evidence is inspected"
ROSTER_CV_VISUAL_EVIDENCE_ACQUISITION = (
    "use existing rendered images, screenshots, exported frames, or video frames when present",
    "render or export local artifacts into inspectable images or frames when safe",
    "request CAP-governed screenshot capture, playback, frame sampling, Computer Use, or app playback only when needed",
    "request CAP-governed OCR/readability or vision-model review when available",
    "ask the user for a screenshot or frame only after local evidence acquisition is unavailable",
)
ROSTER_CV_FINDING_SHAPE = {
    "artifact": "path or artifact label",
    "slide": "slide number/title when available",
    "frame": "frame id when available",
    "timecode": "timecode when available",
    "region": "visible region or location when possible",
    "issue_type": "occlusion|overlap|readability|contrast|missing_content|mismatch|other",
    "severity": "P0|P1|P2|P3",
    "evidence_source": "render|screenshot|frame|playback|ocr|vision_model|user_provided",
    "suggested_fix_owner": "role or owner responsible for correction",
    "suggested_correction": "specific correction to apply",
    "recheck_condition": "visible condition that must pass after correction",
}
PACKET_ROUTE_NATURAL_PROCESS_CUES = (
    "task",
    "workflow",
    "packet form",
    "requirement form",
    "form fill",
    "organized",
    "deliverable",
    "output",
    "artifact",
    "任務",
    "流程",
    "成果",
    "產出",
)
PACKET_ROUTE_NATURAL_DELIVERABLE_TERMS = (
    "appendix",
    "methods appendix",
    "slides",
    "slide",
    "slide deck",
    "lecture slides",
    "deck",
    "presentation",
    "video",
    "lecture video",
    "report",
    "manuscript",
    "paper",
    "draft",
    "section",
    "note",
    "notes",
    "figure",
    "table",
    "worksheet",
    "handout",
    "problem set",
    "solution",
    "script",
    "module",
    "dashboard",
    "artifact",
    "deliverable",
    "投影片",
    "簡報",
    "影片",
    "講義",
    "附錄",
    "文稿",
    "草稿",
    "報告",
    "圖表",
    "表格",
    "教材",
    "筆記",
    "文件",
    "成果",
    "產出",
)
PACKET_ROUTE_UNDERSPECIFIED_ARTIFACT_REFERENCES = (
    "this artifact",
    "the artifact",
    "artifact?",
    "this deliverable",
    "the deliverable",
    "這個 artifact",
    "這份 artifact",
    "這個成果",
    "這份成果",
    "這個產出",
    "這份產出",
)
DEFAULT_BRAIN_COMMANDS = (
    "refresh",
    "doctor",
    "status",
    "bootstrap",
    "intake",
    "artifact-harness",
    "packet-route",
    "roster-install",
    "roster-health",
    "roster-preferences",
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
    artifact_harness = sub.add_parser("artifact-harness", help="Create or inspect a deterministic Artifact Harness packet chain.")
    artifact_harness.add_argument("mission", nargs="?", help="User mission to convert into packet scaffolds, or status/resume/mark/replay/provenance/runtime-check/approval/runtime-invoke/schema-check/migrate/repair-plan for packet commands.")
    artifact_harness.add_argument("--path", default=".", help="Target workspace folder for the mission and packet output. Defaults to the current directory.")
    artifact_harness.add_argument("--id", default=None, help="Optional stable packet id. Defaults to a mission/path-derived id.")
    artifact_harness.add_argument("--artifact", default=None, help="Optional expected artifact path or label from the user mission.")
    artifact_harness.add_argument("--force", "--overwrite", action="store_true", dest="force", help="Explicitly overwrite an existing packet run.")
    artifact_harness.add_argument("--status", default=None, help="Lifecycle status for `artifact-harness mark`.")
    artifact_harness.add_argument("--note", default="", help="Optional lifecycle note for `artifact-harness mark`.")
    artifact_harness.add_argument("--gate", default=None, help="Approval gate id for `artifact-harness approval`.")
    artifact_harness.add_argument("--decision", default=None, help="Approval decision for `artifact-harness approval`: approved or denied.")
    artifact_harness.add_argument("--approver", default=None, help="Approver label for `artifact-harness approval`.")
    artifact_harness.add_argument("--adapter", default=None, help="Runtime adapter for `artifact-harness runtime-invoke`; supported: open-multi-agent.")
    artifact_harness.add_argument("--surface", default=None, help="Runtime execution surface for `artifact-harness runtime-invoke`; supported: typescript-runTasks, cli.")
    artifact_harness.add_argument("--dry-run", action="store_true", help="Create a guarded runtime invocation envelope without executing the adapter.")
    artifact_harness.add_argument("--json", action="store_true", help="Emit a machine-readable JSON result instead of Markdown.")
    packet_route = sub.add_parser("packet-route", help="Route a keyword phrase to a packet workflow; optionally create the packet chain.")
    packet_route.add_argument("utterance", help="User phrase to route with deterministic keyword matching.")
    packet_route.add_argument("--path", default=".", help="Target workspace folder for the routed packet and packet output. Defaults to the current directory.")
    packet_route.add_argument("--id", default=None, help="Optional existing or desired Artifact Harness packet id for downstream packet routing.")
    packet_route.add_argument("--create", action="store_true", help="Create the routed packet chain when a route matches.")
    packet_route.add_argument("--artifact", default=None, help="Optional expected artifact path or label passed through to artifact-harness.")
    packet_route.add_argument("--force", "--overwrite", action="store_true", dest="force", help="Explicitly overwrite an existing routed packet run when used with --create.")
    packet_route.add_argument("--json", action="store_true", help="Emit a machine-readable JSON route instead of Markdown.")
    roster_install = sub.add_parser("roster-install", help="Install or check the repo-owned Roster skill into a Codex skills root.")
    roster_install.add_argument("--codex-home", default=None, help="Codex home whose `skills/` directory should receive the roster skill. Defaults to CODEX_HOME or ~/.codex.")
    roster_install.add_argument("--skills-root", default=None, help="Explicit skills root to install into. Overrides --codex-home.")
    roster_install.add_argument("--force", "--overwrite", action="store_true", dest="force", help="Overwrite an existing installed roster skill.")
    roster_install.add_argument("--json", action="store_true", help="Emit a machine-readable JSON install result instead of Markdown.")
    roster_health = sub.add_parser("roster-health", help="Check the repo-native Roster invocation, packet output, and local provider wiring.")
    roster_health.add_argument("--path", default=".", help="Target workspace folder for the health-check packet output. Defaults to the current directory.")
    roster_health.add_argument("--id", default=None, help="Optional health-check packet id. Defaults to a generated roster-health-smoke id.")
    roster_health.add_argument("--provider", default=None, help="Optional LLM/provider name to validate from local environment state.")
    roster_health.add_argument("--auth-env", default=None, help="Optional environment variable name that should contain provider credentials.")
    roster_health.add_argument("--cv-provider", default=None, help="Optional CV/vision provider name to validate from local environment state.")
    roster_health.add_argument("--cv-auth-env", default=None, help="Optional environment variable name that should contain CV/vision provider credentials.")
    roster_health.add_argument("--codex-home", default=None, help="Optional Codex home whose `skills/roster` install should be verified.")
    roster_health.add_argument("--skills-root", default=None, help="Optional explicit skills root whose `roster` skill install should be verified.")
    roster_health.add_argument("--keep-artifacts", action="store_true", help="Keep the health-check packet output instead of cleaning it up after verification.")
    roster_health.add_argument("--json", action="store_true", help="Emit a machine-readable JSON health report instead of Markdown.")
    roster_preferences = sub.add_parser("roster-preferences", help="Record, list, or archive explicit workspace-local Roster preferences.")
    roster_preferences.add_argument("action", choices=("remember", "list", "forget"), help="Preference action to run.")
    roster_preferences.add_argument("text", nargs="?", default=None, help="Preference text for `remember`.")
    roster_preferences.add_argument("--path", default=".", help="Target workspace folder for the preferences file. Defaults to the current directory.")
    roster_preferences.add_argument("--id", default=None, help="Preference id for `forget`.")
    roster_preferences.add_argument("--json", action="store_true", help="Emit a machine-readable JSON preference result instead of Markdown.")
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


def artifact_harness_registry_path(config: HubConfig) -> Path:
    return config.contexts_dir / "artifact_harness_registry.json"


def artifact_harness_runs_dir(config: HubConfig) -> Path:
    return config.contexts_dir / "artifact_harness_runs"


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


def stable_packet_id(prefix: str, mission: str, target: Path, explicit_id: str | None = None) -> str:
    raw = explicit_id.strip() if explicit_id else mission.strip()
    slug = re.sub(r"[^a-z0-9]+", "-", raw.lower()).strip("-")
    if not slug:
        slug = "artifact-mission"
    slug = slug[:64].strip("-") or "artifact-mission"
    if explicit_id:
        return slug
    digest = hashlib.sha1(f"{mission.strip()}|{target.resolve()}".encode("utf-8")).hexdigest()[:8]
    return f"{prefix}-{slug}-{digest}"


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


def default_artifact_harness_registry() -> dict[str, Any]:
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


def load_routing_section(config: HubConfig) -> dict[str, Any]:
    if not config.config_path.exists():
        return {}
    try:
        payload = tomllib.loads(config.config_path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError:
        return {}
    section = payload.get("routing")
    if not isinstance(section, dict):
        return {}
    return section


def resolve_routing_path(config: HubConfig, value: Any, default: str) -> Path:
    raw = value if isinstance(value, str) and value.strip() else default
    path = Path(raw).expanduser()
    if path.is_absolute():
        return path.resolve()
    return (config.workspace_root / path).resolve()


def load_team_alias_registry(config: HubConfig, routing: dict[str, Any]) -> dict[str, Any]:
    path = resolve_routing_path(config, routing.get("team_alias_registry"), "contexts/team_alias_registry.json")
    return load_json_file(path, {})


def artifact_harness_keyword_list(config: HubConfig) -> list[str]:
    routing = load_routing_section(config)
    registry = load_team_alias_registry(config, routing)
    keywords: list[str] = list(ARTIFACT_HARNESS_DEFAULT_KEYWORDS)
    raw_config_keywords = routing.get("artifact_harness_keywords", [])
    if isinstance(raw_config_keywords, list):
        keywords.extend(item for item in raw_config_keywords if isinstance(item, str))
    for family in registry.get("keyword_families", []):
        if not isinstance(family, dict) or family.get("id") != "artifact_harness_workflow":
            continue
        raw_family_keywords = family.get("keywords", [])
        if isinstance(raw_family_keywords, list):
            keywords.extend(item for item in raw_family_keywords if isinstance(item, str))

    seen: set[str] = set()
    deduped: list[str] = []
    for keyword in keywords:
        normalized = " ".join(keyword.strip().lower().split())
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        deduped.append(keyword.strip())
    return deduped


def artifact_harness_entrypoint(config: HubConfig) -> str:
    routing = load_routing_section(config)
    raw = routing.get("artifact_harness_entrypoint", "artifact-harness")
    if not isinstance(raw, str) or not raw.strip():
        raw = "artifact-harness"
    return raw.strip()


def artifact_harness_packet_root(config: HubConfig, target: Path) -> Path:
    routing = load_routing_section(config)
    raw = routing.get("artifact_harness_packet_root", "contexts/artifact_harness_runs")
    if not isinstance(raw, str) or not raw.strip():
        raw = "contexts/artifact_harness_runs"
    root = Path(raw).expanduser()
    if root.is_absolute():
        return root.resolve()
    return (target / root).resolve()


def artifact_harness_registry_path_for_target(config: HubConfig, target: Path) -> Path:
    return artifact_harness_packet_root(config, target).parent / "artifact_harness_registry.json"


def relative_path_from(root: Path, path: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def ensure_targets_under_root(root: Path, targets: dict[str, Path]) -> None:
    root_resolved = root.resolve()
    for label, path in targets.items():
        try:
            path.resolve().relative_to(root_resolved)
        except ValueError as exc:
            raise HubRuntimeError(f"Refusing to write {label} outside target workspace: {path}") from exc


def dump_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def roster_preferences_path_for_target(target: Path) -> Path:
    return target.resolve() / "contexts" / ROSTER_PREFERENCES_FILENAME


def default_roster_preferences_registry(target: Path) -> dict[str, Any]:
    return {
        "schema_version": ROSTER_PREFERENCES_SCHEMA_VERSION,
        "registry_type": "roster_preferences",
        "generated_at": None,
        "target_path": str(target.resolve()),
        "write_policy": "explicit roster-preferences remember only",
        "boundary": {
            "scope": "workspace-local coordination preferences",
            "does_not_replace": [
                "Artifact Harness SPEC contract or acceptance",
                "HR staffing boundary",
                "Team Architect collaboration pattern",
                "Capability Access Packet authorization",
                "runtime adapter policy",
                "artifact verification or final acceptance",
            ],
        },
        "entries": [],
    }


def load_roster_preferences_registry(target: Path, *, strict: bool = False) -> dict[str, Any]:
    path = roster_preferences_path_for_target(target)
    default = default_roster_preferences_registry(target)
    if strict:
        payload = load_json_file_strict(path, default, "Roster preferences registry")
    else:
        payload = load_json_file(path, default)
    if not isinstance(payload.get("entries"), list):
        payload["entries"] = []
    payload.setdefault("schema_version", ROSTER_PREFERENCES_SCHEMA_VERSION)
    payload.setdefault("registry_type", "roster_preferences")
    payload.setdefault("target_path", str(target.resolve()))
    payload.setdefault("write_policy", "explicit roster-preferences remember only")
    payload.setdefault("boundary", default["boundary"])
    return payload


def roster_preference_category(text: str) -> str:
    normalized = " ".join(text.lower().split())
    visual_terms = (
        "cv",
        "vision",
        "visual",
        "screenshot",
        "screen",
        "slide",
        "video",
        "render",
        "frame",
        "occlusion",
        "overlap",
        "遮擋",
        "重疊",
        "畫面",
        "截圖",
        "影片",
        "投影片",
        "簡報",
    )
    quality_terms = ("quality", "qa", "check", "review", "檢查", "品質", "驗收", "自我檢查")
    staffing_terms = ("team", "role", "staff", "roster", "學生", "老師", "角色", "團隊", "分工")
    invocation_terms = ("invoke", "call", "trigger", "使用", "呼叫", "啟動", "口令")
    if any(term in normalized for term in visual_terms):
        return "visual_quality_preference"
    if any(term in normalized for term in quality_terms):
        return "quality_preference"
    if any(term in normalized for term in staffing_terms):
        return "staffing_preference"
    if any(term in normalized for term in invocation_terms):
        return "invocation_preference"
    return "coordination_preference"


def roster_preference_active_entries(registry: dict[str, Any]) -> list[dict[str, Any]]:
    entries = [entry for entry in registry.get("entries", []) if isinstance(entry, dict)]
    active = [entry for entry in entries if entry.get("status", "active") == "active"]
    return active[-ROSTER_PREFERENCES_MAX_ACTIVE:]


def roster_preferences_summary(target: Path) -> dict[str, Any]:
    path = roster_preferences_path_for_target(target)
    registry = load_roster_preferences_registry(target, strict=False)
    entries = [entry for entry in registry.get("entries", []) if isinstance(entry, dict)]
    active = roster_preference_active_entries(registry)
    return {
        "schema_version": registry.get("schema_version", ROSTER_PREFERENCES_SCHEMA_VERSION),
        "path": str(path),
        "exists": path.exists(),
        "entry_count": len(entries),
        "active_count": len(active),
        "active": active,
        "write_policy": registry.get("write_policy", "explicit roster-preferences remember only"),
        "boundary": registry.get("boundary", default_roster_preferences_registry(target)["boundary"]),
    }


def roster_preferences_base_payload(action: str, target: Path) -> dict[str, Any]:
    path = roster_preferences_path_for_target(target)
    return {
        "schema_version": ROSTER_PREFERENCES_SCHEMA_VERSION,
        "report_type": "roster_preferences",
        "action": action,
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "target_path": str(target.resolve()),
        "preferences_path": str(path),
        "write_policy": "explicit roster-preferences remember only",
        "scope": "workspace",
        "recorded": False,
        "forgot": False,
        "refused": False,
        "reason": None,
    }


def build_roster_preference_entry(text: str) -> dict[str, Any]:
    now = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    return {
        "id": new_record_id("roster-pref"),
        "created_at": now,
        "updated_at": now,
        "status": "active",
        "scope": "workspace",
        "source": "explicit_roster_preferences_remember",
        "category": roster_preference_category(text),
        "preference": text,
        "applies_to": "Roster coordination defaults only",
        "boundary": "does not replace packet contracts, capability authorization, runtime policy, artifact verification, or final acceptance",
    }


def render_roster_preferences_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Roster Preferences",
        "",
        f"- Action: `{payload.get('action')}`",
        f"- Target path: `{payload.get('target_path')}`",
        f"- Preferences path: `{payload.get('preferences_path')}`",
        f"- Recorded: `{payload.get('recorded')}`",
        f"- Forgot: `{payload.get('forgot')}`",
        f"- Refused: `{payload.get('refused')}`",
        f"- Active count: `{payload.get('active_count', 0)}`",
        "",
        "## Active Preferences",
        "",
    ]
    active = payload.get("active", [])
    if active:
        for entry in active:
            lines.append(f"- `{entry.get('id')}` ({entry.get('category')}): {entry.get('preference')}")
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- Preferences guide Roster coordination defaults only.",
            "- They do not replace packet contracts, capability authorization, runtime policy, artifact verification, or final acceptance.",
            "",
        ]
    )
    if payload.get("reason"):
        lines.extend(["## Reason", "", f"- `{payload.get('reason')}`", ""])
    return "\n".join(lines)


def do_roster_preferences(
    config: HubConfig,
    action: str,
    target_arg: str,
    text: str | None,
    preference_id: str | None,
    emit_json: bool = False,
) -> int:
    target = Path(target_arg).expanduser().resolve()
    if not target.exists():
        payload = {
            **roster_preferences_base_payload(action, target),
            "refused": True,
            "reason": "missing_target",
            "summary": roster_preferences_summary(target),
        }
        print(f"Target path does not exist: {target}", file=sys.stderr)
        if emit_json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 1
    if not target.is_dir():
        payload = {
            **roster_preferences_base_payload(action, target),
            "refused": True,
            "reason": "target_not_directory",
            "summary": roster_preferences_summary(target),
        }
        print(f"Target path must be a directory: {target}", file=sys.stderr)
        if emit_json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 1

    path = roster_preferences_path_for_target(target)
    payload = roster_preferences_base_payload(action, target)
    try:
        registry = load_roster_preferences_registry(target, strict=True)
    except HubRuntimeError as exc:
        payload.update({"refused": True, "reason": "invalid_preferences_registry"})
        print(str(exc), file=sys.stderr)
        if emit_json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 1

    if action == "remember":
        preference = (text or "").strip()
        if not preference:
            payload.update({"refused": True, "reason": "empty_preference"})
            print("Roster preference text must not be empty.", file=sys.stderr)
            if emit_json:
                print(json.dumps(payload, ensure_ascii=False, indent=2))
            return 1
        entry = build_roster_preference_entry(preference)
        registry["generated_at"] = payload["generated_at"]
        registry["target_path"] = str(target.resolve())
        registry.setdefault("entries", []).append(entry)
        dump_json(path, registry)
        summary = roster_preferences_summary(target)
        payload.update(summary)
        payload.update({"recorded": True, "entry": entry})
    elif action == "list":
        summary = roster_preferences_summary(target)
        payload.update(summary)
    elif action == "forget":
        pref_id = (preference_id or "").strip()
        if not pref_id:
            payload.update({"refused": True, "reason": "missing_preference_id"})
            print("Roster preference forget requires --id <preference-id>.", file=sys.stderr)
            if emit_json:
                print(json.dumps(payload, ensure_ascii=False, indent=2))
            return 1
        changed = None
        now = payload["generated_at"]
        for entry in registry.get("entries", []):
            if isinstance(entry, dict) and entry.get("id") == pref_id:
                entry["status"] = "archived"
                entry["updated_at"] = now
                entry["archived_at"] = now
                changed = entry
                break
        if changed is None:
            payload.update({"refused": True, "reason": "preference_not_found"})
            print(f"Roster preference not found: {pref_id}", file=sys.stderr)
            if emit_json:
                print(json.dumps(payload, ensure_ascii=False, indent=2))
            return 1
        registry["generated_at"] = now
        dump_json(path, registry)
        summary = roster_preferences_summary(target)
        payload.update(summary)
        payload.update({"forgot": True, "entry": changed})
    else:
        payload.update({"refused": True, "reason": "unsupported_action"})
        if emit_json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 1

    if emit_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(render_roster_preferences_markdown(payload), end="")
    return 0


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
    if lower in {
        "runtime_overlay_registry.json",
        "skill_iteration_registry.json",
        "skill_discovery_registry.json",
        "skill_route_registry.json",
        "artifact_harness_registry.json",
    }:
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
    for base in (
        runtime_overlays_dir(config),
        skill_iteration_closeouts_dir(config),
        skill_iteration_proposals_dir(config),
        artifact_harness_runs_dir(config),
    ):
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
        artifact_harness_registry_path(config),
        memory_governance_registry_path(config),
        memory_governance_status_path(config),
    ):
        if extra.exists():
            writer_paths.add(relative_path(config, extra))
    for base in (
        runtime_overlays_dir(config),
        skill_iteration_closeouts_dir(config),
        skill_iteration_proposals_dir(config),
        artifact_harness_runs_dir(config),
    ):
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


def load_artifact_harness_registry(config: HubConfig, path: Path | None = None) -> dict[str, Any]:
    payload = load_json_file_strict(
        path or artifact_harness_registry_path(config),
        default_artifact_harness_registry(),
        "artifact harness registry",
    )
    if not isinstance(payload.get("entries", []), list):
        raise HubRuntimeError("Artifact harness registry must contain list field `entries`.")
    return payload


def save_artifact_harness_registry(config: HubConfig, payload: dict[str, Any], path: Path | None = None, target_root: Path | None = None) -> None:
    path = path or artifact_harness_registry_path(config)
    if target_root is None:
        ensure_repo_targets(config, {"artifact_harness_registry_json": path})
    else:
        ensure_targets_under_root(target_root, {"artifact_harness_registry_json": path})
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


def roster_cv_activation_ladder() -> list[dict[str, Any]]:
    return [
        {
            "step": "use_existing_visual_evidence",
            "preference": 1,
            "inputs": ["rendered image", "screenshot", "exported video frame"],
            "fallback": False,
        },
        {
            "step": "render_or_export_inspection_artifact",
            "preference": 2,
            "capability_requests": ["render_export_visual_evidence"],
            "capability_owner": "Capability Access Packet",
            "fallback": False,
        },
        {
            "step": "local_capture_or_playback",
            "preference": 3,
            "capability_requests": ["screenshot_capture", "playback_or_frame_sampling", "computer_use_or_app_playback"],
            "capability_owner": "Capability Access Packet",
            "fallback": False,
        },
        {
            "step": "ocr_or_vision_model_review",
            "preference": 4,
            "capability_requests": ["ocr_text_readability", "vision_model_review"],
            "capability_owner": "Capability Access Packet",
            "fallback": False,
        },
        {
            "step": "ask_user_for_screenshot_or_frame",
            "preference": 5,
            "fallback": True,
        },
    ]


def roster_cv_inspection_request(requested: bool) -> dict[str, Any]:
    if not requested:
        return {
            "requested": False,
            "mode": None,
            "inputs": [],
            "checks": [],
            "capability_requests": [],
            "authorization_owner": None,
            "execution_boundary": None,
            "activation_ladder": [],
            "no_visual_evidence_policy": None,
            "evidence_required_for_visual_acceptance": False,
            "finding_shape": None,
        }
    return {
        "requested": True,
        "mode": "activation_ladder",
        "inputs": list(ROSTER_CV_INSPECTION_ROUTE_INPUTS),
        "checks": list(ROSTER_CV_INSPECTION_CHECKS),
        "capability_requests": list(ROSTER_CV_INSPECTION_CAPABILITY_REQUESTS),
        "authorization_owner": "Capability Access Packet",
        "execution_boundary": "advisory until CAP authorizes the needed tools",
        "activation_ladder": roster_cv_activation_ladder(),
        "no_visual_evidence_policy": ROSTER_CV_NO_VISUAL_EVIDENCE_POLICY,
        "evidence_required_for_visual_acceptance": True,
        "finding_shape": dict(ROSTER_CV_FINDING_SHAPE),
    }


def artifact_harness_quality_loop_for_mission(mission: str) -> dict[str, Any]:
    natural_details = packet_route_natural_artifact_details(mission)
    front_doors = ["roster"] if match_artifact_harness_keywords(mission, ["Roster", "@roster"]) else []
    quality_details = packet_route_roster_quality_details(mission, front_doors)
    return packet_route_visual_quality_loop_details(mission, natural_details, quality_details)


def artifact_harness_cv_requested(quality_loop: dict[str, Any] | None) -> bool:
    if not isinstance(quality_loop, dict):
        return False
    cv_inspection = quality_loop.get("cv_inspection")
    return bool(isinstance(cv_inspection, dict) and cv_inspection.get("requested") is True)


def render_spec_cv_inspection_section(quality_loop: dict[str, Any] | None) -> str:
    if not artifact_harness_cv_requested(quality_loop):
        return ""
    return """
## Visual / CV Inspection Targets

- visual inspection request [source: mission keywords]: yes
- inspection inputs [source: Roster visual Quality loop]: rendered image, screenshot, video frame
- acceptance targets [source: Roster visual Quality loop]: text occlusion; key element occlusion; layout overlap; contrast/readability; missing expected content; slide/render/video mismatch
- visual acceptance rule [source: Roster CV activation ladder]: when visual output is part of the artifact, visual acceptance requires inspected visual evidence from a screenshot, render, frame, or playback sample
- no visual evidence rule [source: Roster CV activation ladder]: without inspected visual evidence, only non-visual, text, or structure checks can be marked complete; visual quality remains limited
- activation ladder [source: Roster CV activation ladder]: use existing visual evidence; render/export an inspection artifact; use CAP-governed local capture or playback; use CAP-governed OCR or vision-model review; ask the user for a screenshot or frame only as the final fallback
- capability boundary [source: CAP policy]: screenshot capture, playback/frame sampling, OCR/readability, and vision-model review require Capability Access Packet authorization before use
- actionable visual finding shape [source: Quality output contract]: artifact, slide/frame/timecode, region, issue type, severity, evidence source, suggested fix owner, suggested correction, and recheck condition
- pass condition [source: verification/review]: visible output has no material occlusion, overlap, unreadable text, missing expected content, or slide/render/video mismatch before delivery
"""


def render_team_cv_inspection_section(quality_loop: dict[str, Any] | None) -> str:
    if not artifact_harness_cv_requested(quality_loop):
        return ""
    return """
## Visual Inspect-And-Correct Loop

- detected from mission: visual artifact production or visual Quality request
- recommended iterations: 2-3 bounded passes, stopping earlier when no material issue remains
- quality reviewer / visual inspector: assign when the Team Operating Packet needs an explicit review role
- activation ladder task procedure: first use existing rendered/exported visual files; if absent, render/export inspectable images or frames; if local GUI state is needed, request CAP-governed screenshot capture, playback, frame sampling, Computer Use, or app playback; if available, request CAP-governed OCR/readability or vision-model review; ask the user for a screenshot or frame only as the final fallback
- inspect -> finding -> fix -> recheck loop: produce first output; inspect visible evidence; record a structured finding; apply a focused correction by the fix owner; re-inspect the same evidence condition before delivery
- structured finding shape: artifact, slide/frame/timecode, region, issue type, severity, evidence source, suggested fix owner, suggested correction, and recheck condition
- no visual evidence rule: if no screenshot, render, frame, or playback evidence is inspected, visual quality remains limited and only non-visual checks can be considered complete
- capability source: Capability Access Packet must authorize render/export evidence, screenshot capture, playback/frame sampling, OCR/readability, vision-model review, and Computer Use/app playback only when needed
- boundary: this loop attaches to production and does not replace Artifact Harness acceptance or CAP authorization
"""


def render_cap_cv_inspection_section(quality_loop: dict[str, Any] | None) -> str:
    if not artifact_harness_cv_requested(quality_loop):
        return ""
    return """
## CV Inspection Capability Request

- request status: requested by Roster visual Quality loop
- intended use: inspect rendered images, screenshots, rendered frames, or video frames for visible defects before artifact delivery
- activation ladder authorization: prefer existing visual evidence without extra access; request render/export evidence, local capture/playback, OCR/readability, vision-model review, Computer Use, or app playback only when the previous ladder step cannot supply enough visual evidence
- capability requests:
  - render_export_visual_evidence: render or export the artifact into an inspectable image or frame when safe and local
  - screenshot_capture: capture still output for review
  - playback_or_frame_sampling: inspect video playback or selected frames when video is involved
  - computer_use_or_app_playback: use local GUI/app playback only when the artifact state cannot be inspected from files
  - ocr_text_readability: check whether visible text can be read at delivery scale
  - vision_model_review: review screenshot, frame, or image for occlusion, overlap, contrast/readability, missing expected content, and slide/render/video mismatch
- user evidence fallback: ask the user for a screenshot or frame only after local evidence acquisition is unavailable
- approval gate: user or local policy approval before exposing external services, Computer Use, playback, screenshot capture, OCR, or vision-model review tools
- authorization boundary: CAP authorizes tools and gates only; it does not accept the artifact, own Quality, or make runtime adapters governance owners
"""


def render_runtime_cv_inspection_section(quality_loop: dict[str, Any] | None) -> str:
    if not artifact_harness_cv_requested(quality_loop):
        return ""
    return """
## CV Inspection Runtime Trace

- CAP-derived capability request: CV inspection / agent vision review
- visual inspection runtime steps: render/export evidence, screenshot capture, playback/frame sampling, OCR/readability, vision-model review, and Computer Use/app playback
- expose visual inspection steps to runtime only if CAP explicitly authorizes the needed render/export, screenshot, playback/frame sampling, OCR/readability, vision-model review, or Computer Use/app playback tools
- runtime task graph source: Team Operating Packet visual inspect-and-correct loop
- runtime boundary: this mapping may wire authorized capabilities for execution, but it does not own authorization, verification, artifact acceptance, or governance
"""


def render_artifact_harness_spec_packet(mission: str, target: Path, expected_artifact: str, packet_paths: dict[str, str], quality_loop: dict[str, Any] | None = None) -> str:
    cv_section = render_spec_cv_inspection_section(quality_loop)
    return f"""# Artifact Harness SPEC

## Metadata

- owner: Artifact Harness
- status: draft
- target_mission: {mission}
- generated_by: system_hub artifact-harness
- expected_downstream_packet: {packet_paths['hr_staffing_packet']}
- autofill_source: user mission; --path; --artifact when provided

## Field Source Map

- user mission: user phrase
- expected artifact: --artifact or inferred from user phrase
- artifact location: --artifact or open question
- artifact consumer: user phrase or open question
- rules: user phrase or open question
- acceptance checks: user phrase or open question
- boundaries: user phrase, repo policy, or open question
- handoff targets: fixed Artifact Harness workflow

## Mission

- user mission [source: user phrase]: {mission}
- expected artifact [source: --artifact or inference]: {expected_artifact or 'open question'}
- artifact location [source: --artifact or open question]: {expected_artifact or 'open question'}
- artifact consumer [source: user phrase or open question]: open question
- why a harness is needed [source: workflow default]: artifact task needs explicit rules, acceptance, and boundaries before staffing or runtime mapping

## Artifact Contract

- artifact type [source: user phrase or inference]: open question
- required sections or fields [source: user phrase or open question]: open question
- required inputs [source: user phrase or repo evidence]: open question
- allowed source material [source: user phrase, repo evidence, or approval question]: open question
- required output format [source: user phrase or artifact type]: open question
- required evidence [source: acceptance needs]: open question

## Rules

- invariant rules [source: user phrase or repo policy]: open question
- sequencing rules [source: workflow default]: SPEC before staffing; staffing before Team Operating Packet; CAP before runtime mapping
- naming or path rules [source: generated packet layout]: {packet_paths['run_dir']}
- source-use rules [source: user phrase or approval question]: open question
- review rules [source: workflow default]: verify against this SPEC before acceptance

## Acceptance Checks

- check:
  - method [source: user phrase or verification owner]: open question
  - owner [source: verification/review]: verification/review
  - pass condition [source: user phrase or open question]: open question
  - failure action [source: workflow default]: revise packet or artifact before promotion
{cv_section}

## Boundaries

- in scope [source: user phrase]: {mission}
- out of scope [source: user phrase or open question]: open question
- must not change [source: repo policy]: HR staffing boundary; Team Architect collaboration boundary; CAP authorization boundary; runtime execution-only boundary
- user approval required for [source: approval gate]: widening artifact scope, tool access, or runtime authority
- deferred [source: open questions]: unresolved fields above

## Handoff

- staffing target [source: workflow default]: {packet_paths['hr_staffing_packet']}
- Team Architect target [source: workflow default]: {packet_paths['team_operating_packet']}
- capability access expected [source: workflow default]: yes if skills, plugins, tools, or runtime gates are needed
- runtime adapter expected [source: user phrase or open question]: open question
- verification or review target [source: workflow default]: verification/review

## Must Not Do

- choose or redesign staffing
- authorize skills, plugins, or tools
- choose runtime execution mechanics
- change memory-engine level or promotion state
- claim full automation without filled-run or executable evidence

## Open Questions

- Fill artifact type, required fields, allowed sources, and pass conditions before execution.
"""


def render_hr_staffing_packet_scaffold(mission: str, packet_paths: dict[str, str]) -> str:
    return f"""# HR Staffing Packet

## Metadata

- owner: HR
- status: draft
- target_mission: {mission}
- generated_by: system_hub artifact-harness
- source_artifact_harness_spec: {packet_paths['artifact_harness_spec']}
- expected_team_architect_packet: {packet_paths['team_operating_packet']}

## Fill Notes

- Fill this packet from the user mission, Artifact Harness SPEC boundaries, and local role surfaces.
- Keep this file agent-readable Markdown in the same workspace folder.
- This packet owns staffing only. It does not authorize capabilities, choose a runtime adapter, or accept the final artifact.

## Staffing Objective

- staffing request:
- why staffing is needed:
- expected team shape:
- Team Architect handoff required: yes/no

## Role Reuse And Fit

- reused roles:
- adapted roles:
- new roles required:
- unresolved role gaps:

## Role Boundaries

- role:
  - mission:
  - owns:
  - must_not_do:

## Staffing Decision

- reuse/adapt/create rationale:
- staffing risks:
- user approval required for:

## Team Architect Handoff

- handoff target: {packet_paths['team_operating_packet']}
- handoff package: mission, Artifact Harness SPEC, role fit, role gaps
- collaboration constraints from staffing:
- open questions for Team Architect:

## Must Not Do

- authorize skills, plugins, or tools
- choose runtime execution mechanics
- own artifact acceptance or verification
- rewrite Artifact Harness SPEC rules, contract, acceptance, or boundaries
- silently widen role authority beyond staffing needs

## Open Questions

- Fill after HR staffing review of local role surfaces.
"""


def render_team_operating_packet_scaffold(mission: str, packet_paths: dict[str, str], quality_loop: dict[str, Any] | None = None) -> str:
    cv_section = render_team_cv_inspection_section(quality_loop)
    return f"""# Team Operating Packet

## Metadata

- owner: Team Architect
- status: draft
- target_mission: {mission}
- generated_by: system_hub artifact-harness
- source_artifact_harness_spec: {packet_paths['artifact_harness_spec']}
- source_hr_staffing_packet: {packet_paths['hr_staffing_packet']}

## Fill Notes

- Fill this template from the Artifact Harness SPEC, HR staffing packet, and coordination baseline.
- Keep this file agent-readable Markdown in the same workspace folder.
- This packet owns collaboration structure, not staffing or capability authorization.
- Generate or link a Capability Access Packet when skills, plugins, tools, or runtime approval gates are needed.

## Team Shape

- team name:
- task shape:
- chosen collaboration pattern:
- why this pattern fits:

## Roles

- role:
  - mission:
  - owns:
  - must_produce:
  - must_not_do:

## Inputs From Staffing

- reused roles:
- adapted roles:
- new roles:
- unresolved role gaps:

## Shared Artifacts

- artifact:
  - owner:
  - purpose:
  - handoff target:
  - promotion rule:
{cv_section}

## Capability Access

- source Artifact Harness SPEC: {packet_paths['artifact_harness_spec']}
- capability access packet: {packet_paths['capability_access_packet']}
- required: yes/no
- reason required:
- authorized capability summary:
- approval gate summary:
- access boundaries:

## Interaction Protocol

1. publish:
2. request:
3. revise:
4. promote:
5. closeout:

## Escalation And Convergence

- escalation triggers:
- dominant issue owner rule:
- stop conditions:
- fallback if the pattern stalls:

## Authority Envelope

- what this team may decide:
- what requires user approval:
- what must not be changed silently:

## Invocation Guidance

- how to call the team:
- when to use this team:
- when not to use this team:

## Execution Runtime Mapping

- runtime adapter:
- runtime mode:
- why this mode fits:
- task graph source:
- mapping artifact: {packet_paths['runtime_mapping']}
- source capability access packet: {packet_paths['capability_access_packet']}
- approval gate locations:
- expected runtime byproducts:

## Open Questions

- Fill after HR staffing packet is available.
"""


def render_capability_access_packet_scaffold(mission: str, packet_paths: dict[str, str], quality_loop: dict[str, Any] | None = None) -> str:
    cv_section = render_cap_cv_inspection_section(quality_loop)
    return f"""# Capability Access Packet

## Metadata

- owner: Team Architect
- status: draft
- target_mission: {mission}
- generated_by: system_hub artifact-harness
- source_artifact_harness_spec: {packet_paths['artifact_harness_spec']}
- source_team_operating_packet: {packet_paths['team_operating_packet']}

## Fill Notes

- Fill this template from the Artifact Harness SPEC, Team Operating Packet, and available local skills, plugins, and tools.
- Keep this file agent-readable Markdown in the same workspace folder.
- This packet authorizes capabilities and gates only. It does not choose roles, collaboration patterns, artifact acceptance, or runtime ownership.

## Purpose

- why capability access is needed:
- expected artifact or runtime outcome from source packets:
- capability risk level:

## Authorized Capabilities

- skill:
  - allowed use:
  - scope:
  - output expected:
  - approval gate:
- plugin:
  - allowed use:
  - scope:
  - output expected:
  - approval gate:
- tool:
  - allowed use:
  - scope:
  - output expected:
  - approval gate:
{cv_section}

## Runtime Allowlist

- exposed skills:
- exposed plugins:
- exposed tools:
- withheld capabilities:
- allowlist source:

## Denied Or Deferred Capabilities

- capability:
  - reason:
  - fallback:

## Access Boundaries

- allowed files or folders:
- allowed external services:
- allowed network use:
- allowed writes:
- forbidden writes:
- secrets or credentials rule:
- runtime byproducts rule:

## Approval Gates

- gate:
  - trigger:
  - approval owner:
  - allowed continuation:
  - rejected fallback:

## Runtime Exposure Constraints

- runtime adapter from Team Operating Packet:
- runtime mapping artifact from Team Architect: {packet_paths['runtime_mapping']}
- capabilities to expose:
- capabilities to withhold:
- approval gates to enforce:
- evidence to return:

This section constrains runtime exposure only. It does not choose the runtime adapter and does not create the runtime task graph.

## Evidence For Verification

- access evidence:
- capability exposure evidence:
- approval gate evidence:
- closeout evidence to return:

This section supplies evidence to verification/review. It does not decide artifact acceptance.

## Must Not Do

- choose or redesign staffing
- replace the Team Architect operating packet
- change the Artifact Harness SPEC rules, contract, acceptance, or boundaries
- own verification or artifact acceptance
- make the runtime adapter a governance owner
- claim complete automation without executable evidence

## Open Questions

- Fill after Team Operating Packet identifies capability needs.
"""


def render_runtime_mapping_scaffold(mission: str, packet_paths: dict[str, str], quality_loop: dict[str, Any] | None = None) -> str:
    cv_section = render_runtime_cv_inspection_section(quality_loop)
    return f"""# open-multi-agent runTasks Mapping

## Metadata

- source operating packet: {packet_paths['team_operating_packet']}
- source capability access packet: {packet_paths['capability_access_packet']}
- status: draft
- runtime adapter: open-multi-agent
- runtime mode: runTasks
- generated_by: system_hub artifact-harness

## Fill Notes

- Fill this mapping from the Team Operating Packet, Capability Access Packet, and runtime adapter policy.
- Keep this file agent-readable Markdown in the same workspace folder.
- This mapping is for optional runtime execution; it does not make the runtime adapter a governance owner.
- No persistent server is required by this template.

## Adapter Decision

- why `runTasks()` is appropriate:
- why `runTeam()` is not the primary mode:
- expected runtime risk:
- approval gates required: yes/no
- execution surface:
  - TypeScript API required when approval gates are required
  - CLI allowed only when no approval gates are required and no runtime object wiring is needed

## Capability Access Trace

- CAP source: {packet_paths['capability_access_packet']}
- authorized skills:
- authorized plugins:
- authorized tools:
- denied or withheld capabilities:
- CAP approval gates:
- CAP access boundaries:
- runtime exposure rule:
  - expose only capabilities listed above
  - withhold any capability not authorized by CAP
{cv_section}

## TeamConfig

```json
{{
  "name": "",
  "agents": [
    {{
      "name": "",
      "provider": "",
      "model": "",
      "systemPrompt": "",
      "tools": []
    }}
  ],
  "sharedMemory": true,
  "maxConcurrency": 1
}}
```

## Tasks

```json
[
  {{
    "title": "",
    "description": "",
    "assignee": "",
    "dependsOn": [],
    "memoryScope": "dependencies"
  }}
]
```

## Artifact Mapping

- task:
  - expected artifact:
  - artifact owner:
  - acceptance check:
  - promotion rule:

## Approval Gates

- after task:
  - CAP gate source:
  - gate reason:
  - enforcement surface:
  - approved continuation:
  - rejected fallback:

If any approval gate is required, this mapping must be executed through the TypeScript API with an enforceable approval callback. The `oma` CLI path is not allowed for gated execution because JSON configuration cannot carry function callbacks such as `onApproval`.

## Convergence

- stop conditions:
- fallback behavior:
- final synthesis owner:

## Runtime Notes

- preferred API surface:
- same workspace folder:
- CLI allowed:
  - yes only if no approval gates are required
  - no when CAP approval gates, runtime object wiring, or human approval are required
- expected local byproducts:
- byproducts to keep local:

## Open Questions

- Fill only if runtime execution is actually needed for mission: {mission}
"""


def render_artifact_harness_summary(entry: dict[str, Any]) -> str:
    lines = [
        "# Artifact Harness Packet Chain",
        "",
        f"- Packet ID: `{entry['id']}`",
        f"- Mission: {entry['mission']}",
        f"- Target path: `{entry['target_path']}`",
        f"- Generated at: `{entry['generated_at']}`",
        f"- Run directory: `{entry['run_dir']}`",
        f"- Lifecycle status: `{entry.get('status', 'draft')}`",
        f"- Lifecycle metadata: `{entry.get('status_path', '')}`",
        "",
        "## Packets",
        "",
    ]
    for key in ("artifact_harness_spec", "hr_staffing_packet", "team_operating_packet", "capability_access_packet", "runtime_mapping", "manifest"):
        lines.append(f"- {key}: `{entry['packets'][key]}`")
    lines.extend(
        [
            "",
            "## Next Steps",
            "",
            "- Complete the Artifact Harness SPEC fields that remain open questions.",
            "- Fill the HR staffing packet before Team Architect finalizes the operating packet.",
            "- Have Team Architect complete the Team Operating Packet and CAP before runtime mapping.",
            "- Treat runtime mapping as optional execution wiring, not governance ownership.",
            "",
        ]
    )
    return "\n".join(lines)


def existing_artifact_harness_run_conflicts(run_dir: Path, absolute_paths: dict[str, Path]) -> list[str]:
    conflicts: list[str] = []
    if run_dir.exists():
        conflicts.append(f"run directory: {run_dir}")
    for key in (
        "artifact_harness_spec",
        "hr_staffing_packet",
        "team_operating_packet",
        "capability_access_packet",
        "runtime_mapping",
        "manifest",
        "status",
        "schema_metadata",
    ):
        path = absolute_paths[key]
        if path.exists():
            conflicts.append(f"{key}: {path}")
    return conflicts


def artifact_harness_refusal_payload(
    packet_id: str,
    mission: str,
    target: Path,
    run_dir: Path,
    packet_paths: dict[str, Path],
    registry_path: Path,
    reason: str,
) -> dict[str, Any]:
    return {
        "id": packet_id,
        "mission": mission,
        "target_path": str(target),
        "packet_root": str(run_dir.parent),
        "run_dir": str(run_dir),
        "packets": {key: str(packet_paths[key]) for key in ("artifact_harness_spec", "hr_staffing_packet", "team_operating_packet", "capability_access_packet", "runtime_mapping", "manifest")},
        "status_path": str(packet_paths["status"]) if "status" in packet_paths else None,
        "registry_path": str(registry_path),
        "created": False,
        "refused": True,
        "reason": reason,
    }


def artifact_harness_lifecycle_payload(
    packet_id: str,
    status: str,
    updated_at: str,
    note: str,
    updated_by: str,
) -> dict[str, Any]:
    event = {
        "status": status,
        "note": note,
        "updated_at": updated_at,
        "updated_by": updated_by,
    }
    return {
        "schema_version": 1,
        "id": packet_id,
        "status": status,
        "note": note,
        "updated_at": updated_at,
        "updated_by": updated_by,
        "governance_boundary": "Lifecycle status is continuity metadata only; it does not grant approval, capability access, runtime execution authority, or artifact acceptance.",
        "allowed_statuses": list(ARTIFACT_HARNESS_STATUSES),
        "history": [event],
    }


def artifact_harness_run_paths(config: HubConfig, target: Path, packet_id: str) -> tuple[Path, Path, dict[str, Path]]:
    packet_root = artifact_harness_packet_root(config, target)
    run_dir = packet_root / packet_id
    registry_path = artifact_harness_registry_path_for_target(config, target)
    packet_paths = {
        "artifact_harness_spec": run_dir / "artifact_harness_spec.md",
        "hr_staffing_packet": run_dir / "hr_staffing_packet.md",
        "team_operating_packet": run_dir / "team_operating_packet.md",
        "capability_access_packet": run_dir / "capability_access_packet.md",
        "runtime_mapping": run_dir / "open_multi_agent_runtasks_mapping.md",
        "manifest": run_dir / "packet_manifest.json",
        "status": run_dir / "packet_status.json",
        "replay_evidence": run_dir / "artifact_replay_evidence.json",
        "provenance_ledger": run_dir / "packet_provenance_ledger.json",
        "runtime_readiness_report": run_dir / "runtime_readiness_report.json",
        "approval_evidence": run_dir / ARTIFACT_HARNESS_APPROVAL_EVIDENCE_FILENAME,
        "runtime_invocation_report": run_dir / ARTIFACT_HARNESS_RUNTIME_INVOCATION_REPORT_FILENAME,
        "repair_plan": run_dir / ARTIFACT_HARNESS_REPAIR_PLAN_FILENAME,
        "schema_metadata": run_dir / ARTIFACT_HARNESS_SCHEMA_METADATA_FILENAME,
    }
    return run_dir, registry_path, packet_paths


def artifact_harness_lifecycle_refusal_payload(
    action: str,
    packet_id: str | None,
    target: Path | None,
    run_dir: Path | None,
    status_path: Path | None,
    registry_path: Path | None,
    reason: str,
    offending_packet_key: str | None = None,
    attempted_path: Path | str | None = None,
) -> dict[str, Any]:
    return {
        "action": action,
        "id": packet_id,
        "target_path": str(target) if target is not None else None,
        "run_dir": str(run_dir) if run_dir is not None else None,
        "status_path": str(status_path) if status_path is not None else None,
        "evidence_path": str(run_dir / "artifact_replay_evidence.json") if action == "replay" and run_dir is not None else None,
        "registry_path": str(registry_path) if registry_path is not None else None,
        "manifest": None,
        "status": None,
        "packets": {},
        "provenance_ledger_path": str(run_dir / "packet_provenance_ledger.json") if action == "provenance" and run_dir is not None else None,
        "runtime_readiness_report_path": str(run_dir / "runtime_readiness_report.json") if action in {"runtime-check", "runtime-invoke"} and run_dir is not None else None,
        "approval_evidence_path": str(run_dir / ARTIFACT_HARNESS_APPROVAL_EVIDENCE_FILENAME) if action in {"approval", "runtime-invoke"} and run_dir is not None else None,
        "runtime_invocation_report_path": str(run_dir / ARTIFACT_HARNESS_RUNTIME_INVOCATION_REPORT_FILENAME) if action == "runtime-invoke" and run_dir is not None else None,
        "repair_plan_path": str(run_dir / ARTIFACT_HARNESS_REPAIR_PLAN_FILENAME) if action == "repair-plan" and run_dir is not None else None,
        "schema_metadata_path": str(run_dir / ARTIFACT_HARNESS_SCHEMA_METADATA_FILENAME) if action in {"schema-check", "migrate"} and run_dir is not None else None,
        "current_schema_version": None if action in {"schema-check", "migrate"} else None,
        "supported_schema_version": ARTIFACT_HARNESS_SCHEMA_VERSION if action in {"schema-check", "migrate"} else None,
        "compatible": False if action in {"schema-check", "migrate"} else None,
        "migration_required": False if action in {"schema-check", "migrate"} else None,
        "checked_files": [] if action in {"schema-check", "migrate"} else None,
        "missing_files": [] if action in {"schema-check", "migrate"} else None,
        "missing_required_fields": [] if action in {"schema-check", "migrate"} else None,
        "warnings": [] if action in {"schema-check", "migrate"} else None,
        "source_categories": list(ARTIFACT_HARNESS_PROVENANCE_CATEGORIES) if action == "provenance" else [],
        "packet_chain_provenance": {},
        "runtime_invocation_ready": False if action in {"runtime-check", "runtime-invoke"} else None,
        "execution_authorized": False if action in {"runtime-check", "runtime-invoke"} else None,
        "approval_gates_required": False if action in {"runtime-check", "runtime-invoke"} else None,
        "required_execution_surface": None,
        "blocking_findings": [],
        "checks": {},
        "offending_packet_key": offending_packet_key,
        "attempted_path": str(attempted_path) if attempted_path is not None else None,
        "refused": True,
        "reason": reason,
    }


def artifact_harness_lifecycle_command(
    config: HubConfig,
    action: str,
    target: Path,
    packet_id: str,
    *,
    status: str | None = None,
    note: str | None = None,
    emit_json: bool = False,
) -> str:
    command_parts = [
        str(config.scripts_dir / "brain.sh"),
        "artifact-harness",
        action,
        "--path",
        str(target),
        "--id",
        packet_id,
    ]
    if status:
        command_parts.extend(["--status", status])
    if note:
        command_parts.extend(["--note", note])
    if emit_json:
        command_parts.append("--json")
    return " ".join(shlex.quote(part) for part in command_parts)


def artifact_harness_approval_command(
    config: HubConfig,
    target: Path,
    packet_id: str,
    gate_id: str = ARTIFACT_HARNESS_RUNTIME_APPROVAL_GATE_ID,
    decision: str = "approved",
    approver: str = "<approver>",
    *,
    note: str | None = None,
    emit_json: bool = False,
) -> str:
    command_parts = [
        str(config.scripts_dir / "brain.sh"),
        "artifact-harness",
        "approval",
        "--path",
        str(target),
        "--id",
        packet_id,
        "--gate",
        gate_id,
        "--decision",
        decision,
        "--approver",
        approver,
    ]
    if note:
        command_parts.extend(["--note", note])
    if emit_json:
        command_parts.append("--json")
    return " ".join(shlex.quote(part) for part in command_parts)


def artifact_harness_runtime_invoke_command(
    config: HubConfig,
    target: Path,
    packet_id: str,
    *,
    adapter: str = "open-multi-agent",
    surface: str = "typescript-runTasks",
    dry_run: bool = True,
    emit_json: bool = False,
) -> str:
    command_parts = [
        str(config.scripts_dir / "brain.sh"),
        "artifact-harness",
        "runtime-invoke",
        "--path",
        str(target),
        "--id",
        packet_id,
        "--adapter",
        adapter,
        "--surface",
        surface,
    ]
    if dry_run:
        command_parts.append("--dry-run")
    if emit_json:
        command_parts.append("--json")
    return " ".join(shlex.quote(part) for part in command_parts)


def artifact_harness_repair_plan_command(
    config: HubConfig,
    target: Path,
    packet_id: str,
    *,
    emit_json: bool = False,
) -> str:
    command_parts = [
        str(config.scripts_dir / "brain.sh"),
        "artifact-harness",
        "repair-plan",
        "--path",
        str(target),
        "--id",
        packet_id,
    ]
    if emit_json:
        command_parts.append("--json")
    return " ".join(shlex.quote(part) for part in command_parts)


def artifact_harness_next_step(status: str) -> tuple[str, str]:
    if status == "draft":
        return (
            "artifact_harness_spec",
            "Inspect the Artifact Harness SPEC first, then fill unresolved packet fields before marking the run filled.",
        )
    if status == "filled":
        return (
            "team_operating_packet",
            "Review the filled packets against their boundaries; mark reviewed or blocked explicitly.",
        )
    if status == "reviewed":
        return (
            "capability_access_packet",
            "Seek explicit approval if approval is required; status alone is not approval.",
        )
    if status == "approved":
        return (
            "runtime_mapping",
            "Proceed only through the approved CAP and runtime mapping; status alone does not execute anything.",
        )
    if status == "blocked":
        return (
            "status",
            "Resolve the recorded blocker note before changing lifecycle status.",
        )
    if status == "executed":
        return (
            "runtime_mapping",
            "Inspect runtime evidence and verify the artifact against the upstream packets.",
        )
    if status == "verified":
        return (
            "manifest",
            "Keep as current continuity evidence or mark archived when it is no longer active.",
        )
    if status == "superseded":
        return (
            "manifest",
            "Do not treat this run as current; inspect the replacement run or registry note.",
        )
    if status == "archived":
        return (
            "manifest",
            "Use this run as historical evidence only.",
        )
    return (
        "status",
        "Inspect lifecycle metadata and packet manifest before continuing.",
    )


def load_artifact_harness_lifecycle_state(
    config: HubConfig,
    action: str,
    target_arg: str,
    packet_id: str | None,
) -> tuple[int, dict[str, Any], list[str], dict[str, Any] | None, dict[str, Any] | None]:
    if not packet_id or not packet_id.strip():
        payload = artifact_harness_lifecycle_refusal_payload(action, None, None, None, None, None, "missing_packet_id")
        return 1, payload, ["Artifact Harness lifecycle commands require `--id <packet-id>`."], None, None
    target = Path(target_arg).expanduser().resolve()
    if not target.exists():
        payload = artifact_harness_lifecycle_refusal_payload(action, packet_id, target, None, None, None, "missing_target")
        return 1, payload, [f"Target path does not exist: {target}"], None, None
    if not target.is_dir():
        payload = artifact_harness_lifecycle_refusal_payload(action, packet_id, target, None, None, None, "target_not_directory")
        return 1, payload, [f"Target path must be a directory: {target}"], None, None

    run_dir, registry_path, packet_paths = artifact_harness_run_paths(config, target, packet_id.strip())
    try:
        ensure_targets_under_root(target, {"run_dir": run_dir, "registry_path": registry_path, **packet_paths})
    except HubRuntimeError as exc:
        payload = artifact_harness_lifecycle_refusal_payload(
            action,
            packet_id.strip(),
            target,
            run_dir,
            packet_paths["status"],
            registry_path,
            "packet_root_outside_target_workspace",
        )
        return 1, payload, [str(exc)], None, None
    if not run_dir.exists():
        payload = artifact_harness_lifecycle_refusal_payload(action, packet_id.strip(), target, run_dir, packet_paths["status"], registry_path, "missing_packet_run")
        return 1, payload, [f"Artifact Harness packet run does not exist: {run_dir}"], None, None
    if not packet_paths["manifest"].exists():
        payload = artifact_harness_lifecycle_refusal_payload(action, packet_id.strip(), target, run_dir, packet_paths["status"], registry_path, "missing_manifest")
        return 1, payload, [f"Artifact Harness packet manifest does not exist: {packet_paths['manifest']}"], None, None
    if not packet_paths["status"].exists():
        payload = artifact_harness_lifecycle_refusal_payload(action, packet_id.strip(), target, run_dir, packet_paths["status"], registry_path, "missing_packet_status")
        return 1, payload, [f"Artifact Harness lifecycle metadata does not exist: {packet_paths['status']}"], None, None

    try:
        manifest = load_json_file_strict(packet_paths["manifest"], {}, "artifact harness manifest")
        status_payload = load_json_file_strict(packet_paths["status"], {}, "artifact harness lifecycle status")
        registry = load_artifact_harness_registry(config, registry_path)
    except HubRuntimeError as exc:
        payload = artifact_harness_lifecycle_refusal_payload(action, packet_id.strip(), target, run_dir, packet_paths["status"], registry_path, "invalid_lifecycle_json")
        return 1, payload, [str(exc)], None, None

    status_value = status_payload.get("status")
    if status_value not in ARTIFACT_HARNESS_STATUSES:
        payload = artifact_harness_lifecycle_refusal_payload(action, packet_id.strip(), target, run_dir, packet_paths["status"], registry_path, "invalid_status")
        return 1, payload, [f"Invalid Artifact Harness lifecycle status in {packet_paths['status']}: {status_value}"], None, None

    packets: dict[str, str] = {}
    manifest_packets = manifest.get("packets", {})
    if not isinstance(manifest_packets, dict):
        manifest_packets = {}
    for key, rel in manifest_packets.items():
        if not isinstance(key, str) or not isinstance(rel, str):
            continue
        raw_path = Path(rel).expanduser()
        resolved_path = raw_path.resolve() if raw_path.is_absolute() else (target / raw_path).resolve()
        try:
            ensure_targets_under_root(target, {f"manifest_packet:{key}": resolved_path})
        except HubRuntimeError as exc:
            payload = artifact_harness_lifecycle_refusal_payload(
                action,
                packet_id.strip(),
                target,
                run_dir,
                packet_paths["status"],
                registry_path,
                "manifest_packet_path_outside_target_workspace",
                key,
                resolved_path,
            )
            payload["manifest"] = str(packet_paths["manifest"])
            return 1, payload, [str(exc)], None, None
        packets[key] = str(resolved_path)
    packets["manifest"] = str(packet_paths["manifest"])
    state = {
        "action": action,
        "id": packet_id.strip(),
        "target_path": str(target),
        "packet_root": str(run_dir.parent),
        "run_dir": str(run_dir),
        "status_path": str(packet_paths["status"]),
        "schema_metadata_path": str(packet_paths["schema_metadata"]),
        "manifest": str(packet_paths["manifest"]),
        "registry_path": str(registry_path),
        "packets": packets,
        "status": status_value,
        "status_note": status_payload.get("note"),
        "updated_at": status_payload.get("updated_at"),
        "updated_by": status_payload.get("updated_by"),
        "history": status_payload.get("history", []),
        "allowed_statuses": list(ARTIFACT_HARNESS_STATUSES),
        "refused": False,
        "reason": None,
    }
    registry_entry = next((entry for entry in registry.get("entries", []) if isinstance(entry, dict) and entry.get("id") == packet_id.strip()), None)
    if isinstance(registry_entry, dict):
        state["registry_status"] = registry_entry.get("status")
        state["registry_status_updated_at"] = registry_entry.get("status_updated_at")
    return 0, state, [], manifest, status_payload


def render_artifact_harness_lifecycle_markdown(payload: dict[str, Any]) -> str:
    if payload.get("refused"):
        return f"# Artifact Harness Lifecycle\n\n- Refused: `true`\n- Reason: `{payload.get('reason')}`\n"
    lines = [
        "# Artifact Harness Lifecycle",
        "",
        f"- Action: `{payload['action']}`",
        f"- Packet ID: `{payload['id']}`",
        f"- Status: `{payload['status']}`",
        f"- Updated at: `{payload.get('updated_at')}`",
        f"- Run directory: `{payload['run_dir']}`",
        f"- Lifecycle metadata: `{payload['status_path']}`",
    ]
    if payload.get("next_inspection"):
        lines.extend(
            [
                f"- Next inspection: `{payload['next_inspection']}`",
                f"- Next action: {payload['next_action']}",
            ]
        )
    lines.extend(["", "## Commands", ""])
    for label, command in payload.get("commands", {}).items():
        lines.append(f"- {label}: `{command}`")
    lines.append("")
    return "\n".join(lines)


def do_artifact_harness_lifecycle(
    config: HubConfig,
    action: str,
    target_arg: str,
    packet_id: str | None,
    new_status: str | None,
    note: str,
    emit_json: bool = False,
) -> int:
    if action not in {"status", "resume", "mark"}:
        payload = artifact_harness_lifecycle_refusal_payload(action, packet_id, None, None, None, None, "unknown_lifecycle_action")
        if emit_json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print(f"Unknown Artifact Harness lifecycle action: {action}", file=sys.stderr)
        return 1
    code, payload, errors, _manifest, status_payload = load_artifact_harness_lifecycle_state(config, action, target_arg, packet_id)
    if code != 0:
        for line in errors:
            print(line, file=sys.stderr)
        if emit_json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        return code

    target = Path(payload["target_path"])
    packet_id = payload["id"]
    status_path = Path(payload["status_path"])
    registry_path = Path(payload["registry_path"])

    if action == "mark":
        if not new_status or new_status.strip() not in ARTIFACT_HARNESS_STATUSES:
            refused = artifact_harness_lifecycle_refusal_payload(action, packet_id, target, Path(payload["run_dir"]), status_path, registry_path, "invalid_status")
            errors = [
                "Artifact Harness lifecycle status must be one of: "
                + ", ".join(ARTIFACT_HARNESS_STATUSES)
            ]
            for line in errors:
                print(line, file=sys.stderr)
            if emit_json:
                print(json.dumps(refused, ensure_ascii=False, indent=2))
            return 1
        updated_at = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
        status_payload = dict(status_payload or {})
        history = status_payload.get("history", [])
        if not isinstance(history, list):
            history = []
        event = {
            "status": new_status.strip(),
            "note": note.strip(),
            "updated_at": updated_at,
            "updated_by": "system_hub artifact-harness mark",
        }
        history.append(event)
        status_payload.update(
            {
                "schema_version": 1,
                "id": packet_id,
                "status": new_status.strip(),
                "note": note.strip(),
                "updated_at": updated_at,
                "updated_by": "system_hub artifact-harness mark",
                "governance_boundary": "Lifecycle status is continuity metadata only; it does not grant approval, capability access, runtime execution authority, or artifact acceptance.",
                "allowed_statuses": list(ARTIFACT_HARNESS_STATUSES),
                "history": history[-50:],
            }
        )
        dump_json(status_path, status_payload)

        registry = load_artifact_harness_registry(config, registry_path)
        entries = []
        found = False
        for entry in registry.get("entries", []):
            if isinstance(entry, dict) and entry.get("id") == packet_id:
                entry = dict(entry)
                entry["status"] = new_status.strip()
                entry["status_note"] = note.strip()
                entry["status_updated_at"] = updated_at
                entry["status_path"] = relative_path_from(target, status_path)
                found = True
            entries.append(entry)
        if not found:
            entries.append(
                {
                    "id": packet_id,
                    "target_path": str(target),
                    "run_dir": relative_path_from(target, Path(payload["run_dir"])),
                    "status": new_status.strip(),
                    "status_note": note.strip(),
                    "status_updated_at": updated_at,
                    "status_path": relative_path_from(target, status_path),
                }
            )
        registry["generated_at"] = updated_at
        registry["entries"] = entries[-50:]
        save_artifact_harness_registry(config, registry, registry_path, target)
        payload["status"] = new_status.strip()
        payload["status_note"] = note.strip()
        payload["updated_at"] = updated_at
        payload["updated_by"] = "system_hub artifact-harness mark"
        payload["history"] = status_payload["history"]
        payload["registry_status"] = new_status.strip()
        payload["registry_status_updated_at"] = updated_at

    next_inspection, next_action = artifact_harness_next_step(str(payload["status"]))
    payload["next_inspection"] = next_inspection
    payload["next_action"] = next_action
    payload["commands"] = {
        "status_json": artifact_harness_lifecycle_command(config, "status", target, packet_id, emit_json=True),
        "resume_json": artifact_harness_lifecycle_command(config, "resume", target, packet_id, emit_json=True),
        "schema_check_json": artifact_harness_lifecycle_command(config, "schema-check", target, packet_id, emit_json=True),
        "migrate_json": artifact_harness_lifecycle_command(config, "migrate", target, packet_id, emit_json=True),
        "replay_json": artifact_harness_lifecycle_command(config, "replay", target, packet_id, emit_json=True),
        "provenance_json": artifact_harness_lifecycle_command(config, "provenance", target, packet_id, emit_json=True),
        "runtime_check_json": artifact_harness_lifecycle_command(config, "runtime-check", target, packet_id, emit_json=True),
        "repair_plan_json": artifact_harness_repair_plan_command(config, target, packet_id, emit_json=True),
        "mark_filled_json": artifact_harness_lifecycle_command(config, "mark", target, packet_id, status="filled", note="packet fields filled", emit_json=True),
        "mark_blocked_json": artifact_harness_lifecycle_command(config, "mark", target, packet_id, status="blocked", note="describe blocker", emit_json=True),
    }
    if emit_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(render_artifact_harness_lifecycle_markdown(payload), end="")
    return 0


def artifact_harness_packet_completion_heuristics(path: Path) -> dict[str, Any]:
    result: dict[str, Any] = {
        "exists": path.exists(),
        "path": str(path),
        "kind": path.suffix.lstrip(".") or "unknown",
        "byte_count": 0,
        "line_count": 0,
        "open_question_markers": 0,
        "empty_bullet_fields": 0,
        "placeholder_markers": 0,
        "heuristic_open_items": 0,
        "completion_state": "missing",
    }
    if not path.exists():
        return result
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    lower = text.lower()
    open_question_markers = sum(1 for line in lines if "open question" in line.lower())
    empty_bullet_fields = sum(1 for line in lines if re.match(r"^\s*-\s+[^:\n]+:\s*$", line))
    empty_bullets = sum(1 for line in lines if re.match(r"^\s*-\s*$", line))
    placeholder_markers = sum(
        lower.count(marker)
        for marker in (
            "to be filled",
            "fill only",
            "yes/no",
            "draft/reviewed/approved",
            "open questions",
        )
    )
    heuristic_open_items = open_question_markers + empty_bullet_fields + empty_bullets + placeholder_markers
    result.update(
        {
            "byte_count": len(text.encode("utf-8")),
            "line_count": len(lines),
            "open_question_markers": open_question_markers,
            "empty_bullet_fields": empty_bullet_fields + empty_bullets,
            "placeholder_markers": placeholder_markers,
            "heuristic_open_items": heuristic_open_items,
            "completion_state": "open_items_detected" if heuristic_open_items else "no_obvious_open_items",
        }
    )
    return result


def build_artifact_harness_replay_evidence(
    config: HubConfig,
    target_arg: str,
    packet_id: str | None,
) -> tuple[int, dict[str, Any], list[str]]:
    code, state, errors, manifest, _status_payload = load_artifact_harness_lifecycle_state(config, "replay", target_arg, packet_id)
    if code != 0:
        return code, state, errors
    manifest = manifest or {}

    target = Path(state["target_path"])
    run_dir = Path(state["run_dir"])
    evidence_path = run_dir / "artifact_replay_evidence.json"
    try:
        ensure_targets_under_root(target, {"evidence_path": evidence_path})
    except HubRuntimeError as exc:
        payload = dict(state)
        payload.update({"evidence_path": str(evidence_path), "refused": True, "reason": "evidence_path_outside_target_workspace"})
        return 1, payload, [str(exc)]

    packet_paths = {
        "artifact_harness_spec": Path(state["packets"].get("artifact_harness_spec", run_dir / "artifact_harness_spec.md")),
        "hr_staffing_packet": Path(state["packets"].get("hr_staffing_packet", run_dir / "hr_staffing_packet.md")),
        "team_operating_packet": Path(state["packets"].get("team_operating_packet", run_dir / "team_operating_packet.md")),
        "capability_access_packet": Path(state["packets"].get("capability_access_packet", run_dir / "capability_access_packet.md")),
        "runtime_mapping": Path(state["packets"].get("runtime_mapping", run_dir / "open_multi_agent_runtasks_mapping.md")),
        "manifest": Path(state["manifest"]),
        "status": Path(state["status_path"]),
    }
    packets = {key: artifact_harness_packet_completion_heuristics(path) for key, path in packet_paths.items()}
    summary = {
        "packet_count": len(packets),
        "existing_packet_count": sum(1 for item in packets.values() if item["exists"]),
        "missing_packet_count": sum(1 for item in packets.values() if not item["exists"]),
        "heuristic_open_items_total": sum(int(item.get("heuristic_open_items", 0)) for item in packets.values()),
    }
    generated_at = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    evidence = {
        "schema_version": 1,
        "evidence_type": "artifact_harness_replay_evidence",
        "generated_at": generated_at,
        "id": state["id"],
        "mission": manifest.get("mission"),
        "expected_artifact": manifest.get("expected_artifact"),
        "workflow": manifest.get("workflow", []),
        "target_path": state["target_path"],
        "run_dir": state["run_dir"],
        "manifest": state["manifest"],
        "registry_path": state["registry_path"],
        "status": state["status"],
        "registry_status": state.get("registry_status"),
        "registry_status_updated_at": state.get("registry_status_updated_at"),
        "status_path": state["status_path"],
        "status_note": state.get("status_note"),
        "lifecycle_updated_at": state.get("updated_at"),
        "packets": packets,
        "field_completion_summary": summary,
        "heuristics": {
            "open_question_markers": "line contains `open question` case-insensitively",
            "empty_bullet_fields": "Markdown bullet line ending with an empty colon, plus fully empty bullet lines",
            "placeholder_markers": "simple substring counts for visible scaffold placeholders",
            "completion_state": "heuristic only; it is not artifact acceptance or review approval",
        },
        "commands": {
            "replay_json": artifact_harness_lifecycle_command(config, "replay", target, state["id"], emit_json=True),
            "provenance_json": artifact_harness_lifecycle_command(config, "provenance", target, state["id"], emit_json=True),
            "runtime_check_json": artifact_harness_lifecycle_command(config, "runtime-check", target, state["id"], emit_json=True),
            "status_json": artifact_harness_lifecycle_command(config, "status", target, state["id"], emit_json=True),
            "resume_json": artifact_harness_lifecycle_command(config, "resume", target, state["id"], emit_json=True),
        },
        "governance_boundary": "Replay evidence is observation and continuity only. It does not accept artifacts, approve capabilities, select runtime, replace upstream packets, or execute adapters.",
        "evidence_path": str(evidence_path),
        "refused": False,
        "reason": None,
    }
    dump_json(evidence_path, evidence)
    return 0, evidence, []


def render_artifact_harness_replay_markdown(payload: dict[str, Any]) -> str:
    if payload.get("refused"):
        return f"# Artifact Harness Replay Evidence\n\n- Refused: `true`\n- Reason: `{payload.get('reason')}`\n"
    summary = payload.get("field_completion_summary", {})
    lines = [
        "# Artifact Harness Replay Evidence",
        "",
        f"- Packet ID: `{payload['id']}`",
        f"- Target path: `{payload['target_path']}`",
        f"- Run directory: `{payload['run_dir']}`",
        f"- Status: `{payload['status']}`",
        f"- Evidence path: `{payload['evidence_path']}`",
        f"- Existing packets: `{summary.get('existing_packet_count')}`",
        f"- Heuristic open items: `{summary.get('heuristic_open_items_total')}`",
        "",
        "## Packet Presence",
        "",
    ]
    for key, item in payload.get("packets", {}).items():
        lines.append(f"- {key}: `{'exists' if item.get('exists') else 'missing'}` `{item.get('completion_state')}`")
    lines.append("")
    return "\n".join(lines)


def do_artifact_harness_replay(
    config: HubConfig,
    target_arg: str,
    packet_id: str | None,
    emit_json: bool = False,
) -> int:
    code, payload, errors = build_artifact_harness_replay_evidence(config, target_arg, packet_id)
    for line in errors:
        print(line, file=sys.stderr)
    if emit_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    elif code == 0:
        print(render_artifact_harness_replay_markdown(payload), end="")
    return code


def artifact_harness_provenance_record(
    source_category: str,
    confidence: str,
    *,
    source_path: str | None = None,
    source_field: str | None = None,
    value: Any | None = None,
    note: str = "",
    grounded: bool = False,
) -> dict[str, Any]:
    category = source_category if source_category in ARTIFACT_HARNESS_PROVENANCE_CATEGORIES else "unknown"
    record: dict[str, Any] = {
        "source_category": category,
        "confidence": confidence,
        "grounded": grounded,
        "note": note,
    }
    if source_path is not None:
        record["source_path"] = source_path
    if source_field is not None:
        record["source_field"] = source_field
    if value is not None:
        record["value"] = value
    return record


def collect_artifact_harness_provenance_counts(value: Any) -> Counter[str]:
    counts: Counter[str] = Counter()
    if isinstance(value, dict):
        category = value.get("source_category")
        if isinstance(category, str) and category in ARTIFACT_HARNESS_PROVENANCE_CATEGORIES:
            counts[category] += 1
        for nested in value.values():
            counts.update(collect_artifact_harness_provenance_counts(nested))
    elif isinstance(value, list):
        for item in value:
            counts.update(collect_artifact_harness_provenance_counts(item))
    return counts


def build_artifact_harness_provenance_ledger(
    config: HubConfig,
    target_arg: str,
    packet_id: str | None,
) -> tuple[int, dict[str, Any], list[str]]:
    code, state, errors, manifest, status_payload = load_artifact_harness_lifecycle_state(config, "provenance", target_arg, packet_id)
    if code != 0:
        payload = dict(state)
        payload.setdefault("provenance_ledger_path", str(Path(payload["run_dir"]) / "packet_provenance_ledger.json") if payload.get("run_dir") else None)
        payload.setdefault("source_categories", list(ARTIFACT_HARNESS_PROVENANCE_CATEGORIES))
        payload.setdefault("packet_chain_provenance", {})
        return code, payload, errors
    manifest = manifest or {}
    status_payload = status_payload or {}

    target = Path(state["target_path"])
    run_dir = Path(state["run_dir"])
    ledger_path = run_dir / "packet_provenance_ledger.json"
    replay_evidence_path = run_dir / "artifact_replay_evidence.json"
    try:
        ensure_targets_under_root(target, {"provenance_ledger_path": ledger_path, "replay_evidence_path": replay_evidence_path})
    except HubRuntimeError as exc:
        payload = dict(state)
        payload.update(
            {
                "provenance_ledger_path": str(ledger_path),
                "source_categories": list(ARTIFACT_HARNESS_PROVENANCE_CATEGORIES),
                "packet_chain_provenance": {},
                "refused": True,
                "reason": "provenance_ledger_path_outside_target_workspace",
            }
        )
        return 1, payload, [str(exc)]

    packet_paths = {
        "artifact_harness_spec": Path(state["packets"].get("artifact_harness_spec", run_dir / "artifact_harness_spec.md")),
        "hr_staffing_packet": Path(state["packets"].get("hr_staffing_packet", run_dir / "hr_staffing_packet.md")),
        "team_operating_packet": Path(state["packets"].get("team_operating_packet", run_dir / "team_operating_packet.md")),
        "capability_access_packet": Path(state["packets"].get("capability_access_packet", run_dir / "capability_access_packet.md")),
        "runtime_mapping": Path(state["packets"].get("runtime_mapping", run_dir / "open_multi_agent_runtasks_mapping.md")),
        "manifest": Path(state["manifest"]),
        "status": Path(state["status_path"]),
    }
    packet_observations = {key: artifact_harness_packet_completion_heuristics(path) for key, path in packet_paths.items()}
    unresolved_total = sum(int(item.get("heuristic_open_items", 0)) for item in packet_observations.values())

    manifest_path = str(packet_paths["manifest"])
    status_path = str(packet_paths["status"])
    replay_record = (
        artifact_harness_provenance_record(
            "repo_evidence",
            "high",
            source_path=str(replay_evidence_path),
            note="Replay evidence exists and can be inspected as prior observation evidence.",
            grounded=True,
        )
        if replay_evidence_path.exists()
        else artifact_harness_provenance_record(
            "unresolved",
            "high",
            source_path=str(replay_evidence_path),
            note="No replay evidence file exists for this packet run yet.",
        )
    )
    expected_artifact = manifest.get("expected_artifact")
    field_provenance = {
        "packet_id": artifact_harness_provenance_record(
            "generated_scaffold",
            "high",
            source_path=manifest_path,
            source_field="id",
            value=state["id"],
            note="Packet id is generated by the Artifact Harness scaffold or supplied explicitly.",
            grounded=True,
        ),
        "mission": artifact_harness_provenance_record(
            "user_mission",
            "high",
            source_path=manifest_path,
            source_field="mission",
            value=manifest.get("mission"),
            note="Mission is copied from the user-supplied artifact-harness command.",
            grounded=True,
        ),
        "expected_artifact": artifact_harness_provenance_record(
            "user_mission" if expected_artifact else "unresolved",
            "medium" if expected_artifact else "high",
            source_path=manifest_path,
            source_field="expected_artifact",
            value=expected_artifact,
            note="Expected artifact is explicit only when supplied by the mission or --artifact.",
            grounded=bool(expected_artifact),
        ),
        "target_workspace": artifact_harness_provenance_record(
            "user_mission",
            "high",
            source_path=manifest_path,
            source_field="target_path",
            value=state["target_path"],
            note="Target workspace comes from the explicit --path argument.",
            grounded=True,
        ),
        "packet_paths": artifact_harness_provenance_record(
            "generated_scaffold",
            "high",
            source_path=manifest_path,
            source_field="packets",
            value=manifest.get("packets", {}),
            note="Packet paths are scaffold outputs recorded in the manifest.",
            grounded=True,
        ),
        "lifecycle_status": artifact_harness_provenance_record(
            "repo_evidence",
            "high",
            source_path=status_path,
            source_field="status",
            value=state["status"],
            note="Lifecycle status is continuity metadata only, not approval or acceptance.",
            grounded=True,
        ),
        "lifecycle_history": artifact_harness_provenance_record(
            "repo_evidence",
            "high",
            source_path=status_path,
            source_field="history",
            value=status_payload.get("history", []),
            note="Lifecycle history is read from packet_status.json.",
            grounded=True,
        ),
        "replay_evidence": replay_record,
        "open_field_heuristics": artifact_harness_provenance_record(
            "unresolved" if unresolved_total else "repo_evidence",
            "low",
            source_path=str(ledger_path),
            value={"heuristic_open_items_total": unresolved_total},
            note="Open-field counts are simple heuristics and are not verification results.",
            grounded=False,
        ),
    }
    packet_chain_provenance = {
        "artifact_harness_spec": {
            "packet_path": str(packet_paths["artifact_harness_spec"]),
            "mission_source": field_provenance["mission"],
            "contract_source": artifact_harness_provenance_record("generated_scaffold", "medium", source_path=str(packet_paths["artifact_harness_spec"]), note="Contract fields are scaffolded from the mission and template until filled.", grounded=False),
            "acceptance_source": artifact_harness_provenance_record("generated_scaffold", "medium", source_path=str(packet_paths["artifact_harness_spec"]), note="Acceptance checks begin as scaffolded prompts and must be reviewed against the mission.", grounded=False),
            "boundary_source": artifact_harness_provenance_record("template_default", "high", source_path=str(packet_paths["artifact_harness_spec"]), note="SPEC boundary is rule / contract / acceptance / boundary only.", grounded=True),
        },
        "hr_staffing_packet": {
            "packet_path": str(packet_paths["hr_staffing_packet"]),
            "source_spec": artifact_harness_provenance_record("packet_reference", "high", source_path=str(packet_paths["artifact_harness_spec"]), note="HR staffing is derived from the SPEC and mission.", grounded=True),
            "staffing_boundary": artifact_harness_provenance_record("template_default", "high", source_path=str(packet_paths["hr_staffing_packet"]), note="HR owns staffing and role design only.", grounded=True),
            "role_fit": artifact_harness_provenance_record("agent_inference", "medium", source_path=str(packet_paths["hr_staffing_packet"]), note="Role fit remains an inferred staffing decision until reviewed.", grounded=False),
        },
        "team_operating_packet": {
            "packet_path": str(packet_paths["team_operating_packet"]),
            "source_spec": artifact_harness_provenance_record("packet_reference", "high", source_path=str(packet_paths["artifact_harness_spec"]), note="Team Operating Packet references SPEC constraints.", grounded=True),
            "source_hr_staffing_packet": artifact_harness_provenance_record("packet_reference", "high", source_path=str(packet_paths["hr_staffing_packet"]), note="Team Operating Packet references HR staffing output.", grounded=True),
            "collaboration_model": artifact_harness_provenance_record("generated_scaffold", "medium", source_path=str(packet_paths["team_operating_packet"]), note="Collaboration model starts as scaffolded coordination guidance.", grounded=False),
        },
        "capability_access_packet": {
            "packet_path": str(packet_paths["capability_access_packet"]),
            "source_team_operating_packet": artifact_harness_provenance_record("packet_reference", "high", source_path=str(packet_paths["team_operating_packet"]), note="CAP derives capability needs from the Team Operating Packet.", grounded=True),
            "authorization_boundary": artifact_harness_provenance_record("template_default", "high", source_path=str(packet_paths["capability_access_packet"]), note="CAP owns skill/plugin/tool authorization, approval gates, and runtime allowlist only.", grounded=True),
            "approval_gates": artifact_harness_provenance_record("approval_required", "high", source_path=str(packet_paths["capability_access_packet"]), note="Approval gates require explicit approval before capability exposure or continuation.", grounded=False),
        },
        "runtime_mapping": {
            "packet_path": str(packet_paths["runtime_mapping"]),
            "source_team_operating_packet": artifact_harness_provenance_record("packet_reference", "high", source_path=str(packet_paths["team_operating_packet"]), note="Runtime mapping must trace to the Team Operating Packet.", grounded=True),
            "source_capability_access_packet": artifact_harness_provenance_record("packet_reference", "high", source_path=str(packet_paths["capability_access_packet"]), note="Runtime mapping must trace allowed tools and approvals to CAP.", grounded=True),
            "execution_boundary": artifact_harness_provenance_record("template_default", "high", source_path=str(packet_paths["runtime_mapping"]), note="Runtime mapping is an execution layer only, not a governance owner.", grounded=True),
            "runtime_output": artifact_harness_provenance_record("runtime_output", "low", source_path=str(packet_paths["runtime_mapping"]), note="No runtime output is implied by the scaffold unless execution evidence is attached.", grounded=False),
        },
        "lifecycle_status": {
            "status_path": status_path,
            "status_source": field_provenance["lifecycle_status"],
        },
        "replay_evidence": {
            "evidence_path": str(replay_evidence_path),
            "evidence_source": replay_record,
        },
    }
    source_counts = collect_artifact_harness_provenance_counts({"field_provenance": field_provenance, "packet_chain_provenance": packet_chain_provenance})
    generated_at = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    ledger = {
        "schema_version": 1,
        "ledger_type": "artifact_harness_provenance_ledger",
        "generated_at": generated_at,
        "id": state["id"],
        "mission": manifest.get("mission"),
        "target_path": state["target_path"],
        "run_dir": state["run_dir"],
        "manifest": state["manifest"],
        "registry_path": state["registry_path"],
        "status": state["status"],
        "status_path": state["status_path"],
        "provenance_ledger_path": str(ledger_path),
        "source_categories": list(ARTIFACT_HARNESS_PROVENANCE_CATEGORIES),
        "source_category_summary": {category: int(source_counts.get(category, 0)) for category in ARTIFACT_HARNESS_PROVENANCE_CATEGORIES},
        "field_provenance": field_provenance,
        "packet_chain_provenance": packet_chain_provenance,
        "packet_observations": packet_observations,
        "grounding_summary": {
            "grounded_categories": ["user_mission", "packet_reference", "repo_evidence"],
            "scaffold_categories": ["template_default", "generated_scaffold", "agent_inference"],
            "requires_attention_categories": ["approval_required", "unresolved", "unknown"],
            "heuristic_open_items_total": unresolved_total,
        },
        "commands": {
            "provenance_json": artifact_harness_lifecycle_command(config, "provenance", target, state["id"], emit_json=True),
            "runtime_check_json": artifact_harness_lifecycle_command(config, "runtime-check", target, state["id"], emit_json=True),
            "replay_json": artifact_harness_lifecycle_command(config, "replay", target, state["id"], emit_json=True),
            "status_json": artifact_harness_lifecycle_command(config, "status", target, state["id"], emit_json=True),
            "resume_json": artifact_harness_lifecycle_command(config, "resume", target, state["id"], emit_json=True),
        },
        "governance_boundary": "Provenance ledger is source tracking only. It does not accept artifacts, approve capabilities, select runtime, replace upstream packet ownership, perform verification, or execute adapters.",
        "refused": False,
        "reason": None,
    }
    dump_json(ledger_path, ledger)
    return 0, ledger, []


def render_artifact_harness_provenance_markdown(payload: dict[str, Any]) -> str:
    if payload.get("refused"):
        return f"# Artifact Harness Provenance Ledger\n\n- Refused: `true`\n- Reason: `{payload.get('reason')}`\n"
    summary = payload.get("source_category_summary", {})
    lines = [
        "# Artifact Harness Provenance Ledger",
        "",
        f"- Packet ID: `{payload['id']}`",
        f"- Target path: `{payload['target_path']}`",
        f"- Run directory: `{payload['run_dir']}`",
        f"- Status: `{payload['status']}`",
        f"- Ledger path: `{payload['provenance_ledger_path']}`",
        "",
        "## Source Categories",
        "",
    ]
    for category in payload.get("source_categories", []):
        lines.append(f"- {category}: `{summary.get(category, 0)}`")
    lines.append("")
    return "\n".join(lines)


def do_artifact_harness_provenance(
    config: HubConfig,
    target_arg: str,
    packet_id: str | None,
    emit_json: bool = False,
) -> int:
    code, payload, errors = build_artifact_harness_provenance_ledger(config, target_arg, packet_id)
    for line in errors:
        print(line, file=sys.stderr)
    if emit_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    elif code == 0:
        print(render_artifact_harness_provenance_markdown(payload), end="")
    return code


def artifact_harness_markdown_label_value(text: str, label: str) -> str | None:
    pattern = re.compile(rf"^[ \t]*-[ \t]*{re.escape(label)}[ \t]*:[ \t]*(.*)$", re.IGNORECASE | re.MULTILINE)
    match = pattern.search(text)
    if not match:
        return None
    value = match.group(1).strip()
    return value or None


def artifact_harness_markdown_label_is_resolved(text: str, label: str) -> bool:
    value = artifact_harness_markdown_label_value(text, label)
    if value is None:
        return False
    return value.lower() not in {"yes/no", "n/a", "none", "todo", "tbd", "open", "unresolved"}


def artifact_harness_markdown_bool(text: str, label: str) -> str:
    value = artifact_harness_markdown_label_value(text, label)
    if value is None:
        return "unknown"
    normalized = value.lower().strip("` ")
    if normalized == "yes/no":
        return "unknown"
    if re.match(r"^(yes|true|required)\b", normalized):
        return "yes"
    if re.match(r"^(no|false|not required|none)\b", normalized):
        return "no"
    return "unknown"


def artifact_harness_runtime_finding(code: str, severity: str, message: str, source_path: Path | str) -> dict[str, str]:
    return {
        "code": code,
        "severity": severity,
        "message": message,
        "source_path": str(source_path),
    }


def artifact_harness_normalize_decision(value: str | None) -> str:
    return (value or "").strip().lower()


def artifact_harness_latest_approval_decisions(evidence: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    if not isinstance(evidence, dict):
        return {}
    decisions = evidence.get("decisions", [])
    if not isinstance(decisions, list):
        return {}
    latest: dict[str, dict[str, Any]] = {}
    for decision in decisions:
        if not isinstance(decision, dict):
            continue
        gate_id = str(decision.get("gate_id") or "").strip()
        if not gate_id:
            continue
        latest[gate_id] = decision
    return latest


def artifact_harness_approval_decision_lists(evidence: dict[str, Any] | None) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    latest = artifact_harness_latest_approval_decisions(evidence)
    approved: list[dict[str, Any]] = []
    denied: list[dict[str, Any]] = []
    for decision in latest.values():
        normalized = artifact_harness_normalize_decision(str(decision.get("decision") or ""))
        if normalized == "approved":
            approved.append(decision)
        elif normalized == "denied":
            denied.append(decision)
    return approved, denied


def artifact_harness_load_approval_evidence(approval_path: Path) -> dict[str, Any]:
    if not approval_path.exists():
        return {}
    return load_json_file_strict(approval_path, {}, "artifact harness approval evidence")


def artifact_harness_split_capability_value(value: str | None) -> list[str]:
    if not value:
        return []
    raw_items = re.split(r"[,;\n]+|\s+\|\s+", value)
    items: list[str] = []
    for raw_item in raw_items:
        item = raw_item.strip(" `\t\r\n-")
        if not item:
            continue
        if item.lower() in {"none", "n/a", "na", "yes/no", "todo", "tbd", "open", "unresolved"}:
            continue
        if item not in items:
            items.append(item)
    return items


def artifact_harness_extract_runtime_capabilities(runtime_text: str, cap_text: str) -> tuple[list[str], list[str]]:
    exposed: list[str] = []
    for label in (
        "authorized skills",
        "authorized plugins",
        "authorized tools",
        "capabilities to expose",
        "runtime allowlist",
    ):
        for item in artifact_harness_split_capability_value(artifact_harness_markdown_label_value(runtime_text, label)):
            if item not in exposed:
                exposed.append(item)

    withheld: list[str] = []
    for text in (runtime_text, cap_text):
        for label in (
            "denied or withheld capabilities",
            "withheld capabilities",
            "capabilities to withhold",
            "denied capabilities",
        ):
            for item in artifact_harness_split_capability_value(artifact_harness_markdown_label_value(text, label)):
                if item not in withheld:
                    withheld.append(item)

    withheld_lc = {item.lower() for item in withheld}
    filtered_exposed = [item for item in exposed if item.lower() not in withheld_lc]
    return filtered_exposed, withheld


def build_artifact_harness_runtime_readiness_report(
    config: HubConfig,
    target_arg: str,
    packet_id: str | None,
) -> tuple[int, dict[str, Any], list[str]]:
    code, state, errors, manifest, _status_payload = load_artifact_harness_lifecycle_state(config, "runtime-check", target_arg, packet_id)
    if code != 0:
        payload = dict(state)
        payload.setdefault("runtime_readiness_report_path", str(Path(payload["run_dir"]) / "runtime_readiness_report.json") if payload.get("run_dir") else None)
        payload.setdefault("runtime_invocation_ready", False)
        payload.setdefault("execution_authorized", False)
        payload.setdefault("approval_gates_required", False)
        payload.setdefault("required_execution_surface", None)
        payload.setdefault("blocking_findings", [])
        payload.setdefault("checks", {})
        return code, payload, errors
    manifest = manifest or {}

    target = Path(state["target_path"])
    run_dir = Path(state["run_dir"])
    report_path = run_dir / "runtime_readiness_report.json"
    replay_evidence_path = run_dir / "artifact_replay_evidence.json"
    provenance_ledger_path = run_dir / "packet_provenance_ledger.json"
    approval_evidence_path = run_dir / ARTIFACT_HARNESS_APPROVAL_EVIDENCE_FILENAME
    try:
        ensure_targets_under_root(
            target,
            {
                "runtime_readiness_report_path": report_path,
                "replay_evidence_path": replay_evidence_path,
                "provenance_ledger_path": provenance_ledger_path,
                "approval_evidence_path": approval_evidence_path,
            },
        )
    except HubRuntimeError as exc:
        payload = dict(state)
        payload.update(
            {
                "runtime_readiness_report_path": str(report_path),
                "runtime_invocation_ready": False,
                "execution_authorized": False,
                "approval_gates_required": False,
                "required_execution_surface": None,
                "blocking_findings": [],
                "checks": {},
                "refused": True,
                "reason": "runtime_readiness_report_path_outside_target_workspace",
            }
        )
        return 1, payload, [str(exc)]

    packet_paths = {
        "team_operating_packet": Path(state["packets"].get("team_operating_packet", run_dir / "team_operating_packet.md")),
        "capability_access_packet": Path(state["packets"].get("capability_access_packet", run_dir / "capability_access_packet.md")),
        "runtime_mapping": Path(state["packets"].get("runtime_mapping", run_dir / "open_multi_agent_runtasks_mapping.md")),
    }
    cap_path = packet_paths["capability_access_packet"]
    top_path = packet_paths["team_operating_packet"]
    runtime_path = packet_paths["runtime_mapping"]
    cap_text = cap_path.read_text(encoding="utf-8", errors="replace") if cap_path.exists() else ""
    runtime_text = runtime_path.read_text(encoding="utf-8", errors="replace") if runtime_path.exists() else ""
    runtime_lower = runtime_text.lower()
    cap_lower = cap_text.lower()

    source_cap_value = artifact_harness_markdown_label_value(runtime_text, "source capability access packet") or artifact_harness_markdown_label_value(runtime_text, "CAP source")
    source_top_value = artifact_harness_markdown_label_value(runtime_text, "source operating packet")
    declares_source_cap = bool(source_cap_value)
    declares_source_top = bool(source_top_value)
    expected_cap_rel = manifest.get("packets", {}).get("capability_access_packet") if isinstance(manifest.get("packets"), dict) else None
    expected_top_rel = manifest.get("packets", {}).get("team_operating_packet") if isinstance(manifest.get("packets"), dict) else None
    source_cap_matches_manifest = bool(source_cap_value and expected_cap_rel and expected_cap_rel in source_cap_value)
    source_top_matches_manifest = bool(source_top_value and expected_top_rel and expected_top_rel in source_top_value)

    authorized_fields_present = all(label in runtime_lower for label in ("authorized skills", "authorized plugins", "authorized tools"))
    authorized_capabilities_resolved = any(
        artifact_harness_markdown_label_is_resolved(runtime_text, label)
        for label in ("authorized skills", "authorized plugins", "authorized tools")
    )
    denied_fields_present = "denied or withheld capabilities" in runtime_lower or "withheld capabilities" in runtime_lower
    denied_capabilities_resolved = any(
        artifact_harness_markdown_label_is_resolved(text, label)
        for text in (runtime_text, cap_text)
        for label in ("denied or withheld capabilities", "withheld capabilities", "capabilities to withhold")
    )
    cap_gate_fields_present = "cap approval gates" in runtime_lower or "approval gates" in cap_lower
    runtime_exposure_boundaries_present = "runtime exposure rule" in runtime_lower and "expose only capabilities" in runtime_lower and "withhold any capability" in runtime_lower
    cap_access_boundaries_present = "access boundaries" in cap_lower or "cap access boundaries" in runtime_lower

    approval_gate_state = artifact_harness_markdown_bool(runtime_text, "approval gates required")
    if approval_gate_state == "yes":
        approval_gates_required = True
    elif approval_gate_state == "no":
        approval_gates_required = False
    else:
        approval_gates_required = True
    approval_gates_unresolved = approval_gate_state == "unknown"

    cli_allowed_state = artifact_harness_markdown_bool(runtime_text, "CLI allowed")
    cli_execution_allowed = cli_allowed_state == "yes" or bool(re.search(r"\boma\s+cli\s+allowed\s*:\s*(yes|true)\b", runtime_lower))
    enforceable_api_surface = (
        "typescript api" in runtime_lower
        and "runtasks" in runtime_lower
        and ("approval callback" in runtime_lower or "onapproval" in runtime_lower)
    )
    required_execution_surface = "typescript_api_runTasks_with_approval_callbacks" if approval_gates_required else "cli_or_api_without_approval_gates"
    explicit_human_approval_evidence = False
    if provenance_ledger_path.exists():
        try:
            provenance = load_json_file_strict(provenance_ledger_path, {}, "artifact harness provenance ledger")
            summary = provenance.get("source_category_summary", {})
            explicit_human_approval_evidence = isinstance(summary, dict) and int(summary.get("human_approval", 0) or 0) > 0
        except HubRuntimeError:
            explicit_human_approval_evidence = False
    if not explicit_human_approval_evidence:
        explicit_human_approval_evidence = bool(re.search(r"\b(human approval|approval evidence)\s*:\s*(approved|granted|yes|true)\b", cap_lower))
    approved_gate_records: list[dict[str, Any]] = []
    denied_gate_records: list[dict[str, Any]] = []
    if approval_evidence_path.exists():
        try:
            approval_evidence = artifact_harness_load_approval_evidence(approval_evidence_path)
            approved_gate_records, denied_gate_records = artifact_harness_approval_decision_lists(approval_evidence)
            if not explicit_human_approval_evidence and approved_gate_records:
                explicit_human_approval_evidence = True
        except HubRuntimeError:
            approved_gate_records = []
            denied_gate_records = []

    blocking_findings: list[dict[str, str]] = []
    advisory_findings: list[dict[str, str]] = []
    if not declares_source_cap:
        blocking_findings.append(artifact_harness_runtime_finding("missing_source_cap_trace", "P1", "Runtime mapping does not declare a source Capability Access Packet.", runtime_path))
    elif not source_cap_matches_manifest:
        blocking_findings.append(artifact_harness_runtime_finding("source_cap_trace_mismatch", "P1", "Runtime mapping source CAP does not match the manifest CAP packet path.", runtime_path))
    if not declares_source_top:
        blocking_findings.append(artifact_harness_runtime_finding("missing_source_team_operating_packet_trace", "P1", "Runtime mapping does not declare a source Team Operating Packet.", runtime_path))
    elif not source_top_matches_manifest:
        blocking_findings.append(artifact_harness_runtime_finding("source_team_operating_packet_trace_mismatch", "P1", "Runtime mapping source operating packet does not match the manifest TOP path.", runtime_path))
    if not authorized_fields_present or not authorized_capabilities_resolved:
        blocking_findings.append(artifact_harness_runtime_finding("authorized_capabilities_unresolved", "P1", "Runtime mapping does not resolve CAP-derived authorized capabilities.", runtime_path))
    if not denied_fields_present:
        blocking_findings.append(artifact_harness_runtime_finding("denied_capabilities_trace_missing", "P2", "Runtime mapping does not record denied or withheld capabilities.", runtime_path))
    elif not denied_capabilities_resolved:
        advisory_findings.append(artifact_harness_runtime_finding("denied_capabilities_unresolved", "P2", "Denied or withheld capabilities are present but not filled.", runtime_path))
    if not cap_gate_fields_present:
        blocking_findings.append(artifact_harness_runtime_finding("cap_approval_gates_missing", "P1", "Runtime mapping does not record CAP approval gates.", runtime_path))
    if approval_gates_unresolved:
        blocking_findings.append(artifact_harness_runtime_finding("approval_gate_state_unresolved", "P1", "Runtime mapping leaves approval gate requirement as unresolved.", runtime_path))
    if approval_gates_required and not enforceable_api_surface:
        blocking_findings.append(artifact_harness_runtime_finding("approval_gate_requires_enforceable_api", "P1", "Approval-gated execution requires the TypeScript runTasks() API with approval callbacks.", runtime_path))
    if approval_gates_required and cli_execution_allowed:
        blocking_findings.append(artifact_harness_runtime_finding("approval_gate_requires_enforceable_api", "P1", "Approval gates are required, but the mapping allows CLI execution; the oma CLI is non-enforcing for approval callbacks.", runtime_path))
    if not runtime_exposure_boundaries_present or not cap_access_boundaries_present:
        blocking_findings.append(artifact_harness_runtime_finding("runtime_exposure_boundaries_missing", "P1", "Runtime exposure boundaries are missing or incomplete.", runtime_path))

    execution_authorized = bool(explicit_human_approval_evidence and not blocking_findings)
    if not explicit_human_approval_evidence:
        advisory_findings.append(artifact_harness_runtime_finding("missing_explicit_human_approval", "P2", "No explicit human approval evidence was found; lifecycle status alone is not approval.", cap_path))
    checks = {
        "source_cap_packet_path": str(cap_path),
        "source_team_operating_packet_path": str(top_path),
        "declares_source_cap": declares_source_cap,
        "source_cap_matches_manifest": source_cap_matches_manifest,
        "declares_source_team_operating_packet": declares_source_top,
        "source_team_operating_packet_matches_manifest": source_top_matches_manifest,
        "includes_cap_derived_authorized_capabilities": authorized_capabilities_resolved,
        "authorized_capability_fields_present": authorized_fields_present,
        "includes_denied_or_withheld_capabilities": denied_fields_present,
        "denied_or_withheld_capabilities_resolved": denied_capabilities_resolved,
        "records_cap_approval_gates": cap_gate_fields_present,
        "approval_gate_state": approval_gate_state,
        "enforceable_api_surface_present": enforceable_api_surface,
        "cli_execution_allowed": cli_execution_allowed,
        "runtime_exposure_boundaries_present": runtime_exposure_boundaries_present,
        "cap_access_boundaries_present": cap_access_boundaries_present,
        "explicit_human_approval_evidence": explicit_human_approval_evidence,
        "lifecycle_status_counts_as_approval": False,
        "replay_evidence_present": replay_evidence_path.exists(),
        "provenance_ledger_present": provenance_ledger_path.exists(),
        "approval_evidence_present": approval_evidence_path.exists(),
        "approved_runtime_gates": [record.get("gate_id") for record in approved_gate_records],
        "denied_runtime_gates": [record.get("gate_id") for record in denied_gate_records],
    }
    generated_at = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    report = {
        "schema_version": 1,
        "report_type": "artifact_harness_runtime_readiness",
        "generated_at": generated_at,
        "id": state["id"],
        "mission": manifest.get("mission"),
        "target_path": state["target_path"],
        "run_dir": state["run_dir"],
        "manifest": state["manifest"],
        "registry_path": state["registry_path"],
        "status": state["status"],
        "status_path": state["status_path"],
        "runtime_readiness_report_path": str(report_path),
        "runtime_invocation_ready": not blocking_findings,
        "execution_authorized": execution_authorized,
        "approval_gates_required": approval_gates_required,
        "required_execution_surface": required_execution_surface,
        "blocking_findings": blocking_findings,
        "advisory_findings": advisory_findings,
        "checks": checks,
        "evidence_inputs": {
            "capability_access_packet": str(cap_path),
            "team_operating_packet": str(top_path),
            "runtime_mapping": str(runtime_path),
            "replay_evidence": str(replay_evidence_path) if replay_evidence_path.exists() else None,
            "provenance_ledger": str(provenance_ledger_path) if provenance_ledger_path.exists() else None,
            "approval_evidence": str(approval_evidence_path) if approval_evidence_path.exists() else None,
        },
        "commands": {
            "runtime_check_json": artifact_harness_lifecycle_command(config, "runtime-check", target, state["id"], emit_json=True),
            "approval_json": artifact_harness_approval_command(config, target, state["id"], emit_json=True),
            "runtime_invoke_json": artifact_harness_runtime_invoke_command(config, target, state["id"], emit_json=True),
            "provenance_json": artifact_harness_lifecycle_command(config, "provenance", target, state["id"], emit_json=True),
            "replay_json": artifact_harness_lifecycle_command(config, "replay", target, state["id"], emit_json=True),
            "status_json": artifact_harness_lifecycle_command(config, "status", target, state["id"], emit_json=True),
        },
        "governance_boundary": "Runtime readiness is preflight evidence only. It does not approve capabilities, authorize execution, accept artifacts, make the runtime adapter a governance owner, or invoke an external runtime.",
        "refused": False,
        "reason": None,
    }
    dump_json(report_path, report)
    return 0, report, []


def render_artifact_harness_runtime_readiness_markdown(payload: dict[str, Any]) -> str:
    if payload.get("refused"):
        return f"# Artifact Harness Runtime Readiness\n\n- Refused: `true`\n- Reason: `{payload.get('reason')}`\n"
    lines = [
        "# Artifact Harness Runtime Readiness",
        "",
        f"- Packet ID: `{payload['id']}`",
        f"- Target path: `{payload['target_path']}`",
        f"- Run directory: `{payload['run_dir']}`",
        f"- Status: `{payload['status']}`",
        f"- Report path: `{payload['runtime_readiness_report_path']}`",
        f"- Runtime invocation ready: `{'true' if payload['runtime_invocation_ready'] else 'false'}`",
        f"- Execution authorized: `{'true' if payload['execution_authorized'] else 'false'}`",
        f"- Approval gates required: `{'true' if payload['approval_gates_required'] else 'false'}`",
        f"- Required execution surface: `{payload['required_execution_surface']}`",
        "",
        "## Blocking Findings",
        "",
    ]
    findings = payload.get("blocking_findings", [])
    if findings:
        for finding in findings:
            lines.append(f"- `{finding.get('code')}`: {finding.get('message')}")
    else:
        lines.append("- none")
    lines.append("")
    return "\n".join(lines)


def do_artifact_harness_runtime_check(
    config: HubConfig,
    target_arg: str,
    packet_id: str | None,
    emit_json: bool = False,
) -> int:
    code, payload, errors = build_artifact_harness_runtime_readiness_report(config, target_arg, packet_id)
    for line in errors:
        print(line, file=sys.stderr)
    if emit_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    elif code == 0:
        print(render_artifact_harness_runtime_readiness_markdown(payload), end="")
    return code


def artifact_harness_approval_refusal_payload(
    config: HubConfig,
    state: dict[str, Any],
    reason: str,
    *,
    gate_id: str | None = None,
    decision: str | None = None,
    approver: str | None = None,
) -> dict[str, Any]:
    payload = dict(state)
    target = Path(payload["target_path"]) if payload.get("target_path") else None
    packet_id = str(payload.get("id") or "") if payload.get("id") else ""
    approval_path = Path(payload["run_dir"]) / ARTIFACT_HARNESS_APPROVAL_EVIDENCE_FILENAME if payload.get("run_dir") else None
    payload.update(
        {
            "command": "artifact-harness approval",
            "schema_version": ARTIFACT_HARNESS_COMMAND_SCHEMA_VERSION,
            "approval_evidence_path": str(approval_path) if approval_path else payload.get("approval_evidence_path"),
            "gate_id": gate_id,
            "decision": decision,
            "approver": approver,
            "decisions": [],
            "latest_decisions": {},
            "commands": {
                "status_json": artifact_harness_lifecycle_command(config, "status", target, packet_id, emit_json=True)
                if target is not None and packet_id
                else None,
            },
            "governance_boundary": "Approval evidence records explicit decisions only. It does not rewrite CAP, approve capabilities by itself, accept artifacts, mark lifecycle status, or execute runtime adapters.",
            "refused": True,
            "reason": reason,
        }
    )
    return payload


def build_artifact_harness_approval_evidence(
    config: HubConfig,
    target_arg: str,
    packet_id: str | None,
    gate_id: str | None,
    decision: str | None,
    approver: str | None,
    note: str,
) -> tuple[int, dict[str, Any], list[str]]:
    code, state, errors, _manifest, _status_payload = load_artifact_harness_lifecycle_state(config, "approval", target_arg, packet_id)
    if code != 0:
        return code, artifact_harness_approval_refusal_payload(config, state, state.get("reason") or "approval_refused", gate_id=gate_id, decision=decision, approver=approver), errors

    normalized_gate = (gate_id or "").strip()
    normalized_decision = artifact_harness_normalize_decision(decision)
    normalized_approver = (approver or "").strip()
    validation_errors: list[str] = []
    if not normalized_gate:
        validation_errors.append("Artifact Harness approval requires `--gate <gate-id>`.")
    if normalized_decision not in {"approved", "denied"}:
        validation_errors.append("Artifact Harness approval requires `--decision approved|denied`.")
    if not normalized_approver:
        validation_errors.append("Artifact Harness approval requires `--approver <label>`.")
    if validation_errors:
        reason = "missing_required_approval_fields" if not normalized_gate or not normalized_approver else "invalid_approval_decision"
        return 1, artifact_harness_approval_refusal_payload(config, state, reason, gate_id=gate_id, decision=decision, approver=approver), validation_errors

    target = Path(state["target_path"])
    run_dir = Path(state["run_dir"])
    approval_path = run_dir / ARTIFACT_HARNESS_APPROVAL_EVIDENCE_FILENAME
    try:
        ensure_targets_under_root(target, {"approval_evidence_path": approval_path})
    except HubRuntimeError as exc:
        return 1, artifact_harness_approval_refusal_payload(config, state, "approval_evidence_path_outside_target_workspace", gate_id=normalized_gate, decision=normalized_decision, approver=normalized_approver), [str(exc)]

    try:
        existing = artifact_harness_load_approval_evidence(approval_path)
    except HubRuntimeError as exc:
        return 1, artifact_harness_approval_refusal_payload(config, state, "invalid_approval_evidence_json", gate_id=normalized_gate, decision=normalized_decision, approver=normalized_approver), [str(exc)]

    decisions = existing.get("decisions", []) if isinstance(existing, dict) else []
    if not isinstance(decisions, list):
        decisions = []
    created_at = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    decision_record = {
        "gate_id": normalized_gate,
        "decision": normalized_decision,
        "approver": normalized_approver,
        "note": note.strip(),
        "source": "user_cli",
        "created_at": created_at,
    }
    decisions.append(decision_record)
    evidence = {
        "schema_version": ARTIFACT_HARNESS_COMMAND_SCHEMA_VERSION,
        "evidence_type": "artifact_harness_approval_evidence",
        "id": state["id"],
        "target_path": state["target_path"],
        "run_dir": state["run_dir"],
        "approval_evidence_path": str(approval_path),
        "updated_at": created_at,
        "decisions": decisions,
        "latest_decisions": artifact_harness_latest_approval_decisions({"decisions": decisions}),
        "governance_boundary": "Approval evidence records explicit gate decisions only. It does not replace CAP ownership, lifecycle status, artifact acceptance, or runtime execution.",
    }
    dump_json(approval_path, evidence)
    payload = dict(evidence)
    payload.update(
        {
            "command": "artifact-harness approval",
            "ok": True,
            "decision_record": decision_record,
            "status": state["status"],
            "status_path": state["status_path"],
            "manifest": state["manifest"],
            "packets": state["packets"],
            "commands": {
                "approval_json": artifact_harness_approval_command(config, target, state["id"], normalized_gate, normalized_decision, normalized_approver, note=note.strip(), emit_json=True),
                "runtime_check_json": artifact_harness_lifecycle_command(config, "runtime-check", target, state["id"], emit_json=True),
                "runtime_invoke_json": artifact_harness_runtime_invoke_command(config, target, state["id"], emit_json=True),
                "status_json": artifact_harness_lifecycle_command(config, "status", target, state["id"], emit_json=True),
            },
            "refused": False,
            "reason": None,
        }
    )
    return 0, payload, []


def render_artifact_harness_approval_markdown(payload: dict[str, Any]) -> str:
    if payload.get("refused"):
        return f"# Artifact Harness Approval Evidence\n\n- Refused: `true`\n- Reason: `{payload.get('reason')}`\n"
    latest = payload.get("latest_decisions", {})
    lines = [
        "# Artifact Harness Approval Evidence",
        "",
        f"- Packet ID: `{payload['id']}`",
        f"- Evidence path: `{payload['approval_evidence_path']}`",
        f"- Updated at: `{payload['updated_at']}`",
        "",
        "## Latest Decisions",
        "",
    ]
    for gate_id, decision in latest.items():
        if isinstance(decision, dict):
            lines.append(f"- `{gate_id}`: `{decision.get('decision')}` by `{decision.get('approver')}`")
    lines.append("")
    return "\n".join(lines)


def do_artifact_harness_approval(
    config: HubConfig,
    target_arg: str,
    packet_id: str | None,
    gate_id: str | None,
    decision: str | None,
    approver: str | None,
    note: str,
    emit_json: bool = False,
) -> int:
    code, payload, errors = build_artifact_harness_approval_evidence(config, target_arg, packet_id, gate_id, decision, approver, note)
    for line in errors:
        print(line, file=sys.stderr)
    if emit_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    elif code == 0:
        print(render_artifact_harness_approval_markdown(payload), end="")
    return code


def artifact_harness_runtime_invocation_refusal_payload(
    config: HubConfig,
    state: dict[str, Any],
    reason: str,
    *,
    adapter: str | None = None,
    surface: str | None = None,
    dry_run: bool = False,
    readiness: dict[str, Any] | None = None,
    approval_evidence: dict[str, Any] | None = None,
    blocking_findings: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    payload = dict(state)
    target = Path(payload["target_path"]) if payload.get("target_path") else None
    run_dir = Path(payload["run_dir"]) if payload.get("run_dir") else None
    packet_id = str(payload.get("id") or "") if payload.get("id") else ""
    readiness_inputs = readiness.get("evidence_inputs", {}) if isinstance(readiness, dict) else {}
    approved, denied = artifact_harness_approval_decision_lists(approval_evidence)
    payload.update(
        {
            "command": "artifact-harness runtime-invoke",
            "schema_version": ARTIFACT_HARNESS_COMMAND_SCHEMA_VERSION,
            "id": packet_id or payload.get("id"),
            "adapter": adapter,
            "execution_surface": surface,
            "dry_run": dry_run,
            "would_execute": False,
            "runtime_invocation_allowed": False,
            "execution_performed": False,
            "source_capability_access_packet": readiness_inputs.get("capability_access_packet"),
            "source_team_operating_packet": readiness_inputs.get("team_operating_packet"),
            "source_runtime_mapping": readiness_inputs.get("runtime_mapping"),
            "runtime_readiness_report_path": str(run_dir / "runtime_readiness_report.json") if run_dir else payload.get("runtime_readiness_report_path"),
            "approval_evidence_path": str(run_dir / ARTIFACT_HARNESS_APPROVAL_EVIDENCE_FILENAME) if run_dir else payload.get("approval_evidence_path"),
            "runtime_invocation_report_path": str(run_dir / ARTIFACT_HARNESS_RUNTIME_INVOCATION_REPORT_FILENAME) if run_dir else payload.get("runtime_invocation_report_path"),
            "approval_gates_required": bool(readiness.get("approval_gates_required")) if isinstance(readiness, dict) else False,
            "required_execution_surface": readiness.get("required_execution_surface") if isinstance(readiness, dict) else None,
            "runtime_invocation_ready": bool(readiness.get("runtime_invocation_ready")) if isinstance(readiness, dict) else False,
            "execution_authorized": False,
            "approved_gates": [record.get("gate_id") for record in approved],
            "denied_gates": [record.get("gate_id") for record in denied],
            "exposed_capabilities": [],
            "withheld_capabilities": [],
            "blocking_findings": blocking_findings if blocking_findings is not None else (readiness.get("blocking_findings", []) if isinstance(readiness, dict) else []),
            "commands": {
                "runtime_check_json": artifact_harness_lifecycle_command(config, "runtime-check", target, packet_id, emit_json=True)
                if target is not None and packet_id
                else None,
                "approval_json": artifact_harness_approval_command(config, target, packet_id, emit_json=True)
                if target is not None and packet_id
                else None,
            },
            "governance_boundary": "Runtime invocation guard is execution-boundary evidence only. It does not approve capabilities, accept artifacts, invoke adapters, spawn agents, or make runtime adapters governance owners.",
            "refused": True,
            "reason": reason,
        }
    )
    return payload


def artifact_harness_required_runtime_gates(readiness: dict[str, Any]) -> list[str]:
    if readiness.get("approval_gates_required"):
        return [ARTIFACT_HARNESS_RUNTIME_APPROVAL_GATE_ID]
    return []


def artifact_harness_requested_surface_matches_required(readiness: dict[str, Any], surface: str) -> bool:
    required_surface = readiness.get("required_execution_surface")
    if required_surface == "typescript_api_runTasks_with_approval_callbacks":
        return surface == "typescript-runTasks"
    if required_surface == "cli_or_api_without_approval_gates":
        return surface in {"typescript-runTasks", "cli"}
    return False


def artifact_harness_load_or_build_readiness_for_invoke(
    config: HubConfig,
    target_arg: str,
    packet_id: str | None,
    state: dict[str, Any],
) -> tuple[int, dict[str, Any], list[str], str]:
    readiness_path = Path(state["run_dir"]) / "runtime_readiness_report.json"
    if readiness_path.exists():
        try:
            readiness = load_json_file_strict(readiness_path, {}, "artifact harness runtime readiness report")
            return 0, readiness, [], "loaded_existing"
        except HubRuntimeError as exc:
            return 1, {}, [str(exc)], "invalid_existing"
    code, readiness, errors = build_artifact_harness_runtime_readiness_report(config, target_arg, packet_id)
    return code, readiness, errors, "computed"


def build_artifact_harness_runtime_invocation_report(
    config: HubConfig,
    target_arg: str,
    packet_id: str | None,
    adapter: str | None,
    surface: str | None,
    dry_run: bool,
) -> tuple[int, dict[str, Any], list[str]]:
    code, state, errors, _manifest, _status_payload = load_artifact_harness_lifecycle_state(config, "runtime-invoke", target_arg, packet_id)
    if code != 0:
        return code, artifact_harness_runtime_invocation_refusal_payload(config, state, state.get("reason") or "runtime_invocation_refused", adapter=adapter, surface=surface, dry_run=dry_run), errors

    target = Path(state["target_path"])
    run_dir = Path(state["run_dir"])
    approval_path = run_dir / ARTIFACT_HARNESS_APPROVAL_EVIDENCE_FILENAME
    invocation_path = run_dir / ARTIFACT_HARNESS_RUNTIME_INVOCATION_REPORT_FILENAME
    runtime_path = Path(state["packets"].get("runtime_mapping", run_dir / "open_multi_agent_runtasks_mapping.md"))
    cap_path = Path(state["packets"].get("capability_access_packet", run_dir / "capability_access_packet.md"))
    try:
        ensure_targets_under_root(
            target,
            {
                "approval_evidence_path": approval_path,
                "runtime_invocation_report_path": invocation_path,
                "runtime_mapping": runtime_path,
                "capability_access_packet": cap_path,
            },
        )
    except HubRuntimeError as exc:
        payload = artifact_harness_runtime_invocation_refusal_payload(config, state, "runtime_invocation_path_outside_target_workspace", adapter=adapter, surface=surface, dry_run=dry_run)
        return 1, payload, [str(exc)]

    readiness_code, readiness, readiness_errors, readiness_source = artifact_harness_load_or_build_readiness_for_invoke(config, target_arg, packet_id, state)
    if readiness_code != 0:
        reason = readiness.get("reason") if isinstance(readiness, dict) and readiness.get("reason") else "runtime_readiness_refused"
        payload = artifact_harness_runtime_invocation_refusal_payload(config, state, str(reason), adapter=adapter, surface=surface, dry_run=dry_run, readiness=readiness)
        if reason != "manifest_packet_path_outside_target_workspace":
            dump_json(invocation_path, payload)
        return 1, payload, readiness_errors

    normalized_adapter = (adapter or "").strip()
    normalized_surface = (surface or "").strip()
    approval_evidence: dict[str, Any] = {}
    try:
        approval_evidence = artifact_harness_load_approval_evidence(approval_path)
    except HubRuntimeError as exc:
        payload = artifact_harness_runtime_invocation_refusal_payload(config, state, "invalid_approval_evidence_json", adapter=normalized_adapter, surface=normalized_surface, dry_run=dry_run, readiness=readiness)
        dump_json(invocation_path, payload)
        return 1, payload, [str(exc)]

    latest_decisions = artifact_harness_latest_approval_decisions(approval_evidence)
    required_gates = artifact_harness_required_runtime_gates(readiness)
    approved_gates: list[str] = []
    denied_gates: list[str] = []
    missing_gates: list[str] = []
    for gate in required_gates:
        latest = latest_decisions.get(gate)
        latest_value = artifact_harness_normalize_decision(str(latest.get("decision") if isinstance(latest, dict) else ""))
        if latest_value == "approved":
            approved_gates.append(gate)
        elif latest_value == "denied":
            denied_gates.append(gate)
        else:
            missing_gates.append(gate)

    runtime_text = runtime_path.read_text(encoding="utf-8", errors="replace") if runtime_path.exists() else ""
    cap_text = cap_path.read_text(encoding="utf-8", errors="replace") if cap_path.exists() else ""
    exposed_capabilities, withheld_capabilities = artifact_harness_extract_runtime_capabilities(runtime_text, cap_text)

    blocking_findings = list(readiness.get("blocking_findings", []) if isinstance(readiness.get("blocking_findings"), list) else [])
    reason: str | None = None
    if normalized_adapter not in ARTIFACT_HARNESS_SUPPORTED_RUNTIME_ADAPTERS:
        reason = "unsupported_runtime_adapter"
    elif normalized_surface not in ARTIFACT_HARNESS_SUPPORTED_EXECUTION_SURFACES:
        reason = "unsupported_execution_surface"
    elif not dry_run:
        reason = "dry_run_required"
    elif blocking_findings:
        reason = "runtime_readiness_blocking_findings"
    elif readiness.get("approval_gates_required") and normalized_surface == "cli":
        reason = "approval_gated_cli_forbidden"
    elif denied_gates:
        reason = "approval_denied"
    elif missing_gates:
        reason = "missing_required_approval_evidence"
    elif not artifact_harness_requested_surface_matches_required(readiness, normalized_surface):
        reason = "execution_surface_mismatch"

    generated_at = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    allowed = reason is None
    report = {
        "schema_version": ARTIFACT_HARNESS_COMMAND_SCHEMA_VERSION,
        "report_type": "artifact_harness_runtime_invocation_guard",
        "generated_at": generated_at,
        "command": "artifact-harness runtime-invoke",
        "id": state["id"],
        "target_path": state["target_path"],
        "run_dir": state["run_dir"],
        "manifest": state["manifest"],
        "status": state["status"],
        "adapter": normalized_adapter,
        "execution_surface": normalized_surface,
        "dry_run": dry_run,
        "would_execute": bool(allowed and dry_run and normalized_surface == "typescript-runTasks"),
        "runtime_invocation_allowed": allowed,
        "execution_performed": False,
        "source_capability_access_packet": readiness.get("evidence_inputs", {}).get("capability_access_packet") if isinstance(readiness.get("evidence_inputs"), dict) else None,
        "source_team_operating_packet": readiness.get("evidence_inputs", {}).get("team_operating_packet") if isinstance(readiness.get("evidence_inputs"), dict) else None,
        "source_runtime_mapping": readiness.get("evidence_inputs", {}).get("runtime_mapping") if isinstance(readiness.get("evidence_inputs"), dict) else None,
        "runtime_readiness_report_path": readiness.get("runtime_readiness_report_path") or str(run_dir / "runtime_readiness_report.json"),
        "runtime_readiness_source": readiness_source,
        "approval_evidence_path": str(approval_path),
        "runtime_invocation_report_path": str(invocation_path),
        "approval_gates_required": bool(readiness.get("approval_gates_required")),
        "required_runtime_gates": required_gates,
        "required_execution_surface": readiness.get("required_execution_surface"),
        "approved_gates": approved_gates,
        "denied_gates": denied_gates,
        "missing_gates": missing_gates,
        "exposed_capabilities": exposed_capabilities,
        "withheld_capabilities": withheld_capabilities,
        "blocking_findings": blocking_findings,
        "readiness": {
            "runtime_invocation_ready": bool(readiness.get("runtime_invocation_ready")),
            "execution_authorized": bool(readiness.get("execution_authorized")),
            "checks": readiness.get("checks", {}),
        },
        "commands": {
            "runtime_check_json": artifact_harness_lifecycle_command(config, "runtime-check", target, state["id"], emit_json=True),
            "approval_json": artifact_harness_approval_command(config, target, state["id"], emit_json=True),
            "runtime_invoke_json": artifact_harness_runtime_invoke_command(config, target, state["id"], adapter=normalized_adapter or "open-multi-agent", surface=normalized_surface or "typescript-runTasks", dry_run=True, emit_json=True),
        },
        "governance_boundary": "Runtime invocation guard is a dry-run execution-boundary check only. It does not approve capabilities, accept artifacts, invoke runtime adapters, spawn agents, run tasks, or make runtime adapters governance owners.",
        "refused": not allowed,
        "reason": reason,
    }
    dump_json(invocation_path, report)
    return (0 if allowed else 1), report, []


def render_artifact_harness_runtime_invocation_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Artifact Harness Runtime Invocation Guard",
        "",
        f"- Packet ID: `{payload.get('id')}`",
        f"- Refused: `{'true' if payload.get('refused') else 'false'}`",
        f"- Reason: `{payload.get('reason')}`",
        f"- Adapter: `{payload.get('adapter')}`",
        f"- Surface: `{payload.get('execution_surface')}`",
        f"- Dry run: `{'true' if payload.get('dry_run') else 'false'}`",
        f"- Execution performed: `{'true' if payload.get('execution_performed') else 'false'}`",
        f"- Report path: `{payload.get('runtime_invocation_report_path')}`",
        "",
    ]
    return "\n".join(lines)


def do_artifact_harness_runtime_invoke(
    config: HubConfig,
    target_arg: str,
    packet_id: str | None,
    adapter: str | None,
    surface: str | None,
    dry_run: bool,
    emit_json: bool = False,
) -> int:
    code, payload, errors = build_artifact_harness_runtime_invocation_report(config, target_arg, packet_id, adapter, surface, dry_run)
    for line in errors:
        print(line, file=sys.stderr)
    if emit_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    elif code == 0 or payload:
        print(render_artifact_harness_runtime_invocation_markdown(payload), end="")
    return code


def artifact_harness_schema_contract() -> dict[str, Any]:
    return {
        "schema_version": ARTIFACT_HARNESS_SCHEMA_VERSION,
        "command_json_schema_version": ARTIFACT_HARNESS_COMMAND_SCHEMA_VERSION,
        "artifacts": {
            "registry": ARTIFACT_HARNESS_SCHEMA_VERSION,
            "manifest": ARTIFACT_HARNESS_SCHEMA_VERSION,
            "lifecycle_status": ARTIFACT_HARNESS_SCHEMA_VERSION,
            "replay_evidence": ARTIFACT_HARNESS_SCHEMA_VERSION,
            "provenance_ledger": ARTIFACT_HARNESS_SCHEMA_VERSION,
            "runtime_readiness_report": ARTIFACT_HARNESS_SCHEMA_VERSION,
            "approval_evidence": ARTIFACT_HARNESS_SCHEMA_VERSION,
            "runtime_invocation_report": ARTIFACT_HARNESS_SCHEMA_VERSION,
            "repair_plan": ARTIFACT_HARNESS_SCHEMA_VERSION,
            "artifact_harness_command_json": ARTIFACT_HARNESS_COMMAND_SCHEMA_VERSION,
            "packet_route_command_json": ARTIFACT_HARNESS_COMMAND_SCHEMA_VERSION,
        },
        "required_packet_files": list(ARTIFACT_HARNESS_REQUIRED_PACKET_KEYS),
        "required_json_files": ["packet_manifest.json", "packet_status.json"],
        "optional_generated_reports": list(ARTIFACT_HARNESS_OPTIONAL_REPORT_KEYS),
        "schema_metadata_file": ARTIFACT_HARNESS_SCHEMA_METADATA_FILENAME,
        "policy": "policy/ARTIFACT_HARNESS_SCHEMA_V0.md",
    }


def artifact_harness_schema_metadata_payload(packet_id: str, target: Path, run_dir: Path, generated_at: str) -> dict[str, Any]:
    return {
        "schema_version": ARTIFACT_HARNESS_SCHEMA_VERSION,
        "metadata_type": "artifact_harness_schema_metadata",
        "generated_at": generated_at,
        "id": packet_id,
        "target_path": str(target),
        "run_dir": str(run_dir),
        "contract": artifact_harness_schema_contract(),
        "governance_boundary": "Schema metadata is compatibility evidence only; it does not approve capabilities, accept artifacts, execute runtimes, choose staffing, or transfer ownership.",
    }


def artifact_harness_json_schema_version(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.strip().isdigit():
        return int(value.strip())
    return None


def artifact_harness_checked_file(key: str, path: Path, *, required: bool, schema_version: int | None = None) -> dict[str, Any]:
    return {
        "key": key,
        "path": str(path),
        "exists": path.exists(),
        "required": required,
        "schema_version": schema_version,
    }


def artifact_harness_missing_field(file_key: str, field: str) -> dict[str, str]:
    return {"file": file_key, "field": field}


def artifact_harness_schema_finding(code: str, severity: str, message: str, source_path: Path | str) -> dict[str, str]:
    return {
        "code": code,
        "severity": severity,
        "message": message,
        "source_path": str(source_path),
    }


def artifact_harness_schema_commands(config: HubConfig, target: Path, packet_id: str) -> dict[str, str]:
    return {
        "schema_check_json": artifact_harness_lifecycle_command(config, "schema-check", target, packet_id, emit_json=True),
        "migrate_json": artifact_harness_lifecycle_command(config, "migrate", target, packet_id, emit_json=True),
        "resume_json": artifact_harness_lifecycle_command(config, "resume", target, packet_id, emit_json=True),
        "replay_json": artifact_harness_lifecycle_command(config, "replay", target, packet_id, emit_json=True),
        "provenance_json": artifact_harness_lifecycle_command(config, "provenance", target, packet_id, emit_json=True),
        "runtime_check_json": artifact_harness_lifecycle_command(config, "runtime-check", target, packet_id, emit_json=True),
        "approval_json": artifact_harness_approval_command(config, target, packet_id, emit_json=True),
        "runtime_invoke_json": artifact_harness_runtime_invoke_command(config, target, packet_id, adapter="open-multi-agent", surface="typescript-runTasks", dry_run=True, emit_json=True),
        "repair_plan_json": artifact_harness_repair_plan_command(config, target, packet_id, emit_json=True),
    }


def artifact_harness_schema_refusal_payload(
    config: HubConfig,
    action: str,
    state: dict[str, Any],
    reason: str | None = None,
) -> dict[str, Any]:
    packet_id = state.get("id")
    target_path = state.get("target_path")
    run_dir = state.get("run_dir")
    target = Path(target_path) if isinstance(target_path, str) and target_path else None
    commands = artifact_harness_schema_commands(config, target, str(packet_id)) if target is not None and packet_id else {}
    payload = dict(state)
    payload.update(
        {
            "command": f"artifact-harness {action}",
            "schema_version": ARTIFACT_HARNESS_COMMAND_SCHEMA_VERSION,
            "ok": False,
            "schema_contract": artifact_harness_schema_contract(),
            "current_schema_version": state.get("current_schema_version"),
            "supported_schema_version": ARTIFACT_HARNESS_SCHEMA_VERSION,
            "compatible": False,
            "migration_required": False,
            "schema_metadata_path": str(Path(run_dir) / ARTIFACT_HARNESS_SCHEMA_METADATA_FILENAME) if run_dir else state.get("schema_metadata_path"),
            "checked_files": state.get("checked_files", []),
            "missing_files": state.get("missing_files", []),
            "missing_required_fields": state.get("missing_required_fields", []),
            "warnings": state.get("warnings", []),
            "blocking_findings": state.get("blocking_findings", []),
            "changed_files": [],
            "commands": commands,
            "refused": True,
            "reason": reason or state.get("reason"),
            "governance_boundary": "Schema-check and migration are compatibility tools only. They do not approve capabilities, accept artifacts, execute runtimes, choose staffing, or transfer ownership.",
        }
    )
    return payload


def build_artifact_harness_schema_report(
    config: HubConfig,
    target_arg: str,
    packet_id: str | None,
    action: str = "schema-check",
) -> tuple[int, dict[str, Any], list[str], dict[str, Any] | None]:
    code, state, errors, manifest, status_payload = load_artifact_harness_lifecycle_state(config, action, target_arg, packet_id)
    if code != 0:
        return code, artifact_harness_schema_refusal_payload(config, action, state), errors, None

    manifest = manifest or {}
    status_payload = status_payload or {}
    target = Path(state["target_path"])
    run_dir = Path(state["run_dir"])
    registry_path = Path(state["registry_path"])
    manifest_path = Path(state["manifest"])
    status_path = Path(state["status_path"])
    schema_metadata_path = Path(state.get("schema_metadata_path") or (run_dir / ARTIFACT_HARNESS_SCHEMA_METADATA_FILENAME))
    replay_path = run_dir / "artifact_replay_evidence.json"
    provenance_path = run_dir / "packet_provenance_ledger.json"
    runtime_report_path = run_dir / "runtime_readiness_report.json"
    approval_evidence_path = run_dir / ARTIFACT_HARNESS_APPROVAL_EVIDENCE_FILENAME
    runtime_invocation_report_path = run_dir / ARTIFACT_HARNESS_RUNTIME_INVOCATION_REPORT_FILENAME
    repair_plan_path = run_dir / ARTIFACT_HARNESS_REPAIR_PLAN_FILENAME

    try:
        ensure_targets_under_root(
            target,
            {
                "schema_metadata_path": schema_metadata_path,
                "replay_evidence_path": replay_path,
                "provenance_ledger_path": provenance_path,
                "runtime_readiness_report_path": runtime_report_path,
                "approval_evidence_path": approval_evidence_path,
                "runtime_invocation_report_path": runtime_invocation_report_path,
                "repair_plan_path": repair_plan_path,
            },
        )
    except HubRuntimeError as exc:
        refused = artifact_harness_schema_refusal_payload(config, action, state, "schema_metadata_path_outside_target_workspace")
        return 1, refused, [str(exc)], None

    try:
        registry = load_artifact_harness_registry(config, registry_path)
    except HubRuntimeError as exc:
        refused = artifact_harness_schema_refusal_payload(config, action, state, "invalid_registry_json")
        return 1, refused, [str(exc)], None

    schema_metadata: dict[str, Any] = {}
    if schema_metadata_path.exists():
        try:
            schema_metadata = load_json_file_strict(schema_metadata_path, {}, "artifact harness schema metadata")
        except HubRuntimeError as exc:
            refused = artifact_harness_schema_refusal_payload(config, action, state, "invalid_schema_metadata_json")
            return 1, refused, [str(exc)], None

    optional_report_paths = {
        "replay_evidence": replay_path,
        "provenance_ledger": provenance_path,
        "runtime_readiness_report": runtime_report_path,
        "approval_evidence": approval_evidence_path,
        "runtime_invocation_report": runtime_invocation_report_path,
        "repair_plan": repair_plan_path,
    }
    optional_report_versions: dict[str, int | None] = {}
    optional_report_warnings: list[dict[str, str]] = []
    for key, path in optional_report_paths.items():
        optional_report_versions[key] = None
        if not path.exists():
            continue
        try:
            optional_payload = load_json_file_strict(path, {}, f"artifact harness {key}")
            optional_report_versions[key] = artifact_harness_json_schema_version(optional_payload.get("schema_version"))
        except HubRuntimeError as exc:
            optional_report_warnings.append(
                {
                    "code": "invalid_optional_generated_report_json",
                    "file": key,
                    "path": str(path),
                    "message": str(exc),
                }
            )

    packet_paths = {
        key: Path(state["packets"].get(key, run_dir / filename))
        for key, filename in {
            "artifact_harness_spec": "artifact_harness_spec.md",
            "hr_staffing_packet": "hr_staffing_packet.md",
            "team_operating_packet": "team_operating_packet.md",
            "capability_access_packet": "capability_access_packet.md",
            "runtime_mapping": "open_multi_agent_runtasks_mapping.md",
        }.items()
    }
    manifest_version = artifact_harness_json_schema_version(manifest.get("schema_version"))
    status_version = artifact_harness_json_schema_version(status_payload.get("schema_version"))
    registry_version = artifact_harness_json_schema_version(registry.get("schema_version"))
    metadata_version = artifact_harness_json_schema_version(schema_metadata.get("schema_version"))
    current_schema_version = metadata_version or manifest_version
    checked_files = [
        artifact_harness_checked_file(key, path, required=True)
        for key, path in packet_paths.items()
    ]
    checked_files.extend(
        [
            artifact_harness_checked_file("manifest", manifest_path, required=True, schema_version=manifest_version),
            artifact_harness_checked_file("lifecycle_status", status_path, required=True, schema_version=status_version),
            artifact_harness_checked_file("registry", registry_path, required=True, schema_version=registry_version),
            artifact_harness_checked_file("schema_metadata", schema_metadata_path, required=False, schema_version=metadata_version),
            artifact_harness_checked_file("replay_evidence", replay_path, required=False, schema_version=optional_report_versions["replay_evidence"]),
            artifact_harness_checked_file("provenance_ledger", provenance_path, required=False, schema_version=optional_report_versions["provenance_ledger"]),
            artifact_harness_checked_file("runtime_readiness_report", runtime_report_path, required=False, schema_version=optional_report_versions["runtime_readiness_report"]),
            artifact_harness_checked_file("approval_evidence", approval_evidence_path, required=False, schema_version=optional_report_versions["approval_evidence"]),
            artifact_harness_checked_file("runtime_invocation_report", runtime_invocation_report_path, required=False, schema_version=optional_report_versions["runtime_invocation_report"]),
            artifact_harness_checked_file("repair_plan", repair_plan_path, required=False, schema_version=optional_report_versions["repair_plan"]),
        ]
    )
    missing_files = [item for item in checked_files if item["required"] and not item["exists"]]
    missing_required_fields: list[dict[str, str]] = []
    for field in ("schema_version", "id", "generated_at", "mission", "target_path", "workflow", "packets", "lifecycle", "boundaries"):
        if field not in manifest:
            missing_required_fields.append(artifact_harness_missing_field("manifest", field))
    for field in ("schema_version", "id", "status", "updated_at", "updated_by", "history", "governance_boundary", "allowed_statuses"):
        if field not in status_payload:
            missing_required_fields.append(artifact_harness_missing_field("lifecycle_status", field))
    if "schema_version" not in registry:
        missing_required_fields.append(artifact_harness_missing_field("registry", "schema_version"))
    if "entries" not in registry:
        missing_required_fields.append(artifact_harness_missing_field("registry", "entries"))

    registry_entries = registry.get("entries", [])
    registry_entry = next(
        (entry for entry in registry_entries if isinstance(entry, dict) and entry.get("id") == state["id"]),
        None,
    )
    if not isinstance(registry_entry, dict):
        missing_required_fields.append(artifact_harness_missing_field("registry", f"entries[id={state['id']}]"))
    else:
        for field in ("id", "run_dir", "packets", "status", "status_path"):
            if field not in registry_entry:
                missing_required_fields.append(artifact_harness_missing_field("registry_entry", field))

    warnings: list[dict[str, str]] = list(optional_report_warnings)
    for key, path in optional_report_paths.items():
        if not path.exists():
            warnings.append(
                {
                    "code": "missing_optional_generated_report",
                    "file": key,
                    "path": str(path),
                    "message": f"Optional generated report is absent: {key}.",
                }
            )

    blocking_findings: list[dict[str, str]] = []
    for item in missing_files:
        blocking_findings.append(
            artifact_harness_schema_finding(
                "missing_required_file",
                "P1",
                f"Required Artifact Harness file is missing: {item['key']}.",
                item["path"],
            )
        )
    if not isinstance(manifest.get("packets"), dict):
        blocking_findings.append(artifact_harness_schema_finding("manifest_packets_invalid", "P1", "Manifest packets field must be an object.", manifest_path))
    for label, version, path in (
        ("manifest", manifest_version, manifest_path),
        ("lifecycle_status", status_version, status_path),
        ("registry", registry_version, registry_path),
        ("schema_metadata", metadata_version, schema_metadata_path),
        ("replay_evidence", optional_report_versions["replay_evidence"], replay_path),
        ("provenance_ledger", optional_report_versions["provenance_ledger"], provenance_path),
        ("runtime_readiness_report", optional_report_versions["runtime_readiness_report"], runtime_report_path),
        ("approval_evidence", optional_report_versions["approval_evidence"], approval_evidence_path),
        ("runtime_invocation_report", optional_report_versions["runtime_invocation_report"], runtime_invocation_report_path),
        ("repair_plan", optional_report_versions["repair_plan"], repair_plan_path),
    ):
        if version is not None and version > ARTIFACT_HARNESS_SCHEMA_VERSION:
            blocking_findings.append(
                artifact_harness_schema_finding(
                    "unsupported_schema_version",
                    "P1",
                    f"{label} schema_version={version} is newer than supported schema_version={ARTIFACT_HARNESS_SCHEMA_VERSION}.",
                    path,
                )
            )
    if manifest.get("id") not in (None, state["id"]):
        blocking_findings.append(artifact_harness_schema_finding("manifest_id_mismatch", "P1", "Manifest id does not match the requested packet id.", manifest_path))
    if status_payload.get("id") not in (None, state["id"]):
        blocking_findings.append(artifact_harness_schema_finding("status_id_mismatch", "P1", "Lifecycle status id does not match the requested packet id.", status_path))

    migration_required = False
    if not schema_metadata_path.exists() or metadata_version != ARTIFACT_HARNESS_SCHEMA_VERSION:
        migration_required = True
    if manifest_version != ARTIFACT_HARNESS_SCHEMA_VERSION or "schema_contract" not in manifest:
        migration_required = True
    if registry_version != ARTIFACT_HARNESS_SCHEMA_VERSION:
        migration_required = True
    if isinstance(registry_entry, dict) and (
        registry_entry.get("schema_version") != ARTIFACT_HARNESS_SCHEMA_VERSION
        or "schema_metadata_path" not in registry_entry
    ):
        migration_required = True

    compatible = not blocking_findings and not any(item["exists"] is False for item in missing_files)
    generated_at = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    report = {
        "command": f"artifact-harness {action}",
        "schema_version": ARTIFACT_HARNESS_COMMAND_SCHEMA_VERSION,
        "ok": compatible,
        "schema_contract": artifact_harness_schema_contract(),
        "generated_at": generated_at,
        "id": state["id"],
        "target_path": state["target_path"],
        "run_dir": state["run_dir"],
        "manifest": state["manifest"],
        "registry_path": state["registry_path"],
        "status": state["status"],
        "status_path": state["status_path"],
        "schema_metadata_path": str(schema_metadata_path),
        "current_schema_version": current_schema_version,
        "supported_schema_version": ARTIFACT_HARNESS_SCHEMA_VERSION,
        "compatible": compatible,
        "migration_required": migration_required,
        "checked_files": checked_files,
        "missing_files": missing_files,
        "missing_required_fields": missing_required_fields,
        "warnings": warnings,
        "blocking_findings": blocking_findings,
        "migration_safe": compatible and not blocking_findings,
        "changed_files": [],
        "commands": artifact_harness_schema_commands(config, target, state["id"]),
        "governance_boundary": "Schema-check and migration are compatibility tools only. They do not approve capabilities, accept artifacts, execute runtimes, choose staffing, or transfer ownership.",
        "refused": False,
        "reason": None,
    }
    context = {
        "state": state,
        "manifest": manifest,
        "status_payload": status_payload,
        "registry": registry,
        "registry_entry": registry_entry,
        "schema_metadata": schema_metadata,
        "schema_metadata_path": schema_metadata_path,
        "manifest_path": manifest_path,
        "registry_path": registry_path,
        "target": target,
        "run_dir": run_dir,
    }
    return 0, report, [], context


def render_artifact_harness_schema_markdown(payload: dict[str, Any]) -> str:
    if payload.get("refused"):
        return f"# Artifact Harness Schema\n\n- Refused: `true`\n- Reason: `{payload.get('reason')}`\n"
    lines = [
        "# Artifact Harness Schema",
        "",
        f"- Packet ID: `{payload['id']}`",
        f"- Command: `{payload['command']}`",
        f"- Compatible: `{'true' if payload['compatible'] else 'false'}`",
        f"- Migration required: `{'true' if payload['migration_required'] else 'false'}`",
        f"- Current schema version: `{payload.get('current_schema_version')}`",
        f"- Supported schema version: `{payload['supported_schema_version']}`",
        f"- Schema metadata: `{payload['schema_metadata_path']}`",
        "",
        "## Blocking Findings",
        "",
    ]
    findings = payload.get("blocking_findings", [])
    if findings:
        for finding in findings:
            lines.append(f"- `{finding.get('code')}`: {finding.get('message')}")
    else:
        lines.append("- none")
    lines.append("")
    return "\n".join(lines)


def do_artifact_harness_schema_check(config: HubConfig, target_arg: str, packet_id: str | None, emit_json: bool = False) -> int:
    code, payload, errors, _context = build_artifact_harness_schema_report(config, target_arg, packet_id, "schema-check")
    for line in errors:
        print(line, file=sys.stderr)
    if emit_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    elif code == 0:
        print(render_artifact_harness_schema_markdown(payload), end="")
    return code


def do_artifact_harness_migrate(config: HubConfig, target_arg: str, packet_id: str | None, emit_json: bool = False) -> int:
    code, payload, errors, context = build_artifact_harness_schema_report(config, target_arg, packet_id, "migrate")
    for line in errors:
        print(line, file=sys.stderr)
    if code != 0:
        if emit_json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        return code
    if not payload.get("migration_safe"):
        payload["ok"] = False
        payload["refused"] = True
        payload["reason"] = "schema_migration_blocked"
        print("Artifact Harness migration refused because required files or fields are missing.", file=sys.stderr)
        if emit_json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 1

    assert context is not None
    target = context["target"]
    run_dir = context["run_dir"]
    manifest_path = context["manifest_path"]
    registry_path = context["registry_path"]
    schema_metadata_path = context["schema_metadata_path"]
    manifest = dict(context["manifest"])
    registry = dict(context["registry"])
    generated_at = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    schema_metadata = artifact_harness_schema_metadata_payload(str(payload["id"]), target, run_dir, generated_at)
    schema_metadata_rel = relative_path_from(target, schema_metadata_path)
    changed_files: list[str] = []

    desired_schema_contract = {
        "schema_version": ARTIFACT_HARNESS_SCHEMA_VERSION,
        "schema_metadata_path": schema_metadata_rel,
        "contract_policy": "policy/ARTIFACT_HARNESS_SCHEMA_V0.md",
        "command_json_schema_version": ARTIFACT_HARNESS_COMMAND_SCHEMA_VERSION,
    }
    manifest_changed = False
    if manifest.get("schema_version") != ARTIFACT_HARNESS_SCHEMA_VERSION:
        manifest["schema_version"] = ARTIFACT_HARNESS_SCHEMA_VERSION
        manifest_changed = True
    if manifest.get("schema_contract") != desired_schema_contract:
        manifest["schema_contract"] = desired_schema_contract
        manifest_changed = True
    if manifest_changed:
        dump_json(manifest_path, manifest)
        changed_files.append(str(manifest_path))

    existing_metadata = context.get("schema_metadata") if isinstance(context.get("schema_metadata"), dict) else {}
    stable_existing_metadata = dict(existing_metadata)
    stable_existing_metadata.pop("generated_at", None)
    stable_desired_metadata = dict(schema_metadata)
    stable_desired_metadata.pop("generated_at", None)
    if stable_existing_metadata != stable_desired_metadata:
        dump_json(schema_metadata_path, schema_metadata)
        changed_files.append(str(schema_metadata_path))

    entries = []
    registry_changed = False
    found = False
    for entry in registry.get("entries", []):
        if isinstance(entry, dict) and entry.get("id") == payload["id"]:
            found = True
            updated_entry = dict(entry)
            updates = {
                "schema_version": ARTIFACT_HARNESS_SCHEMA_VERSION,
                "schema_metadata_path": schema_metadata_rel,
                "manifest_schema_version": ARTIFACT_HARNESS_SCHEMA_VERSION,
            }
            for key, value in updates.items():
                if updated_entry.get(key) != value:
                    updated_entry[key] = value
                    registry_changed = True
            entry = updated_entry
        entries.append(entry)
    if not found:
        payload["ok"] = False
        payload["refused"] = True
        payload["reason"] = "schema_migration_blocked"
        payload["blocking_findings"].append(
            artifact_harness_schema_finding(
                "missing_registry_entry",
                "P1",
                "Registry does not contain an entry for this packet id; migration is ambiguous.",
                registry_path,
            )
        )
        print("Artifact Harness migration refused because the registry entry is missing.", file=sys.stderr)
        if emit_json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 1
    if registry.get("schema_version") != ARTIFACT_HARNESS_SCHEMA_VERSION:
        registry["schema_version"] = ARTIFACT_HARNESS_SCHEMA_VERSION
        registry_changed = True
    if registry_changed:
        registry["entries"] = entries
        registry["generated_at"] = registry.get("generated_at") or generated_at
        save_artifact_harness_registry(config, registry, registry_path, target)
        changed_files.append(str(registry_path))

    # Re-check after migration so the emitted JSON reflects post-migration state.
    _post_code, post_payload, _post_errors, _post_context = build_artifact_harness_schema_report(config, target_arg, packet_id, "migrate")
    post_payload["ok"] = _post_code == 0 and bool(post_payload.get("compatible"))
    post_payload["changed_files"] = changed_files
    post_payload["migration_required"] = False if post_payload["ok"] else post_payload.get("migration_required", True)
    post_payload["refused"] = False
    post_payload["reason"] = None
    if emit_json:
        print(json.dumps(post_payload, ensure_ascii=False, indent=2))
    else:
        print(render_artifact_harness_schema_markdown(post_payload), end="")
    return 0 if post_payload["ok"] else 1


def artifact_harness_repair_item(
    code: str,
    severity: str,
    source: str,
    message: str,
    recommended_action: str,
    *,
    source_path: str | Path | None = None,
    owner_boundary: str | None = None,
    commands: dict[str, str] | None = None,
) -> dict[str, Any]:
    item: dict[str, Any] = {
        "code": code,
        "severity": severity,
        "source": source,
        "message": message,
        "recommended_action": recommended_action,
        "owner_boundary": owner_boundary or "Repair planning is advisory and does not transfer packet ownership.",
    }
    if source_path is not None:
        item["source_path"] = str(source_path)
    if commands:
        item["commands"] = commands
    return item


def artifact_harness_repair_sort_key(item: dict[str, Any]) -> tuple[int, str]:
    severity_order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
    return severity_order.get(str(item.get("severity")), 9), str(item.get("code", ""))


def artifact_harness_repair_commands(config: HubConfig, target: Path, packet_id: str) -> dict[str, str]:
    return {
        "repair_plan_json": artifact_harness_repair_plan_command(config, target, packet_id, emit_json=True),
        "status_json": artifact_harness_lifecycle_command(config, "status", target, packet_id, emit_json=True),
        "resume_json": artifact_harness_lifecycle_command(config, "resume", target, packet_id, emit_json=True),
        "schema_check_json": artifact_harness_lifecycle_command(config, "schema-check", target, packet_id, emit_json=True),
        "migrate_json": artifact_harness_lifecycle_command(config, "migrate", target, packet_id, emit_json=True),
        "replay_json": artifact_harness_lifecycle_command(config, "replay", target, packet_id, emit_json=True),
        "provenance_json": artifact_harness_lifecycle_command(config, "provenance", target, packet_id, emit_json=True),
        "runtime_check_json": artifact_harness_lifecycle_command(config, "runtime-check", target, packet_id, emit_json=True),
        "approval_json": artifact_harness_approval_command(config, target, packet_id, emit_json=True),
        "runtime_invoke_json": artifact_harness_runtime_invoke_command(config, target, packet_id, adapter="open-multi-agent", surface="typescript-runTasks", dry_run=True, emit_json=True),
        "mark_filled_json": artifact_harness_lifecycle_command(config, "mark", target, packet_id, status="filled", note="packet fields filled", emit_json=True),
        "mark_blocked_json": artifact_harness_lifecycle_command(config, "mark", target, packet_id, status="blocked", note="describe blocker", emit_json=True),
    }


def artifact_harness_repair_refusal_payload(
    config: HubConfig,
    state: dict[str, Any],
    reason: str,
) -> dict[str, Any]:
    packet_id = state.get("id")
    target_path = state.get("target_path")
    run_dir = state.get("run_dir")
    target = Path(target_path) if isinstance(target_path, str) and target_path else None
    commands = artifact_harness_repair_commands(config, target, str(packet_id)) if target is not None and packet_id else {}
    payload = dict(state)
    payload.update(
        {
            "command": "artifact-harness repair-plan",
            "schema_version": ARTIFACT_HARNESS_COMMAND_SCHEMA_VERSION,
            "report_type": "artifact_harness_repair_plan",
            "repair_plan_path": str(Path(run_dir) / ARTIFACT_HARNESS_REPAIR_PLAN_FILENAME) if run_dir else state.get("repair_plan_path"),
            "needs_repair": True,
            "ready_to_continue": False,
            "repair_items": [],
            "summary": {},
            "recommended_next_action": "Resolve the refusal before repair planning can inspect the packet run.",
            "commands": commands,
            "governance_boundary": "Repair plans are advisory evidence only. They do not rewrite packet Markdown, approve capabilities, accept artifacts, execute runtimes, or transfer ownership.",
            "refused": True,
            "reason": reason,
        }
    )
    return payload


def artifact_harness_load_optional_report(path: Path, label: str) -> tuple[dict[str, Any] | None, str | None]:
    if not path.exists():
        return None, None
    try:
        return load_json_file_strict(path, {}, label), None
    except HubRuntimeError as exc:
        return None, str(exc)


def build_artifact_harness_repair_plan(
    config: HubConfig,
    target_arg: str,
    packet_id: str | None,
) -> tuple[int, dict[str, Any], list[str]]:
    code, state, errors, manifest, status_payload = load_artifact_harness_lifecycle_state(config, "repair-plan", target_arg, packet_id)
    if code != 0:
        return code, artifact_harness_repair_refusal_payload(config, state, state.get("reason") or "repair_plan_refused"), errors

    manifest = manifest or {}
    status_payload = status_payload or {}
    target = Path(state["target_path"])
    run_dir = Path(state["run_dir"])
    repair_path = run_dir / ARTIFACT_HARNESS_REPAIR_PLAN_FILENAME
    replay_path = run_dir / "artifact_replay_evidence.json"
    provenance_path = run_dir / "packet_provenance_ledger.json"
    runtime_report_path = run_dir / "runtime_readiness_report.json"
    approval_path = run_dir / ARTIFACT_HARNESS_APPROVAL_EVIDENCE_FILENAME
    invocation_path = run_dir / ARTIFACT_HARNESS_RUNTIME_INVOCATION_REPORT_FILENAME
    try:
        ensure_targets_under_root(
            target,
            {
                "repair_plan_path": repair_path,
                "replay_evidence_path": replay_path,
                "provenance_ledger_path": provenance_path,
                "runtime_readiness_report_path": runtime_report_path,
                "approval_evidence_path": approval_path,
                "runtime_invocation_report_path": invocation_path,
            },
        )
    except HubRuntimeError as exc:
        refused = artifact_harness_repair_refusal_payload(config, state, "repair_plan_path_outside_target_workspace")
        return 1, refused, [str(exc)]

    commands = artifact_harness_repair_commands(config, target, state["id"])
    packet_paths = {
        key: Path(state["packets"].get(key, run_dir / filename))
        for key, filename in {
            "artifact_harness_spec": "artifact_harness_spec.md",
            "hr_staffing_packet": "hr_staffing_packet.md",
            "team_operating_packet": "team_operating_packet.md",
            "capability_access_packet": "capability_access_packet.md",
            "runtime_mapping": "open_multi_agent_runtasks_mapping.md",
        }.items()
    }
    packet_completion = {key: artifact_harness_packet_completion_heuristics(path) for key, path in packet_paths.items()}
    repair_items: list[dict[str, Any]] = []

    status = str(state.get("status") or "")
    if status == "blocked":
        repair_items.append(
            artifact_harness_repair_item(
                "lifecycle_blocked",
                "P1",
                "packet_status",
                f"Packet lifecycle is blocked: {state.get('status_note') or status_payload.get('note') or 'no blocker note recorded'}.",
                "Resolve the blocker in the owning packet, then mark the run filled/reviewed only after the packet evidence is updated.",
                source_path=state.get("status_path"),
                owner_boundary="Lifecycle status is continuity metadata only; repair must happen in the owning packet or artifact.",
                commands={"status_json": commands["status_json"], "mark_filled_json": commands["mark_filled_json"]},
            )
        )
    elif status in {"superseded", "archived"}:
        repair_items.append(
            artifact_harness_repair_item(
                "inactive_lifecycle_status",
                "P2",
                "packet_status",
                f"Packet lifecycle is `{status}`; do not treat this run as the active work item without an explicit decision.",
                "Inspect the replacement/current run or create a new packet id instead of repairing this one in place.",
                source_path=state.get("status_path"),
                owner_boundary="Archived or superseded runs are continuity evidence, not active execution targets.",
                commands={"status_json": commands["status_json"], "resume_json": commands["resume_json"]},
            )
        )

    for key, item in packet_completion.items():
        path = item.get("path")
        if not item.get("exists"):
            repair_items.append(
                artifact_harness_repair_item(
                    "missing_packet_file",
                    "P1",
                    key,
                    f"Required packet is missing: {key}.",
                    "Recover the missing packet from source control or create a new packet run; do not let downstream packets stand in for the missing owner.",
                    source_path=path,
                    owner_boundary=f"{key} must be repaired at its own packet boundary.",
                    commands={"schema_check_json": commands["schema_check_json"], "resume_json": commands["resume_json"]},
                )
            )
        elif int(item.get("heuristic_open_items", 0) or 0) > 0:
            repair_items.append(
                artifact_harness_repair_item(
                    "packet_open_items_detected",
                    "P2",
                    key,
                    f"`{key}` still has {item.get('heuristic_open_items')} heuristic open item(s).",
                    "Fill or explicitly resolve the open fields in this packet before advancing lifecycle or runtime checks.",
                    source_path=path,
                    owner_boundary=f"{key} owns its own unresolved fields; repair-plan does not fill them.",
                    commands={"resume_json": commands["resume_json"], "replay_json": commands["replay_json"]},
                )
            )

    schema_code, schema_report, schema_errors, _schema_context = build_artifact_harness_schema_report(config, target_arg, state["id"], "schema-check")
    if schema_code != 0:
        repair_items.append(
            artifact_harness_repair_item(
                "schema_check_refused",
                "P1",
                "schema_check",
                f"Schema-check refused: {schema_report.get('reason') or 'unknown reason'}.",
                "Resolve the schema/path refusal before using this packet run as continuity evidence.",
                source_path=schema_report.get("manifest") or state.get("manifest"),
                owner_boundary="Schema repair may update JSON compatibility surfaces only; it must not rewrite packet Markdown.",
                commands={"schema_check_json": commands["schema_check_json"]},
            )
        )
    else:
        for finding in schema_report.get("blocking_findings", []):
            repair_items.append(
                artifact_harness_repair_item(
                    str(finding.get("code") or "schema_blocking_finding"),
                    str(finding.get("severity") or "P1"),
                    "schema_check",
                    str(finding.get("message") or "Schema-check reported a blocking finding."),
                    "Resolve schema blocking findings before migration or downstream execution.",
                    source_path=finding.get("source_path") or schema_report.get("manifest"),
                    owner_boundary="Schema-check is compatibility evidence only and does not repair packet content.",
                    commands={"schema_check_json": commands["schema_check_json"], "migrate_json": commands["migrate_json"]},
                )
            )
        if schema_report.get("migration_required") and not schema_report.get("blocking_findings"):
            repair_items.append(
                artifact_harness_repair_item(
                    "schema_migration_required",
                    "P2",
                    "schema_check",
                    "Packet JSON compatibility metadata is missing or older than the current schema.",
                    "Run migrate to update only safe JSON compatibility surfaces.",
                    source_path=schema_report.get("schema_metadata_path"),
                    owner_boundary="Migration must not rewrite filled packet Markdown or change governance ownership.",
                    commands={"migrate_json": commands["migrate_json"], "schema_check_json": commands["schema_check_json"]},
                )
            )
        if schema_report.get("missing_required_fields"):
            repair_items.append(
                artifact_harness_repair_item(
                    "schema_required_fields_missing",
                    "P2",
                    "schema_check",
                    f"Schema-check reported missing required JSON fields: {len(schema_report.get('missing_required_fields', []))}.",
                    "Inspect schema-check output and migrate only if migration is safe.",
                    source_path=schema_report.get("manifest"),
                    owner_boundary="Missing JSON fields are compatibility concerns, not approval or artifact acceptance.",
                    commands={"schema_check_json": commands["schema_check_json"], "migrate_json": commands["migrate_json"]},
                )
            )

    approval_payload, approval_error = artifact_harness_load_optional_report(approval_path, "artifact harness approval evidence")
    denied_gate_records: list[dict[str, Any]] = []
    approved_gate_records: list[dict[str, Any]] = []
    if approval_error:
        repair_items.append(
            artifact_harness_repair_item(
                "invalid_approval_evidence_json",
                "P1",
                "approval_evidence",
                "Approval evidence exists but is not readable JSON.",
                "Repair or recreate approval evidence before runtime invocation; do not infer approval from lifecycle status.",
                source_path=approval_path,
                owner_boundary="Approval evidence records explicit gate decisions only and does not replace CAP ownership.",
                commands={"approval_json": commands["approval_json"]},
            )
        )
    elif approval_payload is not None:
        approved_gate_records, denied_gate_records = artifact_harness_approval_decision_lists(approval_payload)
        for record in denied_gate_records:
            gate_id = record.get("gate_id")
            repair_items.append(
                artifact_harness_repair_item(
                    "approval_gate_denied",
                    "P1",
                    "approval_evidence",
                    f"Latest approval decision denies required gate `{gate_id}`.",
                    "Revise the packet/CAP/runtime boundary or get an explicit new approval decision; do not override denial by lifecycle status.",
                    source_path=approval_path,
                    owner_boundary="CAP owns approval gates; repair-plan cannot approve or override them.",
                    commands={"approval_json": artifact_harness_approval_command(config, target, state["id"], gate_id=str(gate_id or ARTIFACT_HARNESS_RUNTIME_APPROVAL_GATE_ID), emit_json=True)},
                )
            )

    runtime_payload, runtime_error = artifact_harness_load_optional_report(runtime_report_path, "artifact harness runtime readiness report")
    if runtime_error:
        repair_items.append(
            artifact_harness_repair_item(
                "invalid_runtime_readiness_report_json",
                "P1",
                "runtime_readiness_report",
                "Runtime readiness report exists but is not readable JSON.",
                "Re-run runtime-check after repairing packet paths and CAP/runtime mapping.",
                source_path=runtime_report_path,
                owner_boundary="Runtime readiness is preflight evidence only; it does not execute adapters.",
                commands={"runtime_check_json": commands["runtime_check_json"]},
            )
        )
    elif runtime_payload is None:
        repair_items.append(
            artifact_harness_repair_item(
                "runtime_readiness_not_checked",
                "P3",
                "runtime_readiness_report",
                "No runtime readiness report exists yet.",
                "Run runtime-check before any runtime invocation planning.",
                source_path=runtime_report_path,
                owner_boundary="Runtime adapters remain execution layers and must not become governance owners.",
                commands={"runtime_check_json": commands["runtime_check_json"]},
            )
        )
    else:
        runtime_blockers = runtime_payload.get("blocking_findings", [])
        if isinstance(runtime_blockers, list):
            for finding in runtime_blockers:
                if not isinstance(finding, dict):
                    continue
                repair_items.append(
                    artifact_harness_repair_item(
                        str(finding.get("code") or "runtime_readiness_blocker"),
                        str(finding.get("severity") or "P1"),
                        "runtime_readiness_report",
                        str(finding.get("message") or "Runtime readiness has a blocking finding."),
                        "Repair CAP/runtime mapping traceability or execution surface before runtime invocation.",
                        source_path=finding.get("source_path") or runtime_report_path,
                        owner_boundary="Runtime mapping is execution wiring only and must remain traceable to CAP and TOP.",
                        commands={"runtime_check_json": commands["runtime_check_json"], "resume_json": commands["resume_json"]},
                    )
                )
        if runtime_payload.get("approval_gates_required") and approval_payload is None:
            repair_items.append(
                artifact_harness_repair_item(
                    "missing_required_approval_evidence",
                    "P2",
                    "approval_evidence",
                    "Runtime readiness requires approval gates, but no approval evidence exists.",
                    "Record explicit approval or denial for the required gate before runtime-invoke dry-run.",
                    source_path=approval_path,
                    owner_boundary="Approval evidence is explicit gate evidence only; it does not accept artifacts.",
                    commands={"approval_json": commands["approval_json"]},
                )
            )

    invocation_payload, invocation_error = artifact_harness_load_optional_report(invocation_path, "artifact harness runtime invocation report")
    if invocation_error:
        repair_items.append(
            artifact_harness_repair_item(
                "invalid_runtime_invocation_report_json",
                "P1",
                "runtime_invocation_report",
                "Runtime invocation report exists but is not readable JSON.",
                "Re-run runtime-invoke dry-run only after readiness and approvals are repaired.",
                source_path=invocation_path,
                owner_boundary="Runtime invocation reports are dry-run guard evidence only.",
                commands={"runtime_invoke_json": commands["runtime_invoke_json"]},
            )
        )
    elif invocation_payload is not None and invocation_payload.get("refused"):
        repair_items.append(
            artifact_harness_repair_item(
                "runtime_invocation_refused",
                "P2",
                "runtime_invocation_report",
                f"Latest runtime invocation guard refused: {invocation_payload.get('reason') or 'unknown reason'}.",
                "Follow the refusal reason, then re-run runtime-check and runtime-invoke dry-run.",
                source_path=invocation_path,
                owner_boundary="Invocation guard evidence does not execute runtime adapters or approve capabilities.",
                commands={"runtime_check_json": commands["runtime_check_json"], "runtime_invoke_json": commands["runtime_invoke_json"]},
            )
        )

    repair_items = sorted(repair_items, key=artifact_harness_repair_sort_key)
    severity_counts = Counter(str(item.get("severity")) for item in repair_items)
    needs_repair = bool(repair_items)
    ready_to_continue = not any(str(item.get("severity")) in {"P0", "P1", "P2"} for item in repair_items)
    recommended_next_action = (
        str(repair_items[0].get("recommended_action"))
        if repair_items
        else "No obvious repair action was detected; continue with review or verification based on lifecycle status."
    )
    generated_at = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    plan = {
        "command": "artifact-harness repair-plan",
        "schema_version": ARTIFACT_HARNESS_COMMAND_SCHEMA_VERSION,
        "report_type": "artifact_harness_repair_plan",
        "generated_at": generated_at,
        "id": state["id"],
        "mission": manifest.get("mission"),
        "target_path": state["target_path"],
        "run_dir": state["run_dir"],
        "manifest": state["manifest"],
        "registry_path": state["registry_path"],
        "status": state["status"],
        "status_note": state.get("status_note") or status_payload.get("note"),
        "repair_plan_path": str(repair_path),
        "needs_repair": needs_repair,
        "ready_to_continue": ready_to_continue,
        "recommended_next_action": recommended_next_action,
        "summary": {
            "repair_item_count": len(repair_items),
            "severity_counts": dict(severity_counts),
            "missing_packet_count": sum(1 for item in packet_completion.values() if not item.get("exists")),
            "heuristic_open_items_total": sum(int(item.get("heuristic_open_items", 0) or 0) for item in packet_completion.values()),
            "denied_gate_count": len(denied_gate_records),
            "approved_gate_count": len(approved_gate_records),
            "runtime_readiness_report_present": runtime_payload is not None,
            "approval_evidence_present": approval_payload is not None,
            "runtime_invocation_report_present": invocation_payload is not None,
        },
        "packet_completion": packet_completion,
        "repair_items": repair_items,
        "commands": commands,
        "governance_boundary": "Repair plans are advisory evidence only. They do not rewrite packet Markdown, approve capabilities, accept artifacts, execute runtimes, choose staffing, or transfer ownership between Artifact Harness, HR, Team Architect, CAP, and runtime adapters.",
        "refused": False,
        "reason": None,
    }
    dump_json(repair_path, plan)
    return 0, plan, []


def render_artifact_harness_repair_plan_markdown(payload: dict[str, Any]) -> str:
    if payload.get("refused"):
        return f"# Artifact Harness Repair Plan\n\n- Refused: `true`\n- Reason: `{payload.get('reason')}`\n"
    lines = [
        "# Artifact Harness Repair Plan",
        "",
        f"- Packet ID: `{payload.get('id')}`",
        f"- Status: `{payload.get('status')}`",
        f"- Needs repair: `{'true' if payload.get('needs_repair') else 'false'}`",
        f"- Ready to continue: `{'true' if payload.get('ready_to_continue') else 'false'}`",
        f"- Repair plan: `{payload.get('repair_plan_path')}`",
        f"- Recommended next action: {payload.get('recommended_next_action')}",
        "",
        "## Repair Items",
        "",
    ]
    repair_items = payload.get("repair_items", [])
    if repair_items:
        for item in repair_items:
            lines.append(f"- `{item.get('severity')}` `{item.get('code')}`: {item.get('recommended_action')}")
    else:
        lines.append("- none")
    lines.append("")
    return "\n".join(lines)


def do_artifact_harness_repair_plan(config: HubConfig, target_arg: str, packet_id: str | None, emit_json: bool = False) -> int:
    code, payload, errors = build_artifact_harness_repair_plan(config, target_arg, packet_id)
    for line in errors:
        print(line, file=sys.stderr)
    if emit_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    elif code == 0 or payload:
        print(render_artifact_harness_repair_plan_markdown(payload), end="")
    return code


def build_artifact_harness_packet_chain(
    config: HubConfig,
    mission: str,
    target_arg: str,
    explicit_id: str | None,
    expected_artifact: str | None,
    force: bool = False,
) -> tuple[int, dict[str, Any], list[str]]:
    mission = mission.strip()
    if not mission:
        return 1, {"created": False, "refused": True, "reason": "empty_mission"}, ["Artifact Harness mission must not be empty."]
    target = Path(target_arg).expanduser().resolve()
    if not target.exists():
        return 1, {"created": False, "refused": True, "reason": "missing_target", "target_path": str(target)}, [f"Target path does not exist: {target}"]
    if not target.is_dir():
        return 1, {"created": False, "refused": True, "reason": "target_not_directory", "target_path": str(target)}, [f"Target path must be a directory: {target}"]

    packet_id = stable_packet_id("artifact", mission, target, explicit_id)
    packet_root = artifact_harness_packet_root(config, target)
    run_dir, registry_path, packet_paths = artifact_harness_run_paths(config, target, packet_id)
    try:
        ensure_targets_under_root(target, {"run_dir": run_dir, "registry_path": registry_path, **packet_paths})
    except HubRuntimeError as exc:
        payload = artifact_harness_refusal_payload(
            packet_id,
            mission,
            target,
            run_dir,
            packet_paths,
            registry_path,
            "packet_root_outside_target_workspace",
        )
        return 1, payload, [str(exc)]
    paths = {
        "run_dir": relative_path_from(target, run_dir),
        "artifact_harness_spec": relative_path_from(target, packet_paths["artifact_harness_spec"]),
        "hr_staffing_packet": relative_path_from(target, packet_paths["hr_staffing_packet"]),
        "team_operating_packet": relative_path_from(target, packet_paths["team_operating_packet"]),
        "capability_access_packet": relative_path_from(target, packet_paths["capability_access_packet"]),
        "runtime_mapping": relative_path_from(target, packet_paths["runtime_mapping"]),
        "manifest": relative_path_from(target, packet_paths["manifest"]),
        "status": relative_path_from(target, packet_paths["status"]),
        "schema_metadata": relative_path_from(target, packet_paths["schema_metadata"]),
    }
    absolute_paths = {**packet_paths, "run_dir": run_dir}
    conflicts = existing_artifact_harness_run_conflicts(run_dir, absolute_paths)
    if conflicts and not force:
        payload = artifact_harness_refusal_payload(packet_id, mission, target, run_dir, packet_paths, registry_path, "existing_packet_run")
        errors = [
            f"Artifact Harness packet run already exists: {run_dir}",
            "Refusing to overwrite existing packet scaffolds without explicit --force/--overwrite.",
            "Use `--id <new-id>` for a separate run, or re-run with `--force` only when overwriting is intentional.",
            "Existing targets:",
            *[f"- {conflict}" for conflict in conflicts[:8]],
        ]
        return 1, payload, errors
    run_dir.mkdir(parents=True, exist_ok=True)

    generated_at = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    artifact_label = (expected_artifact or "").strip()
    quality_loop = artifact_harness_quality_loop_for_mission(mission)
    packet_payloads = {
        "artifact_harness_spec": render_artifact_harness_spec_packet(mission, target, artifact_label, paths, quality_loop),
        "hr_staffing_packet": render_hr_staffing_packet_scaffold(mission, paths),
        "team_operating_packet": render_team_operating_packet_scaffold(mission, paths, quality_loop),
        "capability_access_packet": render_capability_access_packet_scaffold(mission, paths, quality_loop),
        "runtime_mapping": render_runtime_mapping_scaffold(mission, paths, quality_loop),
    }
    for key, content in packet_payloads.items():
        packet_paths[key].write_text(content, encoding="utf-8")

    manifest = {
        "schema_version": 1,
        "id": packet_id,
        "generated_at": generated_at,
        "mission": mission,
        "target_path": str(target),
        "expected_artifact": artifact_label or None,
        "workflow": [
            "user mission",
            "Artifact Harness SPEC",
            "HR staffing",
            "Team Operating Packet",
            "Capability Access Packet",
            "runtime mapping",
            "verification/review",
        ],
        "packets": {key: paths[key] for key in ("artifact_harness_spec", "hr_staffing_packet", "team_operating_packet", "capability_access_packet", "runtime_mapping")},
        "lifecycle": {
            "status": "draft",
            "status_path": paths["status"],
            "status_updated_at": generated_at,
            "status_note": "Initial scaffold created; status is continuity metadata only.",
        },
        "boundaries": {
            "artifact_harness_spec": "rule / contract / acceptance / boundary only",
            "hr_staffing_packet": "staffing / role design only",
            "team_architect": "collaboration pattern / shared artifacts / task graph / convergence / CAP",
            "capability_access_packet": "skill / plugin / tool authorization, approval gates, runtime allowlist",
            "runtime_mapping": "execution mapping only",
        },
        "schema_contract": {
            "schema_version": ARTIFACT_HARNESS_SCHEMA_VERSION,
            "schema_metadata_path": paths["schema_metadata"],
            "contract_policy": "policy/ARTIFACT_HARNESS_SCHEMA_V0.md",
            "command_json_schema_version": ARTIFACT_HARNESS_COMMAND_SCHEMA_VERSION,
        },
        "quality_loop": quality_loop if quality_loop.get("detected") else None,
    }
    dump_json(packet_paths["manifest"], manifest)
    status_payload = artifact_harness_lifecycle_payload(
        packet_id,
        "draft",
        generated_at,
        "Initial scaffold created; status is continuity metadata only.",
        "system_hub artifact-harness",
    )
    dump_json(packet_paths["status"], status_payload)
    schema_metadata = artifact_harness_schema_metadata_payload(packet_id, target, run_dir, generated_at)
    dump_json(packet_paths["schema_metadata"], schema_metadata)

    registry = load_artifact_harness_registry(config, registry_path)
    entries = [entry for entry in registry.get("entries", []) if isinstance(entry, dict) and entry.get("id") != packet_id]
    registry_entry = {
        "id": packet_id,
        "generated_at": generated_at,
        "mission": mission,
        "target_path": str(target),
        "run_dir": paths["run_dir"],
        "packets": {**manifest["packets"], "manifest": paths["manifest"]},
        "status": "draft",
        "status_note": status_payload["note"],
        "status_path": paths["status"],
        "status_updated_at": generated_at,
        "schema_version": ARTIFACT_HARNESS_SCHEMA_VERSION,
        "schema_metadata_path": paths["schema_metadata"],
        "manifest_schema_version": ARTIFACT_HARNESS_SCHEMA_VERSION,
    }
    entries.append(registry_entry)
    registry["generated_at"] = generated_at
    registry["entries"] = entries[-50:]
    save_artifact_harness_registry(config, registry, registry_path, target)

    payload = {
        "id": packet_id,
        "generated_at": generated_at,
        "mission": mission,
        "target_path": str(target),
        "packet_root": str(packet_root),
        "run_dir": str(run_dir),
        "packets": {key: str(packet_paths[key]) for key in ("artifact_harness_spec", "hr_staffing_packet", "team_operating_packet", "capability_access_packet", "runtime_mapping")},
        "registry_path": str(registry_path),
        "manifest": str(packet_paths["manifest"]),
        "status": "draft",
        "status_path": str(packet_paths["status"]),
        "schema_version": ARTIFACT_HARNESS_COMMAND_SCHEMA_VERSION,
        "schema_metadata_path": str(packet_paths["schema_metadata"]),
        "created": True,
        "refused": False,
        "reason": None,
    }
    payload["packets"]["manifest"] = str(packet_paths["manifest"])
    return 0, payload, []


def do_artifact_harness(
    config: HubConfig,
    mission: str,
    target_arg: str,
    explicit_id: str | None,
    expected_artifact: str | None,
    force: bool = False,
    emit_json: bool = False,
) -> int:
    code, payload, errors = build_artifact_harness_packet_chain(config, mission, target_arg, explicit_id, expected_artifact, force)
    for line in errors:
        print(line, file=sys.stderr)
    if emit_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    elif code == 0:
        print(render_artifact_harness_summary(payload), end="")
    return code


def match_artifact_harness_keywords(utterance: str, keywords: list[str]) -> list[str]:
    matches: list[str] = []
    for keyword in keywords:
        normalized = " ".join(keyword.strip().split())
        if not normalized:
            continue
        phrase_pattern = r"\s+".join(re.escape(part) for part in normalized.split())
        pattern = re.compile(rf"(?<![A-Za-z0-9_]){phrase_pattern}(?![A-Za-z0-9_])", re.IGNORECASE)
        if pattern.search(utterance):
            matches.append(keyword)
    return matches


def packet_route_natural_artifact_details(utterance: str) -> dict[str, Any]:
    production_cues = match_artifact_harness_keywords(utterance, list(PACKET_ROUTE_NATURAL_PRODUCTION_CUES))
    quality_cues = match_artifact_harness_keywords(utterance, list(PACKET_ROUTE_NATURAL_QUALITY_CUES))
    process_cues = match_artifact_harness_keywords(utterance, list(PACKET_ROUTE_NATURAL_PROCESS_CUES))
    deliverables = match_artifact_harness_keywords(utterance, list(PACKET_ROUTE_NATURAL_DELIVERABLE_TERMS))
    underspecified_refs = match_artifact_harness_keywords(utterance, list(PACKET_ROUTE_UNDERSPECIFIED_ARTIFACT_REFERENCES))
    generic_deliverables = {"artifact", "deliverable", "output", "成果", "產出"}
    generic_process_cues = {"artifact", "deliverable", "output", "成果", "產出"}
    specific_deliverables = [item for item in deliverables if " ".join(item.lower().split()) not in generic_deliverables]
    specific_process_cues = [item for item in process_cues if " ".join(item.lower().split()) not in generic_process_cues]
    action_cues = production_cues + quality_cues + specific_process_cues
    create_ready = bool(specific_deliverables and action_cues)
    vague_artifact_hint = bool((underspecified_refs or deliverables) and not create_ready)
    detected = create_ready or vague_artifact_hint
    matched_terms: list[str] = []
    for group in (production_cues, quality_cues, process_cues, deliverables, underspecified_refs):
        for item in group:
            if item not in matched_terms:
                matched_terms.append(item)
    confidence = "none"
    if create_ready:
        confidence = "high" if production_cues and deliverables else "medium"
    elif vague_artifact_hint:
        confidence = "low"
    clarifying_questions = []
    if vague_artifact_hint:
        clarifying_questions = [
            "What artifact should be produced or improved?",
            "What would make the result review-ready or acceptable?",
        ]
    reason = None
    if create_ready:
        reason = "natural artifact-production intent detected from deliverable and action/quality cues"
    elif vague_artifact_hint:
        reason = "artifact reference is present but the deliverable or success criteria are underspecified"
    return {
        "detected": detected,
        "create_ready": create_ready,
        "needs_clarification": vague_artifact_hint,
        "confidence": confidence,
        "production_cues": production_cues,
        "quality_cues": quality_cues,
        "process_cues": process_cues,
        "deliverables": deliverables,
        "underspecified_refs": underspecified_refs,
        "matched_terms": matched_terms,
        "clarifying_questions": clarifying_questions,
        "reason": reason,
    }


def packet_route_roster_quality_details(utterance: str, front_doors: list[str]) -> dict[str, Any]:
    def dedupe(items: list[str]) -> list[str]:
        result: list[str] = []
        for item in items:
            if item not in result:
                result.append(item)
        return result

    quality_terms = dedupe(match_artifact_harness_keywords(utterance, list(ROSTER_QUALITY_DIRECTION_TERMS)))
    action_terms = dedupe(match_artifact_harness_keywords(utterance, list(ROSTER_QUALITY_DIRECTION_ACTION_TERMS)))
    detected = "roster" in front_doors and bool(quality_terms) and bool(action_terms)
    return {
        "detected": detected,
        "quality_terms": quality_terms,
        "action_terms": action_terms,
        "short_term_focus": [
            "current artifact or unit can be delivered",
            "content, media, and steps are internally consistent",
            "obvious omissions are caught before handoff",
        ],
        "long_term_focus": [
            "repeated issues become team or template improvements",
            "recurring checks become a stable review habit",
            "final output gets one full acceptance pass before delivery",
        ],
        "self_check_source": "Harness SPEC acceptance remains the source of truth when a packet exists.",
    }


def packet_route_visual_quality_loop_details(
    utterance: str,
    natural_details: dict[str, Any],
    quality_details: dict[str, Any],
) -> dict[str, Any]:
    def dedupe(items: list[str]) -> list[str]:
        result: list[str] = []
        for item in items:
            if item not in result:
                result.append(item)
        return result

    visual_terms = dedupe(match_artifact_harness_keywords(utterance, list(ROSTER_VISUAL_ARTIFACT_TERMS)))
    loop_terms = dedupe(match_artifact_harness_keywords(utterance, list(ROSTER_VISUAL_QUALITY_LOOP_TERMS)))
    visual_production = bool(visual_terms and natural_details.get("create_ready"))
    explicit_visual_quality = bool(visual_terms and (quality_details.get("detected") or loop_terms))
    detected = visual_production or explicit_visual_quality
    reason = None
    if visual_production:
        reason = "visual artifact production should include a bounded quality loop before delivery"
    elif explicit_visual_quality:
        reason = "visual quality request should use the Roster quality loop guidance"
    return {
        "detected": detected,
        "artifact_mode": "visual" if detected else None,
        "recommended_iterations": "2-3" if detected else None,
        "inspection_targets": list(ROSTER_CV_INSPECTION_CHECKS) if detected else [],
        "process_steps": [
            "produce initial artifact",
            "inspect visible output",
            "detect material visual defects",
            "apply focused correction",
            "repeat until no material issue remains or the bounded iteration limit is reached",
        ] if detected else [],
        "matched_visual_terms": visual_terms,
        "matched_loop_terms": loop_terms,
        "capability_boundary": "visual inspection tools require CAP authorization when used" if detected else None,
        "cv_inspection": roster_cv_inspection_request(detected),
        "reason": reason,
    }


def artifact_harness_command(
    config: HubConfig,
    entrypoint: str,
    utterance: str,
    target: Path,
    expected_artifact: str | None = None,
    force: bool = False,
    explicit_id: str | None = None,
) -> str:
    try:
        entrypoint_parts = shlex.split(entrypoint)
    except ValueError:
        entrypoint_parts = [entrypoint]
    if not entrypoint_parts:
        entrypoint_parts = ["artifact-harness"]
    first = entrypoint_parts[0]
    if first.startswith("/"):
        command_parts = entrypoint_parts
    elif first in {"./scripts/brain.sh", "scripts/brain.sh"}:
        command_parts = [str(config.scripts_dir / "brain.sh"), *entrypoint_parts[1:]]
    elif first.startswith("./"):
        command_parts = [str((config.workspace_root / first[2:]).resolve()), *entrypoint_parts[1:]]
    elif first.startswith("scripts/"):
        command_parts = [str((config.workspace_root / first).resolve()), *entrypoint_parts[1:]]
    else:
        command_parts = [str(config.scripts_dir / "brain.sh"), *entrypoint_parts]
    command_parts.extend([utterance, "--path", str(target)])
    if explicit_id and explicit_id.strip():
        command_parts.extend(["--id", explicit_id.strip()])
    artifact = (expected_artifact or "").strip()
    if artifact:
        command_parts.extend(["--artifact", artifact])
    if force:
        command_parts.append("--force")
    return " ".join(shlex.quote(part) for part in command_parts)


def packet_route_stage_for_family(family_id: str) -> str:
    return {
        "artifact_harness_workflow": "Artifact Harness SPEC",
        "team_architect_packet": "Team Operating Packet",
        "capability_access_packet": "Capability Access Packet",
        "runtime_mapping": "runtime mapping",
    }.get(family_id, family_id)


def packet_route_handoff_for_front_doors(front_doors: list[str]) -> str | None:
    if "human_resources" in front_doors:
        return "HR staffing"
    if "team_architect_packet" in front_doors:
        return "Team Operating Packet"
    if "capability_access_packet" in front_doors:
        return "Capability Access Packet"
    if "runtime_mapping" in front_doors:
        return "runtime mapping"
    return None


def packet_route_artifact_intent(utterance: str, front_doors: list[str], natural_details: dict[str, Any] | None = None) -> bool:
    text = " ".join(utterance.lower().split())
    markers = (
        "artifact",
        "requirement form",
        "packet form",
        "harness spec",
        "artifact harness",
        "methods appendix",
        "form fill",
        "artifact mission",
    )
    if any(marker in text for marker in markers):
        return True
    if natural_details is None:
        natural_details = packet_route_natural_artifact_details(utterance)
    if natural_details.get("create_ready"):
        return True
    return False


def packet_route_alias_is_leading_invocation(utterance: str, alias: str) -> bool:
    normalized = " ".join(alias.strip().split())
    if not normalized:
        return False
    phrase_pattern = r"\s+".join(re.escape(part) for part in normalized.split())
    pattern = re.compile(rf"^\s*{phrase_pattern}(?=$|[\s,;:.!?-])", re.IGNORECASE)
    return bool(pattern.search(utterance))


def packet_route_alias_has_artifact_context(utterance: str, natural_details: dict[str, Any]) -> bool:
    if natural_details.get("detected"):
        return True
    text = " ".join(utterance.lower().split())
    context_markers = (
        "artifact",
        "deliverable",
        "requirement form",
        "packet form",
        "harness spec",
        "artifact harness",
        "slide",
        "slides",
        "slide deck",
        "deck",
        "presentation",
        "appendix",
        "report",
        "manuscript",
        "paper",
        "figure",
        "table",
        "投影片",
        "簡報",
        "附錄",
        "報告",
        "圖表",
        "表格",
        "成果",
        "產出",
    )
    return any(marker in text for marker in context_markers)


def packet_route_alias_matches(utterance: str, alias_entry: dict[str, Any], natural_details: dict[str, Any]) -> list[str]:
    aliases = [item for item in alias_entry.get("aliases", []) if isinstance(item, str)]
    matches = match_artifact_harness_keywords(utterance, aliases)
    if alias_entry.get("requires_leading_invocation"):
        matches = [alias for alias in matches if packet_route_alias_is_leading_invocation(utterance, alias)]
    if alias_entry.get("requires_artifact_context") and not packet_route_alias_has_artifact_context(utterance, natural_details):
        return []
    return matches


def packet_route_alias_target(alias_entry: dict[str, Any], alias_id: str) -> str:
    target_route = alias_entry.get("target_route")
    if isinstance(target_route, str) and target_route.strip():
        return target_route.strip()
    return alias_id


def packet_route_candidate_routes(config: HubConfig, utterance: str) -> tuple[list[dict[str, Any]], list[str], list[str]]:
    routing = load_routing_section(config)
    registry = load_team_alias_registry(config, routing)
    candidate_routes: list[dict[str, Any]] = []
    recognized_front_doors: list[str] = []
    matched_keywords: list[str] = []
    downstream_keyword_norms: set[str] = set()
    natural_details = packet_route_natural_artifact_details(utterance)
    for family in registry.get("keyword_families", []):
        if not isinstance(family, dict) or family.get("id") == "artifact_harness_workflow":
            continue
        for keyword in family.get("keywords", []):
            if isinstance(keyword, str):
                downstream_keyword_norms.add(" ".join(keyword.lower().split()))

    for alias_entry in registry.get("aliases", []):
        if not isinstance(alias_entry, dict):
            continue
        alias_id = str(alias_entry.get("id", "")).strip()
        matches = packet_route_alias_matches(utterance, alias_entry, natural_details)
        if not alias_id or not matches:
            continue
        target_route = packet_route_alias_target(alias_entry, alias_id)
        workflow_stage = alias_entry.get("workflow_stage")
        if not isinstance(workflow_stage, str) or not workflow_stage.strip():
            workflow_stage = "HR staffing" if alias_id == "human_resources" else packet_route_stage_for_family(target_route)
        directly_executable = target_route == "artifact_harness_workflow"
        if target_route == "artifact_harness_workflow":
            reason = "registered alias to Artifact Harness workflow; artifact-production requests remain SPEC-first"
        else:
            reason = "registered team surface; route output is advisory and does not create packet artifacts"
        recognized_front_doors.append(alias_id)
        matched_keywords.extend(matches)
        candidate_routes.append(
            {
                "route": target_route,
                "matched_source": "alias",
                "matched_id": alias_id,
                "alias_id": alias_id,
                "matched_keywords": matches,
                "workflow_stage": workflow_stage,
                "directly_executable": directly_executable,
                "create_allowed": directly_executable,
                "reason": reason,
            }
        )

    raw_config_keywords = routing.get("artifact_harness_keywords", [])
    if isinstance(raw_config_keywords, list):
        config_matches = [
            keyword
            for keyword in match_artifact_harness_keywords(utterance, [item for item in raw_config_keywords if isinstance(item, str)])
            if " ".join(keyword.lower().split()) not in downstream_keyword_norms
        ]
        if config_matches:
            recognized_front_doors.append("artifact_harness_workflow")
            matched_keywords.extend(config_matches)
            candidate_routes.append(
                {
                    "route": "artifact_harness_workflow",
                    "matched_source": "config_keywords",
                    "matched_id": "artifact_harness_keywords",
                    "matched_keywords": config_matches,
                    "workflow_stage": "Artifact Harness SPEC",
                    "directly_executable": True,
                    "create_allowed": True,
                    "reason": "config-level Artifact Harness keyword addition",
                }
            )

    for family in registry.get("keyword_families", []):
        if not isinstance(family, dict):
            continue
        family_id = str(family.get("id", "")).strip()
        keywords = [item for item in family.get("keywords", []) if isinstance(item, str)]
        matches = match_artifact_harness_keywords(utterance, keywords)
        if not family_id or not matches:
            continue
        recognized_front_doors.append(family_id)
        matched_keywords.extend(matches)
        candidate_routes.append(
            {
                "route": family_id,
                "matched_source": "keyword_family",
                "matched_id": family_id,
                "matched_keywords": matches,
                "workflow_stage": packet_route_stage_for_family(family_id),
                "directly_executable": family_id == "artifact_harness_workflow",
                "create_allowed": family_id == "artifact_harness_workflow",
                "reason": "registered keyword family",
            }
        )

    if natural_details.get("detected") and not candidate_routes:
        recognized_front_doors.append("artifact_harness_workflow")
        matched_keywords.extend(natural_details.get("matched_terms", []))
        candidate_routes.append(
            {
                "route": "artifact_harness_workflow",
                "matched_source": "natural_artifact_intent",
                "matched_id": "natural_artifact_mission",
                "matched_keywords": natural_details.get("matched_terms", []),
                "workflow_stage": "Artifact Harness SPEC",
                "directly_executable": bool(natural_details.get("create_ready")),
                "create_allowed": bool(natural_details.get("create_ready")),
                "needs_clarification": bool(natural_details.get("needs_clarification")),
                "confidence": natural_details.get("confidence"),
                "reason": natural_details.get("reason"),
            }
        )

    seen_front_doors: set[str] = set()
    deduped_front_doors: list[str] = []
    for front_door in recognized_front_doors:
        if front_door in seen_front_doors:
            continue
        seen_front_doors.add(front_door)
        deduped_front_doors.append(front_door)

    seen_keywords: set[str] = set()
    deduped_keywords: list[str] = []
    for keyword in matched_keywords:
        normalized = " ".join(keyword.lower().split())
        if normalized in seen_keywords:
            continue
        seen_keywords.add(normalized)
        deduped_keywords.append(keyword)

    return candidate_routes, deduped_front_doors, deduped_keywords


def render_packet_route_markdown(route: dict[str, Any]) -> str:
    matched = bool(route["matched"])
    lines = [
        "# Packet Route",
        "",
        f"- Utterance: {route['utterance']}",
        f"- Target path: `{route['target_path']}`",
        f"- Matched: `{'true' if matched else 'false'}`",
        f"- Route: `{route['route']}`",
        f"- Recommended route: `{route.get('recommended_route')}`",
        f"- Create requested: `{'true' if route['create'] else 'false'}`",
        f"- Force requested: `{'true' if route['force'] else 'false'}`",
        f"- Create allowed: `{'true' if route.get('create_allowed') else 'false'}`",
        f"- Chain start: `{route.get('chain_start')}`",
        "",
        "## Next Step",
        "",
        f"- {route.get('next_step_label')}: {route.get('user_message')}",
        f"- Action: {route.get('visible_next_action')}",
        f"- Intent: `{route.get('user_intent')}`",
        f"- Confidence: `{route.get('confidence')}`",
        f"- Needs clarification: `{'true' if route.get('needs_clarification') else 'false'}`",
        "",
    ]
    if route.get("clarifying_questions"):
        lines.extend(["## Clarifying Questions", ""])
        lines.extend(f"- {question}" for question in route["clarifying_questions"])
        lines.append("")
    lines.extend(
        [
            "## Recognized Front Doors",
            "",
        ]
    )
    if route.get("recognized_front_doors"):
        lines.extend(f"- `{front_door}`" for front_door in route["recognized_front_doors"])
    else:
        lines.append("- none")
    lines.extend(["", "## Matched Keywords", ""])
    if route["matched_keywords"]:
        lines.extend(f"- `{keyword}`" for keyword in route["matched_keywords"])
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "## Candidate Routes",
            "",
        ]
    )
    if route.get("candidate_routes"):
        for candidate in route["candidate_routes"]:
            lines.append(f"- `{candidate['route']}` -> `{candidate.get('workflow_stage')}`: {candidate.get('reason')}")
    else:
        lines.append("- none")
    preferences = route.get("roster_preferences") or {}
    active_preferences = preferences.get("active") if isinstance(preferences, dict) else []
    if active_preferences:
        lines.extend(["", "## Roster Preferences", ""])
        for entry in active_preferences:
            lines.append(f"- `{entry.get('id')}` ({entry.get('category')}): {entry.get('preference')}")
        lines.append(f"- Write policy: `{preferences.get('write_policy')}`")
    lines.extend(
        [
            "",
            "## Boundaries",
            "",
            "- Routing is advisory unless `--create` writes an Artifact Harness packet chain.",
            "- Route output does not approve capabilities, execute runtime adapters, accept artifacts, or move ownership across HR, Team Architect, CAP, and runtime adapter boundaries.",
            "",
            "## Next Actions",
            "",
        ]
    )
    if matched and route.get("recommended_command"):
        lines.append(f"- `{route['recommended_command']}`")
        if route.get("recommended_route") == "artifact_harness_workflow" and route.get("create_allowed") and not route["create"]:
            lines.append("- Re-run this command with `--create` to write the task forms.")
    elif matched:
        lines.append("- No direct command is emitted for this front door; inspect the candidate route and hand off through the registered team surface.")
    else:
        lines.append("- No registered front door matched; continue with ordinary intake, skill routing, or an explicit artifact-harness command.")
    if route.get("refused"):
        lines.append(f"- Refused: `{route.get('reason')}`")
    lines.append("")
    return "\n".join(lines)


def packet_route_existing_run_command(config: HubConfig, route_id: str, target: Path, packet_id: str) -> tuple[str, str | None]:
    if route_id == "runtime_mapping":
        return "runtime-check", artifact_harness_lifecycle_command(config, "runtime-check", target, packet_id, emit_json=True)
    return "resume", artifact_harness_lifecycle_command(config, "resume", target, packet_id, emit_json=True)


def do_packet_route(
    config: HubConfig,
    utterance: str,
    target_arg: str,
    explicit_id: str | None,
    create: bool,
    expected_artifact: str | None,
    force: bool = False,
    emit_json: bool = False,
) -> int:
    utterance = utterance.strip()
    if not utterance:
        print("Packet route utterance must not be empty.", file=sys.stderr)
        if emit_json:
            print(json.dumps({"utterance": utterance, "target_path": None, "matched": False, "route": "none", "recognized_front_doors": [], "matched_keywords": [], "candidate_routes": [], "recommended_route": "none", "recommended_command": None, "command": None, "create": create, "force": force, "refused": True, "reason": "empty_utterance"}, ensure_ascii=False, indent=2))
        return 1
    target = Path(target_arg).expanduser().resolve()
    if not target.exists():
        print(f"Target path does not exist: {target}", file=sys.stderr)
        if emit_json:
            print(json.dumps({"utterance": utterance, "target_path": str(target), "matched": False, "route": "none", "recognized_front_doors": [], "matched_keywords": [], "candidate_routes": [], "recommended_route": "none", "recommended_command": None, "command": None, "create": create, "force": force, "refused": True, "reason": "missing_target"}, ensure_ascii=False, indent=2))
        return 1
    if not target.is_dir():
        print(f"Target path must be a directory: {target}", file=sys.stderr)
        if emit_json:
            print(json.dumps({"utterance": utterance, "target_path": str(target), "matched": False, "route": "none", "recognized_front_doors": [], "matched_keywords": [], "candidate_routes": [], "recommended_route": "none", "recommended_command": None, "command": None, "create": create, "force": force, "refused": True, "reason": "target_not_directory"}, ensure_ascii=False, indent=2))
        return 1

    preferences = roster_preferences_summary(target)
    entrypoint = artifact_harness_entrypoint(config)
    candidate_routes, recognized_front_doors, matched_keywords = packet_route_candidate_routes(config, utterance)
    matched = bool(candidate_routes)
    natural_details = packet_route_natural_artifact_details(utterance)
    quality_details = packet_route_roster_quality_details(utterance, recognized_front_doors)
    quality_loop = packet_route_visual_quality_loop_details(utterance, natural_details, quality_details)
    artifact_intent = packet_route_artifact_intent(utterance, recognized_front_doors, natural_details)
    roster_quality_direction_detected = bool(
        quality_details.get("detected")
        or (quality_loop.get("detected") and "roster" in recognized_front_doors and not artifact_intent)
    )
    downstream_front_doors = [front_door for front_door in recognized_front_doors if front_door in {"team_architect_packet", "capability_access_packet", "runtime_mapping"}]
    packet_id = explicit_id.strip() if isinstance(explicit_id, str) and explicit_id.strip() else None
    recommended_route = "none"
    recommended_command: str | None = None
    command_action: str | None = None
    create_allowed = False
    chain_start: str | None = None
    handoff_target: str | None = None
    reason: str | None = None
    existing_run_found = False
    natural_only_match = matched and all(candidate.get("matched_source") == "natural_artifact_intent" for candidate in candidate_routes)
    needs_clarification = bool(natural_details.get("needs_clarification") and natural_only_match)
    clarifying_questions = list(natural_details.get("clarifying_questions", [])) if needs_clarification else []
    user_intent = "ordinary"
    confidence = natural_details.get("confidence") if natural_details.get("detected") else "none"

    if matched:
        if packet_id and downstream_front_doors:
            code, state, _errors, _manifest, _status = load_artifact_harness_lifecycle_state(config, "resume", str(target), packet_id)
            existing_run_found = code == 0
            if existing_run_found:
                route_id = downstream_front_doors[0]
                recommended_route = route_id
                command_action, recommended_command = packet_route_existing_run_command(config, route_id, target, packet_id)
                create_allowed = False
                chain_start = "existing packet run"
                handoff_target = packet_route_stage_for_family(route_id)
                reason = "existing packet run found; route to safe inspection command without creating downstream-only packets"
            else:
                recommended_route = "artifact_harness_workflow"
                recommended_command = artifact_harness_command(config, entrypoint, utterance, target, expected_artifact, force, packet_id)
                create_allowed = False
                chain_start = "Artifact Harness SPEC"
                handoff_target = packet_route_handoff_for_front_doors(downstream_front_doors)
                reason = "packet id was supplied but no existing run was found; do not bypass missing upstream packets"
        elif artifact_intent:
            recommended_route = "artifact_harness_workflow"
            recommended_command = None if needs_clarification else artifact_harness_command(config, entrypoint, utterance, target, expected_artifact, force, packet_id)
            create_allowed = not needs_clarification
            chain_start = "Artifact Harness SPEC"
            handoff_target = packet_route_handoff_for_front_doors(recognized_front_doors)
            reason = "artifact-production intent uses the SPEC-first Artifact Harness workflow" if create_allowed else "artifact request needs clarification before packet creation"
        elif roster_quality_direction_detected:
            recommended_route = "roster_quality_direction"
            recommended_command = None
            create_allowed = False
            chain_start = None
            handoff_target = None
            reason = "Roster Quality direction request; answer directly with short-term and long-term self-check guidance"
        elif "human_resources" in recognized_front_doors:
            recommended_route = "human_resources"
            recommended_command = None
            create_allowed = False
            chain_start = None
            handoff_target = "HR staffing"
            reason = "HR-only staffing or role-design request; do not create Artifact Harness packets"
        elif downstream_front_doors:
            recommended_route = "artifact_harness_workflow"
            recommended_command = None
            create_allowed = False
            chain_start = "Artifact Harness SPEC"
            handoff_target = packet_route_handoff_for_front_doors(downstream_front_doors)
            reason = "downstream packet request needs an artifact mission or --id for an existing run before creation"
        elif natural_details.get("needs_clarification") and "artifact_harness_workflow" in recognized_front_doors:
            recommended_route = "artifact_harness_workflow"
            recommended_command = None
            create_allowed = False
            chain_start = "Artifact Harness SPEC"
            handoff_target = None
            reason = "artifact reference is too underspecified to create a packet chain"
        else:
            recommended_route = candidate_routes[0]["route"]
            reason = "registered front door matched"

    if recommended_route == "artifact_harness_workflow" and (artifact_intent or natural_details.get("detected")):
        user_intent = "artifact_production" if not needs_clarification else "artifact_hint"
        if confidence == "none":
            confidence = "medium"
    elif recommended_route == "human_resources":
        user_intent = "hr_staffing"
        confidence = "high"
    elif recommended_route in {"team_architect_packet", "capability_access_packet", "runtime_mapping"} or downstream_front_doors:
        user_intent = "downstream_packet_reference"
        confidence = "medium"
    elif recommended_route == "roster_quality_direction":
        user_intent = "quality_direction"
        confidence = "high"
    elif not matched:
        user_intent = "ordinary"
        confidence = "none"

    if needs_clarification:
        next_step_label = "Clarify artifact task"
        user_message = "This sounds like an artifact task, but it is too underspecified to create packets yet."
        visible_next_action = "State the deliverable and what would make it review-ready or acceptable."
    elif recommended_route == "artifact_harness_workflow" and create_allowed:
        next_step_label = "Start task forms"
        user_message = "This looks like a concrete artifact task. I can set up the quality, staffing, capability, and runtime-boundary forms in this workspace."
        visible_next_action = "Run the recommended command with `--create` to write the forms."
    elif recommended_route == "human_resources":
        next_step_label = "Use HR staffing surface"
        user_message = "This looks like a staffing or role-design question, not a full artifact-production packet run."
        visible_next_action = "Use the HR team surface directly; do not create Artifact Harness packets."
    elif recommended_route == "roster_quality_direction":
        next_step_label = "Set Quality direction"
        user_message = "This is a Quality direction question. Answer with short-term delivery checks first, then long-term workflow improvements."
        visible_next_action = "Separate this-task fixes from reusable team, process, or template improvements."
    elif downstream_front_doors:
        next_step_label = "Inspect or start upstream packet chain"
        user_message = "This names a downstream packet surface. Use an existing packet id for inspection, or start from the artifact task first."
        visible_next_action = "Provide `--id <packet-id>` for an existing run, or restate the artifact mission."
    elif matched:
        next_step_label = "Inspect matched front door"
        user_message = "A registered front door matched, but no packet-chain creation path is available from this phrase."
        visible_next_action = "Inspect the candidate route before creating anything."
    else:
        next_step_label = "Ordinary intake"
        user_message = "No registered artifact or team front door matched this phrase."
        visible_next_action = "Continue normally, or use an explicit Artifact Harness command if this is an artifact-production task."

    route = {
        "utterance": utterance,
        "target_path": str(target),
        "matched": matched,
        "route": recommended_route,
        "recognized_front_doors": recognized_front_doors,
        "matched_keywords": matched_keywords,
        "candidate_routes": candidate_routes,
        "recommended_route": recommended_route,
        "recommended_command": recommended_command,
        "command": recommended_command,
        "command_action": command_action,
        "packet_id": packet_id,
        "existing_run_found": existing_run_found,
        "chain_start": chain_start,
        "handoff_target": handoff_target,
        "create_allowed": create_allowed,
        "user_intent": user_intent,
        "confidence": confidence,
        "needs_clarification": needs_clarification,
        "clarifying_questions": clarifying_questions,
        "natural_triggers": {
            "production_cues": natural_details.get("production_cues", []),
            "quality_cues": natural_details.get("quality_cues", []),
            "process_cues": natural_details.get("process_cues", []),
            "deliverables": natural_details.get("deliverables", []),
            "underspecified_refs": natural_details.get("underspecified_refs", []),
        },
        "quality_direction": quality_details,
        "quality_loop": quality_loop,
        "roster_preferences": preferences,
        "next_step_label": next_step_label,
        "user_message": user_message,
        "visible_next_action": visible_next_action,
        "create": create,
        "force": force,
        "refused": False,
        "reason": reason,
        "boundaries": {
            "routing": "advisory unless --create writes an Artifact Harness packet chain",
            "human_resources": "staffing and role design only",
            "team_architect": "collaboration pattern, shared artifacts, task graph, convergence, and CAP generation",
            "capability_access_packet": "skill/plugin/tool authorization, approval gates, and runtime allowlist only",
            "runtime_mapping": "execution mapping only; no runtime execution or governance ownership",
        },
    }
    code = 0
    if create and (not matched or recommended_route != "artifact_harness_workflow" or not create_allowed):
        code = 1
        route["refused"] = True
        route["reason"] = "needs_clarification" if route.get("needs_clarification") else ("create_not_allowed_for_recommended_route" if matched else "no_registered_front_door")
        if route.get("needs_clarification"):
            print("Packet route refused --create because the artifact request needs clarification before packet creation.", file=sys.stderr)
        else:
            print("Packet route refused --create because the recommended route is not an Artifact Harness packet-chain creation path.", file=sys.stderr)
    elif matched and create:
        code, artifact_payload, errors = build_artifact_harness_packet_chain(config, utterance, str(target), packet_id, expected_artifact, force)
        route["artifact_harness"] = artifact_payload
        for line in errors:
            print(line, file=sys.stderr)
        if code != 0:
            route["refused"] = True
            route["reason"] = artifact_payload.get("reason")
    if emit_json:
        print(json.dumps(route, ensure_ascii=False, indent=2))
    else:
        print(render_packet_route_markdown(route), end="")
        if matched and create and code == 0 and route.get("artifact_harness"):
            print()
            print(render_artifact_harness_summary(route["artifact_harness"]), end="")
    return code


def roster_skills_root(codex_home_arg: str | None = None, skills_root_arg: str | None = None) -> Path:
    if isinstance(skills_root_arg, str) and skills_root_arg.strip():
        return Path(skills_root_arg).expanduser().resolve()
    codex_home = (codex_home_arg or os.getenv("CODEX_HOME") or "~/.codex").strip()
    return Path(codex_home).expanduser().resolve() / "skills"


def roster_skill_path(codex_home_arg: str | None = None, skills_root_arg: str | None = None) -> Path:
    return roster_skills_root(codex_home_arg, skills_root_arg) / ROSTER_SKILL_NAME


def roster_skill_manifest_path(skill_path: Path) -> Path:
    return skill_path / "references" / "install_manifest.json"


def build_roster_install_manifest(config: HubConfig, skill_path: Path) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "installed_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "skill_name": ROSTER_SKILL_NAME,
        "skill_path": str(skill_path),
        "kit_root": str(config.workspace_root),
        "brain_command": str(config.scripts_dir / "brain.sh"),
        "current_user_invocation": ROSTER_CURRENT_USER_INVOCATION,
        "future_product_target": ROSTER_PRODUCT_TARGET,
        "verified_invocation_mechanism": "codex_skill_plus_repo_adapter",
        "repo_adapter": ROSTER_VERIFIED_INVOCATION_MECHANISM,
        "at_roster_status": "product_target_unverified_as_installed_codex_mention",
        "no_persistent_server_required": True,
    }


def roster_skill_install_check(codex_home_arg: str | None = None, skills_root_arg: str | None = None, *, requested: bool = False) -> dict[str, Any]:
    skills_root = roster_skills_root(codex_home_arg, skills_root_arg)
    skill_path = skills_root / ROSTER_SKILL_NAME
    skill_md = skill_path / "SKILL.md"
    manifest_path = roster_skill_manifest_path(skill_path)
    skill_exists = skill_path.is_dir()
    skill_md_exists = skill_md.is_file()
    manifest_exists = manifest_path.is_file()
    status = "installed" if skill_exists and skill_md_exists else ("missing" if requested else "not_checked")
    reason = None
    if requested and not skill_exists:
        reason = "skill_not_installed"
    elif requested and not skill_md_exists:
        reason = "skill_md_missing"
    manifest: dict[str, Any] | None = None
    if manifest_exists:
        try:
            parsed = json.loads(manifest_path.read_text(encoding="utf-8"))
            if isinstance(parsed, dict):
                manifest = parsed
        except json.JSONDecodeError:
            reason = "install_manifest_invalid_json"
            if status == "installed":
                status = "installed_manifest_invalid"
    return {
        "status": status,
        "requested": requested,
        "skill_name": ROSTER_SKILL_NAME,
        "skills_root": str(skills_root),
        "skill_path": str(skill_path),
        "skill_md": str(skill_md),
        "skill_exists": skill_exists,
        "skill_md_exists": skill_md_exists,
        "install_manifest_path": str(manifest_path),
        "install_manifest_exists": manifest_exists,
        "install_manifest": manifest,
        "current_user_invocation": ROSTER_CURRENT_USER_INVOCATION,
        "future_product_target": ROSTER_PRODUCT_TARGET,
        "reason": reason,
    }


def build_roster_install_result(config: HubConfig, codex_home_arg: str | None = None, skills_root_arg: str | None = None, force: bool = False) -> tuple[int, dict[str, Any], list[str]]:
    skills_root = roster_skills_root(codex_home_arg, skills_root_arg)
    skill_path = skills_root / ROSTER_SKILL_NAME
    payload_base = {
        "schema_version": 1,
        "report_type": "roster_skill_install",
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "skill_name": ROSTER_SKILL_NAME,
        "kit_root": str(config.workspace_root),
        "source_skill_path": str(ROSTER_SKILL_SOURCE_DIR),
        "skills_root": str(skills_root),
        "skill_path": str(skill_path),
        "current_user_invocation": ROSTER_CURRENT_USER_INVOCATION,
        "future_product_target": ROSTER_PRODUCT_TARGET,
        "verified_invocation_mechanism": "codex_skill_plus_repo_adapter",
        "next_human_command": "Start a new Codex thread and type `Roster, <your artifact task>`.",
        "at_roster_status": "product_target_unverified_as_installed_codex_mention",
        "server_required": False,
        "daemon_required": False,
        "database_required": False,
        "separate_ui_required": False,
    }
    if not ROSTER_SKILL_SOURCE_DIR.is_dir() or not (ROSTER_SKILL_SOURCE_DIR / "SKILL.md").is_file():
        return 1, {**payload_base, "installed": False, "refused": True, "reason": "missing_roster_skill_source"}, [f"Roster skill source is missing: {ROSTER_SKILL_SOURCE_DIR}"]
    if skill_path.exists() and not force:
        return 1, {
            **payload_base,
            "installed": False,
            "refused": True,
            "reason": "existing_roster_skill",
            "installed_skill": roster_skill_install_check(codex_home_arg, skills_root_arg, requested=True),
        }, [f"Roster skill already exists: {skill_path}; use --force to overwrite."]
    skills_root.mkdir(parents=True, exist_ok=True)
    if skill_path.exists():
        if skill_path.is_dir():
            shutil.rmtree(skill_path)
        else:
            skill_path.unlink()
    shutil.copytree(ROSTER_SKILL_SOURCE_DIR, skill_path)
    manifest_path = roster_skill_manifest_path(skill_path)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(build_roster_install_manifest(config, skill_path), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0, {
        **payload_base,
        "installed": True,
        "refused": False,
        "reason": None,
        "installed_skill": roster_skill_install_check(codex_home_arg, skills_root_arg, requested=True),
    }, []


def render_roster_install_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Roster Skill Install",
        "",
        f"- Installed: `{payload.get('installed')}`",
        f"- Refused: `{payload.get('refused')}`",
        f"- Skill path: `{payload.get('skill_path')}`",
        f"- Current invocation: `{payload.get('current_user_invocation')}`",
        f"- Future target: `{payload.get('future_product_target')}`",
        "",
        "## Next",
        "",
        str(payload.get("next_human_command") or "Start a new Codex thread and type `Roster, <task>`."),
        "",
        "`@roster` is not verified as an installed Codex mention.",
        "",
    ]
    if payload.get("reason"):
        lines.extend(["## Reason", "", f"- `{payload.get('reason')}`", ""])
    return "\n".join(lines)


def do_roster_install(config: HubConfig, codex_home: str | None, skills_root: str | None, force: bool = False, emit_json: bool = False) -> int:
    code, payload, errors = build_roster_install_result(config, codex_home, skills_root, force)
    for line in errors:
        print(line, file=sys.stderr)
    if emit_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(render_roster_install_markdown(payload), end="")
    return code


def roster_provider_auth_env(provider: str | None, auth_env: str | None) -> str | None:
    if isinstance(auth_env, str) and auth_env.strip():
        return auth_env.strip()
    if not isinstance(provider, str) or not provider.strip():
        return None
    normalized = re.sub(r"[^a-z0-9]+", "-", provider.strip().lower()).strip("-")
    return ROSTER_PROVIDER_AUTH_ENV_DEFAULTS.get(normalized)


def build_roster_provider_check(provider_arg: str | None, auth_env_arg: str | None) -> dict[str, Any]:
    provider = (provider_arg or os.getenv("ROSTER_LLM_PROVIDER") or "").strip()
    auth_env = roster_provider_auth_env(provider, auth_env_arg)
    if not provider:
        return {
            "status": "missing_provider",
            "diagnostic_code": "missing_provider",
            "provider": None,
            "auth_env_var": auth_env,
            "auth_env_present": False,
            "remote_call_attempted": False,
            "verification_method": "local_configuration_only",
            "message": "Set --provider or ROSTER_LLM_PROVIDER, then provide local credentials for that provider.",
            "secret_material": "not_read_or_reported",
        }
    if not auth_env:
        return {
            "status": "missing_auth",
            "diagnostic_code": "missing_auth_env_mapping",
            "provider": provider,
            "auth_env_var": None,
            "auth_env_present": False,
            "remote_call_attempted": False,
            "verification_method": "local_configuration_only",
            "message": "Provider was specified, but no auth environment variable is known; pass --auth-env for this machine.",
            "secret_material": "not_read_or_reported",
        }
    auth_present = bool(os.getenv(auth_env))
    if not auth_present:
        return {
            "status": "missing_auth",
            "diagnostic_code": "missing_auth",
            "provider": provider,
            "auth_env_var": auth_env,
            "auth_env_present": False,
            "remote_call_attempted": False,
            "verification_method": "local_configuration_only",
            "message": f"Set {auth_env} in the local environment or use Codex login/provider auth before relying on LLM-dependent paths.",
            "secret_material": "not_read_or_reported",
        }
    return {
        "status": "configured",
        "diagnostic_code": "auth_env_present_remote_call_not_attempted",
        "provider": provider,
        "auth_env_var": auth_env,
        "auth_env_present": True,
        "remote_call_attempted": False,
        "verification_method": "local_environment_presence",
        "message": "Provider credential variable is present locally; the health check does not print secrets or make a remote model call.",
        "secret_material": "not_read_or_reported",
    }


def build_roster_cv_capability_check(cv_provider_arg: str | None, cv_auth_env_arg: str | None) -> dict[str, Any]:
    explicit_check_requested = bool((cv_provider_arg or "").strip() or (cv_auth_env_arg or "").strip())
    provider = (cv_provider_arg or os.getenv("ROSTER_CV_PROVIDER") or "").strip()
    auth_env = (cv_auth_env_arg or os.getenv("ROSTER_CV_AUTH_ENV") or roster_provider_auth_env(provider, None) or "").strip()
    source = "none"
    if (cv_provider_arg or "").strip() or (cv_auth_env_arg or "").strip():
        source = "cli_args"
    elif os.getenv("ROSTER_CV_PROVIDER") or os.getenv("ROSTER_CV_AUTH_ENV"):
        source = "environment"

    base = {
        "supported_local_input_modes": list(ROSTER_CV_INSPECTION_SUPPORTED_LOCAL_INPUT_MODES),
        "supported_checks": list(ROSTER_CV_INSPECTION_CHECKS),
        "capability_requests": list(ROSTER_CV_INSPECTION_CAPABILITY_REQUESTS),
        "activation_ladder": roster_cv_activation_ladder(),
        "visual_evidence_acquisition": {
            "status": "available_as_capability_plan",
            "modes": list(ROSTER_CV_VISUAL_EVIDENCE_ACQUISITION),
            "capability_owner": "Capability Access Packet",
        },
        "user_evidence_fallback": {
            "status": "last_fallback",
            "requested_only_after": "existing evidence, local render/export, local capture/playback, and OCR/vision review are unavailable or unauthorized",
            "accepted_inputs": ["screenshot", "frame", "rendered image"],
        },
        "no_visual_evidence_policy": ROSTER_CV_NO_VISUAL_EVIDENCE_POLICY,
        "evidence_required_for_visual_acceptance": True,
        "finding_shape": dict(ROSTER_CV_FINDING_SHAPE),
        "authorization_owner": "Capability Access Packet",
        "execution_boundary": "local-only diagnostic; no remote calls; advisory until CAP authorizes tools",
        "remote_call_attempted": False,
        "verification_method": "local_configuration_only",
        "secret_material": "not_read_or_reported",
        "explicit_check_requested": explicit_check_requested,
        "default_health_blocked": False,
        "configuration_source": source,
    }
    if not provider:
        return {
            **base,
            "status": "not_configured",
            "diagnostic_code": "cv_provider_not_configured",
            "provider": None,
            "auth_env_var": auth_env or None,
            "auth_env_present": False,
            "health_blocking": explicit_check_requested,
            "message": "CV inspection is available as a local capability request; set --cv-provider or ROSTER_CV_PROVIDER to check provider auth.",
        }
    if not auth_env:
        return {
            **base,
            "status": "missing_auth",
            "diagnostic_code": "cv_auth_env_mapping_missing",
            "provider": provider,
            "auth_env_var": None,
            "auth_env_present": False,
            "health_blocking": explicit_check_requested,
            "message": "CV provider was specified, but no auth environment variable is known; pass --cv-auth-env for this machine.",
        }
    auth_present = bool(os.getenv(auth_env))
    if not auth_present:
        return {
            **base,
            "status": "missing_auth",
            "diagnostic_code": "cv_auth_missing",
            "provider": provider,
            "auth_env_var": auth_env,
            "auth_env_present": False,
            "health_blocking": explicit_check_requested,
            "message": f"Set {auth_env} in the local environment before relying on CV/vision provider inspection.",
        }
    return {
        **base,
        "status": "configured",
        "diagnostic_code": "cv_auth_env_present_remote_call_not_attempted",
        "provider": provider,
        "auth_env_var": auth_env,
        "auth_env_present": True,
        "health_blocking": False,
        "message": "CV provider credential variable is present locally; the health check does not print secrets or make a remote vision call.",
    }


def roster_health_route_command(config: HubConfig, utterance: str, target: Path, *, create: bool = False, packet_id: str | None = None) -> list[str]:
    command = [
        "bash",
        str(config.scripts_dir / "brain.sh"),
        "--config",
        str(config.config_path),
        "packet-route",
        utterance,
        "--path",
        str(target),
        "--json",
    ]
    if create:
        command.append("--create")
    if packet_id:
        command.extend(["--id", packet_id])
    return command


def run_roster_health_route(config: HubConfig, utterance: str, target: Path, *, create: bool = False, packet_id: str | None = None) -> dict[str, Any]:
    command = roster_health_route_command(config, utterance, target, create=create, packet_id=packet_id)
    proc = subprocess.run(
        command,
        cwd=config.workspace_root,
        text=True,
        capture_output=True,
        check=False,
        env=os.environ.copy(),
    )
    payload: dict[str, Any] | None = None
    parse_error = None
    if proc.stdout.strip():
        try:
            parsed = json.loads(proc.stdout)
            if isinstance(parsed, dict):
                payload = parsed
            else:
                parse_error = "stdout_json_not_object"
        except json.JSONDecodeError as exc:
            parse_error = f"invalid_json_stdout: {exc}"
    else:
        parse_error = "empty_stdout"
    return {
        "command": " ".join(shlex.quote(part) for part in command),
        "returncode": proc.returncode,
        "payload": payload,
        "stdout_parse_error": parse_error,
        "stderr": proc.stderr.strip(),
    }


def path_is_under(root: Path, path_value: str | None) -> bool:
    if not path_value:
        return False
    try:
        Path(path_value).expanduser().resolve().relative_to(root.resolve())
        return True
    except (OSError, ValueError):
        return False


def roster_packet_output_check(target: Path, route_result: dict[str, Any]) -> dict[str, Any]:
    payload = route_result.get("payload") if isinstance(route_result.get("payload"), dict) else {}
    artifact_payload = payload.get("artifact_harness") if isinstance(payload.get("artifact_harness"), dict) else {}
    packets = artifact_payload.get("packets") if isinstance(artifact_payload.get("packets"), dict) else {}
    paths_to_check = [
        artifact_payload.get("run_dir"),
        artifact_payload.get("registry_path"),
        artifact_payload.get("manifest"),
        artifact_payload.get("status_path"),
        *packets.values(),
    ]
    under_target = all(path_is_under(target, str(path)) for path in paths_to_check if path)
    expected_paths_exist = all(Path(str(path)).exists() for path in paths_to_check if path)
    created = bool(artifact_payload.get("created") is True and artifact_payload.get("refused") is False)
    status = "success" if route_result.get("returncode") == 0 and created and under_target and expected_paths_exist else "failed"
    reason = None
    if status != "success":
        reason = artifact_payload.get("reason") or payload.get("reason") or route_result.get("stdout_parse_error") or "packet_output_check_failed"
    return {
        "status": status,
        "packet_id": artifact_payload.get("id"),
        "target_path": str(target),
        "run_dir": artifact_payload.get("run_dir"),
        "registry_path": artifact_payload.get("registry_path"),
        "manifest": artifact_payload.get("manifest"),
        "created": created,
        "under_target_workspace": under_target,
        "expected_paths_exist": expected_paths_exist,
        "reason": reason,
    }


def restore_roster_health_registry(registry_path: Path, registry_before: str | None) -> dict[str, Any]:
    if registry_before is None:
        if registry_path.exists():
            registry_path.unlink()
        return {"registry_restored": True, "registry_removed": True}
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    registry_path.write_text(registry_before, encoding="utf-8")
    return {"registry_restored": True, "registry_removed": False}


def remove_empty_dirs_up_to(path: Path, stop: Path) -> list[str]:
    removed: list[str] = []
    current = path.resolve()
    stop_resolved = stop.resolve()
    while current != stop_resolved:
        try:
            current.relative_to(stop_resolved)
        except ValueError:
            break
        try:
            current.rmdir()
            removed.append(str(current))
        except OSError:
            break
        current = current.parent
    return removed


def cleanup_roster_packet_output(target: Path, packet_output: dict[str, Any], registry_before: str | None) -> dict[str, Any]:
    cleanup = {
        "attempted": True,
        "status": "skipped",
        "run_dir_removed": False,
        "registry_restored": False,
        "registry_removed": False,
        "empty_dirs_removed": [],
        "reason": None,
    }
    run_dir_value = packet_output.get("run_dir")
    registry_value = packet_output.get("registry_path")
    if not path_is_under(target, str(run_dir_value)) or not path_is_under(target, str(registry_value)):
        cleanup["status"] = "skipped"
        cleanup["reason"] = "output_paths_not_under_target_workspace"
        return cleanup

    run_dir = Path(str(run_dir_value)).expanduser().resolve()
    registry_path = Path(str(registry_value)).expanduser().resolve()
    if run_dir.exists():
        shutil.rmtree(run_dir)
        cleanup["run_dir_removed"] = True
    registry_cleanup = restore_roster_health_registry(registry_path, registry_before)
    cleanup.update(registry_cleanup)
    removed_dirs: list[str] = []
    removed_dirs.extend(remove_empty_dirs_up_to(run_dir.parent, target))
    removed_dirs.extend(remove_empty_dirs_up_to(registry_path.parent, target))
    cleanup["empty_dirs_removed"] = removed_dirs
    cleanup["status"] = "success"
    return cleanup


def build_roster_health_report(
    config: HubConfig,
    target_arg: str,
    packet_id_arg: str | None,
    provider: str | None,
    auth_env: str | None,
    cv_provider: str | None,
    cv_auth_env: str | None,
    keep_artifacts: bool = False,
    codex_home: str | None = None,
    skills_root: str | None = None,
) -> tuple[int, dict[str, Any], list[str]]:
    target = Path(target_arg).expanduser().resolve()
    packet_id = (packet_id_arg or "").strip() or new_record_id(ROSTER_HEALTH_DEFAULT_ID)
    generated_at = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    if not target.exists():
        payload = {
            "schema_version": 1,
            "report_type": "roster_install_register_health",
            "generated_at": generated_at,
            "target_path": str(target),
            "overall_status": "failed",
            "refused": True,
            "reason": "missing_target",
        }
        return 1, payload, [f"Target path does not exist: {target}"]
    if not target.is_dir():
        payload = {
            "schema_version": 1,
            "report_type": "roster_install_register_health",
            "generated_at": generated_at,
            "target_path": str(target),
            "overall_status": "failed",
            "refused": True,
            "reason": "target_not_directory",
        }
        return 1, payload, [f"Target path must be a directory: {target}"]

    visibility_result = run_roster_health_route(config, ROSTER_HEALTH_VISIBILITY_UTTERANCE, target)
    visibility_payload = visibility_result.get("payload") if isinstance(visibility_result.get("payload"), dict) else {}
    visible = (
        visibility_result.get("returncode") == 0
        and visibility_payload.get("matched") is True
        and "roster" in visibility_payload.get("recognized_front_doors", [])
    )
    visibility_status = "visible" if visible else "unavailable"
    registry_path = artifact_harness_registry_path_for_target(config, target)
    registry_before = registry_path.read_text(encoding="utf-8") if path_is_under(target, str(registry_path)) and registry_path.exists() else None
    packet_result = run_roster_health_route(config, ROSTER_HEALTH_PACKET_UTTERANCE, target, create=True, packet_id=packet_id) if visible else {}
    packet_output = roster_packet_output_check(target, packet_result) if visible else {
        "status": "skipped",
        "packet_id": packet_id,
        "target_path": str(target),
        "run_dir": None,
        "registry_path": None,
        "created": False,
        "under_target_workspace": False,
        "expected_paths_exist": False,
        "reason": "invocation_surface_unavailable",
    }
    if visible and packet_output.get("status") == "success" and not keep_artifacts:
        packet_output["cleanup"] = cleanup_roster_packet_output(target, packet_output, registry_before)
    elif visible and packet_output.get("status") == "success":
        packet_output["cleanup"] = {"attempted": False, "status": "kept", "reason": "keep_artifacts_requested"}
    provider_check = build_roster_provider_check(provider, auth_env)
    cv_capability = build_roster_cv_capability_check(cv_provider, cv_auth_env)
    installed_skill = roster_skill_install_check(codex_home, skills_root, requested=bool(codex_home or skills_root))
    dependency_check = {
        "persistent_server_required": False,
        "daemon_required": False,
        "database_required": False,
        "separate_ui_required": False,
        "external_control_plane_required": False,
        "verified_repo_native_adapter": ROSTER_VERIFIED_INVOCATION_MECHANISM,
    }
    blocking = []
    if not visible:
        blocking.append("invocation_surface_unavailable")
    if packet_output.get("status") != "success":
        blocking.append("packet_output_failed")
    if installed_skill.get("requested") and installed_skill.get("status") != "installed":
        blocking.append("roster_skill_not_installed")
    cv_health_degraded = bool(cv_capability.get("health_blocking") and cv_capability.get("status") != "configured")
    if blocking:
        overall_status = "failed"
    elif provider_check.get("status") in {"missing_provider", "missing_auth"} or cv_health_degraded:
        overall_status = "degraded"
    else:
        overall_status = "healthy"
    payload = {
        "schema_version": 1,
        "report_type": "roster_install_register_health",
        "generated_at": generated_at,
        "kit_root": str(config.workspace_root),
        "target_path": str(target),
        "overall_status": overall_status,
        "refused": False,
        "reason": None,
        "product_target": ROSTER_PRODUCT_TARGET,
        "verified_invocation_mechanism": {
            "status": visibility_status,
            "mechanism_type": "repo_cli_adapter",
            "name": ROSTER_VERIFIED_INVOCATION_MECHANISM,
            "command": visibility_result.get("command"),
            "matched": bool(visibility_payload.get("matched")),
            "recognized_front_doors": visibility_payload.get("recognized_front_doors", []),
            "matched_keywords": visibility_payload.get("matched_keywords", []),
            "current_codex_surface": {
                "mention_at_roster": "product_target_unverified_as_installed_codex_mention",
                "skill": installed_skill.get("status"),
                "plugin": "not_registered_by_this_repo_health_check",
                "app_mention": "not_registered_by_this_repo_health_check",
                "slash_command": "not_verified",
            },
            "unavailable_reason": None if visible else (visibility_payload.get("reason") or visibility_result.get("stdout_parse_error") or visibility_result.get("stderr") or "route_not_visible"),
        },
        "installed_skill": installed_skill,
        "packet_output": packet_output,
        "llm_provider": provider_check,
        "cv_inspection_capability": cv_capability,
        "runtime_dependency_check": dependency_check,
        "portable_setup": [
            "repo files: scripts/brain.sh, scripts/system_hub.py, policy/system_hub.toml, contexts/team_alias_registry.json, skills/roster, templates/",
            "install adapter: scripts/brain.sh roster-install --codex-home <codex-home>",
            "verified adapter: scripts/brain.sh packet-route, then artifact-harness packet output under --path",
        ],
        "machine_local_state": [
            "Codex login/session state",
            "provider API keys or local auth environment variables",
            "personal memory, caches, and machine-local overlays",
        ],
        "blocking_findings": blocking,
        "route_checks": {
            "visibility": visibility_result,
            "packet_create": packet_result if visible else None,
        },
    }
    return command_exit_code(overall_status), payload, []


def render_roster_health_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Roster Health Check",
        "",
        f"- Overall status: `{payload.get('overall_status')}`",
        f"- Product target: `{payload.get('product_target')}`",
        f"- Verified mechanism: `{payload.get('verified_invocation_mechanism', {}).get('name')}`",
        f"- Invocation surface: `{payload.get('verified_invocation_mechanism', {}).get('status')}`",
        f"- Installed skill: `{payload.get('installed_skill', {}).get('status')}`",
        f"- Target path: `{payload.get('target_path')}`",
        f"- Packet output: `{payload.get('packet_output', {}).get('status')}`",
        f"- LLM/provider: `{payload.get('llm_provider', {}).get('status')}`",
        f"- CV inspection: `{payload.get('cv_inspection_capability', {}).get('status')}`",
        "",
        "## Boundaries",
        "",
        "- `@roster` remains the product target; this check does not prove an installed Codex mention.",
        "- No persistent server, daemon, database, separate UI, or external control plane is required.",
        "- Provider and CV secrets are checked only for presence and are not printed.",
        "",
    ]
    if payload.get("blocking_findings"):
        lines.extend(["## Blocking Findings", ""])
        lines.extend(f"- `{finding}`" for finding in payload["blocking_findings"])
        lines.append("")
    return "\n".join(lines)


def do_roster_health(
    config: HubConfig,
    target_arg: str,
    packet_id: str | None,
    provider: str | None,
    auth_env: str | None,
    cv_provider: str | None,
    cv_auth_env: str | None,
    codex_home: str | None,
    skills_root: str | None,
    keep_artifacts: bool = False,
    emit_json: bool = False,
) -> int:
    code, payload, errors = build_roster_health_report(config, target_arg, packet_id, provider, auth_env, cv_provider, cv_auth_env, keep_artifacts, codex_home, skills_root)
    for line in errors:
        print(line, file=sys.stderr)
    if emit_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(render_roster_health_markdown(payload), end="")
    return code


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
        if args.command == "artifact-harness":
            if args.mission == "replay":
                return do_artifact_harness_replay(config, args.path, args.id, args.json)
            if args.mission == "provenance":
                return do_artifact_harness_provenance(config, args.path, args.id, args.json)
            if args.mission == "runtime-check":
                return do_artifact_harness_runtime_check(config, args.path, args.id, args.json)
            if args.mission == "approval":
                return do_artifact_harness_approval(config, args.path, args.id, args.gate, args.decision, args.approver, args.note, args.json)
            if args.mission == "runtime-invoke":
                return do_artifact_harness_runtime_invoke(config, args.path, args.id, args.adapter, args.surface, args.dry_run, args.json)
            if args.mission == "schema-check":
                return do_artifact_harness_schema_check(config, args.path, args.id, args.json)
            if args.mission == "migrate":
                return do_artifact_harness_migrate(config, args.path, args.id, args.json)
            if args.mission == "repair-plan":
                return do_artifact_harness_repair_plan(config, args.path, args.id, args.json)
            if args.mission in {"status", "resume", "mark"}:
                return do_artifact_harness_lifecycle(config, args.mission, args.path, args.id, args.status, args.note, args.json)
            if not args.mission:
                payload = {"created": False, "refused": True, "reason": "missing_mission"}
                print("Artifact Harness requires a mission or action: status, resume, mark, replay, provenance, runtime-check, approval, runtime-invoke, schema-check, migrate, repair-plan.", file=sys.stderr)
                if args.json:
                    print(json.dumps(payload, ensure_ascii=False, indent=2))
                return 1
            return do_artifact_harness(config, args.mission, args.path, args.id, args.artifact, args.force, args.json)
        if args.command == "packet-route":
            return do_packet_route(config, args.utterance, args.path, args.id, args.create, args.artifact, args.force, args.json)
        if args.command == "roster-install":
            return do_roster_install(config, args.codex_home, args.skills_root, args.force, args.json)
        if args.command == "roster-health":
            return do_roster_health(config, args.path, args.id, args.provider, args.auth_env, args.cv_provider, args.cv_auth_env, args.codex_home, args.skills_root, args.keep_artifacts, args.json)
        if args.command == "roster-preferences":
            return do_roster_preferences(config, args.action, args.path, args.text, args.id, args.json)
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
