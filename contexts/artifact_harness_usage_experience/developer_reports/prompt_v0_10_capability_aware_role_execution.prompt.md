# Prompt v0.10.0: Capability-Aware Role Execution

## Context

Roster `v0.9.0` added Role Interaction Patterns:

```text
role -> work card -> interaction edge
```

The next issue is execution planning. A role may need web search, browser,
visual capture, CV, filesystem/code execution, specialist skills, plugins,
connectors, or subagents. The user should not need to manually decide which
role gets which LLM platform tool.

The direction has been documented in:

- `contexts/artifact_harness_usage_experience/ROSTER_V0_10_CAPABILITY_AWARE_ROLE_EXECUTION.md`

## Goal

Implement the smallest useful Roster `v0.10.0` surface:

```text
Capability-Aware Role Execution
```

Core chain:

```text
role -> work -> interaction -> capability need -> availability -> fallback
```

## Required Packet

Read and follow:

- `contexts/task_runs/roster-v0_10-capability-aware-role-execution-2026-05-03/INTENT.md`
- `contexts/task_runs/roster-v0_10-capability-aware-role-execution-2026-05-03/CURRENT_STATE.md`
- `contexts/task_runs/roster-v0_10-capability-aware-role-execution-2026-05-03/IMPLEMENTATION_SPEC.md`

Use:

- `contexts/task_runs/roster-v0_10-capability-aware-role-execution-2026-05-03/DEVELOPER_HANDOFF.md`

for execution rules and final response format.

## Hard Boundaries

- Do not implement a new web-search adapter.
- Do not implement browser/CV/screenshot connector logic.
- Do not add automatic connector login or external actions.
- Do not create a new runtime architecture.
- Do not force every role into a subagent.
- Do not replace CAP authorization with Roster planning.
- Do not claim host-dependent tools are available unless local evidence proves
  availability; use `unknown` where appropriate.

## Expected Result

The implementation should make Roster able to express that a role needs a
platform capability and what fallback applies when the capability is absent.

Subagents should be documented as one capability category, not the headline.

`roster-health` should expose a conservative capability summary if practical;
if not, explicitly defer it with a reason.

## Validation

Run:

```sh
python3 -m py_compile scripts/system_hub.py scripts/test_system_hub.py
python3 scripts/test_system_hub.py
python3 scripts/test_overlay_policy.py
python3 scripts/test_run_agent_benchmark.py
python3 -m json.tool contexts/team_alias_registry.json
git diff --check
```
