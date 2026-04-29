# Prompt 9 Report: Roster Visual Artifact Quality Loop

## Issue

Prompt 9 identified that artifact failures are often visual or rendered-output
defects, not ordinary prose defects. Examples include hidden text, layer
occlusion, unreadable contrast or scale, overlap after layout changes, and
slide/render/video mismatch.

## Changes

- Added Roster documentation for a built-in visual Quality loop on slide, scene,
  render, video, screenshot, image, UI, and presentation production.
- Kept artifact production SPEC-first. The loop attaches as production behavior
  and does not block packet creation.
- Added `quality_loop` advisory JSON to `packet-route --json` for visual
  artifact production and visual Quality-only requests.
- Kept visual inspection tools under CAP boundaries: playback, screenshot, OCR,
  render, Computer Use, and similar tools are capabilities, not owned by
  Quality.
- Added regression tests for visual production with `Quality loop` and a pure
  Chinese visual quality request.

## Route Behavior

Production request:

```text
Roster, create a review-ready Lecture1 slide with Quality loop
```

returns:

- `recommended_route: artifact_harness_workflow`
- `create_allowed: true`
- `quality_loop.detected: true`
- `quality_loop.recommended_iterations: 2-3`

Quality-only visual request:

```text
Roster，幫我檢查 Lecture1 影片畫面品質
```

returns:

- `recommended_route: roster_quality_direction`
- `create_allowed: false`
- `quality_loop.detected: true`
- inspection targets including text occlusion, layout overlap, and
  contrast/readability

## Boundary Preservation

- Quality is built into Roster.
- Artifact production remains SPEC-first.
- Quality loop guidance is advisory context, not a separate permanent agent by
  default.
- Quality may request visible-output inspection, but CAP owns tool
  authorization.

## Validation

Passed:

- `python3 -m py_compile scripts/system_hub.py scripts/test_system_hub.py`
- `python3 scripts/test_system_hub.py`
- `git diff --check`
- `./scripts/brain.sh packet-route "Roster, create a review-ready Lecture1 slide with Quality loop" --path /tmp --json`
- `./scripts/brain.sh packet-route "Roster，幫我檢查 Lecture1 影片畫面品質" --path /tmp --json`

## Remaining Risk

This implements deterministic routing evidence and Roster documentation. It
does not make Codex automatically run screenshot, playback, OCR, render, or
Computer Use checks; those remain task-specific capabilities that must be
authorized through CAP when used.
