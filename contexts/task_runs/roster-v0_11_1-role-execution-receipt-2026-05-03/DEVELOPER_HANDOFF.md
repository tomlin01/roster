# Developer Handoff

Copy this into a fresh developer CLI/thread.

## Role

You are the developer thread. Implement only the attached implementation spec.
Do not use hidden assumptions from the main conversation.

## Required Reads

Read these files first:

- `contexts/task_runs/roster-v0_11_1-role-execution-receipt-2026-05-03/INTENT.md`
- `contexts/task_runs/roster-v0_11_1-role-execution-receipt-2026-05-03/CURRENT_STATE.md`
- `contexts/task_runs/roster-v0_11_1-role-execution-receipt-2026-05-03/IMPLEMENTATION_SPEC.md`

Optional supporting files:

- `contexts/artifact_harness_usage_experience/ROSTER_V0_11_1_ROLE_EXECUTION_RECEIPT.md`
- `contexts/artifact_harness_usage_experience/ROSTER_MILESTONE_ROADMAP.md`
- `contexts/artifact_harness_usage_experience/ROSTER_NEXT_VERSION_DIRECTION.md`
- `contexts/artifact_harness_usage_experience/ROSTER_V0_10_CAPABILITY_AWARE_ROLE_EXECUTION.md`
- `skills/roster/SKILL.md`
- `plugins/roster/commands/roster.md`
- `README.md`
- `contexts/artifact_harness_usage_experience/README.md`
- `contexts/artifact_harness_usage_experience/README.target-user-experience.draft.md`

## Execution Rules

- Follow the implementation spec literally.
- Use the current state file to avoid redoing completed work.
- Preserve user intent from the intent record.
- Make the smallest correct change.
- Do not widen scope.
- Keep first-touch UX short and natural.
- Make later completion style match the Roster agent-coordination idea:
  outcome, role actions, and convergence.
- Do not claim separate runtime agents or parallel subagents ran unless that is
  actually true in the documented behavior.
- Do not implement new web/browser/CV/plugin/connector/subagent adapters.
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

Tests or text audits:
- added / deferred
- <short detail>

Validation:
- <command>: <result>

Risks or blockers:
- <item-or-none>

Ready for review:
- <yes/no>
```

