#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY_DIR = ROOT / "policy"
SCRIPT_DIR = ROOT / "scripts"
POLICY_FILES = [
    "RESOURCE_TAXONOMY.md",
    "GLOBAL_OPERATING_MODEL.md",
    "global_agent_defaults.json",
    "agent_contract_schema.json",
    "benchmark_case_schema.json",
    "benchmark_report_schema.json",
]
RUNNER_FILES = [
    "overlay_policy.py",
    "run_agent_benchmark.py",
    "run_agent_benchmark.sh",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Publish repo canonical policy artifacts to $CODEX_HOME/agent_policy.")
    parser.add_argument("--codex-home", default=str(Path.home() / ".codex"), help="Override CODEX_HOME.")
    parser.add_argument("--dry-run", action="store_true", help="Print publish actions without writing files.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    codex_home = Path(args.codex_home).expanduser().resolve()
    target_dir = codex_home / "agent_policy"
    manifest = {
        "source_workspace": str(ROOT),
        "target_dir": str(target_dir),
        "policy_files": POLICY_FILES,
        "runner_files": RUNNER_FILES,
    }

    if not POLICY_DIR.exists():
        raise SystemExit(f"Missing policy directory: {POLICY_DIR}")
    for filename in POLICY_FILES:
        if not (POLICY_DIR / filename).exists():
            raise SystemExit(f"Missing required policy artifact: {POLICY_DIR / filename}")
    for filename in RUNNER_FILES:
        if not (SCRIPT_DIR / filename).exists():
            raise SystemExit(f"Missing required runner artifact: {SCRIPT_DIR / filename}")

    if args.dry_run:
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
        return 0

    target_dir.mkdir(parents=True, exist_ok=True)
    for filename in POLICY_FILES:
        shutil.copy2(POLICY_DIR / filename, target_dir / filename)
    for filename in RUNNER_FILES:
        shutil.copy2(SCRIPT_DIR / filename, target_dir / filename)
    (target_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"published_to={target_dir}")
    print(f"files={len(POLICY_FILES) + len(RUNNER_FILES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
