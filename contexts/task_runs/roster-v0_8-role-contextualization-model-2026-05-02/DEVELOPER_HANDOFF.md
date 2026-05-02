# Developer Handoff

Copy this into a fresh developer CLI/thread.

## Role

You are the developer thread. Implement only the attached implementation spec.
Do not use hidden assumptions from the main conversation.

## Required Reads

Read these files first:

- `/Users/tom/Documents/PHD/codex-cns/contexts/task_runs/roster-v0_8-role-contextualization-model-2026-05-02/INTENT.md`
- `/Users/tom/Documents/PHD/codex-cns/contexts/task_runs/roster-v0_8-role-contextualization-model-2026-05-02/CURRENT_STATE.md`
- `/Users/tom/Documents/PHD/codex-cns/contexts/task_runs/roster-v0_8-role-contextualization-model-2026-05-02/IMPLEMENTATION_SPEC.md`

Supporting files:

- `/Users/tom/Documents/PHD/codex-cns/contexts/artifact_harness_usage_experience/ROSTER_NEXT_VERSION_DIRECTION.md`
- `/Users/tom/Documents/PHD/codex-cns/contexts/artifact_harness_usage_experience/ROSTER_MILESTONE_ROADMAP.md`
- `/Users/tom/Documents/PHD/codex-cns/contexts/artifact_harness_usage_experience/developer_reports/prompt_v0_8_role_contextualization_model.prompt.md`
- `/Users/tom/Documents/PHD/codex-cns/skills/roster/SKILL.md`
- `/Users/tom/Documents/PHD/codex-cns/plugins/roster/commands/roster.md`
- `/Users/tom/Documents/PHD/codex-cns/README.md`

## Execution Rules

- Follow the implementation spec literally.
- Keep this pass scoped to `v0.8.0` Role Contextualization Model.
- Make the smallest correct change.
- Do not implement Role Interaction Patterns, subagent spawning, persistent role
  storage, or project/team mode.
- Preserve truthful caveats around `@roster` and `/roster`.
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

Validation:
- <command>: <result>

Risks or blockers:
- <item-or-none>

Ready for review:
- <yes/no>
```
