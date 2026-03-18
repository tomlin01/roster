#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path


ROOTS = [
    Path.home() / ".codex" / "skills",
    Path.home() / ".agents" / "skills",
]


@dataclass
class Skill:
    name: str
    description: str
    path: Path
    source_root: Path


def parse_frontmatter(skill_md: Path) -> tuple[str, str]:
    text = skill_md.read_text(encoding="utf-8", errors="ignore")
    m = re.match(r"^---\n(.*?)\n---", text, flags=re.DOTALL)
    if not m:
        return skill_md.parent.name, ""
    frontmatter = m.group(1)
    n = re.search(r"^name:\s*(.+)$", frontmatter, flags=re.MULTILINE)
    d = re.search(r"^description:\s*(.+)$", frontmatter, flags=re.MULTILINE)
    name = (n.group(1).strip().strip("'").strip('"') if n else skill_md.parent.name) or skill_md.parent.name
    desc = d.group(1).strip().strip("'").strip('"') if d else ""
    return name, desc


def scan_skills(roots: list[Path]) -> tuple[list[Skill], dict[str, list[Skill]], dict[Path, int]]:
    all_skills: list[Skill] = []
    by_name: dict[str, list[Skill]] = defaultdict(list)
    entries_per_root: dict[Path, int] = {}

    for root in roots:
        count = 0
        if not root.exists():
            entries_per_root[root] = 0
            continue
        for entry in sorted(root.iterdir(), key=lambda p: p.name.lower()):
            if entry.name.startswith("."):
                continue
            skill_md = entry / "SKILL.md"
            if not skill_md.exists():
                continue
            name, desc = parse_frontmatter(skill_md)
            rec = Skill(name=name, description=desc, path=entry, source_root=root)
            all_skills.append(rec)
            by_name[name].append(rec)
            count += 1
        entries_per_root[root] = count
    return all_skills, by_name, entries_per_root


def categorize(skill: Skill) -> str:
    corpus = f"{skill.name} {skill.description}".lower()
    if any(k in corpus for k in ("skill-", "skill ", "skills", "installer", "lookup", "router", "manager")):
        return "Skill management"
    if any(
        k in corpus
        for k in (
            "arxiv",
            "pubmed",
            "openalex",
            "biorxiv",
            "citation",
            "literature",
            "review",
            "protocol",
            "synthesis",
            "clinical",
            "paper",
        )
    ):
        return "Research and evidence"
    if any(k in corpus for k in ("playwright", "webapp", "figma", "frontend", "deploy", "vercel", "cloudflare")):
        return "Web and delivery"
    if any(k in corpus for k in ("obsidian", "pdf", "docx", "doc ", "pptx", "xlsx", "json-canvas", "canvas")):
        return "Docs and knowledge tools"
    if any(k in corpus for k in ("workflow", "automation", "orchestration", "agent")):
        return "Automation and orchestration"
    return "General"


def pick(names: set[str], options: list[str]) -> list[str]:
    return [o for o in options if o in names]


def build_routes(unique_names: set[str]) -> dict[str, list[str]]:
    return {
        "Research pipeline": pick(
            unique_names,
            [
                "pipeline-router",
                "research-pipeline-runner",
                "arxiv-search",
                "openalex-database",
                "pubmed-database",
                "paper-notes",
                "citation-verifier",
                "subsection-writer",
                "prose-writer",
                "writer-selfloop",
            ],
        ),
        "Web implementation loop": pick(
            unique_names,
            [
                "project-planning",
                "figma-implement-design",
                "webapp-testing",
                "playwright",
                "vercel-deploy",
            ],
        ),
        "Knowledge base operations": pick(
            unique_names,
            [
                "obsidian-markdown",
                "obsidian-bases",
                "json-canvas",
                "file-organizer",
                "workflow-automation",
            ],
        ),
    }


def generate_markdown(
    all_skills: list[Skill],
    by_name: dict[str, list[Skill]],
    entries_per_root: dict[Path, int],
) -> str:
    unique = {name: recs[0] for name, recs in by_name.items()}
    category_map: dict[str, list[str]] = defaultdict(list)
    for name, rec in unique.items():
        category_map[categorize(rec)].append(name)

    for names in category_map.values():
        names.sort(key=str.lower)

    duplicate_names = sorted([name for name, recs in by_name.items() if len(recs) > 1], key=str.lower)
    unique_names = set(unique.keys())
    routes = build_routes(unique_names)

    lines: list[str] = []
    lines.append("# Skill Graph")
    lines.append("")
    lines.append(f"- Generated: {dt.datetime.now().isoformat(timespec='seconds')}")
    lines.append(f"- Total discovered entries: {len(all_skills)}")
    lines.append(f"- Unique skill names: {len(unique)}")
    lines.append(f"- Duplicate names across roots: {len(duplicate_names)}")
    lines.append("")
    lines.append("## Sources")
    for root, count in entries_per_root.items():
        lines.append(f"- `{root}`: {count} entries")
    lines.append("")
    lines.append("## Category Summary")
    cat_counts = Counter({cat: len(names) for cat, names in category_map.items()})
    for cat, count in sorted(cat_counts.items(), key=lambda kv: (-kv[1], kv[0].lower())):
        lines.append(f"- {cat}: {count}")
    lines.append("")
    lines.append("## Suggested Routes")
    for route, skills in routes.items():
        if skills:
            lines.append(f"- {route}: " + " -> ".join(f"`{s}`" for s in skills))
        else:
            lines.append(f"- {route}: (missing skills for this route)")
    lines.append("")
    lines.append("## Categories")
    for cat in sorted(category_map.keys(), key=str.lower):
        lines.append(f"### {cat}")
        for name in category_map[cat]:
            lines.append(f"- `{name}`")
        lines.append("")
    if duplicate_names:
        lines.append("## Duplicate Names Across Roots")
        for name in duplicate_names:
            paths = ", ".join(str(rec.path) for rec in by_name[name])
            lines.append(f"- `{name}`: {paths}")
        lines.append("")
    lines.append("## Usage")
    lines.append("Regenerate with:")
    lines.append("```bash")
    lines.append("python3 /Users/tom/Documents/PHD/codex_updat/scripts/build_skill_graph.py")
    lines.append("```")
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a skill inventory and route map.")
    parser.add_argument(
        "--skill-root",
        action="append",
        default=None,
        help="Optional skill root override. Repeat to provide multiple roots.",
    )
    parser.add_argument(
        "--output",
        default=str(Path.home() / ".codex" / "skill_graph.md"),
        help="Primary markdown output path (global default).",
    )
    parser.add_argument(
        "--mirror-output",
        default="/Users/tom/Documents/PHD/codex_updat/contexts/skill_graph.md",
        help="Optional mirror output path (workspace copy).",
    )
    parser.add_argument(
        "--no-mirror",
        action="store_true",
        help="Disable writing mirror output.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    roots = [Path(raw).expanduser().resolve() for raw in args.skill_root] if args.skill_root else [p.resolve() for p in ROOTS]
    all_skills, by_name, entries = scan_skills(roots)
    markdown = generate_markdown(all_skills, by_name, entries)

    out = Path(args.output).expanduser().resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(markdown, encoding="utf-8")
    print(f"output={out}")

    if not args.no_mirror:
        mirror = Path(args.mirror_output).expanduser().resolve()
        mirror.parent.mkdir(parents=True, exist_ok=True)
        mirror.write_text(markdown, encoding="utf-8")
        print(f"mirror_output={mirror}")

    print(f"entries={len(all_skills)} unique={len(by_name)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
