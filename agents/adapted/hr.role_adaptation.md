# Role Adaptation Draft

## Metadata

- Owner: Codex
- Status: adapted to native team surface
- Version: v0.5
- Updated at: 2026-04-20

## Source

- Upstream repo: `msitarzewski/agency-agents`
- Upstream commit: `783f6a72bfd7f3135700ac273c619d92821b419a`
- Upstream file:
  - `references/third_party/agency-agents/specialized/recruitment-specialist.md`
  - `references/third_party/agency-agents/specialized/hr-onboarding.md`
  - `references/third_party/agency-agents/specialized/corporate-training-designer.md`
- Local draft path: `agents/native/hr.md`
- Canonical team surface path: `teams/human-resources/AGENTS.md`

## Role Core

- Local role name: `Human Resources`
- One-line mission: design the multi-agent team, find or adapt the right roles, and create missing roles when needed
- Local modeling decision:
  - no longer treated as one compressed role
  - promoted into one team surface with internal member roles
- Team composition:
  - `HR Director`
  - `Role Scout`
  - `Role Architect`
- In scope:
  - team-shape and role-gap definition for multi-agent work
  - local and upstream role-library search
  - role reuse versus adaptation decision
  - new-role drafting when the current library is insufficient
  - staffing-side handoff to `Team Architect` when collaboration design is needed
- Must produce:
  - agent team plan
  - role matrix
  - role sourcing note
  - role adaptation brief
  - new-role brief
  - `Team Architect` handoff brief
- Must not do:
  - silently promote draft roles to canonical or global default
  - import upstream orchestration doctrine as local default
  - widen one bounded team-design task into general governance redesign

## Local Team Surface Decision

The first local draft proved that `HR` was clearer than many generic roles but
was still anchored too much to human staffing language.

The local decision is therefore:

- keep `HR` as a compatibility entrypoint
- treat the real reusable surface as `Human Resources`
- let the caller address the team as one partner
- keep internal role choice inside the team boundary
- reinterpret `Human Resources` as agent-workforce design rather than human recruiting
- move non-trivial collaboration instantiation to `Team Architect`

## Upstream Assumptions To Remove Or Rewrite

- Orchestration assumptions:
  - remove NEXUS-style team and phase assumptions
  - keep the role usable inside local task-shaped orchestration
- Tool or runtime assumptions:
  - remove ATS, platform, and automation requirements as defaults
  - treat them as optional environment-specific surfaces
- Stack or domain assumptions:
  - remove China-specific platform defaulting
  - reframe the role from human recruiting into agent-team design, role sourcing, and role creation
- Quality-gate assumptions:
  - remove upstream success-metric inflation and platform-heavy KPI framing
  - keep evidence-backed selection rationale, capability-gap thinking, and clean handoff

## Local Binding

- Preferred runtime: `default`
- Collaboration mode: `orchestrator-subagent`
- Expected inputs:
  - mission, project, or business goal
  - constraints on scope, timeline, permissions, and collaboration shape
  - existing local roles or teams when already known
- Expected outputs:
  - agent team plan
  - sourcing/adaptation/creation recommendation
  - role brief or draft when needed
  - handoff brief for collaboration instantiation when needed
- Handoff contract:
  - to the main orchestrator or user for team approval
  - to the next owner for actual use of the designed team
- Verification expectations:
  - team shape maps to the real work rather than a generic team chart
  - recommendation tied to explicit criteria
  - reuse versus adaptation versus creation is justified
  - new or modified roles have bounded deliverables and must-not-do constraints
  - handoff artifacts are complete enough that the next role does not infer missing context

## Borrowed Sections

- Keep:
  - structured team-building logic
  - gap-based thinking
  - handoff awareness
- Rewrite:
  - all platform-specific sourcing language
  - human recruiting language into agent-role sourcing language
  - full onboarding into role-handoff scope
- Drop:
  - market-specific channel playbooks
  - vendor-specific ATS details
  - compensation benchmarking by named local services
  - long HR operations coverage outside agent-team setup

## Trial Notes

- First bounded use: not yet run
- Observed strengths:
  - clear team-design workflow
  - strong deliverable orientation
  - natural split between team design, role sourcing, role creation, and later collaboration instantiation
- Observed drift or failure modes:
  - tendency to drift back into human-staffing language
  - tendency to create new roles too early without enough reuse search
  - tendency to absorb collaboration design that should belong to `Team Architect`
- Promotion decision:
  - promote from single adapted role to local team surface
  - keep maturity below canonical until at least one bounded agent-team design run succeeds
- Open questions:
  - whether a future `Product Design` or `Operations` specialist should join the team
  - whether `Team Architect` should eventually gain a direct alias
