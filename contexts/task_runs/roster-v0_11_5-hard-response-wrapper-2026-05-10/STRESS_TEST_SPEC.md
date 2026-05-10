# Stress Test Spec

Task ID: `roster-v0_11_5-hard-response-wrapper-2026-05-10`

## Purpose

Verify that a fresh CLI session using the installed branch-local Roster skill
still follows the v0.11.5 hard response wrapper when the user does not mention
agents, workflow, role count, or internal contract terms.

## Acceptance Gate

Each non-trivial Roster reply must include:

- `本次啟用`
- `目前階段`
- useful work for the prompt
- `本次分工執行`
- `最後收斂`

Each reply must avoid ordinary-user leakage of:

- `route check`
- `packet-route`
- `artifact-harness`
- `preference`
- `roster_preferences`
- `registry`
- `CAP`
- `runtime adapter`
- `control plane`

## Prompts

### Prompt 1: Creative Experience Planning

```text
Roster，我想做一個「漂浮城市的夜市導覽」。使用者只有 3 分鐘，要理解這個地方、決定先去哪個攤位，最後留下可追蹤的選擇紀錄。

它未來可能變成簡報、互動網頁、遊戲規則或展示原型，但這輪先不要產出正式內容。請先幫我判斷怎麼拆、第一輪該確認什麼、哪些地方容易走偏。
```

### Prompt 2: Product Improvement Proposal

```text
Roster，我們有一個 SaaS 後台，最近新使用者常常不知道第一步要做什麼，通知也太多，主管只想知道本週哪些問題會影響交付。

最後可能會做成一頁式產品改善提案，但這輪先不要寫正式提案。請先幫我整理應該怎麼判斷優先順序、要收集哪些證據、兩週內最可能先處理什麼。
```

### Prompt 3: Meeting Notes To Executive Slides

```text
Roster，我有一份很散的會議紀錄，裡面有決議、抱怨、待辦、主管補充、一些還沒確認的數字。

之後可能要變成給主管看的 6 頁簡報，但這輪先不要產出簡報內容。請先幫我判斷怎麼整理、哪些資訊要先確認、怎麼避免最後做出來像流水帳。
```

### Prompt 4: Questionnaire App Planning

```text
Roster，我想把一份中醫體質問卷做成 APP。一般使用者要填答並看到結果，專業端要看到分數、題目明細和後續追蹤線索。

之後可能會變成產品需求文件或原型，但這輪先不要產出正式 PRD。請先幫我判斷這件事要怎麼拆，哪些風險要先處理，怎麼確認使用者端和專業端不會互相打架。
```

### Prompt 5: Cross-Skill Resource Integration Review

```text
Roster，我想重新審視一個既有的簡報製作流程。它看起來能產出東西，但我覺得整合資料、圖片、圖表和版面資源時常常不夠穩。

這輪先不要直接改文件，也不要寫正式 review。請先幫我判斷可能問題在哪些層次、怎麼檢查是不是資源整合流程本身有問題、下一輪應該先看什麼證據。
```

## CLI Method

Run each prompt in an independent ephemeral Codex CLI session after installing
the current branch with:

```sh
./scripts/brain.sh roster-install --codex-home /Users/tom/.codex --force --json
```

Use read-only sandbox and save each final answer under this task-run directory.
