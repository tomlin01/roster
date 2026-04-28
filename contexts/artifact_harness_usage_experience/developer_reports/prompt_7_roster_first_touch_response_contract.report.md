# Prompt 7 Report: Roster First-Touch Response Contract

## Findings Addressed

- Added a first-touch reply contract to `skills/roster/SKILL.md`.
- Updated the root `README.md` first-screen example so the initial response is short, user-facing, and does not expose internal control-plane roles.
- Updated target README guidance so specialized aliases and internal packet names are not first-screen material.
- Added UX-008 to the usage-experience log for the Lecture1 team-roster response issue.
- Preserved the internal governance boundaries; this change is presentation behavior only.

## Changed Files

- `skills/roster/SKILL.md`
- `README.md`
- `contexts/artifact_harness_usage_experience/README.target-user-experience.draft.md`
- `contexts/artifact_harness_usage_experience/TARGET_README_INSTRUCTION.md`
- `contexts/artifact_harness_usage_experience/README.md`
- `contexts/artifact_harness_usage_experience/developer_reports/prompt_7_roster_first_touch_response_contract.prompt.md`
- `contexts/artifact_harness_usage_experience/developer_reports/prompt_7_roster_first_touch_response_contract.report.md`

## Behavior Now Specified

Ordinary first-touch Roster replies should:

- lead with the completed user-facing outcome
- show only task-relevant working roles
- keep role descriptions short
- provide one next invocation phrase
- add at most one durable file link at the end

They should not mention `HR`, `Team Architect`, `Artifact Harness`, `CAP`, runtime adapter, control plane, packet chain, or continuity receipt unless the user asks for review/debug/governance detail.

They should not frame current-turn scope as a capability limit. If this turn only prepared a roster, it should still make clear that future Roster runs can assign scene, render, video, QA, or other artifact work.

## Verification Results

Passed:

- `python3 -m py_compile scripts/system_hub.py scripts/test_system_hub.py`
- `python3 scripts/test_system_hub.py`
- `git diff --check`

Text audit:

- First-touch examples now avoid exposing `HR`, `Team Architect`, `Artifact Harness`, `CAP`, runtime adapter, control plane, or continuity receipt.
- Internal governance sections still retain those terms where appropriate.
- The Lecture1 example no longer says or implies Roster cannot execute future slide/scene/render/video work.

## Execution Note

An attempted `codex exec` developer run failed because the sandboxed process could not create or access `/Users/tom/.codex/sessions`. The repo edits were completed directly in the current workspace instead.

