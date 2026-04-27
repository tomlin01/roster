# Local Agents

This folder stores workspace-owned agent definitions and their adaptation notes.

The goal is to keep local agents separate from:

- upstream raw role libraries under [`../references/third_party/`](../references/third_party/)
- policy and orchestration contracts under [`../policy/`](../policy/)
- team surfaces under [`../teams/`](../teams/)

## Structure

- [`native/`](./native/)
  - local-owned agent definitions intended for repeated use
- [`adapted/`](./adapted/)
  - adaptation notes and draft mappings from upstream role libraries

## Current Rule

- `native/` means the definition is local-owned
- it does not automatically mean the role is fully canonical
- role maturity should still be stated inside the file itself

## Current Agents

- [`native/team-architect.md`](./native/team-architect.md)
  - role for instantiating collaboration method from the global multi-agent coordination policy
- [`native/hr.md`](./native/hr.md)
  - compatibility entrypoint for the `Human Resources` team surface
- [`adapted/hr.role_adaptation.md`](./adapted/hr.role_adaptation.md)
  - provenance and adaptation note for the `Human Resources` team surface
