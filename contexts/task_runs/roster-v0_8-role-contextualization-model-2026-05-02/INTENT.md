# Intent Record

Task ID: `roster-v0_8-role-contextualization-model-2026-05-02`
Date: `2026-05-02`
Workspace: `/Users/tom/Documents/PHD/codex-cns`
Main Thread: `current Codex thread`
Source: `chat planning + roadmap`

## Purpose

Preserve the user's intent for the next Roster release after `v0.7.0`.
This file is evidence for translation. It is not the implementation contract.

## Original User Language

```text
那你寫一下v0.8.0
```

Immediate context:

- `v0.7.0` first-touch UX contract was implemented and merged.
- The roadmap defines `v0.8.0` as `Role Contextualization Model`.
- The user has been discussing roles as layers, domain-specific role extension,
  peer specialists, sign-off perspectives, and natural user-added roles.

## User Outcome

What the user wants to be true after the work:

- `v0.8.0` is written as a concrete, bounded next task.
- A developer thread can implement role contextualization without reading the
  full chat.
- The work remains focused on role interpretation, not a full role interaction
  engine.

## Why It Matters

Roster's core value is helping the user assemble and coordinate a multi-agent
working shape. If roles remain fixed labels, Roster cannot naturally handle
real user input like `加一個主管`, `新增金融技術人員`, or `加一個學生視角`.

The next release should make those role changes understandable and executable
without making the user learn internal taxonomy.

## Main-Thread Interpretation

Translate the user's language into practical engineering meaning:

- Create a `thread_packet_workflow` packet for `v0.8.0`.
- Write a developer prompt for `Role Contextualization Model`.
- Scope `v0.8.0` to role/perspective/layer/agent-instance distinctions and
  user-named role handling.
- Defer Role Interaction Patterns, subagent policy, and project/team mode to
  later releases.

## Ambiguities

Items that are not yet fully specified:

- Whether implementation should remain documentation-only or include route/help
  JSON hints.
- Whether Team Operating Packet templates need minimal fill-note updates in this
  pass.
- Whether release tagging should happen after review or in the same branch.

## Constraints From User

Hard constraints:

- Follow `thread_packet_workflow`.
- Keep this release smaller than a complete role engine.
- Do not make the user decide the task complexity or internal role taxonomy.
- Preserve normal first-touch UX from `v0.7.0`.

Soft preferences:

- Use natural Traditional Chinese examples where relevant.
- Prefer human role names and practical behavior over abstract taxonomy.
- Keep the implementation small enough to review.

## Parent Spec Check

Is this too broad for one developer pass?

- Parent spec: `yes, ROSTER_NEXT_VERSION_DIRECTION.md is broader`.
- Child spec for this pass: `v0.8.0 Role Contextualization Model only`.

## Do Not Infer

Things the developer/reviewer must not assume:

- Do not implement full Role Interaction Patterns.
- Do not implement automatic subagent spawning.
- Do not make every added role a new agent.
- Do not add a persistent role database.
- Do not change runtime adapter architecture.
- Do not expose internal governance terms in ordinary user-facing examples.
