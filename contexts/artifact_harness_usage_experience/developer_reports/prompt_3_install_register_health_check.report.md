Implemented the smallest current-status path.

Changed this turn:
- [scripts/system_hub.py](/Users/tom/Documents/PHD/codex-cns/scripts/system_hub.py:93): added `roster-health`.
- [scripts/test_system_hub.py](/Users/tom/Documents/PHD/codex-cns/scripts/test_system_hub.py:2731): added health-check coverage.
- [README.md](/Users/tom/Documents/PHD/codex-cns/README.md:12): documented the verified mechanism.
- [README.target-user-experience.draft.md](/Users/tom/Documents/PHD/codex-cns/contexts/artifact_harness_usage_experience/README.target-user-experience.draft.md:192): updated target install/health wording.

Verified mechanism: `./scripts/brain.sh packet-route ...` and `./scripts/brain.sh roster-health ...`. `@roster` remains the product target, not a verified installed Codex mention, skill, plugin, app mention, or slash command.

Health check behavior:
- verifies Roster route visibility through `packet-route`
- creates packet output under `--path <workspace>`, then cleans it by default
- reports `configured`, `missing_provider`, or `missing_auth`
- does not print secrets
- confirms no server, daemon, database, separate UI, or hidden control plane

Validation run:
- `python3 -m py_compile scripts/system_hub.py scripts/test_system_hub.py`
- temp workspace `roster-health --json` smoke and JSON parse
- missing-provider and missing-auth simulations
- fake configured provider check with secret non-leak assertion
- `python3 scripts/test_system_hub.py`
- `git diff --check`
- Markdown local link check
- confirmed no repo-local artifact-harness smoke registry/run output remains

Remaining risks:
- no actual installed `@roster` mention surface yet
- provider check verifies local credential presence only, not a remote model call
- worktree still contains pre-existing Prompt 2 changes in `AGENTS.md` and `contexts/team_alias_registry.json`

