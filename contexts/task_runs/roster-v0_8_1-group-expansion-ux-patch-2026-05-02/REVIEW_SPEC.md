# Review Spec

Task ID: `roster-v0_8_1-group-expansion-ux-patch-2026-05-02`
Intent Record: `/Users/tom/Documents/PHD/codex-cns/contexts/task_runs/roster-v0_8_1-group-expansion-ux-patch-2026-05-02/INTENT.md`
Implementation Spec: `/Users/tom/Documents/PHD/codex-cns/contexts/task_runs/roster-v0_8_1-group-expansion-ux-patch-2026-05-02/IMPLEMENTATION_SPEC.md`
Current State: `/Users/tom/Documents/PHD/codex-cns/contexts/task_runs/roster-v0_8_1-group-expansion-ux-patch-2026-05-02/CURRENT_STATE.md`
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
- `prompt_v0_8_1_group_expansion_ux_patch.prompt.md`

## Review Checklist

Check:

- Intent fidelity: is this limited to `v0.8.1` Group Expansion UX Patch?
- Scope control: did it avoid full Role Interaction Patterns, subagent spawning,
  persistent storage, runtime changes, and project/team mode?
- UX shape: does broad first-touch stay group-level by default?
- Expansion trigger: does it say when to expand groups into members?
- Expanded member quality: do members carry responsibility, perspective, and
  deliverable?
- Agent restraint: does it avoid implying every member is a separate agent?
- Boundary: does it say group expansion is not full interaction-edge modeling?
- User-facing tone: are examples natural and not overloaded?
- Governance leakage: ordinary examples must not expose internal terms.
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
