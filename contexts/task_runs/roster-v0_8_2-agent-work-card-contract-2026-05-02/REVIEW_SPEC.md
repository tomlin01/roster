# Review Spec

Task ID: `roster-v0_8_2-agent-work-card-contract-2026-05-02`
Intent Record: `/Users/tom/Documents/PHD/codex-cns/contexts/task_runs/roster-v0_8_2-agent-work-card-contract-2026-05-02/INTENT.md`
Implementation Spec: `/Users/tom/Documents/PHD/codex-cns/contexts/task_runs/roster-v0_8_2-agent-work-card-contract-2026-05-02/IMPLEMENTATION_SPEC.md`
Current State: `/Users/tom/Documents/PHD/codex-cns/contexts/task_runs/roster-v0_8_2-agent-work-card-contract-2026-05-02/CURRENT_STATE.md`
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
- `prompt_v0_8_2_agent_work_card_contract.prompt.md`
- `BCQ_III_GROUP_EXPANSION_RUN_2026-05-02.md`

## Review Checklist

Check:

- Intent fidelity: is this limited to `v0.8.2` Agent Work Card Contract?
- Scope control: did it avoid full Role Interaction Patterns, subagent spawning,
  persistent storage, runtime changes, CAP ownership changes, and project/team
  mode?
- Work-card completeness: do docs define responsibility, perspective, inputs,
  output/deliverable, done condition, handoff target, capability need, assignment
  mode, and open questions?
- UX restraint: do first-touch examples stay short?
- Agent assignment: does it avoid implying every work card becomes a separate
  agent?
- Authorization boundary: does it state capability need is not authorization?
- Interaction boundary: does it avoid treating handoff target as full v0.9
  role interaction edges?
- Example quality: does BCQ_III or equivalent show a concrete work card?
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
