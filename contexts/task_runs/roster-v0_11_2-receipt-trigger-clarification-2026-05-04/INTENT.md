# Intent Record

Task ID: `roster-v0_11_2-receipt-trigger-clarification-2026-05-04`
Date: `2026-05-04`
Workspace: `/Users/tom/Documents/PHD/codex-cns`
Main Thread: `Codex desktop main thread`
Source: `chat`

## Purpose

Preserve the user's intent and context. This file is evidence for translation.
It is not the implementation contract.

## Original User Language

```text
可能是任務太簡單，我重開了
```

The user then provided a fresh-thread Roster response. The response produced a
useful two-week product plan, but still did not include the expected
`本次分工執行` receipt.

```text
這樣是contract的問題
```

```text
oK，那是做一下v0.11.2的文件
```

```text
可以建立branch之後進入workflow
```

## User Outcome

The user wants Roster's `v0.11.2` contract to fix the observed behavior:

- `本次分工執行` must not be treated as debug trace.
- `不要展開完整 debug trace` should suppress full trace, not suppress ordinary
  role-action receipt.
- If a task discusses role-summary as a future product feature, the current
  answer still needs its own current-turn receipt when multiple perspectives
  were used.
- Task simplicity can make the receipt shorter, but should not remove it when
  the task qualifies.

## Why It Matters

`v0.11.1` made Role Execution Receipt visible in docs, but the behavior remained
unstable in real testing. Roster kept describing role contribution summary as a
future feature instead of showing the current answer's role actions.

This undermines the core Roster idea: users should be able to see whether
declared roles or perspectives actually did work.

## Main-Thread Interpretation

Translate the user's language into practical engineering meaning:

- Create a narrow `v0.11.2` patch focused on receipt trigger semantics.
- Update Roster behavior docs so ordinary role-action receipt is explicitly
  separated from review/debug trace.
- Add a tested example based on the observed two-week product plan prompt.
- Keep first-touch UX unaffected.
- Do not implement runtime enforcement, subagent runtime, health changes,
  install changes, or slash command behavior changes beyond docs.

## Ambiguities

- The exact wording can be improved by the developer, but must preserve the
  user's point that this is a contract issue.
- Automated enforcement is optional unless a narrow text audit is clearly
  low-risk.

## Constraints From User

Hard constraints:

- Enter the established branch + thread-packet workflow.
- Treat this as contract correction, not a new broad feature.
- Preserve first-touch UX.
- Do not equate ordinary receipt with debug trace.

Soft preferences:

- Keep the fix lightweight.
- Use the observed test failure as a concrete example.
- Prefer human-readable examples over heavy internal terminology.

## Parent Spec Check

Is this too broad for one developer pass?

- Parent spec: `no`
- If yes, child spec for this pass: `not applicable`

## Do Not Infer

Things the developer/reviewer must not assume:

- Do not infer that every Roster answer needs a receipt.
- Do not infer that receipt requires full debug/source/capability trace.
- Do not infer that this patch should implement runtime or subagent behavior.
- Do not infer that this patch should change install, health, or slash routing.

