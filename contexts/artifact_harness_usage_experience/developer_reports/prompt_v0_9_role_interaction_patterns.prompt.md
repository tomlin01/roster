# Prompt v0.9.0: Role Interaction Patterns

## Context

Roster has reached the point where:

- `v0.8.0` treats roles as context-shaped responsibilities and perspectives.
- `v0.8.1` expands broad groups into concrete members.
- `v0.8.2` turns expanded members into Agent Work Cards.
- BCQ_III and meeting-notes-to-executive-slides behavior evidence show that
  Roster can now create useful role/work-card structures.

The current gap is that complex multi-agent rosters still lack explicit
role-to-role interaction edges. A role can know what it owns, but the team does
not yet formally know how roles interact.

## Goal

Implement `v0.9.0` as Role Interaction Patterns:

```text
roles -> work cards -> interaction edges
```

The change should let Roster and Team Operating Packet record:

- who hands off to whom;
- who aligns with whom;
- who challenges or reviews whom;
- where Quality loops back;
- where sign-off can block progress;
- what shared artifact anchors the interaction;
- how each interaction completes or escalates.

## Required Reads

Read the packet first:

- `/Users/tom/Documents/PHD/codex-cns/contexts/task_runs/roster-v0_9-role-interaction-patterns-2026-05-02/INTENT.md`
- `/Users/tom/Documents/PHD/codex-cns/contexts/task_runs/roster-v0_9-role-interaction-patterns-2026-05-02/CURRENT_STATE.md`
- `/Users/tom/Documents/PHD/codex-cns/contexts/task_runs/roster-v0_9-role-interaction-patterns-2026-05-02/IMPLEMENTATION_SPEC.md`
- `/Users/tom/Documents/PHD/codex-cns/contexts/task_runs/roster-v0_9-role-interaction-patterns-2026-05-02/REVIEW_SPEC.md`

Then read:

- `/Users/tom/Documents/PHD/codex-cns/contexts/artifact_harness_usage_experience/ROSTER_NEXT_VERSION_DIRECTION.md`
- `/Users/tom/Documents/PHD/codex-cns/contexts/artifact_harness_usage_experience/ROSTER_MILESTONE_ROADMAP.md`
- `/Users/tom/Documents/PHD/codex-cns/templates/team_architect/team_operating_packet.template.md`
- `/Users/tom/Documents/PHD/codex-cns/contexts/artifact_harness_usage_experience/behavior_validation/BCQ_III_AGENT_WORK_CARD_RUN_2026-05-02.md`
- `/Users/tom/Documents/PHD/codex-cns/contexts/artifact_harness_usage_experience/behavior_validation/MEETING_NOTES_TO_EXEC_SLIDES_RUN_2026-05-02.md`

## Required Changes

Implement the docs/template layer for Role Interaction Patterns.

Likely files:

- `skills/roster/SKILL.md`
- `plugins/roster/commands/roster.md`
- `README.md`
- `contexts/artifact_harness_usage_experience/README.md`
- `contexts/artifact_harness_usage_experience/README.target-user-experience.draft.md`
- `contexts/artifact_harness_usage_experience/ROSTER_NEXT_VERSION_DIRECTION.md`
- `contexts/artifact_harness_usage_experience/ROSTER_MILESTONE_ROADMAP.md`
- `templates/team_architect/team_operating_packet.template.md`
- optionally `templates/team_architect/role_interaction_edge.template.md`

Write a developer report to:

`contexts/artifact_harness_usage_experience/developer_reports/prompt_v0_9_role_interaction_patterns.report.md`

## Interaction Pattern Vocabulary

Define these pattern types:

- `handoff`: one role passes a completed or prepared artifact to another role.
- `dialogue_friction_loop`: a counter-perspective role creates productive
  friction with a primary role before production.
- `peer_alignment`: same-level roles align assumptions, definitions, or
  boundaries before handoff.
- `review_challenge`: one role checks another role's output and may request
  revision without blocking by default.
- `approval_signoff`: one role can approve or block the next step only when the
  user or policy grants that authority.
- `parallel_contribution`: multiple roles produce separate parts that later
  integrate.
- `quality_loop`: Quality findings return to the responsible producer or
  upstream role for correction and recheck.

## Interaction Edge Fields

Each edge should be able to record:

- source role;
- target role or roles;
- interaction type;
- direction: one-way / two-way / parallel / loop;
- trigger;
- shared artifact;
- expected output or decision;
- done condition;
- revision or escalation rule;
- authority boundary;
- capability implication;
- fallback owner.

## Required Examples

Include examples for:

- Teacher + Student: `dialogue_friction_loop`.
- Engineering Technical Staff + Financial Technical Staff: `peer_alignment`.
- Producer + Quality Reviewer: `quality_loop`.
- Manager sign-off: `approval_signoff` only when granted.
- BCQ_III:
  - 中醫內容負責人 -> 統計方法人員: `handoff`;
  - 統計方法人員 <-> 模型驗證人員: `peer_alignment` or
    `review_challenge`, depending on authority;
  - 使用者端產品人員 and 醫師端產品人員: `parallel_contribution`
    followed by integration;
  - APP 前端人員 <-> Quality 檢查人員: `quality_loop`;
  - 法務與隱私審查人員 -> 專案協調人: `approval_signoff` only if
    granted.
- Meeting notes to executive slides:
  - 原始內容整理人 -> 會議紀錄人員: `handoff`;
  - 會議紀錄人員 <-> 內容一致性檢查人員: `review_challenge`;
  - 主管視角整理人 <-> 簡報架構人員: `peer_alignment`;
  - 簡報製作人員 <-> 視覺整理人員: `quality_loop`;
  - 交付前檢查人員 -> 使用者: `approval_signoff` only if granted.

## Boundary Rules

Preserve these boundaries:

- Interaction edges alter task graph behavior, not governance ownership.
- Interaction edges do not grant capability authorization.
- Capability implications are inputs to CAP only.
- Interaction edges do not automatically spawn subagents.
- Approval signoff is blocking only when user or policy grants blocking
  authority.
- Runtime adapters remain execution layers only.
- Team Architect owns the task graph and convergence; Roster supplies the
  role-context and interaction-edge information.

## User-Facing Wording

Ordinary first-touch replies should not expose internal labels.

Good user-facing shape:

```text
我會先讓會議紀錄人員整理決議和待辦，再交給簡報企劃壓成主管看的 6 頁架構。
簡報初稿完成後，Quality 會回頭檢查是否漏掉決議、待辦是否有負責人、頁面是否能快速讀懂。
```

Bad patterns:

- Dumping `interaction_edge` fields in first-touch replies.
- Saying `Team Architect` or `CAP` in ordinary user-facing output.
- Saying a manager approval blocks delivery when the user never granted
  blocking authority.
- Saying a Quality loop automatically has screenshot, CV, or runtime access.
- Saying every edge spawns a separate subagent.

## Non-Goals

Do not implement:

- automatic subagent spawning;
- subagent policy;
- runtime execution changes;
- message bus;
- shared-state runtime;
- approval execution;
- CAP authorization changes;
- real BCQ_III app;
- real meeting-note or slide-deck production;
- release tagging.

## Verification

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

- Role Interaction Patterns vocabulary is complete.
- Team Operating Packet separates role list, work cards, and interaction
  edges.
- Public first-touch examples remain short.
- No docs imply interaction edges authorize tools.
- No docs imply interaction edges spawn agents.
- No docs imply approval signoff blocks without user/policy authority.

## Report

Return:

- Changed files.
- What was implemented.
- Validation commands and results.
- Remaining risks.
- Whether ready for review.
