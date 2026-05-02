# Prompt v0.7.0: Roster First-Touch UX Contract

## Context

Roster `v0.6.0` has install/uninstall/health, local plugin/slash source, natural
`Roster, ...` fallback, workspace-local preferences, and packet routing. The next
release should improve ordinary first-touch UX without expanding the architecture.

Read first:

- `contexts/artifact_harness_usage_experience/ROSTER_NEXT_VERSION_DIRECTION.md`
- `contexts/artifact_harness_usage_experience/ROSTER_MILESTONE_ROADMAP.md`
- `skills/roster/SKILL.md`
- `plugins/roster/commands/roster.md`
- `README.md`

## Goal

Implement the `v0.7.0` First-Touch UX Contract:

- Roster replies should feel natural, short, and role-shaped.
- Roster should adapt its first response to task complexity.
- Roster should not expose internal governance terms in ordinary first-touch
  replies.
- Roster should use concrete role names that match the user's context.

## Required Behavior

Add guidance and examples so Roster first-touch replies follow these rules:

1. Use the smallest useful team presentation.
2. Keep layer coverage active even when execution stays single-agent.
3. Do not show `Level 1`, `Level 2`, `complexity score`, or similar debug terms
   to ordinary users.
4. Use plain phrasing to reveal the selected handling mode:
   - `這個任務我會直接處理並自檢。`
   - `這個任務我先用一個精簡小組處理。`
   - `這個任務牽涉幾個面向，我會先分成幾組協作。`
   - `這個任務的目標和權責還需要先對齊，我先幫你定隊形。`
5. For meeting-note examples, use natural Traditional Chinese role names:
   - `轉錄人員`
   - `會議紀錄人員`
   - `會議負責人`
6. Let the user adjust roles naturally:
   - `加一個主管`
   - `讓 PM 看一下`
   - `需要法務審`
   - `加一個學生視角`
7. Do not expose `Artifact Harness`, `HR`, `Team Architect`, `CAP`, runtime
   adapter, packet chain, or control-plane terms unless the user asks for
   review/debug/governance detail.

## Complexity Response Shapes

Document or encode these first-touch response shapes.

Level 1 behavior:

```text
這個任務我會直接處理並自檢，不先拆小組。
我會先整理出第一版，再檢查是否漏掉重點。
```

Level 2 behavior:

```text
我先用一個精簡會議小組處理：

- 轉錄人員：整理錄音或逐字稿
- 會議紀錄人員：抓重點、決議、待辦事項和負責人
- 會議負責人：確認紀錄是否符合會議目的和後續追蹤需求

如果可以，我就照這樣開始；你也可以直接說要加主管、法務、PM 或其他角色。
```

Level 3 behavior:

```text
這個任務牽涉幾個面向，我會先分成幾組協作：

- 內容組：整理主軸和交付物
- 技術組：處理資料、工具或轉換流程
- 審核組：檢查正確性、風險和品質

如果這個分組方向可以，我就展開每組的角色和第一步。
```

Level 4 behavior:

```text
這個任務的目標、權責或風險還需要先對齊。
我先幫你定隊形：先確認交付物、誰能決定方向、哪些地方需要審核。
確認後我再把它轉成工作小組和任務圖。
```

## Likely Files

- `skills/roster/SKILL.md`
- `plugins/roster/commands/roster.md`
- `README.md`
- `contexts/artifact_harness_usage_experience/README.md`
- `contexts/artifact_harness_usage_experience/README.target-user-experience.draft.md`
- optionally `scripts/system_hub.py` and `scripts/test_system_hub.py` if route
  output or health/report examples need to expose first-touch guidance

## Non-Goals

Do not implement:

- full role interaction engine;
- Team Operating Packet schema changes;
- automatic subagent spawning;
- new runtime adapter behavior;
- Rust rewrite;
- project/team mode.

Do not claim:

- that `@roster` or `/roster` UI invocation works without install/reload and
  host support;
- that Roster can know all task complexity perfectly;
- that every role becomes a separate agent.

## Validation

Run:

```sh
python3 -m py_compile scripts/system_hub.py scripts/test_system_hub.py
python3 scripts/test_system_hub.py
python3 scripts/test_overlay_policy.py
python3 scripts/test_run_agent_benchmark.py
python3 -m json.tool contexts/team_alias_registry.json
git diff --check
```

Text audit:

- Ordinary first-touch examples do not expose `Artifact Harness`, `HR`,
  `Team Architect`, `CAP`, runtime adapter, packet chain, or control plane.
- Complexity examples do not show `Level 1` / `Level 2` labels in the user-facing
  response body.
- Meeting-note examples use `轉錄人員`, `會議紀錄人員`, and `會議負責人`.
- Docs preserve fallback invocation: `Roster, ...`.
- Docs truthfully describe installed invocation: `@roster` and `/roster` only
  after `roster-install` plus Codex reload / supported host behavior.

## Report

Write a report to:

`contexts/artifact_harness_usage_experience/developer_reports/prompt_v0_7_first_touch_ux_contract.report.md`

Report:

- changed files;
- implemented first-touch behavior;
- validation commands and results;
- remaining risks;
- whether ready for review.
