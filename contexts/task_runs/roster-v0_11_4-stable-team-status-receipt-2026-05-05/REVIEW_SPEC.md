# Review Spec

Task ID: `roster-v0_11_4-stable-team-status-receipt-2026-05-05`

## Review Goal

Review whether Roster `v0.11.4` actually solves the response instability:

```text
User cannot tell team state from ordinary Roster responses.
```

## Required Review Checks

1. Explicit Roster invocation for non-trivial work requires agent count.
2. One-agent Roster tasks still declare one-agent workflow.
3. Future-artifact planning examples distinguish current stage from capability
   limit.
4. `本次分工執行` lists concrete actions, not only role names.
5. Examples do not claim actual parallel runtime subagents unless runtime
   execution is real.
6. Ordinary responses do not expose internal packet, CAP, runtime adapter, or
   control-plane jargon.
7. The response is still useful and not dominated by team-status boilerplate.

## Findings Format

Use findings-first review.

If issues exist, include:

- priority;
- file path;
- line range;
- concrete behavior risk;
- suggested fix direction.

If no issues exist, say so clearly and identify remaining residual risk.

## Suggested Test Prompts

Fuzzy future artifact:

```text
Roster，我有一個有點散的需求想先整理。

最後我希望能形成一份明確的 artifact：一頁式「產品改善提案」，
但這一輪先不要直接產出正式 artifact，我只想看初步規劃。
背景大概是：使用者說系統不好上手，客服說問題重複，工程覺得
很多只是文案或流程，主管只想知道哪些問題影響留存或交付節奏。
```

One-agent:

```text
Roster，幫我用一句話整理這個任務現在的下一步。
```

