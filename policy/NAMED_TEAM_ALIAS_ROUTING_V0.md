# Named Team Alias Routing v0

## Purpose

Define how a stable local team surface may be invoked through a short natural
language alias.

This policy exists so a team such as `Human Resources` can be called directly
as `HR` without forcing the user to route through an explicit skill call.

## Core Rule

When a local team surface has a registered alias, treat that alias as the
primary human-facing invocation surface.

Do not force:

- explicit skill syntax
- manual internal role selection
- repeated reminder of the canonical file path

## Preferred Invocation Order

1. natural language alias
2. canonical team surface
3. compatibility entrypoint
4. explicit skill fallback, if one exists

The skill surface is optional.
It is not the primary daily entrypoint for a stable named team.

## Resolution Contract

When a registered alias is used:

1. resolve the alias to the canonical team surface
2. apply the team's internal routing and convergence rules
3. keep the caller-facing interface singular
4. return one integrated packet unless the task explicitly asks for staged output

## When To Register An Alias

Register a named team alias only when all of the following are true:

- the team surface is stable enough for repeated use
- the alias is short, memorable, and unlikely to collide locally
- the team has a clear canonical surface
- the team has explicit authority boundaries

## Collision Rule

If an alias could resolve to more than one stable surface:

- do not silently choose
- prefer the canonical named team only when the local registry says it is unique
- otherwise ask for clarification

## Relationship To Skills

Skills and named team aliases are not the same thing.

- named team alias:
  - human-facing invocation surface
  - best for direct chat usage
- skill:
  - routing adapter
  - useful for automation, portability, or forced invocation

A stable team may have both, but the alias should remain the default daily path.

## Current Active Local Alias

See [`../contexts/team_alias_registry.json`](../contexts/team_alias_registry.json).

The first active local alias is:

- `HR` -> `Human Resources`

## Packet Route Front Door

`packet-route` is an explicit CLI/agent-called route helper. It does not
automatically intercept every free-form Codex CLI or GUI phrase.

The route helper must read both registered aliases and `keyword_families` from
[`../contexts/team_alias_registry.json`](../contexts/team_alias_registry.json).
Config-level TOML keywords may add hints, but they are not the only source of
truth.

The route helper may also use conservative natural artifact-mission heuristics
when no registered front door matched. These heuristics must be deterministic:
they require a deliverable term plus an action, quality, or process cue before
allowing Artifact Harness packet creation. Vague artifact references may be
recognized as hints, but they must return clarification questions and refuse
`--create` until the deliverable and acceptance target are clear.

Artifact-production requests remain SPEC-first even when the utterance names a
downstream front door:

- `HR` with artifact-production intent -> Artifact Harness SPEC, then HR staffing
- `Team Architect` with artifact-production intent -> Artifact Harness SPEC, then Team Operating Packet
- `CAP` with artifact-production intent -> Artifact Harness SPEC, then Capability Access Packet
- runtime mapping with artifact-production intent -> Artifact Harness SPEC, then runtime mapping

HR-only staffing or role-design requests stay on the `Human Resources` team
surface and must not create Artifact Harness packet runs.

Direct downstream packet requests without an existing packet id must not bypass
upstream packets. With `--id <packet-id>` for an existing run, route to the
safest existing-run command such as `artifact-harness resume` or
`artifact-harness runtime-check`.
