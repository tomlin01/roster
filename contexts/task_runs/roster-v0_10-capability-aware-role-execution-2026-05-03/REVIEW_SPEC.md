# Review Spec

Task ID: `roster-v0_10-capability-aware-role-execution-2026-05-03`
Intent Record: `contexts/task_runs/roster-v0_10-capability-aware-role-execution-2026-05-03/INTENT.md`
Implementation Spec: `contexts/task_runs/roster-v0_10-capability-aware-role-execution-2026-05-03/IMPLEMENTATION_SPEC.md`
Current State: `contexts/task_runs/roster-v0_10-capability-aware-role-execution-2026-05-03/CURRENT_STATE.md`
Diff or PR: `current branch diff`

## Review Role

You are the reviewer thread. Review the result against the user's intent and
implementation spec. Do not rewrite unless explicitly asked.

## Review Inputs

Required:

- Intent record.
- Implementation spec.
- Current state.
- Git diff, PR, or changed files.
- Validation evidence.

Optional:

- Developer final response.
- `ROSTER_V0_10_CAPABILITY_AWARE_ROLE_EXECUTION.md`
- `ROSTER_SKILL_INTEROP_NOTE.md`

## Review Checklist

Check:

- Intent fidelity: does the result implement capability-aware role execution,
  not merely subagent policy?
- Scope control: did it avoid new web/browser/CV/connector/runtime adapters?
- Boundary discipline: does it preserve `Roster plans needs; CAP authorizes;
  runtime executes`?
- Requirement coverage: are capability categories and availability states
  present where needed?
- Work-card/template coverage: can role capability needs, evidence expected,
  availability, and fallback be represented?
- Health output: if implemented, is it conservative and tested? If deferred, is
  the reason explicit?
- First-touch UX: ordinary examples should not expose capability matrices or
  internal governance terms.
- Unsupported claims: no claim that Roster universally owns web search,
  browser, CV, connectors, or subagents.
- Validation: did required checks run and support the report?

## Severity Scale

- P0: blocks use or violates a hard boundary.
- P1: likely incorrect result, data loss, or serious workflow break.
- P2: important fix before merge or handoff.
- P3: minor issue, cleanup, or follow-up.

## Output Format

Return findings first:

```text
Findings:
- [P<level>] <title> - <file:line> - <explanation>

Open questions:
- <question-or-none>

Validation gaps:
- <gap-or-none>

Verdict:
- <accept / fix-before-accept / narrow-scope / split-task / return-to-main>
```
