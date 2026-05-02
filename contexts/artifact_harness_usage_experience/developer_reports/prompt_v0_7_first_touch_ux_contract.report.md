# Prompt v0.7.0 Report: Roster First-Touch UX Contract

## Changed Files

- `skills/roster/SKILL.md`
- `plugins/roster/commands/roster.md`
- `README.md`
- `contexts/artifact_harness_usage_experience/README.md`
- `contexts/artifact_harness_usage_experience/README.target-user-experience.draft.md`

## Implemented

- Added a first-touch response contract that tells Roster to choose the smallest
  useful team shape.
- Added plain handling phrases for direct work, compact teams, multi-part
  collaboration, and ambiguous ownership.
- Added meeting-note examples with natural Traditional Chinese roles:
  `轉錄人員`, `會議紀錄人員`, and `會議負責人`.
- Added role-adjustment examples such as `加一個主管`, `讓 PM 看一下`,
  `需要法務審`, and `加一個學生視角`.
- Preserved the rule that ordinary first-touch replies should not expose
  internal governance or packet terminology.
- Kept `Roster, ...` as the stable fallback while leaving `@roster` and
  `/roster` caveated by install, reload, and supported host behavior.

## Validation

Passed:

```sh
python3 -m py_compile scripts/system_hub.py scripts/test_system_hub.py
python3 scripts/test_system_hub.py
python3 scripts/test_overlay_policy.py
python3 scripts/test_run_agent_benchmark.py
python3 -m json.tool contexts/team_alias_registry.json
git diff --check
```

Additional text audit passed:

```text
v0.7 first-touch text audit passed
```

Text audit:

- Ordinary first-touch examples avoid internal governance terms.
- Complexity examples use natural phrases, not user-facing `Level 1` /
  `Level 2` labels.
- Meeting-note examples use `轉錄人員`, `會議紀錄人員`, and `會議負責人`.
- Installed invocation remains caveated by `roster-install`, Codex reload, and
  supported host behavior.

## Remaining Risks

- This is a documentation and behavior-contract change. It does not implement a
  full role interaction engine or automatic subagent spawning.
- Roster still depends on the active model following the skill/plugin guidance
  for first-touch reply style.

## Ready For Review

Yes, after validation commands pass.
