# Prompt 10: Roster CV Inspection Capability Wiring

## Context

Prompt 9 added a visual Quality loop. That was the right direction, but the
user now wants actual CV capability to be part of the loop because the highest
value failures are visual:

- text hidden by another layer
- important visual elements occluded
- overlap after layout changes
- unreadable scale or contrast
- slide/render/video frame mismatch
- playback or screenshot-only defects not visible from source text

The goal is not a heavy autonomous CV service. Roster should remain
Codex-native, same-folder, no persistent server, and usable from CLI/GUI. CV
inspection should be a capability that the Quality loop can request and CAP can
authorize.

## Goal

Wire a minimal but real `cv_inspection` capability into Roster's visual Quality
loop, packet scaffolds, and health diagnostics.

Core invariant:

- Artifact production remains SPEC-first.
- Quality loop attaches to production; it must not block packet creation.
- CV inspection is a tool/capability request, not a governance owner.
- CAP owns authorization for Computer Use, screenshot capture, playback, OCR,
  render/export, frame sampling, and vision-model review.
- Runtime adapters remain execution layers only.
- Do not claim `@roster` works as an installed mention.

## Required Changes

Implement the smallest useful version on branch
`gh-1-roster-quality-self-check`.

Likely files:

- `scripts/system_hub.py`
- `scripts/test_system_hub.py`
- `skills/roster/SKILL.md`
- `README.md`
- `contexts/artifact_harness_usage_experience/README.md`
- `contexts/artifact_harness_usage_experience/README.target-user-experience.draft.md`
- `contexts/artifact_harness_usage_experience/TARGET_README_INSTRUCTION.md`
- add a prompt 10 developer report

### 1. Route JSON

Extend `packet-route --json` so visual Quality loop output includes a structured
`cv_inspection` object when visual production or visual quality-only prompts are
detected.

Suggested shape:

```json
{
  "quality_loop": {
    "detected": true,
    "artifact_mode": "visual",
    "recommended_iterations": "2-3",
    "cv_inspection": {
      "requested": true,
      "mode": "agent_vision_review",
      "inputs": ["rendered image", "screenshot", "video frame"],
      "checks": [
        "text occlusion",
        "key element occlusion",
        "layout overlap",
        "contrast/readability",
        "missing expected content",
        "slide/render/video mismatch"
      ],
      "capability_requests": [
        "screenshot_capture",
        "playback_or_frame_sampling",
        "ocr_text_readability",
        "vision_model_review"
      ],
      "authorization_owner": "Capability Access Packet",
      "execution_boundary": "advisory until CAP authorizes the needed tools"
    }
  }
}
```

Adjust exact fields if needed, but keep the output parseable and agent-friendly.

### 2. Packet Scaffolds

When `artifact-harness --create` or `packet-route --create` is invoked for a
visual artifact mission, generated packet scaffolds should carry the CV
inspection request forward:

- Artifact Harness SPEC: acceptance/check section should mention visual
  inspection targets when detected.
- Team Operating Packet: task/quality plan should include a bounded visual
  inspect-and-correct loop, and may assign a Quality reviewer / visual inspector
  role when useful.
- Capability Access Packet: include a clearly bounded CV inspection capability
  request:
  - screenshot capture
  - playback or frame sampling for video
  - OCR/readability check when text is present
  - vision-model review of screenshot/frame/image
  - Computer Use or app playback only when needed
  - explicit note that CAP authorizes tools only and does not accept artifacts
- Runtime mapping: if these capabilities are exposed, they must be CAP-derived;
  do not make runtime mapping the owner.

This can be scaffolded from mission keywords; it does not need perfect NL
understanding.

### 3. Roster Health

Extend `roster-health --json` with a local-only CV capability diagnostic.

Minimum:

- report a `cv_inspection_capability` object
- include supported local input modes: screenshot, image, rendered frame, video
  frame, OCR/readability review
- include provider/auth state if supplied by optional CLI args or env vars
  (`--cv-provider`, `--cv-auth-env`, or reasonable env defaults such as
  `ROSTER_CV_PROVIDER`)
- do not make remote calls
- do not print secrets
- do not fail normal health when CV is not configured unless the user explicitly
  requested a CV provider/auth check

If adding args is too large, at least add local env-based detection and tests
with temp env.

### 4. Docs / Skill Behavior

Update Roster docs so ordinary user-facing behavior is natural:

```text
我會把這個當成需要看畫面的任務：先產出第一版，擷取畫面或播放片段，檢查文字有沒有被遮住、重點元素是否清楚，再修 1-2 輪。

需要截圖、播放、OCR 或 vision review 時，我會把它當成工具能力處理。
```

Avoid first-touch governance jargon. Internal docs can mention CAP boundaries.
Do not say Roster cannot do slide/render/video work.

## Regression Tests

Add focused tests for at least:

1. Visual production route:

```text
Roster, create a review-ready Lecture1 slide with CV quality check
```

Expected:

- `recommended_route == "artifact_harness_workflow"`
- `create_allowed is True`
- `quality_loop.detected is True`
- `quality_loop.cv_inspection.requested is True`
- `quality_loop.cv_inspection.capability_requests` includes screenshot or
  vision review capability

2. Visual quality-only route:

```text
Roster，幫我用CV檢查 Lecture1 影片畫面品質
```

Expected:

- `recommended_route == "roster_quality_direction"`
- `create_allowed is False`
- `quality_loop.cv_inspection.requested is True`
- checks include occlusion/readability/overlap

3. Packet scaffold creation:

Use temp workspace:

```bash
./scripts/brain.sh packet-route "Roster, create a review-ready Lecture1 slide with CV quality check" --path <tmp> --id smoke-cv-quality --create --json
```

Expected generated CAP/TOP/SPEC/runtime mapping under `<tmp>/contexts/...`
contain CV inspection / screenshot / vision review capability wording, while
preserving ownership boundaries.

4. Health JSON:

`roster-health --json` should include `cv_inspection_capability`, parse as JSON,
and not fail merely because CV provider auth is absent unless explicitly
requested.

## Verification

Run:

```bash
python3 -m py_compile scripts/system_hub.py scripts/test_system_hub.py
python3 scripts/test_system_hub.py
git diff --check
```

Manual smokes:

```bash
./scripts/brain.sh packet-route "Roster, create a review-ready Lecture1 slide with CV quality check" --path /tmp --json
./scripts/brain.sh packet-route "Roster，幫我用CV檢查 Lecture1 影片畫面品質" --path /tmp --json
tmp=$(mktemp -d)
./scripts/brain.sh packet-route "Roster, create a review-ready Lecture1 slide with CV quality check" --path "$tmp" --id smoke-cv-quality --create --json
./scripts/brain.sh roster-health --path "$tmp" --json
rm -rf "$tmp"
```

Confirm no repo-local `contexts/artifact_harness_registry.json` or
`contexts/artifact_harness_runs/` smoke output remains.

## Report

Write a report to:

`contexts/artifact_harness_usage_experience/developer_reports/prompt_10_roster_cv_inspection_capability.report.md`

Then commit and push the branch. Do not merge PR #2.
