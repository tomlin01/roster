# Implementation Spec

Task ID: `roster-v0_7-first-touch-ux-contract-2026-05-02`
Parent Spec: `/Users/tom/Documents/PHD/codex-cns/contexts/artifact_harness_usage_experience/ROSTER_MILESTONE_ROADMAP.md`
Intent Record: `/Users/tom/Documents/PHD/codex-cns/contexts/task_runs/roster-v0_7-first-touch-ux-contract-2026-05-02/INTENT.md`
Current State: `/Users/tom/Documents/PHD/codex-cns/contexts/task_runs/roster-v0_7-first-touch-ux-contract-2026-05-02/CURRENT_STATE.md`

## Objective

Implement this specific change:

```text
Make Roster first-touch replies natural, short, role-shaped, and complexity-aware without exposing internal governance or implementing deeper role-engine behavior.
```

## Work Type

Select the closest type:

- `docs`
- `markdown`
- `tests`
- `code` only if existing route/help/health output needs small support changes

## Scope

Allowed scope:

- `skills/roster/SKILL.md`
- `plugins/roster/commands/roster.md`
- `README.md`
- `contexts/artifact_harness_usage_experience/README.md`
- `contexts/artifact_harness_usage_experience/README.target-user-experience.draft.md`
- `contexts/artifact_harness_usage_experience/ROSTER_NEXT_VERSION_DIRECTION.md`
- `contexts/artifact_harness_usage_experience/ROSTER_MILESTONE_ROADMAP.md`
- `contexts/artifact_harness_usage_experience/developer_reports/prompt_v0_7_first_touch_ux_contract.prompt.md`
- `scripts/system_hub.py`
- `scripts/test_system_hub.py`
- this packet directory

Forbidden scope:

- Do not implement full Role Interaction Patterns.
- Do not change Team Operating Packet schema for `v0.7.0`.
- Do not implement automatic subagent spawning.
- Do not add project/team mode.
- Do not rewrite runtime adapter architecture.
- Do not edit installed local state under `/Users/tom/.codex/`.

## Requirements

Behavior or content requirements:

- Add a first-touch response contract for Roster.
- Preserve layer coverage while keeping the ordinary reply lightweight.
- Make complexity handling visible through plain phrasing, not labels.
- Include natural Traditional Chinese meeting-note examples using:
  - `轉錄人員`
  - `會議紀錄人員`
  - `會議負責人`
- Let users adjust roles through ordinary phrases such as:
  - `加一個主管`
  - `讓 PM 看一下`
  - `需要法務審`
  - `加一個學生視角`
- Keep `Roster, ...` as the stable fallback invocation.
- Keep installed `@roster` and `/roster` claims scoped to `roster-install`,
  Codex reload, and supported host behavior.

Structure requirements:

- Public docs should lead with practical use, not governance terminology.
- Skill and slash command docs should instruct the active model to choose the
  smallest useful first-touch response.
- Tests or text audits should catch internal-governance leakage in ordinary
  examples.

Wording requirements:

- Do not expose `Artifact Harness`, `HR`, `Team Architect`, `CAP`, runtime
  adapter, packet chain, or control-plane terms in ordinary first-touch examples.
- Do not show `Level 1`, `Level 2`, `complexity score`, or similar terms to
  ordinary users.
- Use real role names instead of abstract work-function labels when examples
  have a clear domain.

## Non-Goals

Do not do these in this pass:

- full role contextualization engine;
- role interaction edge storage;
- subagent policy implementation;
- project/team mode;
- release tagging;
- large README rewrite unrelated to first-touch UX.

## Acceptance Criteria

The task is complete when:

- `skills/roster/SKILL.md` includes the first-touch UX contract.
- `plugins/roster/commands/roster.md` includes the same ordinary-response
  guidance.
- Public/usage docs include concise examples for complexity-aware first-touch
  replies.
- Text audit confirms ordinary examples do not leak internal governance terms.
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

- Ordinary first-touch examples do not expose internal governance terms.
- Complexity examples do not show `Level 1` / `Level 2` labels in the
  user-facing response body.
- Meeting-note examples use `轉錄人員`, `會議紀錄人員`, and `會議負責人`.
- `@roster` / `/roster` support is caveated truthfully.

If validation cannot run, explain why and what risk remains.

## Handoff Requirements

Developer final response must include:

- Changed files.
- Implemented first-touch behavior.
- Validation commands and results.
- Remaining risks.
- Whether the task is ready for review.
