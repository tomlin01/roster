# Intent Record

Task ID: `roster-v0_7-first-touch-ux-contract-2026-05-02`
Date: `2026-05-02`
Workspace: `/Users/tom/Documents/PHD/codex-cns`
Main Thread: `current Codex thread`
Source: `chat planning + roadmap`

## Purpose

Preserve the user's intent for the next Roster release. This file is evidence
for translation. It is not the implementation contract.

## Original User Language

```text
你接下來要按照`thread_packet_workflow`的流程去走
```

The immediate prior context:

```text
我們先分出未來Git會有幾個版本
```

and the accepted next step:

```text
v0.7.0: First-Touch UX Contract
```

## User Outcome

What the user wants to be true after the work:

- The next Roster implementation step follows `thread_packet_workflow`.
- `v0.7.0` is scoped as a clear first-touch UX task before deeper role-engine
  work starts.
- A developer thread can implement `v0.7.0` from packet files without reading
  the full chat.

## Why It Matters

What problem this solves for the user's workflow:

- The design discussion has grown large and should not be handed to a developer
  as raw chat.
- Roster needs a controlled release sequence so first-touch UX, role
  contextualization, role interaction edges, and subagent policy do not collapse
  into one oversized change.
- The user wants durable file-grounded continuity.

## Main-Thread Interpretation

Translate the user's language into practical engineering meaning:

- Create a `thread_packet_workflow` packet for `v0.7.0`.
- Keep `v0.7.0` focused on first-touch user experience.
- Defer role contextualization engine, interaction edges, and subagent policy to
  later releases.

## Ambiguities

Items that are not yet fully specified:

- Whether the developer will implement directly on `main` or on a new branch.
- Whether `v0.7.0` should include code-level route output changes or docs/skill
  guidance only.
- Whether final release tagging should happen in the same developer pass.

## Constraints From User

Hard constraints:

- Follow `thread_packet_workflow`.
- Do not treat the full direction discussion as one implementation task.
- Keep first-touch behavior natural for ordinary users.

Soft preferences:

- Use Traditional Chinese examples where relevant.
- Avoid showing internal governance terms in ordinary user-facing replies.
- Keep the work small enough to review.

## Parent Spec Check

Is this too broad for one developer pass?

- Parent spec: `no for v0.7.0`
- If yes, child spec for this pass: `not applicable`

## Do Not Infer

Things the developer/reviewer must not assume:

- Do not assume `v0.7.0` includes a full role interaction engine.
- Do not assume subagents should be spawned automatically.
- Do not claim `@roster` or `/roster` works without install/reload and host
  support.
- Do not expose `Artifact Harness`, `HR`, `Team Architect`, `CAP`, runtime
  adapter, or packet-chain terminology in ordinary first-touch examples.
