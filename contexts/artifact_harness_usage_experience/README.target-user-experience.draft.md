# Roster

`Roster` is a local Codex-native staffing-and-project-planning surface.

It helps Codex turn artifact-producing work into a clear task brief, role plan,
tool-access boundary, execution map, and review checklist inside the same
workspace folder.

It does not require a persistent server, daemon, database, or separate
orchestration UI. You use it from ordinary Codex CLI or Codex GUI sessions.

## Start Here

Current primary invocation:

```text
Roster, 幫我把這些會議筆記整理成可執行的專案計畫。
```

In the stable path, type `Roster` in ordinary Codex chat and then say the task
in natural language. After `roster-install` and a Codex reload, users should
also be able to try `@roster <task>` and `/roster <task>` through the local
plugin/slash registration surface.

Specialized aliases may also work in ordinary chat, but they are secondary and
should not appear on the first screen unless the user asks for review, staffing,
debug, or implementation details.

Other examples:

```text
Roster, organize the working team for this artifact.
```

```text
Roster, organize the task boundary and handoff for this artifact.
```

```text
Roster, 這個任務現在卡在哪裡？
```

## First-Touch Response

For the first response to a team or task setup request, Codex should keep the
reply short and useful:

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

Do not put internal control-plane roles, packet names, runtime details, or
continuity receipts in this first response. Keep those in generated files,
review/debug replies, or later explanations when the user asks.

If this turn only prepared a roster, say that as current-turn scope. Do not make
it sound like Roster cannot later assign and execute document, planning, data,
code, presentation, visual, media, or QA work.

Roster should choose the smallest useful team shape. It may internally estimate
how much coordination is needed, but the user-facing response should not expose
debug labels such as `Level 1`, `Level 2`, or `complexity score`.

Use plain handling phrases:

```text
這個任務我會直接處理並自檢。
我會先整理出第一版，再檢查是否漏掉重點。
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

For meeting notes or transcript work, the first team should use ordinary role
names:

```text
我先用一個精簡會議小組處理：

- 轉錄人員：整理錄音或逐字稿
- 會議紀錄人員：抓重點、決議、待辦事項和負責人
- 會議負責人：確認紀錄是否符合會議目的和後續追蹤需求

如果可以，我就照這樣開始；你也可以直接說要加主管、法務、PM 或其他角色。
```

The user can add roles by status, domain, or review perspective, for example
`加一個主管`, `讓 PM 看一下`, `需要法務審`, or `加一個學生視角`. Roster should
fold the role into the team and continue the task without exposing the internal
coordination model.

Role additions should be interpreted in context:

```text
Roster, 技術人員加入金融 domain。
```

Response shape:

```text
我會先把技術人員改成「工程 + 金融」的整合視角：一邊處理資料和工具，一邊確認金融定義沒有被處理流程扭曲。
```

```text
Roster, 新增一位金融技術人員，跟原本技術人員同級。
```

Response shape:

```text
我會把它拆成兩個同級視角：工程技術人員負責資料和工具流程，金融技術人員確認指標定義和解讀。兩邊先對齊，再交給產出角色。
```

```text
Roster, 金融技術人員要核准模型結果才能交付。
```

Response shape:

```text
我會把金融技術人員放在交付前審核位置：模型結果先由他確認定義和風險，通過後再交付。
```

```text
Roster, 加一個學生視角。
```

Response shape:

```text
我會加入學生視角來挑出哪裡太難、太快或缺例子；教師角色再根據這個回饋調整講解順序。
```

Adding a role does not automatically mean adding a new agent. The default
four-role shape is a compact layer model, not a maximum team size.

For Quality setup requests, Codex should answer as a project coordinator first,
not as a governance explainer:

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

The short-term layer stabilizes the current artifact or unit. The long-term
layer captures repeated problems as team, process, checklist, or template
improvements. If an acceptance contract already exists, use it as the source of
truth for the checks without showing internal packet terminology in the first
reply.

For visual artifact production, Codex should quietly add a short Quality loop
before delivery:

```text
我會把這個當成需要看畫面的任務：先產出第一版，擷取畫面或播放片段，檢查文字有沒有被遮住、重點元素是否清楚，再修 1-2 輪。

需要截圖、播放、OCR 或 vision review 時，我會把它當成工具能力處理。

我會先嘗試自動取得畫面證據，例如 render/export、截圖、播放片段或抽 frame；如果環境拿不到畫面，再請你提供截圖。

沒有畫面證據時，我只能做非視覺品質檢查，不能把畫面驗收當成完成。
```

The loop applies to presentations, figures, screenshots, images, UIs, rendered
outputs, and media artifacts. It should inspect visible output for text occlusion, key
element occlusion, layout overlap, poor contrast or unreadable scale, missing
expected content, and source/export mismatch. Use 2-3 bounded iterations,
or stop earlier when no material issue remains.

CV inspection, playback, screenshot, OCR, render, Computer Use, and similar
inspection tools remain tool capabilities governed by the Capability Access
Packet. Quality may plan the check, but it does not own tool authorization. The
activation order is: use existing rendered/exported visual files, render/export
inspectable evidence when safe, use CAP-governed capture/playback/frame
sampling, use CAP-governed OCR or vision review, and ask the user for a
screenshot or frame only as the final fallback.

Visual acceptance requires inspected visual evidence when the artifact has a
visual output. Without a screenshot, render, frame, or playback evidence,
Roster can complete only non-visual, text, or structure checks. Visual findings
should include artifact, slide/frame/timecode, region, issue type, severity,
evidence source, suggested fix owner, suggested correction, and recheck
condition.

Codex should answer in plain language first for broader setup tasks too:

```text
I set up the task brief, role plan, tool-access note, and review checklist.
The files are in your workspace under contexts/artifact_harness_runs/...
```

You should not need to remember or type `brain.sh`, `packet-route`, or
`artifact-harness` during ordinary work. Those commands are internal adapters
for Codex, reviewers, and debugging.

## Workspace And Output

The active Codex workspace is the default output root.

Generated packet files are written under the workspace where the artifact work
is happening, not under the `Roster` kit repo by default:

```text
<active-workspace>/contexts/artifact_harness_runs/<packet-id>/
<active-workspace>/contexts/artifact_harness_registry.json
```

If Codex cannot tell which workspace should receive the files, it should ask one
short location question before writing anything.

## When To Use It

Use `Roster` when a task has enough moving parts that Codex should make the
working boundary explicit before acting:

- a project plan, document, dataset, code change, review packet, or research
  artifact must be produced or revised
- several roles or review perspectives are useful
- tool, plugin, LLM, filesystem, network, or runtime access needs to be clear
- the task may need to be resumed later
- a reviewer should be able to inspect why Codex acted the way it did

The kit creates agent-readable packet files in your target workspace. These
files are not bureaucracy for the user; they are the audit trail Codex and future
reviewers can use.

## What Codex Creates

For non-trivial artifact work, Codex creates a packet run in the target
workspace:

```text
<workspace>/contexts/artifact_harness_runs/<packet-id>/
<workspace>/contexts/artifact_harness_registry.json
```

The usual packet chain is:

```text
user mission
-> task brief
-> staffing / role plan
-> collaboration plan
-> tool-access and approval boundary
-> optional runtime map
-> verification / review checklist
```

Formal packet names:

- Artifact Harness SPEC: rules, contract, acceptance, and boundaries
- HR staffing packet: staffing and role design only
- Team Operating Packet: collaboration pattern, task graph, shared artifacts,
  and convergence plan
- Capability Access Packet: skills, plugins, tools, approval gates, and runtime
  allowlist
- runtime mapping: optional execution wiring for an adapter

Codex should explain the human outcome first and link these formal files after
that.

## When It Should Stay Lightweight

Not every request needs the full packet chain.

Codex should stay lightweight when the task is just:

- a quick question
- a small single-file edit
- a staffing check
- a short note
- a one-step verification

In those cases, Codex should answer or act directly and only create packet files
if the task grows into artifact production, tool authorization, review evidence,
or resumable work.

## Resume

You should be able to resume with ordinary language:

```text
這個任務現在卡在哪裡？
```

Codex should inspect the current workspace, registry, and recent packet runs. If
there is one likely active run, Codex should summarize:

- current status
- blocker, if any
- next action
- relevant file links

If several runs are possible, Codex should ask one short disambiguation question
using human-readable mission titles, not internal ids first.

## Permissions And Tool Access

The kit makes tool access visible without making the user read governance files
first.

Codex should summarize access in plain language:

```text
No external tools needed.
```

```text
Needs filesystem writes only.
```

```text
Needs LLM/provider access; no external runtime.
```

```text
Needs approval before network/plugin/runtime execution.
```

The formal allowlist and approval gates live in the Capability Access Packet.
Runtime adapters remain execution layers only; they do not own governance.

## Install On Another Machine

`install` does not mean starting a server. It means registering the Codex-native
invocation surface and verifying that the packet engine and LLM path work on the
new machine.

On a new machine:

1. Clone or copy the Roster kit.
2. Open Codex in the kit folder.
3. Install the repo-owned `roster` skill from the kit root:

```bash
./scripts/brain.sh roster-install --codex-home ~/.codex --json
```

4. Run the current verified health check from the kit root:

```bash
./scripts/brain.sh roster-health --codex-home ~/.codex --path <workspace-folder> --json
```

5. If the work needs an external provider, name it explicitly:

```bash
./scripts/brain.sh roster-health --codex-home ~/.codex --path <workspace-folder> --provider openai --auth-env OPENAI_API_KEY --json
```

6. Confirm the invocation status. Current mechanism: installed `roster` skill,
   local `roster` plugin, `/roster` command, and `Roster` as the stable
   natural-language fallback.
7. Restart or reload Codex so plugin and slash-command state refreshes.
8. Configure local LLM credentials or Codex auth for the provider you intend to
   use.
9. Try the installed health-check prompt:

```text
@roster run health check for this workspace.
```

10. Confirm that the health check reports skill/plugin install visibility, packet output,
   and LLM/provider status.

Current status: the repo-native health check verifies local registration files
and config state. Final composer visibility for `@roster` and `/roster` is
verified by reloading Codex and trying the installed surfaces.
`roster-health` creates a smoke packet under the target workspace and cleans it
up by default. Use `--keep-artifacts` only when a reviewer needs the smoke
packet files retained as evidence. Provider credential values are never printed;
a present credential environment variable verifies local provider wiring, not a
remote model-call transcript.

The health check should confirm:

- Codex can see or invoke the coordination surface
- packet files can be written under the target workspace
- the expected LLM/provider path is locally configured, or reports a structured
  missing-provider / missing-auth diagnostic
- missing credentials fail with a clear missing-auth or missing-provider message
- no persistent server, daemon, database, or hidden control plane was added

Repo-portable artifacts:

- expected file layout
- `scripts/brain.sh`
- `scripts/system_hub.py`
- `policy/system_hub.toml`
- `contexts/team_alias_registry.json`
- templates and policy docs
- future skill/plugin/slash registration metadata, if verified
- LLM provider requirements and environment variable names
- health-check steps

Machine-local state should not be committed:

- Codex auth/session state
- API keys and provider credentials
- personal accumulated memory
- local model caches
- machine-local overlays that have not been artifactized

## For Reviewers And Debugging

The command-line adapter remains available for evidence and reproducibility.
These commands are not the basic user workflow.

Run these from the `Roster` kit root, or use the absolute path to the
installed kit script in generated diagnostics.

Representative checks from the kit root:

```bash
./scripts/brain.sh roster-health --path <workspace> --json
./scripts/brain.sh roster-health --path <workspace> --json --keep-artifacts
./scripts/brain.sh packet-route "<utterance>" --path <workspace> --json
./scripts/brain.sh artifact-harness "<mission>" --path <workspace> --json
./scripts/brain.sh artifact-harness resume --path <workspace> --id <packet-id> --json
./scripts/brain.sh artifact-harness runtime-check --path <workspace> --id <packet-id> --json
./scripts/brain.sh artifact-harness repair-plan --path <workspace> --id <packet-id> --json
```

Reviewer expectations:

- packet output stays in the target workspace
- reruns do not overwrite filled packets unless overwrite is explicit
- smoke tests use temporary workspaces or clean up test packet runs
- JSON mode returns structured success and refusal payloads
- CAP remains the source for tool allowlists and approval gates

## Ownership Boundaries

Keep the layers separate:

- Artifact Harness owns task rules, contract, acceptance, and boundary.
- HR owns staffing and role design only.
- Team Architect owns collaboration pattern, shared artifacts, task graph,
  convergence, and CAP generation.
- Capability Access Packet owns skill, plugin, tool authorization, approval
  gates, and runtime allowlist.
- Runtime adapters execute; they do not become governance owners.

## What This Is Not

`Roster` is not:

- a persistent server
- a separate orchestration UI
- a database-backed control plane
- a replacement for Codex CLI or GUI
- a place to hide approvals
- a generic scratchpad for unrelated experiments

It is a staffing-and-coordination surface: small enough to use inside normal Codex work, explicit
enough that a future Codex run or human reviewer can understand what happened.

## Current Implementation Note

Until the final invocation and install layers are verified, treat this README as
the target experience. The current repo may still expose shell commands more
prominently than the final user experience should.
