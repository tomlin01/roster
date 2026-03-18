# codex_updat

`codex_updat` is the incubation and integration workspace for central-nervous-system workflows.
It is where new operating patterns are validated, converged, and documented before they are promoted outward.

This folder is not meant to be a generic scratchpad or a dump of one-off experiments.
Its value comes from making governance decisions, workflow contracts, and reusable patterns explicit.

## What This Workspace Owns

This workspace currently owns three layers of work:

- `stable core`
  - memory routing
  - benchmark / policy / overlay contract
  - reconciliation / status / capability surfaces
- `active convergence`
  - skill lifecycle
  - bootstrap / session discipline
- `experimental`
  - quality-aware skill router
  - intent parsing
  - discovery / candidate-install orchestration
  - multi-agent interaction pilots

## Start Here

If you are opening this workspace on a new machine or in a new session, read in this order:

1. [`AGENTS.md`](./AGENTS.md)
2. [`PRINCIPLES.md`](./PRINCIPLES.md)
3. [`policy/CENTRAL_NERVOUS_SYSTEM_BRIEF.md`](./policy/CENTRAL_NERVOUS_SYSTEM_BRIEF.md)
4. [`policy/STABLE_CORE_CONTRACT.md`](./policy/STABLE_CORE_CONTRACT.md)
5. [`policy/SKILL_LIFECYCLE_CONTRACT.md`](./policy/SKILL_LIFECYCLE_CONTRACT.md)

Only read [`contexts/system_status.md`](./contexts/system_status.md) when you need the current machine/runtime state.

## Key Documents

### Human-oriented re-entry

- [`policy/CENTRAL_NERVOUS_SYSTEM_BRIEF.md`](./policy/CENTRAL_NERVOUS_SYSTEM_BRIEF.md)
  - the shortest re-entry map for central nervous system work

### Stable contract surfaces

- [`policy/STABLE_CORE_CONTRACT.md`](./policy/STABLE_CORE_CONTRACT.md)
  - what counts as stable and what must not be broken casually
- [`policy/GLOBAL_OPERATING_MODEL.md`](./policy/GLOBAL_OPERATING_MODEL.md)
  - machine-wide layering and compatibility model

### Skill system

- [`policy/SKILL_LIFECYCLE_CONTRACT.md`](./policy/SKILL_LIFECYCLE_CONTRACT.md)
  - discovery, candidate, trial, review, promote / reject

### Multi-agent pilot

  - [`policy/VIS_MATH_MULTI_AGENT_PILOT_V0.md`](./policy/VIS_MATH_MULTI_AGENT_PILOT_V0.md)
  - current pilot for role + artifact + protocol + convergence

### Portability and setup

- [`PORTABILITY_GUIDE.md`](./PORTABILITY_GUIDE.md)
- [`docs/SETUP_PORTABILITY.md`](./docs/SETUP_PORTABILITY.md)
- [`docs/CONFIG_REFERENCE.md`](./docs/CONFIG_REFERENCE.md)
- [`docs/RUNTIME_ARTIFACT_POLICY.md`](./docs/RUNTIME_ARTIFACT_POLICY.md)
- [`docs/PORTABILITY_CHECKLIST.md`](./docs/PORTABILITY_CHECKLIST.md)

## What This Workspace Is Not

This workspace is not:

- the permanent home for all functional project work
- a replacement for canonical source-of-truth documents
- proof that every experimental feature is already globally safe

Concrete implementation work should often happen in a separate functional session or project folder, then be folded back here after convergence.

## Portability Note

This folder is designed to be partially portable to GitHub, but not every file is equally portable.

Portable by intent:

- `AGENTS.md`
- `PRINCIPLES.md`
- `policy/`
- selected reusable templates
- selected durable context artifacts

Machine-local or runtime-derived artifacts should be treated more carefully.
See [`PORTABILITY_GUIDE.md`](./PORTABILITY_GUIDE.md).
