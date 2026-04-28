Implemented the smallest repo-native Roster install/register health path.

Changed:
- [scripts/system_hub.py](/Users/tom/Documents/PHD/codex-cns/scripts/system_hub.py): added `roster-health`, JSON health report, provider diagnostics, target-workspace packet smoke, default smoke cleanup, and standard healthy/degraded/failed exit codes.
- [scripts/test_system_hub.py](/Users/tom/Documents/PHD/codex-cns/scripts/test_system_hub.py): added health-check coverage for temp workspace output, cleanup, missing provider/auth, configured provider, JSON refusals, and no secret leakage.
- [README.md](/Users/tom/Documents/PHD/codex-cns/README.md): documented the current verified mechanism as `./scripts/brain.sh packet-route ...` / `./scripts/brain.sh roster-health ...`, not an installed `@roster` mention.
- [README.target-user-experience.draft.md](/Users/tom/Documents/PHD/codex-cns/contexts/artifact_harness_usage_experience/README.target-user-experience.draft.md): separated repo-portable setup from machine-local credentials/state.

Verified:
- `python3 -m py_compile scripts/system_hub.py scripts/test_system_hub.py`
- `python3 scripts/test_system_hub.py`
- temp-workspace `roster-health --json` smoke with structured `missing_provider`
- repo-root `roster-health --path . --provider local-test --auth-env ROSTER_TEST_API_KEY --json`
- Markdown link check: `missing_count = 0`
- no `contexts/artifact_harness_registry.json` or `contexts/artifact_harness_runs` left in the repo

Remaining risks:
- `@roster` is still only the product target, not a verified installed Codex mention/skill/plugin/app/slash surface.
- Provider “configured” currently verifies local credential wiring only; it does not make a remote model call by default.

Existing uncommitted `AGENTS.md` and `contexts/team_alias_registry.json` changes were already in the worktree and left intact.

