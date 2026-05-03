# Implementation Spec

Task ID: `roster-v0_11_1-role-execution-receipt-2026-05-03`
Parent Spec: `contexts/artifact_harness_usage_experience/ROSTER_V0_11_1_ROLE_EXECUTION_RECEIPT.md`
Intent Record: `contexts/task_runs/roster-v0_11_1-role-execution-receipt-2026-05-03/INTENT.md`
Current State: `contexts/task_runs/roster-v0_11_1-role-execution-receipt-2026-05-03/CURRENT_STATE.md`

## Objective

Implement the smallest useful Roster `v0.11.1` response-contract surface for
Role Execution Receipts.

## Work Type

- `docs`
- `markdown`
- `governance`
- `tests` only if a small existing text audit is easy to extend

## Scope

Allowed scope:

- `skills/roster/SKILL.md`
- `plugins/roster/commands/roster.md`
- `README.md`
- `contexts/artifact_harness_usage_experience/README.md`
- `contexts/artifact_harness_usage_experience/README.target-user-experience.draft.md`
- `contexts/artifact_harness_usage_experience/ROSTER_MILESTONE_ROADMAP.md`
- `contexts/artifact_harness_usage_experience/ROSTER_NEXT_VERSION_DIRECTION.md`
- `contexts/artifact_harness_usage_experience/ROSTER_V0_11_1_ROLE_EXECUTION_RECEIPT.md`
- `contexts/artifact_harness_usage_experience/developer_reports/`
- `scripts/test_system_hub.py` only if adding a narrow text audit is clearly
  low-risk

Forbidden scope:

- new subagent runtime behavior
- new web-search, browser, screenshot, CV, connector, or plugin adapter
  implementation
- persistent server, daemon, database, or separate UI
- unrelated skills under `/Users/tom/.codex/skills`
- unrelated target workspaces such as `/Users/tom/Documents/PHD/Vis_Math`
- broad rename, package, release, or GitHub repository changes

## Requirements

Behavior or content requirements:

- Define `Role Execution Receipt` as the ordinary completion evidence layer
  after Roster has used multiple roles or meaningful perspectives.
- Preserve the three response layers:
  - first-touch reply;
  - ordinary completion reply;
  - review/debug/verification reply.
- Keep first-touch replies short and natural.
- Make ordinary completion replies follow:
  `outcome -> role actions -> convergence`.
- Add the label `本次分工執行` for ordinary completion receipts.
- State that receipts should list only roles that actually contributed.
- State that receipts should describe concrete behavior: checked, produced,
  compared, decided, inspected, verified, challenged, corrected, or converged.
- State that receipts should avoid title theater such as listing a reviewer
  without saying what was reviewed.
- State that Roster must distinguish role or perspective execution from actual
  runtime/subagent execution.
- State that if no separate runtime agent was spawned, Roster should say
  `角色分工` or `視角分工`, not claim multiple agents ran in parallel.
- State that missing capability should be surfaced when a role needed web,
  browser, CV, plugin, connector, or subagent capability but could not use it.
- State that full capability/source/assumption traces belong in review, debug,
  or verification mode, not ordinary completion replies.
- Keep the relationship to `v0.10.0` clear:
  `v0.10.0` plans capability needs; `v0.11.1` reports completed role behavior
  enough for the user to judge.

Structure requirements:

- Put the primary behavior contract in `skills/roster/SKILL.md`.
- Keep or refine the direction document so it remains the canonical
  rationale.
- Update public or target README guidance so a new user understands that later
  Roster replies may include a compact role-action receipt.
- Add at least one good example and one bad pattern.
- If updating plugin command docs, keep slash/mention/fallback claims truthful.

Wording requirements:

- Use `Role Execution Receipt`.
- Use `本次分工執行`.
- Use the concept `outcome -> role actions -> convergence`.
- Keep ordinary user-facing examples free of internal terms such as
  `Artifact Harness`, `HR`, `Team Architect`, `CAP`, `runtime adapter`,
  `control plane`, and `packet chain`.
- Do not overclaim that Roster actually spawned multiple runtime agents unless
  that is true in the described example.

## Non-Goals

Do not do these in this pass:

- Implement or require real subagent spawning.
- Implement a message bus, runtime adapter, or tool router.
- Change packet lifecycle behavior.
- Change install/uninstall behavior.
- Create broad new tests around runtime behavior.
- Make ordinary replies into complete audit logs.
- Rename Roster or change repository packaging.

## Acceptance Criteria

The task is complete when:

- `skills/roster/SKILL.md` documents how ordinary completion replies should
  include role-action receipts when appropriate.
- User-facing docs or README surfaces mention the receipt behavior without
  making first-touch UX heavier.
- Examples show role action and convergence, not just role titles.
- Docs explicitly distinguish role/perspective execution from actual runtime
  agent execution.
- Docs do not expose internal governance terms in ordinary examples.
- Validation commands pass or any unavailable command is explained.

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

- First-touch examples remain short and natural.
- Ordinary completion examples contain `本次分工執行`.
- Ordinary examples do not claim separate runtime agents without evidence.
- Review/debug examples can expand to role, capability, source, assumptions,
  and execution mode.

If validation cannot run, explain why and what risk remains.

## Handoff Requirements

Developer final response must include:

- Changed files.
- What was implemented.
- Whether any test or text audit was added or deferred.
- Validation commands and results.
- Any unresolved risks or questions.
- Whether the task is ready for review.

