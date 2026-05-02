# Developer Handoff

Copy this into a fresh developer CLI/thread.

## Role

You are the developer thread. Implement only the attached implementation spec. Do not use hidden assumptions from the main conversation.

## Required Reads

Read these files first:

- `/Users/tom/Documents/PHD/codex-cns/contexts/task_runs/roster-post-v0_6-review-backlog-triage-2026-04-30/INTENT.md`
- `/Users/tom/Documents/PHD/codex-cns/contexts/task_runs/roster-post-v0_6-review-backlog-triage-2026-04-30/CURRENT_STATE.md`
- `/Users/tom/Documents/PHD/codex-cns/contexts/task_runs/roster-post-v0_6-review-backlog-triage-2026-04-30/IMPLEMENTATION_SPEC.md`

Optional supporting files:

- `/Users/tom/Documents/PHD/codex-cns/README.md`
- `/Users/tom/Documents/PHD/codex-cns/AGENTS.md`
- `/Users/tom/Documents/PHD/codex-cns/scripts/system_hub.py`
- `/Users/tom/Documents/PHD/codex-cns/scripts/test_system_hub.py`
- `/Users/tom/Documents/PHD/codex-cns/templates/team_architect/open_multi_agent_runtasks_mapping.template.md`
- `/Users/tom/Documents/PHD/codex-cns/templates/team_architect/capability_access_packet.template.md`
- `/Users/tom/Documents/PHD/codex-cns/templates/artifact_harness/artifact_harness_spec.template.md`
- `/Users/tom/Documents/PHD/codex-cns/policy/ARTIFACT_HARNESS_WORKFLOW_V0.md`

## Execution Rules

- Follow the implementation spec literally.
- Use the current state file to avoid redoing completed work.
- Preserve user intent from the intent record.
- Make the smallest correct change.
- Do not widen scope.
- If a finding is stale, mark it stale with evidence instead of changing files.
- If the spec is impossible or contradictory, stop and report the blocker.

## Validation

Run the validation plan from the implementation spec.

If you add or change tests, run the smallest relevant test set first.

## Final Response Format

Return:

```text
Changed files:
- <path>

Finding triage:
- <finding-id>: <fixed/stale/current/needs split/cannot reproduce> - <evidence>

Implemented:
- <item>

Validation:
- <command>: <result>

Risks or blockers:
- <item-or-none>

Ready for review:
- <yes/no>
```
