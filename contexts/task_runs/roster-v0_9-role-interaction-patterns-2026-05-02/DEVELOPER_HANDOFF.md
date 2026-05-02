# Developer Handoff

Copy this into a fresh developer CLI/thread.

## Role

You are the developer thread. Implement only the attached implementation spec.
Do not use hidden assumptions from the main conversation.

## Required Reads

Read these files first:

- `/Users/tom/Documents/PHD/codex-cns/contexts/task_runs/roster-v0_9-role-interaction-patterns-2026-05-02/INTENT.md`
- `/Users/tom/Documents/PHD/codex-cns/contexts/task_runs/roster-v0_9-role-interaction-patterns-2026-05-02/CURRENT_STATE.md`
- `/Users/tom/Documents/PHD/codex-cns/contexts/task_runs/roster-v0_9-role-interaction-patterns-2026-05-02/IMPLEMENTATION_SPEC.md`

Supporting files:

- `/Users/tom/Documents/PHD/codex-cns/contexts/artifact_harness_usage_experience/ROSTER_NEXT_VERSION_DIRECTION.md`
- `/Users/tom/Documents/PHD/codex-cns/contexts/artifact_harness_usage_experience/ROSTER_MILESTONE_ROADMAP.md`
- `/Users/tom/Documents/PHD/codex-cns/contexts/artifact_harness_usage_experience/developer_reports/prompt_v0_9_role_interaction_patterns.prompt.md`
- `/Users/tom/Documents/PHD/codex-cns/contexts/artifact_harness_usage_experience/behavior_validation/BCQ_III_AGENT_WORK_CARD_RUN_2026-05-02.md`
- `/Users/tom/Documents/PHD/codex-cns/contexts/artifact_harness_usage_experience/behavior_validation/MEETING_NOTES_TO_EXEC_SLIDES_RUN_2026-05-02.md`
- `/Users/tom/Documents/PHD/codex-cns/templates/team_architect/team_operating_packet.template.md`

## Execution Rules

- Follow the implementation spec literally.
- Keep the change scoped to `v0.9.0` Role Interaction Patterns.
- Preserve user intent from the intent record.
- Make the smallest correct documentation/template change.
- Do not widen scope into subagent policy, runtime execution, message bus, CAP
  authorization, approval execution, or real artifact production.
- If the spec is impossible or contradictory, stop and report the blocker.

## Validation

Run the validation plan from the implementation spec.

If a validation command is unrelated but required by the spec, still run it and
report the result.

## Final Response Format

Return:

```text
Changed files:
- <path>

Implemented:
- <item>

Validation:
- <command>: <result>

Risks or blockers:
- <item-or-none>

Ready for review:
- <yes/no>
```
