# Intent Record

Task ID: `roster-v0_9-role-interaction-patterns-2026-05-02`
Date: `2026-05-02`
Workspace: `/Users/tom/Documents/PHD/codex-cns`
Main Thread: `main Roster development thread`
Source: `chat`

## Purpose

Preserve the user's intent for the next Roster milestone after `v0.8.2`.
This file is evidence for translation. It is not the implementation contract.

## Original User Language

```text
現在應該可以正式走到0.9?
OK，先撰寫文件
```

Relevant preceding context:

```text
這麼複雜的multi-agents有建立好pattern嗎?
```

## User Outcome

The user wants Roster to move from role/work-card planning into a more complete
multi-agent coordination model:

- Roles should not only have responsibilities; they should know how to interact.
- Complex teams should have recognizable coordination patterns between roles.
- The next milestone should be prepared as a bounded document/spec step before
  implementation.

## Why It Matters

- `v0.8.2` makes each role actionable, but the relation between roles is still
  mostly implicit.
- Without interaction edges, a complex roster can become a polished list rather
  than a working multi-agent system.
- Roster needs to coordinate teams naturally without exposing internal
  governance vocabulary to ordinary users.

## Main-Thread Interpretation

`v0.9.0` should implement `Role Interaction Patterns` as micro-coordination
edges inside the Team Architect task graph.

This means Roster should be able to model:

- who hands off to whom;
- who aligns with whom as peers;
- who challenges or reviews whom;
- where a quality loop returns;
- where sign-off can block progress;
- what shared artifact or decision anchors each interaction;
- what completion or fallback rule ends the interaction.

## Ambiguities

- Whether `v0.9.0` should add only docs/templates or small route/help surfaces.
- Whether to add a standalone role-interaction-edge template.
- Whether examples should appear in public README or stay in usage/developer
  docs.

## Constraints From User

Hard constraints:

- Do not jump into runtime execution or automatic subagent spawning.
- Keep the user-facing experience natural and not overloaded.
- Preserve the existing governance boundaries.
- Treat this as the next release after v0.8.2 behavior evidence.

Soft preferences:

- Use examples grounded in prior discussion: BCQ_III, meeting notes to slides,
  Teacher + Student, Engineering Technical Staff + Financial Technical Staff,
  Producer + Quality Reviewer, Manager sign-off.
- Keep changes release-sized and reviewable.

## Parent Spec Check

Is this too broad for one developer pass?

- Parent spec: `no for documentation/template contract`
- If yes, child spec for this pass: `not applicable`

`v0.9.0` should stay narrow: define and document interaction edges. It should
not implement the later `v0.10.0` subagent policy.

## Do Not Infer

The developer/reviewer must not assume:

- Every role interaction becomes a runtime subagent.
- Interaction edges grant tool authorization.
- A reviewer or manager can block delivery without explicit user or policy
  authority.
- This milestone implements message bus, shared-state runtime, persistent
  service, or automatic approvals.
- Public first-touch replies should expose internal labels such as
  `interaction_edge` or `Team Architect`.
