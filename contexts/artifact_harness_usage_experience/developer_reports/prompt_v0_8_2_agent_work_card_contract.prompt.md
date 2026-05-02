# Prompt v0.8.2: Agent Work Card Contract

## Context

Roster `v0.8.0` added role contextualization. Roster `v0.8.1` added group
expansion: a broad task can first show groups, then expand groups into members
with responsibility, perspective, and deliverable.

The user then raised the next practical concern:

```text
我想另外確定每個AGENT都有對應的職責而不是只有給使用者看
```

The issue is not whether every role must become a separate runtime subagent.
The issue is whether each expanded role/member is actionable enough to become a
handoff unit when needed.

## Goal

Implement `v0.8.2` as an Agent Work Card Contract:

- Expanded members should not be decorative labels.
- Roster should be able to turn each relevant member into a compact executable
  work card.
- Work cards should define what the role needs, produces, checks, and hands off.
- Work cards should not force every role into a separate agent.
- Work cards should not implement the full `v0.9.0` Role Interaction Patterns
  edge model.

## Required Behavior

Add guidance and examples so Roster follows this rule:

```text
When Roster expands a role/member beyond first-touch preview, that member must
be convertible into a work card with concrete responsibility, input, output,
done condition, handoff target, capability need, and assignment mode.
```

### When To Show Work Cards

Do not show full work cards in ordinary short first-touch replies.

Show or offer work cards when:

- the user asks `誰做什麼`, `展開工作`, `工作卡`, `每個 agent 的職責`, or
  equivalent;
- the task moves from planning into implementation;
- the task is high risk and owner/completion clarity matters;
- the user adds a role with review, sign-off, domain, tool, or quality
  responsibility.

### Work Card Fields

Each work card should include, in natural language or structured form:

- `role_name`: role or member name.
- `group`: group or layer this role belongs to.
- `responsibility`: what this role owns.
- `perspective`: what this role watches for.
- `inputs`: what this role needs before starting.
- `outputs_or_deliverables`: what this role produces.
- `done_condition`: how Roster knows this role has completed its part.
- `handoff_target`: who receives the output next.
- `tool_or_capability_need`: likely skill, plugin, tool, data, screenshot, OCR,
  filesystem, runtime, or model need.
- `agent_assignment`: one of:
  - `separate_agent`
  - `merged_with`
  - `simulated_perspective`
  - `reviewer_only`
  - `approval_gate_candidate`
- `open_questions`: ambiguity that must be resolved before execution.

### Assignment Rules

Document these rules:

- A work card can map to a separate agent, but does not have to.
- A small task may use one agent to carry several work cards.
- A role can be a simulated perspective when separation is useful but runtime
  subagents are not needed or unavailable.
- Reviewer-only roles check outputs but do not own production.
- Approval-gate candidates may block delivery only when the user or policy gives
  explicit authority.
- Capability needs do not authorize tools. They are inputs to the Capability
  Access Packet and approval gates.

## Good Example

For the BCQ_III app task, one expanded member can become this work card:

```text
統計方法人員
- group: 統計與計分組
- responsibility: 定義填答轉分數、構面分數和門檻
- perspective: 分數是否可解釋、可重現，是否符合 BCQ_III 題目與構面
- inputs: BCQ_III 題目、構面定義、填答資料格式、使用者端與醫師端顯示需求
- outputs_or_deliverables: 計分規格與分數解釋規則
- done_condition: 每一題都能追到構面與計分規則，使用者端和醫師端分數定義一致
- handoff_target: 資料處理人員、分數驗證人員、使用者端組、醫師端組
- tool_or_capability_need: 試算表或統計腳本；若要執行程式，必須走工具授權
- agent_assignment: merged_with 分數驗證人員 for small tasks; separate_agent for high-risk validation
- open_questions: 是否已有正式 BCQ_III 計分規則與門檻來源
```

Short user-facing version:

```text
統計方法人員會交付「計分規格」：把每題如何轉成構面分數、門檻和解讀寫清楚。完成條件是使用者端和醫師端看到的是同一套可追蹤分數。小任務可和分數驗證合併；高風險時再拆成獨立 agent。
```

## Required Documentation Points

Document:

- Work cards are for execution clarity, not first-touch verbosity.
- Work cards make roles actionable.
- Work cards may be merged, simulated, separate, reviewer-only, or approval-gate
  candidates.
- Capability needs are not capability authorization.
- Handoff target is a next receiver, not the full v0.9 interaction-edge schema.
- Work cards do not replace Team Operating Packet, Capability Access Packet,
  runtime policy, verification, approval evidence, or final artifact acceptance.

## Likely Files

- `skills/roster/SKILL.md`
- `plugins/roster/commands/roster.md`
- `README.md`
- `contexts/artifact_harness_usage_experience/README.md`
- `contexts/artifact_harness_usage_experience/README.target-user-experience.draft.md`
- `contexts/artifact_harness_usage_experience/ROSTER_MILESTONE_ROADMAP.md`
- `contexts/artifact_harness_usage_experience/ROSTER_NEXT_VERSION_DIRECTION.md`
- `templates/team_architect/team_operating_packet.template.md`
- optionally `templates/team_architect/agent_work_card.template.md` if a small
  standalone template is cleaner than overloading the Team Operating Packet.

## Non-Goals

Do not implement:

- full Role Interaction Patterns;
- interaction-edge schema;
- automatic subagent spawning;
- persistent role/work-card database;
- runtime adapter changes;
- CAP authorization changes;
- project/team mode;
- BCQ_III app implementation.

Do not claim:

- every work card creates a separate agent;
- Roster can safely infer approval authority without user or policy evidence;
- tool or capability need equals permission;
- work cards are a replacement for artifact acceptance or verification.

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

- Roster docs define work-card fields.
- BCQ_III or equivalent example includes responsibility, perspective, inputs,
  deliverable, done condition, handoff target, capability need, and assignment
  mode.
- Public first-touch examples do not become long work-card dumps.
- Docs state work cards do not automatically spawn subagents.
- Docs state capability needs are not authorization.
- Docs state this is not full v0.9 interaction-edge modeling.

## Report

Write a report to:

`contexts/artifact_harness_usage_experience/developer_reports/prompt_v0_8_2_agent_work_card_contract.report.md`

Report:

- changed files;
- implemented work-card behavior;
- validation commands and results;
- remaining risks;
- whether ready for review.
