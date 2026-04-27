# Prompt 7: Artifact Harness Schema And Migration

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
- Round 005 added runtime readiness preflight evidence.
- Round 006 added deterministic keyword intake/front-door routing and fixed the
  short-alias boundary false positive.

For this round, focus only on schema versioning, compatibility checks, and a
safe migration surface for Artifact Harness packet runs and command JSON.

Do not run external runtime adapters. Do not implement runtime execution. Do not
add a server, daemon, database, orchestration UI, or new dependency.

## Problem

Artifact Harness now writes multiple machine-readable files and JSON command
payloads:

- `artifact_harness_registry.json`
- `packet_manifest.json`
- `packet_status.json`
- `artifact_replay_evidence.json`
- `packet_provenance_ledger.json`
- `runtime_readiness_report.json`
- `artifact-harness ... --json` output
- `packet-route ... --json` output

Most of these payloads include some version hints, but there is no single,
documented compatibility contract for future Codex agents to rely on.

This creates several practical risks:

- future agents may scrape incidental JSON fields instead of using a stable
  contract
- older packet runs may be treated as current even when required fields are
  missing
- schema drift may silently break `resume`, `replay`, `provenance`,
  `runtime-check`, or `packet-route`
- a migration could accidentally rewrite filled Markdown packets
- Round 009 Human UX work could be blocked by unclear command output contracts

Prompt 7 should stabilize the contract without turning the kit into a heavy
framework.

## Goal

Add a minimal, same-folder, CLI-friendly schema and migration layer for Artifact
Harness packet runs.

The layer should let a future Codex agent answer:

- Which schema version is this packet run using?
- Is this run compatible with the current kit?
- What required files or fields are missing?
- Can this run be safely migrated without touching filled Markdown?
- What command output contract can another agent consume without scraping
  Markdown?

Suggested command shape:

```bash
./scripts/brain.sh artifact-harness schema-check --path <workspace> --id <packet-id> --json
./scripts/brain.sh artifact-harness migrate --path <workspace> --id <packet-id> --json
```

Another predictable subcommand name is acceptable if documented, but keep it
under the existing `artifact-harness` family.

## Required Behavior

1. Define the current schema contract.
   - Add a lightweight policy or reference doc for Artifact Harness schema
     versions.
   - It should identify the current version for:
     - registry
     - manifest
     - lifecycle/status sidecar
     - replay evidence
     - provenance ledger
     - runtime readiness report
     - command JSON envelope for `artifact-harness`
     - command JSON envelope for `packet-route`
   - Do not over-specify every text field. Focus on stable keys, required
     files, compatibility, and migration behavior.

2. Add a non-destructive `schema-check` command.
   - It must inspect an existing packet run and return structured JSON under
     `--json`.
   - It must read only files inside the target workspace after validating
     manifest-derived paths.
   - It must not rewrite packet Markdown or generated JSON files.
   - It must report at least:
     - `id`
     - `target_path`
     - `run_dir`
     - `current_schema_version`
     - `supported_schema_version`
     - `compatible`
     - `migration_required`
     - `checked_files`
     - `missing_files`
     - `missing_required_fields`
     - `warnings`
     - `blocking_findings`
     - `refused`
     - `reason`

3. Add a conservative `migrate` command.
   - It must operate only on existing packet runs.
   - It may create or update schema metadata JSON sidecars and registry/manifest
     compatibility fields.
   - It must not rewrite filled packet Markdown files:
     - `artifact_harness_spec.md`
     - `hr_staffing_packet.md`
     - `team_operating_packet.md`
     - `capability_access_packet.md`
     - `open_multi_agent_runtasks_mapping.md`
   - It must fail fast with parseable JSON if required packet files are missing,
     if manifest paths point outside the target workspace, or if the run is too
     ambiguous to migrate safely.
   - It should be idempotent: running it twice should not change packet
     Markdown, create duplicate registry entries, or produce conflicting schema
     metadata.

4. Keep command JSON agent-friendly.
   - `artifact-harness schema-check --json` and `migrate --json` must emit
     parseable JSON for success and refusal paths.
   - Prefer a stable envelope such as:
     - `command`
     - `schema_version`
     - `ok`
     - `refused`
     - `reason`
     - `target_path`
     - `id`
     - `commands`
   - Do not make future agents scrape Markdown summaries.
   - Human Markdown output is fine, but JSON mode is the contract.

5. Preserve ownership boundaries.
   - Schema-check and migrate are compatibility tools only.
   - They do not approve capabilities, accept artifacts, execute runtimes,
     choose staffing, change Team Architect ownership, or alter CAP authority.
   - Lifecycle status must remain continuity metadata only; migration must not
     mark a packet as approved, executed, or verified.

6. Keep same-folder semantics.
   - All generated migration artifacts must stay under:
     `<workspace>/contexts/artifact_harness_runs/<packet-id>/`
     or the sibling registry:
     `<workspace>/contexts/artifact_harness_registry.json`
   - Do not write durable smoke packet output under the `codex-cns` repo
     `contexts/` directory.
   - Temp workspace smoke output is fine.

7. Cover older/minimal packet runs.
   - Add tests using temp workspaces that simulate:
     - a current valid packet run
     - a run missing optional generated reports
     - a run missing required packet files
     - a run with an older manifest or missing schema metadata that can be
       migrated safely
     - a run with manifest packet paths outside the target workspace
   - The migration command should distinguish safe migration from refusal.

8. Use the Vis_Math Lecture1 packet run as a real continuity smoke.
   - Target workspace:
     `/Users/tom/Documents/PHD/Vis_Math/Slides/Lecture1`
   - Prefer the existing packet id:
     `vis-math-lecture1-team-smoke`
   - Do not overwrite packet Markdown.
   - Running `schema-check` is expected.
   - Running `migrate` is allowed only if it is non-destructive and produces a
     clear report; if the run is missing or ambiguous, return a structured
     refusal instead of forcing creation.

9. Update docs minimally.
   - README / AGENTS / workflow policy should mention schema-check/migration
     only where needed.
   - Add or update a policy/reference file if that is cleaner than expanding
     README.
   - Do not market this as full automation or a stable public API beyond the
     documented current JSON contract.

## Constraints

- Do not start Prompt 8.
- Do not stage files.
- Do not revert unrelated worktree changes.
- Do not add a server, daemon, database, orchestration UI, or new dependency.
- Do not run external runtime adapters.
- Do not rename existing packet files unless there is a hard compatibility
  reason.
- Do not rewrite filled packet Markdown during schema-check or migrate.
- Preserve existing overwrite/rerun guards.

## Exchange Artifacts

Create or update:

- `contexts/artifact_harness_improvement_rounds/round_007_schema_and_migration/developer_report.md`
- `contexts/artifact_harness_improvement_rounds/round_007_schema_and_migration/verification.md`

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

- temp workspace `artifact-harness schema-check --json` returns parseable JSON
- schema-check does not rewrite packet Markdown
- temp workspace `artifact-harness migrate --json` returns parseable JSON
- migrate is idempotent
- migrate does not rewrite packet Markdown, including when a sentinel line is
  added to a packet file before migration
- a safe older/minimal run can be migrated or clearly reported as compatible
- missing required packet file returns structured refusal JSON
- manifest packet path outside target workspace refuses before reading outside
  content
- Vis_Math Lecture1 schema-check succeeds or fails fast with a structured reason
- Vis_Math migrate, if run, is non-destructive and reported clearly
- repo-local artifact-harness output check stays empty:

```bash
find contexts -maxdepth 3 \( -path '*artifact_harness_runs*' -o -name 'artifact_harness_registry.json' \) -print
```

## Acceptance

- There is a repeatable CLI path to check schema compatibility for an existing
  packet run.
- There is a conservative, non-destructive migration path for safe older runs.
- JSON success and refusal paths are parseable and stable enough for another
  Codex agent to consume.
- Migration never rewrites filled packet Markdown.
- Schema checks preserve same-workspace read/write boundaries.
- The schema layer is compatibility evidence only, not governance, approval,
  artifact acceptance, runtime execution, or ownership transfer.
- Round 007 has developer report and verification evidence.
