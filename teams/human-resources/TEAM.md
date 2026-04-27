# Human Resources Team Contract

## Status

- local-owned: yes
- maturity: draft team surface
- version: v0.3

## Shared Goal

Convert a mission or multi-agent need into a concrete agent team plan, a role
reuse-or-build decision, and a usable staffing packet.

## Team Members

- `HR Director`
  - owns intake, staffing shape, scope control, and final staffing synthesis
- `Role Scout`
  - owns role-library search, reuse-first discipline, and gap detection
- `Role Architect`
  - owns role adaptation, new-role drafting, and definition quality

## Routing Heuristics

- team ambiguity or sequencing ambiguity
  - route first to `HR Director`
- need to inspect local agents, upstream role libraries, or reuse options
  - add `Role Scout`
- need to modify an existing role or create a new one
  - add `Role Architect`
- large or multi-role team packet
  - `HR Director` coordinates the specialists

## Shared Artifacts

- `agent_team_plan`
- `hr_staffing_packet`
- `role_matrix`
- `role_sourcing_note`
- `role_adaptation_brief`
- `new_role_brief`
- `team_architect_handoff_brief`

## Convergence Rule

The team is not done when one member finishes a local subtask.

The team closes only when:

- the team shape matches the actual work
- reuse versus adaptation versus creation is justified
- any new or modified role has a clear boundary and deliverables
- the next owner can act without re-deriving context
- the packet makes clear whether `Team Architect` is required next

## Failure Patterns To Watch

- role creation before checking whether a local or upstream role already fits
- role adaptation that silently imports upstream control-plane assumptions
- new roles with vague scope, fuzzy deliverables, or overlapping authority
- HR drifting into collaboration design that should be instantiated by `Team Architect`
- staffing notes that do not explain what the next owner should do

## Default Delegation Stance

- keep the caller-facing surface singular
- keep internal role activation minimal
- increase internal collaboration only when the artifact boundary demands it
- prefer one final packet over multiple disconnected summaries
- do not force the caller to micromanage internal role choice
- hand off collaboration design to `Team Architect` when it is non-trivial
