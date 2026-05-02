# Prompt v0.8.1: Group Expansion UX Patch

## Context

Roster `v0.7.0` added first-touch UX guidance. Roster `v0.8.0` added role
contextualization: user-added roles can be interpreted as domain extensions,
peer domain roles, reviewer/approver roles, or counter-perspectives.

The user confirmed one missing UX detail:

```text
多組協作是會幫我細分小組成員嗎
```

Expected answer: yes, but not on the first touch unless the task needs it.
Roster should first show groups for broad tasks, then expand groups into
members, responsibilities, perspectives, and deliverables when the user asks,
the task needs implementation detail, or risk requires it.

## Goal

Implement `v0.8.1` as a small UX patch:

- Multi-group collaboration is not only a list of group names.
- Roster can expand groups into concrete members.
- First-touch replies stay short by default.
- Expansion happens on request, during implementation planning, or for high-risk
  / high-complexity tasks.
- This does not become the full `v0.9.0` Role Interaction Patterns work.

## Required Behavior

Add guidance and examples so Roster follows this flow:

1. First touch for broad tasks:
   - Show group-level structure only.
   - Use short group names and one-line responsibilities.
   - Do not overload the user with every member immediately.
2. Expansion trigger:
   - The user says `展開`, `細分`, `小組成員`, `誰負責什麼`, or equivalent.
   - The task is moving from planning into implementation.
   - The task is high-risk enough that owner/perspective clarity matters.
3. Expanded view:
   - Each group may expand into members.
   - Each member should have responsibility, perspective, and deliverable.
   - Expansion should reuse `v0.8.0` role-context rules.
4. Role additions after expansion:
   - Decide whether the role joins an existing group, becomes a same-level peer,
     becomes reviewer/approver, or becomes counter-perspective.
5. Keep user-facing language natural:
   - Say what changed and what happens next.
   - Do not expose internal packet, governance, or interaction-edge vocabulary.

## Good Example

For a BCQ_III app task:

First touch:

```text
這個任務牽涉中醫內容、統計邏輯和 APP 雙端流程，我會先分成幾組協作：

- 問卷與中醫組：整理 BCQ_III 題目、構面、體質解讀和報告文字
- 統計與計分組：定義分數計算、構面分數、門檻和可信度提醒
- 使用者端組：設計填答流程、報告結果、解讀文字和下一步建議
- 醫師端組：設計填答明細、分數表、風險提示和追蹤註記
- Quality 組：檢查分數一致性、醫療語氣、資料隱私和使用者誤解風險

如果這個分組方向可以，我再展開每組的小組成員和第一步。
```

Expansion:

```text
我會把 BCQ_III APP 的小組展開成這樣：

- 問卷與中醫組
  - 中醫內容負責人：確認構面和體質解讀
  - 報告文字整理人：把中醫概念轉成使用者看得懂的說明
  - 醫師審核人：確認文字不會過度診斷或誤導

- 統計與計分組
  - 統計方法人員：確認計分規則、構面分數和門檻
  - 資料處理人員：把問卷答案轉成可計算資料
  - 分數驗證人員：檢查分數是否可重現、是否和題目對應

- 使用者端組
  - UX 人員：設計填答流程和報告閱讀順序
  - APP 前端人員：實作填答畫面和結果頁
  - 使用者代表：檢查結果是否看得懂、會不會誤解

- 醫師端組
  - 臨床使用者代表：確認醫師需要哪些分數和原始填答
  - 後台產品人員：設計分數表、填答明細和追蹤紀錄
  - 權限與隱私人員：確認誰能看哪些資料

- Quality 組
  - 醫療風險檢查人員：檢查診斷、建議和免責語氣
  - 計分一致性檢查人員：核對使用者端和醫師端分數一致
  - 可用性檢查人員：檢查報告是否清楚、欄位是否容易看錯
```

## Required Documentation Points

Document:

- Group-level preview is the default for broad first-touch replies.
- Member expansion is available and expected when useful.
- Expanded members should include responsibility, perspective, and deliverable.
- Expansion does not automatically mean every member is a separate agent.
- Expansion does not replace `v0.9.0` role interaction edges.
- Expansion should preserve `v0.8.0` role contextualization rules.

## Likely Files

- `skills/roster/SKILL.md`
- `plugins/roster/commands/roster.md`
- `README.md`
- `contexts/artifact_harness_usage_experience/README.md`
- `contexts/artifact_harness_usage_experience/README.target-user-experience.draft.md`
- `contexts/artifact_harness_usage_experience/ROSTER_MILESTONE_ROADMAP.md`
- `contexts/artifact_harness_usage_experience/ROSTER_NEXT_VERSION_DIRECTION.md`
- optionally `templates/team_architect/team_operating_packet.template.md` if
  group/member expansion fill notes are needed

## Non-Goals

Do not implement:

- full Role Interaction Patterns;
- handoff / peer_alignment / review_challenge edge schema;
- automatic subagent spawning;
- persistent group/member storage;
- runtime adapter changes;
- project/team mode.

Do not claim:

- every expanded member becomes a separate agent;
- every broad task needs all groups expanded immediately;
- group expansion is the same as role interaction modeling.

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

- BCQ_III example or equivalent appears in docs.
- First-touch group preview remains shorter than expanded member view.
- Expanded member view includes responsibility, perspective, and deliverable
  either explicitly or through clear role descriptions.
- Docs state expansion does not automatically create separate agents.
- Docs state this is not full role interaction-edge modeling.

## Report

Write a report to:

`contexts/artifact_harness_usage_experience/developer_reports/prompt_v0_8_1_group_expansion_ux_patch.report.md`

Report:

- changed files;
- implemented group-expansion UX behavior;
- validation commands and results;
- remaining risks;
- whether ready for review.
