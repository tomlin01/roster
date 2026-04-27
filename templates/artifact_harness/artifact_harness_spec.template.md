# Artifact Harness SPEC

## Metadata

- owner:
- status: draft/reviewed/approved
- target_mission:
- generated_by:
- expected_downstream_packet:
- autofill_source:

## Fill Notes

- Fill this template from the user mission and repo-local evidence.
- Keep this file agent-readable Markdown in the same workspace folder.
- Record unknowns as open questions instead of inventing hidden defaults.
- This SPEC is a quality contract, not a staffing plan or runtime plan.

## Mission

- user mission [source: user phrase]:
- expected artifact [source: user phrase, `--artifact`, or inference]:
- artifact location [source: user phrase, `--artifact`, repo evidence, or open question]:
- artifact consumer [source: user phrase or open question]:
- why a harness is needed [source: workflow default or user phrase]:

## Artifact Contract

- artifact type [source: user phrase, file extension, repo evidence, or inference]:
- required sections or fields [source: user phrase, repo evidence, or open question]:
- required inputs [source: user phrase, repo evidence, or open question]:
- allowed source material [source: user phrase, repo evidence, or approval question]:
- required output format [source: user phrase, artifact type, or open question]:
- required evidence [source: acceptance checks, reviewer need, or open question]:

## Rules

- invariant rules [source: user phrase, repo policy, or open question]:
- sequencing rules [source: workflow policy]:
- naming or path rules [source: packet command, user phrase, or repo policy]:
- source-use rules [source: user phrase, repo evidence, or approval question]:
- review rules [source: workflow policy, user phrase, or verification owner]:

## Acceptance Checks

- check:
  - method [source: user phrase, verification owner, repo evidence, or open question]:
  - owner [source: verification/review, user phrase, or open question]:
  - pass condition [source: user phrase, artifact contract, repo evidence, or open question]:
  - failure action [source: workflow policy, user phrase, or open question]:

## Boundaries

- in scope [source: user phrase]:
- out of scope [source: user phrase, repo policy, or open question]:
- must not change [source: repo policy or explicit user boundary]:
- user approval required for [source: approval gate]:
- deferred [source: unresolved open question]:

## Handoff

- staffing target [source: workflow policy]:
- Team Architect target [source: workflow policy]:
- capability access expected [source: Team Operating Packet need, user phrase, or open question]: yes/no
- runtime adapter expected [source: user phrase, Team Operating Packet, or open question]: yes/no
- verification or review target [source: workflow policy, user phrase, or open question]:

## Must Not Do

- choose or redesign staffing
- authorize skills, plugins, or tools
- choose runtime execution mechanics
- change memory-engine level or promotion state
- claim full automation without filled-run or executable evidence

## Open Questions

- 
