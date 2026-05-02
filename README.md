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
make a remote model call.

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
