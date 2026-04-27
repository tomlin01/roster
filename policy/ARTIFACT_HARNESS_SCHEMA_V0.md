# Artifact Harness Schema V0

## Purpose

This file documents the current Artifact Harness compatibility contract for
agent-readable packet runs. It is a same-folder schema and migration reference,
not a public API promise, governance owner, approval surface, artifact
acceptance rule, or runtime execution layer.

Current supported schema version: `1`.

Current command JSON envelope version: `1`.

## Versioned Artifacts

| Artifact | Current Version | Required For Compatibility |
| --- | ---: | --- |
| `contexts/artifact_harness_registry.json` | `1` | yes |
| `packet_manifest.json` | `1` | yes |
| `packet_status.json` | `1` | yes |
| `packet_schema_metadata.json` | `1` | migration metadata |
| `artifact_replay_evidence.json` | `1` | optional generated evidence |
| `packet_provenance_ledger.json` | `1` | optional generated evidence |
| `runtime_readiness_report.json` | `1` | optional generated evidence |
| `approval_evidence.json` | `1` | optional generated evidence |
| `runtime_invocation_report.json` | `1` | optional generated evidence |
| `repair_plan.json` | `1` | optional generated evidence |
| `artifact-harness ... --json` | `1` | command contract |
| `packet-route ... --json` | `1` | command contract |

## Required Packet Files

The packet run directory must contain these Markdown packets:

- `artifact_harness_spec.md`
- `hr_staffing_packet.md`
- `team_operating_packet.md`
- `capability_access_packet.md`
- `open_multi_agent_runtasks_mapping.md`

Schema tools may read these files for existence, but must not rewrite them.

## Stable JSON Keys

`schema-check --json` and `migrate --json` use this stable envelope:

- `command`
- `schema_version`
- `ok`
- `refused`
- `reason`
- `target_path`
- `id`
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
- `commands`

Other command payloads may include richer fields for their own evidence, but
future agents should rely on documented stable keys instead of scraping
Markdown summaries.

## Compatibility Rules

A packet run is compatible when required packet files exist, manifest-derived
paths stay inside the target workspace, required JSON sidecars are readable, and
no artifact declares a schema version newer than the supported version.

Missing optional generated reports are warnings, not blockers:

- `artifact_replay_evidence.json`
- `packet_provenance_ledger.json`
- `runtime_readiness_report.json`
- `approval_evidence.json`
- `runtime_invocation_report.json`
- `repair_plan.json`

Missing schema metadata or older manifest/registry compatibility fields may
require migration without making the packet run unusable.

## Migration Rules

`artifact-harness migrate` may update only JSON compatibility surfaces:

- `packet_manifest.json`
- `packet_schema_metadata.json`
- `contexts/artifact_harness_registry.json`

It must not rewrite filled packet Markdown, change lifecycle status to
`approved`/`executed`/`verified`, approve capabilities, accept artifacts,
execute runtime adapters, choose staffing, or transfer ownership between
Artifact Harness, HR, Team Architect, CAP, and runtime mapping.

Migration must refuse before reading outside content if a manifest packet path
points outside the target workspace.
