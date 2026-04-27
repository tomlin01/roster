# Artifact Harness Workflow V0

## Purpose

This policy defines the minimal workflow for artifact-driven missions that need
a harness contract, multi-agent staffing, explicit capability access, and
optional runtime execution.

The workflow keeps artifact expectations, staffing, collaboration design,
capability authorization, runtime execution, and verification in separate
layers.

This is a Codex-native, template-first workflow. It assumes the agent can read
and fill packet files in the same workspace folder from Codex CLI or Codex GUI.
It does not require a persistent server or a separate orchestration UI.

## Workflow

```text
user mission
-> Artifact Harness SPEC
-> HR staffing
-> Team Operating Packet
-> Capability Access Packet
-> runtime mapping
-> verification/review
```

Runtime mapping may target an external runtime adapter, but the adapter remains
an execution layer only.

## Layer Responsibilities

### User Mission

- states the target outcome
- may name the expected artifact, path, quality bar, or boundary
- does not need to preselect roles, tools, plugins, or runtime adapters
- can be turned into packet fields only where the mission or repo evidence
  actually supports the fill

### Artifact Harness SPEC

Template:

- [`../templates/artifact_harness/artifact_harness_spec.template.md`](../templates/artifact_harness/artifact_harness_spec.template.md)

Owns:

- rule
- contract
- acceptance checks
- boundaries

Autofill source:

- user mission
- explicitly named artifact path or expected output
- repo-local evidence provided by the user or current workspace

Must not own:

- staffing
- skill, plugin, or tool authorization
- runtime execution
- memory-engine promotion

### HR Staffing

Owns:

- staffing
- role selection
- role adaptation or new-role draft decisions
- staffing-side handoff to `Team Architect`

Autofill source:

- user mission
- Artifact Harness SPEC boundaries
- local team and role surfaces

Must not own:

- tool authorization
- collaboration instantiation
- runtime adapter governance

Canonical surface:

- [`../teams/human-resources/AGENTS.md`](../teams/human-resources/AGENTS.md)

### Team Architect Operating Packet

Template:

- [`../templates/team_architect/team_operating_packet.template.md`](../templates/team_architect/team_operating_packet.template.md)

Owns:

- collaboration pattern
- task graph and shared artifacts
- interaction protocol
- convergence and stop conditions
- runtime mapping source when runtime execution is appropriate
- CAP generation when capability authorization or runtime gates are needed

Autofill source:

- Artifact Harness SPEC
- HR staffing packet
- coordination baseline

When a mission has a clear artifact expectation and needs multi-agent execution
or tool authorization, `Team Architect` must produce both:

- a Team Operating Packet
- a Capability Access Packet

### Capability Access Packet

Template:

- [`../templates/team_architect/capability_access_packet.template.md`](../templates/team_architect/capability_access_packet.template.md)

Owns only:

- skill authorization
- plugin authorization
- tool authorization
- approval gates for those capabilities
- runtime allowlist derived from those capabilities

Autofill source:

- Artifact Harness SPEC boundaries
- Team Operating Packet task graph and artifact needs
- available local skills, plugins, and tools

Any access boundary recorded in this packet exists only to constrain skill,
plugin, tool, or runtime exposure. It is not a separate governance layer.

Must not own:

- staffing
- artifact contract rules
- collaboration pattern selection
- artifact verification or acceptance
- runtime governance ownership

### Runtime Adapter

Owns:

- execution mechanics
- task dispatch
- runtime byproducts
- returning execution evidence to the orchestrator

Autofill source for runtime mapping:

- Team Operating Packet
- Capability Access Packet
- runtime adapter policy

Must not own:

- local governance
- staffing
- artifact acceptance rules
- capability policy

Runtime adapter policy:

- [`MULTI_AGENT_RUNTIME_ADAPTERS_V0.md`](./MULTI_AGENT_RUNTIME_ADAPTERS_V0.md)

### Verification And Review

Owns:

- checking the produced artifact against the Artifact Harness SPEC
- checking execution evidence against the Team Operating Packet
- checking tool exposure against the Capability Access Packet
- deciding whether the result is accepted, revised, or blocked

## Minimal Operating Rules

- Start with an Artifact Harness SPEC when the expected output is an artifact,
  not just a conversational answer.
- Route staffing through `HR`; do not redesign HR for this workflow.
- Route collaboration design through `Team Architect`; do not leave a team list
  without an operating method.
- Use a Capability Access Packet only for capability authorization and approval
  gates.
- Expose only the capabilities needed by the operating packet and harness
  acceptance checks.
- Keep runtime adapters as execution mechanisms, not governance owners.
- Do not start `memory_engine_system_v0` L5 as part of this v0 workflow.
- Keep all required packets usable as ordinary Markdown in the same workspace
  folder.
- Do not claim full automation unless a concrete executable path or filled-run
  evidence exists.

## Packet Location And Naming

The repo-native entrypoint is:

```text
./scripts/brain.sh artifact-harness "<mission>" --path <workspace-folder>
```

`--path <workspace-folder>` is the target workspace and packet output root. By
default the packet chain is written under:

```text
<workspace-folder>/contexts/artifact_harness_runs/<packet-id>/
```

The packet id is deterministic from the mission and target path unless `--id`
is supplied. Each run directory contains:

- `artifact_harness_spec.md`
- `hr_staffing_packet.md`
- `team_operating_packet.md`
- `capability_access_packet.md`
- `open_multi_agent_runtasks_mapping.md`
- `packet_manifest.json`
- `packet_status.json`
- `packet_provenance_ledger.json` when provenance is requested
- `runtime_readiness_report.json` when runtime readiness is checked
- `approval_evidence.json` when explicit approval gate decisions are recorded
- `runtime_invocation_report.json` when the runtime invocation guard is checked
- `repair_plan.json` when failure recovery is planned

The registry is:

- `<workspace-folder>/contexts/artifact_harness_registry.json`

This gives Codex CLI/GUI a same-folder form-fill target without requiring a
persistent server.

## Packet Lifecycle

Packet lifecycle metadata is stored in:

```text
<workspace-folder>/contexts/artifact_harness_runs/<packet-id>/packet_status.json
```

The allowed status vocabulary is:

```text
draft, filled, reviewed, approved, blocked, executed, verified, superseded, archived
```

New scaffolded packet runs start as `draft`. Status updates are metadata-only:
they may update `packet_status.json` and
`<workspace-folder>/contexts/artifact_harness_registry.json`, but they must not
rewrite filled packet Markdown.

CLI/GUI-friendly lifecycle and evidence commands:

```text
./scripts/brain.sh artifact-harness status --path <workspace-folder> --id <packet-id>
./scripts/brain.sh artifact-harness resume --path <workspace-folder> --id <packet-id> --json
./scripts/brain.sh artifact-harness mark --path <workspace-folder> --id <packet-id> --status filled --note "packet fields filled" --json
./scripts/brain.sh artifact-harness replay --path <workspace-folder> --id <packet-id> --json
./scripts/brain.sh artifact-harness provenance --path <workspace-folder> --id <packet-id> --json
./scripts/brain.sh artifact-harness runtime-check --path <workspace-folder> --id <packet-id> --json
./scripts/brain.sh artifact-harness approval --path <workspace-folder> --id <packet-id> --gate runtime_execution --decision approved --approver "<label>" --json
./scripts/brain.sh artifact-harness runtime-invoke --path <workspace-folder> --id <packet-id> --adapter open-multi-agent --surface typescript-runTasks --dry-run --json
./scripts/brain.sh artifact-harness repair-plan --path <workspace-folder> --id <packet-id> --json
./scripts/brain.sh artifact-harness schema-check --path <workspace-folder> --id <packet-id> --json
./scripts/brain.sh artifact-harness migrate --path <workspace-folder> --id <packet-id> --json
```

`resume` is advisory only. It returns packet paths, lifecycle status, next
recommended inspection/action, and safe command forms. It does not invoke an
agent, approve a run, authorize capabilities, execute a runtime adapter, or
accept the final artifact.

## Replay Evidence

Replay evidence is stored in the packet run directory when requested:

```text
<workspace-folder>/contexts/artifact_harness_runs/<packet-id>/artifact_replay_evidence.json
```

`replay` inspects existing packet files, `packet_manifest.json`,
`packet_status.json`, the workspace registry, and command metadata. It records
packet presence plus simple open-field heuristics such as empty Markdown bullet
fields and visible open-question markers.

Replay evidence is observation and continuity only. It does not accept the
artifact, approve capabilities, choose runtime execution, replace SPEC/HR/Team
Architect/CAP/runtime mapping, or perform verification/review.

## Provenance Ledger

Provenance ledger output is stored in the packet run directory when requested:

```text
<workspace-folder>/contexts/artifact_harness_runs/<packet-id>/packet_provenance_ledger.json
```

`provenance` inspects the existing packet run, manifest, lifecycle status,
registry, packet files, and replay evidence if present. It records coarse source
categories for important packet facts, including `user_mission`,
`template_default`, `generated_scaffold`, `packet_reference`,
`repo_evidence`, `agent_inference`, `runtime_output`, `test_result`,
`human_approval`, `approval_required`, `unresolved`, and `unknown`.

The ledger is source tracking only. It does not accept the artifact, approve
capabilities, choose runtime execution, replace SPEC/HR/Team
Architect/CAP/runtime mapping ownership, or perform verification/review.

## Runtime Readiness Report

Runtime readiness output is stored in the packet run directory when requested:

```text
<workspace-folder>/contexts/artifact_harness_runs/<packet-id>/runtime_readiness_report.json
```

`runtime-check` inspects the existing packet run, manifest, lifecycle status,
Capability Access Packet, runtime mapping, replay evidence if present, and
provenance ledger if present. It checks whether runtime mapping traces to CAP
and the Team Operating Packet, whether CAP-derived capabilities and approval
gates are represented, and whether approval-gated execution requires an
enforceable TypeScript `runTasks()` surface instead of CLI-only execution.

The readiness report is preflight evidence only. It does not approve
capabilities, authorize execution, accept artifacts, invoke runtime adapters, or
make runtime adapters governance owners. Lifecycle status alone never counts as
approval evidence.

## Approval Evidence

Approval evidence is stored in the packet run directory when explicit gate
decisions are recorded:

```text
<workspace-folder>/contexts/artifact_harness_runs/<packet-id>/approval_evidence.json
```

`approval` records explicit user/agent-visible decisions for named gates such as
`runtime_execution`. It may update only `approval_evidence.json`; it must not
rewrite CAP, Team Operating Packet, runtime mapping, lifecycle status, packet
Markdown, or artifact acceptance. If multiple decisions exist for the same gate,
the latest decision wins. A latest `denied` decision for a required runtime gate
blocks runtime invocation.

Approval evidence does not replace CAP ownership. CAP still defines the
authorized skills/plugins/tools, approval gates, and runtime allowlist.

## Runtime Invocation Guard

Runtime invocation guard output is stored in the packet run directory when
requested:

```text
<workspace-folder>/contexts/artifact_harness_runs/<packet-id>/runtime_invocation_report.json
```

`runtime-invoke` is a guarded dry-run/export surface. It validates the existing
packet run, manifest-derived packet paths, runtime readiness report, CAP-derived
approval gates, approval evidence, requested adapter, and requested execution
surface before producing an invocation envelope. For approval-gated runs, CLI
execution is refused because it cannot carry the required approval callbacks or
runtime object wiring.

`runtime_invocation_report.json` is evidence only. In this workflow version,
`execution_performed` must remain `false`; the command must not call external
runtime adapters, spawn agents, run tasks, start a server, approve capabilities,
accept artifacts, or make runtime adapters governance owners.

## Repair Plan

Repair plan output is stored in the packet run directory when requested:

```text
<workspace-folder>/contexts/artifact_harness_runs/<packet-id>/repair_plan.json
```

`repair-plan` inspects an existing packet run, lifecycle status, schema-check
output, packet open-field heuristics, approval evidence, runtime readiness
report, and runtime invocation report. It produces explicit recovery items for
missing or open packets, blocked/superseded lifecycle state, denied approval
gates, runtime readiness blockers, missing approval evidence, and guarded
runtime invocation refusals.

`repair_plan.json` is advisory evidence only. It must not rewrite packet
Markdown, change lifecycle status, approve or deny gates, edit CAP/runtime
mapping, accept artifacts, execute runtime adapters, or transfer ownership
between Artifact Harness, HR, Team Architect, CAP, verification, and runtime
adapters. Repair actions must happen in the owning packet or artifact and be
rechecked through lifecycle, schema, runtime readiness, approval, or review
commands as appropriate.

## Schema Compatibility

Schema compatibility output is returned as JSON when requested:

```text
./scripts/brain.sh artifact-harness schema-check --path <workspace-folder> --id <packet-id> --json
./scripts/brain.sh artifact-harness migrate --path <workspace-folder> --id <packet-id> --json
```

`schema-check` inspects an existing packet run, validates manifest-derived paths
against the target workspace, and reports required files, missing fields,
warnings, blocking findings, and whether migration is required. It does not
rewrite packet Markdown or generated JSON files.

`migrate` is conservative. It may update only JSON compatibility metadata such
as `packet_manifest.json`, `packet_schema_metadata.json`, and the workspace
artifact-harness registry. It must not rewrite filled packet Markdown, change
lifecycle status into approval/execution/verification, approve capabilities,
accept artifacts, invoke runtime adapters, or move ownership boundaries.

The current schema contract lives in
[`policy/ARTIFACT_HARNESS_SCHEMA_V0.md`](./ARTIFACT_HARNESS_SCHEMA_V0.md).

## Field Provenance

Each packet must make its source explicit.

| Packet | Filled From | Owns |
| --- | --- | --- |
| Artifact Harness SPEC | user mission, explicit boundaries, expected artifact | rules, contract, acceptance, boundaries |
| HR staffing packet | user mission, Harness SPEC boundaries, local role library | staffing, role fit, role gaps |
| Team Operating Packet | Harness SPEC, HR packet, coordination baseline | collaboration pattern, shared artifacts, task graph, convergence |
| Capability Access Packet | Harness SPEC boundaries, Team Operating Packet, available skills/plugins/tools | capability authorization and approval gates |
| runtime mapping | Team Operating Packet, Capability Access Packet, runtime adapter policy | execution mapping and capability exposure trace |
| verification/review | produced artifact, execution evidence, all upstream packets | acceptance or revision decision |

No downstream packet may silently widen an upstream boundary. If a downstream
packet needs more authority than its sources provide, it must stop at an
approval gate.

## Instantiation Procedure

1. Convert the user mission into an Artifact Harness SPEC:
   - extract the expected artifact, location, consumer, rules, acceptance checks,
     and boundaries
   - mark unresolved mission ambiguity as open questions, not hidden defaults
2. Send the mission plus SPEC boundaries to `HR`:
   - fill role selection, reuse/adapt/create decisions, and unresolved role gaps
   - hand off collaboration design to `Team Architect` when non-trivial
3. Have `Team Architect` fill the Team Operating Packet:
   - select the collaboration pattern from the coordination baseline
   - assign shared artifacts, owners, task graph source, and convergence rules
   - link the source Artifact Harness SPEC
4. If skills, plugins, tools, or runtime approvals are needed, fill the
   Capability Access Packet:
   - derive allowed capabilities from the operating packet and SPEC boundaries
   - record denied or withheld capabilities
   - define approval gates for capability exposure or continuation
5. If a runtime adapter is used, fill the runtime mapping:
   - link both the Team Operating Packet and Capability Access Packet
   - derive the runtime tool allowlist from the Capability Access Packet
   - record approval gates and their enforcement surface
   - forbid CLI execution when approval gates require TypeScript callbacks or
     other runtime object wiring
6. Verify/review:
   - check artifact output against the Artifact Harness SPEC
   - check collaboration and execution evidence against the Team Operating
     Packet
   - check exposed capabilities and gates against the Capability Access Packet

## Out Of Scope For V0

- redesigning the HR architecture
- handing tool authorization to HR
- promoting new memory-engine behavior
- making runtime adapters canonical governance owners
- replacing the existing runtime adapter policy
- broad automation beyond the named packet chain

## Acceptance For This Workflow

A run follows this policy when:

- the Artifact Harness SPEC states rules, contract, acceptance, and boundaries
- the HR packet states the staffed roles and any role gaps
- the Team Operating Packet states collaboration, artifacts, protocol, and
  convergence
- the Capability Access Packet states authorized skills, plugins, tools, and
  approval gates
- the runtime adapter mapping, if used, links both the Team Operating Packet and
  Capability Access Packet
- the runtime mapping derives its tool allowlist and approval gates from the
  Capability Access Packet
- approval-gated runtime execution uses an API surface that can enforce gates
- verification/review checks the final artifact against the harness contract
