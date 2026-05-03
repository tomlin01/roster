# Review Spec

Task ID: `roster-v0_11_2-receipt-trigger-clarification-2026-05-04`
Intent Record: `contexts/task_runs/roster-v0_11_2-receipt-trigger-clarification-2026-05-04/INTENT.md`
Implementation Spec: `contexts/task_runs/roster-v0_11_2-receipt-trigger-clarification-2026-05-04/IMPLEMENTATION_SPEC.md`
Current State: `contexts/task_runs/roster-v0_11_2-receipt-trigger-clarification-2026-05-04/CURRENT_STATE.md`
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

- `contexts/artifact_harness_usage_experience/ROSTER_V0_11_2_RECEIPT_TRIGGER_CLARIFICATION.md`
- `skills/roster/SKILL.md`
- `README.md`
- `plugins/roster/commands/roster.md`

## Review Checklist

Check:

- Intent fidelity: does the result fix the contract issue the user identified?
- Trigger clarity: does it say receipt is ordinary completion evidence, not
  debug trace?
- Suppression behavior: does it say `不要展開 debug trace` should shorten, not
  remove, a qualifying receipt?
- Current-turn receipt: does it prevent future role-summary feature discussion
  from replacing the current answer's own receipt?
- Simplicity behavior: does it say qualifying simple tasks get shorter receipts,
  not no receipt?
- Scope control: did it avoid runtime, subagent, install, health, slash-routing,
  and adapter behavior changes?
- First-touch preservation: did it avoid making first-touch replies heavier?
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

