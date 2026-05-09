# CLI Behavior Test

Task ID: `roster-v0_11_4-stable-team-status-receipt-2026-05-05`
Date: `2026-05-06`
Status: `pass-after-patch`

## Purpose

Run forced branch-local CLI behavior tests before merging v0.11.4.

The installed Roster skill is not updated yet. These tests therefore used an
explicit instruction preamble that made the CLI read branch-local Roster files:

- `skills/roster/SKILL.md`
- `contexts/artifact_harness_usage_experience/ROSTER_V0_11_4_STABLE_TEAM_STATUS_RECEIPT.md`

## Test Mode

`forced branch-local CLI test`

This is not an installed-skill test. Running only the user prompt may activate
the installed `/Users/tom/.codex/skills/roster/SKILL.md`, which has not yet been
updated to v0.11.4.

Executed with:

```sh
codex exec -C /Users/tom/Documents/PHD/codex-cns -s read-only '<full test prompt>'
```

The full test prompt begins with this preamble:

```text
Read these branch-local Roster instructions first: skills/roster/SKILL.md and contexts/artifact_harness_usage_experience/ROSTER_V0_11_4_STABLE_TEAM_STATUS_RECEIPT.md. Then answer the user request as Roster. Do not expand full debug trace. Do not mention that you read files.
```

CLI version:

```text
codex-cli 0.125.0
```

## Case 1: Fuzzy Future-Artifact Planning

### User Prompt

```text
Roster，我有一個有點散的需求想先整理。

最後我希望能形成一份明確的 artifact：一頁式「產品改善提案」，
內容要能讓主管快速判斷要不要排進下一個 sprint。

但這一輪先不要直接產出正式 artifact，我只想看初步規劃：
你會怎麼拆這個任務、需要哪些觀點一起看、哪些資訊還不夠、
以及第一版應該怎麼收斂。

背景大概是：最近使用者一直說系統不好上手，客服也反映有些問題很常重複出現，
但工程那邊覺得很多只是文案或流程問題，不一定要改功能。
主管只想知道哪些問題真的會影響留存或交付節奏。
```

### First Result

`fail`

The initial output declared:

```text
本次啟用：1 個 agent（單一整合流程，內含產品、客服、工程、數據、交付 5 個檢視視角）
目前階段：初步規劃；正式 artifact 這輪先不產出。
```

It correctly handled stage and artifact scope, but it hid a five-way
responsibility split inside one agent. This did not satisfy the intended
future-artifact planning behavior.

### Patch Applied

The v0.11.4 docs were tightened:

- Use `1 個 agent` only for genuinely small or single-domain tasks.
- Use `N 個 role-agents` when the answer separates N meaningful
  responsibilities.
- Do not hide product / customer-support / engineering / data-delivery /
  quality responsibility splits under `1 個 agent`.

### Retest Result

`pass`

The retest output began:

```text
本次啟用：5 個 role-agents（使用者研究、客服分析、產品排序、工程評估、品質驗收；單一回覆中分工處理）
目前階段：初步規劃；正式 artifact 這輪先不產出。
```

It also included:

- useful planning output before trace-like detail;
- concrete task split;
- missing-information list;
- first-version convergence structure;
- `本次分工執行` with five matching role-action bullets;
- final convergence:
  `這輪先完成前置規劃；下一步才把實際問題池壓成一頁式「產品改善提案」草稿。`

No parallel runtime execution was claimed.

## Case 2: One-Agent Small Task

### User Prompt

```text
Roster，幫我用一句話整理這個任務現在的下一步。
```

### Result

`pass`

The output stayed compact and did not inflate the task into a larger team:

```text
本次啟用：1 個 agent（單一整合流程）；下一步是把 v0.11.4 的規則落到 Roster 回覆模板與驗收檢查，確保明確 Roster 呼叫會宣告 agent 數、目前階段、分工執行與收斂。
```

This satisfies the small-task side of the forced branch-local contract:
one-agent behavior remains visible without over-expanding the answer.

## CLI Notes

- The CLI automatically consulted relevant memory for Case 1. This makes the
  run closer to normal use, but not a pure skill-only test.
- The pass result depends on the explicit branch-local preamble above. It is not
  evidence that the currently installed Roster skill already has v0.11.4.
- CLI emitted non-blocking environment warnings about `goals`, plugin manifest
  prompts, rollout recording, and MCP shutdown. These did not affect the
  generated Roster responses.
