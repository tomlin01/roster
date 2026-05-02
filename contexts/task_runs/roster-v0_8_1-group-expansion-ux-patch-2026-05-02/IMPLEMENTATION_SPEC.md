# Implementation Spec

Task ID: `roster-v0_8_1-group-expansion-ux-patch-2026-05-02`
Parent Spec: `/Users/tom/Documents/PHD/codex-cns/contexts/artifact_harness_usage_experience/ROSTER_MILESTONE_ROADMAP.md`
Intent Record: `/Users/tom/Documents/PHD/codex-cns/contexts/task_runs/roster-v0_8_1-group-expansion-ux-patch-2026-05-02/INTENT.md`
Current State: `/Users/tom/Documents/PHD/codex-cns/contexts/task_runs/roster-v0_8_1-group-expansion-ux-patch-2026-05-02/CURRENT_STATE.md`

## Objective

Implement this specific change:

```text
Teach Roster that multi-group collaboration can expand into concrete group
members when useful, while first-touch replies stay group-level by default.
```

## Work Type

Select the closest type:

- `docs`
- `markdown`
- `tests`
- `code` only if route/help output needs small group-expansion support

## Scope

Allowed scope:

- `skills/roster/SKILL.md`
- `plugins/roster/commands/roster.md`
- `README.md`
- `contexts/artifact_harness_usage_experience/README.md`
- `contexts/artifact_harness_usage_experience/README.target-user-experience.draft.md`
- `contexts/artifact_harness_usage_experience/ROSTER_NEXT_VERSION_DIRECTION.md`
- `contexts/artifact_harness_usage_experience/ROSTER_MILESTONE_ROADMAP.md`
- `contexts/artifact_harness_usage_experience/developer_reports/prompt_v0_8_1_group_expansion_ux_patch.prompt.md`
- `templates/team_architect/team_operating_packet.template.md`
- this packet directory

Forbidden scope:

- Do not implement full Role Interaction Patterns.
- Do not add interaction-edge schema.
- Do not implement automatic subagent spawning.
- Do not add persistent group/member storage.
- Do not rewrite runtime adapter architecture.
- Do not add project/team mode.

## Requirements

Behavior or content requirements:

- Add group expansion guidance.
- State that broad first-touch replies should usually show groups first.
- State that Roster can expand groups into members when:
  - the user asks to expand;
  - the task moves into implementation planning;
  - risk or complexity requires owner/perspective clarity.
- Expanded members should carry:
  - responsibility;
  - perspective;
  - deliverable.
- State that expansion does not automatically mean every member is a separate
  agent.
- State that group expansion is not full role interaction-edge modeling.
- Preserve `v0.8.0` role contextualization rules for added roles.
- Include a BCQ_III or equivalent example with:
  - first-touch group preview;
  - expanded member view.

Structure requirements:

- Public docs should keep the first-touch example short.
- Usage docs may hold the fuller BCQ_III expanded example.
- Skill and slash command docs should tell the active model when to expand.
- Templates may receive fill notes for groups and members only if useful.

Wording requirements:

- Do not expose internal governance terms in ordinary examples.
- Do not show a long member list in the first-touch example unless the task asks
  for expansion.
- Do not imply every expanded member becomes a runtime agent.

## Non-Goals

Do not do these in this pass:

- full interaction-edge vocabulary;
- handoff / peer alignment / review challenge schema;
- automatic subagent policy or execution;
- persistent group/member storage;
- release tagging;
- large README rewrite unrelated to group expansion.

## Acceptance Criteria

The task is complete when:

- `skills/roster/SKILL.md` includes group expansion rules.
- `plugins/roster/commands/roster.md` includes the same ordinary expansion
  guidance.
- Public/usage docs include a group preview and expanded member example.
- Docs state expansion does not automatically create separate agents.
- Docs state expansion is not full role interaction-edge modeling.
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

- BCQ_III example or equivalent appears in docs.
- First-touch group preview is shorter than expanded member view.
- Expanded member view includes responsibility, perspective, and deliverable.
- No docs imply every member is a separate agent.
- No docs imply this patch is full role interaction modeling.

If validation cannot run, explain why and what risk remains.

## Handoff Requirements

Developer final response must include:

- Changed files.
- Implemented group-expansion UX behavior.
- Validation commands and results.
- Remaining risks.
- Whether the task is ready for review.
