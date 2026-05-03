# Implementation Spec

Task ID: `roster-v0_11_2-receipt-trigger-clarification-2026-05-04`
Parent Spec: `contexts/artifact_harness_usage_experience/ROSTER_V0_11_2_RECEIPT_TRIGGER_CLARIFICATION.md`
Intent Record: `contexts/task_runs/roster-v0_11_2-receipt-trigger-clarification-2026-05-04/INTENT.md`
Current State: `contexts/task_runs/roster-v0_11_2-receipt-trigger-clarification-2026-05-04/CURRENT_STATE.md`

## Objective

Implement the smallest useful Roster `v0.11.2` contract patch so ordinary
Role Execution Receipt is not omitted as if it were debug trace.

## Work Type

- `docs`
- `markdown`
- `governance`
- `tests` only if a narrow text audit is low-risk

## Scope

Allowed scope:

- `skills/roster/SKILL.md`
- `plugins/roster/commands/roster.md`
- `README.md`
- `contexts/artifact_harness_usage_experience/README.md`
- `contexts/artifact_harness_usage_experience/README.target-user-experience.draft.md`
- `contexts/artifact_harness_usage_experience/ROSTER_MILESTONE_ROADMAP.md`
- `contexts/artifact_harness_usage_experience/ROSTER_V0_11_1_ROLE_EXECUTION_RECEIPT.md`
- `contexts/artifact_harness_usage_experience/ROSTER_V0_11_2_RECEIPT_TRIGGER_CLARIFICATION.md`
- `contexts/artifact_harness_usage_experience/developer_reports/`
- `scripts/test_system_hub.py` only for a very small text audit if clearly
  useful and low-risk

Forbidden scope:

- `scripts/system_hub.py` behavior changes
- new runtime enforcement
- subagent runtime implementation
- web/browser/CV/plugin/connector adapter implementation
- install/uninstall behavior changes
- health-check behavior changes
- slash routing behavior changes
- unrelated skills under `/Users/tom/.codex/skills`
- broad release/tag/push work

## Requirements

Behavior or content requirements:

- State explicitly: `Role Execution Receipt is part of the ordinary completion
  reply, not debug trace`.
- State explicitly: if a task qualifies for a receipt, `不要展開完整 debug trace`
  means keep the receipt short, not remove it.
- State explicitly: if the answer discusses role-summary as a future product
  feature, it still needs a current-turn receipt when the answer itself used
  multiple roles or perspectives.
- State explicitly: task simplicity changes receipt length, not the trigger.
- Define qualifying signals:
  - user asks Roster to consider multiple dimensions;
  - answer uses multiple roles, perspectives, or checks;
  - result includes product, engineering, quality, domain, source, visual, or
    risk judgment;
  - user needs to judge whether declared roles actually did work.
- Preserve the default receipt shape:
  `本次分工執行` plus role-action lines and optional `最後收斂`.
- Keep full capability/source/assumption/reviewer trace out of ordinary
  completion replies.
- Add a good example based on the two-week product plan failure pattern.
- Add a bad pattern that shows only planning a future role-summary feature
  without current-turn receipt.

Structure requirements:

- Put the primary trigger rule near the existing completion reply contract in
  `skills/roster/SKILL.md`.
- Mirror the rule in `/roster` command docs so plugin invocation has the same
  behavior.
- Update README or target UX docs so a human understands receipt is not debug
  trace.
- Keep `ROSTER_V0_11_2_RECEIPT_TRIGGER_CLARIFICATION.md` as the rationale and
  observed failure record.

Wording requirements:

- Use `Receipt Trigger Clarification`.
- Use `Role Execution Receipt is part of the ordinary completion reply, not
  debug trace`.
- Use `No debug trace != no receipt`.
- Use `Future role-summary feature != current-turn receipt`.
- Use `Simple qualifying task != no receipt`.
- Do not expose internal governance terms in ordinary user-facing examples.
- Do not claim separate runtime agents were used unless evidence exists.

## Non-Goals

Do not do these in this pass:

- Make every response include a receipt.
- Add full trace output to ordinary replies.
- Change first-touch behavior.
- Change health wording or install output.
- Implement runtime/subagent enforcement.
- Add new tool capabilities.
- Create a release or tag.

## Acceptance Criteria

The task is complete when:

- Roster skill docs explicitly say receipt is ordinary completion evidence, not
  debug trace.
- The rule is mirrored in plugin and user-facing docs.
- The observed two-week product-plan failure pattern is covered by good/bad
  examples.
- Docs clearly say `不要展開 debug trace` does not remove a qualifying receipt.
- Docs clearly say future role-summary feature planning does not replace the
  answer's current-turn receipt.
- First-touch UX remains unaffected.
- Validation commands pass or gaps are explained.

## Validation Plan

Run:

```sh
python3 -m py_compile scripts/system_hub.py scripts/test_system_hub.py
python3 scripts/test_system_hub.py
git diff --check
```

If the developer touches policy-sensitive files or tests, also run:

```sh
python3 scripts/test_overlay_policy.py
python3 scripts/test_run_agent_benchmark.py
python3 -m json.tool contexts/team_alias_registry.json
```

Also inspect:

- Ordinary examples include `本次分工執行` where the task has multiple
  perspectives.
- Ordinary examples do not include internal governance terms.
- `do not expand debug trace` is represented as short receipt, not no receipt.
- The change does not imply runtime/subagent execution.

If validation cannot run, explain why and what risk remains.

## Handoff Requirements

Developer final response must include:

- Changed files.
- What was implemented.
- Whether any text audit or test was added or deferred.
- Validation commands and results.
- Any unresolved risks or questions.
- Whether the task is ready for review.

