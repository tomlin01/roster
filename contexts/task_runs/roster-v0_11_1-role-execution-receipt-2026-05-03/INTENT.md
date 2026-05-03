# Intent Record

Task ID: `roster-v0_11_1-role-execution-receipt-2026-05-03`
Date: `2026-05-03`
Workspace: `/Users/tom/Documents/PHD/codex-cns`
Main Thread: `Codex desktop main thread`
Source: `chat`

## Purpose

Preserve the user's intent and context. This file is evidence for translation.
It is not the implementation contract.

## Original User Language

```text
應該說至少可以讓使用者判斷不同AGENT是不是真的有按照宣告在執行任務
```

```text
OK，我們把這個設定成v0.11.1
```

```text
應該說除了first UX外，後續的風格要跟AGENT理念維持一致
```

```text
這個應該好處理，你寫一下交付文件後進入workflow
```

## User Outcome

The user wants Roster's later task responses to make role execution visible
enough to judge whether declared agents or perspectives actually performed
their assigned work.

Expected outcomes:

- First-touch UX stays short and natural.
- Later completion replies preserve Roster's agent-coordination identity.
- Users can see who did what without reading a full internal audit trace.
- Roster does not pretend separate runtime agents were spawned if work was only
  simulated as role perspectives inside one coordinating agent.
- Review/debug mode can expand into capability, source, assumption, and runtime
  execution details when requested.

## Why It Matters

Roster's product identity is not just "summarize a plan." It is an agent
coordination surface. If a response declares roles but later collapses into a
generic assistant summary, the user cannot judge whether the roles were useful
or decorative.

This matters especially after `v0.10.0`, because role planning can now include
capability needs such as web lookup, filesystem inspection, code execution,
visual review, specialist skills, plugin/connectors, and subagent execution.
Those needs must not disappear from the completion story.

## Main-Thread Interpretation

Translate the user's language into practical engineering meaning:

- Add a durable Roster `v0.11.1` response contract for ordinary completion
  replies.
- Keep first-touch replies minimal, but make later replies follow:
  `outcome -> role actions -> convergence`.
- Introduce a lightweight `Role Execution Receipt`, likely labeled
  `本次分工執行`, for non-trivial multi-role tasks.
- Require receipts to list only roles that actually contributed.
- Require receipts to describe concrete actions, checks, evidence, limitations,
  or convergence, not just role names.
- Distinguish role/perspective execution from actual runtime/subagent
  execution.
- Keep full role/capability/source/assumption trace in review/debug mode.

## Ambiguities

- The exact final wording in public README and skill docs is open to the
  developer, as long as the behavior contract is clear and user-facing.
- It is acceptable to keep this pass documentation-first unless a small test or
  text audit is already present and easy to extend.
- This pass does not need to prove a real multi-runtime execution run.

## Constraints From User

Hard constraints:

- Do not make first-touch UX heavier.
- Preserve Roster's agent-centered concept in later replies.
- Do not create misleading claims that separate agents ran when only role
  perspectives were simulated.
- Follow the thread packet workflow.

Soft preferences:

- Keep ordinary user-facing language natural and short.
- Use enough role-action detail that a human can judge whether declared roles
  were meaningful.
- Avoid exposing internal governance terms unless the user asks for review,
  debug, or implementation detail.

## Parent Spec Check

Is this too broad for one developer pass?

- Parent spec: `no`
- If yes, child spec for this pass: `not applicable`

## Do Not Infer

Things the developer/reviewer must not assume:

- Do not infer that every Roster role must be a separate runtime agent.
- Do not infer that this pass should implement a new subagent runtime, message
  bus, web adapter, browser adapter, CV adapter, plugin adapter, or connector.
- Do not infer that ordinary completion replies should become full audit logs.
- Do not infer that internal terms such as Artifact Harness, HR, Team Architect,
  CAP, runtime adapter, or control plane should appear in ordinary user
  replies.

