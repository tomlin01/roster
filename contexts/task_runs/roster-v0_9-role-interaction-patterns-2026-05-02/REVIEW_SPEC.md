# Review Spec

Task ID: `roster-v0_9-role-interaction-patterns-2026-05-02`
Intent Record: `/Users/tom/Documents/PHD/codex-cns/contexts/task_runs/roster-v0_9-role-interaction-patterns-2026-05-02/INTENT.md`
Implementation Spec: `/Users/tom/Documents/PHD/codex-cns/contexts/task_runs/roster-v0_9-role-interaction-patterns-2026-05-02/IMPLEMENTATION_SPEC.md`
Current State: `/Users/tom/Documents/PHD/codex-cns/contexts/task_runs/roster-v0_9-role-interaction-patterns-2026-05-02/CURRENT_STATE.md`
Diff or PR: `local branch or PR after implementation`

## Review Role

You are the reviewer thread. Review the result against the user's intent and
implementation spec. Do not rewrite unless explicitly asked.

## Review Inputs

Required:

- Intent record.
- Implementation spec.
- Current state.
- Git diff, PR, or changed files.
- Developer final response and validation evidence.

Optional:

- Related issue or ticket.
- Behavior validation records.

## Review Checklist

Check:

- Intent fidelity: does the result move from work cards to role interaction
  patterns?
- Scope control: did it avoid subagent policy, runtime behavior, message bus,
  CAP changes, approval execution, and real artifact production?
- Requirement coverage: are all required interaction types defined?
- Template usability: can Team Operating Packet distinguish roles, work cards,
  and interaction edges?
- Boundary clarity: do interaction edges alter task graph behavior without
  changing governance ownership?
- Authority clarity: is approval signoff blocking only when user or policy
  grants authority?
- Capability clarity: are capability implications treated as CAP inputs, not
  authorization?
- First-touch UX: do ordinary examples remain short and human-facing?
- Evidence: did validation run and does it support the claim?
- Unsupported claims: did the result overstate subagent, slash/plugin, runtime,
  or approval behavior?

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
