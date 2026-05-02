# Implementation Spec

Task ID: `roster-v0_9-role-interaction-patterns-2026-05-02`
Parent Spec: `/Users/tom/Documents/PHD/codex-cns/contexts/artifact_harness_usage_experience/ROSTER_MILESTONE_ROADMAP.md`
Intent Record: `/Users/tom/Documents/PHD/codex-cns/contexts/task_runs/roster-v0_9-role-interaction-patterns-2026-05-02/INTENT.md`
Current State: `/Users/tom/Documents/PHD/codex-cns/contexts/task_runs/roster-v0_9-role-interaction-patterns-2026-05-02/CURRENT_STATE.md`

## Objective

Implement this specific change:

```text
Teach Roster to record how roles interact through explicit Role Interaction
Patterns, instead of only listing roles and work cards.
```

## Work Type

Select the closest type:

- `docs`
- `markdown`
- `template`
- `text-audit`
- `tests` only if existing docs/tests need small updates
- `code` only if help/route output already has a narrow place for interaction
  pattern guidance

## Scope

Allowed scope:

- `skills/roster/SKILL.md`
- `plugins/roster/commands/roster.md`
- `README.md`
- `contexts/artifact_harness_usage_experience/README.md`
- `contexts/artifact_harness_usage_experience/README.target-user-experience.draft.md`
- `contexts/artifact_harness_usage_experience/ROSTER_NEXT_VERSION_DIRECTION.md`
- `contexts/artifact_harness_usage_experience/ROSTER_MILESTONE_ROADMAP.md`
- `contexts/artifact_harness_usage_experience/developer_reports/prompt_v0_9_role_interaction_patterns.prompt.md`
- `templates/team_architect/team_operating_packet.template.md`
- optionally `templates/team_architect/role_interaction_edge.template.md`
- optionally behavior validation docs under
  `contexts/artifact_harness_usage_experience/behavior_validation/`
- this packet directory

Forbidden scope:

- Do not implement automatic subagent spawning.
- Do not change runtime adapter behavior.
- Do not add a message bus, daemon, server, database, or persistent runtime
  service.
- Do not change CAP authorization ownership.
- Do not execute approvals automatically.
- Do not implement real BCQ_III APP work.
- Do not implement real meeting-note or slide-deck production.
- Do not make ordinary first-touch replies expose internal governance terms.

## Requirements

Behavior or content requirements:

- Define Role Interaction Patterns as role-to-role edges inside the Team
  Architect task graph.
- Distinguish:
  - role list;
  - group/member expansion;
  - Agent Work Cards;
  - Role Interaction Patterns.
- Add or preserve this vocabulary:
  - `handoff`;
  - `dialogue_friction_loop`;
  - `peer_alignment`;
  - `review_challenge`;
  - `approval_signoff`;
  - `parallel_contribution`;
  - `quality_loop`.
- For each pattern, define:
  - directionality;
  - when to use it;
  - authority boundary;
  - expected shared artifact or decision;
  - revision, escalation, or fallback behavior.
- State that interaction edges alter task graph behavior, not governance
  ownership.
- State that approval signoff is only blocking when the user or policy grants
  blocking authority.
- State that capability implications from an interaction edge are only inputs
  to CAP; they are not authorization.
- State that interaction edges do not automatically spawn subagents.

Structure requirements:

- Team Operating Packet should have a clear place to record role interaction
  edges, either inline or through a linked template.
- A role interaction edge should have enough fields to be executable by a future
  agent:
  - source role;
  - target role(s);
  - interaction type;
  - direction;
  - trigger;
  - shared artifact;
  - expected output or decision;
  - done condition;
  - revision or escalation rule;
  - authority boundary;
  - capability implication;
  - fallback owner.
- Work-card docs should explain that `handoff_target` is only the next receiver,
  while interaction edges describe how the roles work together.
- Public README should stay short and human-facing; fuller vocabulary can live
  in usage/developer docs.

Example requirements:

- Teacher + Student maps to `dialogue_friction_loop`.
- Engineering Technical Staff + Financial Technical Staff maps to
  `peer_alignment`.
- Producer + Quality Reviewer maps to `quality_loop`.
- Meeting notes -> executive slides should include edges such as:
  - 原始內容整理人 -> 會議紀錄人員: `handoff`;
  - 會議紀錄人員 <-> 內容一致性檢查人員: `review_challenge`;
  - 主管視角整理人 <-> 簡報架構人員: `peer_alignment`;
  - 簡報製作人員 <-> 視覺整理人員: `quality_loop`;
  - 交付前檢查人員 -> 使用者: `approval_signoff` only if granted.
- BCQ_III should include edges such as:
  - 中醫內容負責人 -> 統計方法人員: `handoff`;
  - 統計方法人員 <-> 模型驗證人員: `peer_alignment` or
    `review_challenge`, depending on authority;
  - 使用者端產品人員 <-> 醫師端產品人員: `parallel_contribution`
    followed by integration;
  - APP 前端人員 <-> Quality 檢查人員: `quality_loop`;
  - 法務與隱私審查人員 -> 專案協調人: `approval_signoff` only if
    granted.

Wording requirements:

- Ordinary user-facing examples should use plain language such as:
  `我會讓會議紀錄先交給簡報企劃，再由 Quality 回頭檢查是否漏掉決議。`
- Do not force terms like `interaction_edge`, `Team Architect`, `CAP`, or
  `runtime adapter` into first-touch examples.
- Do not imply the user must choose the interaction pattern manually.
- Do not imply Roster has finished the future `v0.10.0` subagent policy.

## Non-Goals

Do not do these in this pass:

- subagent policy implementation;
- automatic subagent spawning;
- persistent interaction-edge storage beyond packet/template docs;
- runtime invocation changes;
- message bus implementation;
- shared-state runtime implementation;
- CAP authorization changes;
- approval execution;
- release tagging;
- real app/deck artifact production.

## Acceptance Criteria

The task is complete when:

- `skills/roster/SKILL.md` explains when and how to use Role Interaction
  Patterns.
- `plugins/roster/commands/roster.md` carries equivalent user-facing behavior
  guidance.
- `templates/team_architect/team_operating_packet.template.md` can record
  interaction edges separately from roles and work cards.
- A standalone `role_interaction_edge` template exists or the Team Operating
  Packet has a complete inline structure.
- Docs define all required interaction types.
- Docs include at least one BCQ_III interaction-edge example and one meeting
  notes to executive slides example.
- Docs preserve first-touch simplicity and do not leak internal governance
  terms into ordinary examples.
- Docs state interaction edges do not grant capability authorization or spawn
  agents.
- Validation commands pass or failures are documented with risk.
- Developer report is written to the required report path.

## Validation Plan

Run or perform:

```sh
python3 -m py_compile scripts/system_hub.py scripts/test_system_hub.py
python3 scripts/test_system_hub.py
python3 scripts/test_overlay_policy.py
python3 scripts/test_run_agent_benchmark.py
python3 -m json.tool contexts/team_alias_registry.json
git diff --check
```

Also inspect:

- public README first-touch examples stay short;
- Role Interaction Patterns vocabulary is complete;
- Team Operating Packet separates role list, work cards, and interaction
  edges;
- no docs imply every interaction edge becomes a subagent;
- no docs imply approval signoff blocks without user/policy authority;
- no docs imply capability implication equals authorization.

If validation cannot run, explain why and what risk remains.

## Handoff Requirements

Developer final response must include:

- Changed files.
- Implemented interaction-pattern behavior.
- Validation commands and results.
- Remaining risks.
- Whether the task is ready for review.
