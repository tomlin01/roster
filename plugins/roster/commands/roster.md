---
description: Coordinate an artifact task with Roster
argument-hint: [artifact-task]
allowed-tools: [Read, Glob, Grep, Bash, Write, Edit]
---

# /roster

Use Roster to coordinate the user's artifact task with a working team, quality
checks, tool boundaries, and resumable packet output in the active workspace.

## Arguments

The user invoked this command with: $ARGUMENTS

## Workflow

1. Identify the active workspace. If several folders are plausible, ask one
   short location question before writing files.
2. Read `references/install_manifest.json` from the installed Roster plugin if
   available. Use its `brain_command` value instead of guessing the kit path.
3. If the manifest is unavailable, ask for the local Roster kit folder before
   running adapter commands.
4. Route the task through Roster:

```bash
<brain_command> packet-route "$ARGUMENTS" --path <workspace> --json
```

5. Create packet files only when the route is create-ready or the user clearly
   asks to set up the task forms:

```bash
<brain_command> packet-route "$ARGUMENTS" --path <workspace> --create --json
```

6. Reply in plain user-facing language first. Do not expose Artifact Harness,
   HR, Team Architect, CAP, runtime, control-plane, or packet-chain terminology
   unless the user asks for review, debug, or governance detail.

## First-Touch Response

Use the smallest useful team shape in the first reply. Keep layer coverage in
mind internally, but do not show `Level 1`, `Level 2`, `complexity score`, or
similar labels to the user.

Plain handling phrases are enough:

```text
這個任務我會直接處理並自檢。
```

```text
這個任務我先用一個精簡小組處理。
```

```text
這個任務牽涉幾個面向，我會先分成幾組協作。
```

```text
這個任務的目標和權責還需要先對齊，我先幫你定隊形。
```

For meeting-note tasks, use concrete Traditional Chinese roles:

```text
我先用一個精簡會議小組處理：

- 轉錄人員：整理錄音或逐字稿
- 會議紀錄人員：抓重點、決議、待辦事項和負責人
- 會議負責人：確認紀錄是否符合會議目的和後續追蹤需求

如果可以，我就照這樣開始；你也可以直接說要加主管、法務、PM 或其他角色。
```

Natural role edits such as `加一個主管`, `讓 PM 看一下`, `需要法務審`, and
`加一個學生視角` should adjust the team shape without exposing internal planning
mechanics.

## Completion Response (v0.11.2 Receipt Trigger Clarification)

For non-trivial completed work, keep the public reply in this order:

```text
outcome -> role actions -> convergence
```

Include a compact Role Execution Receipt section:

```text
本次分工執行
```

Rules:

- Role Execution Receipt is part of the ordinary completion reply, not debug
  trace
- include only roles or perspectives that actually contributed
- describe concrete actions, not just titles
- avoid internal governance terms in ordinary completion replies
- do not claim multi-agent runtime execution unless that actually happened
- when no separate runtime agent was spawned, describe as `角色分工` or
  `視角分工`
- if a needed capability (web, browser, visual/CV, plugin/connector,
  subagent) was unavailable, note the limitation briefly
- No debug trace != no receipt
  - `不要展開 debug trace` means short receipt, not receipt removal for
    qualifying tasks
- Future role-summary feature != current-turn receipt
  - if the response mentions future role-summary planning, still include this
    answer's current-turn receipt when qualifying
- Simple qualifying task != no receipt
  - task simplicity can shorten the receipt, not remove the trigger

Qualifying signals:

- the user asked for multiple dimensions
- the response used multiple roles, perspectives, or checks
- the result includes product, engineering, quality, domain, source, visual,
  or risk judgment
- the user needs to judge whether declared roles actually did work

Good pattern:

```text
我已經整理出可執行的三步修正方案。

本次分工執行：
- 規劃視角：把問題拆成入口、驗證、文件三段。
- 技術視角：對照現有命令與文件，確認不擴張底層執行方式。
- 品質視角：刪除超出範圍提案，保留最小可交付差異。

最後收斂：先交付文件契約，執行層改動留在後續版本。
```

Bad pattern:

```text
以下是結論...
```

If a multi-role task was declared, this bad pattern hides who did what.

Bad trigger-miss pattern:

```text
以下是兩週規劃，角色摘要先放到未來功能。
```

If this answer used multiple perspectives, this is not acceptable. Keep a short
current-turn receipt.

## Role Context

Interpret role edits before replying. A user-added role can be a domain
extension, a peer role, a reviewer/approver, or a counter-perspective. Adding a
role does not automatically add a new agent.

Use these practical defaults:

- `技術人員加入金融 domain`: merge into one engineering + finance technical
  perspective unless the task risk or user wording requires separation.
- `新增一位金融技術人員，跟原本技術人員同級`: add a peer role and an alignment
  step; do not make the peer an approver by default.
- `金融技術人員要核准模型結果才能交付`: add a pre-delivery review or sign-off
  position.
- `加一個學生視角`: add a counter-perspective that challenges clarity,
  pacing, examples, and audience fit.
- `加一個主管`: add direction, priority, and final-fit review.
- `讓 PM 看一下`: add scope, sequencing, dependency, and handoff review.
- `需要法務審`: add legal review and confirm blocking authority when the
  consequence matters.

Keep the user-facing explanation short: say how the team shape changes and what
happens next. Do not dump role taxonomy unless the user asks for design detail.

## Group Expansion

For broad tasks, show groups before members. Expand into members only when the
user asks to expand, the task moves into implementation planning, or risk
requires clear ownership.

Expanded members should include responsibility, perspective, and deliverable.
Do not imply every expanded member is a separate agent. Do not treat group
expansion as full role interaction-edge modeling.

When expanded members need to become executable rather than only visible, offer
or emit Agent Work Cards. Do not dump full work cards in ordinary first-touch
replies. Use them when the user asks `誰做什麼`, `展開工作`, `工作卡`,
`每個 agent 的職責`, or equivalent; when the task moves into implementation
planning; when risk or authority clarity matters; or when an added role has
review, sign-off, domain, tool, or quality responsibility.

Each work card should include:

- role_name
- group
- responsibility
- perspective
- inputs
- outputs_or_deliverables
- done_condition
- handoff_target
- tool_or_capability_need
- capability_needs: capability, purpose, availability, evidence_expected, and
  fallback when detailed execution planning is needed
- agent_assignment: `separate_agent`, `merged_with`,
  `simulated_perspective`, `reviewer_only`, or `approval_gate_candidate`
- open_questions

Assignment guidance:

- a work card can become a separate agent, but does not have to
- one agent may carry several cards for small tasks
- simulated perspectives are valid when runtime separation is unnecessary or
  unavailable
- reviewer-only roles check outputs but do not own production
- approval-gate candidates do not approve or block delivery unless the user or
  policy gives explicit authority
- tool_or_capability_need is not authorization; CAP still owns tool, plugin,
  approval, and runtime allowlist decisions
- handoff_target is only the next receiver, not the full v0.9 interaction-edge
  model

Do not ask the user to choose assignment modes unless they ask for design
detail. Work cards do not replace review, final acceptance, approval evidence,
CAP, runtime policy, or the Team Operating Packet.

## Capability-Aware Role Execution

Use Capability-Aware Role Execution when roles need an execution plan, not only
a name and responsibility:

```text
role -> work -> interaction -> capability need -> availability -> fallback
```

Roster plans capability needs; CAP authorizes access; runtime executes.

Capability categories are `reasoning_only`, `filesystem_read`,
`filesystem_write`, `code_execution`, `web_search`, `browser`,
`visual_capture`, `vision_review`, `specialist_skill`, `plugin_or_connector`,
and `subagent_execution`.

Availability states are `available`, `available_after_reload`,
`available_if_approved`, `unknown`, and `unavailable`. Use `unknown` when the
local environment has not proven host support, especially for web search,
browser, visual capture, vision review, plugins/connectors, and subagents.

Do not expose the capability matrix in ordinary first-touch replies. Mention
only practical behavior and fallback:

```text
我會先用本機資料整理第一版；如果需要外部查證，我會讓查證角色去找來源並留下引用。
如果目前環境不能查，我會改請你提供來源。
```

Examples for detailed planning:

- Research Reviewer: `web_search`, `browser`; evidence is URLs, dates, source
  summaries; fallback is user sources or local files.
- Visual QA: `visual_capture`, `vision_review`, `browser`; evidence is
  screenshot/render/frame/OCR/CV findings; fallback is limited visual
  acceptance.
- Slide Producer: `specialist_skill`, `plugin_or_connector`,
  `filesystem_write`; evidence is deck/slide output plus verification;
  fallback is outline or HTML draft.
- Skill Reviewer: `filesystem_read`, optional `filesystem_write`; evidence is
  diagnosis, file-line findings, optional patch; fallback is no-patch review.
- Statistical Reviewer: `code_execution`, `specialist_skill`; evidence is
  reproducible checks, test cases, assumption notes; fallback is conceptual
  review.

## Role Interactions

When the roster needs more than `who does what`, explain how roles work together
in plain language first. Keep ordinary replies practical:

```text
我會讓會議紀錄先交給簡報企劃，再由 Quality 回頭檢查是否漏掉決議。
```

Use internal interaction patterns only when creating or reviewing the detailed
team plan. Keep the layers separate:

- role list: visible team roles
- group/member expansion: concrete members inside broad groups
- Agent Work Cards: ownership, inputs, outputs, completion, and next receiver
- Role Interaction Patterns: role-to-role edges for coordination, revision,
  review, alignment, sign-off, and fallback

Supported interaction types:

- `handoff`: one role passes a prepared artifact to another role
- `dialogue_friction_loop`: a counter-perspective challenges a primary role
  before production
- `peer_alignment`: same-level roles align assumptions, definitions, or
  boundaries before handoff
- `review_challenge`: one role checks another role's output and may request
  revision without blocking by default
- `approval_signoff`: blocks only when the user or policy grants blocking
  authority
- `parallel_contribution`: multiple roles create separate parts that later
  integrate
- `quality_loop`: Quality findings return to the responsible producer or
  upstream owner for correction and recheck

For each detailed edge, record source role, target role or roles, interaction
type, direction, trigger, shared artifact, expected output or decision, done
condition, revision or escalation rule, authority boundary, capability
implication, and fallback owner.

Boundaries:

- interaction edges change task graph behavior, not governance ownership
- interaction edges do not grant tools, plugins, model access, screenshots,
  OCR, filesystem access, or runtime authority
- capability implications are inputs for CAP only
- interaction edges do not automatically spawn subagents
- manager, legal, or final checks block delivery only when user wording or
  policy grants that authority

Example mappings:

- Teacher + Student -> `dialogue_friction_loop`
- Engineering Technical Staff + Financial Technical Staff -> `peer_alignment`
- Producer + Quality Reviewer -> `quality_loop`
- 原始內容整理人 -> 會議紀錄人員 -> `handoff`
- 會議紀錄人員 <-> 內容一致性檢查人員 -> `review_challenge`
- 主管視角整理人 <-> 簡報架構人員 -> `peer_alignment`
- 簡報製作人員 <-> 視覺整理人員 -> `quality_loop`
- 交付前檢查人員 -> 使用者 -> `approval_signoff` only if granted

Example first touch:

```text
這個任務牽涉中醫內容、統計邏輯和 APP 雙端流程，我會先分成幾組協作：

- 問卷與中醫組：整理 BCQ_III 題目、構面、體質解讀和報告文字
- 統計與計分組：定義分數計算、構面分數、門檻和可信度提醒
- 使用者端組：設計填答流程、報告結果、解讀文字和下一步建議
- 醫師端組：設計填答明細、分數表、風險提示和追蹤註記
- Quality 組：檢查分數一致性、醫療語氣、資料隱私和使用者誤解風險

如果這個分組方向可以，我再展開每組的小組成員和第一步。
```

## Guardrails

- Keep packet output under `<workspace>/contexts/artifact_harness_runs/`.
- Do not start a server, daemon, database, or separate orchestration UI.
- Do not silently record preferences. Use `roster-preferences remember` only
  when the user explicitly asks Roster to remember a future coordination
  preference.
- Treat visual/CV inspection as a capability request governed by the task's
  tool-access boundary.

## Examples

```text
/roster help me turn these meeting notes into a project plan
/roster 幫我把這些會議筆記整理成可執行的專案計畫
/roster set up quality checks for this report
```
