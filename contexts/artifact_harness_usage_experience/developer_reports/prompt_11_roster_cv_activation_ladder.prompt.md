# Prompt 11: Roster CV Activation Ladder

## Context

Prompt 10 wired `cv_inspection` as a structured capability request. That is
necessary but not sufficient. The user clarified the real product need:

- CV should not be treated as passive prose guidance.
- Users should not be asked to provide screenshots first.
- Roster should try to obtain visual evidence itself when safe and locally
  available.
- User-provided screenshots/frames are the final fallback.
- If no visual evidence is inspected, Roster must not present visual quality as
  complete.

The practical goal is to make CV useful for slide, render, UI, image, and video
work where failures are often visible only in the final output:

- text hidden by another layer
- important elements occluded
- layout overlap
- unreadable scale or contrast
- missing expected visible content
- slide/render/video mismatch
- playback or screenshot-only defects

## Goal

Implement a minimal, repo-native **CV Activation Ladder** for Roster.

The ladder should make visual Quality behave like this:

1. Prefer existing rendered/exported visual files when present.
2. If safe and locally available, render/export the artifact into inspectable
   images or frames.
3. If GUI playback or local app state is needed, request or use CAP-governed
   Computer Use / screenshot / playback / frame sampling capabilities.
4. If OCR or vision-model review is available, run or request it as a
   CAP-governed inspection capability.
5. Only when Roster cannot obtain visual evidence, ask the user to provide a
   screenshot or frame.

This is an activation and evidence policy. It does not need to implement a
remote vision call in this prompt.

## Core Invariants

- Artifact production remains SPEC-first.
- Visual Quality attaches to production and does not block packet creation.
- CV is a capability/evidence layer, not a governance owner.
- CAP authorizes screenshot, playback, frame sampling, OCR, vision-model review,
  Computer Use, and app playback.
- Quality consumes visual evidence and proposes fixes.
- Artifact Harness SPEC remains the source of acceptance.
- Runtime adapters remain execution layers only.
- Do not claim `@roster` works as an installed Codex mention.
- Do not make a persistent server, daemon, database, or separate orchestration
  UI.

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
- add a prompt 11 developer report

### 1. Route JSON

Extend `packet-route --json` visual Quality output so `quality_loop.cv_inspection`
contains an activation/evidence plan, not only capability names.

Suggested shape:

```json
{
  "quality_loop": {
    "detected": true,
    "cv_inspection": {
      "requested": true,
      "activation_ladder": [
        {
          "step": "use_existing_visual_evidence",
          "preference": 1,
          "inputs": ["rendered image", "screenshot", "exported video frame"],
          "fallback": false
        },
        {
          "step": "render_or_export_inspection_artifact",
          "preference": 2,
          "capability_owner": "Capability Access Packet",
          "fallback": false
        },
        {
          "step": "local_capture_or_playback",
          "preference": 3,
          "capability_requests": ["screenshot_capture", "playback_or_frame_sampling", "computer_use_or_app_playback"],
          "capability_owner": "Capability Access Packet",
          "fallback": false
        },
        {
          "step": "ocr_or_vision_model_review",
          "preference": 4,
          "capability_requests": ["ocr_text_readability", "vision_model_review"],
          "capability_owner": "Capability Access Packet",
          "fallback": false
        },
        {
          "step": "ask_user_for_screenshot_or_frame",
          "preference": 5,
          "fallback": true
        }
      ],
      "no_visual_evidence_policy": "visual quality is limited until a screenshot, render, frame, or playback evidence is inspected",
      "evidence_required_for_visual_acceptance": true
    }
  }
}
```

Exact field names may differ, but keep them structured, parseable, and stable
enough for tests. The key is that user-provided screenshots are explicitly the
last fallback.

### 2. Packet Scaffolds

Generated packets for visual missions should carry the ladder forward:

- Artifact Harness SPEC:
  - state that visual acceptance requires inspected visual evidence when visual
    output is part of the artifact
  - state that without visual evidence, only non-visual/text/structure checks
    can be marked complete
- Team Operating Packet:
  - include the activation ladder as task procedure
  - include an inspect -> finding -> fix -> recheck loop
  - make user-provided screenshot/frame the final fallback
- Capability Access Packet:
  - request capabilities for render/export evidence, screenshot capture,
    playback/frame sampling, OCR/readability, vision-model review, and
    Computer Use/app playback only when needed
  - preserve authorization-only boundary
- Runtime mapping:
  - expose visual inspection steps only when CAP explicitly authorizes them
  - keep runtime as execution layer only

### 3. Visual Quality Finding Shape

Add a structured finding shape in docs/scaffolds/tests so future CV output is
actionable. It should include:

- artifact / slide / frame / timecode when available
- region or visible location when possible
- issue type
- severity
- evidence source
- suggested fix owner
- suggested correction
- recheck condition

This does not need to run a vision model now. It needs to be the expected output
contract when visual evidence is inspected.

### 4. Health Diagnostics

Extend `roster-health --json` to distinguish:

- CV capability configured/auth status
- visual evidence acquisition availability
- remote call status
- whether default health is blocked

Minimum structured fields:

- `cv_inspection_capability.status`
- `cv_inspection_capability.remote_call_attempted`
- `cv_inspection_capability.visual_evidence_acquisition`
- `cv_inspection_capability.user_evidence_fallback`
- `cv_inspection_capability.no_visual_evidence_policy`

Default health must not fail merely because no CV provider is configured.
Explicit `--cv-provider` / `--cv-auth-env` checks may degrade if missing, as
Prompt 10 already does.

### 5. User-Facing Behavior

Update Roster skill/docs so the ordinary first-touch response can say this
without governance jargon:

```text
我會先嘗試自動取得畫面證據，例如 render/export、截圖、播放片段或抽 frame；如果環境拿不到畫面，再請你提供截圖。

沒有畫面證據時，我只能做非視覺品質檢查，不能把畫面驗收當成完成。
```

Avoid saying Roster cannot do slide/render/video work. The point is that visual
acceptance needs visual evidence.

## Regression Tests

Add or update focused tests for:

1. Visual production route:

```text
Roster, create a review-ready Lecture1 slide with CV quality check
```

Expected:

- `recommended_route == "artifact_harness_workflow"`
- `create_allowed is True`
- `quality_loop.cv_inspection.requested is True`
- activation ladder exists
- final activation step asks user for screenshot/frame as fallback
- `evidence_required_for_visual_acceptance is True`

2. Visual quality-only route:

```text
Roster，幫我用CV檢查 Lecture1 影片畫面品質
```

Expected:

- `recommended_route == "roster_quality_direction"`
- `create_allowed is False`
- activation ladder exists
- no visual evidence policy is present

3. Packet scaffold creation in temp workspace:

```bash
./scripts/brain.sh packet-route "Roster, create a review-ready Lecture1 slide with CV quality check" --path <tmp> --id smoke-cv-ladder --create --json
```

Expected generated SPEC/TOP/CAP/runtime mapping under `<tmp>/contexts/...`
contain:

- activation ladder / evidence acquisition wording
- no-visual-evidence limited quality wording
- actionable visual finding shape
- CAP authorization boundary
- runtime execution-layer boundary

4. Health JSON:

`roster-health --json` should include evidence acquisition fields and parse as
JSON. Default health may be degraded by normal missing LLM provider state, but
must not fail solely because CV provider auth is absent unless explicitly
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
./scripts/brain.sh packet-route "Roster, create a review-ready Lecture1 slide with CV quality check" --path "$tmp" --id smoke-cv-ladder --create --json
./scripts/brain.sh roster-health --path "$tmp" --json
rm -rf "$tmp"
find contexts -maxdepth 3 \( -name 'artifact_harness_registry.json' -o -path 'contexts/artifact_harness_runs/*' \) -print
```

## Report

Write a report to:

`contexts/artifact_harness_usage_experience/developer_reports/prompt_11_roster_cv_activation_ladder.report.md`

Report:

- changed files
- activation ladder fields added
- route behavior
- packet scaffold behavior
- health JSON behavior
- verification commands and results
- remaining risks

Commit and push the branch if verification passes. Do not merge PR #2.
