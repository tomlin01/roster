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
Roster, 幫我把這個 slide 任務安排好。
```

In the current verified path, type `Roster` in ordinary Codex chat and then say
the task in natural language. `@roster` has been tested and is not currently a
working installed Codex mention, skill, plugin, app mention, or slash command.
Keep `@roster` as a future install target only until a real registration layer
proves it.

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
我已經把 Lecture1 的工作隊形整理好了：

- Student：看懂不懂、哪裡會卡
- Teacher：決定講解順序和例題
- Video Production：處理畫面、旁白和輸出
- Quality Management：做播放檢查和成品驗收

之後你可以直接說：
`用 Lecture1 team 跑下一個 unit`

我會照這個隊形把任務分下去，該改 slide、scene、render 或影片時再進到對應步驟。

文件在：`LECTURE1_TEAM_ROSTER.md`
```

Do not put internal control-plane roles, packet names, runtime details, or
continuity receipts in this first response. Keep those in generated files,
review/debug replies, or later explanations when the user asks.

If this turn only prepared a roster, say that as current-turn scope. Do not make
it sound like Roster cannot later assign and execute slide, scene, render,
video, or QA work.

For Quality setup requests, Codex should answer as a project coordinator first,
not as a governance explainer:

```text
我會把 Quality 分成兩層：

短期先看這次 unit 能不能交付：
- 內容是否講得清楚
- slide / scene / video 是否一致
- 有沒有明顯漏掉的步驟

長期則看這個 Lecture1 team 是否需要固定檢查流程：
- 每個 unit 完成後都做 playback check
- 每次修改 scene 後確認 slide 對應
- 最後輸出前做一次完整驗收

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
我會把這類 visual artifact 預設加一個短 Quality loop：

- 先產出第一版
- 看畫面裡文字、重點元素和圖層有沒有互相遮住
- 修掉明顯的可讀性或畫面一致性問題
- 再重看 1-2 輪，沒有明顯問題才交付

如果需要播放或截圖檢查，我會把那當成工具能力來處理。
```

The loop applies to slides, scenes, renders, videos, screenshots, images, UIs,
and presentations. It should inspect visible output for text occlusion, key
element occlusion, layout overlap, poor contrast or unreadable scale, missing
expected content, and slide/render/video mismatch. Use 2-3 bounded iterations,
or stop earlier when no material issue remains.

Playback, screenshot, OCR, render, Computer Use, and similar inspection tools
remain tool capabilities governed by the Capability Access Packet. Quality may
plan the check, but it does not own tool authorization.

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

- a document, slide deck, dataset, code change, video, or research artifact must
  be produced or revised
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

6. Confirm the invocation status. Current verified mechanism:
   installed `roster` skill plus `Roster` as a natural-language route alias,
   with `scripts/brain.sh packet-route` available to Codex or a reviewer as the
   internal adapter. `@roster` has been tested and is not yet a working installed
   Codex mention, plugin/app mention, or slash command.
7. Configure local LLM credentials or Codex auth for the provider you intend to
   use.
8. After a real mention/plugin/slash layer is implemented and verified,
   use the target health-check prompt:

```text
@roster run health check for this workspace.
```

9. Confirm that the health check reports skill install visibility, packet output,
   and LLM/provider status.

Current status: the prompt form above remains target behavior and is known not
to work through `@roster` today. The implemented health check is the repo-native
`roster-health` command, and the implemented install layer is the repo-owned
`roster` skill. It must not be described as a verified installed `@roster`
mention.
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
