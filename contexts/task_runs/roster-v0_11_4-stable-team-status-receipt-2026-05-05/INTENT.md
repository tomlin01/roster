# Intent

Task ID: `roster-v0_11_4-stable-team-status-receipt-2026-05-05`
Date: `2026-05-05`

## Original User Need

The user has tested Roster for several days and found that response behavior is
still unstable:

- Roster often produces useful planning and artifacts.
- But response shape is still too sensitive to the user's prompt.
- It can drift back into a generic assistant or consultant answer.
- The user cannot reliably see the team state.
- The user wants Roster to explicitly state how many agents are active.
- Even if only one agent is active, Roster should say that and describe the
  one-agent workflow.

## Product Interpretation

This is not primarily an artifact-quality problem. It is a response-contract
problem.

Roster should make its coordination state visible enough that the user can
judge whether a Roster workflow actually ran.

The missing stable surface is:

```text
agent count + workflow state
```

## Target Direction

`v0.11.4` should become:

```text
Stable Team Status Receipt
```

Core rule:

```text
Explicit Roster invocation + non-trivial task
-> agent count + workflow state
-> useful output
-> role-action receipt
-> convergence.
```

## User Experience Goal

The user should not need to ask:

- "How many agents did Roster use?"
- "Was this a one-agent answer or a multi-agent workflow?"
- "Which stage is this in?"
- "Why did it plan an artifact but not produce it?"

Roster should answer those implicitly and compactly.

