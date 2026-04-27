# open-multi-agent Runtime Diff

## Summary

`open-multi-agent` is a runtime framework, not a role catalog.

Compared with `agency-agents`, it is more relevant to the execution layer of the local multi-agent system. Its strongest fit is below `HR` and `Team Architect`, where an already-designed team operating packet needs to become an executable task graph.

## What It Adds

- concrete `TeamConfig` surface for named agents
- dependency-aware task execution through `runTasks()`
- goal-driven coordinator execution through `runTeam()`
- optional shared memory
- inter-agent message bus
- task retry and failure propagation
- synchronous `delegate_to_agent` tool
- progress, trace, and approval callback hooks in the TypeScript API
- CLI for shell and CI execution

## Main Fit With Local Design

Local design currently separates:

- `HR`: staffing and role design
- `Team Architect`: collaboration pattern, artifacts, handoff, convergence
- global coordination policy: approved collaboration patterns
- runtime execution: not yet fixed

`open-multi-agent` fits the last layer.

The preferred local mapping is:

```text
mission
-> HR staffing packet
-> Team Architect operating packet
-> open-multi-agent runTasks() mapping
-> execution result and artifacts
```

## runTasks() Versus runTeam()

Use `runTasks()` when local governance has already decided the task graph.

Local reasons:

- preserves `Team Architect` as owner of collaboration design
- makes assignee, dependencies, artifacts, and gates explicit
- reduces duplicate decomposition by a framework coordinator
- gives future runs a stable task graph to inspect

Use `runTeam()` when the task is exploratory.

Local reasons:

- lets the framework's temporary coordinator decompose the goal
- reduces upfront planning cost
- accepts more runtime discretion
- is less suitable for governed or high-impact execution

## Important Gaps

- no first-class long-running handoff paradigm
- no built-in checkpoint/persistence layer
- CLI has no interactive REPL, human approval gates, or session persistence
- custom durable memory stores require TypeScript API wiring, not CLI JSON
- local alias routing and role governance still live in `codex-cns`

## Adoption Rule

Do not make `open-multi-agent` the global default until at least one local pilot validates:

- generated `TeamConfig`
- generated `runTasks()` task list
- artifact collection
- approval gate behavior
- fallback behavior when a task fails or blocks downstream work

