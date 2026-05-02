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

### v0.10.0: Perspective Separation And Subagent Policy

Goal:

- Make perspective separation a Roster execution contract.
- Use subagents only when useful and runtime-supported.

User-facing behavior:

- The user does not need to ask for subagents.
- Roster's reply should make the chosen handling mode feel natural.
- Roster should not announce internal subagent details unless useful or asked.

Internal behavior:

- Force layer coverage and perspective separation.
- Prefer subagents only when separation improves quality more than it adds
  coordination cost.
- If subagents are unavailable or too costly, simulate separated perspectives
  explicitly in one agent.

In scope:

- subagent policy in skill/command docs
- runtime capability reporting where practical
- examples for Level 1 single-agent full-layer pass and Level 3 expanded
  specialist roster

Out of scope:

- forcing every role into a separate agent
- Rust rewrite
- new runtime architecture

Acceptance signal:

- Docs state: `Force perspective separation; use subagents when useful.`
- Health or capability reporting can tell whether current runtime support is
  known, unknown, or unavailable.

Risk:

- Runtime-specific behavior can drift across Codex, Claude, and other hosts.

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
