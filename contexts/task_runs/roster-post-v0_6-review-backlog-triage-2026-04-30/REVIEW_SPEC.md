# Review Spec

Task ID: `roster-post-v0_6-review-backlog-triage-2026-04-30`
Intent Record: `/Users/tom/Documents/PHD/codex-cns/contexts/task_runs/roster-post-v0_6-review-backlog-triage-2026-04-30/INTENT.md`
Implementation Spec: `/Users/tom/Documents/PHD/codex-cns/contexts/task_runs/roster-post-v0_6-review-backlog-triage-2026-04-30/IMPLEMENTATION_SPEC.md`
Current State: `/Users/tom/Documents/PHD/codex-cns/contexts/task_runs/roster-post-v0_6-review-backlog-triage-2026-04-30/CURRENT_STATE.md`
Diff or PR: `<path-or-url>`

## Review Role

You are the reviewer thread. Review the result against the user's intent and implementation spec. Do not rewrite unless explicitly asked.

## Review Inputs

Required:

- Intent record.
- Implementation spec.
- Current state.
- Git diff, PR, or changed files.
- `TRIAGE_RESULT.md` from this packet directory.
- Validation evidence.

Optional:

- Developer final response.
- Related issue or PR.

## Review Checklist

Check:

- Intent fidelity: does the result triage historical findings against current `main` instead of blindly fixing stale issues?
- Scope control: did it avoid forbidden areas and non-goals?
- Requirement coverage: are all attached findings accounted for?
- Acceptance: are all acceptance criteria satisfied?
- Evidence: did validation run and does it support the claim?
- Markdown/prose quality: are headings, wording, and hierarchy clear?
- Unsupported claims: did the result overstate UI verification, install behavior, or governance boundaries?
- Residual risks: what still needs a human or a later pass?

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
