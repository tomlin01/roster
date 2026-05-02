# Review Spec

Task ID: `roster-v0_7-first-touch-ux-contract-2026-05-02`
Intent Record: `/Users/tom/Documents/PHD/codex-cns/contexts/task_runs/roster-v0_7-first-touch-ux-contract-2026-05-02/INTENT.md`
Implementation Spec: `/Users/tom/Documents/PHD/codex-cns/contexts/task_runs/roster-v0_7-first-touch-ux-contract-2026-05-02/IMPLEMENTATION_SPEC.md`
Current State: `/Users/tom/Documents/PHD/codex-cns/contexts/task_runs/roster-v0_7-first-touch-ux-contract-2026-05-02/CURRENT_STATE.md`
Diff or PR: `<path-or-url>`

## Review Role

You are the reviewer thread. Review the result against the user's intent and
implementation spec. Do not rewrite unless explicitly asked.

## Review Inputs

Required:

- Intent record.
- Implementation spec.
- Current state.
- Git diff, PR, or changed files.
- Developer report.
- Validation evidence.

Optional:

- `ROSTER_NEXT_VERSION_DIRECTION.md`
- `ROSTER_MILESTONE_ROADMAP.md`
- `prompt_v0_7_first_touch_ux_contract.prompt.md`

## Review Checklist

Check:

- Intent fidelity: is this limited to `v0.7.0` First-Touch UX?
- Scope control: did it avoid role interaction engine, subagent spawning, and
  team mode?
- User-facing tone: are examples short, natural, and role-shaped?
- Traditional Chinese examples: do meeting-note examples use natural role names?
- Complexity behavior: is it visible through plain phrases, not debug labels?
- Governance leakage: ordinary examples must not expose internal terms.
- Invocation truthfulness: `@roster` and `/roster` must remain caveated by
  install/reload/host support.
- Evidence: did validation run and support the claim?

## Severity Scale

- P0: blocks use or violates a hard boundary.
- P1: likely incorrect result, overclaim, or serious UX break.
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
