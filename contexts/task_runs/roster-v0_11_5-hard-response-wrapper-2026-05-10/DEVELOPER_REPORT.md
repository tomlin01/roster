# Developer Report

Task ID: `roster-v0_11_5-hard-response-wrapper-2026-05-10`

## Changes Made

- Added `ROSTER_V0_11_5_HARD_RESPONSE_WRAPPER.md` to define the hard response
  gate.
- Updated `skills/roster/SKILL.md` and `plugins/roster/commands/roster.md` so
  non-trivial ordinary Roster replies must include:
  - `本次啟用`
  - `目前階段`
  - useful work
  - `本次分工執行`
  - `最後收斂`
- Added an internal diagnostics barrier for ordinary replies:
  route checks, packet adapters, preferences, registries, CAP, runtime adapter,
  and control-plane details stay out of normal user-facing output.
- Added a repo-level `Roster v0.11.5 Visible Response Guard` in `AGENTS.md` so
  fresh starts do not send visible pre-tool status lines with internal
  route/packet/preference diagnostics.
- Tightened the required first line so it must use literal `agent` or
  `role-agents`, not generic `角色`.
- Tightened Roster preference-memory detection so `未來可能` / `之後可能`
  artifact wording does not route to preference memory without explicit
  remember/default wording.
- Updated README and usage-experience docs with the same v0.11.5 contract.
- Added a focused regression text audit to `scripts/test_system_hub.py`.
- Added task-run intent and implementation spec files.
- Added `STRESS_TEST_REPORT.md` with the failed and accepted CLI rounds.

## Verification

- `python3 -m py_compile scripts/system_hub.py scripts/test_system_hub.py`
  passed.
- `git diff --check` passed.
- `python3 scripts/test_system_hub.py` passed.
- Reinstalled Roster into `/Users/tom/.codex` with
  `./scripts/brain.sh roster-install --codex-home /Users/tom/.codex --force --json`.
- Round 3: five independent fresh `codex exec --ephemeral` sessions passed the
  saved-final gate for `本次啟用`, `目前階段`, useful work,
  `本次分工執行`, `最後收斂`, and no internal adapter leakage.
- Round 6: repeated the highest-risk creative planning prompt after the
  repo-level visible-response guard and explicit `role-agents` wording; saved
  final began with `本次啟用：4 個 role-agents...` and passed the leak scan.

## Remaining Risk

- This is still a skill/plugin response contract, not a runtime formatter.
  The fresh CLI starts tested here now pass the saved-final gate, but host
  behavior can still vary when a workspace does not load this repo's
  `AGENTS.md` guard.
