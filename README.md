# Roster

`Roster` is the human-facing name for this Codex-native
staffing-and-coordination kit. It helps Codex turn artifact-producing work into
a clear task brief, role plan, tool-access boundary, execution map, and review
checklist inside the same workspace folder.

It does not require a persistent server, daemon, database, or separate
orchestration UI. You use it from ordinary Codex CLI or Codex GUI sessions.
`codex-cns` remains the internal repository and historical name.

## Basic Use

In ordinary Codex chat, name `Roster` and describe the artifact task in natural
language:

```text
Roster, 幫我把這個 slide 任務安排好。
```

For a first team setup, Codex should answer briefly:

```text
我已經把 Lecture1 的工作隊形整理好了：

- Student：看懂不懂、哪裡會卡
- Teacher：決定講解順序和例題
- Video Production：處理畫面、旁白和輸出
- Quality Management：做播放檢查和成品驗收

之後你可以直接說：
`用 Lecture1 team 跑下一個 unit`

我會照這個隊形把任務分下去，該改 slide、scene、render 或影片時再進到對應步驟。
```

Future install target:

```text
@roster 幫我把這個 slide 任務安排好。
```

Current status: `@roster` is a product target, not a verified installed Codex
mention, plugin/app mention, or slash command. The repo-owned `roster` skill is
installable, and the repo-native `packet-route` adapter recognizes `Roster`,
literal `@roster`, and artifact-context `PM`, but those are Codex/reviewer-called
route helpers, not automatic Codex GUI or CLI mention interception. Do not rely
on `@roster` as the current user invocation until a real Codex mention layer
proves it.

Specialized aliases exist for review, staffing, and debugging, but ordinary use
should start with `Roster`.

You should not need to remember or type `brain.sh`, `packet-route`, or
`artifact-harness` during ordinary work. The current verified command fallback
is documented separately below.

## Quality Direction

Quality is built into Roster as direction-setting and self-check behavior. It
helps Codex decide what to check now, what to improve later, and how to turn the
accepted task contract into practical review steps.

When a user asks for Quality, Codex should infer the likely quality direction
from the artifact and task context. If the direction is ambiguous, ask one short
question about the quality bar before changing files.

For ordinary first-touch Quality replies, keep the answer short and
human-facing:

```text
我會把 Quality 分成兩層：

短期先看這次 unit 能不能交付：
- 內容是否講得清楚
- slide / scene / video 是否一致
- 有沒有明顯漏掉的步驟

長期則看這個 Lecture1 team 是否需要固定檢查流程：
- 每個 unit 完成後都做 playback check
- 每次修改 scene 後確認 slide 對應
- 最後輸出前做一次完整驗收

我會先用短期檢查幫你把這次任務穩住，再把重複出現的問題記成長期改善項目。
```

Quality has two working layers:

- Short-term correction: stabilize the current artifact, unit, scene, render,
  table, draft, or output so it can be delivered.
- Long-term improvement: record repeated issues as process, team, checklist, or
  template improvements for future work.

When an Artifact Harness SPEC exists, its acceptance checks remain the source of
truth. Quality consumes those checks and turns them into self-check behavior; it
does not replace the SPEC, authorize tools, choose runtime execution, or own
final acceptance.

## Workspace And Output

The active Codex workspace is the default output root.

Generated packet files are written under the workspace where the artifact work
is happening, not under the `Roster` kit repo by default:

```text
<active-workspace>/contexts/artifact_harness_runs/<packet-id>/
<active-workspace>/contexts/artifact_harness_registry.json
```

If Codex cannot tell which workspace should receive the files, it should ask one
short location question before writing anything.

## When To Use It

Use `Roster` when a task has enough moving parts that Codex should make the
working boundary explicit before acting:

- a document, slide deck, dataset, code change, video, or research artifact must
  be produced or revised
- several roles or review perspectives are useful
- tool, plugin, LLM, filesystem, network, or runtime access needs to be clear
- the task may need to be resumed later
- a reviewer should be able to inspect why Codex acted the way it did

The kit creates agent-readable packet files in your target workspace. These
files are the audit trail Codex and future reviewers can use.

## What Codex Creates

For non-trivial artifact work, Codex creates a packet run in the target
workspace:

```text
<workspace>/contexts/artifact_harness_runs/<packet-id>/
<workspace>/contexts/artifact_harness_registry.json
```

The usual packet chain is:

```text
user mission
-> task brief
-> staffing / role plan
-> collaboration plan
-> tool-access and approval boundary
-> optional runtime map
-> verification / review checklist
```

Formal packet names:

- Artifact Harness SPEC: rules, contract, acceptance, and boundaries
- HR staffing packet: staffing and role design only
- Team Operating Packet: collaboration pattern, task graph, shared artifacts,
  and convergence plan
- Capability Access Packet: skills, plugins, tools, approval gates, and runtime
  allowlist
- runtime mapping: optional execution wiring for an adapter

Codex should explain the human outcome first and link these formal files after
that.

## When It Stays Lightweight

Not every request needs the full packet chain.

Codex should stay lightweight when the task is just:

- a quick question
- a small single-file edit
- a staffing check
- a short note
- a one-step verification

In those cases, Codex should answer or act directly and only create packet files
if the task grows into artifact production, tool authorization, review evidence,
or resumable work.

## Resume

You should be able to resume with ordinary language:

```text
Roster, 這個任務現在卡在哪裡？
```

Target behavior: Codex inspects the current workspace, registry, and recent
packet runs. If there is one likely active run, Codex summarizes current status,
blocker, next action, and relevant file links. If several runs are possible,
Codex asks one short disambiguation question using human-readable mission titles
or artifact names.

Current verified fallback: lifecycle resume commands require
`--id <packet-id>`. Active-run discovery by ordinary language remains target
experience wording until a no-id discovery path is verified.

## Permissions And Tool Access

The kit makes tool access visible without making the user read governance files
first.

Codex should summarize access in plain language:

```text
No external tools needed.
```

```text
Needs filesystem writes only.
```

```text
Needs LLM/provider access; no external runtime.
```

```text
Needs approval before network/plugin/runtime execution.
```

The formal allowlist and approval gates live in the Capability Access Packet.
Runtime adapters remain execution layers only; they do not own governance.

## Install Or Reconstruct On Another Machine

Current status: Roster has a repo-owned `roster` Codex skill source and a
repo-native install command. This registers a skill-style surface for future
Codex threads; it does not register `@roster` as a Codex mention, plugin/app
mention, or slash command.

On a new machine:

1. Clone or copy the `Roster` kit.
2. Open Codex in the kit folder.
3. Choose an existing target workspace where packet output should be written.
4. Install the `roster` skill into the local Codex home.
5. Configure local Codex auth or provider credentials for any LLM/provider path
   you intend to use.
6. Run the current verified health check shown in the next section.
7. Start a new Codex thread and type `Roster, <your artifact task>`.
8. Treat `configured`, `missing_provider`, and `missing_auth` as setup status,
   not artifact acceptance.

Repo-portable setup is limited to the files in this repo: `scripts/brain.sh`,
`scripts/system_hub.py`, `policy/system_hub.toml`,
`contexts/team_alias_registry.json`, `skills/roster`, templates, and policy
docs. Machine-local state remains outside the repo: Codex login/session state,
provider API keys, personal memory, caches, model downloads, installed skill
copies, and local overlays.

## Current Verified Fallback

These commands are for Codex, reviewers, setup, and debugging. They are not the
basic user-facing path. Run them from the `Roster` kit root.

Current setup health check:

```bash
./scripts/brain.sh roster-install --codex-home ~/.codex --json
./scripts/brain.sh roster-health --path <workspace-folder> --json
./scripts/brain.sh roster-health --codex-home ~/.codex --path <workspace-folder> --json
./scripts/brain.sh roster-health --path <workspace-folder> --provider openai --auth-env OPENAI_API_KEY --json
```

`roster-install` copies the repo-owned `skills/roster` skill into the requested
Codex skills root and writes an install manifest that points back to this kit.
`roster-health` verifies that the repo can see the Roster route through
`packet-route`, optionally sees the installed `roster` skill when `--codex-home`
or `--skills-root` is supplied, creates a smoke packet under the target
workspace, removes that smoke output by default, and confirms that no persistent
server, daemon, database, separate UI, or external control plane is required.
Its LLM/provider status is local setup diagnostics: `configured` means the named
credential environment variable is present; `missing_provider` and
`missing_auth` identify setup gaps. It does not make a remote model call, does
not register `@roster`, and does not print secrets. Use `--keep-artifacts` only
when debugging the smoke packet itself.

Explicit keyword route checks:

```bash
./scripts/brain.sh packet-route "<utterance>" --path <workspace-folder>
./scripts/brain.sh packet-route "<utterance>" --path <workspace-folder> --create
./scripts/brain.sh packet-route "<utterance>" --path <workspace-folder> --json
./scripts/brain.sh packet-route "<utterance>" --path <workspace-folder> --id <packet-id> --json
```

`packet-route` uses deterministic keywords from [`policy/system_hub.toml`](./policy/system_hub.toml)
and [`contexts/team_alias_registry.json`](./contexts/team_alias_registry.json).
It is a CLI/agent-called route helper; it does not automatically intercept every
free-form Codex GUI or CLI phrase unless Codex invokes this route check.
It also includes a conservative natural artifact-mission intake layer for
phrases like `make a review-ready methods appendix` or `幫我整理這個投影片任務`.
That layer requires deterministic deliverable plus action/quality cues before
it allows packet creation; underspecified hints such as `help with this
artifact` ask for clarification instead of writing misleading packets.
It recognizes registered front doors such as `HR`, `Team Architect`, `CAP`,
runtime mapping, `Roster`, literal `@roster` text, artifact-context `PM`, and
requirement-form language. `Roster`, literal `@roster` text, and unambiguous
artifact-task `PM` route to the Artifact Harness workflow when the route helper
is called. Artifact-production requests remain SPEC-first even when the
utterance names a downstream packet; HR-only staffing requests stay HR-only and
do not create Artifact Harness runs.

`--path <workspace-folder>` is both the mission target and the packet output
workspace. Generated packet chains live under
`<workspace-folder>/contexts/artifact_harness_runs/<packet-id>/`; the registry
is `<workspace-folder>/contexts/artifact_harness_registry.json`.
Smoke verification should run in a temporary workspace, or clean up any
`smoke-artifact-harness` registry/run output before committing repo content.

## Reviewer/Debug Command Reference

Minimal packet entrypoint from the kit root:

```bash
./scripts/brain.sh artifact-harness "<mission>" --path <workspace-folder>
./scripts/brain.sh artifact-harness "<mission>" --path <workspace-folder> --json
```

Packet lifecycle and evidence entrypoints from the kit root:

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

Artifact-harness improvement rounds use a lightweight evidence exchange under
[`contexts/artifact_harness_improvement_rounds/`](./contexts/artifact_harness_improvement_rounds/):
prompt, developer report, reviewer notes, and verification evidence.

## Ownership Boundaries

Keep the layers separate:

- Artifact Harness owns rules, contract, acceptance, and boundary.
- HR owns staffing and role design only.
- PM remains an optional natural alias for project-planning language, not the
  primary product name.
- Team Architect owns collaboration pattern, shared artifacts, task graph,
  convergence, and CAP generation.
- Capability Access Packet owns skill, plugin, tool authorization, approval
  gates, and runtime allowlist.
- Runtime adapters execute; they do not become governance owners.

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
  - machine-readable alias registry; currently registers `Roster` / literal `@roster` route-helper text / artifact-context `PM` -> Artifact Harness workflow, and `HR` -> `Human Resources`

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
