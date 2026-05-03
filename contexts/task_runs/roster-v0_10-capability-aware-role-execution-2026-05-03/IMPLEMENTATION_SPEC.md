# Implementation Spec

Task ID: `roster-v0_10-capability-aware-role-execution-2026-05-03`
Parent Spec: `contexts/artifact_harness_usage_experience/ROSTER_V0_10_CAPABILITY_AWARE_ROLE_EXECUTION.md`
Intent Record: `contexts/task_runs/roster-v0_10-capability-aware-role-execution-2026-05-03/INTENT.md`
Current State: `contexts/task_runs/roster-v0_10-capability-aware-role-execution-2026-05-03/CURRENT_STATE.md`

## Objective

Implement the smallest useful Roster `v0.10.0` surface for
Capability-Aware Role Execution.

## Work Type

- `docs`
- `markdown`
- `templates`
- `tests`
- `governance`
- `code` only if needed for conservative `roster-health` capability reporting

## Scope

Allowed scope:

- `skills/roster/SKILL.md`
- `plugins/roster/commands/roster.md`
- `README.md`
- `AGENTS.md` if a repo-level note is needed
- `contexts/artifact_harness_usage_experience/README.md`
- `contexts/artifact_harness_usage_experience/README.target-user-experience.draft.md`
- `contexts/artifact_harness_usage_experience/ROSTER_MILESTONE_ROADMAP.md`
- `contexts/artifact_harness_usage_experience/ROSTER_NEXT_VERSION_DIRECTION.md`
- `contexts/artifact_harness_usage_experience/ROSTER_V0_10_CAPABILITY_AWARE_ROLE_EXECUTION.md`
- `templates/team_architect/team_operating_packet.template.md`
- optional new template under `templates/team_architect/`
- `scripts/system_hub.py`
- `scripts/test_system_hub.py`

Forbidden scope:

- new web-search, browser, screenshot, CV, or connector adapter implementation
- automatic connector login or external service actions
- persistent server, daemon, database, or separate orchestration UI
- Rust rewrite
- broad runtime adapter rewrite
- unrelated skill repos under `/Users/tom/.codex/skills`

## Requirements

Behavior or content requirements:

- Define `Capability-Aware Role Execution` as:
  `role -> work -> interaction -> capability need -> availability -> fallback`.
- State that Roster identifies capability needs, CAP authorizes access, and
  runtime/host executes.
- Treat subagents as a capability category, not the primary v0.10 headline.
- Preserve perspective separation: if a role is not split into a subagent, its
  perspective should still be explicit.
- Add capability categories:
  - `reasoning_only`
  - `filesystem_read`
  - `filesystem_write`
  - `code_execution`
  - `web_search`
  - `browser`
  - `visual_capture`
  - `vision_review`
  - `specialist_skill`
  - `plugin_or_connector`
  - `subagent_execution`
- Add availability states:
  - `available`
  - `available_after_reload`
  - `available_if_approved`
  - `unknown`
  - `unavailable`
- Add or update work-card fields/fill notes so roles can carry capability
  needs, purpose, availability, evidence expected, and fallback.
- Include examples for:
  - Research Reviewer needing web/browser.
  - Visual QA needing visual capture/CV/browser.
  - Slide Producer needing specialist skill/plugin/filesystem write.
  - Skill Reviewer needing filesystem read and optional patch capability.
  - Statistical Reviewer needing code execution/statistics skill.
- Add a conservative `roster-health` capability summary if practical. It should
  never overclaim host-dependent tools. Use `unknown` when local evidence is
  insufficient.

Structure requirements:

- Keep ordinary user-facing examples short and non-mechanical.
- Keep detailed capability matrices in internal docs/templates, not first-touch
  examples.
- If adding JSON output to `roster-health`, use stable keys and test them.
- If adding a new template, keep it under `templates/team_architect/` and make
  it clearly advisory/fillable, not executable authorization.

Wording requirements:

- Use `Capability-Aware Role Execution`.
- Use: `Roster plans capability needs; CAP authorizes access; runtime executes.`
- Do not say Roster has web search, browser, CV, connector, or subagent support
  as a universal built-in.
- Prefer `host capability`, `platform capability`, or `active runtime
  capability` over claiming Roster owns the tool.
- Keep `CAP` references boundary-focused, not user-facing first-touch wording.

## Non-Goals

Do not do these in this pass:

- Implement web search, browser, CV, screenshot, or connector adapters.
- Create automatic external actions.
- Guarantee behavior across all LLM hosts.
- Force every role into a separate subagent.
- Replace CAP authorization or runtime adapter policy.
- Modify unrelated skills.
- Implement Team Review Mode beyond preserving the note as future validation.

## Acceptance Criteria

The task is complete when:

- Roster skill/plugin docs explain capability-aware role execution and preserve
  first-touch UX boundaries.
- Team Operating Packet or a related template can express role capability
  needs, availability, evidence expected, and fallback.
- `roster-health` either exposes a conservative capability summary with tests,
  or the developer explicitly explains why this is deferred.
- Docs do not overclaim that Roster ships web/browser/CV/subagent adapters.
- Subagents are treated as conditional capability use.
- Validation commands pass.

## Validation Plan

Run:

```sh
python3 -m py_compile scripts/system_hub.py scripts/test_system_hub.py
python3 scripts/test_system_hub.py
python3 scripts/test_overlay_policy.py
python3 scripts/test_run_agent_benchmark.py
python3 -m json.tool contexts/team_alias_registry.json
git diff --check
```

Also inspect:

- First-touch examples do not expose capability matrices by default.
- Capability need does not imply authorization.
- Health/capability output, if implemented, is conservative for host-dependent
  capabilities.

If validation cannot run, explain why and what risk remains.

## Handoff Requirements

Developer final response must include:

- Changed files.
- What was implemented.
- Whether `roster-health` capability reporting was implemented or deferred.
- Validation commands and results.
- Any unresolved risks or questions.
- Whether the task is ready for review.
