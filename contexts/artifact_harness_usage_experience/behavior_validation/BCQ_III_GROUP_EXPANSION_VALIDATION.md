# BCQ_III Group Expansion Behavior Validation

Date: `2026-05-02`
Status: `scenario-ready / first in-thread behavior run recorded`
Related release: `v0.8.1`

## Purpose

Use the BCQ_III app task as the first behavior-validation scenario for Roster's
group expansion contract.

This is not a new feature spec. It is a validation script for checking whether
the current Roster skill and `/roster` command actually lead the model to behave
as intended in ordinary use.

## Scenario

The target artifact is a BCQ_III questionnaire app that combines:

- traditional Chinese medicine questionnaire content;
- statistical scoring and score interpretation;
- user-facing report output;
- physician-facing questionnaire answers and score view;
- quality and risk checks for medical wording, score consistency, and privacy.

## What This Validates

This scenario validates whether Roster can:

- keep the first response group-level for a broad task;
- avoid overloading the user with every member immediately;
- expand groups into concrete members when asked;
- include responsibility, perspective, and deliverable for expanded members;
- handle added roles after expansion without assuming every role is a separate
  agent;
- avoid leaking internal packet or governance terminology in ordinary replies.

## Prompt 1: First Touch

Use this prompt in a fresh ordinary Codex/Roster interaction:

```text
Roster, 用 BCQ_III 做一個問卷 APP，形式是使用者填答問卷；使用者端要看到報告結果，醫師端要看到填答問卷和分數。
```

Expected response shape:

```text
這個任務牽涉中醫內容、統計邏輯和 APP 雙端流程，我會先分成幾組協作：

- 問卷與中醫組：整理 BCQ_III 題目、構面、體質解讀和報告文字
- 統計與計分組：定義分數計算、構面分數、門檻和可信度提醒
- 使用者端組：設計填答流程、報告結果、解讀文字和下一步建議
- 醫師端組：設計填答明細、分數表、風險提示和追蹤註記
- Quality 組：檢查分數一致性、醫療語氣、資料隱私和使用者誤解風險

如果這個分組方向可以，我再展開每組的小組成員和第一步。
```

Pass criteria:

- Response starts with group-level collaboration, not full member expansion.
- It includes both user side and physician side.
- It includes TCM/questionnaire content, statistical scoring, and Quality.
- It offers expansion as the next step.
- It does not mention internal packet names, governance layers, runtime
  adapters, or control-plane terms.

Fail signals:

- It immediately lists a long full team with every possible member.
- It treats the task as only a software UI task and omits TCM/statistics.
- It uses internal labels as the main response.
- It says Roster cannot later implement or coordinate app work.

## Prompt 2: Expand Groups

Use this follow-up:

```text
展開每組的小組成員，並列出每個人的責任、觀點和交付物。
```

Expected response shape:

```text
我會把 BCQ_III APP 的小組展開成這樣：

- 問卷與中醫組
  - 中醫內容負責人：責任是確認構面和體質解讀；觀點是中醫概念是否被正確轉譯；交付物是可用的中醫內容規則。
  - 報告文字整理人：責任是把中醫概念轉成使用者看得懂的說明；觀點是使用者是否會誤解；交付物是報告文案。
  - 醫師審核人：責任是檢查文字是否過度診斷或誤導；觀點是臨床使用安全；交付物是醫療語氣修正。

- 統計與計分組
  - 統計方法人員：責任是確認計分規則、構面分數和門檻；觀點是分數是否可解釋；交付物是計分規格。
  - 資料處理人員：責任是把問卷答案轉成可計算資料；觀點是資料欄位是否穩定；交付物是資料欄位和轉換規則。
  - 分數驗證人員：責任是檢查分數可重現且對應題目；觀點是使用者端和醫師端是否一致；交付物是分數驗證結果。

- 使用者端組
  - UX 人員：責任是設計填答流程和報告閱讀順序；觀點是使用者是否能完成填答並理解結果；交付物是使用者流程。
  - APP 前端人員：責任是實作填答畫面和結果頁；觀點是互動是否清楚；交付物是前端畫面。
  - 使用者代表：責任是指出看不懂或容易誤解的地方；觀點是非醫療背景使用者；交付物是可讀性回饋。

- 醫師端組
  - 臨床使用者代表：責任是確認醫師需要哪些分數和原始填答；觀點是門診或追蹤使用；交付物是醫師端需求。
  - 後台產品人員：責任是設計分數表、填答明細和追蹤紀錄；觀點是醫師端工作流；交付物是後台流程。
  - 權限與隱私人員：責任是確認誰能看哪些資料；觀點是資料安全和角色權限；交付物是權限規則。

- Quality 組
  - 醫療風險檢查人員：責任是檢查診斷、建議和免責語氣；觀點是避免過度醫療宣稱；交付物是風險清單。
  - 計分一致性檢查人員：責任是核對使用者端和醫師端分數一致；觀點是計算結果可追蹤；交付物是一致性檢查。
  - 可用性檢查人員：責任是檢查報告是否清楚、欄位是否容易看錯；觀點是成品可用性；交付物是可用性問題。
```

Pass criteria:

- It expands groups only after asked.
- Each member has responsibility, perspective, and deliverable.
- It preserves the two app surfaces: user-facing report and physician-facing
  score/questionnaire view.
- It does not imply each member must become a separate runtime agent.
- It does not introduce full role interaction-edge vocabulary as the main
  explanation.

Fail signals:

- Expanded view is still only group names.
- Members lack perspective or deliverable.
- It overcommits to separate agents for every member.
- It collapses physician side into ordinary admin UI without clinical review.

## Prompt 3: Add A Role

Use this follow-up:

```text
加一個法務審，另外統計組需要一位模型驗證人員。
```

Expected response shape:

```text
我會這樣調整：

- 法務審：加入 Quality 或交付前審核位置，檢查隱私、告知文字、醫療宣稱和責任邊界；如果法務需要擋下交付，我會把它視為審核關卡。
- 模型驗證人員：加入統計與計分組，負責檢查計分規則、模型或門檻是否可重現、是否和 BCQ_III 題目與構面對應。

這兩個新增角色不會自動變成獨立 agent；我會先把它們放進現有小組和審核位置。
```

Pass criteria:

- Legal review is classified as reviewer/approver only when blocking authority
  matters.
- Model validator joins the statistics/scoring group.
- Response explains what changed and what happens next.
- It does not create separate agents by default.

Fail signals:

- It treats legal review as ordinary content writing.
- It treats the model validator as an unrelated software QA role.
- It says both roles must be separate agents.

## Validation Record

Fill this after running the scenario:

- tested_at:
- runtime or host:
- invocation used: `Roster, ...` / `@roster` / `/roster`
- prompt_1_result: pass/fail/partial
- prompt_2_result: pass/fail/partial
- prompt_3_result: pass/fail/partial
- notable excerpts:
- failure notes:
- recommended follow-up: none / wording patch / v0.8.2 / v0.9 input

## Current Status

This file makes the BCQ_III case scenario-ready. It does not prove the behavior
until the prompts are run in an actual Roster interaction and the results are
recorded.

First in-thread behavior run:

- `BCQ_III_GROUP_EXPANSION_RUN_2026-05-02.md`
