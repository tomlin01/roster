# BCQ_III Role Interaction Pattern Behavior Run

Date: `2026-05-02`
Related scenario:

- `BCQ_III_GROUP_EXPANSION_RUN_2026-05-02.md`
- `BCQ_III_AGENT_WORK_CARD_RUN_2026-05-02.md`

Related release: `v0.9.0`
Status: `pass for current-branch Roster behavior / installed-skill proof pending`

## Purpose

Validate the next BCQ_III behavior layer after Agent Work Cards:

```text
roles -> group/member expansion -> work cards -> role interaction patterns
```

This run checks whether Roster can explain how the BCQ_III APP team works
together, not only who exists or what each role owns.

This is a behavior validation run. It does not implement the BCQ_III APP, does
not execute runtime agents, and does not grant tool or model access.

## Setup

The current branch version of `skills/roster/SKILL.md` contains the `Role
Interaction Patterns` section and required BCQ_III interaction examples.

The installed user-level skill at `/Users/tom/.codex/skills/roster/SKILL.md`
did not show the v0.9 Role Interaction section during this run. Therefore this
test uses the repository branch skill as the behavior source of truth.

This means the run validates current-branch behavior, not cross-host or
installed `@roster` / `/roster` behavior.

## Prompt

```text
Roster, 用 BCQ_III 問卷 APP 的團隊，補上角色之間怎麼互動。
要包含中醫內容、統計計分、使用者端、醫師端、Quality loop，以及法務審是否能擋下交付。
```

## Actual Roster Response

```text
我會把 BCQ_III APP 的協作方式整理成幾條工作線：

- 中醫內容先把題目、構面和體質解讀整理成可計分的規格，再交給統計與計分組確認分數邏輯。
- 統計方法人員和模型驗證人員要先對齊計分規則、測試案例和雙端顯示邏輯；如果驗證結果不一致，先回到統計方法人員修正規則。
- 使用者端和醫師端可以並行設計，但兩邊必須共用同一套分數定義：使用者端負責報告能不能看懂，醫師端負責原始填答和分數能不能追溯。
- APP 前端做出填答、報告、分數表和明細後，Quality 會把問題回送給對應角色：文字誤解回中醫內容，分數不一致回統計，畫面或流程問題回前端與產品人員。
- 法務與隱私審查先作為交付前風險審查；只有當你明確指定法務有擋下交付的權限，或任務政策要求時，它才是 blocking sign-off。

所以第一版不是把每條互動都拆成獨立 agent，而是先讓角色知道誰要對齊、誰要挑戰、誰要修正、誰能審核。
如果進入實作，我會再把高風險的統計驗證、法務審查和 Quality loop 拆成更明確的工作卡或獨立執行單元。
```

## Interaction Edge Extraction

The response can be mapped into v0.9 interaction edges:

- 中醫內容負責人 -> 統計方法人員
  - interaction_type: `handoff`
  - shared_artifact: BCQ_III 題目、構面、體質解讀、可計分規格
  - done_condition: 統計與計分組能用同一套內容定義建立分數規則
  - authority_boundary: work transfer, not approval

- 統計方法人員 <-> 模型驗證人員
  - interaction_type: `peer_alignment` before scoring is stable;
    `review_challenge` when validation checks completed scoring output
  - shared_artifact: 計分規則、測試案例、雙端顯示邏輯
  - revision_or_escalation_rule: 分數不一致時回到統計方法人員修正
  - authority_boundary: alignment/revision request, not final approval by default

- 使用者端產品人員 + 醫師端產品人員
  - interaction_type: `parallel_contribution`
  - shared_artifact: shared score definition and integration note
  - expected_output_or_decision: 使用者端報告與醫師端分數/填答明細使用同一套分數定義
  - fallback_owner: 專案協調人

- APP 前端人員 <-> Quality 檢查人員
  - interaction_type: `quality_loop`
  - shared_artifact: 填答畫面、報告頁、分數表、填答明細、Quality findings
  - revision_or_escalation_rule: findings return to the responsible producer
  - authority_boundary: requests revision; blocking requires user/policy authority

- 法務與隱私審查人員 -> 專案協調人
  - interaction_type: `approval_signoff` only if granted; otherwise reviewer-only
  - shared_artifact: 法務風險清單、隱私告知、醫療宣稱與免責文字
  - authority_boundary: reviewer-only by default; blocking only with explicit
    user or policy authority

## Validation Result

Status: `pass for current-branch behavior`

Pass evidence:

- The response explains role-to-role coordination rather than only listing roles.
- It includes required BCQ_III edges:
  - 中醫內容 -> 統計計分: `handoff`
  - 統計方法 <-> 模型驗證: `peer_alignment` / `review_challenge`
  - 使用者端 + 醫師端: `parallel_contribution`
  - APP 前端 <-> Quality: `quality_loop`
  - 法務與隱私 -> 專案協調: conditional `approval_signoff`
- It keeps the user-facing response plain and does not expose `Team Architect`,
  `CAP`, runtime adapter, or packet-chain language.
- It does not imply every interaction becomes a separate runtime agent.
- It treats legal sign-off as blocking only when explicitly granted.
- It treats Quality as returning findings to responsible producers rather than
  owning governance or tool authorization.

## Remaining Boundary

This run does not prove:

- installed `@roster` or `/roster` surfaces have picked up v0.9;
- a fresh external host will produce the same behavior;
- the BCQ_III APP can be implemented end to end;
- runtime subagents, CAP authorization, legal approval, or Quality CV tools are
  automatically available.

Recommended next steps:

- After merge/tag, reinstall Roster and rerun a short installed-skill check.
- Run the second v0.9 behavior case with a non-medical task:
  `meeting transcript -> meeting notes -> executive slides`.
