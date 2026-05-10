---
name: roster
description: Use when the user invokes Roster for staffing, coordination, planning, review, or artifact-task setup. Ordinary Roster replies must begin with 本次啟用 and must not mention route/packet/preference internals unless the user asks for debug or governance detail.
---

# Roster

Use Roster as the local staffing-and-coordination surface for artifact-producing
work. Keep ordinary user interaction in plain language and use the repo packet
engine as an internal adapter.

## Mandatory Final Answer Shape

For every non-trivial explicit Roster invocation, the final answer MUST begin
with `本次啟用：...` and MUST include all five visible parts below:

```text
本次啟用：<N> 個 agent 或 role-agents（簡短說明）
目前階段：<目前工作階段；若正式 artifact 這輪不產出就明說>

<useful work for the user's request>

本次分工執行：
- <role or perspective>：<concrete action done in this answer>

最後收斂：<single convergence judgment or next decision>
```

This is a hard response wrapper, not an optional style. A non-trivial Roster
answer that starts with `目前階段`, `我會先`, `這輪先`, or only a normal plan is
invalid; rewrite it before sending.

The first line must use the literal word `agent` or `role-agents`. Do not write
only `角色`, `小組`, `視角`, or `流程` in place of the agent count.

This wrapper still applies when the user says `先不要產出正式內容`, `不要寫正式
review`, `不要展開 debug trace`, or asks only for initial planning. Compress the
work section when needed, but do not remove `本次啟用`, `目前階段`, `本次分工執行`,
or `最後收斂`.

If you read this skill file, consult memory, use tools, or run adapters, the
final user-facing answer still follows the wrapper. Tool output, route checks,
and memory snippets are not the final answer.

Ordinary replies must not mention `route check`, `packet-route`,
`artifact-harness`, `preference`, `roster_preferences`, `registry`, `routing
score`, `CAP`, `runtime adapter`, or `control plane`. Use those terms only when
the user explicitly asks for review, debug, implementation, or governance detail.

## Trigger

Use this skill when the user asks for:

- `Roster, ...` task coordination
- staffing or role design for an artifact task
- project/task boundary setup
- Quality direction, self-check setup, or short-term vs long-term correction
  planning for an artifact task
- explicit Roster preference memory such as "記住", "記錄", "每次", "預設",
  "always", or "from now on" for future coordination behavior in this workspace
- Team Architect, Capability Access Packet, runtime mapping, or review handoff
- resuming or inspecting a Roster packet run
- installing, uninstalling, or checking the Roster coordination surface

After `roster-install` and a Codex reload, `@roster` and `/roster` are the
intended installed invocation targets. If the current Codex UI does not surface
the plugin immediately, fall back to `Roster, ...` and use `roster-health` to
inspect registration state.

## Operating Boundary

- Artifact Harness owns task rules, contract, acceptance, and boundary.
- HR owns staffing and role design only.
- Team Architect owns collaboration pattern, shared artifacts, task graph,
  convergence, and CAP generation.
- Capability Access Packet owns skill, plugin, tool authorization, approval
  gates, and runtime allowlist.
- Runtime adapters execute only; they do not own governance.
- Quality consumes Artifact Harness acceptance and turns it into practical
  self-check behavior. It does not replace the Artifact Harness SPEC, CAP,
  runtime authorization, tool ownership, or final acceptance.

## Response-First Workflow

For ordinary explicit Roster planning, review, and setup requests, the
user-facing response comes before any adapter mechanics.

If the user says this turn should not produce a formal artifact, PRD, review,
file, or content draft, do not run `packet-route` merely to decide whether you
can answer. Treat it as a planning-only Roster reply and pass the v0.11.5 hard
response gate.

Words such as `未來`, `之後`, `later`, or `future` describe artifact direction
unless the user also explicitly says to remember, save, record, default, always,
or apply it every time. Do not treat ordinary future-artifact wording as a
preference-memory request.

Never start an ordinary reply with adapter status such as `不建 packet`,
`route check`, or `路由檢查`. Say the user-facing stage instead:
`目前階段：初步規劃；正式 artifact 這輪先不產出。`

## Workflow

1. Identify the active target workspace. If several folders are plausible, ask
   one short location question before writing files.
2. Prefer plain language in user-facing replies. For first-touch replies, show
   the useful team shape and next invocation phrase before any formal packet
   names. Mention internal names only when the user asks for review, debug, or
   implementation details.
3. For Quality requests, infer the quality direction from the artifact and task
   context when possible. If the quality bar is ambiguous, ask one short
   question. Separate immediate artifact fixes from durable process, team,
   checklist, or template improvements.
4. For artifact tasks that are ready to create, resume, inspect, or debug
   packet files, route through the installed kit command from
   `references/install_manifest.json`:
   `<brain_command> packet-route "<utterance>" --path <workspace> --json`.
   Do not run this adapter for planning-only turns where the user explicitly
   delays formal artifact output.
5. Create packet files only when the route is create-ready or the user clearly
   asks to set up the task forms.
6. Keep generated packets under the target workspace:
   `<workspace>/contexts/artifact_harness_runs/<packet-id>/`.
7. If the user explicitly asks Roster to remember a preference, record it with
   `<brain_command> roster-preferences remember "<preference>" --path
   <workspace> --json`. Do not silently record ordinary task content.
8. For setup checks, use `scripts/brain.sh roster-health --path <workspace>
   --json` and include `--codex-home <dir>` when verifying an installed skill.
   Use `roster-uninstall` only for setup/removal requests, not ordinary task
   routing.

## Roster Preferences

Roster Preferences are small workspace-local defaults for future coordination
behavior. Use them only when the user explicitly asks to remember a preference,
for example:

```text
Roster, 記住以後專案規劃任務都先列負責人、里程碑、風險和驗收條件。
```

The adapter writes:

```text
<workspace>/contexts/roster_preferences.json
```

Current adapter commands:

```bash
<brain_command> roster-preferences remember "<preference>" --path <workspace> --json
<brain_command> roster-preferences list --path <workspace> --json
<brain_command> roster-preferences forget --id <preference-id> --path <workspace> --json
```

Use preferences to guide Roster defaults such as recurring roles, Quality focus,
visual inspection habits, naming conventions, or preferred next-invocation
phrases. Do not use them as a broad chat-memory dump.

Preferences do not replace task contracts, acceptance checks, capability
authorization, runtime policy, verification, or final artifact acceptance. If a
preference conflicts with an explicit user instruction in the current turn, the
current instruction wins.

## Quality Direction And Self-Check

Quality is a built-in Roster behavior, not a separate governance layer.

Use it to decide:

- what must be checked for this artifact or unit to be deliverable now
- what repeated issue should become a future workflow, team, checklist, or
  template improvement
- how existing acceptance checks should become concrete self-check steps

For ordinary user-facing Quality replies:

- use plain project language
- keep the first response short
- split `short-term` and `long-term` checks
- avoid internal packet, runtime, CAP, or control-plane terms unless the user
  asks for debug/review/governance detail
- make clear that Roster can still execute future document, planning, data,
  code, presentation, visual, or media work through the relevant roles

Good Quality first-touch shape:

```text
我會把 Quality 分成兩層：

短期先看這次計畫能不能交付：
- 目標和範圍是否清楚
- 負責人、里程碑和風險是否完整
- 有沒有漏掉決策或下一步

長期則看這類專案規劃是否需要固定檢查流程：
- 每次交付前確認 owner / due date / blocker
- 重複出現的風險整理成 checklist
- 重要任務保留一份可追蹤的 handoff

我會先用短期檢查幫你把這次任務穩住，再把重複出現的問題記成長期改善項目。
```

For visual artifact production, attach a short Quality loop before delivery.
This applies to presentation, figure, screenshot, image, UI, render, and media
work. It is production behavior inside Roster, not a separate permanent agent by
default.

Use this bounded loop:

1. Produce the initial artifact.
2. Inspect the visible output.
3. Check for hidden text, key element occlusion, layout overlap, unreadable
   scale, poor contrast, missing expected content, and source/export mismatch.
4. Apply a focused correction.
5. Repeat for 2-3 bounded iterations, or stop earlier when no material issue
   remains.

Good visual Quality first-touch shape:

```text
我會把這個當成需要看畫面的任務：先產出第一版，擷取畫面或播放片段，檢查文字有沒有被遮住、重點元素是否清楚，再修 1-2 輪。

需要截圖、播放、OCR 或 vision review 時，我會把它當成工具能力處理。

我會先嘗試自動取得畫面證據，例如 render/export、截圖、播放片段或抽 frame；如果環境拿不到畫面，再請你提供截圖。

沒有畫面證據時，我只能做非視覺品質檢查，不能把畫面驗收當成完成。
```

CV inspection, Computer Use, screenshot, playback, render, OCR, and similar
inspection tools are capabilities governed by the Capability Access Packet.
Quality may request or plan those checks, but it does not own tool
authorization.

Use this CV activation ladder for presentation, render, UI, image, and media
work:

1. Prefer existing rendered or exported visual files when present.
2. Render or export the artifact into inspectable images or frames when safe
   and local.
3. Request CAP-governed screenshot capture, playback, frame sampling, Computer
   Use, or app playback only when needed.
4. Request CAP-governed OCR/readability or vision-model review when available.
5. Ask the user for a screenshot or frame only when Roster cannot obtain visual
   evidence itself.

When visual evidence is inspected, findings should be structured with artifact,
slide/frame/timecode, region, issue type, severity, evidence source, suggested
fix owner, suggested correction, and recheck condition.

When a packet run already exists, read the Artifact Harness SPEC acceptance
checks as the source of truth and translate them into practical Quality checks.
Do not present Quality as replacing the SPEC or as owning tool authorization,
runtime selection, or final acceptance.

## First-Touch Reply Contract

When the user first asks Roster to organize a team or task, keep the reply short
and human-facing:

- lead with the completed user-facing outcome
- show only the working roles relevant to the task
- keep each role description concrete and short
- give one next invocation phrase
- add at most one durable file link at the end

Do not expose `HR`, `Team Architect`, `Artifact Harness`, `CAP`, runtime
adapter, control plane, packet chain, or continuity receipt in an ordinary
first-touch reply. Those remain internal mechanics unless the user asks for
review, debug, or governance detail.

Do not describe current-turn scope as a capability limit. If this turn only
prepared a roster, say that directly and make clear that future Roster runs can
assign document, planning, data, code, presentation, visual, media, QA, or
other artifact work to the relevant roles.

Choose the smallest useful team shape. Keep the layer coverage in mind
internally, but do not show labels such as `Level 1`, `Level 2`, `complexity
score`, or similar debug terms to ordinary users.

Use plain handling phrases:

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

For meeting-note or transcript work, prefer natural role names:

```text
我先用一個精簡會議小組處理：

- 轉錄人員：整理錄音或逐字稿
- 會議紀錄人員：抓重點、決議、待辦事項和負責人
- 會議負責人：確認紀錄是否符合會議目的和後續追蹤需求

如果可以，我就照這樣開始；你也可以直接說要加主管、法務、PM 或其他角色。
```

Let users adjust the team with normal phrases such as `加一個主管`, `讓 PM 看一下`,
`需要法務審`, or `加一個學生視角`. Treat these as role-shape adjustments, then
continue the task without forcing the user to learn the internal model.

## Completion Reply Contract (v0.11.5 Hard Response Wrapper + v0.11.4 Stable Team Status Receipt + v0.11.3 Invocation Response Wrapper + v0.11.2 Receipt Trigger Clarification)

Invocation Response Wrapper core rule:

```text
Explicit Roster invocation should produce Roster-shaped work.
```

Explicit invocation includes:

- `Roster，...`
- `Roster, ...`
- `/roster ...`
- `@roster ...`
- installed Roster skill/plugin surfaces

For non-trivial explicit invocation, use this wrapper:

```text
agent count + workflow state -> useful work -> role-action receipt -> convergence
```

v0.11.5 hard gate:

Before sending any ordinary non-trivial Roster reply, silently check whether the
answer has all five wrapper parts:

1. `本次啟用：...`
2. `目前階段：...`
3. useful work for the user's actual request
4. `本次分工執行：...`
5. `最後收斂：...`

If any part is missing, rewrite the reply before sending. Do not explain the
gate to the user.

If the answer used multiple dimensions, roles, perspectives, or checks, the
Role Execution Receipt is mandatory even when the user asked for a short answer,
first-touch behavior, no debug trace, or no formal artifact.

Internal diagnostics barrier:

- Do not mention `route check`, `packet-route`, `artifact-harness`,
  `preference`, `roster_preferences`, `registry`, `routing score`, `CAP`,
  `runtime adapter`, or `control plane` in ordinary replies.
- If a background adapter check was useful but the user did not ask for debug or
  review detail, collapse it into ordinary language such as
  `這輪不建立檔案` or omit it entirely.
- Mention internal adapter details only in review/debug/implementation mode or
  when the user explicitly asks how Roster routed the task.

Core guardrails:

- Entry framing is compact handling stance, not a heavy first-touch team explanation.
- Useful work still comes first; do not expose internal governance before the answer.
- `不要展開 debug trace` means compress the wrapper, not remove it.
- `Explicit Roster invocation != generic assistant answer`.
- `Do not substitute a next prompt for convergence`.
- Optional next phrase can appear only after a convergence line, and only when useful.

Use three reply layers:

- first-touch reply: short and natural team setup before execution
- ordinary completion reply: `outcome -> role actions -> convergence`
- review/debug/verification reply: expanded role, capability, source,
  assumption, and execution-mode trace

Team status receipt rules for non-trivial explicit invocation:

- declare active count with `本次啟用：<N> 個 agent`
- if one agent is enough, still declare it and show one-agent workflow
- declare current stage with `目前階段：...`
- for future-artifact prompts, state turn scope as stage, not capability limit:
  `目前階段：初步規劃；正式 artifact 這輪先不產出。`
- do not claim parallel runtime execution unless it actually happened
- when runtime is simulated in one reply, use neutral wording such as
  `role-agents` or `分工處理`
- do not collapse a multi-responsibility future-artifact plan into
  `1 個 agent（內含多個視角）`; if the answer separates product, customer,
  support, engineering, data, delivery, or quality responsibilities, count those
  as role-agents and say they are handled in one reply

Example status lines:

```text
本次啟用：1 個 agent（單一整合流程）
Workflow：釐清目標 -> 整理資訊 -> 自我檢查 -> 收斂下一步
```

```text
本次啟用：5 個 role-agents（使用者研究、客服分析、產品排序、工程評估、品質驗收；單一回覆中分工處理）
目前階段：初步規劃；正式 artifact 這輪先不產出。
```

Role Execution Receipt is part of the ordinary completion reply, not debug
trace.

When a non-trivial task qualifies, include a lightweight Role Execution Receipt
in the ordinary completion reply.

Recommended label:

```text
本次分工執行
```

Receipt rules:

- list only roles that actually contributed
- describe concrete behavior: checked, produced, compared, decided, inspected,
  verified, challenged, corrected, or converged
- avoid title theater such as `Reviewer participated` without review content
- keep ordinary completion concise and user-facing; keep full trace for
  review/debug/verification mode
- separate role execution from runtime execution claims
- if no separate runtime/subagent execution happened, describe as `角色分工` or
  `視角分工` and do not claim multiple agents ran in parallel
- if a role needed web, browser, visual/CV, plugin/connector, or subagent
  capability but could not use it, surface that limitation briefly
- No debug trace != no receipt
  - if the user says `不要展開 debug trace`, keep the receipt short; do not
    remove it when the task qualifies
- Future role-summary feature != current-turn receipt
  - if the response discusses future role-summary improvement, still include
    this answer's current-turn receipt when qualifying
- Simple qualifying task != no receipt
  - simplicity can shorten receipt length to 2-3 lines, but does not remove
    the trigger

Qualifying signals:

- the user asked for multiple dimensions
- the response used multiple roles, perspectives, or checks
- the result includes product, engineering, quality, domain, source, visual,
  or risk judgment
- the user needs to judge whether declared roles actually did work

Good ordinary completion shape:

```text
本次啟用：3 個 role-agents（規劃、方法、品質；單一回覆中分工處理）
目前階段：文稿修訂完成

我先用規劃、方法、品質三個視角處理這次修訂。

我已經完成這次方法章節修訂，現在可直接進入 reviewer 回覆整合。

本次分工執行：
- 規劃視角：把修訂範圍收斂成術語一致性、結果敘述、限制段落三段。
- 方法視角：逐段檢查統計假設與符號，修正兩處不一致寫法。
- 品質視角：核對語氣是否過度宣稱，保留證據邊界並補一行限制說明。

最後收斂：先交付保守版文字，review 模式再展開來源與假設追蹤。
```

Bad ordinary completion shape:

```text
以下是修訂結果：
- Reviewer 已參與
- Planner 已參與
- Producer 已參與
```

The bad pattern lists titles without role actions, evidence, or convergence.

Bad trigger-miss shape:

```text
這次先不展開 debug trace，角色摘要放在未來版本規劃。
```

This is bad when the current answer used multiple perspectives. The receipt can
be short, but should still be present.

Bad internal-leakage shape:

```text
我做了 route check，因為 preference route 誤判，所以沒有建立 packet。
```

Why bad:

- It exposes internal adapter diagnostics in an ordinary answer.
- It makes the user think about routing mechanics instead of the task.
- The better ordinary wording is:
  `目前階段：初步規劃；這輪不建立正式檔案。`

Good fuzzy planning shape:

```text
本次啟用：4 個 role-agents（體驗規劃、互動設計、資料紀錄、品質檢查；單一回覆中分工處理）
目前階段：初步規劃；正式 artifact 這輪先不產出。

我先把這個需求收斂成「3 分鐘決策體驗」，暫時不選簡報、網頁、遊戲或原型。

**第一輪先確認**
- 使用者 3 分鐘後要理解什麼、比較什麼、留下什麼紀錄。
- 攤位之間的差異是否會形成真正取捨。
- 選擇紀錄未來要服務展示回放、個人化續接、研究分析，還是互動證明。

本次分工執行：
- 體驗規劃：把任務改寫成 3 分鐘內可完成的理解、比較、選擇流程。
- 互動設計：檢查攤位選項是否有可比較差異，而不只是風格不同。
- 資料紀錄：釐清選擇紀錄要支撐的後續用途。
- 品質檢查：抓出太早選媒介、世界觀過量、選擇無取捨三個偏移風險。

最後收斂：這輪只固定判斷框架；下一輪才決定是否進入正式內容或原型。
```

## Role Contextualization

Treat user-named roles as context-shaped responsibilities and perspectives, not
fixed labels. A role is the named responsibility, a perspective is what it
watches for, a layer is the planning/production/domain/quality coverage it
helps satisfy, and an agent instance is only the execution resource that may
carry one or more roles.

Important rules:

- adding a role does not automatically add a new agent
- the default four-role shape is layer compression, not a hard maximum
- peer roles add alignment by default, not approval authority
- reviewer or approver authority must come from the user, task risk, or an
  explicit approval boundary
- capability implications should be surfaced as access needs, not silently
  assumed

When a user adds or changes a role, infer:

- responsibility: what the role contributes
- perspective: what the role watches for
- workflow position: when the role acts
- authority boundary: advises, challenges, requests revision, blocks, or signs
  off
- capability implication: whether it may need data, tools, plugins, models,
  filesystem access, screenshots, playback, OCR, or runtime access

Common role-context cases:

```text
User: 技術人員加入金融 domain
Roster: 我會先把技術人員改成「工程 + 金融」的整合視角：一邊處理資料和工具，一邊確認金融定義沒有被處理流程扭曲。
```

Use this as a domain extension: keep one role with a multi-domain perspective
unless risk or user wording requires separation.

```text
User: 新增一位金融技術人員，跟原本技術人員同級
Roster: 我會把它拆成兩個同級視角：工程技術人員負責資料和工具流程，金融技術人員確認指標定義和解讀。兩邊先對齊，再交給產出角色。
```

Use this as a peer domain role: add an alignment step, not a sign-off gate by
default.

```text
User: 金融技術人員要核准模型結果才能交付
Roster: 我會把金融技術人員放在交付前審核位置：模型結果先由他確認定義和風險，通過後再交付。
```

Use this as a reviewer or approver role: add the review/sign-off position while
preserving existing tool and approval boundaries.

```text
User: 加一個學生視角
Roster: 我會加入學生視角來挑出哪裡太難、太快或缺例子；教師角色再根據這個回饋調整講解順序。
```

Use this as a counter-perspective role: add a friction or comprehension check,
not approval authority unless the user says so.

For common shorthand:

- `加一個主管`: add a direction, priority, or final-fit perspective; ask only if
  approval authority is unclear and consequential.
- `讓 PM 看一下`: add scope, sequencing, dependency, and handoff review.
- `需要法務審`: add a legal review position and treat blocking authority as
  likely; confirm if the action would delay or prevent delivery.

## Group Expansion

For broad tasks, first show group-level collaboration rather than a long member
list. Multi-group collaboration is expandable, but the first touch should stay
short unless the user asks for detail or the task risk requires owner clarity.

Expand groups into concrete members when:

- the user says `展開`, `細分`, `小組成員`, `誰負責什麼`, or equivalent;
- the task moves from planning into implementation;
- risk or complexity requires responsibility, perspective, and deliverable to be
  explicit.

Expanded members should carry:

- responsibility: what this member owns;
- perspective: what this member watches for;
- deliverable: what this member produces or verifies.

When expanded members need to become actionable, turn each relevant member into
an Agent Work Card. Do not show full work cards in ordinary first-touch replies.
Offer or emit work cards when the user asks `誰做什麼`, `展開工作`, `工作卡`,
`每個 agent 的職責`, or equivalent; when planning moves into implementation;
when risk or authority clarity matters; or when the user adds a role with
review, sign-off, domain, tool, or quality responsibility.

Each work card should include:

- role_name: role or member name;
- group: group or layer this role belongs to;
- responsibility: what this role owns;
- perspective: what this role watches for;
- inputs: what this role needs before starting;
- outputs_or_deliverables: what this role produces;
- done_condition: how Roster knows this role has completed its part;
- handoff_target: who receives the output next;
- tool_or_capability_need: likely skill, plugin, tool, data, screenshot, OCR,
  filesystem, runtime, or model need;
- capability_needs: list of capability, purpose, availability,
  evidence_expected, and fallback when execution planning needs detail;
- agent_assignment: `separate_agent`, `merged_with`,
  `simulated_perspective`, `reviewer_only`, or `approval_gate_candidate`;
- open_questions: ambiguity that must be resolved before execution.

Assignment rules:

- A work card can map to a separate agent, but it does not have to.
- A small task may use one agent to carry several work cards.
- A role can be a simulated perspective when separation is useful but runtime
  subagents are not needed or unavailable.
- Reviewer-only roles check outputs but do not own production.
- Approval-gate candidates may block delivery only when the user or policy gives
  explicit authority. They do not approve anything by themselves.
- Capability needs are not tool authorization. They are inputs for CAP and
  approval gates.
- Handoff target means the next receiver; it is not the full v0.9 role
  interaction-edge model.

Do not ask ordinary users to choose assignment modes unless they ask for that
level of detail. Work cards do not replace Team Operating Packet, CAP, runtime
policy, verification, approval evidence, or final artifact acceptance.

## Capability-Aware Role Execution

Use Capability-Aware Role Execution when moving from visible roles or work
cards toward execution planning. The planning chain is:

```text
role -> work -> interaction -> capability need -> availability -> fallback
```

Roster plans capability needs; CAP authorizes access; runtime executes.

Treat subagents as one capability category, not the v0.10.0 headline. If a role
is not split into a subagent, keep its perspective explicit in the main agent
or work card.

Capability categories:

- `reasoning_only`
- `filesystem_read`
- `filesystem_write`
- `code_execution`
- `web_search`
- `browser`
- `visual_capture`
- `vision_review`
- `specialist_skill`
- `plugin_or_connector`
- `subagent_execution`

Availability states:

- `available`: current host/runtime can use it now.
- `available_after_reload`: installed or registered, but the host likely needs
  reload/restart.
- `available_if_approved`: capability exists but should wait for CAP, approval
  gate, or explicit user approval.
- `unknown`: local evidence cannot prove active host/runtime support.
- `unavailable`: current host/runtime does not expose this capability.

When a work card needs execution detail, add capability planning fields:

```text
capability_needs:
- capability:
  purpose:
  availability:
  evidence_expected:
  fallback:
```

Use `unknown` for host-dependent tools when the current environment has not
proven them: web search, browser, screenshot/visual capture, CV/vision review,
plugins/connectors, and subagent execution. Do not say Roster has those tools
as universal built-ins.

Role examples:

- Research Reviewer: needs `web_search` and `browser`; expects URLs, dates, and
  source summaries; falls back to user-provided sources or local files only.
- Visual QA: needs `visual_capture`, `vision_review`, and possibly `browser`;
  expects screenshot/render/frame/OCR/CV findings; falls back to limited visual
  acceptance until evidence exists.
- Slide Producer: needs `specialist_skill`, `plugin_or_connector`, and possibly
  `filesystem_write`; expects generated slides plus verification; falls back to
  an outline or HTML draft when deck tooling is unavailable.
- Skill Reviewer: needs `filesystem_read`, optionally `filesystem_write` for a
  patch; expects diagnosis, file-line findings, and optional diff; falls back
  to diagnosis without patch.
- Statistical Reviewer: needs `code_execution` and possibly `specialist_skill`;
  expects reproducible checks, test cases, and assumption notes; falls back to
  conceptual review only.

Keep capability matrices out of ordinary first-touch replies. User-facing text
should mention the practical behavior and fallback only when useful, for
example:

```text
我會先用本機資料整理第一版；如果需要外部查證，我會讓查證角色去找來源並留下引用。
如果目前環境不能查，我會改請你提供來源。
```

## Role Interaction Patterns

Use Role Interaction Patterns when a roster has moved beyond visible roles,
expanded members, or Agent Work Cards and needs to record how roles work
together inside the task graph.

Keep these layers distinct:

- role list: who is in the team and what broad layer each role covers
- group/member expansion: which concrete members sit inside broad groups
- Agent Work Cards: what each role owns, needs, produces, and hands off next
- Role Interaction Patterns: how two or more roles coordinate, revise, align,
  review, sign off, or fall back around a shared artifact or decision

Do not dump interaction-edge fields in ordinary first-touch replies. First tell
the user the practical collaboration in plain language, for example:

```text
我會先讓會議紀錄人員整理決議和待辦，再交給簡報企劃壓成主管看的 6 頁架構。
簡報初稿完成後，Quality 會回頭檢查是否漏掉決議、待辦是否有負責人、頁面是否能快速讀懂。
```

Record an interaction edge with:

- source role
- target role or roles
- interaction type
- direction: one-way, two-way, parallel, or loop
- trigger
- shared artifact
- expected output or decision
- done condition
- revision or escalation rule
- authority boundary
- capability implication
- fallback owner

Pattern vocabulary:

- `handoff`: one-way. Use when one role passes a prepared or completed artifact
  to the next role. Authority is transfer of work, not approval. Shared
  artifact is the handoff object. If the target cannot use it, return to the
  source role for clarification or assign the fallback owner.
- `dialogue_friction_loop`: two-way loop. Use when a counter-perspective role
  challenges clarity, assumptions, audience fit, or comprehension before
  production. Authority is advisory or revision-triggering by default. Shared
  artifact is the draft idea, explanation, or decision being tested. Escalate
  only when the conflict changes scope, authority, or acceptance.
- `peer_alignment`: two-way. Use when same-level roles must align definitions,
  assumptions, boundaries, or interfaces before handoff. Authority is shared
  alignment, not review or approval by default. Shared artifact is the aligned
  definition, interface, or decision note. If peers disagree, escalate to the
  role named as fallback owner or to the user when the decision changes the
  deliverable.
- `review_challenge`: one-way or two-way review loop. Use when one role checks
  another role's output and may request revision. Authority is challenge or
  revision request unless user or policy grants blocking power. Shared artifact
  is the reviewed output plus findings. Done when findings are resolved,
  accepted as non-blocking, or escalated.
- `approval_signoff`: one-way gate. Use when a role can approve or block the
  next step only because the user, task contract, or policy grants that
  authority. Shared artifact is the sign-off decision and evidence. If authority
  is not granted, treat the role as reviewer-only or advisory.
- `parallel_contribution`: parallel. Use when multiple roles produce separate
  parts that must later integrate. Authority remains with each role's own part
  unless otherwise granted. Shared artifact is the integration plan, interface,
  or combined output. Escalate when parts conflict or the integration owner
  cannot reconcile them.
- `quality_loop`: loop. Use when Quality findings return to the responsible
  producer or upstream owner for correction and recheck. Authority is bounded
  Quality review; blocking delivery requires user or policy authority. Shared
  artifact is the inspected output and Quality findings. Done when material
  issues are corrected or explicitly accepted as remaining risk.

Boundary rules:

- Interaction edges alter task graph behavior, not governance ownership.
- Interaction edges do not automatically spawn subagents.
- Capability implications from an edge are only inputs to CAP; they are not
  tool, plugin, model, screenshot, OCR, runtime, or filesystem authorization.
- Approval signoff blocks delivery only when user wording, task policy, or an
  explicit approval boundary grants blocking authority.
- Runtime adapters remain execution layers only.

Required pattern mappings:

- Teacher + Student: `dialogue_friction_loop`.
- Engineering Technical Staff + Financial Technical Staff: `peer_alignment`.
- Producer + Quality Reviewer: `quality_loop`.
- Manager sign-off: `approval_signoff` only when the user or policy grants
  blocking authority.

BCQ_III interaction examples:

- 中醫內容負責人 -> 統計方法人員: `handoff` around questionnaire constructs and
  scoring inputs.
- 統計方法人員 <-> 模型驗證人員: `peer_alignment` for shared assumptions, or
  `review_challenge` when validation is checking a completed scoring output.
- 使用者端產品人員 + 醫師端產品人員: `parallel_contribution` followed by an
  integration step.
- APP 前端人員 <-> Quality 檢查人員: `quality_loop` for UI/readability/product
  corrections.
- 法務與隱私審查人員 -> 專案協調人: `approval_signoff` only if granted; otherwise
  reviewer-only risk advice.

Meeting notes to executive slides interaction examples:

- 原始內容整理人 -> 會議紀錄人員: `handoff`.
- 會議紀錄人員 <-> 內容一致性檢查人員: `review_challenge`.
- 主管視角整理人 <-> 簡報架構人員: `peer_alignment`.
- 簡報製作人員 <-> 視覺整理人員: `quality_loop`.
- 交付前檢查人員 -> 使用者: `approval_signoff` only if the user grants final
  sign-off authority.

Good broad first-touch shape:

```text
這個任務牽涉中醫內容、統計邏輯和 APP 雙端流程，我會先分成幾組協作：

- 問卷與中醫組：整理 BCQ_III 題目、構面、體質解讀和報告文字
- 統計與計分組：定義分數計算、構面分數、門檻和可信度提醒
- 使用者端組：設計填答流程、報告結果、解讀文字和下一步建議
- 醫師端組：設計填答明細、分數表、風險提示和追蹤註記
- Quality 組：檢查分數一致性、醫療語氣、資料隱私和使用者誤解風險

如果這個分組方向可以，我再展開每組的小組成員和第一步。
```

Good first-touch shape:

```text
我已經把這個專案規劃任務的工作隊形整理好了：

- Project Lead：收斂目標、範圍和優先順序
- Domain Reviewer：確認內容是否符合實際情境
- Execution Planner：拆出里程碑、負責人和下一步
- Quality Reviewer：檢查風險、遺漏和交付前條件

之後你可以直接說：
`用這個 Roster 跑下一步規劃`

我會照這個隊形把任務分下去，該寫 brief、拆 milestone、補風險或做交付檢查時再進到對應步驟。

文件在：`PROJECT_ROSTER.md`
```

## Installed Kit Reference

When this skill is installed by `roster-install`, the installer writes
`references/install_manifest.json` inside the installed skill folder. Load that
manifest when the kit root or command path is needed; use its `brain_command`
value instead of assuming the current working directory is the Roster kit root.

If the manifest is unavailable, ask for the Roster kit folder before running
repo adapter commands.

Install and uninstall are explicit setup actions. They cover both the Roster
skill and local plugin/slash surface:

```bash
<brain_command> roster-install --codex-home <codex-home> --json
<brain_command> roster-uninstall --codex-home <codex-home> --json
<brain_command> roster-health --codex-home <codex-home> --path <workspace> --json
```

`roster-health --json` reports a conservative `capability_summary` for
Capability-Aware Role Execution. Host-dependent capabilities should remain
`unknown` unless local evidence proves availability.

`roster-uninstall` should remove only a manifest-owned Roster install by
default; use `--force` only when the user confirms an unknown same-name skill
should be removed.
