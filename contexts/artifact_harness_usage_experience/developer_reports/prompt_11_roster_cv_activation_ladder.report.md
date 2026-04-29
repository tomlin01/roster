# Prompt 11 Report: Roster CV Activation Ladder

## Issue

Prompt 10 made CV inspection a structured capability request, but Roster still
needed an evidence policy for how to obtain visual evidence before asking the
user for screenshots. Prompt 11 required a minimal CV activation ladder for
slide, render, UI, image, and video work.

## Changes

- Extended `quality_loop.cv_inspection` route JSON with:
  - an ordered activation ladder
  - a no-visual-evidence policy
  - `evidence_required_for_visual_acceptance`
  - an actionable visual finding shape
- Kept artifact production SPEC-first and Quality/CV as an attached
  capability/evidence layer.
- Carried the ladder into generated packet scaffolds:
  - Artifact Harness SPEC requires inspected visual evidence for visual
    acceptance and limits completion when visual evidence is missing.
  - Team Operating Packet includes the activation ladder, an
    inspect -> finding -> fix -> recheck loop, and final user-evidence fallback.
  - Capability Access Packet requests render/export evidence, screenshot
    capture, playback/frame sampling, Computer Use/app playback,
    OCR/readability, and vision-model review only when needed.
  - Runtime mapping exposes visual inspection steps only when CAP authorizes
    them and keeps runtime as an execution layer.
- Extended `roster-health --json` with visual evidence acquisition,
  user-evidence fallback, no-visual-evidence policy, and default-health blocking
  diagnostics.
- Updated Roster docs and skill instructions with the plain first-touch wording
  that Roster tries to obtain visual evidence first and asks the user for a
  screenshot/frame only when the environment cannot provide one.

## Boundary Preservation

- Artifact Harness SPEC remains the source of acceptance.
- Visual Quality attaches to production and does not block packet creation.
- CV remains a capability/evidence layer, not a governance owner.
- CAP owns authorization for screenshot, playback, frame sampling, OCR,
  vision-model review, Computer Use, app playback, and render/export evidence
  when needed.
- Runtime adapters remain execution layers only.
- `@roster` remains a future product target, not a verified installed Codex
  mention.

## Validation

Passed:

- `python3 -m py_compile scripts/system_hub.py scripts/test_system_hub.py`
- `python3 scripts/test_system_hub.py`
- `git diff --check`
- `./scripts/brain.sh packet-route "Roster, create a review-ready Lecture1 slide with CV quality check" --path /tmp --json`
- `./scripts/brain.sh packet-route "Roster，幫我用CV檢查 Lecture1 影片畫面品質" --path /tmp --json`
- temp-workspace packet creation:
  `./scripts/brain.sh packet-route "Roster, create a review-ready Lecture1 slide with CV quality check" --path <tmp> --id smoke-cv-ladder --create --json`
- temp-workspace health smoke:
  `./scripts/brain.sh roster-health --path <tmp> --json`

The health smoke returned degraded only because the normal LLM provider was not
configured in that temporary environment. The CV diagnostic itself remained
local-only, reported `not_configured`, exposed visual evidence acquisition and
user-evidence fallback fields, made no remote call, and did not block default
health.
