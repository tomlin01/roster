---
name: roster
description: This skill should be used when the user invokes Roster or asks Codex to staff, coordinate, plan, boundary, route, resume, or review a concrete artifact task using the local Roster coordination kit.
---

# Roster

Use Roster as the local staffing-and-coordination surface for artifact-producing
work. Keep ordinary user interaction in plain language and use the repo packet
engine as an internal adapter.

## Trigger

Use this skill when the user asks for:

- `Roster, ...` task coordination
- staffing or role design for an artifact task
- project/task boundary setup
- Team Architect, Capability Access Packet, runtime mapping, or review handoff
- resuming or inspecting a Roster packet run
- installing or checking the Roster coordination surface

Do not claim `@roster` is a working installed Codex mention. Treat `@roster` as
a future product target unless a local health check explicitly proves otherwise.

## Operating Boundary

- Artifact Harness owns task rules, contract, acceptance, and boundary.
- HR owns staffing and role design only.
- Team Architect owns collaboration pattern, shared artifacts, task graph,
  convergence, and CAP generation.
- Capability Access Packet owns skill, plugin, tool authorization, approval
  gates, and runtime allowlist.
- Runtime adapters execute only; they do not own governance.

## Workflow

1. Identify the active target workspace. If several folders are plausible, ask
   one short location question before writing files.
2. Prefer plain language in user-facing replies. For first-touch replies, show
   the useful team shape and next invocation phrase before any formal packet
   names. Mention internal names only when the user asks for review, debug, or
   implementation details.
3. For artifact tasks, route through the installed kit command from
   `references/install_manifest.json`:
   `<brain_command> packet-route "<utterance>" --path <workspace> --json`.
4. Create packet files only when the route is create-ready or the user clearly
   asks to set up the task forms.
5. Keep generated packets under the target workspace:
   `<workspace>/contexts/artifact_harness_runs/<packet-id>/`.
6. For setup checks, use `scripts/brain.sh roster-health --path <workspace>
   --json` and include `--codex-home <dir>` when verifying an installed skill.

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
assign scene, render, video, QA, or other artifact work to the relevant roles.

Good first-touch shape:

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

## Installed Kit Reference

When this skill is installed by `roster-install`, the installer writes
`references/install_manifest.json` inside the installed skill folder. Load that
manifest when the kit root or command path is needed; use its `brain_command`
value instead of assuming the current working directory is the Roster kit root.

If the manifest is unavailable, ask for the Roster kit folder before running
repo adapter commands.
