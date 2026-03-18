# Central Nervous System Brief

## Purpose

This document is the human-oriented re-entry brief for central-nervous-system work.
Use it to start or resume a governance session without replaying the full construction history.

This repo remains the `incubation + integration workspace`.
The goal is to converge new operating patterns here first, then promote them outward only after they are stable.

## How To Use This Brief

When starting a new central session in this workspace, read in this order:

1. [`AGENTS.md`](../AGENTS.md)
2. [`PRINCIPLES.md`](../PRINCIPLES.md)
3. this brief
4. [`contexts/system_status.md`](../contexts/system_status.md) only if current operational state matters

Use this brief for `essence` and `design` level reasoning.
Only drop to implementation detail when the task explicitly requires it.

## What Has Recently Converged

### 1. Memory routing

See also: [`STABLE_CORE_CONTRACT.md`](./STABLE_CORE_CONTRACT.md)

The memory stack is now treated as:

- `Obsidian` = source of truth
- session state = short-lived execution memory
- folder overlays and policy artifacts = stable behavioral memory
- retrieval/index layers = reconstructable support, not canonical truth

For runtime continuity in this repo, prefer:

- `overlay`
- `closeout`
- `session-gate`

`memory-triage` is kept as a governance and diagnostic surface, not the daily default entrypoint.

### 2. Benchmark / policy / overlay contract

See also: [`STABLE_CORE_CONTRACT.md`](./STABLE_CORE_CONTRACT.md)

The global vs local policy split is now explicit:

- global defaults define schema and baseline behavior
- folder overlays specialize behavior without breaking global contracts
- session state is transient and lower priority

This repo is the staging area for changes to:

- benchmark schema
- overlay interpretation
- promotion rules
- machine-wide governance defaults

### 3. Skill lifecycle

See also: [`SKILL_LIFECYCLE_CONTRACT.md`](./SKILL_LIFECYCLE_CONTRACT.md)

The skill line is no longer treated as only inventory management.
It now has a clearer lifecycle:

- discovery
- candidate trial
- closeout-based learning
- review / promote / reject

This part is in active convergence and is more stable than it was before.

### 4. Skill router

The router should be understood as a `quality-aware workflow planner`, not a flat skill list generator.

Current operating stance:

- router use is `user-attached, assistant-advised`
- `gap = true` is a valid answer
- `primary = none` is preferred over forcing a wrong route
- discovery / candidate install is allowed only through trusted-source discipline

The router is improved, but still belongs to the experimental layer.

### 5. Session discipline

This repo is now explicitly treated as the governance lane, not the place where every implementation task should live.

Current split:

- central session = policy, convergence, operating model, synthesis
- functional session = concrete implementation or domain work
- scratch lane = fast exploration that does not automatically promote upward

Only converged results should be folded back into the central lane.

## Stable Core vs Active Convergence vs Experimental

### Stable core

- memory routing
- benchmark / policy / overlay contract
- reconciliation / status / capability surfaces

### Active convergence

- skill lifecycle
- bootstrap and session discipline

### Experimental

- quality-aware skill router
- intent parsing
- discovery / candidate-install orchestration
- multi-agent interaction protocol pilots

## Multi-Agent: Current Best Understanding

Do not treat current native subagents as the full multi-agent system.

Current distinction:

- `subagent = primitive`
- `multi-agent = roles + artifacts + protocol + convergence`

The important insight is that stronger collaboration does not come from more personas alone.
It comes from:

- clear role boundaries
- artifact-based handoff
- promotion gates
- explicit convergence rules

## Current Multi-Agent Direction

The first serious pilot is in `Vis_Math`.

Its current shape is:

- narrative roles: `Teacher`, `Student`
- production roles: `Video Producer`
- likely next visual role: `Video QA`

The working direction is:

- do not let every role free-chat over the same problem
- route collaboration through shared artifacts
- separate content convergence from visual polish

This is not a global standard yet.
It is an active pilot for future multi-agent use.

## What This Thread Should Be Treated As

This thread can now be treated as a `construction layer` rather than the canonical central entrypoint.

That means:

- the thread contains valuable implementation and reasoning history
- but future central sessions should not depend on replaying all of it
- they should re-enter through this brief plus current repo policy artifacts

## What A New Central Session Should Remember

- this repo is the incubation and integration workspace
- central work here is about convergence, not endless implementation
- memory, benchmark/policy/overlay, and governance contracts are the current stable backbone
- skill lifecycle is maturing
- skill router and multi-agent protocol are still experimental
- prefer essence first, then design, then implementation

## Practical Re-entry Rule

If the user says "go back to the central nervous system" or opens a new governance session here, the session should:

1. treat this brief as the first human-oriented context artifact
2. use [`contexts/system_status.md`](../contexts/system_status.md) only for current operational status
3. avoid inheriting implementation noise unless the task explicitly requires construction detail

## Promotion Rule Reminder

Nothing should be treated as globally standard merely because it worked once here.
Promote outward only when:

- local validation passes
- canonical outputs are stable
- contracts stay intact
- the behavior survives beyond a single narrow workspace case
