# Prompt 10: Failure Recovery

## Context

We are continuing `codex-cns` Artifact Harness improvement rounds.

`codex-cns` is a Codex-native agent coordination kit. It does not assume a
persistent server and does not require users to leave Codex CLI/GUI. It turns
artifact-production quality contracts, staffing, capability authorization,
runtime mapping, approval evidence, and runtime invocation boundaries into
agent-readable files and templates inside the same working folder.

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
- Round 008 added approval evidence and a guarded runtime invocation dry-run
  envelope.
- Round 009 improved explicit natural intake for artifact-production missions.

Prompt 10 focuses on recovery. A packet run can now be scaffolded, resumed,
replayed, checked, approved, and dry-run guarded. The missing surface is a
structured, same-folder way for Codex to understand what to repair when the
chain is partial, blocked, inconsistent, or refused.

## Problem

Current failure modes are visible across separate commands, but the user or
agent has to infer the recovery path manually:

- packet Markdown still has open fields
- lifecycle status is `blocked`, `superseded`, or stale
- schema-check reports missing required files or compatibility drift
- approval evidence records a denial
- runtime readiness has blockers
- runtime invocation guard refuses
- older packet runs lack lifecycle/schema sidecars

Without an explicit recovery packet, future Codex runs may silently rerun,
overwrite, skip CAP approval gates, or treat runtime refusal as a generic
failure rather than a bounded next action.

## Goal

Add a non-executing repair-planning command:

```bash
./scripts/brain.sh artifact-harness repair-plan --path <workspace-folder> --id <packet-id> --json
```

It should inspect existing packet evidence and write:

```text
<workspace-folder>/contexts/artifact_harness_runs/<packet-id>/repair_plan.json
```

The repair plan is advisory evidence only. It must not rewrite packet
Markdown, change lifecycle status, approve or deny gates, edit CAP/runtime
mapping, accept artifacts, execute runtime adapters, or transfer ownership
between Artifact Harness, HR, Team Architect, CAP, verification, and runtime
adapters.

## Required Behavior

1. Add `artifact-harness repair-plan`.
   - Requires an existing packet id.
   - Returns parseable JSON with `command`, `schema_version`, `report_type`,
     `id`, `target_path`, `run_dir`, `repair_plan_path`, `needs_repair`,
     `ready_to_continue`, `summary`, `repair_items`, `commands`, `refused`,
     and `reason`.
   - Writes only `repair_plan.json` when the existing run can be inspected.
   - Does not write anything on missing-run or path-boundary refusal.

2. Inspect existing evidence without fixing it.
   - lifecycle status and status note
   - packet open-field heuristics
   - schema-check output
   - approval evidence and latest gate decisions
   - runtime readiness report
   - runtime invocation report

3. Produce explicit recovery items.
   - missing packet file: recover packet or create a new packet run
   - open packet fields: fill the owning packet field, then replay/check
   - blocked lifecycle: resolve blocker in owning packet/artifact, then mark
   - inactive lifecycle: inspect replacement or create a new packet id
   - schema incompatibility: run schema-check/migrate only when safe
   - denied approval: revise CAP/runtime boundary or record a new explicit
     approval decision
   - runtime readiness blocker: repair CAP/runtime mapping traceability or
     execution surface
   - missing approval evidence: record explicit gate decision before
     runtime-invoke
   - runtime invocation refusal: follow refusal reason, then re-run
     runtime-check and runtime-invoke dry-run

4. Keep ownership boundaries explicit.
   - Repair plan may recommend commands, but it does not perform repairs.
   - HR remains staffing only.
   - Team Architect remains collaboration/task graph/CAP generation owner.
   - CAP remains capability/gate/allowlist owner.
   - Runtime adapter remains execution layer only.

5. Integrate with schema compatibility.
   - `repair_plan.json` is an optional generated report in the schema
     contract.
   - `schema-check` should inspect its path and schema version when present.
   - Missing repair plan is a warning, not a blocker.

6. Update docs minimally.
   - README and AGENTS should list the command and boundary.
   - Workflow policy should define the recovery surface.
   - Runtime artifact policy should classify `repair_plan.json` as local
     advisory evidence.

## Required Tests

Add regression tests using temporary workspaces for at least:

1. `repair-plan --json` writes `repair_plan.json` for an inspectable run,
   reports open packet fields, and preserves packet Markdown.
2. `repair-plan --json` surfaces blocked lifecycle state and denied approval
   gates.
3. `repair-plan --json` surfaces missing approval evidence and runtime
   invocation refusal after a guarded runtime-invoke refusal.
4. Missing packet run refusal returns parseable JSON and does not write a
   repair plan.
5. `schema-check --json` includes `repair_plan` in optional generated report
   checks and reads its schema version when present.
6. Existing lifecycle, replay, provenance, runtime-check, approval,
   runtime-invoke, schema-check, migrate, packet-route, and rerun guard tests
   still pass.

## Real Workspace Smoke

Use the existing simple target workspace:

- `/Users/tom/Documents/PHD/Vis_Math/Slides/Lecture1`

Run `repair-plan` against an existing packet id if available, such as:

```text
vis-math-lecture1-team-smoke
```

Expected behavior:

- parseable JSON
- `repair_plan.json` written under the Vis_Math target workspace only
- packet Markdown hashes unchanged
- no runtime execution
- old packet runs without lifecycle metadata should return structured refusal
  instead of writing misleading repair evidence

## Constraints

- Do not start Prompt 11.
- Do not stage files.
- Do not revert unrelated worktree changes.
- Do not write durable smoke packet output under the `codex-cns` repo
  `contexts/` directory.
- Do not run external runtime adapters.
- Do not add a server, daemon, database, orchestration UI, or dependency.
- Do not weaken rerun guards, path guards, schema-check/migrate behavior,
  approval evidence behavior, runtime readiness behavior, runtime invocation
  dry-run behavior, or natural intake behavior.

## Exchange Artifacts

Create or update:

- `contexts/artifact_harness_improvement_rounds/round_010_failure_recovery/developer_report.md`
- `contexts/artifact_harness_improvement_rounds/round_010_failure_recovery/verification.md`
- `contexts/artifact_harness_improvement_rounds/round_010_failure_recovery/reviewer_notes.md`

Use the Round 000 protocol spirit:

- Findings Addressed
- Changed Files
- Generated Artifacts
- Verification Commands
- Known Non-Goals
- Remaining Risks
