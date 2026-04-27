# Multi-Agent Runtime Adapters V0

## Purpose

This policy defines how external multi-agent runtimes can be introduced into `codex-cns` without replacing local role governance or the machine-wide coordination policy.

Runtime adapters execute a plan.
They do not own the plan.

`codex-cns` remains Codex-native and same-folder first. A runtime adapter is
optional and must not introduce a persistent server requirement for ordinary
Codex CLI or Codex GUI packet assembly.

## Current Adapter Candidates

### open-multi-agent

- upstream: `https://github.com/JackChen-me/open-multi-agent`
- local snapshot: `../references/third_party/open-multi-agent/`
- status: `execution-adapter-candidate`
- preferred API: TypeScript `runTasks()`
- exploratory API: TypeScript `runTeam()`
- CLI status: shell/CI helper only

## Layer Boundary

The local layer order is:

```text
user mission
-> Human Resources
-> Team Architect
-> runtime adapter
-> execution evidence
```

For Artifact Harness workflow runs, use the fuller packet chain:

```text
user mission
-> Artifact Harness SPEC
-> HR staffing
-> Team Operating Packet
-> Capability Access Packet
-> runtime mapping
-> verification/review
```

`Human Resources` owns staffing and role design.

`Team Architect` owns collaboration design and task-graph preparation using `/Users/tom/.codex/agent_policy/MULTI_AGENT_COORDINATION.md`.

The runtime adapter owns execution mechanics only.

## Preferred open-multi-agent Mapping

Use `runTasks()` when execution should follow a local operating packet.

The mapping must provide:

- `TeamConfig`
- agent names
- model/provider assumptions
- system prompts
- allowed tools
- explicit tasks
- `assignee`
- `dependsOn`
- artifact expectations
- memory scope
- approval gate positions
- convergence and fallback notes

Use `runTeam()` only when:

- the task is exploratory
- a formal task graph is not yet worth writing
- the caller accepts framework-led decomposition
- output is low-risk or will be reviewed before promotion

## Required Safeguards

Every adapter-backed run must state:

- whether it uses `runTasks()` or `runTeam()`
- which local packet generated the runtime input
- which artifacts are expected
- which failures should stop execution
- which decisions require user approval

For Artifact Harness workflow runs, the runtime mapping must also:

- link the source Capability Access Packet
- derive exposed tools and approval gates from that packet
- withhold capabilities not explicitly authorized there
- avoid CLI execution when approval gates require TypeScript callbacks or other
  runtime object wiring
- avoid direct adapter execution from Markdown mapping alone
- pass through the Artifact Harness invocation guard, or an equivalent guard
  with the same CAP, runtime readiness, approval-evidence, and surface checks

## Runtime Invocation Guard

Adapter-backed execution must be preceded by a same-folder invocation envelope
before any real runtime call. For the Artifact Harness workflow, the repo-native
guard is:

```text
./scripts/brain.sh artifact-harness runtime-invoke --path <workspace-folder> --id <packet-id> --adapter open-multi-agent --surface typescript-runTasks --dry-run --json
```

The guard must refuse when required approval evidence is missing or denied,
when runtime readiness has blocking findings, when the requested surface does
not match the CAP-derived runtime requirement, or when approval-gated execution
is requested through a CLI-only surface.

`approval_evidence.json` records explicit gate decisions only; it does not
replace CAP ownership, artifact acceptance, or verification.
`runtime_invocation_report.json` is guard evidence only; it is not runtime
execution, not an approval authority, and not a transfer of governance to the
adapter.

## Promotion Requirements

Before an adapter becomes a stable local execution path, a pilot must verify:

- generated task graph is readable
- runtime execution follows task dependencies
- outputs can be mapped back to expected artifacts
- failure and skipped-task behavior is acceptable
- approval gates work through the selected API
- invocation reports constrain exposed capabilities and withhold denied
  capabilities before execution
- generated runtime byproducts follow `docs/RUNTIME_ARTIFACT_POLICY.md`
