# Naming Decision Draft

This draft records the naming direction for the user-facing coordination kit.

## Problem

`codex-cns` is too internal for ordinary use.

The name reflects the repo's original central-nervous-system metaphor, but a
human user does not naturally think:

```text
I need CNS to organize this work.
```

The user is more likely to think:

```text
I need the right people and roles for this work.
```

or:

```text
I need someone to staff and organize this project.
```

The visible name should preserve the human-resources advantage without sounding
like a generic HR database or an official Codex product. It should be short
enough to call naturally.

## Naming Principles

- Prefer one word.
- Avoid `codex-` in the user-facing product or invocation name.
- Keep a human staffing / role-allocation feel.
- Avoid names that sound like a server, runtime, platform, or governance layer.
- Avoid overly literal names like `Project Office` if they feel administrative.
- Keep `HR` as a staffing and role-design sub-surface.
- Let the primary surface cover staffing plus project boundary, handoff, access,
  and review coordination.
- Make the invocation easy to type in Codex CLI/GUI.

## Role Model

Recommended visible model:

- `Roster`: primary coordination surface
  - staff the work
  - shape roles
  - define the deliverable boundary
  - create the collaboration plan
  - route into HR / Team Architect / CAP as needed
  - leave review evidence
- `PM`: optional natural alias
  - project-planning phrasing
  - handoff to Roster when the request is broader than staffing
  - not the primary product name
- `HR`: staffing-only surface
  - role design
  - staffing fit
  - role boundary
  - handoff when the work needs broader coordination
- `CAP`: advanced/audit surface
  - tool, skill, plugin, approval, and runtime allowlist checks

This keeps the human-resources value visible without letting HR own project
coordination or tool authorization.

## Candidate Names

### Roster

- product name: `Roster`
- current invocation: `Roster, ...`
- future install target: `@roster`
- natural aliases: `Roster`, `PM`
- retained staffing alias: `HR`

Pros:

- one word
- strong staffing and human-team signal
- less literal than `Project Office`
- works as a verb-like user idea: `roster this task`
- broad enough to include role design, task ownership, and review handoff
- does not imply a server, runtime, or official Codex product

Cons:

- may sound like only a list of people unless the README explains that Roster
  also creates task boundaries, tool-access notes, and review checklists
- `PM` remains useful as an alias because `Roster` alone does not immediately
  imply project planning

### Crew

- product name: `Crew`
- invocation: `@crew`
- natural aliases: `Crew`, `HR`

Pros:

- one word
- human and team-oriented
- friendly and easy to remember

Cons:

- more casual than the system's review/evidence ambitions
- weaker fit for academic, governance, and approval-bound workflows

### Lineup

- product name: `Lineup`
- invocation: `@lineup`
- natural aliases: `Lineup`, `HR`

Pros:

- one word
- clearly about assigning people to work
- implies a chosen team rather than generic planning

Cons:

- can feel sports-like
- less natural for artifact contracts and tool access

### Bench

- product name: `Bench`
- invocation: `@bench`
- natural aliases: `Bench`, `HR`

Pros:

- one word
- conveys available talent and role sourcing
- good fit for staffing-oriented workflows

Cons:

- can imply unused capacity rather than active coordination
- weaker project-planning signal

### Project Office

- product name: `Project Office`
- invocation: `@project-office`
- natural aliases: `Project Office`, `PM`

Pros:

- clear project-planning meaning
- strong fit for coordination, handoffs, and review

Cons:

- too many words
- feels administrative
- not enough human-resources signal
- less natural as a daily invocation

## Current Recommendation

Use `Roster` as the primary user-facing name.

Current status: `Roster, ...` is the current natural-language invocation path.
`@roster` has been tested and is not working as an installed Codex mention in
this phase, so it remains a future install target only.

Target surfaces:

- product/display name: `Roster`
- current invocation: `Roster, ...`
- future install target: `@roster`
- natural aliases: `Roster`, `PM`
- retained staffing alias: `HR`

Human-facing explanation:

```text
Call Roster when you want the right people, roles, and task boundary for the
work.
Call HR when you only need staffing or role design.
Roster may route to HR, Team Architect, CAP, or runtime checks when the task
needs those layers.
```

## Boundary Rule

The rename must not collapse ownership:

- Roster does not become HR.
- HR does not own project coordination.
- Roster does not own tool authorization.
- CAP still owns tool, skill, plugin, approval, and runtime allowlist.
- Runtime adapters still execute only.

## README Impact

The target README should replace old invocation placeholders with:

```text
Roster, ...
```

and explain:

```text
Use `Roster, ...` when you want the work staffed and organized.
Use `HR` when you only need staffing or role design.
Treat `@roster` as a future install target until registration is verified.
```

The internal repo may still contain historical `codex-cns` names during
transition, but the user-facing target should converge on the Roster surface.
