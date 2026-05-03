# Roster Next Version Direction

Date: `2026-04-30`
Status: `working direction`

## Core Direction

Roster should feel less like a hidden governance system and more like a
lightweight project office that helps the user form a working team.

The user still defines the product, goal, taste, and final direction. Roster
does not replace that judgment. Its job is to propose a simple team shape,
translate that team into roles that fit the user's situation, explain how the
roles will collaborate, and let the user confirm or adjust before the task
becomes too heavy.

## First-Touch UX

When a user starts a non-trivial task with Roster, the useful first response is
not a full packet chain. It should show a compact team preview. The generic
Planner / Producer / Reviewer shape is still useful as an internal default,
but Roster should translate that shape into roles that fit the user's actual
situation when the situation is clear.

```text
我先用這個隊形跑：

- Planner：整理目標、範圍和交付物
- Domain Reviewer：檢查內容是否合理
- Producer：產出第一版 artifact
- Quality Reviewer：做最後檢查和 1-2 輪修正

協作方式：
Planner 先收斂邊界，Producer 做第一版，Reviewer 檢查後回給 Producer 修正。

如果這個隊形可以，我就照它開始；如果你想加人或換角色，直接說。
```

This preview should be short enough that the user can accept or adjust without
thinking through internal architecture. The role names should feel like people
who would naturally exist in the user's work setting, not like Roster's
internal process labels.

Users should not have to judge task complexity themselves. Roster should make
an initial complexity call, then present only the amount of team structure that
fits the task.

Suggested first-touch complexity levels:

1. `single-agent full-layer pass`
   - One agent covers planning, production, domain judgment, and quality.
   - Use for small, low-risk, low-ambiguity tasks.
   - User-facing response should be short and should not show a full team unless
     useful.
2. `basic four-layer team`
   - Use the default planning, production, domain judgment, and quality layers.
   - These may appear as four visible roles or as context-shaped equivalents.
   - Use when the task has a clear artifact and benefits from explicit checks.
3. `expanded specialist roster`
   - Expand one or more layers into specialist, peer, counter-perspective, or
     approval roles.
   - Tentative size guideline: about 6-8 visible roles or perspectives, but only
     when the task needs that much separation.
   - Use for multi-domain, high-quality, visual, analytical, or stakeholder-heavy
     work.
4. `agent-led roster design`
   - Roster should not guess a final team shape alone.
   - Use when goals, authority, risk, stakeholder expectations, or capability
     boundaries are unclear.
   - Roster leads a short discussion with the user to shape the team, then turns
     that into the working roster and task graph.

The first response should adapt to the level. Level 1 should feel almost
invisible. Level 2 can show a compact team preview. Level 3 can show a grouped
roster. Level 4 should explicitly say that Roster needs to design the team with
the user before proceeding.

The response should make the chosen level understandable without exposing
internal machinery. Use plain phrases such as:

- `這個任務我會直接處理並自檢。`
- `這個任務我先用一個精簡小組處理。`
- `這個任務牽涉幾個面向，我會先分成幾組協作。`
- `這個任務的目標和權責還需要先對齊，我先幫你定隊形。`

Do not make the user see labels like `Level 1`, `Level 2`, or `complexity
score` unless the user asks for debug or design detail.

Example response shapes:

Level 1:

```text
這個任務我會直接處理並自檢，不先拆小組。
我會先整理出第一版，再檢查是否漏掉重點。
```

Level 2:

```text
我先用一個精簡會議小組處理：

- 轉錄人員：整理錄音或逐字稿
- 會議紀錄人員：抓重點、決議、待辦事項和負責人
- 會議負責人：確認紀錄是否符合會議目的和後續追蹤需求

如果可以，我就照這樣開始；你也可以直接說要加主管、法務、PM 或其他角色。
```

Level 3:

```text
這個任務牽涉幾個面向，我會先分成幾組協作：

- 內容組：整理主軸和交付物
- 技術組：處理資料、工具或轉換流程
- 審核組：檢查正確性、風險和品質

如果這個分組方向可以，我就展開每組的角色和第一步。
```

Level 4:

```text
這個任務的目標、權責或風險還需要先對齊。
我先幫你定隊形：先確認交付物、誰能決定方向、哪些地方需要審核。
確認後我再把它轉成工作小組和任務圖。
```

## Product Definition Boundary

Roster should not ask the user to fully define the product before helping.

Better behavior:

- propose a default team and collaboration pattern;
- ask only one or two clarifying questions when the artifact goal is ambiguous;
- let the user modify roles in ordinary language;
- accept role additions by title, rank, function, or shorthand;
- infer a reasonable responsibility and workflow position for added roles;
- start work when the user says to proceed.

Avoid:

- requiring a complete product brief up front;
- asking the user to choose internal packet types;
- exposing HR, Team Architect, CAP, runtime mapping, or Artifact Harness terms
  in ordinary first-touch replies;
- implying Roster cannot execute artifact work just because the current turn
  only prepared planning;
- making the user define a complete org chart before Roster can help.

## Suggested Default Team

Use the generic team as the fallback mental model, but treat it as coordination
layers rather than fixed headcount:

- Planner: task boundary, deliverable, sequence, handoff.
- Domain Reviewer: factual or domain-specific correctness.
- Producer: creates the concrete artifact.
- Quality Reviewer: runs checks, catches omissions, requests one or two
  correction passes.

These four are not the maximum number of roles. They are the default layers a
task usually needs: planning, production, domain judgment, and quality. A real
task roster may expand one layer into multiple roles, merge layers for a small
task, or add counter-perspective and approval roles when the task needs them.

When the task naturally suggests a familiar workflow, extend the agent
background into concrete roles instead of showing only abstract role names.

Examples:

- Meeting notes:
  - Technical Staff: handles recording, speech-to-text, and basic formatting.
  - Recorder: extracts key points, decisions, action items, and owners.
  - Manager: confirms the meeting record satisfies the user's need.
- Slide or document work:
  - Content Owner: decides message, structure, and examples.
  - Visual Editor: handles layout, readability, and formatting.
  - Reviewer: checks whether the final artifact matches the intended use.
- Data-analysis work:
  - Data Handler: prepares files, cleaning, and reproducible inputs.
  - Analyst: runs the analysis and writes the interpretation.
  - Method Reviewer: checks assumptions, labels, and evidence boundaries.

These concrete roles do not replace the internal coordination model. They are
the user-facing expression of the same team shape in a domain-specific setting.

## User-Named Role Handling

Users may name only a role, rank, or function without defining the role in
detail. Roster should treat that as enough to propose a reasonable responsibility
and workflow position.

Examples:

- `加一個主管`
- `這次需要法務看一下`
- `讓 PM 也確認`
- `加一個助教`
- `需要技術人員處理轉檔`

Expected behavior:

- infer the likely contribution from the role name;
- place the role in the workflow at a sensible point;
- ask for clarification only when the role is ambiguous, high-impact, or likely
  to change approval responsibility;
- let the user correct the inferred responsibility in ordinary language.

Typical inferred positions:

- Manager or supervisor: direction check, decision, final acceptance.
- PM: scope, priority, milestone, handoff tracking.
- Legal or compliance: risk, wording, policy, and pre-release check.
- Technical staff: tools, conversion, environment, data access, recording, or
  automation.
- Recorder or secretary: extract decisions, action items, owners, and durable
  notes.
- Assistant or teaching assistant: learner perspective, examples, and
  comprehension checks.

The point is not just to list the extra role. Roster should reasonably rebalance
the collaboration pattern around the added role.

## Role Perspectives And Task Graph

Context-shaped roles are not just display labels. In a multi-agent setting,
each role should carry an agent perspective that affects how the task is
executed.

For example:

- Manager is not only a sign-off checkbox. The role represents a perspective on
  whether the artifact satisfies the need, is worth delivering, and fits the
  user's goal.
- Technical Staff is not only a preprocessing step. The role represents a
  perspective on feasibility, tool limits, source quality, conversion risk, and
  automation risk.
- Recorder is not only a writing step. The role represents a perspective on
  information extraction, emphasis, ownership, and traceability.

When Roster contextualizes or adds a role, it should infer:

- responsibility: what the role contributes;
- perspective: what the role is watching for;
- workflow position: when the role intervenes;
- authority boundary: whether the role advises, blocks, requests revision, or
  signs off;
- capability implication: which tools, data, plugins, or runtime permissions the
  role may require.

This can change the task graph and the human-facing roster. It can add review
steps, approval gates, revision loops, or capability requests. It must not
change governance ownership:

- Artifact Harness SPEC still owns rule, contract, acceptance, and boundary.
- HR still owns staffing and role design only.
- Team Architect still owns collaboration pattern, task graph, shared
  artifacts, convergence, and CAP generation.
- CAP still owns capability authorization and approval gates only.
- Runtime adapters remain execution layers only.

Working principle:

```text
User-facing roles become agent perspectives in the task graph, not just labels.
Role contextualization changes task execution, not governance ownership.
```

## Agent Work Cards

Expanded roles and members should be convertible into actionable work cards.
The purpose is execution clarity: each visible member should know what it owns,
what it needs, what it produces, when it is done, and where the output goes.

Work cards should not appear in ordinary first-touch replies. They should appear
or be offered when:

- the user asks who does what, asks to expand work, asks for work cards, or asks
  for each agent's responsibility;
- the task moves from planning into implementation;
- risk, authority, review, sign-off, domain, tool, or quality responsibility
  requires owner and completion clarity.

Each work card records:

- role name;
- group;
- responsibility;
- perspective;
- inputs;
- output or deliverable;
- done condition;
- handoff target;
- tool or capability need;
- agent assignment mode;
- open questions.

Agent assignment mode should distinguish:

- separate agent;
- merged role;
- simulated perspective;
- reviewer-only;
- approval-gate candidate.

The assignment mode is Roster's coordination decision. Do not ask the user to
choose it unless the user asks for implementation-design detail.

Important boundaries:

- A work card can become a separate agent, but does not have to.
- One agent can carry several work cards when the task is small.
- Capability need is not capability authorization; CAP still owns tool, plugin,
  approval, and runtime allowlist decisions.
- Approval-gate candidates do not approve or block anything without user or
  policy authority.
- Handoff target is the next receiver, not the full v0.9 role interaction-edge
  model.
- Work cards do not replace Team Operating Packet, CAP, runtime policy,
  verification, approval evidence, or final artifact acceptance.

BCQ_III example:

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

Working principle:

```text
Expanded members become work units before they become runtime agents.
```

## Role Interaction Patterns

After roles are contextualized, groups are expanded, and work cards make each
member actionable, Roster still needs to record how roles work together. This is
the `v0.9.0` layer:

```text
roles -> work cards -> interaction edges
```

Role Interaction Patterns are task-graph edges between roles. They are not
governance owners, tool authorization, runtime execution, approval execution, or
automatic subagent spawning.

Each interaction edge should record:

- source role;
- target role or roles;
- interaction type;
- direction: one-way, two-way, parallel, or loop;
- trigger;
- shared artifact;
- expected output or decision;
- done condition;
- revision or escalation rule;
- authority boundary;
- capability implication;
- fallback owner.

Pattern types:

- `handoff`: one role passes a completed or prepared artifact to another role.
- `dialogue_friction_loop`: a counter-perspective role creates productive
  friction with a primary role before production.
- `peer_alignment`: same-level roles align assumptions, definitions,
  interfaces, or boundaries before handoff.
- `review_challenge`: one role checks another role's output and may request
  revision without blocking by default.
- `approval_signoff`: one role can approve or block the next step only when the
  user or policy grants that authority.
- `parallel_contribution`: multiple roles produce separate parts that later
  integrate.
- `quality_loop`: Quality findings return to the responsible producer or
  upstream owner for correction and recheck.

Boundaries:

- Interaction edges alter task graph behavior, not governance ownership.
- Capability implications are inputs to CAP only; they do not authorize tools,
  plugins, model access, screenshots, OCR, filesystem access, or runtime access.
- Approval signoff blocks only when user wording, policy, or an explicit
  approval boundary grants blocking authority.
- Interaction edges do not automatically spawn subagents.

Common mappings:

- Teacher + Student: `dialogue_friction_loop`.
- Engineering Technical Staff + Financial Technical Staff: `peer_alignment`.
- Producer + Quality Reviewer: `quality_loop`.
- Manager sign-off: `approval_signoff` only when granted.

BCQ_III examples:

- 中醫內容負責人 -> 統計方法人員: `handoff`.
- 統計方法人員 <-> 模型驗證人員: `peer_alignment` or `review_challenge`,
  depending on authority.
- 使用者端產品人員 + 醫師端產品人員: `parallel_contribution` followed by
  integration.
- APP 前端人員 <-> Quality 檢查人員: `quality_loop`.
- 法務與隱私審查人員 -> 專案協調人: `approval_signoff` only if granted.

Meeting notes to executive slides examples:

- 原始內容整理人 -> 會議紀錄人員: `handoff`.
- 會議紀錄人員 <-> 內容一致性檢查人員: `review_challenge`.
- 主管視角整理人 <-> 簡報架構人員: `peer_alignment`.
- 簡報製作人員 <-> 視覺整理人員: `quality_loop`.
- 交付前檢查人員 -> 使用者: `approval_signoff` only if granted.

Ordinary user-facing wording should stay natural:

```text
我會讓會議紀錄先交給簡報企劃，再由 Quality 回頭檢查是否漏掉決議。
```

## Role Splitting And Merging

The same role name does not always mean the same role. Roster should decide
whether a user-named role is one multi-domain perspective or several
collaborating perspectives.

Example: `technical staff` can mean different things in different domains.

Merged role example:

```text
Technical Staff (engineering + finance): handles the data pipeline and tooling,
while checking that technical processing does not distort financial metric
definitions.
```

Use a merged multi-domain role when:

- the task is small or low risk;
- the domains are tightly coupled in one workflow;
- one integrated technical judgment is more useful than two handoffs;
- splitting roles would add coordination cost without improving quality.

Split role example:

```text
- Engineering Technical Staff: handles data flow, tooling, automation, and
  reproducibility.
- Financial Technical Staff: checks financial indicators, assumptions,
  interpretation, and risk boundaries.
```

Collaboration pattern:

```text
Engineering Technical Staff builds the data and computation path.
Financial Technical Staff reviews metric definitions and interpretation.
If the financial definition changes, Engineering Technical Staff revises the
pipeline before final review.
```

Split roles when:

- the domains use different judgment standards;
- one role should review or challenge the other;
- the task is high risk or domain confusion would create a real error;
- one role owning both sides would create a conflict of interest;
- independent acceptance or sign-off is needed.

If uncertain, Roster should propose the split as perspectives, not as fixed
headcount:

```text
我會先把「技術人員」拆成工程技術和金融技術兩個視角來跑；
如果你想合併成一個角色，也可以直接說。
```

Roster should distinguish three common cases:

1. Domain extension:
   - The user adds a domain to an existing role.
   - Example: `技術人員加入金融 domain`.
   - Default behavior: keep one role with a multi-domain perspective.
   - Do not add a new agent or approval gate by default.
2. Peer domain role:
   - The user adds a new person or agent at the same level as an existing role.
   - Example: `新增一位金融技術人員，跟原本技術人員同級`.
   - Default behavior: add a peer role and an alignment step.
   - Do not treat the new peer as a reviewer or approver unless the user says so.
3. Reviewer or approver domain role:
   - The user gives the new role review, blocking, approval, or sign-off
     authority.
   - Example: `金融技術人員要核准模型結果才能交付`.
   - Default behavior: add a review or approval gate and update the task graph.

Peer role pattern:

```text
Engineering Technical Staff + Financial Technical Staff
-> alignment on technical processing and domain definitions
-> Producer / Recorder
-> Manager or Quality review
```

Peer domain roles increase coordination cost, but not necessarily governance
weight. They add an alignment step by default; they become approval gates only
when the user gives them approval authority or the risk requires explicit gate
tracking.

## Counter-Perspective Roles

Some added roles are not peers, reviewers, or approvers. They are
counter-perspective roles that create productive friction with a primary role.

Abstract rule:

- Counter-perspective roles represent audience, learner, stakeholder,
  edge-case, or opposing-domain viewpoints.
- They usually create a dialogue or revision loop before production.
- They are advisory or revision-triggering by default, not approval gates.
- They should not replace the final quality or acceptance role.

Short example:

```text
Adding a student perspective to a teaching-video task helps challenge whether
the teacher's explanation is understandable before production begins.
```

Non-normative example detail:

Educational video production can start with three roles:

- Teacher: owns concepts, teaching sequence, and example correctness.
- Video Production: owns visuals, pacing, editing, and output.
- Quality Management: owns playback checks, readability, and final correction
  requests.

Adding `Student` is not just adding a lower-rank reviewer. In this example,
Student represents the learner's comprehension load:

- challenges whether the teacher's explanation is too abstract or too complex;
- points out unclear steps, fast pacing, missing examples, or confusing terms;
- triggers teacher revision before video production;
- does not replace Quality Management or final acceptance.

The task graph should model dialogue, not one-way approval:

```text
Teacher <-> Student concept-friction loop
-> Teacher revises explanation
-> Video Production
-> Quality Management
```

Roster should infer this pattern when a role is added to create contrast,
audience perspective, critique, or comprehension pressure.

Characteristics:

- Role type: counter-perspective role.
- Purpose: productive friction before production.
- Authority: advisory or revision-triggering, not final approval by default.
- Task graph effect: adds a dialogue loop with the primary content role.

This detailed example is meant to preserve the design intent for future
implementation. It should not make educational video the default Roster domain.
The general capability is counter-perspective modeling.

For visual, slide, video, UI, or document-layout tasks, the Quality Reviewer
should request visual evidence when available and should flag occlusion,
readability, overlap, missing content, and mismatch between intended and actual
output.

## Collaboration Pattern

Default collaboration should be:

```text
Planner -> Producer -> Domain Reviewer + Quality Reviewer -> Producer revision -> final check
```

For small tasks, collapse roles into a single pass and do not show the full
team preview unless useful.

For larger tasks, the preview can become a saved roster or packet-backed plan.

## Roles As Layers, Not Fixed Slots

The original four-role shape should be treated as a compact layer model:

- Planning layer: defines goal, scope, sequence, and handoff.
- Production layer: creates or edits the artifact.
- Domain judgment layer: checks meaning, assumptions, correctness, and audience
  fit.
- Quality layer: checks finished artifact quality, omissions, evidence, and
  revision needs.

Roster can expand, merge, or specialize these layers:

- expand one layer into several roles when domains or perspectives differ;
- merge layers when the task is small and coordination cost would outweigh
  benefit;
- add peer roles when same-level domains must align;
- add counter-perspective roles when productive friction is needed;
- add approval roles when the user or risk requires explicit sign-off;
- preserve Quality as a real check rather than just a label.

This means the next version should not hard-code "four agents" as the team
model. It should treat the four-role shape as a default compression of the
larger roster logic.

This layer model should not force Roster into a linear coordination pattern.
The layers define coverage requirements, not topology:

- Layers: what kinds of work must be covered.
- Coordination pattern: how those layers interact.
- Role interaction pattern: the local edge between roles.
- Agent instance: the execution resource that performs one or more roles,
  perspectives, or layers.

Examples:

- In `generator-verifier`, the production layer generates, the domain judgment
  and quality layers verify, and failed checks loop back to production.
- In `orchestrator-subagent`, the planning layer can stay with the orchestrator
  while production, domain judgment, or quality checks become bounded subtasks.
- In `agent teams`, different slices can each carry their own production and
  quality loops before integration.
- In `shared-state`, layers may contribute evidence, notes, and decisions to a
  shared artifact with explicit ownership and merge rules.
- In `message bus`, layers may emit and react to events such as `draft_ready`,
  `review_needed`, `quality_failed`, or `approval_required`.

Working principle:

```text
Layers are coverage requirements.
Coordination patterns are topology.
Role interaction patterns are edges.
Agent instances are execution resources.
```

## Perspective Separation And Subagents

The goal is not to spawn more agents for its own sake. The goal is to activate
multiple reasoning perspectives so the model's native strengths can cover the
weaknesses of a single-pass agent.

Single-agent failure modes Roster should compensate for:

- jumping into production before clarifying goal, boundary, or acceptance;
- trusting its own output too quickly;
- leaving domain assumptions unchallenged;
- treating quality review as a formality;
- missing the user's, reader's, learner's, manager's, legal, technical, or
  other stakeholder perspective;
- delivering without a recheck.

Roster should force perspective separation and layer coverage. Subagents are an
optional execution resource for making that separation stronger when the runtime
supports it.

Contract:

1. Every Roster task should cover the layers, even if execution stays
   single-agent.
2. Every non-trivial task should separate production from review at least as
   explicit reasoning passes.
3. High-risk or multi-domain tasks should separate domain perspectives.
4. Counter-perspective roles should be used when expert blind spots are likely.
5. Subagents are preferred when runtime support exists and separation improves
   quality more than it adds coordination cost.
6. If subagents are unavailable or too costly, Roster should simulate separated
   perspectives explicitly in one agent.

Working principle:

```text
Force perspective separation; use subagents when useful.
```

## Team Architect Layer Detail

Current Roster already has a macro coordination layer through Team Architect.
Team Architect owns the collaboration pattern, task graph, shared artifacts,
convergence, and CAP generation. That layer should remain the place where a
team list becomes an operating method.

What is missing for the next version is a smaller layer inside the Team
Architect task graph: role-to-role interaction edges. These are micro
coordination patterns. They describe how two or more roles interact after the
overall collaboration pattern is chosen.

Macro coordination pattern answers:

- Is this generator-verifier, orchestrator-subagent, agent team, shared-state,
  or another approved pattern?
- Where is the main production path?
- What are the convergence and stop conditions?
- What shared artifacts exist?
- What capability access or runtime mapping is needed?

Role interaction pattern answers:

- Does Role A hand off to Role B?
- Do two roles align as peers before production?
- Does one role challenge another before production?
- Does one role review and request revisions?
- Does one role approve or block the next step when authority was granted?
- Do several roles contribute in parallel and then integrate?
- Does Quality loop back to the producer or to an earlier role?

This layer should be represented in the Team Operating Packet as part of the
task graph, interaction protocol, shared artifact ownership, and convergence
rules. It should not create a new governance owner.

## Role Interaction Patterns

Role Interaction Patterns are the micro-coordination edges between roles inside
a larger Team Architect collaboration pattern. They are how Roster moves from
"a list of roles" to "a team that knows how to work together."

They should capture:

- participating roles;
- interaction type;
- directionality: one-way, two-way, parallel, or loop;
- trigger: when the interaction starts;
- expected artifact or decision;
- revision or escalation behavior;
- authority level: advise, revise, challenge, approve, or block;
- capability implication when the interaction needs tools or data access.

Suggested vocabulary:

- `handoff`: one role completes a step and passes the artifact to another.
- `dialogue_friction_loop`: roles iterate to resolve comprehension, framing, or
  conceptual tension before production.
- `peer_alignment`: same-level roles align domain assumptions or technical
  definitions before handoff.
- `review_challenge`: one role reviews another role's output and may request
  revision, without final approval authority by default.
- `approval_signoff`: a role can approve or block the next step only when the
  user or policy grants that authority.
- `parallel_contribution`: roles produce separate parts that later integrate.
- `quality_loop`: quality findings return to the responsible producer or
  upstream role for correction.

Pattern details:

- `handoff`
  - Direction: one-way.
  - Use when one role prepares material for another.
  - Example: Technical Staff -> Recorder.
- `dialogue_friction_loop`
  - Direction: two-way loop.
  - Use when a counter-perspective role should create productive friction before
    production.
  - Example: Teacher <-> Student.
- `peer_alignment`
  - Direction: peer-to-peer.
  - Use when same-level roles must align assumptions, definitions, or technical
    choices before handoff.
  - Example: Engineering Technical Staff + Financial Technical Staff.
- `review_challenge`
  - Direction: reviewer to producer, with possible revision.
  - Use when one role checks another role's output but does not hold final
    sign-off by default.
- `approval_signoff`
  - Direction: producer to approver, with blocking authority only when granted.
  - Use only when the user, task policy, or explicit approval boundary gives
    sign-off authority. If authority is not granted, record reviewer-only advice
    or `review_challenge` instead.
- `parallel_contribution`
  - Direction: parallel branches into integration.
  - Use when roles produce separate components that must be combined.
- `quality_loop`
  - Direction: quality finding -> responsible role -> recheck.
  - Use when artifact quality requires concrete correction and re-inspection.

Example mappings:

- Teacher + Student: `dialogue_friction_loop`.
- Engineering Technical Staff + Financial Technical Staff:
  `peer_alignment`.
- Technical Staff -> Recorder: `handoff`.
- Producer -> Quality Reviewer -> Producer: `quality_loop`.
- Producer -> Manager: `approval_signoff` only when the user gives the manager
  sign-off authority.

Working principle:

```text
Team Architect selects the macro coordination pattern.
Roster role contextualization supplies role interaction edges.
The Team Operating Packet records both without changing governance ownership.
```

## Relationship To Existing Roster Internals

The internal model remains unchanged:

- Artifact Harness SPEC owns rule, contract, acceptance, and boundary.
- HR owns staffing and role design only.
- Team Architect owns collaboration pattern, task graph, shared artifacts,
  convergence, and CAP generation.
- CAP owns capability authorization and approval gates only.
- Runtime adapters remain execution layers only.

The next UX improvement is presentation and invocation behavior, not ownership
redesign.

## External Inspiration: gstack

Reference: `https://github.com/garrytan/gstack`

`gstack` is useful as a nearby reference because it presents AI-assisted work
as a virtual team with named roles and slash-command workflows. It is not only
a tool list; it frames the workflow as a process for planning, building,
reviewing, QA, shipping, and reflecting.

Observed overlap with Roster:

- Both are role-based work systems rather than single-agent helpers.
- Both benefit from CLI-native or slash-command invocation.
- Both make planning, review, QA, and execution feel like a coordinated team.
- Both should reduce how much process detail the user has to remember.
- Both point away from "copilot" framing and toward "team" framing.

Important difference:

- `gstack` is closer to an opinionated software factory: CEO, engineer,
  designer, reviewer, QA, release, and deployment flows.
- Roster should stay more focused: project staffing, artifact-quality
  coordination, task boundary, capability access, and same-folder packet
  continuity.
- `gstack` is stronger as a first-touch UX and slash-command ecology reference.
- Roster is stronger where governance boundaries, Capability Access Packet,
  runtime mapping, and artifact traceability matter.

Reference boundary:

```text
Use gstack as a UX and packaging reference, not as a role taxonomy or
architecture template.
```

Roster should not copy a fixed executive/product/engineering/design/release
team. Its differentiator should be role synthesis:

```text
task -> layers -> context-shaped roles -> interaction edges -> optional subagents
```

In other words, `gstack` shows that users understand agent systems more easily
when they can see a team and invoke it naturally. Roster should translate that
lesson into its own model: a small coordination surface that infers, compresses,
or expands roles from the user's task instead of installing one fixed software
factory.

Borrowable directions for Roster:

1. Make the README first screen more product-like. Lead with what Roster does
   for a messy task: form a working team, quality loop, and execution boundary.
2. Keep a small number of memorable invocation paths instead of many commands:
   `/roster`, `/roster quality`, `/roster remember`, and `/roster health` are
   enough as a mental model if they map cleanly to existing internals.
3. Consider a team/repo mode later. Personal install should stay
   `roster-install`; project-local setup could become `roster-init` or
   `roster-install --team` if it writes only lightweight repo guidance, health
   checks, and packet conventions.

Do not copy `gstack` by expanding Roster into a full software factory. Treat it
as UX evidence that people understand agent systems more easily when they can
see a team, choose a simple entrypoint, and let the tool handle coordination.

## Candidate Version Theme

Candidate theme for the next version:

```text
Roster proposes the team, the user adjusts the team, then Roster coordinates the work.
```

Possible feature names:

- Team preview
- Roster preview
- Working team proposal
- Confirm-or-adjust team shape

## Candidate Git Version Split

Current released baseline: `v0.6.0`.

The next work should be split into small Git releases so Roster does not absorb
all role, layer, interaction, and subagent ideas in one jump.

### v0.7.0: First-Touch UX Contract

Goal:

- Make ordinary Roster replies feel natural and role-shaped.
- Add the four complexity levels as response behavior.
- Keep changes mostly in skill, slash command, README, and usage docs.

Should include:

- first-touch response contract;
- natural Traditional Chinese examples for meeting-note tasks;
- no internal governance leakage in ordinary replies;
- visible but lightweight complexity handling;
- user role adjustment phrasing such as `加一個主管` or `讓 PM 看一下`.

Should not include:

- full role interaction engine;
- new packet schema;
- automatic subagent spawning.

### v0.8.0: Role Contextualization Model

Goal:

- Teach Roster to treat roles as context-shaped responsibilities, not fixed
  labels.
- Add the role / perspective / layer distinction to docs, templates, and route
  evidence where useful.

Should include:

- role contextualization guidance;
- user-named role handling;
- domain extension vs peer domain role vs reviewer/approver role;
- roles as layers, not fixed slots;
- tests or examples showing that added roles adjust the team shape without
  always becoming new agents.

Should not include:

- full runtime-level delegation;
- broad rewrite of Team Architect.

### v0.9.0: Role Interaction Patterns

Goal:

- Add micro-coordination edges to the Team Architect layer.
- Let Team Operating Packet record how roles interact, not just which roles
  exist.

Should include:

- Role Interaction Patterns vocabulary:
  `handoff`, `dialogue_friction_loop`, `peer_alignment`, `review_challenge`,
  `approval_signoff`, `parallel_contribution`, `quality_loop`;
- Team Operating Packet fields or fill notes for role interaction edges;
- examples for Teacher + Student, Engineering Technical Staff + Financial
  Technical Staff, Producer + Quality Reviewer, and Manager sign-off;
- clear boundary that interaction edges alter task graph behavior, not
  governance ownership.

Should not include:

- new persistent runtime service;
- message bus implementation;
- automatic approval execution beyond existing approval evidence.

### v0.10.0: Capability-Aware Role Execution

Goal:

- Let Roster plan which LLM platform capabilities each role needs to complete
  its work.
- Keep subagents as one capability inside the broader execution plan, not the
  whole milestone.

Should include:

- `role -> work -> interaction -> capability need -> availability -> fallback`;
- capability categories such as web search, browser, filesystem read/write,
  code execution, visual capture, vision review, specialist skill,
  plugin/connector, and subagent execution;
- work-card fields or fill notes for capability needs, evidence expected,
  availability, and fallback;
- first-touch behavior that keeps tool mechanics quiet unless useful or asked;
- health or capability reporting for whether important platform capabilities
  are known, available, unavailable, or approval-bound where practical;
- subagent policy as a subsection:
  use subagents when separation improves quality more than it adds coordination
  cost, otherwise simulate separated perspectives in one agent.

Should not include:

- new web-search adapter shipped inside Roster;
- automatic connector login or external actions;
- replacing CAP with Roster;
- forcing every role into a separate agent;
- Rust rewrite or new runtime architecture.

Direction note:

- `ROSTER_V0_10_CAPABILITY_AWARE_ROLE_EXECUTION.md`

### v0.11.0: Project/Team Mode Candidate

Goal:

- Explore repo-local Roster setup inspired by team-mode ideas.
- Keep it lightweight and same-folder.

Should include:

- candidate `roster-init` or `roster-install --team`;
- project-local Roster guidance;
- packet convention and health-check wiring for a target workspace;
- no persistent server, daemon, database, or separate orchestration UI.

Should not include:

- making Roster a full software factory;
- replacing existing Codex/Claude host behavior.

### v1.0.0: Stable Public Contract

Goal:

- Promote only after first-touch UX, role contextualization, interaction edges,
  install/uninstall, health, and same-folder packet behavior are stable.

Release bar:

- public README matches actual behavior;
- install/uninstall works across a fresh machine path;
- `@roster` / `/roster` support is documented truthfully for supported hosts;
- role layers and role interaction patterns are covered by examples and tests;
- no major governance boundary ambiguity remains.

## Open Questions

- Should team preview appear every time, or only for first use / ambiguous
  multi-role tasks?
- Should `Roster, use the usual team` skip the preview?
- Should saved preferences influence the default team shape?
- Should `/roster` support a subcommand-like phrasing such as `/roster team`,
  `/roster quality`, or `/roster remember`, or should these stay natural
  language only?
