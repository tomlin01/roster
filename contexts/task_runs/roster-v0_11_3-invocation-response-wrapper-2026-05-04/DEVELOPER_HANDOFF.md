# Developer Handoff

Copy this into a fresh developer CLI/thread.

## Role

You are the developer thread. Implement only the attached implementation spec.
Do not use hidden assumptions from the main conversation.

## Required Reads

Read these files first:

- `contexts/task_runs/roster-v0_11_3-invocation-response-wrapper-2026-05-04/INTENT.md`
- `contexts/task_runs/roster-v0_11_3-invocation-response-wrapper-2026-05-04/CURRENT_STATE.md`
- `contexts/task_runs/roster-v0_11_3-invocation-response-wrapper-2026-05-04/IMPLEMENTATION_SPEC.md`

Optional supporting files:

- `contexts/artifact_harness_usage_experience/ROSTER_V0_11_3_INVOCATION_RESPONSE_WRAPPER.md`
- `contexts/artifact_harness_usage_experience/ROSTER_V0_11_2_RECEIPT_TRIGGER_CLARIFICATION.md`
- `contexts/artifact_harness_usage_experience/ROSTER_MILESTONE_ROADMAP.md`
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
- Keep first-touch UX unchanged.
- Do not implement runtime/subagent/web/browser/CV/plugin/connector adapters.
- Do not change health, install, or slash routing behavior.
- Do not push, tag, or release.
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

