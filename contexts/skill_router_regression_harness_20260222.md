# Skill Router Regression Harness

Date: 2026-02-22

## Added
- Case fixtures:
  - `/Users/tom/.codex/skills/requirement-skill-router/references/router_regression_cases.json`
- Runner script:
  - `/Users/tom/.codex/skills/requirement-skill-router/scripts/run_router_regression.py`
- Workspace wrapper:
  - `/Users/tom/Documents/PHD/codex_updat/scripts/run_router_regression.sh`

## How to Run
- Full suite:
  - `bash /Users/tom/Documents/PHD/codex_updat/scripts/run_router_regression.sh`
- Selected cases:
  - `bash /Users/tom/Documents/PHD/codex_updat/scripts/run_router_regression.sh --only explicit_dollar_playwright install_skill_from_repo`
- Save JSON report:
  - `bash /Users/tom/Documents/PHD/codex_updat/scripts/run_router_regression.sh --json-report /Users/tom/Documents/PHD/codex_updat/contexts/router_regression_latest.json`

## Current Suite Scope
11 cases covering:
- mixed figma+browser chain
- quality closeout route
- router keyword noise guard
- external action connect route
- explicit `$skill` handling
- skill-management with domain primary
- install intent forcing installer primary
- local github workflow guard
- visual explanation route
- research pipeline route
- `$skill` prefix false-positive guard

Runner safeguards:
- validates fixture check keys/types (unknown keys fail fast)
- resolves `route_a` by route id (not list position)
- supports skill-level assertions (`skill_fields_equal`) for explicit mention flags

## Latest Run
- Report path: `/Users/tom/Documents/PHD/codex_updat/contexts/router_regression_latest.json`
- Status: PASS (11/11)
