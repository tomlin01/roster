# Intent Record

Task ID: `roster-v0_8_1-group-expansion-ux-patch-2026-05-02`
Date: `2026-05-02`
Workspace: `/Users/tom/Documents/PHD/codex-cns`
Main Thread: `current Codex thread`
Source: `chat planning + roadmap`

## Purpose

Preserve the user's intent for the next small Roster patch after `v0.8.0`.
This file is evidence for translation. It is not the implementation contract.

## Original User Language

```text
OK，那你先寫v0.8.1的文件
```

Immediate context:

```text
所以之後多組協作是會幫我細分小組成員嗎
```

The accepted answer was yes: multi-group collaboration should be expandable into
members, but the first response should stay short by default.

## User Outcome

What the user wants to be true after the work:

- `v0.8.1` is written as a concrete, bounded patch task.
- Roster can explain that grouped collaboration can later expand into concrete
  members.
- The patch stays between `v0.8.0` role contextualization and `v0.9.0` role
  interaction patterns.

## Why It Matters

`v0.8.0` teaches Roster to interpret roles. The user now wants the UX contract
for broad group plans: first show groups, then expand into people/roles when
needed. Without this, broad first-touch replies may either stay too shallow or
overload the user with too many members immediately.

## Main-Thread Interpretation

Translate the user's language into practical engineering meaning:

- Create a `thread_packet_workflow` packet for `v0.8.1`.
- Write a developer prompt for `Group Expansion UX Patch`.
- Scope `v0.8.1` to group-preview and member-expansion behavior.
- Defer interaction-edge modeling to `v0.9.0`.

## Ambiguities

Items that are not yet fully specified:

- Whether the BCQ_III example should appear in public README or only usage docs.
- Whether Team Operating Packet templates need group/member fill notes in this
  patch.
- Whether implementation should be docs-only or include route/help examples.

## Constraints From User

Hard constraints:

- Keep first-touch replies short.
- Make clear that multi-group collaboration can expand into members.
- Do not treat expansion as full interaction-edge modeling.
- Do not imply every expanded member becomes a separate agent.

Soft preferences:

- Use a practical example.
- BCQ_III is acceptable as the motivating example.
- Keep the implementation small enough to review.

## Parent Spec Check

Is this too broad for one developer pass?

- Parent spec: `no for v0.8.1`
- If yes, child spec for this pass: `not applicable`

## Do Not Infer

Things the developer/reviewer must not assume:

- Do not implement full Role Interaction Patterns.
- Do not implement automatic subagent spawning.
- Do not add persistent group/member storage.
- Do not make every member a separate agent.
- Do not move into project/team mode.
