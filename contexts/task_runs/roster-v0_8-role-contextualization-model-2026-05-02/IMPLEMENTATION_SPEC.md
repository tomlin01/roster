# Implementation Spec

Task ID: `roster-v0_8-role-contextualization-model-2026-05-02`
Parent Spec: `/Users/tom/Documents/PHD/codex-cns/contexts/artifact_harness_usage_experience/ROSTER_MILESTONE_ROADMAP.md`
Intent Record: `/Users/tom/Documents/PHD/codex-cns/contexts/task_runs/roster-v0_8-role-contextualization-model-2026-05-02/INTENT.md`
Current State: `/Users/tom/Documents/PHD/codex-cns/contexts/task_runs/roster-v0_8-role-contextualization-model-2026-05-02/CURRENT_STATE.md`

## Objective

Implement this specific change:

```text
Teach Roster to interpret user-named roles as context-shaped responsibilities,
perspectives, layers, and possible agent assignments without making every added
role a new agent.
```

## Work Type

Select the closest type:

- `docs`
- `markdown`
- `tests`
- `code` only if route/help/JSON output needs small role-context support

## Scope

Allowed scope:

- `skills/roster/SKILL.md`
- `plugins/roster/commands/roster.md`
- `README.md`
- `contexts/artifact_harness_usage_experience/README.md`
- `contexts/artifact_harness_usage_experience/README.target-user-experience.draft.md`
- `contexts/artifact_harness_usage_experience/ROSTER_NEXT_VERSION_DIRECTION.md`
- `contexts/artifact_harness_usage_experience/ROSTER_MILESTONE_ROADMAP.md`
- `contexts/artifact_harness_usage_experience/developer_reports/prompt_v0_8_role_contextualization_model.prompt.md`
- `templates/team_architect/team_operating_packet.template.md`
- `templates/team_architect/capability_access_packet.template.md` only if needed
- `scripts/system_hub.py`
- `scripts/test_system_hub.py`
- this packet directory

Forbidden scope:

- Do not implement full Role Interaction Patterns.
- Do not add Team Operating Packet interaction-edge schema.
- Do not implement automatic subagent spawning.
- Do not add project/team mode.
- Do not add persistent role memory or a role database.
- Do not rewrite runtime adapter architecture.
- Do not edit installed local state under `/Users/tom/.codex/`.

## Requirements

Behavior or content requirements:

- Add role contextualization guidance for user-added roles.
- Define the distinctions:
  - `role`
  - `perspective`
  - `layer`
  - `agent instance`
- State clearly that adding a role does not automatically add a new agent.
- State clearly that the default four-role shape is layer compression, not a
  hard maximum.
- Add examples for:
  - title/rank additions: `加一個主管`
  - function additions: `讓 PM 看一下`
  - review/authority additions: `需要法務審`
  - counter-perspective additions: `加一個學生視角`
  - domain extension: `技術人員加入金融 domain`
  - peer domain role: `新增一位金融技術人員，跟原本技術人員同級`
  - reviewer/approver role: `金融技術人員要核准模型結果才能交付`
- Teach Roster to decide whether a new role should be:
  - merged into an existing role as a multi-domain perspective;
  - added as a peer domain role with an alignment step;
  - added as reviewer or approver with review/sign-off position;
  - added as counter-perspective for friction/comprehension checks.
- Keep ordinary user-facing examples short and natural.

Structure requirements:

- Public docs should explain the behavior with examples, not taxonomy first.
- Skill and slash command docs should tell the active model how to interpret
  user role edits.
- Templates may receive fill notes only if needed to preserve role context in
  generated packet output.
- Tests or text audits should catch the required example coverage.

Wording requirements:

- Do not expose `Artifact Harness`, `HR`, `Team Architect`, `CAP`, runtime
  adapter, packet chain, or control-plane terms in ordinary user-facing
  examples.
- Do not show role taxonomy to the user before the practical interpretation.
- Do not overclaim that Roster can safely infer approval authority when the
  user is ambiguous.

## Non-Goals

Do not do these in this pass:

- full role interaction edge vocabulary;
- task graph interaction-edge schema;
- automatic subagent policy or execution;
- persistent role storage;
- release tagging;
- large README rewrite unrelated to role contextualization.

## Acceptance Criteria

The task is complete when:

- `skills/roster/SKILL.md` includes role contextualization rules.
- `plugins/roster/commands/roster.md` includes the same ordinary role-edit
  guidance.
- Public/usage docs include examples for domain extension, peer domain role,
  reviewer/approver role, and counter-perspective role.
- Docs state that added roles do not automatically become new agents.
- Docs state that the four-role shape is layer compression, not a maximum.
- Text audit confirms ordinary examples do not leak internal governance terms.
- Validation commands pass or failures are documented with risk.
- Developer report is written to the required report path.

## Validation Plan

Run or perform:

```sh
python3 -m py_compile scripts/system_hub.py scripts/test_system_hub.py
python3 scripts/test_system_hub.py
python3 scripts/test_overlay_policy.py
python3 scripts/test_run_agent_benchmark.py
python3 -m json.tool contexts/team_alias_registry.json
git diff --check
```

Also inspect:

- Role examples include domain extension, peer domain role, reviewer/approver,
  and counter-perspective cases.
- Ordinary examples avoid internal governance terms.
- No docs imply that every added role becomes a new agent.
- No docs imply that a peer role is automatically an approver.
- `@roster` / `/roster` support remains caveated truthfully.

If validation cannot run, explain why and what risk remains.

## Handoff Requirements

Developer final response must include:

- Changed files.
- Implemented role-context behavior.
- Validation commands and results.
- Remaining risks.
- Whether the task is ready for review.
