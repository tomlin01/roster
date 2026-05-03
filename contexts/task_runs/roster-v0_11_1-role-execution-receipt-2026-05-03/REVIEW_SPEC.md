# Review Spec

Task ID: `roster-v0_11_1-role-execution-receipt-2026-05-03`
Intent Record: `contexts/task_runs/roster-v0_11_1-role-execution-receipt-2026-05-03/INTENT.md`
Implementation Spec: `contexts/task_runs/roster-v0_11_1-role-execution-receipt-2026-05-03/IMPLEMENTATION_SPEC.md`
Current State: `contexts/task_runs/roster-v0_11_1-role-execution-receipt-2026-05-03/CURRENT_STATE.md`
Diff or PR: `git diff`

## Review Role

You are the reviewer thread. Review the result against the user's intent and
implementation spec. Do not rewrite unless explicitly asked.

## Review Inputs

Required:

- Intent record.
- Implementation spec.
- Current state.
- Git diff or changed files.
- Developer final response.
- Validation evidence.

Optional:

- `contexts/artifact_harness_usage_experience/ROSTER_V0_11_1_ROLE_EXECUTION_RECEIPT.md`
- `skills/roster/SKILL.md`
- `README.md`
- `plugins/roster/commands/roster.md`

## Review Checklist

Check:

- Intent fidelity: does the result let users judge whether declared roles
  actually did work?
- First-touch preservation: did it avoid making first-touch replies heavier?
- Later-response style: does it preserve Roster's agent-coordination identity?
- Requirement coverage: are `Role Execution Receipt`, `本次分工執行`, and
  `outcome -> role actions -> convergence` represented?
- Scope control: did it avoid runtime, adapter, subagent, install, packaging, or
  unrelated skill changes?
- Runtime honesty: does it avoid implying separate subagents ran unless true?
- User-facing clarity: do ordinary examples avoid internal terms such as
  Artifact Harness, HR, Team Architect, CAP, runtime adapter, control plane, and
  packet chain?
- Evidence discipline: do examples distinguish source-backed findings,
  capability limitations, and simulated perspectives where appropriate?
- Acceptance: are all acceptance criteria satisfied?
- Validation: did the developer run appropriate commands, or clearly explain
  gaps?

## Severity Scale

- P0: blocks use or violates a hard boundary.
- P1: likely incorrect result, misleading runtime claim, or serious workflow
  break.
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

