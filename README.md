# Roster

Roster helps Codex organize artifact work into a working team, a short quality
loop, and clear tool boundaries.

Use it when a task is more than a one-shot answer: project plans, meeting notes,
documents, datasets, code changes, reviews, or any artifact that benefits from
roles, checks, and handoff continuity.

Roster is Codex-native. It does not require a persistent server, daemon,
database, or separate orchestration UI. It writes task packets into the same
workspace where the work happens.

## Install

Clone the kit and install the local `roster` skill plus local plugin surface
into your Codex home:

```bash
git clone https://github.com/tomlin01/roster.git
cd roster
./scripts/brain.sh roster-install --codex-home ~/.codex --json
```

Restart or reload Codex after install so plugin and slash-command state can be
refreshed.

Check that Roster can see a target workspace and write/clean a smoke packet
there:

```bash
./scripts/brain.sh roster-health --codex-home ~/.codex --path <workspace-folder> --json
```

If your workflow needs provider-backed LLM or vision/CV checks, configure local
Codex auth or a provider environment variable, then include it in health:

```bash
./scripts/brain.sh roster-health --codex-home ~/.codex --path <workspace-folder> --provider openai --auth-env OPENAI_API_KEY --json
```

`roster-health` checks local setup only. It does not print secrets and does not
make a remote model call. Its JSON output includes a conservative
`capability_summary`; host-dependent capabilities such as web search, browser,
visual capture, vision review, plugins/connectors, and subagents stay
`unknown` unless local evidence proves otherwise.

## Use

Open Codex in the project workspace and say:

```text
Roster, help me turn these meeting notes into a project plan.
```

or:

```text
Roster, 幫我把這些會議筆記整理成可執行的專案計畫。
```

Roster should answer in plain project language: what team shape it will use,
what quality checks matter, and what the next useful phrase is. You should not
need to say internal workflow names during normal use.

Current truthful invocation:

```text
Roster, <your task>
```

Installed invocation targets after `roster-install` and a Codex reload:

```text
@roster <your task>
/roster <your task>
```

If the current Codex UI does not surface the plugin immediately, use the stable
fallback `Roster, <your task>` and run `roster-health --codex-home ~/.codex` to
inspect the local registration state.

### First Reply

Roster should not make you learn its internal workflow on the first turn. It
should choose the smallest useful team shape and explain it in plain language.

For a simple task:

```text
這個任務我會直接處理並自檢。
我會先整理出第一版，再檢查是否漏掉重點。
```

For meeting notes:

```text
我先用一個精簡會議小組處理：

- 轉錄人員：整理錄音或逐字稿
- 會議紀錄人員：抓重點、決議、待辦事項和負責人
- 會議負責人：確認紀錄是否符合會議目的和後續追蹤需求

如果可以，我就照這樣開始；你也可以直接說要加主管、法務、PM 或其他角色。
```

For a broader project:

```text
這個任務牽涉幾個面向，我會先分成幾組協作：

- 內容組：整理主軸和交付物
- 技術組：處理資料、工具或轉換流程
- 審核組：檢查正確性、風險和品質

如果這個分組方向可以，我就展開每組的角色和第一步。
```

For ambiguous ownership or risk:

```text
這個任務的目標、權責或風險還需要先對齊。
我先幫你定隊形：先確認交付物、誰能決定方向、哪些地方需要審核。
確認後我再把它轉成工作小組和任務圖。
```

You can adjust the team in normal language: `加一個主管`, `讓 PM 看一下`,
`需要法務審`, or `加一個學生視角`.

### Adjusting Roles

Roster treats roles as responsibilities and viewpoints, not fixed job labels.
Adding a role does not automatically mean adding a new agent.

Examples:

```text
Roster, 技術人員加入金融 domain。
```

Roster should treat this as one integrated technical role unless the work is
risky enough to separate the domains.

```text
Roster, 新增一位金融技術人員，跟原本技術人員同級。
```

Roster should add a peer role and an alignment step, not a sign-off gate by
default.

```text
Roster, 金融技術人員要核准模型結果才能交付。
```

Roster should place that role before delivery as a reviewer or approver.

```text
Roster, 加一個學生視角。
```

Roster should add a counter-perspective that checks clarity, pacing, examples,
and audience fit.

The default four-role shape is a compact layer model, not a maximum team size.
Small tasks can merge layers into one pass; larger tasks can split one layer
into several domain or review perspectives.

### Expanding Groups

For broad tasks, Roster should show groups first and keep the first response
short. If you ask to `展開`, `細分`, or show `小組成員`, Roster should expand
each group into members with responsibility, perspective, and deliverable.
中文使用時，展開後應該能看出每個成員的責任、觀點和交付物。

Expansion does not mean every member becomes a separate agent. It is a planning
view first; execution may still stay compact when that is enough.

Example:

```text
Roster, 用 BCQ_III 做一個問卷 APP，使用者端看報告，醫師端看分數和填答明細。
```

Roster should first show groups such as 問卷與中醫組, 統計與計分組, 使用者端組,
醫師端組, and Quality 組. If you then ask it to expand, it should list the
members under each group and what they produce or verify.

### Work Cards

When you ask who does what, ask to expand the work, or move into implementation
planning, Roster can turn expanded members into Agent Work Cards.

A work card states what the role owns, what it needs, what it produces, how its
part is done, who receives the handoff, what capability it may need, and whether
the role should be a separate agent, merged role, simulated perspective,
reviewer-only role, or approval-gate candidate.

Work cards do not automatically spawn separate agents. Capability needs are not
tool authorization, and approval-gate candidates do not approve delivery unless
the user or policy gives them that authority. A handoff target is only the next
receiver; the deeper planning layer records how roles actually work together.

Short version:

```text
統計方法人員會交付「計分規格」：把每題如何轉成構面分數、門檻和解讀寫清楚。完成條件是使用者端和醫師端看到的是同一套可追蹤分數。小任務可和分數驗證合併；高風險時再拆成獨立 agent。
```

### How Roles Work Together

For complex rosters, Roster can also record how roles coordinate after their
work cards exist. The public reply should stay plain:

```text
我會讓會議紀錄先交給簡報企劃，再由 Quality 回頭檢查是否漏掉決議。
```

Internally, the plan can distinguish handoffs, peer alignment, productive
friction, review challenges, parallel contributions, Quality loops, and
sign-off checks. These interactions do not grant tool access, do not spawn
agents by themselves, and do not make a sign-off blocking unless the user or
policy gives that role blocking authority.

### Capability-Aware Role Execution

Roster v0.10.0 plans how each role can actually do its work:

```text
role -> work -> interaction -> capability need -> availability -> fallback
```

Roster plans capability needs; CAP authorizes access; runtime executes.

This is broader than subagents. A role may need ordinary reasoning, filesystem
read/write, code execution, web search, browser inspection, visual capture,
vision review, a specialist skill, a plugin/connector, or a separate subagent.
Roster should identify the need and fallback, but it must not claim that every
host has those capabilities.

Detailed work cards can carry capability planning fields:

```text
capability_needs:
- capability: web_search
  purpose: verify current public claims
  availability: unknown
  evidence_expected: URLs, dates, short source summaries
  fallback: ask the user for sources or use local files only
```

Availability states are `available`, `available_after_reload`,
`available_if_approved`, `unknown`, and `unavailable`. Use `unknown` when local
evidence cannot prove the active host exposes the capability.

### Completion Reply (v0.11.5 Hard Response Wrapper + v0.11.4 Stable Team Status Receipt + v0.11.3 Invocation Response Wrapper + v0.11.2 Receipt Trigger Clarification)

Invocation Response Wrapper:

```text
Explicit Roster invocation should produce Roster-shaped work.
```

For non-trivial explicit invocation (`Roster，...`, `Roster, ...`, `/roster ...`,
`@roster ...`, or installed Roster surfaces), use:

```text
agent count + workflow state -> useful work -> role-action receipt -> convergence
```

Before sending an ordinary non-trivial Roster reply, Codex should silently
verify that the reply includes:

- `本次啟用：...`
- `目前階段：...`
- useful work
- `本次分工執行：...`
- `最後收斂：...`

If any part is missing, the answer should be rewritten before sending. The user
should not see this internal check.

Ordinary replies must not leak adapter diagnostics such as `route check`,
`packet-route`, `artifact-harness`, `preference`, `registry`, `CAP`, runtime
adapter, or control-plane wording. Those belong in review/debug/implementation
mode. For ordinary users, collapse the same fact into scope wording such as
`這輪不建立正式檔案`.

Planning-only turns should not run routing just to decide whether Roster can
answer. If the user says the formal artifact, PRD, review, file, or content
draft should not be produced this turn, answer with the wrapper first. Treat
`未來`, `之後`, `later`, and `future` as artifact-direction words unless the
user explicitly says to remember, save, record, set a default, always apply it,
or do it every time.

Key constraints:

- entry framing should stay compact; it is not a heavy first-touch explanation
- useful work still comes first, not internal governance mechanics
- `不要展開 debug trace` keeps wrapper/receipt short, not absent
- `Explicit Roster invocation != generic assistant answer`
- `Do not substitute a next prompt for convergence`
- optional next phrase appears only after a convergence line, and only when useful

After a non-trivial task is completed, Roster should keep first-touch minimal
but make later completion replies auditable in a compact way:

```text
outcome -> role actions -> convergence
```

Team status receipt rules:

- declare active count with `本次啟用：<N> 個 agent`
- one-agent tasks still declare one-agent workflow
- declare current stage with `目前階段：...`
- for future-artifact prompts where the user delays formal output, state turn
  scope as stage:
  `目前階段：初步規劃；正式 artifact 這輪先不產出。`
- do not claim parallel runtime execution unless actual subagents were run
- if a future-artifact planning answer separates product, customer/support,
  engineering, data/delivery, or quality responsibilities, count them as
  role-agents rather than hiding them inside `1 個 agent`

Good status examples:

```text
本次啟用：1 個 agent（單一整合流程）
Workflow：釐清目標 -> 整理資訊 -> 自我檢查 -> 收斂下一步
```

```text
本次啟用：5 個 role-agents（使用者研究、客服分析、產品排序、工程評估、品質驗收；單一回覆中分工處理）
目前階段：初步規劃；正式 artifact 這輪先不產出。
```

Ordinary completion replies should include a lightweight Role Execution Receipt:

```text
本次分工執行
```

Receipt behavior:

- Role Execution Receipt is part of the ordinary completion reply, not debug
  trace
- list only roles/perspectives that actually contributed
- state concrete actions each role performed
- avoid role-title-only theater
- distinguish role/perspective execution from real runtime/subagent execution
- if no separate runtime agent was spawned, use `角色分工` or `視角分工`
- if required capability was unavailable, note the limitation briefly
- keep full capability/source/assumption trace in review/debug/verification
  replies, not ordinary completion
- No debug trace != no receipt
  - if the user says `不要展開 debug trace`, keep the receipt short for a
    qualifying task instead of removing it
- Future role-summary feature != current-turn receipt
  - future feature planning does not replace this answer's current-turn receipt
- Simple qualifying task != no receipt
  - simplicity affects receipt length, not the trigger

Qualifying signals:

- the user asks for multiple dimensions
- the response uses multiple roles, perspectives, or checks
- the result includes product, engineering, quality, domain, source, visual,
  or risk judgment
- the user needs to judge whether declared roles actually did work

Example:

```text
本次啟用：3 個 role-agents（規劃、技術、品質；單一回覆中分工處理）
目前階段：規劃收斂

我先用規劃、技術、品質三個視角收斂這次規劃。

我已經把這次規劃收斂成可直接執行的三步。

本次分工執行：
- 規劃視角：收斂範圍與交付順序，先固定本版邊界。
- 技術視角：核對可用命令與文件位置，避免超出既有介面。
- 品質視角：檢查是否有過度承諾，刪除沒有證據的執行宣告。

最後收斂：先交付文件更新，執行層留待後續版本。
```

Trigger-clarification example (two-week plan prompt):

```text
本次啟用：4 個 role-agents（使用者痛點、工程可行性、產品排序、品質驗收）
目前階段：初步規劃

我先用使用者痛點、工程可行性、產品排序、品質驗收四個視角收斂這段回饋。

我已經把使用者回饋收斂成 2 週內可執行的改善方案。

本次分工執行：
- 使用者痛點視角：整理高頻卡點並轉成可驗收需求。
- 工程可行性視角：限定兩週內可落地改動，排除高風險重構。
- 產品排序視角：把直接影響第一次成功的項目排在前面。
- 品質驗收視角：補上完成條件，保留必要限制說明。

最後收斂：先做入口指引與驗收一致性，後續再擴功能。
```

Bad trigger-miss example:

```text
以下是 2 週方案，角色摘要放到未來功能再做。
```

Bad internal-leakage example:

```text
我做了 route check，因為 preference route 誤判，所以沒有建立 packet。
```

## What Roster Does

For a non-trivial artifact task, Roster helps Codex:

- clarify the task and output boundary
- choose a working team or review perspectives
- decide what quality checks apply now
- keep tool and provider access explicit
- write resumable task packets under the target workspace
- preserve enough context for future Codex sessions or reviewers

Packet output stays with the work:

```text
<workspace>/contexts/artifact_harness_runs/<packet-id>/
<workspace>/contexts/artifact_harness_registry.json
```

If Codex cannot tell which workspace should receive files, it should ask one
short location question before writing.

## Quality

Quality is built into Roster as a short self-check loop.

For text and planning work, Roster should check whether the current artifact is
clear, internally consistent, and ready to hand off.

For visual work, such as presentations, screenshots, figures, UI, or rendered
outputs, Roster should try to inspect actual visual evidence before calling the
output done. A typical loop is:

1. produce the first version
2. inspect a screenshot, render, frame, or playback segment
3. catch text occlusion, key element overlap, poor readability, missing
   content, or source/export mismatch
4. make a focused correction
5. repeat for 2-3 bounded iterations, or stop earlier when no material issue
   remains

When Roster cannot obtain visual evidence itself, it should say that visual
quality is limited and ask for a screenshot or frame as the fallback.

## Preferences

Roster can keep a tiny workspace-local preference file for explicit future
coordination preferences:

```text
Roster, 記住以後專案規劃任務都先列負責人、里程碑、風險和驗收條件。
```

The adapter writes:

```text
<workspace>/contexts/roster_preferences.json
```

This is not general chat memory. Use it for recurring Roster preferences such
as team shape, quality focus, visual inspection habits, naming conventions, or
preferred coordination wording.

## Uninstall

Remove the installed skill and local plugin surface from a Codex home:

```bash
./scripts/brain.sh roster-uninstall --codex-home ~/.codex --json
```

By default, uninstall only removes a Roster skill installed by this kit. If a
different same-name skill exists, it refuses unless `--force` is explicit.

## Debug Commands

These commands are for setup, reviewers, and debugging. They are not the normal
chat path.

```bash
./scripts/brain.sh packet-route "<utterance>" --path <workspace-folder> --json
./scripts/brain.sh packet-route "<utterance>" --path <workspace-folder> --create --json
./scripts/brain.sh artifact-harness "<mission>" --path <workspace-folder> --json
./scripts/brain.sh roster-preferences list --path <workspace-folder> --json
```

For deeper internal architecture, packet lifecycle, runtime checks, and policy
references, see [docs/DEVELOPER_REFERENCE.md](./docs/DEVELOPER_REFERENCE.md).

## Credits And Third-Party References

Roster includes local reference notes and adaptation history informed by
[msitarzewski/agency-agents](https://github.com/msitarzewski/agency-agents),
an MIT-licensed AI agent role library.

The vendored snapshot under
[`references/third_party/agency-agents/`](./references/third_party/agency-agents/)
is kept as read-only reference material. It is not installed by
`roster-install`, and it is not the active Roster runtime.

Roster's active roles, quality behavior, packet workflow, and installation
surface are local adaptations under this repository's own workflow boundaries.

See [THIRD_PARTY_NOTICES.md](./THIRD_PARTY_NOTICES.md) for provenance and
license details.
