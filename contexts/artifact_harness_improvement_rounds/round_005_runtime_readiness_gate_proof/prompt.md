# Prompt 5: Runtime Readiness Gate Proof

## Context

We are continuing `codex-cns` Artifact Harness improvement rounds.

`codex-cns` is a Codex-native agent coordination kit. It does not assume a
persistent server and does not require users to leave Codex CLI/GUI. It turns
artifact-production quality contracts, staffing, capability authorization, and
runtime mapping into agent-readable files and templates so Codex can assemble
task forms and execution boundaries inside the same working folder.

Completed rounds:

- Round 000 established the improvement-round evidence exchange.
- Round 001 added the missing `hr_staffing_packet` slot.
- Round 002 added lifecycle/status/resume metadata and commands.
- Round 003 added replay evidence and fixed the manifest-derived packet path
  read boundary.
- Round 004 added provenance/source tracking for existing packet runs.

For this round, focus only on runtime readiness and CAP gate proof. Do not run
an external runtime adapter. Do not implement full open-multi-agent execution.
Do not add a server, daemon, database, or orchestration UI.

## Problem

The workflow now has a runtime mapping packet and a Capability Access Packet
(CAP), but there is still no executable check that the mapping is actually
constrained by CAP.

This creates a practical risk:

- a runtime mapping can look present even if it does not trace to CAP
- a mapping can claim approval gates while still allowing CLI execution
- future Codex agents may treat runtime mapping text as execution permission
- evidence from replay/provenance can show packet state but not whether runtime
  invocation is blocked, allowed, or requires an enforceable approval surface

Prompt 5 should close that gap with a same-folder runtime readiness report.
The report is preflight evidence only. It must not become approval authority,
artifact acceptance, runtime ownership, or actual runtime execution.

## Goal

Add a minimal, repo-native runtime readiness command that reads an existing
Artifact Harness packet run and produces a structured report showing whether
the runtime mapping is CAP-traced, whether approval gates require an enforceable
API surface, and whether CLI execution is blocked when gates are present.

Suggested command:

```bash
./scripts/brain.sh artifact-harness runtime-check --path <workspace> --id <packet-id> --json
```

Another predictable command name is acceptable if documented, but it must remain
under the `artifact-harness` command family.

## Required Behavior

1. Add a non-executing runtime readiness command.
   - It must inspect an existing packet run, manifest, lifecycle status, CAP,
     runtime mapping, replay evidence if present, and provenance ledger if
     present.
   - It must not invoke open-multi-agent, spawn agents, call external tools, or
     execute a runtime adapter.
   - It must not approve capabilities or accept artifacts.
   - It must return structured JSON when `--json` is supplied.

2. Persist a runtime readiness report inside the target workspace.
   - Use the existing packet run directory:
     `<workspace>/contexts/artifact_harness_runs/<packet-id>/`.
   - Suggested file:
     - `runtime_readiness_report.json`
   - The report must not rewrite packet Markdown, lifecycle metadata, manifest,
     replay evidence, or provenance ledger.
   - Regenerating the report may overwrite only `runtime_readiness_report.json`.

3. Validate CAP trace and runtime mapping alignment.
   - The report should identify at least:
     - source CAP packet path
     - source Team Operating Packet path
     - whether runtime mapping declares a source CAP
     - whether runtime mapping includes CAP-derived authorized capabilities
     - whether runtime mapping includes denied/withheld capabilities
     - whether runtime mapping records CAP approval gates
     - whether runtime mapping states runtime exposure boundaries
   - Missing or unresolved fields should produce findings and keep readiness
     conservative.

4. Validate approval-gated execution surface.
   - If CAP or runtime mapping indicates approval gates are required, the
     report must require an enforceable API surface, such as TypeScript API
     `runTasks()` with approval callbacks.
   - If approval gates are required and the mapping allows CLI execution, the
     report must fail readiness with a finding such as
     `approval_gate_requires_enforceable_api`.
   - If approval gates are required and there is no explicit human approval
     evidence, the report must not claim execution authorization.
   - Lifecycle status alone must never count as approval.
   - The `oma` CLI path must be treated as non-enforcing for approval-gated
     execution.

5. Separate readiness from authorization and execution.
   - Use distinct fields such as:
     - `runtime_invocation_ready`
     - `execution_authorized`
     - `required_execution_surface`
     - `approval_gates_required`
     - `blocking_findings`
   - `execution_authorized` should remain `false` unless the implementation can
     point to explicit approval evidence. Do not invent approval.
   - A clean preflight may say the mapping is ready to be inspected or invoked
     through the required surface, but the report itself must not grant
     permission.

6. Keep same-workspace and read-boundary guarantees.
   - All generated report paths must stay under the target workspace.
   - Manifest-derived packet paths must continue to be validated before reading.
   - Expected refusal/error cases in `--json` mode must emit parseable JSON.
   - Do not read manifest packet paths outside the target workspace.

7. Use example-driven validation in tests.
   - Add regression tests for at least:
     - default scaffold: report is JSON-parseable, conservative, and not
       execution-authorized
     - CAP-traced runtime mapping: report detects CAP trace
     - approval gate + CLI allowed conflict: readiness fails with the expected
       blocking finding
     - no approval gate + CLI allowed scenario: report does not raise the gated
       CLI conflict, while still not granting execution authorization unless
       explicit approval evidence exists
     - manifest packet path outside target workspace: parseable refusal before
       reading outside content
   - These tests should use temporary workspaces, not durable repo-local packet
     output.

8. Use the Vis_Math Lecture1 packet run as a real continuity smoke.
   - Target workspace:
     `/Users/tom/Documents/PHD/Vis_Math/Slides/Lecture1`
   - Prefer the existing packet id:
     `vis-math-lecture1-team-smoke`
   - Do not overwrite packet Markdown.
   - Writing `runtime_readiness_report.json` under that existing target
     workspace run is allowed.
   - If the run is missing or blocked, report a structured refusal rather than
     forcing creation.

9. Update docs minimally.
   - README / AGENTS / workflow policy should mention the runtime readiness
     report only where needed.
   - Do not market this as runtime execution.
   - Do not claim complete automation.
   - Keep runtime adapters as execution layers only.

## Constraints

- Do not start Prompt 6.
- Do not stage files.
- Do not revert unrelated worktree changes.
- Do not write durable smoke packet output under the `codex-cns` repo
  `contexts/` directory.
- Temp workspace smoke output is fine.
- The real Vis_Math runtime readiness report is allowed because this prompt
  names that target workspace explicitly.
- Do not add new dependencies unless there is a clear local reason.

## Exchange Artifacts

Create or update:

- `contexts/artifact_harness_improvement_rounds/round_005_runtime_readiness_gate_proof/developer_report.md`
- `contexts/artifact_harness_improvement_rounds/round_005_runtime_readiness_gate_proof/verification.md`

Use the round 000 protocol spirit:

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

- temp workspace runtime-check command returns parseable JSON
- `runtime_readiness_report.json` is written under the target workspace packet
  run directory
- runtime-check does not rewrite packet Markdown
- missing packet run returns structured refusal JSON under `--json`
- corrupted manifest packet path outside the target workspace refuses before
  reading packet contents
- approval gate + CLI allowed conflict produces a blocking finding
- no approval gate + CLI allowed scenario does not produce the gated CLI
  conflict
- Vis_Math Lecture1 runtime-check smoke succeeds or fails fast with a
  structured reason
- `find contexts -maxdepth 3 \( -path '*artifact_harness_runs*' -o -name 'artifact_harness_registry.json' \) -print` returns no `codex-cns` repo smoke output

## Acceptance

- There is a repeatable CLI path from an existing packet run to a runtime
  readiness report.
- JSON output includes at least:
  - `id`
  - `target_path`
  - `run_dir`
  - `manifest`
  - `status`
  - `runtime_readiness_report_path`
  - `runtime_invocation_ready`
  - `execution_authorized`
  - `approval_gates_required`
  - `required_execution_surface`
  - `blocking_findings`
  - `checks`
  - `refused`
  - `reason`
- Approval-gated runtime execution is blocked from CLI-only paths.
- Runtime mapping readiness traces to CAP and Team Operating Packet.
- Lifecycle status alone is not treated as approval.
- The report is explicitly preflight/evidence only, not acceptance, approval,
  runtime execution, or governance ownership.
