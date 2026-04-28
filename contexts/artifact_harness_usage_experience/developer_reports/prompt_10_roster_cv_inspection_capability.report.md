# Prompt 10 Report: Roster CV Inspection Capability Wiring

## Issue

Prompt 9 added the visual Quality loop, but the loop still treated visual
inspection as prose guidance. Prompt 10 required a minimal real
`cv_inspection` capability request so Roster can carry screenshot, playback,
OCR/readability, and vision-model review needs through route JSON, packet
scaffolds, and health diagnostics without making CV a governance owner.

## Changes

- Added structured `quality_loop.cv_inspection` JSON for visual production and
  visual Quality-only Roster prompts.
- Kept artifact production SPEC-first. Visual/CV Quality attaches to production
  and does not block packet creation.
- Added CV inspection carry-through in generated packet scaffolds:
  - Artifact Harness SPEC lists visual/CV inspection acceptance targets.
  - Team Operating Packet includes a bounded visual inspect-and-correct loop.
  - Capability Access Packet requests screenshot capture, playback/frame
    sampling, OCR/readability, vision-model review, and Computer Use/app
    playback only when needed.
  - Runtime mapping records a CAP-derived CV trace without owning
    authorization.
- Extended `roster-health --json` with a local-only
  `cv_inspection_capability` diagnostic, optional `--cv-provider` and
  `--cv-auth-env` checks, supported local input modes, and no remote calls or
  secret printing.
- Updated Roster docs and skill wording so ordinary first-touch behavior says
  the task needs visible-output inspection, while internal docs preserve CAP
  authorization boundaries.

## Route Behavior

Production request:

```text
Roster, create a review-ready Lecture1 slide with CV quality check
```

returns:

- `recommended_route: artifact_harness_workflow`
- `create_allowed: true`
- `quality_loop.detected: true`
- `quality_loop.cv_inspection.requested: true`
- CV capability requests including `screenshot_capture` and
  `vision_model_review`

Quality-only request:

```text
Roster，幫我用CV檢查 Lecture1 影片畫面品質
```

returns:

- `recommended_route: roster_quality_direction`
- `create_allowed: false`
- `quality_loop.cv_inspection.requested: true`
- checks for occlusion, readability, overlap, missing content, and
  slide/render/video mismatch

## Boundary Preservation

- Artifact production remains SPEC-first.
- Quality loop remains production behavior and advisory self-check context.
- CV inspection is a capability request, not a role owner, governance owner, or
  acceptance owner.
- CAP owns authorization for screenshot capture, playback/frame sampling,
  OCR/readability, vision-model review, Computer Use/app playback, and related
  approval gates.
- Runtime adapters remain execution layers only.
- The docs still say `@roster` is a future product target, not a verified
  installed Codex mention.

## Validation

Passed:

- `python3 -m py_compile scripts/system_hub.py scripts/test_system_hub.py`
- `python3 scripts/test_system_hub.py`
- `git diff --check`
- `./scripts/brain.sh packet-route "Roster, create a review-ready Lecture1 slide with CV quality check" --path /tmp --json`
- `./scripts/brain.sh packet-route "Roster，幫我用CV檢查 Lecture1 影片畫面品質" --path /tmp --json`
- temp-workspace packet creation:
  `./scripts/brain.sh packet-route "Roster, create a review-ready Lecture1 slide with CV quality check" --path <tmp> --id smoke-cv-quality --create --json`
- temp-workspace health smoke:
  `./scripts/brain.sh roster-health --path <tmp> --json`

The health smoke returned degraded only because the normal LLM provider was not
configured in that temporary environment. The CV diagnostic itself remained
local-only, reported `not_configured`, made no remote call, and did not print
secrets.

## Remaining Risk

This wires the capability request, packet scaffolding, and local diagnostics. It
does not execute screenshot capture, playback, OCR, or vision-model review by
itself; those remain task-specific tool uses that CAP must authorize when a real
artifact run needs them.
