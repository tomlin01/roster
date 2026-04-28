Implemented executable Roster routing.

Changed:
- [contexts/team_alias_registry.json](/Users/tom/Documents/PHD/codex-cns/contexts/team_alias_registry.json:12): added `Roster`, `@roster`, and context-limited `PM` aliases to the Artifact Harness workflow.
- [scripts/system_hub.py](/Users/tom/Documents/PHD/codex-cns/scripts/system_hub.py:8880): added alias-target routing, leading-invocation/context guards for `PM`, and SPEC-first alias handling.
- [scripts/test_system_hub.py](/Users/tom/Documents/PHD/codex-cns/scripts/test_system_hub.py:2386): added route-hit, ambiguous `PM` miss, and cross-workspace `--create` coverage.
- [README.md](/Users/tom/Documents/PHD/codex-cns/README.md:12) and [AGENTS.md](/Users/tom/Documents/PHD/codex-cns/AGENTS.md:54): updated usage notes without claiming automatic GUI interception.

Verified:
- `python3 -m py_compile scripts/system_hub.py scripts/test_system_hub.py`
- `python3 scripts/test_system_hub.py`
- Direct JSON checks for the three requested route-hit phrases plus ambiguous `5 PM` miss.
- Repo-local smoke output check returned empty for artifact-harness runs/registry under `contexts/`.

Remaining risk: this makes `packet-route` executable for the aliases; it still does not implement automatic Codex GUI interception or install behavior. Also, the pre-existing untracked `contexts/artifact_harness_usage_experience/` directory is still present and untouched.

