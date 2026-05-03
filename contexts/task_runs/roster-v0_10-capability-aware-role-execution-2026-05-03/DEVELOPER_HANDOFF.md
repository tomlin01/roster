# Developer Handoff

Copy this into a fresh developer CLI/thread.

## Role

You are the developer thread. Implement only the attached implementation spec.
Do not use hidden assumptions from the main conversation.

## Required Reads

Read these files first:

- `contexts/task_runs/roster-v0_10-capability-aware-role-execution-2026-05-03/INTENT.md`
- `contexts/task_runs/roster-v0_10-capability-aware-role-execution-2026-05-03/CURRENT_STATE.md`
- `contexts/task_runs/roster-v0_10-capability-aware-role-execution-2026-05-03/IMPLEMENTATION_SPEC.md`

Optional supporting files:

- `contexts/artifact_harness_usage_experience/ROSTER_V0_10_CAPABILITY_AWARE_ROLE_EXECUTION.md`
- `contexts/artifact_harness_usage_experience/ROSTER_MILESTONE_ROADMAP.md`
- `contexts/artifact_harness_usage_experience/ROSTER_NEXT_VERSION_DIRECTION.md`
- `contexts/artifact_harness_usage_experience/ROSTER_SKILL_INTEROP_NOTE.md`
- `skills/roster/SKILL.md`
- `plugins/roster/commands/roster.md`
- `templates/team_architect/team_operating_packet.template.md`
- `scripts/system_hub.py`
- `scripts/test_system_hub.py`

## Execution Rules

- Follow the implementation spec literally.
- Use the current state file to avoid redoing completed work.
- Preserve user intent from the intent record.
- Make the smallest correct change.
- Do not widen scope.
- Do not implement new web/browser/CV/connector/runtime adapters.
- Do not claim host-dependent tools are available unless local evidence proves
  it; use `unknown` where appropriate.
- If the spec is impossible or contradictory, stop and report the blocker.

## Validation

Run the validation plan from the implementation spec.

If you add or change tests, run the smallest relevant test set first.

## Final Response Format

Return:

```text
Changed files:
- <path>

Implemented:
- <item>

Roster-health capability reporting:
- implemented / deferred
- <short detail>

Validation:
- <command>: <result>

Risks or blockers:
- <item-or-none>

Ready for review:
- <yes/no>
```
