# open-multi-agent Reference Snapshot

## Provenance

- upstream: `https://github.com/JackChen-me/open-multi-agent`
- local snapshot path: `references/third_party/open-multi-agent/`
- inspected commit: `6aba8edd01a47739c082dad093ed67a3d56354c3`
- package: `@jackchen_me/open-multi-agent`
- package version at inspection: `1.2.0`
- inspection date: `2026-04-24`

## Local Classification

Treat this snapshot as a raw third-party runtime reference.

It is not:

- a local role library
- a replacement for `Human Resources`
- a replacement for `Team Architect`
- a replacement for `/Users/tom/.codex/agent_policy/MULTI_AGENT_COORDINATION.md`

It may become:

- an execution adapter for multi-agent task packets
- a TypeScript runtime substrate for explicit `runTasks()` plans
- a reference implementation for team roster, task queue, shared memory, and message bus behavior

## Useful Surfaces

- `README.md`
  - high-level architecture and framework positioning
- `DECISIONS.md`
  - explicit non-goals: agent handoffs as first-class paradigm, state persistence/checkpointing
- `docs/cli.md`
  - CLI behavior and limits
- `src/team/team.ts`
  - `Team` roster, message bus, task queue, shared memory, event bus
- `src/orchestrator/orchestrator.ts`
  - `runTeam()`, `runTasks()`, scheduler, approval gate, task execution
- `src/task/queue.ts`
  - dependency-aware task queue
- `src/tool/built-in/delegate.ts`
  - synchronous `delegate_to_agent` tool
- `src/memory/shared.ts`
  - namespaced shared memory abstraction

## Local Use Boundary

Prefer `runTasks()` for governed local multi-agent execution.

Use `runTasks()` when:

- `HR` has already produced a team plan
- `Team Architect` has already produced an operating packet
- task owners, dependencies, artifacts, and convergence rules are explicit
- the user expects the plan to be followed rather than reinterpreted

Use `runTeam()` only for exploratory or low-risk work where the framework may decompose the goal itself.

## Adoption Status

Current status: `reference/adapter-candidate`.

This snapshot is now available for local design and mapping work, but no production runtime integration has been validated yet.
