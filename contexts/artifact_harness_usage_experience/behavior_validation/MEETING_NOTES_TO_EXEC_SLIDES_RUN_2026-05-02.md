# Meeting Notes To Executive Slides Behavior Run

Date: `2026-05-02`
Related releases: `v0.8.1`, `v0.8.2`
Status: `pass for current-thread Roster behavior / artifact production not run`

## Purpose

Use a non-medical, common workplace task to validate whether Roster can handle a
moderately complex multi-artifact workflow:

```text
meeting transcript -> meeting notes -> executive slide deck
```

This case is intentionally more ordinary than the BCQ_III app scenario. It tests
whether Roster can coordinate role expansion and work cards for a task that
starts as text cleanup but ends as a visual/manager-facing artifact.

This is a behavior validation run, not a real slide-deck production run.

## Scenario

The user asks:

```text
Roster, 幫我把一段會議逐字稿整理成會議記錄，再做成一份給主管看的簡報。最後簡報要控制在 6 頁內，主管只想知道結論、風險、待辦和需要決策的地方。
```

Task characteristics:

- source artifact: meeting transcript
- intermediate artifact: meeting notes
- final artifact: executive slide deck
- audience: manager / decision maker
- constraints: 6 pages or fewer, conclusion/risk/action/decision oriented
- quality needs: faithful summary, no missing decisions, readable slides,
  action owners and open decisions visible

## What This Validates

This scenario validates whether Roster can:

- keep the first response short and group-level;
- recognize a text-to-visual artifact chain;
- include both note-taking and slide-production roles;
- include executive-decision framing rather than only transcript cleanup;
- expand groups only when asked;
- turn expanded members into actionable work cards;
- include Quality checks for content fidelity and slide readability;
- avoid internal governance, packet, runtime, or CAP terminology in the ordinary
  response.

## Prompt 1: First Touch

```text
Roster, 幫我把一段會議逐字稿整理成會議記錄，再做成一份給主管看的簡報。最後簡報要控制在 6 頁內，主管只想知道結論、風險、待辦和需要決策的地方。
```

## Actual Roster Response 1

```text
這個任務我會用一個精簡小組處理：

- 會議內容整理：把逐字稿整理成重點、決議、待辦和負責人
- 主管簡報企劃：把會議內容改成主管需要看的結論、風險和決策題
- 簡報製作：控制在 6 頁內，整理頁面順序、標題和視覺層級
- Quality 檢查：確認沒有漏掉決議、待辦清楚、簡報能快速讀懂

你可以把逐字稿貼上來，或先說：
`展開小組成員和每個人的工作`
```

## Result 1

Status: `pass`

Notes:

- The first response stayed short and user-facing.
- It recognized the chain from transcript to notes to executive slides.
- It preserved the manager audience and 6-page constraint.
- It did not mention internal packet, runtime, or governance terms.

## Prompt 2: Expand Groups

```text
展開小組成員和每個人的責任、觀點、交付物。
```

## Actual Roster Response 2

```text
我會把這個會議記錄到主管簡報的任務展開成這樣：

- 會議內容整理組
  - 原始內容整理人：責任是清理逐字稿、合併重複發言、標出主題段落；觀點是內容不能被改意思；交付物是整理後的會議素材。
  - 會議紀錄人員：責任是抓重點、決議、待辦、負責人和期限；觀點是會後能不能追蹤；交付物是會議記錄。
  - 決議追蹤人員：責任是找出需要主管決策或後續追蹤的項目；觀點是哪些事會卡住進度；交付物是決策與待辦清單。

- 主管簡報企劃組
  - 主管視角整理人：責任是把會議內容改寫成主管需要看的結論、風險和決策題；觀點是主管是否能快速判斷；交付物是簡報故事線。
  - 簡報架構人員：責任是把內容控制在 6 頁內；觀點是每頁是否只有一個重點；交付物是頁面大綱。

- 簡報製作組
  - 簡報製作人員：責任是把大綱變成投影片；觀點是標題、圖表和文字層級是否清楚；交付物是簡報初稿。
  - 視覺整理人員：責任是讓重點、風險、待辦和決策題容易掃讀；觀點是主管能不能在短時間看懂；交付物是版面修正。

- Quality 組
  - 內容一致性檢查人員：責任是核對簡報和會議記錄是否忠於逐字稿；觀點是有沒有漏掉決議或誤解發言；交付物是一致性檢查。
  - 交付前檢查人員：責任是檢查 6 頁限制、待辦負責人、風險、需要決策的地方是否完整；觀點是這份簡報能不能直接交給主管；交付物是交付檢查清單。

這些是工作角色，不代表每個人都必須是獨立 agent；簡單版本可以合併，正式製作時再拆開。
```

## Result 2

Status: `pass`

Notes:

- Groups expanded only after the user asked.
- Each member has responsibility, perspective, and deliverable.
- The expansion preserves the intermediate meeting-notes artifact and final
  executive slide-deck artifact.
- It avoids forcing every member into a separate agent.

## Prompt 3: Work Cards

```text
展開工作卡，確認每個 agent 怎麼做、交給誰、怎麼算完成。
```

## Actual Roster Response 3

```text
我會先把這個任務整理成可執行的工作卡：

### Work Card 1: 原始內容整理人

- role_name: 原始內容整理人
- group: 會議內容整理組
- responsibility: 清理逐字稿、合併重複發言、標出主題段落和不清楚處
- perspective: 原意是否被保留，是否把發言人的語氣誤改成結論
- inputs: 原始逐字稿、會議主題、已知參與者或角色
- outputs_or_deliverables: 整理後的會議素材、主題段落、待確認片段
- done_condition: 逐字稿已分段，明顯重複或雜訊已移除，不確定內容有標註
- handoff_target: 會議紀錄人員、決議追蹤人員
- tool_or_capability_need: 文件編輯；若有錄音或影片來源，可能需要轉錄、播放或截圖能力
- agent_assignment: merged_with 會議紀錄人員 for small tasks; separate_agent when transcript is long
- open_questions: 是否有完整參與者名單與會議目的

### Work Card 2: 會議紀錄人員

- role_name: 會議紀錄人員
- group: 會議內容整理組
- responsibility: 抓重點、決議、待辦、負責人和期限
- perspective: 會後是否能依這份紀錄追蹤執行
- inputs: 整理後的會議素材、會議目的、參與者角色
- outputs_or_deliverables: 會議記錄、決議列表、待辦列表
- done_condition: 每個待辦都有 owner、due date 或待確認狀態；決議和討論事項分開
- handoff_target: 決議追蹤人員、主管視角整理人、內容一致性檢查人員
- tool_or_capability_need: 文件編輯與表格整理
- agent_assignment: separate_agent for note-heavy meetings; merged_with 原始內容整理人 for short meetings
- open_questions: 是否要保留逐字稿引用作為證據

### Work Card 3: 決議追蹤人員

- role_name: 決議追蹤人員
- group: 會議內容整理組
- responsibility: 找出需要主管決策、後續追蹤、卡住進度或跨部門協調的項目
- perspective: 哪些事情如果不處理會影響下一步
- inputs: 會議記錄、決議列表、待辦列表
- outputs_or_deliverables: 決策題清單、風險清單、追蹤項目清單
- done_condition: 需要主管看的項目已和一般待辦分開，風險和決策題有明確描述
- handoff_target: 主管視角整理人、簡報架構人員、交付前檢查人員
- tool_or_capability_need: 文件整理；若要和專案管理工具同步需額外工具授權
- agent_assignment: reviewer_only for small meetings; separate_agent for high-stakes project reviews
- open_questions: 主管是否只看需要決策的事項，還是也要完整進度摘要

### Work Card 4: 主管視角整理人

- role_name: 主管視角整理人
- group: 主管簡報企劃組
- responsibility: 把會議內容改寫成主管需要看的結論、風險、待辦和決策題
- perspective: 主管是否能快速判斷要不要介入、批准或追蹤
- inputs: 會議記錄、決策題清單、風險清單、主管偏好的溝通方式
- outputs_or_deliverables: 主管簡報故事線、每頁主訊息、需要決策的問題
- done_condition: 每頁都有明確主訊息，結論、風險、待辦和決策題沒有混在一起
- handoff_target: 簡報架構人員、簡報製作人員
- tool_or_capability_need: 文件與簡報大綱編輯
- agent_assignment: separate_agent for executive-facing work; simulated_perspective for early draft
- open_questions: 主管偏好摘要式、風險式，還是決策式簡報

### Work Card 5: 簡報架構人員

- role_name: 簡報架構人員
- group: 主管簡報企劃組
- responsibility: 把內容壓成 6 頁內的頁面順序和每頁重點
- perspective: 每頁是否只有一個重點，是否符合主管閱讀節奏
- inputs: 主管簡報故事線、決策題、風險與待辦清單
- outputs_or_deliverables: 6 頁內頁面大綱、頁面標題、每頁內容框架
- done_condition: 頁數不超過 6 頁，且每頁對應結論、風險、待辦或決策需求之一
- handoff_target: 簡報製作人員、視覺整理人員、交付前檢查人員
- tool_or_capability_need: 簡報大綱或 deck 編輯工具
- agent_assignment: merged_with 簡報製作人員 for small decks; separate_agent for executive decks
- open_questions: 是否需要公司模板或既有簡報格式

### Work Card 6: 簡報製作人員

- role_name: 簡報製作人員
- group: 簡報製作組
- responsibility: 把頁面大綱做成投影片初稿
- perspective: 標題、內容區塊、表格和視覺層級是否清楚
- inputs: 6 頁內頁面大綱、會議記錄、主管故事線、公司模板或樣式要求
- outputs_or_deliverables: 簡報初稿
- done_condition: 每頁有清楚標題和主訊息，內容可被 Quality 檢查
- handoff_target: 視覺整理人員、內容一致性檢查人員、交付前檢查人員
- tool_or_capability_need: presentation/deck 編輯能力；若要看畫面需 render、截圖或 CV 檢查
- agent_assignment: separate_agent when producing a real deck; not needed for behavior-only validation
- open_questions: 最終格式是 PPTX、PDF、Markdown slides，還是圖片簡報

### Work Card 7: 視覺整理人員

- role_name: 視覺整理人員
- group: 簡報製作組
- responsibility: 檢查投影片可讀性、視覺層級、文字量和重點是否被淹沒
- perspective: 主管是否能快速掃讀並抓到要決策的地方
- inputs: 簡報初稿、6 頁限制、主管閱讀需求
- outputs_or_deliverables: 版面修正建議、可讀性問題清單
- done_condition: 沒有明顯文字過密、層級混亂、重點不清或頁面目的不明
- handoff_target: 簡報製作人員、交付前檢查人員
- tool_or_capability_need: 截圖、render、CV/OCR 或簡報播放檢查；工具使用需授權
- agent_assignment: reviewer_only for draft checks; separate_agent for visual QA loop
- open_questions: 是否要做 1-2 輪畫面檢查後再交付

### Work Card 8: 內容一致性檢查人員

- role_name: 內容一致性檢查人員
- group: Quality 組
- responsibility: 核對簡報、會議記錄和逐字稿是否一致
- perspective: 有沒有漏掉決議、誤解發言、把討論改寫成已決定事項
- inputs: 原始逐字稿、會議記錄、簡報初稿
- outputs_or_deliverables: 一致性檢查結果、需要修正或補證據的地方
- done_condition: 簡報中的結論、風險、待辦和決策題都能追回會議內容
- handoff_target: 會議紀錄人員、主管視角整理人、交付前檢查人員
- tool_or_capability_need: 文件比對；長逐字稿可能需要檢索或引用定位
- agent_assignment: reviewer_only by default; separate_agent for high-risk reports
- open_questions: 是否允許補充會議外的背景資料

### Work Card 9: 交付前檢查人員

- role_name: 交付前檢查人員
- group: Quality 組
- responsibility: 檢查 6 頁限制、主管需求、待辦負責人、風險和決策題是否完整
- perspective: 這份簡報能不能直接交給主管看
- inputs: 簡報初稿、會議記錄、一致性檢查結果、視覺整理結果
- outputs_or_deliverables: 交付前檢查清單、阻斷問題、可延後改善項目
- done_condition: 阻斷問題已列出或修正，剩餘問題被標成可延後改善
- handoff_target: 簡報製作人員、主管視角整理人、使用者
- tool_or_capability_need: 文件審查、簡報預覽、截圖或 CV 檢查
- agent_assignment: reviewer_only; approval_gate_candidate only if user grants final sign-off authority
- open_questions: 主管是否需要附錄或原始會議記錄連結
```

## Result 3

Status: `pass`

Notes:

- Work cards include all required v0.8.2 fields.
- The task is non-medical and common enough for ordinary user testing.
- The cards distinguish the meeting-record artifact from the executive-slide
  artifact.
- The cards include a visual Quality path without pretending CV/tool access is
  automatically authorized.
- The output keeps assignment modes explicit without asking the user to manage
  them.

## Overall Result

Status: `pass for current-thread behavior`

This case supports the claim that Roster's group expansion and Agent Work Card
behavior is not limited to the BCQ_III medical/statistical scenario.

It also shows the next missing layer clearly: the role list is actionable, but
the interaction edges are still implicit. A future `v0.9.0` Role Interaction
Patterns pass should formalize edges such as:

- 原始內容整理人 -> 會議紀錄人員: handoff
- 會議紀錄人員 <-> 內容一致性檢查人員: review_challenge
- 主管視角整理人 <-> 簡報架構人員: peer_alignment
- 簡報製作人員 <-> 視覺整理人員: quality_loop
- 交付前檢查人員 -> 使用者: approval_signoff only if granted

## Remaining Boundary

This run does not create a real meeting note or slide deck. A later artifact
production validation should use an actual transcript, generate the meeting
notes, produce a small deck, and run a visual Quality check on the exported
slides.

