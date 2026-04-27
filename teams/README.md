# Local Teams

This folder stores workspace-owned team surfaces.

Use a team surface when the entrypoint should feel like one durable partner even
if multiple internal roles may need to collaborate behind that interface.

Keep team surfaces separate from:

- single-role definitions under [`../agents/`](../agents/)
- policy and orchestration contracts under [`../policy/`](../policy/)

## Structure

- team folder
  - `AGENTS.md`
    - human-facing entrypoint for the team
  - `TEAM.md`
    - internal contract, routing, and convergence notes
  - `roles/`
    - internal member-role definitions

## Current Teams

- [`human-resources/AGENTS.md`](./human-resources/AGENTS.md)
  - canonical `Human Resources` team surface for agent-team design, role
    sourcing, role creation, and staffing-side handoff
  - official alias: `HR`
