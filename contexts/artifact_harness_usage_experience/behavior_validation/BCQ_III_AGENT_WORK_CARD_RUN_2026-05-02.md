# BCQ_III Agent Work Card Behavior Run

Date: `2026-05-02`
Related scenario: `BCQ_III_GROUP_EXPANSION_VALIDATION.md`
Related releases: `v0.8.1`, `v0.8.2`
Status: `pass for current-thread @roster invocation / broader cross-host proof pending`

## Purpose

Complete the BCQ_III behavior scenario after the `v0.8.2` Agent Work Card
contract.

The previous BCQ_III run validated that Roster can show group-level planning,
expand groups into concrete members, and accept added roles without forcing each
member into a separate runtime agent. This run checks the next requirement:
expanded members must become actionable work units with responsibility,
perspective, inputs, deliverables, done conditions, handoff targets, capability
needs, assignment mode, and open questions.

This is a Roster behavior validation run, not a BCQ_III app implementation.

## Setup

The installed Roster skill was refreshed before this run:

```sh
./scripts/brain.sh roster-install --codex-home /Users/tom/.codex --force --json
```

Installed files were checked for `Agent Work Card` text:

```sh
rg -n "Agent Work Card|done_condition|tool_or_capability_need|agent_assignment" \
  /Users/tom/.codex/skills/roster/SKILL.md \
  /Users/tom/.codex/local-marketplaces/roster-local/plugins/roster/commands/roster.md
```

The installed skill and local plugin command both included the expected v0.8.2
work-card guidance.

## Invocation Mode

The user invoked:

```text
[@roster](plugin://roster@roster-local) 把先把 BCQ_III 跑完
```

This run used the current Codex app thread with the installed Roster skill
guidance and an explicit `@roster` plugin mention in the user message. It does
not separately prove `/roster` slash-command behavior or behavior in a fresh
external host.

## Roster Output

我會把 BCQ_III APP 先收斂成這個可執行隊形：

- 問卷與中醫組：確認 BCQ_III 題目、構面、體質解讀和報告文字
- 統計與計分組：定義填答轉分數、構面分數、門檻和可重現檢查
- 使用者端組：設計填答流程、報告結果、解讀文字和下一步提醒
- 醫師端組：設計填答明細、分數表、構面比較和追蹤註記
- Quality 與法務組：檢查醫療語氣、資料隱私、法務風險和分數一致性

下面是本輪需要真的能分工的 Agent Work Cards。

### Work Card 1: 專案協調人

- role_name: 專案協調人
- group: 整體協調
- responsibility: 收斂 BCQ_III APP 的目標、雙端範圍、交付順序和待確認問題
- perspective: 任務是否被拆成可執行的小段，使用者端與醫師端是否沒有互相漏接
- inputs: 使用者需求、BCQ_III 問卷來源、預期使用場景、交付時程
- outputs_or_deliverables: 專案範圍表、第一階段任務順序、角色 handoff 清單
- done_condition: 每個主要小組都有明確輸入、輸出、下一接收者和未決問題
- handoff_target: 問卷與中醫組、統計與計分組、使用者端組、醫師端組、Quality 與法務組
- tool_or_capability_need: 文件編輯與任務追蹤；不需要額外 runtime
- agent_assignment: merged_with 使用者端產品人員 for small planning; separate_agent for implementation planning
- open_questions: 第一版是否只做原型，還是要進入可部署 APP 規格

### Work Card 2: 中醫內容負責人

- role_name: 中醫內容負責人
- group: 問卷與中醫組
- responsibility: 確認 BCQ_III 題目、構面、體質解讀和報告文字是否正確
- perspective: 中醫概念是否被過度簡化、誤譯或變成不當診斷
- inputs: 正式 BCQ_III 題目、構面定義、計分或判讀來源、使用場景
- outputs_or_deliverables: 問卷內容規則、構面說明、體質解讀草稿
- done_condition: 每個題目都能對應到構面，報告文字不超出來源可支持範圍
- handoff_target: 統計方法人員、報告文字整理人、醫療風險檢查人員
- tool_or_capability_need: 來源文件讀取與引用整理；若需外部文獻查找需額外授權
- agent_assignment: separate_agent for content review; simulated_perspective for early rough planning
- open_questions: 是否已有正式授權或公開可用的 BCQ_III 題目與計分規則

### Work Card 3: 統計方法人員

- role_name: 統計方法人員
- group: 統計與計分組
- responsibility: 定義填答轉分數、構面分數、門檻和結果解釋規則
- perspective: 分數是否可解釋、可重現，是否符合 BCQ_III 題目與構面
- inputs: BCQ_III 題目、構面定義、填答資料格式、使用者端與醫師端顯示需求
- outputs_or_deliverables: 計分規格、構面分數定義、結果解釋規則
- done_condition: 每一題都能追到構面與計分規則，使用者端和醫師端分數定義一致
- handoff_target: 資料處理人員、模型驗證人員、使用者端組、醫師端組
- tool_or_capability_need: 試算表或統計腳本；若要執行程式，必須走工具授權
- agent_assignment: merged_with 模型驗證人員 for small tasks; separate_agent for high-risk validation
- open_questions: 是否存在正式分數門檻、常模或臨床解讀規則

### Work Card 4: 資料處理人員

- role_name: 資料處理人員
- group: 統計與計分組
- responsibility: 把使用者填答轉成可計算、可追蹤、可稽核的資料結構
- perspective: 欄位命名、缺漏值、反向題、版本變更是否會讓分數不可重現
- inputs: 問卷題目、答案選項、計分規則、使用者與醫師端資料需求
- outputs_or_deliverables: 資料欄位表、答案轉換規則、缺漏值處理規則
- done_condition: 每個答案欄位都有型別、合法值、轉分規則和錯誤處理
- handoff_target: 統計方法人員、模型驗證人員、APP 前端人員、後台產品人員
- tool_or_capability_need: 表格或 JSON schema 編輯；測試資料生成可能需要腳本
- agent_assignment: separate_agent if schema becomes code; merged_with 統計方法人員 for paper planning
- open_questions: 問卷版本是否需要保留歷史版本與分數重算能力

### Work Card 5: 模型驗證人員

- role_name: 模型驗證人員
- group: 統計與計分組
- responsibility: 檢查計分規則、模型或門檻是否可重現，是否和 BCQ_III 題目與構面對應
- perspective: 使用者端結果、醫師端分數表、原始填答是否能互相追溯
- inputs: 計分規格、資料欄位表、測試填答資料、預期分數結果
- outputs_or_deliverables: 驗證案例、分數一致性檢查、錯誤案例清單
- done_condition: 至少有代表性填答案例可重算，且雙端顯示結果一致
- handoff_target: Quality 組、使用者端組、醫師端組、專案協調人
- tool_or_capability_need: 統計腳本、試算表或測試 runner；工具使用需授權
- agent_assignment: reviewer_only for initial planning; separate_agent for implementation validation
- open_questions: 第一版驗證要用人工試算、試算表，還是自動化測試

### Work Card 6: 使用者端產品人員

- role_name: 使用者端產品人員
- group: 使用者端組
- responsibility: 設計使用者填答流程、報告閱讀順序、結果說明和下一步提醒
- perspective: 一般使用者是否能完成填答並理解結果，而不把報告當成診斷
- inputs: 問卷內容規則、計分規格、體質解讀草稿、風險語氣要求
- outputs_or_deliverables: 使用者端流程、報告頁資訊架構、提示與免責文字位置
- done_condition: 使用者能從填答進入結果頁，看到清楚分數、解讀和非診斷提醒
- handoff_target: APP 前端人員、報告文字整理人、可用性檢查人員
- tool_or_capability_need: 產品文件或 wireframe；若要視覺驗證需截圖/畫面檢查能力
- agent_assignment: separate_agent for app planning; merged_with 專案協調人 for early planning
- open_questions: 使用者報告要顯示原始分數、體質分類，還是兩者都顯示

### Work Card 7: 醫師端產品人員

- role_name: 醫師端產品人員
- group: 醫師端組
- responsibility: 設計醫師看到的填答明細、分數表、構面比較和追蹤註記
- perspective: 醫師是否能快速看出重點、追溯答案，並用於門診或追蹤討論
- inputs: 原始填答資料、計分規格、醫師端使用需求、權限規則
- outputs_or_deliverables: 醫師端資訊架構、分數表規格、填答明細規格
- done_condition: 每個醫師端欄位都有來源、用途、可見權限和追蹤方式
- handoff_target: 後台產品人員、權限與隱私人員、Quality 組
- tool_or_capability_need: 產品文件、資料表或 UI 草圖；若要畫面檢查需 CV/截圖能力
- agent_assignment: separate_agent for physician workflow; simulated_perspective if only drafting
- open_questions: 醫師端是否需要多次填答趨勢、個案比較或匯出功能

### Work Card 8: APP 前端人員

- role_name: APP 前端人員
- group: 使用者端組 / 醫師端組
- responsibility: 把填答畫面、結果頁、醫師分數表和填答明細轉成可操作介面
- perspective: 使用者操作是否清楚，醫師端資訊是否密集但可讀
- inputs: 使用者端流程、醫師端資訊架構、資料欄位表、設計規格
- outputs_or_deliverables: 前端頁面或原型、狀態與錯誤處理、基本互動流程
- done_condition: 主要路徑可以從填答到結果，醫師端可檢視分數與原始回答
- handoff_target: 可用性檢查人員、計分一致性檢查人員、專案協調人
- tool_or_capability_need: 前端框架、瀏覽器測試、截圖或 CV 檢查；工具需授權
- agent_assignment: separate_agent when implementation starts; not needed for current planning-only run
- open_questions: APP 技術棧、部署方式、資料儲存方式尚未指定

### Work Card 9: 法務與隱私審查人員

- role_name: 法務與隱私審查人員
- group: Quality 與法務組
- responsibility: 檢查個資告知、資料使用範圍、醫療宣稱、免責文字和責任邊界
- perspective: 使用者資料與醫療相關說明是否可能造成法律或倫理風險
- inputs: 使用者端文案、醫師端功能、資料欄位表、資料保存與分享需求
- outputs_or_deliverables: 法務風險清單、隱私告知需求、交付前審查意見
- done_condition: 高風險資料與醫療宣稱都有對應提醒、限制或待確認事項
- handoff_target: 專案協調人、使用者端產品人員、醫師端產品人員
- tool_or_capability_need: 文件審查；正式法務判斷需使用者提供合格審查來源
- agent_assignment: approval_gate_candidate if user grants blocking authority; reviewer_only by default
- open_questions: 法務審是否有正式擋下交付的權限

### Work Card 10: Quality 檢查人員

- role_name: Quality 檢查人員
- group: Quality 與法務組
- responsibility: 檢查分數一致性、醫療語氣、資料隱私、可用性和成品誤解風險
- perspective: 第一版能否交付給使用者理解，並能被醫師端追溯和審核
- inputs: 計分驗證結果、使用者端流程、醫師端流程、法務風險清單
- outputs_or_deliverables: 交付前檢查清單、阻斷問題、可延後改善項目
- done_condition: 短期交付阻斷問題已列出，長期流程改善已分開標記
- handoff_target: 專案協調人、APP 前端人員、中醫內容負責人、統計方法人員
- tool_or_capability_need: 文件審查、測試資料、畫面截圖或 CV 檢查；視覺工具需授權
- agent_assignment: reviewer_only for planning; separate_agent for visual/product QA loop
- open_questions: 是否要在第一版就做 2-3 輪視覺與可用性自我迭代

## Validation Result

- prompt_1_group_preview: `pass`, already recorded in
  `BCQ_III_GROUP_EXPANSION_RUN_2026-05-02.md`
- prompt_2_group_expansion: `pass`, already recorded in
  `BCQ_III_GROUP_EXPANSION_RUN_2026-05-02.md`
- prompt_3_added_roles: `pass`, already recorded in
  `BCQ_III_GROUP_EXPANSION_RUN_2026-05-02.md`
- prompt_4_work_cards: `pass`

Pass evidence:

- Work cards include all required v0.8.2 fields.
- Expanded members became actionable work units, not only labels for the user.
- Role assignment distinguishes separate agents, merged roles, simulated
  perspectives, reviewer-only roles, and approval-gate candidates.
- Capability needs are listed as needs, not as authorization.
- Legal review is not treated as a blocker unless the user grants that
  authority.
- The run preserves the user-facing BCQ_III APP shape: questionnaire input,
  user report, physician score/questionnaire view, scoring validation, and
  Quality review.

## Remaining Boundary

This is enough to say the BCQ_III behavior scenario is complete for the current
thread and installed Roster skill guidance.

It is not yet a full cross-host behavior proof because this run did not
separately exercise `/roster` in a fresh external thread, nor did it implement
the BCQ_III APP. Those belong to later product validation or implementation
work.

