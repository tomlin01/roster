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
