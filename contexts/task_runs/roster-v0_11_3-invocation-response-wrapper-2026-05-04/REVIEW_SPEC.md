# Review Spec

Task ID: `roster-v0_11_3-invocation-response-wrapper-2026-05-04`
Intent Record: `contexts/task_runs/roster-v0_11_3-invocation-response-wrapper-2026-05-04/INTENT.md`
Implementation Spec: `contexts/task_runs/roster-v0_11_3-invocation-response-wrapper-2026-05-04/IMPLEMENTATION_SPEC.md`
Current State: `contexts/task_runs/roster-v0_11_3-invocation-response-wrapper-2026-05-04/CURRENT_STATE.md`
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

- `contexts/artifact_harness_usage_experience/ROSTER_V0_11_3_INVOCATION_RESPONSE_WRAPPER.md`
- `skills/roster/SKILL.md`
- `README.md`
- `plugins/roster/commands/roster.md`

## Review Checklist

Check:

- Intent fidelity: does the result fix the user's complaint that Roster answers
  still feel generic?
- Invocation trigger: does it clearly state explicit Roster invocation should
  produce Roster-shaped work?
- Wrapper shape: does it include
  `entry framing -> useful work -> role-action receipt -> convergence`?
- Entry framing: does it distinguish compact entry framing from heavy
  first-touch/team explanation?
- Useful work: does it avoid putting internal governance before the answer?
- Receipt: does it preserve `本次分工執行` for qualifying tasks?
- Convergence: does it prevent generic next prompts from replacing convergence?
- Scope control: did it avoid runtime, subagent, install, health, slash-routing,
  and adapter behavior changes?
- User-facing examples: do ordinary examples avoid internal governance terms and
  misleading runtime-agent claims?
- Validation: did the developer run the required commands or explain gaps?

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

