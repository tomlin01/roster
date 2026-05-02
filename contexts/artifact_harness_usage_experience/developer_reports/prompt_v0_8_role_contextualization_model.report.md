# Prompt v0.8.0 Report: Roster Role Contextualization Model

## Changed Files

- `skills/roster/SKILL.md`
- `plugins/roster/commands/roster.md`
- `README.md`
- `contexts/artifact_harness_usage_experience/README.md`
- `contexts/artifact_harness_usage_experience/README.target-user-experience.draft.md`
- `templates/team_architect/team_operating_packet.template.md`

## Implemented

- Added role contextualization rules for user-added roles.
- Defined role, perspective, layer, and agent instance distinctions in the
  Roster skill guidance.
- Stated that adding a role does not automatically add a new agent.
- Stated that the default four-role shape is layer compression, not a hard
  maximum.
- Added examples for:
  - `加一個主管`
  - `讓 PM 看一下`
  - `需要法務審`
  - `加一個學生視角`
  - `技術人員加入金融 domain`
  - `新增一位金融技術人員，跟原本技術人員同級`
  - `金融技術人員要核准模型結果才能交付`
- Added Team Operating Packet fill notes for role context, authority boundary,
  peer alignment, and capability implications.

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
v0.8 role contextualization text audit passed
```

Text audit:

- Role examples include domain extension, peer domain role, reviewer/approver,
  and counter-perspective cases.
- Ordinary examples avoid internal governance terms.
- Docs state that added roles do not automatically become new agents.
- Docs state that the four-role shape is layer compression, not a hard maximum.
- Peer roles are not treated as approvers by default.

## Remaining Risks

- This is a documentation/template contract change, not a full role interaction
  engine.
- The actual runtime still depends on the active model following the Roster
  skill/plugin guidance.

## Ready For Review

Yes, after validation commands pass.
