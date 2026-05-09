# Roster Milestone Roadmap

Date: `2026-05-02`
Baseline release: `v0.6.0`
Status: `planning roadmap`

## Purpose

This roadmap turns the next-version direction into release-sized milestones.
It is intentionally less detailed than an implementation spec. Only the next
release should receive a full developer prompt before implementation.

Guiding rule:

```text
Roadmap broadly; spec narrowly.
```

## Release Sequence

### v0.7.0: First-Touch UX Contract

Goal:

- Make ordinary Roster invocation feel natural, short, and role-shaped.
- Add first-touch complexity behavior without exposing internal level labels.

User-facing behavior:

- Roster answers with the smallest useful amount of team structure.
- Simple tasks get a direct "I will handle and self-check" response.
- Clear medium tasks get a compact team preview with familiar role names.
- Larger tasks get grouped roles.
- Ambiguous or high-authority tasks get a short agent-led team-design exchange.

Internal behavior:

- Roster makes an initial complexity call.
- Roster keeps layer coverage active even when execution is single-agent.
- Roster does not expose Artifact Harness, HR, Team Architect, CAP, runtime, or
  packet-chain terms in ordinary first-touch responses.

In scope:

- `skills/roster/SKILL.md`
- `plugins/roster/commands/roster.md`
- `README.md`
- usage-experience docs
- tests or text audits for first-touch examples

Out of scope:

- full role interaction engine
- Team Operating Packet schema changes
- automatic subagent spawning
- new runtime adapter behavior

Acceptance signal:

- First-touch examples are short, concrete, and human-facing.
- Meeting-note example uses natural Traditional Chinese role names such as
  `轉錄人員`, `會議紀錄人員`, and `會議負責人`.
- Complexity is visible through plain phrasing, not labels like `Level 2`.
- Public docs and skill docs do not overclaim UI or subagent behavior.

Risk:

- Overexplaining the team preview could make Roster feel heavier than direct
  assistant use.

### v0.8.0: Role Contextualization Model

Goal:

- Treat roles as context-shaped responsibilities and perspectives, not fixed
  labels.

User-facing behavior:

- The user can add roles by title, rank, function, or shorthand.
- Roster infers a likely responsibility and workflow position.
- Roster asks for clarification only when ambiguity, authority, or risk makes
  guessing unsafe.

Internal behavior:

- Roster distinguishes role, perspective, layer, and agent instance.
- Roster distinguishes domain extension, peer domain role, and reviewer or
  approver role.
- Added roles can adjust the task graph without automatically becoming new
  agents.

In scope:

- role contextualization guidance
- user-named role handling
- examples and tests for role additions
- docs/templates where the distinction matters

Out of scope:

- broad Team Architect rewrite
- full subagent policy implementation
- persistent role database

Acceptance signal:

- Examples show role additions such as `加一個主管`, `讓 PM 看一下`,
  `新增金融技術人員`, and `加一個學生視角`.
- Roster can explain whether it merged, split, or aligned roles.

Risk:

- Role inference can overstep if authority or approval boundaries are not
  clearly separated.

### v0.8.1: Group Expansion UX Patch

Goal:

- Let broad multi-group plans expand into concrete group members when useful,
  without overloading first-touch replies.

User-facing behavior:

- First touch shows group-level structure for broad tasks.
- When the user asks to expand, or the task moves into implementation planning,
  Roster can list group members with short responsibilities, perspectives, and
  deliverables.
- Roster states that expanded members do not automatically become separate
  agents.

Internal behavior:

- Group expansion reuses the v0.8.0 role contextualization model.
- Expansion stays below the full role interaction-edge model.

Acceptance signal:

- BCQ_III-style examples can show a group preview first, then expand each group
  into members.
- Added roles can be placed into an existing group, promoted to a peer role, or
  treated as reviewer/approver when authority is explicit.

Risk:

- Expanded lists can become decorative if members do not carry executable work.

### v0.8.2: Agent Work Card Contract

Goal:

- Make expanded roles and members actionable work units rather than display-only
  roster labels.

User-facing behavior:

- Ordinary first-touch replies stay short.
- When the user asks who does what, asks for implementation planning, or the
  task is high risk, Roster can expand members into compact work cards.
- Work cards make clear what each agent or simulated perspective needs, produces,
  and hands off.

Internal behavior:

- Each work card records role name, group, responsibility, perspective, input,
  output, done condition, handoff target, capability need, assignment mode, and
  open questions.
- Assignment mode distinguishes separate agent, merged role, simulated
  perspective, reviewer-only, and approval-gate candidate.
- Capability need is only a need signal; CAP still authorizes tools, plugins,
  approvals, and runtime allowlists.
- Approval-gate candidates do not approve anything by themselves.
- Handoff target is a next receiver, not the full v0.9 role interaction-edge
  model.

Acceptance signal:

- A BCQ_III statistics member can be turned into a work card with a concrete
  scoring-spec deliverable, completion condition, handoff target, and capability
  need.
- Docs do not imply every work card spawns a separate subagent.
- Docs do not treat work cards as full v0.9 role interaction edges.

Risk:

- Too much work-card detail can make Roster feel heavy if shown before the user
  asks for planning depth.

### v0.9.0: Role Interaction Patterns

Goal:

- Define role-to-role interaction edges inside the Team Architect task graph.

User-facing behavior:

- Roster can explain how roles interact without exposing internal governance.
- Examples make it clear when a role is handoff, peer alignment, friction loop,
  review, approval, parallel contribution, or quality loop.

Internal behavior:

- Team Operating Packet records interaction edges.
- Role interaction edges alter task graph behavior, not governance ownership.
- Work-card `handoff_target` remains a next receiver; interaction edges record
  direction, shared artifact, authority boundary, revision/escalation, and
  fallback behavior.
- Capability implications from edges are CAP inputs only, not authorization.

In scope:

- Role Interaction Patterns vocabulary:
  - `handoff`
  - `dialogue_friction_loop`
  - `peer_alignment`
  - `review_challenge`
  - `approval_signoff`
  - `parallel_contribution`
  - `quality_loop`
- Team Operating Packet fields or fill notes
- examples and text audits

Out of scope:

- message bus implementation
- new persistent runtime service
- automatic approval execution beyond existing approval evidence

Acceptance signal:

- Team Operating Packet can distinguish role list from interaction edges.
- Teacher + Student maps to `dialogue_friction_loop`.
- Engineering Technical Staff + Financial Technical Staff maps to
  `peer_alignment`.
- Producer + Quality maps to `quality_loop`.

Risk:

- Too much vocabulary can leak into user-facing replies if not constrained.

Packet:

- `contexts/task_runs/roster-v0_9-role-interaction-patterns-2026-05-02/`
- `contexts/artifact_harness_usage_experience/developer_reports/prompt_v0_9_role_interaction_patterns.prompt.md`

### v0.10.0: Capability-Aware Role Execution

Goal:

- Plan each role not only by responsibility and interaction, but also by the
  LLM host capabilities it needs to do the work.
- Treat subagents as one possible capability, not the whole milestone.

User-facing behavior:

- The user does not need to manually decide which role should use web search,
  browser, screenshot/CV, filesystem/code execution, specialist skills,
  plugins, or subagents.
- Roster's reply should make capability use feel like part of the team doing
  its job.
- Roster should not expose capability matrices, CAP, runtime, or subagent
  details unless useful or asked.

Internal behavior:

- Extend role/work-card planning with capability needs, availability state,
  evidence expected, and fallback.
- Use the chain:
  `role -> work -> interaction -> capability need -> availability -> fallback`.
- Keep perspective separation active even when one agent simulates several
  roles.
- Use subagents only when runtime support exists and separation improves quality
  more than it adds coordination cost.

In scope:

- capability-aware role execution docs
- work-card capability fields or fill notes
- capability vocabulary for web, browser, visual capture, vision review,
  filesystem/code execution, specialist skills, plugins/connectors, and
  subagent execution
- runtime capability reporting where practical
- examples for Research Reviewer, Visual QA, Slide Producer, Skill Reviewer,
  and Statistical Reviewer
- subagent policy as a subsection

Out of scope:

- forcing every role into a separate agent
- shipping a new web-search adapter inside Roster
- automatic connector login or external actions
- Rust rewrite
- new runtime architecture

Acceptance signal:

- Docs state: `Roster plans capability needs; CAP authorizes access; runtime
  executes.`
- Work cards can express needed platform capabilities and fallback behavior.
- Health or capability reporting can tell whether important capability classes
  are known, available, unavailable, or require approval where practical.
- Subagents are described as conditional capability use, not as the default for
  every role.

Risk:

- Runtime-specific behavior can drift across Codex, Claude, and other hosts.
- Roster could overexpose tool mechanics in ordinary user replies if the first
  touch contract is not preserved.

Direction note:

- `contexts/artifact_harness_usage_experience/ROSTER_V0_10_CAPABILITY_AWARE_ROLE_EXECUTION.md`

### v0.11.0: Project/Team Mode Candidate

Goal:

- Explore repo-local Roster setup for a target project.

User-facing behavior:

- A project can carry lightweight Roster usage guidance and health checks.
- The user does not need a persistent server or separate orchestration UI.

Internal behavior:

- Roster can write project-local guidance, packet conventions, and health
  wiring when explicitly requested.

In scope:

- candidate `roster-init` or `roster-install --team`
- project-local Roster guide
- same-folder packet conventions
- health check integration

Out of scope:

- full software factory behavior
- replacing Codex or Claude host behavior
- long-running service

Acceptance signal:

- A fresh workspace can be initialized with Roster guidance and verified with a
  health check.

Risk:

- Team mode could overreach if it writes too much into target projects.

### v0.11.1: Role Execution Receipt

Goal:

- Let users judge whether declared Roster roles actually did work after a
  non-trivial task is completed.
- Preserve the short first-touch UX while adding lightweight role-action
  evidence to ordinary completion replies.
- Keep later response style aligned with Roster's agent-coordination identity:
  outcome, role actions, and convergence.

User-facing behavior:

- First-touch replies stay short and natural.
- Ordinary completion replies include a compact `本次分工執行` section when
  multiple meaningful roles or perspectives contributed.
- Each listed role says what it checked, produced, compared, or decided.
- Later replies should not collapse into generic single-agent summaries when a
  multi-role task was declared.
- Full capability/source/assumption traces appear only in review, debug, or
  verification mode.

Internal behavior:

- Distinguish role execution evidence from runtime execution.
- Do not imply separate subagents were spawned unless they actually were.
- If work was performed as simulated perspectives inside one coordinating
  agent, say so when the user asks for multi-agent evidence.
- Surface missing web, browser, CV, plugin, connector, or subagent capability
  when a role needed it and could not use it.

In scope:

- Roster response contract docs.
- Skill and README guidance for role-action summaries.
- Examples that show `who did what` without exposing internal packet chain
  terms.
- Review/debug trace guidance for capability, source, assumptions, and runtime
  execution mode.

Out of scope:

- forcing every role into a separate runtime agent;
- building a new message bus;
- making ordinary replies into full audit logs;
- replacing the Artifact Harness, Team Architect, CAP, runtime, or verification
  boundaries.

Acceptance signal:

- Users can tell whether a named role was real work or just a label.
- Ordinary completion replies stay readable.
- First-touch replies do not get heavier.
- Review/debug mode can expand to role, capability, source, and assumption
  traces.

Direction note:

- `contexts/artifact_harness_usage_experience/ROSTER_V0_11_1_ROLE_EXECUTION_RECEIPT.md`

### v0.11.2: Receipt Trigger Clarification

Goal:

- Tighten the `v0.11.1` receipt contract so Roster does not omit
  `本次分工執行` when the user says not to expand debug trace.
- Prevent Roster from treating role-action receipt only as a future product
  feature when the current answer itself used multiple roles or perspectives.

User-facing behavior:

- `本次分工執行` is ordinary completion evidence, not debug trace.
- If a non-trivial task uses multiple roles, perspectives, or quality checks,
  include a short receipt even when debug trace is suppressed.
- If the task discusses a future role-summary feature, still include a
  current-turn receipt for the answer itself.
- Simpler tasks may use shorter receipts, but qualifying tasks should not drop
  the receipt entirely.

Internal behavior:

- Before finalizing a non-trivial completion reply, check whether more than one
  role, perspective, or quality check contributed.
- Treat `do not expand debug trace` as a request to suppress full trace, not a
  request to suppress role-action receipt.
- Keep receipts lightweight and separate from capability/source/assumption
  traces.

In scope:

- Roster response-contract docs.
- Skill and README wording that distinguishes ordinary receipt from debug trace.
- Examples using the observed two-week product plan failure pattern.

Out of scope:

- runtime enforcement;
- new subagent behavior;
- debug/source/capability trace UI;
- install, health, or slash invocation behavior changes.

Acceptance signal:

- A two-week product plan with UX, engineering, priority, and quality judgment
  includes a short `本次分工執行`.
- The receipt remains present when the user asks not to expand debug trace.
- Role-summary can be discussed as a future feature, but the current answer also
  shows current-turn role actions.
- First-touch replies remain unaffected.

Direction note:

- `contexts/artifact_harness_usage_experience/ROSTER_V0_11_2_RECEIPT_TRIGGER_CLARIFICATION.md`

### v0.11.3: Invocation Response Wrapper

Goal:

- Ensure explicit Roster invocation produces Roster-shaped work instead of a
  generic assistant answer.
- Add a lightweight response wrapper for non-trivial Roster tasks:
  `entry framing -> useful work -> role-action receipt -> convergence`.

User-facing behavior:

- When the user invokes `Roster，...`, `/roster`, or `@roster` for a
  non-trivial task, the answer starts with a compact work frame such as
  `我先用產品、工程、品質三個視角...`.
- The useful artifact, plan, review, or decision still comes first; users should
  not need to read internal governance before the answer.
- Qualifying tasks still include `本次分工執行`.
- The closeout should end with convergence, not only a generic suggested next
  prompt.
- `不要展開 debug trace` keeps the wrapper short but does not remove it.

Internal behavior:

- Treat explicit Roster invocation as a mode trigger for response style.
- Compress the wrapper for smaller tasks instead of removing it.
- Distinguish entry framing from full first-touch team explanation.
- Do not expose internal packet, control-plane, CAP, or runtime details in
  ordinary replies.

In scope:

- Roster response-contract docs.
- Skill/plugin/README wording for explicit invocation behavior.
- Examples based on the dashboard/product-plan failure pattern.
- Good and bad examples for next-prompt substitution versus convergence.

Out of scope:

- runtime enforcement;
- new subagent behavior;
- slash routing behavior changes;
- install or health behavior changes;
- making every Roster reply long.

Acceptance signal:

- A fresh-thread non-trivial `Roster，...` prompt starts with compact
  role/perspective framing.
- The answer includes useful output plus `本次分工執行` when multiple
  perspectives contributed.
- The answer ends with a convergence line instead of only a suggested next
  command.
- First-touch remains short and does not leak internal governance.

Direction note:

- `contexts/artifact_harness_usage_experience/ROSTER_V0_11_3_INVOCATION_RESPONSE_WRAPPER.md`

### v0.11.4: Stable Team Status Receipt

Goal:

- Make Roster's team state visible even when the user prompt is vague.
- Require explicit agent count and workflow state for non-trivial Roster
  invocation.
- Preserve useful artifact/planning output while making it clear how many agents
  or role-agents were used.

User-facing behavior:

- A qualifying `Roster，...`, `/roster`, or `@roster` answer starts with a
  compact status line such as:
  `本次啟用：5 個 role-agents（使用者研究、客服分析、產品排序、工程評估、品質驗收；單一回覆中分工處理）`.
- If only one agent is needed, Roster still says so:
  `本次啟用：1 個 agent（單一整合流程）`.
- The response declares current workflow stage, especially when the final
  artifact is not produced yet:
  `目前階段：初步規劃；正式 artifact 這輪先不產出。`
- `本次分工執行` remains concrete: role actions, not only role names or
  perspectives.

Internal behavior:

- Agent count is inferred by Roster; the user should not need to specify team
  size.
- Small tasks can stay one-agent, but still show the one-agent workflow when
  Roster is explicitly invoked.
- Do not claim parallel runtime execution unless actual subagents were used.
- Do not inflate agent count just to make Roster look more complex.

In scope:

- Roster response-contract docs.
- Examples for fuzzy planning prompts with explicit future artifact scope.
- One-agent workflow examples.
- Good and bad examples for agent count and workflow stage visibility.

Out of scope:

- runtime enforcement;
- required subagent spawning;
- install, health, slash, or plugin behavior changes;
- fixed team-size rules;
- exposing packet, CAP, control-plane, or runtime details in ordinary replies.

Acceptance signal:

- Fuzzy Roster planning prompts declare active agent count.
- One-agent Roster answers declare a one-agent workflow.
- Artifact planning answers distinguish current stage from capability limit.
- The answer still leads with useful work and ends with convergence.

Direction note:

- `contexts/artifact_harness_usage_experience/ROSTER_V0_11_4_STABLE_TEAM_STATUS_RECEIPT.md`

### v1.0.0: Stable Public Contract

Goal:

- Promote Roster after first-touch UX, role contextualization, interaction
  edges, install/uninstall, health, and same-folder packet behavior are stable.

Release bar:

- public README matches actual behavior;
- install/uninstall works across a fresh machine path;
- `@roster` and `/roster` support is documented truthfully for supported hosts;
- role layers and interaction patterns are covered by examples and tests;
- same-folder packet behavior remains reliable;
- no major governance boundary ambiguity remains.

## Sequencing Notes

- Implement `v0.7.0` first and review with real user-facing examples.
- Do not write detailed implementation prompts for `v0.8.0+` until `v0.7.0`
  has been reviewed.
- If `v0.7.0` shows that first-touch UX is still too heavy, adjust the roadmap
  before implementing deeper role logic.
