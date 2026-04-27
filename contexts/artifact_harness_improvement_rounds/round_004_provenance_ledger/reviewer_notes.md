# Reviewer Notes

## Round Metadata

- round: `round_004_provenance_ledger`
- reviewed by: external reviewer pass in Codex desktop thread
- date: `2026-04-27`
- prompt file: `contexts/artifact_harness_improvement_rounds/round_004_provenance_ledger/prompt.md`
- developer report: `contexts/artifact_harness_improvement_rounds/round_004_provenance_ledger/developer_report.md`
- verification evidence: `contexts/artifact_harness_improvement_rounds/round_004_provenance_ledger/verification.md`

## Findings

No blocking P0/P1/P2 findings were found in this review pass.

## Review Summary

- `artifact-harness provenance --path <workspace> --id <packet-id> --json` is wired as a repo-native CLI/GUI-friendly command.
- The command writes `packet_provenance_ledger.json` in the existing packet run directory under the target workspace.
- The command reuses the lifecycle loader, so manifest packet paths are validated before packet contents are read.
- The provenance ledger records coarse source categories and packet-chain source relationships without taking ownership of approval, acceptance, verification, runtime selection, or runtime execution.
- The runtime mapping provenance includes both `source_team_operating_packet` and `source_capability_access_packet`.
- The Vis_Math Lecture1 smoke run now has a valid provenance ledger at:
  `/Users/tom/Documents/PHD/Vis_Math/Slides/Lecture1/contexts/artifact_harness_runs/vis-math-lecture1-team-smoke/packet_provenance_ledger.json`

## Reviewer Verification

- `python3 -m py_compile scripts/system_hub.py scripts/test_system_hub.py`
  - result: passed
- `python3 scripts/test_system_hub.py`
  - result: passed
  - output summary: `system hub test harness checks passed`
- independent temp workspace smoke:
  - created a packet chain with absolute `brain.sh`
  - added `REVIEW_SENTINEL_R004` to `artifact_harness_spec.md`
  - ran `artifact-harness provenance --json`
  - parsed JSON output
  - verified `packet_provenance_ledger.json` exists in the packet run directory
  - verified the sentinel remained in packet Markdown
  - verified runtime mapping provenance traces to CAP
- independent missing-run refusal smoke:
  - ran `artifact-harness provenance --json` for a missing packet id
  - verified non-zero exit
  - parsed structured JSON refusal
  - verified `reason=missing_packet_run`
  - verified no ledger was written
- independent manifest-boundary smoke:
  - created a packet chain
  - generated an initial provenance ledger
  - corrupted `packet_manifest.json` so `artifact_harness_spec` pointed outside the target workspace
  - verified `artifact-harness provenance --json` refused before reading outside content
  - verified `reason=manifest_packet_path_outside_target_workspace`
  - verified outside sentinel text was not leaked in stdout
  - verified the existing ledger was not rewritten
- Vis_Math smoke:
  - reran `artifact-harness provenance --path /Users/tom/Documents/PHD/Vis_Math/Slides/Lecture1 --id vis-math-lecture1-team-smoke --json`
  - parsed JSON output
  - parsed the persisted ledger with `json.loads`
- repo cleanup check:
  - `find contexts -maxdepth 3 \( -path '*artifact_harness_runs*' -o -name 'artifact_harness_registry.json' \) -print`
  - result: returned empty

## Remaining Risks

- The provenance ledger is a coarse source ledger, not a field-complete Markdown parser.
- `schema_version=1` is an implementation contract, not yet a separately documented JSON schema.
- The command overwrites the latest provenance snapshot for a packet run; it does not retain provenance revision history.
- Source category counts include category records that explain absent evidence, such as no runtime output, so consumers should read the note fields rather than treating every nonzero count as proof of completed work.

