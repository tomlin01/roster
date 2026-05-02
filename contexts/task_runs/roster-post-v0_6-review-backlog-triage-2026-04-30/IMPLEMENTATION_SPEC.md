# Implementation Spec

Task ID: `roster-post-v0_6-review-backlog-triage-2026-04-30`
Parent Spec: `none`
Intent Record: `/Users/tom/Documents/PHD/codex-cns/contexts/task_runs/roster-post-v0_6-review-backlog-triage-2026-04-30/INTENT.md`
Current State: `/Users/tom/Documents/PHD/codex-cns/contexts/task_runs/roster-post-v0_6-review-backlog-triage-2026-04-30/CURRENT_STATE.md`

## Objective

Implement this specific change:

```text
Triage the attached historical review findings against Roster v0.6.0, then fix only still-current directly reproducible P1/P2 issues without widening Roster's architecture.
```

## Work Type

Select the closest type:

- `code`
- `tests`
- `docs`
- `governance`

## Scope

Allowed scope:

- `scripts/system_hub.py`
- `scripts/test_system_hub.py`
- `contexts/team_alias_registry.json`
- `policy/system_hub.toml`
- `agents/native/hr.md`
- `teams/human-resources/TEAM.md`
- `templates/artifact_harness/artifact_harness_spec.template.md`
- `templates/team_architect/capability_access_packet.template.md`
- `templates/team_architect/open_multi_agent_runtasks_mapping.template.md`
- `policy/ARTIFACT_HARNESS_WORKFLOW_V0.md`
- `policy/MULTI_AGENT_RUNTIME_ADAPTERS_V0.md`
- `README.md`
- `skills/roster/SKILL.md`
- `plugins/roster/`
- This packet directory.

Forbidden scope:

- Do not edit `/Users/tom/.codex/config.toml` or installed local plugin state as part of the repo patch.
- Do not rewrite historical developer reports unless the task explicitly becomes documentation cleanup.
- Do not change third-party reference files.
- Do not create a persistent server, daemon, database, or separate orchestration UI.
- Do not change Roster release tags without explicit user approval.

## Requirements

Behavior or content requirements:

- Build a finding triage matrix with statuses: `fixed`, `stale`, `current`, `needs split`, or `cannot reproduce`.
- Reproduce or invalidate the preference-memory findings:
  - `Roster, 記住以後 Lecture1 的影片任務都先檢查文字遮擋` must route to `roster_preferences`, not artifact production.
  - Corrupt `contexts/roster_preferences.json` must be surfaced in `packet-route --json` as a non-blocking diagnostic.
- Reproduce or invalidate the Quality findings:
  - Concrete artifact production with Quality wording must still route to the SPEC-first artifact workflow.
  - Common self-check phrasing including `檢查`, `check`, and `做` must route to Quality direction when no concrete deliverable is requested.
- Reproduce or invalidate packet workflow findings:
  - Runtime mapping must be traceable to CAP.
  - CAP must not own runtime selection or artifact verification.
  - Approval-gated execution must not claim CLI enforcement when TypeScript API is required.
  - The workflow policy must define provenance, instantiation, output location, and naming if current docs still lack them.
- Reproduce or invalidate UX findings:
  - Keyword aliases must route beyond HR where documented.
  - There must be an artifact packet assembly entrypoint.
  - HR must preserve staffing-only ownership and SPEC-first handoff.
  - User-facing README must give concrete invocation, install, workspace, and debug guidance.

Structure requirements:

- If code changes are needed, add regression tests for each still-current routing defect.
- If docs/templates are changed, keep ownership boundaries explicit and avoid turning CAP, HR, runtime adapters, or Roster into overlapping governance owners.
- Produce a short report under this packet directory, for example `TRIAGE_RESULT.md`.

Wording requirements:

- Use user-facing `Roster` language in public docs.
- Keep internal terms such as Artifact Harness, HR, Team Architect, CAP, and runtime adapter in governance or developer docs only.
- Do not claim `@roster` or `/roster` works in a UI unless the statement is scoped to installed local plugin surface plus Codex reload/UI verification.

## Non-Goals

Do not do these in this pass:

- Do not redesign the Artifact Harness workflow.
- Do not create a new Roster product layer.
- Do not replace the existing packet engine.
- Do not move historical files only to make old review comments disappear.
- Do not broaden Quality into artifact acceptance ownership; Quality should inform checks and iterations, while acceptance remains governed by the task contract.

## Acceptance Criteria

The task is complete when:

- Each attached finding has a triage status with evidence.
- All still-current P1 findings are fixed or split with a concrete follow-up packet.
- Still-current P2 findings are either fixed, explicitly deferred, or split with a reason.
- Regression tests cover any fixed routing behavior.
- Validation commands pass or any failures are documented with risk.
- A reviewer can inspect `TRIAGE_RESULT.md` and the diff without reading this chat.

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

- Targeted `packet-route --json` outputs for preference-memory and Quality examples.
- Template files named in findings 5-8 and 13-14.
- User-facing README / skill / plugin docs for invocation and install claims.

If validation cannot run, explain why and what risk remains.

## Handoff Requirements

Developer final response must include:

- Changed files.
- Finding triage matrix.
- What was implemented.
- Validation commands and results.
- Any unresolved risks or questions.
- Whether the task is ready for review.
