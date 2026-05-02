# BCQ_III Group Expansion Behavior Run

Date: `2026-05-02`
Related scenario: `BCQ_III_GROUP_EXPANSION_VALIDATION.md`
Related release: `v0.8.1`
Status: `pass for in-thread Roster run / broader cross-host validation pending`

## Setup

Before running this behavior check, the installed Roster skill was stale and did
not include the v0.8/v0.8.1 role contextualization and group expansion sections.

Command run:

```sh
./scripts/brain.sh roster-install --codex-home ~/.codex --force --json
```

Result:

- installed: `true`
- refused: `false`
- Roster skill updated at `/Users/tom/.codex/skills/roster/SKILL.md`
- local plugin updated at
  `/Users/tom/.codex/local-marketplaces/roster-local/plugins/roster`
- Codex reload is still required for composer-visible `@roster` / `/roster`
  surfaces.

Verification:

```sh
rg -n "Role Contextualization|Group Expansion|BCQ_III" \
  /Users/tom/.codex/skills/roster/SKILL.md \
  /Users/tom/.codex/local-marketplaces/roster-local/plugins/roster/commands/roster.md
```

The installed files include the expected v0.8/v0.8.1 sections.

## Invocation Mode

This run used the current Codex thread with the installed Roster skill guidance.
It did not separately verify UI composer visibility for `@roster` or `/roster`.

## Prompt 1

```text
Roster, 用 BCQ_III 做一個問卷 APP，形式是使用者填答問卷；使用者端要看到報告結果，醫師端要看到填答問卷和分數。
```

## Actual Roster Response 1

```text
這個 BCQ_III APP 我先用多組協作處理：

- 問卷與中醫組：整理 BCQ_III 題目、構面、體質解讀和報告文字
- 統計與計分組：定義填答轉分數、構面分數、門檻和結果解釋
- 使用者端組：設計填答流程、報告結果、解讀文字和下一步提醒
- 醫師端組：設計填答明細、分數表、構面比較和追蹤註記
- Quality 組：檢查分數一致性、醫療語氣、資料隱私和使用者誤解風險

如果這個分組方向可以，我再展開每組的小組成員、責任、觀點和交付物。
```

## Result 1

Status: `pass`

Notes:

- First response stayed group-level.
- It covered TCM questionnaire content, statistical scoring, user side,
  physician side, and Quality.
- It offered expansion as the next step.
- It did not expose internal governance or packet terminology.

## Prompt 2

```text
展開每組的小組成員，並列出每個人的責任、觀點和交付物。
```

## Actual Roster Response 2

```text
我會把 BCQ_III APP 的小組展開成這樣：

- 問卷與中醫組
  - 中醫內容負責人：責任是確認 BCQ_III 構面、題目意義和體質解讀；觀點是中醫概念是否被正確保留；交付物是可用的問卷內容規則。
  - 報告文字整理人：責任是把中醫概念轉成使用者看得懂的說明；觀點是報告是否清楚、是否容易被誤解成診斷；交付物是使用者端報告文案。
  - 醫師審核人：責任是檢查體質解讀和提醒語氣；觀點是臨床使用是否安全；交付物是醫療語氣修正和審核意見。

- 統計與計分組
  - 統計方法人員：責任是定義分數計算、構面分數和門檻；觀點是分數是否可解釋、可重現；交付物是計分規格。
  - 資料處理人員：責任是把問卷答案轉成可計算資料；觀點是欄位、缺漏值和轉換流程是否穩定；交付物是資料欄位和轉換規則。
  - 分數驗證人員：責任是核對使用者端和醫師端分數一致；觀點是題目、構面和分數是否對應；交付物是分數驗證結果。

- 使用者端組
  - UX 人員：責任是設計填答流程和報告閱讀順序；觀點是使用者是否能順利完成填答並理解結果；交付物是使用者流程。
  - APP 前端人員：責任是實作填答畫面和結果頁；觀點是互動是否清楚、錯誤狀態是否可理解；交付物是使用者端畫面。
  - 使用者代表：責任是指出看不懂、太嚴肅或容易誤解的地方；觀點是非醫療背景使用者；交付物是可讀性回饋。

- 醫師端組
  - 臨床使用者代表：責任是確認醫師需要哪些原始填答、分數和構面摘要；觀點是門診解讀和追蹤使用；交付物是醫師端需求。
  - 後台產品人員：責任是設計填答明細、分數表、排序和追蹤註記；觀點是醫師端工作流是否順；交付物是後台流程。
  - 權限與隱私人員：責任是確認誰能看哪些資料；觀點是個資、醫療資料和角色權限；交付物是權限規則。

- Quality 組
  - 醫療風險檢查人員：責任是檢查診斷、建議和免責語氣；觀點是避免過度醫療宣稱；交付物是風險清單。
  - 計分一致性檢查人員：責任是核對各端顯示的分數一致；觀點是計算結果是否可追蹤；交付物是一致性檢查。
  - 可用性檢查人員：責任是檢查報告是否清楚、欄位是否容易看錯；觀點是成品可用性；交付物是可用性問題。

這些是小組成員和觀點，不代表每個人都一定要變成獨立 agent；實作時可以依任務大小合併或拆開。
```

## Result 2

Status: `pass`

Notes:

- Expanded only after the follow-up prompt.
- Each member carried responsibility, perspective, and deliverable.
- It preserved user-facing report and physician-facing score/questionnaire
  surfaces.
- It explicitly avoided implying every member is a separate agent.

## Prompt 3

```text
加一個法務審，另外統計組需要一位模型驗證人員。
```

## Actual Roster Response 3

```text
我會這樣調整：

- 法務審：放在 Quality 組和交付前審核位置，檢查個資告知、資料使用範圍、醫療宣稱、免責文字和責任邊界。若法務需要擋下交付，我會把它視為交付前審核關卡；如果只是提供意見，則作為風險審查角色。
- 模型驗證人員：加入統計與計分組，負責檢查計分規則、模型或門檻是否可重現、是否和 BCQ_III 題目與構面對應、使用者端和醫師端是否顯示同一套結果。

這兩個新增角色會先放進現有小組和審核位置，不會自動變成獨立 agent。下一步我會更新小組表，標出法務審的審核權限，以及模型驗證人員的驗證交付物。
```

## Result 3

Status: `pass`

Notes:

- Legal review was treated as reviewer/approver depending on blocking
  authority.
- Model validator joined the statistics/scoring group.
- Response explained what changed and what happens next.
- It did not create separate agents by default.

## Overall Result

Status: `pass for this in-thread run`

This run supports the v0.8.1 behavior contract for the BCQ_III scenario. It is
not yet full behavior proof across different hosts or invocation surfaces,
because `@roster` and `/roster` require a Codex reload and were not separately
exercised in this run.

Recommended next step:

- Keep this as the first passing behavior run.
- Add one more scenario outside health/medical apps before calling the behavior
  broadly proven.
