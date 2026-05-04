# Intent Record

Task ID: `roster-v0_11_3-invocation-response-wrapper-2026-05-04`
Date: `2026-05-04`
Workspace: `/Users/tom/Documents/PHD/codex-cns`
Main Thread: `Codex desktop main thread`
Source: `chat`

## Purpose

Preserve the user's intent and context. This file is evidence for translation.
It is not the implementation contract.

## Original User Language

```text
我覺得不管是我們這次要驗收的品質或是作為fist UX，都沒有達標
```

The user provided a fresh Roster output that produced a reasonable two-week
dashboard product plan but did not look like a Roster task run.

```text
OK，那你撰寫v0.11.3的文件
```

```text
OK，那就開branch進入workflow
```

## User Outcome

The user wants Roster to behave like an agent coordination surface when
explicitly invoked, not like a generic assistant that happens to have a skill
loaded.

Expected outcomes:

- Explicit `Roster，...`, `/roster`, or `@roster` invocation activates a
  Roster-shaped response for non-trivial tasks.
- The answer starts with compact role/perspective framing.
- The useful answer still comes first and does not become an internal workflow
  explanation.
- Qualifying non-trivial answers include `本次分工執行`.
- The answer ends with convergence, not only a generic next-prompt suggestion.
- `不要展開 debug trace` suppresses detailed trace only; it does not suppress
  the Roster wrapper.

## Why It Matters

`v0.11.1` and `v0.11.2` focused on the receipt. Testing showed the deeper issue:
the whole answer can still fall back into ordinary assistant style. That means
Roster's agent-coordination identity is not reliably visible to users even when
they explicitly call it.

The user wants Roster to be useful as an agent, not just a context hint.

## Main-Thread Interpretation

Translate the user's language into practical engineering meaning:

- Add a `v0.11.3` response wrapper contract.
- Make explicit invocation a style trigger for non-trivial tasks.
- Define the shape:
  `entry framing -> useful work -> role-action receipt -> convergence`.
- Distinguish entry framing from a heavy first-touch team explanation.
- Keep first-touch short and user-facing.
- Add good/bad examples based on the dashboard/product-plan failure pattern.
- Do not change runtime, install, health, slash routing, or actual subagent
  behavior.

## Ambiguities

- Automated enforcement is optional unless a narrow text audit is low-risk.
- Exact wording can be refined, but the response contract must remain explicit.

## Constraints From User

Hard constraints:

- Create a branch and enter the established workflow.
- Treat this as a response-contract correction, not a runtime rewrite.
- Keep first-touch UX short and natural.
- Do not let generic next-prompt suggestions replace convergence.

Soft preferences:

- Keep the change lightweight.
- Use concrete examples from the failed dashboard/product-plan test.
- Keep ordinary examples free of internal governance jargon.

## Parent Spec Check

Is this too broad for one developer pass?

- Parent spec: `no`
- If yes, child spec for this pass: `not applicable`

## Do Not Infer

Things the developer/reviewer must not assume:

- Do not infer that every Roster reply must be long.
- Do not infer that runtime/subagent execution must be implemented.
- Do not infer that `/roster` routing or installation behavior should change.
- Do not infer that Roster should expose internal packet, CAP, runtime, or
  control-plane terms in ordinary replies.

