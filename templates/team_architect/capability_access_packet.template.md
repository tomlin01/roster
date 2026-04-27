# Capability Access Packet

## Metadata

- owner:
- status: draft/reviewed/approved
- target_mission:
- generated_by:
- source_artifact_harness_spec:
- source_team_operating_packet:

## Fill Notes

- Fill this template from the Artifact Harness SPEC, Team Operating Packet, and
  available local skills, plugins, and tools.
- Keep this file agent-readable Markdown in the same workspace folder.
- This packet authorizes capabilities and gates only. It does not choose roles,
  collaboration patterns, artifact acceptance, or runtime ownership.

## Purpose

- why capability access is needed:
- expected artifact or runtime outcome from source packets:
- capability risk level:

## Authorized Capabilities

- skill:
  - allowed use:
  - scope:
  - output expected:
  - approval gate:
- plugin:
  - allowed use:
  - scope:
  - output expected:
  - approval gate:
- tool:
  - allowed use:
  - scope:
  - output expected:
  - approval gate:

## Runtime Allowlist

- exposed skills:
- exposed plugins:
- exposed tools:
- withheld capabilities:
- allowlist source:

## Denied Or Deferred Capabilities

- capability:
  - reason:
  - fallback:

## Access Boundaries

- allowed files or folders:
- allowed external services:
- allowed network use:
- allowed writes:
- forbidden writes:
- secrets or credentials rule:
- runtime byproducts rule:

## Approval Gates

- gate:
  - trigger:
  - approval owner:
  - allowed continuation:
  - rejected fallback:

## Runtime Exposure Constraints

- runtime adapter from Team Operating Packet:
- runtime mapping artifact from Team Architect:
- capabilities to expose:
- capabilities to withhold:
- approval gates to enforce:
- evidence to return:

This section constrains runtime exposure only. It does not choose the runtime
adapter and does not create the runtime task graph.

## Evidence For Verification

- access evidence:
- capability exposure evidence:
- approval gate evidence:
- closeout evidence to return:

This section supplies evidence to verification/review. It does not decide
artifact acceptance.

## Must Not Do

- choose or redesign staffing
- replace the Team Architect operating packet
- change the Artifact Harness SPEC rules, contract, acceptance, or boundaries
- own verification or artifact acceptance
- make the runtime adapter a governance owner
- claim complete automation without executable evidence

## Open Questions

- 
