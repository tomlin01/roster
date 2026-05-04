# Implementation Spec

Task ID: `roster-v0_11_3-invocation-response-wrapper-2026-05-04`
Parent Spec: `contexts/artifact_harness_usage_experience/ROSTER_V0_11_3_INVOCATION_RESPONSE_WRAPPER.md`
Intent Record: `contexts/task_runs/roster-v0_11_3-invocation-response-wrapper-2026-05-04/INTENT.md`
Current State: `contexts/task_runs/roster-v0_11_3-invocation-response-wrapper-2026-05-04/CURRENT_STATE.md`

## Objective

Implement the smallest useful Roster `v0.11.3` response-contract surface so
explicit Roster invocation produces Roster-shaped work for non-trivial tasks.

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
- `contexts/artifact_harness_usage_experience/ROSTER_V0_11_2_RECEIPT_TRIGGER_CLARIFICATION.md`
- `contexts/artifact_harness_usage_experience/ROSTER_V0_11_3_INVOCATION_RESPONSE_WRAPPER.md`
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

- State explicitly: `Explicit Roster invocation should produce Roster-shaped
  work`.
- Define explicit invocation as:
  - `Roster，...`
  - `Roster, ...`
  - `/roster ...`
  - `@roster ...`
  - installed Roster skill/plugin surface.
- For non-trivial explicit Roster tasks, require the wrapper:
  `entry framing -> useful work -> role-action receipt -> convergence`.
- State that entry framing is not a heavy first-touch team explanation.
- State that useful work still comes first; do not expose internal governance
  before the answer.
- State that `不要展開 debug trace` keeps the wrapper short, not absent.
- State that generic next-prompt suggestions must not replace convergence.
- State that optional next phrase can appear only after a convergence line and
  only when useful.
- Preserve `v0.11.2` receipt trigger rules.
- Add qualifying signals for wrapper use:
  - non-trivial explicit Roster task;
  - multiple dimensions or perspectives;
  - plan, roadmap, review, acceptance decision, artifact recommendation, or
    quality/domain/risk judgment.
- Add a good example based on the dashboard/product-plan failure pattern.
- Add bad examples:
  - generic assistant answer without wrapper;
  - implementation-machinery phrase such as `使用 Roster skill`;
  - next prompt replacing convergence.

Structure requirements:

- Put the primary wrapper rule near the existing completion reply contract in
  `skills/roster/SKILL.md`.
- Mirror the rule in `/roster` command docs so plugin invocation has the same
  behavior.
- Update README or target UX docs so humans can understand the distinction
  between first-touch, wrapper, receipt, and debug trace.
- Keep `ROSTER_V0_11_3_INVOCATION_RESPONSE_WRAPPER.md` as the rationale and
  observed failure record.

Wording requirements:

- Use `Invocation Response Wrapper`.
- Use `Explicit Roster invocation should produce Roster-shaped work`.
- Use `entry framing -> useful work -> role-action receipt -> convergence`.
- Use `Explicit Roster invocation != generic assistant answer`.
- Use `Do not substitute a next prompt for convergence`.
- Avoid internal governance terms in ordinary examples.
- Do not claim separate runtime agents were used unless evidence exists.

## Non-Goals

Do not do these in this pass:

- Make every Roster reply long.
- Add full trace output to ordinary replies.
- Change install, health, or slash routing behavior.
- Implement runtime/subagent enforcement.
- Add new tool capabilities.
- Create a release or tag.
- Push to GitHub.

## Acceptance Criteria

The task is complete when:

- Roster skill docs explicitly say explicit Roster invocation should produce
  Roster-shaped work.
- The wrapper rule appears in plugin and user-facing docs.
- Examples show entry framing, useful work, `本次分工執行`, and convergence.
- Bad examples call out generic assistant answers and next-prompt substitution.
- First-touch remains short and does not leak internal governance.
- Docs do not imply runtime/subagent execution.
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

- Ordinary examples include compact entry framing.
- Ordinary examples include `本次分工執行` when multiple perspectives contributed.
- Ordinary examples end with convergence, not only a suggested next prompt.
- Ordinary examples do not include internal governance terms.
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

