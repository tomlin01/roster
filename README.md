# codex-cns

`codex-cns` is a Codex-native agent coordination kit.
It keeps artifact-quality contracts, role staffing, capability authorization,
runtime mapping, and verification boundaries in agent-readable documents and
templates that Codex can use inside the same workspace folder.

It does not require a persistent server, daemon, or separate orchestration UI.
The intended operating surface is ordinary Codex CLI or Codex GUI work in this
folder, with templates filled by the agent before any optional runtime adapter
is used.

This folder is not meant to be a generic scratchpad or a dump of one-off experiments.
Its value comes from making governance decisions, workflow contracts, and reusable patterns explicit.

Primary artifact workflow:

```text
user mission
-> Artifact Harness SPEC
-> HR staffing
-> Team Operating Packet
-> Capability Access Packet
-> runtime mapping
-> verification/review
```

The workflow is template-first and agent-readable. It is designed so Codex can
auto-fill task packets and execution boundaries from a user mission when the
source information is present. It should not be described as fully automated
unless a specific executable path or filled-run evidence exists in this repo.

Minimal packet entrypoint:

```bash
./scripts/brain.sh artifact-harness "<mission>" --path <workspace-folder>
./scripts/brain.sh artifact-harness "<mission>" --path <workspace-folder> --json
```

Packet lifecycle and evidence entrypoints:

```bash
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

Lifecycle status is stored as metadata in the packet run directory and mirrored
into the workspace registry. It is continuity evidence only; it does not grant
approval, capability access, runtime execution authority, or artifact
acceptance.
`replay` writes `artifact_replay_evidence.json` inside the packet run directory
by inspecting existing packets, manifest, registry, and lifecycle status. It is
observation and continuity only, not artifact verification or runtime execution.
`provenance` writes `packet_provenance_ledger.json` in the same run directory
to record coarse source categories for important packet facts. It is source
tracking only, not approval, acceptance, verification, or runtime selection.
`runtime-check` writes `runtime_readiness_report.json` as preflight evidence for
CAP trace, approval gates, and required execution surface. It does not approve
capabilities, authorize execution, accept artifacts, or invoke a runtime.
`approval` writes explicit gate decisions to `approval_evidence.json`.
`runtime-invoke` writes `runtime_invocation_report.json` as a guarded dry-run
envelope that checks CAP/readiness/approval evidence before any future adapter
launch path. It does not execute open-multi-agent, spawn agents, accept
artifacts, or make the runtime adapter a governance owner.
`repair-plan` writes `repair_plan.json` as advisory failure-recovery evidence
for missing/open packets, blocked lifecycle state, denied gates, and runtime
guard refusals. It does not rewrite packet Markdown, approve capabilities,
change lifecycle status, run adapters, or accept artifacts.
`schema-check` reports packet-run compatibility against the current schema
contract, and `migrate` updates only safe JSON compatibility metadata. Neither
command rewrites filled packet Markdown or changes governance ownership.
The current contract is documented in
[`policy/ARTIFACT_HARNESS_SCHEMA_V0.md`](./policy/ARTIFACT_HARNESS_SCHEMA_V0.md).

Explicit keyword route check:

```bash
./scripts/brain.sh packet-route "<utterance>" --path <workspace-folder>
./scripts/brain.sh packet-route "<utterance>" --path <workspace-folder> --create
./scripts/brain.sh packet-route "<utterance>" --path <workspace-folder> --json
./scripts/brain.sh packet-route "<utterance>" --path <workspace-folder> --id <packet-id> --json
```

`packet-route` uses deterministic keywords from [`policy/system_hub.toml`](./policy/system_hub.toml)
and [`contexts/team_alias_registry.json`](./contexts/team_alias_registry.json).
It is a CLI/agent-called route helper; it does not automatically intercept every
free-form Codex GUI or CLI phrase unless the agent invokes this route check.
It also includes a conservative natural artifact-mission intake layer for
phrases like `make a review-ready methods appendix` or `幫我整理這個投影片任務`.
That layer requires deterministic deliverable plus action/quality cues before
it allows packet creation; underspecified hints such as `help with this
artifact` ask for clarification instead of writing misleading packets.
It recognizes registered front doors such as `HR`, `Team Architect`, `CAP`,
runtime mapping, and requirement-form language. Artifact-production requests
remain SPEC-first even when the utterance names a downstream packet; HR-only
staffing requests stay HR-only and do not create Artifact Harness runs.

`--path <workspace-folder>` is both the mission target and the packet output
workspace. Generated packet chains live under
`<workspace-folder>/contexts/artifact_harness_runs/<packet-id>/`; the registry
is `<workspace-folder>/contexts/artifact_harness_registry.json`.
Smoke verification should run in a temporary workspace, or clean up any
`smoke-artifact-harness` registry/run output before committing repo content.

Artifact-harness improvement rounds use a lightweight evidence exchange under
[`contexts/artifact_harness_improvement_rounds/`](./contexts/artifact_harness_improvement_rounds/):
prompt, developer report, reviewer notes, and verification evidence.

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

### Role-library adoption

- [`policy/ROLE_LIBRARY_ADOPTION_WORKFLOW_V0.md`](./policy/ROLE_LIBRARY_ADOPTION_WORKFLOW_V0.md)
  - how third-party role libraries are converted from raw snapshots into local roles

### Multi-agent runtime adapters

- [`policy/MULTI_AGENT_RUNTIME_ADAPTERS_V0.md`](./policy/MULTI_AGENT_RUNTIME_ADAPTERS_V0.md)
  - how external multi-agent runtimes can execute local operating packets without replacing local role or coordination policy

### Artifact Harness workflow

- [`policy/ARTIFACT_HARNESS_WORKFLOW_V0.md`](./policy/ARTIFACT_HARNESS_WORKFLOW_V0.md)
  - template-first artifact workflow from user mission to verification/review
- [`contexts/team_alias_registry.json`](./contexts/team_alias_registry.json)
  - keyword families for HR, Artifact Harness SPEC, Team Operating Packet, CAP, and runtime mapping
- [`templates/artifact_harness/artifact_harness_spec.template.md`](./templates/artifact_harness/artifact_harness_spec.template.md)
  - artifact rules, contract, acceptance, and boundaries
- [`templates/human_resources/hr_staffing_packet.template.md`](./templates/human_resources/hr_staffing_packet.template.md)
  - staffing, role fit, role boundaries, and Team Architect handoff
- [`templates/team_architect/capability_access_packet.template.md`](./templates/team_architect/capability_access_packet.template.md)
  - skill, plugin, tool authorization, approval gates, and runtime allowlist

### Local agents

- [`agents/README.md`](./agents/README.md)
  - workspace-owned agent definitions and adaptation notes
- [`agents/native/team-architect.md`](./agents/native/team-architect.md)
  - applies the machine-wide coordination policy to a specific team and task
- [`agents/native/hr.md`](./agents/native/hr.md)
  - compatibility entrypoint for the `Human Resources` team surface

### Local teams

- [`teams/README.md`](./teams/README.md)
  - workspace-owned team surfaces that can be invoked as one partner
- [`teams/human-resources/AGENTS.md`](./teams/human-resources/AGENTS.md)
  - canonical `Human Resources` team surface for staffing, role sourcing, role design, and staffing-side handoff
- [`templates/team_architect/team_operating_packet.template.md`](./templates/team_architect/team_operating_packet.template.md)
  - default output template when `Team Architect` instantiates collaboration for a chosen team
- [`templates/team_architect/team_architect_handoff_brief.template.md`](./templates/team_architect/team_architect_handoff_brief.template.md)
  - default handoff template when `HR` must pass a non-trivial collaboration problem to `Team Architect`
- [`templates/team_architect/open_multi_agent_runtasks_mapping.template.md`](./templates/team_architect/open_multi_agent_runtasks_mapping.template.md)
  - optional runtime mapping template when a `Team Architect` packet should execute through `open-multi-agent` `runTasks()`

### Named team aliases

- [`policy/NAMED_TEAM_ALIAS_ROUTING_V0.md`](./policy/NAMED_TEAM_ALIAS_ROUTING_V0.md)
  - policy for treating stable local teams as direct natural-language entrypoints
- [`contexts/team_alias_registry.json`](./contexts/team_alias_registry.json)
  - machine-readable alias registry; currently registers `HR` -> `Human Resources`

### Multi-agent pilot

- [`policy/VIS_MATH_MULTI_AGENT_PILOT_V0.md`](./policy/VIS_MATH_MULTI_AGENT_PILOT_V0.md)
  - current pilot for role + artifact + protocol + convergence

### Third-party role references

- [`references/third_party/README.md`](./references/third_party/README.md)
  - read-only third-party role and template snapshots
- [`references/third_party/agency-agents.index.md`](./references/third_party/agency-agents.index.md)
  - local curation notes for the `agency-agents` raw role library
- [`references/third_party/agency-agents.capability-diff.md`](./references/third_party/agency-agents.capability-diff.md)
  - how the `agency-agents` snapshot differs from local policy and adoption workflow
- [`references/third_party/open-multi-agent.index.md`](./references/third_party/open-multi-agent.index.md)
  - local curation notes for the `open-multi-agent` runtime framework snapshot
- [`references/third_party/open-multi-agent.runtime-diff.md`](./references/third_party/open-multi-agent.runtime-diff.md)
  - how the `open-multi-agent` runtime maps to local `HR`, `Team Architect`, and execution-adapter policy

### Portability and setup

- [`PORTABILITY_GUIDE.md`](./PORTABILITY_GUIDE.md)
- [`docs/SETUP_PORTABILITY.md`](./docs/SETUP_PORTABILITY.md)
- [`docs/DEPENDENCY_BASELINE.md`](./docs/DEPENDENCY_BASELINE.md)
- [`docs/CONFIG_REFERENCE.md`](./docs/CONFIG_REFERENCE.md)
- [`docs/RUNTIME_ARTIFACT_POLICY.md`](./docs/RUNTIME_ARTIFACT_POLICY.md)
- [`docs/PORTABILITY_CHECKLIST.md`](./docs/PORTABILITY_CHECKLIST.md)

## What This Workspace Is Not

This workspace is not:

- the permanent home for all functional project work
- a replacement for canonical source-of-truth documents
- proof that every experimental feature is already globally safe
- a server-first orchestration product
- a requirement to leave Codex CLI or GUI for routine packet assembly

Concrete implementation work should often happen in a separate functional session or project folder, then be folded back here after convergence.

## Portability Note

This folder is designed to be partially portable to GitHub, but not every file is equally portable.

Portable by intent:

- `AGENTS.md`
- `PRINCIPLES.md`
- `policy/`
- `references/third_party/`
- selected reusable templates
- selected durable context artifacts

Machine-local or runtime-derived artifacts should be treated more carefully.
See [`PORTABILITY_GUIDE.md`](./PORTABILITY_GUIDE.md).

The core exported governance scripts are currently standard-library based.
See [`docs/DEPENDENCY_BASELINE.md`](./docs/DEPENDENCY_BASELINE.md).
