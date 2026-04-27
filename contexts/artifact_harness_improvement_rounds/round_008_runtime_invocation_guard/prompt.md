# Prompt 8: Runtime Invocation Guard And Approval Evidence

## Context

We are continuing `codex-cns` Artifact Harness improvement rounds.

`codex-cns` is a Codex-native agent coordination kit. It does not assume a
persistent server and does not require users to leave Codex CLI/GUI. It turns
artifact-production quality contracts, staffing, capability authorization, and
runtime mapping into agent-readable files and templates so Codex can assemble
task forms and execution boundaries inside the same working folder.

Completed rounds:

- Round 000 established the improvement-round evidence exchange.
- Round 001 added the explicit `hr_staffing_packet` slot.
- Round 002 added lifecycle/status/resume metadata and commands.
- Round 003 added replay evidence and fixed the manifest-derived packet path
  read boundary.
- Round 004 added provenance/source tracking for existing packet runs.
- Round 005 added non-executing runtime readiness preflight evidence.
- Round 006 added deterministic keyword intake/front-door routing.
- Round 007 added lightweight schema compatibility and migration tools.

Prompt 8 must address runtime execution proof without turning runtime adapters
into governance owners. The problem is not that we need to execute an external
runtime now. The problem is that, once a runtime adapter exists, it must be hard
for Codex or a user to bypass the Capability Access Packet and approval gates by
calling the adapter directly from a runtime mapping file.

## Problem

Round 005 added `runtime-check`, but it is still a preflight report. It proves
whether a run appears ready, not whether an actual execution launch path is
guarded.

Current remaining gaps:

- approval evidence is not first-class
- `execution_authorized` cannot become true except through fragile Markdown
  heuristics
- there is no same-folder runtime invocation envelope that records which CAP,
  runtime mapping, approval evidence, and readiness report constrained the run
- future adapters could accidentally execute from the Markdown runtime mapping
  directly
- denial/withheld capabilities are not yet enforced at a launch-envelope level

Prompt 8 should add a minimal invocation guard. It should prove that any future
adapter-backed execution path must pass through CAP/readiness/approval checks
and produce a constrained invocation artifact before execution. It should not
execute the adapter.

## Goal

Add a repo-native, same-workspace runtime invocation guard under the existing
`artifact-harness` command family.

Suggested commands:

```bash
./scripts/brain.sh artifact-harness approval --path <workspace> --id <packet-id> --gate <gate-id> --decision approved|denied --approver <label> --note "<note>" --json
./scripts/brain.sh artifact-harness runtime-invoke --path <workspace> --id <packet-id> --adapter open-multi-agent --surface typescript-runTasks --dry-run --json
```

Alternative command names are acceptable if they are predictable and documented,
but keep them under `artifact-harness`.

`runtime-invoke` in this round is a guarded dry-run/export surface only. It must
not call `open-multi-agent`, spawn agents, run tasks, or create a persistent
server. It may create a constrained invocation envelope/report in the packet run
directory when the guard passes or when a refusal needs durable evidence.

## Required Behavior

1. Add first-class approval evidence.
   - Store approval evidence under the existing target workspace packet run:
     `<workspace>/contexts/artifact_harness_runs/<packet-id>/approval_evidence.json`
   - The evidence file should include at least:
     - `schema_version`
     - `id`
     - `target_path`
     - `run_dir`
     - `updated_at`
     - `decisions`
   - Each decision should include at least:
     - `gate_id`
     - `decision`: `approved` or `denied`
     - `approver`
     - `note`
     - `source`: `user_cli` or similarly explicit source label
     - `created_at`
   - Approval evidence is evidence only. It must not rewrite CAP, TOP,
     runtime mapping, lifecycle status, packet Markdown, or artifact acceptance.
   - If multiple decisions exist for the same gate, the latest decision wins.
   - Any latest `denied` decision for a required runtime gate must block
     invocation.

2. Add an approval recording command.
   - It must operate only on an existing packet run.
   - It must require `--gate`, `--decision`, and `--approver`.
   - It must validate all paths stay under the target workspace.
   - It must emit parseable JSON under `--json` for success and refusal paths.
   - It may overwrite only `approval_evidence.json`.
   - It must not mark lifecycle status as approved or executed.

3. Add a guarded runtime invocation dry-run/export command.
   - It must operate only on an existing packet run.
   - It must recompute or load runtime readiness before producing an invocation
     envelope.
   - It must validate manifest-derived packet paths before reading packet
     content.
   - It must require a known adapter. For this round, support only:
     `open-multi-agent`.
   - It must require a known execution surface. For this round, support at
     least:
     - `typescript-runTasks`
     - `cli`
   - It must refuse `cli` whenever approval gates are required.
   - It must refuse if runtime readiness has blocking findings.
   - It must refuse if required approval evidence is missing or denied.
   - It must refuse if the requested surface does not match the readiness
     requirement.
   - It must not execute the adapter even when the guard passes.

4. Produce an invocation artifact/report inside the same packet run.
   - Suggested file:
     - `runtime_invocation_report.json`
   - If the guard passes in dry-run mode, include a constrained invocation
     envelope with at least:
     - `schema_version`
     - `id`
     - `target_path`
     - `run_dir`
     - `adapter`
     - `execution_surface`
     - `dry_run`
     - `would_execute`
     - `runtime_invocation_allowed`
     - `execution_performed`
     - `source_capability_access_packet`
     - `source_team_operating_packet`
     - `source_runtime_mapping`
     - `runtime_readiness_report_path`
     - `approval_evidence_path`
     - `approved_gates`
     - `denied_gates`
     - `exposed_capabilities`
     - `withheld_capabilities`
     - `blocking_findings`
     - `refused`
     - `reason`
   - `execution_performed` must always be `false` in this round.
   - `would_execute` may be `true` only when the guard passes, approval
     evidence is sufficient, and the requested surface is enforceable.
   - The exposed capability list must be derived from CAP/runtime readiness
     evidence and must not include denied or withheld capabilities.

5. Make the runtime policy explicit.
   - Update runtime adapter policy and workflow docs minimally to state:
     - runtime adapters must not execute directly from Markdown mapping
     - adapter execution must be preceded by the invocation guard or an
       equivalent guard with the same CAP/readiness/approval checks
     - `runtime_invocation_report.json` is evidence, not execution itself
     - `approval_evidence.json` records explicit decisions but does not replace
       CAP ownership or artifact acceptance

6. Keep same-folder and CLI-friendly behavior.
   - All durable output must be under the target workspace packet run.
   - Do not write durable smoke packet output under the `codex-cns` repo
     `contexts/` directory.
   - Human output can be Markdown, but `--json` must always be parseable for
     success and refusal paths.
   - Commands in JSON should use the absolute `brain.sh` path, so they are
     copy-paste safe from outside the repo cwd.

7. Preserve ownership boundaries.
   - Artifact Harness SPEC still owns rule/contract/acceptance/boundary.
   - HR still owns staffing/role design only.
   - Team Architect still owns collaboration pattern, task graph, shared
     artifacts, convergence, and CAP generation.
   - CAP still owns capability authorization and approval gates.
   - Runtime adapters remain execution layers only.
   - The invocation guard is an execution-boundary check, not a governance
     owner, approval authority, artifact verifier, or runtime adapter.

## Required Tests

Add regression tests using temporary workspaces for at least:

1. approval command creates parseable `approval_evidence.json` and does not
   rewrite packet Markdown.
2. latest deny overrides earlier approval for the same gate.
3. `runtime-invoke --dry-run --json` refuses when runtime readiness has
   blocking findings.
4. a gate-required run refuses without approval evidence.
5. a gate-required run refuses with `--surface cli` even when approval evidence
   exists.
6. a gate-required run with sufficient approval evidence and
   `--surface typescript-runTasks` produces a dry-run invocation report with
   `execution_performed=false`.
7. denied or withheld capabilities are not included in exposed capabilities.
8. manifest packet path outside the target workspace refuses before reading
   outside content and emits parseable JSON.
9. missing packet run returns structured refusal JSON under both approval and
   runtime-invoke commands.
10. rerunning dry-run invocation is idempotent or overwrites only
    `runtime_invocation_report.json`.

## Real Workspace Smoke

Use the existing Vis_Math Lecture1 packet run:

- target workspace:
  `/Users/tom/Documents/PHD/Vis_Math/Slides/Lecture1`
- packet id:
  `vis-math-lecture1-team-smoke`

Run `runtime-invoke --dry-run --json` against it.

Expected behavior:

- It should succeed as a command only if it can produce structured refusal or
  dry-run evidence.
- It should not execute any runtime adapter.
- It should not rewrite packet Markdown.
- It should write at most `runtime_invocation_report.json` in the existing
  packet run, if the implementation uses durable refusal/guard evidence.
- If the current Vis_Math packet is not ready or lacks approval evidence, that
  refusal is acceptable and expected.

## Constraints

- Do not start Prompt 9.
- Do not stage files.
- Do not revert unrelated worktree changes.
- Do not invoke `open-multi-agent`.
- Do not spawn agents from the runtime-invoke command.
- Do not add a server, daemon, database, orchestration UI, or new dependency.
- Do not make runtime-invoke execute real tasks in this round.
- Do not rewrite filled packet Markdown during approval recording or
  runtime-invoke.
- Preserve rerun guards for packet scaffolding.
- Preserve schema-check/migrate behavior from Round 007.

## Exchange Artifacts

Create or update:

- `contexts/artifact_harness_improvement_rounds/round_008_runtime_invocation_guard/developer_report.md`
- `contexts/artifact_harness_improvement_rounds/round_008_runtime_invocation_guard/verification.md`

Use the Round 000 protocol spirit:

- Findings Addressed
- Changed Files
- Generated Artifacts
- Verification Commands
- Known Non-Goals
- Remaining Risks

## Verification

Run at minimum:

```bash
python3 -m py_compile scripts/system_hub.py scripts/test_system_hub.py
python3 scripts/test_system_hub.py
```

Also verify:

- temp workspace approval command returns parseable JSON
- temp workspace approval evidence file parses as JSON
- temp workspace runtime-invoke refusal returns parseable JSON
- temp workspace runtime-invoke passing dry-run returns parseable JSON and
  writes only the expected invocation report
- runtime-invoke does not rewrite packet Markdown, including with a sentinel
  line in a packet file
- denied capability is not exposed in the invocation envelope
- missing run and outside-target manifest paths refuse before reading outside
  content
- Vis_Math Lecture1 runtime-invoke smoke produces structured refusal or dry-run
  evidence without runtime execution
- non-reference Markdown link check passes
- `find contexts -maxdepth 3 \( -path '*artifact_harness_runs*' -o -name 'artifact_harness_registry.json' \) -print` returns no `codex-cns` repo smoke output

## Acceptance

- Runtime invocation has a same-folder guard path before any future adapter
  execution.
- Approval evidence is first-class and explicit.
- Approval-gated execution cannot use the CLI surface.
- Denials override approvals.
- Denied or withheld capabilities are not exposed in the invocation envelope.
- Guard passing produces a dry-run invocation report/envelope but does not
  execute a runtime.
- Guard refusal is structured and parseable under `--json`.
- Docs clearly state this is execution-boundary evidence, not approval,
  artifact acceptance, runtime execution, or governance ownership.
- Round 008 has developer report and verification evidence.
