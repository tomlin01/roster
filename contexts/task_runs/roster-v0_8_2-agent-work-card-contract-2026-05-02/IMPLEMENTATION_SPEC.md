# Implementation Spec

Task ID: `roster-v0_8_2-agent-work-card-contract-2026-05-02`
Parent Spec: `/Users/tom/Documents/PHD/codex-cns/contexts/artifact_harness_usage_experience/ROSTER_MILESTONE_ROADMAP.md`
Intent Record: `/Users/tom/Documents/PHD/codex-cns/contexts/task_runs/roster-v0_8_2-agent-work-card-contract-2026-05-02/INTENT.md`
Current State: `/Users/tom/Documents/PHD/codex-cns/contexts/task_runs/roster-v0_8_2-agent-work-card-contract-2026-05-02/CURRENT_STATE.md`

## Objective

Implement this specific change:

```text
Teach Roster that expanded roles and members must be actionable work cards, not
only user-facing labels.
```

## Work Type

Select the closest type:

- `docs`
- `markdown`
- `template`
- `tests`
- `code` only if route/help output needs small work-card support

## Scope

Allowed scope:

- `skills/roster/SKILL.md`
- `plugins/roster/commands/roster.md`
- `README.md`
- `contexts/artifact_harness_usage_experience/README.md`
- `contexts/artifact_harness_usage_experience/README.target-user-experience.draft.md`
- `contexts/artifact_harness_usage_experience/ROSTER_NEXT_VERSION_DIRECTION.md`
- `contexts/artifact_harness_usage_experience/ROSTER_MILESTONE_ROADMAP.md`
- `contexts/artifact_harness_usage_experience/developer_reports/prompt_v0_8_2_agent_work_card_contract.prompt.md`
- `templates/team_architect/team_operating_packet.template.md`
- optionally `templates/team_architect/agent_work_card.template.md`
- this packet directory

Forbidden scope:

- Do not implement full Role Interaction Patterns.
- Do not add interaction-edge schema.
- Do not implement automatic subagent spawning.
- Do not add persistent work-card storage.
- Do not rewrite runtime adapter architecture.
- Do not change CAP authorization ownership.
- Do not implement the BCQ_III app.

## Requirements

Behavior or content requirements:

- Define Agent Work Cards as actionable handoff units for expanded roles.
- State that ordinary first-touch replies should not dump full work cards.
- State when work cards appear:
  - user asks for who does what;
  - user asks to expand work or agents;
  - task moves into implementation planning;
  - risk or authority clarity matters.
- Each work card should include:
  - role name;
  - group;
  - responsibility;
  - perspective;
  - inputs;
  - output or deliverable;
  - done condition;
  - handoff target;
  - tool or capability need;
  - agent assignment mode;
  - open questions.
- Assignment mode should distinguish:
  - separate agent;
  - merged role;
  - simulated perspective;
  - reviewer-only;
  - approval-gate candidate.
- State that capability needs are not tool authorization.
- State that approval-gate candidates do not approve anything by themselves.
- State that handoff target is not full v0.9 interaction-edge modeling.
- Preserve `v0.8.0` role contextualization and `v0.8.1` group expansion rules.

Structure requirements:

- Public docs should keep first-touch examples short.
- Usage docs may hold the fuller BCQ_III work-card example.
- Skill and slash command docs should tell the active model when to offer or
  emit work cards.
- Team Operating Packet template should receive work-card fill notes or a
  separate small template if useful.

Wording requirements:

- Do not expose internal governance terms in ordinary user-facing examples.
- Do not imply every work card becomes a runtime subagent.
- Do not imply work cards replace review, acceptance, approval, CAP, or runtime
  policy.
- Do not make Roster ask the user to choose internal assignment modes unless the
  user asks for that level of detail.

## Non-Goals

Do not do these in this pass:

- full interaction-edge vocabulary;
- handoff / peer alignment / review challenge schema;
- automatic subagent execution policy;
- persistent role/work-card storage;
- runtime adapter changes;
- CAP authorization changes;
- release tagging;
- BCQ_III app implementation.

## Acceptance Criteria

The task is complete when:

- `skills/roster/SKILL.md` includes Agent Work Card rules.
- `plugins/roster/commands/roster.md` includes the same ordinary behavior
  guidance.
- Docs define the required work-card fields.
- A BCQ_III or equivalent example shows at least one full work card.
- Docs state work cards do not automatically spawn separate agents.
- Docs state capability needs are not authorization.
- Docs state work cards are not full role interaction-edge modeling.
- Text audit confirms public first-touch examples remain short.
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

- BCQ_III or equivalent work-card example includes all required fields.
- Public first-touch examples do not become long work-card dumps.
- No docs imply every work card is a separate agent.
- No docs imply capability need equals authorization.
- No docs imply this patch is full role interaction modeling.

If validation cannot run, explain why and what risk remains.

## Handoff Requirements

Developer final response must include:

- Changed files.
- Implemented work-card behavior.
- Validation commands and results.
- Remaining risks.
- Whether the task is ready for review.
