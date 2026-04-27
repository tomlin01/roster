# agency-agents Index

## Purpose

This file records the local snapshot and curation notes for the vendored third-party repository:

- upstream: [msitarzewski/agency-agents](https://github.com/msitarzewski/agency-agents)
- local snapshot: [`agency-agents/`](./agency-agents/)

This snapshot is kept as a raw role library.
It is not an active operating model for this workspace.

## Provenance

- source repo: `https://github.com/msitarzewski/agency-agents`
- snapshot commit: `783f6a72bfd7f3135700ac273c619d92821b419a`
- upstream commit date: `2026-04-11 23:25:59 -0500`
- captured for this workspace: `2026-04-20`
- license: `MIT`
- local snapshot note: copied without `.git/`; treat as read-only reference

## Local Snapshot Facts

- total files in snapshot: `241`
- Markdown files in snapshot: `227`
- role files in the main division folders: `172`
- top-level divisions counted locally: `15`

Division counts in the current snapshot:

- `academic`: `5`
- `design`: `8`
- `engineering`: `29`
- `finance`: `5`
- `game-development`: `5`
- `marketing`: `30`
- `paid-media`: `7`
- `product`: `5`
- `project-management`: `6`
- `sales`: `8`
- `spatial-computing`: `6`
- `specialized`: `41`
- `strategy`: `3`
- `support`: `6`
- `testing`: `8`

## What It Is Good For

- broad specialist-role prompts in Markdown rather than tool-specific config
- examples of role sections such as mission, deliverables, constraints, and success metrics
- a reusable prompt vocabulary for reviewer, producer, verifier, and specialist roles
- orchestration doctrine reference material under `strategy/`
- multi-tool export patterns under `integrations/` and `scripts/`

## What It Is Not

- not a local shared-artifact protocol
- not a replacement for local overlay policy
- not a reason to import the NEXUS control plane into machine-wide defaults
- not a canonical role set for this workspace without adaptation

## Useful First Reads

- [`agency-agents/README.md`](./agency-agents/README.md)
- [`agency-agents/strategy/nexus-strategy.md`](./agency-agents/strategy/nexus-strategy.md)
- [`agency-agents/specialized/agents-orchestrator.md`](./agency-agents/specialized/agents-orchestrator.md)
- [`agency-agents/strategy/coordination/handoff-templates.md`](./agency-agents/strategy/coordination/handoff-templates.md)
- [`agency-agents/testing/testing-reality-checker.md`](./agency-agents/testing/testing-reality-checker.md)
- [`agency-agents/engineering/engineering-frontend-developer.md`](./agency-agents/engineering/engineering-frontend-developer.md)
- [`agency-agents/integrations/mcp-memory/README.md`](./agency-agents/integrations/mcp-memory/README.md)
- [`agency-agents/CONTRIBUTING.md`](./agency-agents/CONTRIBUTING.md)

## Local Usage Rule

If a role from this snapshot is adopted locally:

1. keep the upstream snapshot unchanged
2. create a workspace-owned draft using [`../../templates/agent_role_adaptation/role_adaptation.template.md`](../../templates/agent_role_adaptation/role_adaptation.template.md)
3. strip upstream workflow, runtime, and tool assumptions that do not belong in the role core
4. bind the adapted role to local orchestration and artifact contracts before active use
5. promote only after repeated bounded use shows the role is stable
