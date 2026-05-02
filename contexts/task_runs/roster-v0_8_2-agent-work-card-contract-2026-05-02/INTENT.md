# Intent Record

Task ID: `roster-v0_8_2-agent-work-card-contract-2026-05-02`
Date: `2026-05-02`
Workspace: `/Users/tom/Documents/PHD/codex-cns`
Main Thread: `current Codex thread`
Source: `chat planning + BCQ_III behavior validation`

## Purpose

Preserve the user's intent for the next small Roster patch after `v0.8.1`.
This file is evidence for translation. It is not the implementation contract.

## Original User Language

```text
看起來是蠻好的，我想另外確定每個AGENT都有對應的職責而不是只有給使用者看
```

Follow-up:

```text
OK，那你寫v0.8.2的文件
```

Immediate context:

- `v0.8.1` group expansion was validated with a BCQ_III app example.
- The expanded roles had responsibility, perspective, and deliverable.
- The user wants stronger assurance that expanded agents/members are real work
  units, not only user-facing role names.

## User Outcome

What the user wants to be true after the work:

- `v0.8.2` is written as a concrete, bounded patch task.
- Roster can turn expanded members into actionable work cards.
- Each work card identifies what the role owns, needs, produces, completes, and
  hands off.
- Work cards remain compatible with future subagents but do not require them.

## Why It Matters

Roster's core promise is not only to name a team. It should coordinate work. If
expanded roles have no inputs, outputs, completion condition, or handoff target,
they can become decorative labels and fail to guide actual execution.

## Main-Thread Interpretation

Translate the user's language into practical engineering meaning:

- Create a `thread_packet_workflow` packet for `v0.8.2`.
- Write a developer prompt for `Agent Work Card Contract`.
- Scope `v0.8.2` to making expanded roles/members actionable.
- Defer full role interaction edges to `v0.9.0`.
- Defer automatic subagent policy to `v0.10.0`.

## Ambiguities

Items that are not yet fully specified:

- Whether work cards should be a standalone template or only a Team Operating
  Packet section.
- Whether public README should include the full BCQ_III work card or a shorter
  user-facing example.
- Whether route/help JSON output needs to mention work cards.

## Constraints From User

Hard constraints:

- Do not let roles be only for display.
- Preserve the first-touch UX: keep ordinary first replies short.
- Do not force every role into a separate agent.
- Do not conflate capability need with tool authorization.

Soft preferences:

- Use BCQ_III as a concrete example.
- Keep this as a small patch before full role interaction modeling.
- Make it useful for future agent/subagent work.

## Parent Spec Check

Is this too broad for one developer pass?

- Parent spec: `no for v0.8.2`
- If yes, child spec for this pass: `not applicable`

## Do Not Infer

Things the developer/reviewer must not assume:

- Do not implement automatic subagent spawning.
- Do not implement full Role Interaction Patterns.
- Do not add persistent work-card storage.
- Do not make work cards the owner of tool authorization.
- Do not implement the BCQ_III app.
