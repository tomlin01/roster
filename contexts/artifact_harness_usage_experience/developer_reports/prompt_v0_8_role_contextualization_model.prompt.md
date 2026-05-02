# Prompt v0.8.0: Roster Role Contextualization Model

## Context

Roster `v0.7.0` added the first-touch UX contract: short replies, natural role
phrasing, ordinary meeting-note roles, and complexity handling without exposing
internal labels.

The next step is not to add a full role interaction engine. It is to teach
Roster how to interpret user-named roles in context.

Read first:

- `contexts/artifact_harness_usage_experience/ROSTER_NEXT_VERSION_DIRECTION.md`
- `contexts/artifact_harness_usage_experience/ROSTER_MILESTONE_ROADMAP.md`
- `contexts/task_runs/roster-v0_8-role-contextualization-model-2026-05-02/IMPLEMENTATION_SPEC.md`
- `skills/roster/SKILL.md`
- `plugins/roster/commands/roster.md`
- `README.md`

## Goal

Implement the `v0.8.0` Role Contextualization Model:

- Treat roles as context-shaped responsibilities and perspectives, not fixed
  labels.
- Let users add roles by title, rank, function, shorthand, or domain.
- Distinguish role, perspective, layer, and agent instance.
- Distinguish domain extension, peer domain role, and reviewer or approver role.
- Keep user-facing replies natural and short.

## Required Behavior

Add guidance and examples so Roster can handle role changes like these:

```text
加一個主管
讓 PM 看一下
需要法務審
加一個學生視角
技術人員加入金融 domain
新增一位金融技術人員，跟原本技術人員同級
金融技術人員要核准模型結果才能交付
```

Roster should infer:

- responsibility: what the role contributes
- perspective: what the role watches for
- workflow position: when it acts
- authority boundary: advises, challenges, requests revision, blocks, or signs
  off
- capability implication: whether the role may need data, tool, plugin, model,
  filesystem, screenshot, playback, OCR, or runtime access

## Role Classification Rules

### Domain Extension

Use when the user adds a domain to an existing role.

Example:

```text
技術人員加入金融 domain
```

Default behavior:

- Keep one role with a multi-domain perspective.
- Do not create a new agent or approval gate by default.
- Mention the added domain as part of what the role checks.

User-facing shape:

```text
我會先把技術人員改成「工程 + 金融」的整合視角：一邊處理資料和工具，一邊確認金融定義沒有被處理流程扭曲。
```

### Peer Domain Role

Use when the user adds a new same-level person, agent, or domain specialist.

Example:

```text
新增一位金融技術人員，跟原本技術人員同級
```

Default behavior:

- Add a peer role.
- Add an alignment step.
- Do not treat the peer as reviewer or approver unless the user says so.

User-facing shape:

```text
我會把它拆成兩個同級視角：工程技術人員負責資料和工具流程，金融技術人員確認指標定義和解讀。兩邊先對齊，再交給產出角色。
```

### Reviewer Or Approver Role

Use when the user gives the role review, blocking, approval, or sign-off
authority.

Example:

```text
金融技術人員要核准模型結果才能交付
```

Default behavior:

- Add a review or approval checkpoint.
- Preserve existing approval and tool-boundary ownership.
- Do not make the role a runtime or capability owner.

User-facing shape:

```text
我會把金融技術人員放在交付前審核位置：模型結果先由他確認定義和風險，通過後再交付。
```

### Counter-Perspective Role

Use when the user adds an audience, learner, customer, stakeholder, edge-case,
or challenge perspective.

Examples:

```text
加一個學生視角
讓客戶代表看一下
```

Default behavior:

- Add a friction or comprehension check.
- Use it before final production or final review.
- Do not treat it as approval unless the user gives approval authority.

User-facing shape:

```text
我會加入學生視角來挑出哪裡太難、太快或缺例子；教師角色再根據這個回饋調整講解順序。
```

## Required Internal Distinctions

Document these distinctions clearly:

- `role`: a named responsibility in the roster
- `perspective`: what that role is watching for
- `layer`: planning, production, domain judgment, or quality coverage
- `agent instance`: the execution resource that may carry one or more roles,
  perspectives, or layers

Important rule:

```text
Adding a role does not automatically mean adding a new agent.
```

Also document:

```text
The default four-role shape is a layer compression, not a hard maximum.
```

## User-Facing Constraints

- Do not expose `Artifact Harness`, `HR`, `Team Architect`, `CAP`, runtime
  adapter, packet chain, or control-plane terms in ordinary first-touch replies.
- Do not force the user to decide task complexity.
- Do not force the user to know whether a role is a layer, perspective, or
  agent.
- Do not overexplain. Give the role interpretation and the next action.

## Likely Files

- `skills/roster/SKILL.md`
- `plugins/roster/commands/roster.md`
- `README.md`
- `contexts/artifact_harness_usage_experience/README.md`
- `contexts/artifact_harness_usage_experience/README.target-user-experience.draft.md`
- `templates/team_architect/team_operating_packet.template.md`
- `templates/team_architect/capability_access_packet.template.md` only if needed
  for capability implication references
- `scripts/system_hub.py` and `scripts/test_system_hub.py` only if existing
  route/help JSON output needs role-context hints or tests

## Non-Goals

Do not implement:

- full Role Interaction Patterns;
- Team Operating Packet interaction-edge schema;
- automatic subagent spawning;
- runtime adapter changes;
- persistent role database;
- Rust rewrite;
- project/team mode.

Do not claim:

- that every user-added role becomes a separate agent;
- that Roster can infer authority safely when the user is ambiguous;
- that role context replaces approval gates, tool authorization, or final
  artifact acceptance.

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

- Role examples include domain extension, peer domain role, reviewer/approver,
  and counter-perspective cases.
- Ordinary user-facing examples avoid internal governance terms.
- Docs state that adding a role does not automatically add an agent.
- Docs state that the four-role shape is a layer compression, not a hard
  maximum.
- User-facing examples show what Roster will do next, not a long taxonomy dump.

## Report

Write a report to:

`contexts/artifact_harness_usage_experience/developer_reports/prompt_v0_8_role_contextualization_model.report.md`

Report:

- changed files;
- implemented role-context behavior;
- validation commands and results;
- remaining risks;
- whether ready for review.
