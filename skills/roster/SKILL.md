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
- Quality direction, self-check setup, or short-term vs long-term correction
  planning for an artifact task
- explicit Roster preference memory such as "記住", "以後", "每次", or
  "預設" for future coordination behavior in this workspace
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
4. For artifact tasks, route through the installed kit command from
   `references/install_manifest.json`:
   `<brain_command> packet-route "<utterance>" --path <workspace> --json`.
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

`roster-uninstall` should remove only a manifest-owned Roster install by
default; use `--force` only when the user confirms an unknown same-name skill
should be removed.
