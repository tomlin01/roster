# Verification Evidence

## Round Metadata

- round: `round_007_schema_and_migration`
- prompt file: `contexts/artifact_harness_improvement_rounds/round_007_schema_and_migration/prompt.md`
- developer report: `contexts/artifact_harness_improvement_rounds/round_007_schema_and_migration/developer_report.md`
- reviewer notes: `contexts/artifact_harness_improvement_rounds/round_007_schema_and_migration/reviewer_notes.md`
- date: `2026-04-28`

## Reported Verification

Commands reported by the developer.

- command: `python3 -m py_compile scripts/system_hub.py scripts/test_system_hub.py`
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - reported result: passed
  - evidence path or output summary: command exited `0`
- command: `python3 scripts/test_system_hub.py`
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - reported result: passed
  - evidence path or output summary: `system hub test harness checks passed`
- command: temp workspace Round007 schema smoke
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - reported result: passed
  - evidence path or output summary: `/var/folders/_s/p_gdfcgs2_s4dd0rgz1sk1wc0000gn/T/codex-cns-r007-schema-smoke-final-3_48chd5/`; JSON parsed for schema-check/migrate, second migrate had `changed_files=[]`, missing packet refused with `schema_migration_blocked`
- command: `/Users/tom/Documents/PHD/codex-cns/scripts/brain.sh artifact-harness schema-check --path /Users/tom/Documents/PHD/Vis_Math/Slides/Lecture1 --id vis-math-lecture1-team-smoke --json`
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - reported result: passed
  - evidence path or output summary: parseable JSON; `compatible=true`, `migration_required=false`, `schema_metadata.exists=true`
- command: Vis_Math migrate smoke with Markdown hashes before/after
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - reported result: passed
  - evidence path or output summary: wrote only `packet_manifest.json`, `packet_schema_metadata.json`, and `artifact_harness_registry.json`; all packet Markdown hashes unchanged
- command: non-reference Markdown link check
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - reported result: passed
  - evidence path or output summary: `missing=0 files_checked=86`
- command: `find contexts -maxdepth 3 \( -path '*artifact_harness_runs*' -o -name 'artifact_harness_registry.json' \) -print`
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - reported result: passed
  - evidence path or output summary: command returned no repo-local artifact-harness packet output

## Reviewer Rerun Verification

Commands actually rerun by the reviewer.

- command: `python3 -m py_compile scripts/system_hub.py scripts/test_system_hub.py`
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - rerun result: passed
  - evidence path or output summary: command exited `0`
- command: `python3 scripts/test_system_hub.py`
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - rerun result: passed
  - evidence path or output summary: `system hub test harness checks passed`
- command: independent temp workspace schema smoke
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - rerun result: passed
  - evidence path or output summary: create/schema-check/migrate/idempotence passed; sentinel line in packet Markdown remained; missing required packet migrate refusal returned parseable JSON with `reason=schema_migration_blocked`
- command: independent missing manifest field smoke
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - rerun result: passed with observation
  - evidence path or output summary: removing `mission` from `packet_manifest.json` was reported in `missing_required_fields`; `compatible` remained `true`, documented as a P3 review note
- command: `/Users/tom/Documents/PHD/codex-cns/scripts/brain.sh artifact-harness schema-check --path /Users/tom/Documents/PHD/Vis_Math/Slides/Lecture1 --id vis-math-lecture1-team-smoke --json`
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - rerun result: passed
  - evidence path or output summary: parseable JSON; `compatible=true`; `migration_required=false`; no missing files, missing required fields, warnings, or blocking findings
- command: non-reference Markdown link check
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - rerun result: passed
  - evidence path or output summary: `missing=0 files_checked=88`
- command: `find contexts -maxdepth 3 \( -path '*artifact_harness_runs*' -o -name 'artifact_harness_registry.json' \) -print`
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - rerun result: passed
  - evidence path or output summary: command returned no repo-local artifact-harness packet output

## Artifact Inspection

Generated or claimed artifacts inspected by the developer before handoff.

- artifact: `policy/ARTIFACT_HARNESS_SCHEMA_V0.md`
  - expected state: lightweight schema contract documentation
  - observed state: created and linked from README/workflow policy
  - reviewer note: this is a compatibility reference, not a governance owner
- artifact: temp smoke workspace `/var/folders/_s/p_gdfcgs2_s4dd0rgz1sk1wc0000gn/T/codex-cns-r007-schema-smoke-final-3_48chd5/`
  - expected state: temporary packet output only
  - observed state: contained temp Artifact Harness packet output used for schema and migration smoke
  - reviewer note: not repo content
- artifact: Vis_Math `packet_schema_metadata.json`
  - expected state: schema metadata sidecar under the existing named packet run
  - observed state: created by non-destructive migrate
  - reviewer note: allowed by Prompt 7 named target workspace
- artifact: Vis_Math packet Markdown files
  - expected state: unchanged by schema-check and migrate
  - observed state: five packet Markdown hashes unchanged before/after migrate
  - reviewer note: inspect directly if reviewing the real target workspace
- artifact: `contexts/artifact_harness_improvement_rounds/round_007_schema_and_migration/developer_report.md`
  - expected state: durable round handoff report
  - observed state: created
  - reviewer note: report is not a substitute for diff/test/artifact inspection
- artifact: `contexts/artifact_harness_improvement_rounds/round_007_schema_and_migration/verification.md`
  - expected state: durable verification evidence
  - observed state: created
  - reviewer note: contains reported verification only; reviewer rerun is pending

## Not Run / Unable To Run

- command or check: Prompt 8
  - reason not run: explicitly out of scope for Round 007
  - residual risk: later improvement rounds remain future work
- command or check: external runtime adapter execution
  - reason not run: explicitly out of scope for Prompt 7
  - residual risk: no runtime execution behavior is proven or changed
- command or check: formal JSON Schema validation
  - reason not run: Round 007 requested a lightweight same-folder schema layer, not a new dependency or formal validator
  - residual risk: nested JSON shapes are checked by regression tests and stable-key inspection, not by a standalone schema engine

## Verification Summary

- Syntax checks and the full system hub test suite passed.
- Schema-check and migrate return parseable JSON for success and refusal paths.
- Migration is idempotent for current runs and does not rewrite packet Markdown.
- Missing required packet files and outside-target manifest packet paths are refused safely.
- Vis_Math Lecture1 was migrated non-destructively and now schema-checks as compatible with no migration required.
- No repo-local artifact-harness smoke packet output remains under `codex-cns/contexts/`.
