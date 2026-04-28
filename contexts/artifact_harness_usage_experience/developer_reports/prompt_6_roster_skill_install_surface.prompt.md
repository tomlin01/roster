# Prompt 6: Roster Skill Install Surface

Implement the smallest real install/register layer for Roster.

Context:
- The user manually tested `@roster`; it does not work as an installed Codex mention.
- Do not try to force or claim custom `@` behavior unless Codex actually supports it.
- Current verified user path is natural-language `Roster, ...` plus repo-local routing.
- Current verified adapter commands are `packet-route`, `artifact-harness`, and `roster-health`.
- Official local reference index points to reusable Codex skills as the best current packaging path:
  `/Users/tom/Documents/PHD/codex_updat/references/official_openai/use_cases_index.md`.
- Use the local skill-creator guidance if creating a skill:
  `/Users/tom/.codex/skills/skill-creator/SKILL.md`.

Goal:
Create a repo-portable `roster` Codex skill/install surface that can be installed
or simulated on a fresh machine without a persistent server, daemon, database, or
separate orchestration UI.

Implementation requirements:
- Add a repo-owned skill source for `roster` with a valid `SKILL.md`.
- The skill must explain when it triggers: Roster, staffing-and-coordination,
  artifact task planning, HR staffing handoff, Team Architect / CAP / runtime
  boundary coordination.
- The skill must preserve governance boundaries:
  Artifact Harness owns rule/contract/acceptance/boundary;
  HR owns staffing/role design only;
  Team Architect owns collaboration pattern/task graph/shared artifacts/CAP;
  CAP owns skill/plugin/tool authorization and approval gates only;
  runtime adapters remain execution layers only.
- The skill must call or instruct Codex to call existing repo adapters
  (`packet-route`, `artifact-harness`, `roster-health`) as internal mechanics.
  Do not duplicate the packet engine.
- Add an install/register command, preferably `./scripts/brain.sh roster-install`,
  that installs or links/copies the `roster` skill into a Codex skills root.
- The install command must support a temp/test target such as `--codex-home <dir>`
  or `--skills-root <dir>` so tests do not mutate the real user home.
- Add JSON output for install status: installed/refused, skill path, kit root,
  invocation status, and next human command.
- Extend `roster-health` if needed so it can verify:
  - repo route visibility still works;
  - target workspace packet smoke still works and cleans up;
  - installed `roster` skill exists when a skills root/codex home is supplied;
  - provider auth remains local-presence only unless a remote test is explicitly added.
- Do not claim `@roster` works. Keep it as future target only.
- Update README and usage-experience docs so the current install path is concrete:
  install/register skill, provide credentials, run health, interpret result.
- Keep the basic human path natural: `Roster, ...`. Shell commands can appear
  under install/reviewer/debug sections.

Verification requirements:
- Unit/regression tests for temp Codex home installation.
- JSON parsing tests for install and health.
- `python3 -m py_compile scripts/system_hub.py scripts/test_system_hub.py`
- `python3 scripts/test_system_hub.py`
- `python3 scripts/test_overlay_policy.py`
- `python3 scripts/test_run_agent_benchmark.py`
- `python3 -m json.tool contexts/team_alias_registry.json`
- A temp workspace smoke showing:
  1. `roster-install --codex-home <tmp-codex-home> --json` creates the skill.
  2. `roster-health --codex-home <tmp-codex-home> --path <tmp-workspace> --json`
     sees the installed skill and still writes/cleans packet output under the
     target workspace.
- Confirm no repo-local `contexts/artifact_harness_registry.json` or
  `contexts/artifact_harness_runs/` smoke output remains.

Report:
- Changed files.
- Exact install path implemented.
- Exact invocation that is now truthful for a human.
- Verification commands and results.
- Remaining risks, especially anything still unverified around `@`, `/`, plugin,
  or app mentions.
