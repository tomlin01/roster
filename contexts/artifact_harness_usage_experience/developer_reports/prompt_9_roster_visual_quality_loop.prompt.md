# Prompt 9: Roster Visual Artifact Quality Loop

## Context

Roster Quality direction now exists, but real usage shows the main quality
problem is not ordinary prose. The frequent practical failures are visual or
rendered artifact issues:

- text hidden under another layer
- important elements occluded
- poor contrast or unreadable scale
- slide, scene, render, and video frame mismatch
- layout overlap after layering
- render/playback-only defects that are not visible from source text alone

The value of the Harness/SPEC direction is not only defining acceptance. It
should make the first artifact production self-iterating enough to catch obvious
visual defects before the user sees the result.

## Goal

Add a Roster Quality Loop concept for artifact production, especially visual,
slide, video, UI, screenshot, image, render, and presentation work.

This should be implemented as a Roster production behavior and advisory packet
route signal, not as a separate permanent agent by default.

Core invariant:

- Quality is built into Roster.
- Artifact production remains SPEC-first.
- Quality loop attaches to production; it must not block packet creation.
- Visual artifacts should plan 2-3 bounded quality iterations before delivery.
- A Quality reviewer role can be assigned when useful, but the loop/process is
  the primary concept.
- Computer Use, screenshot, playback, render, OCR, or similar tools are
  capabilities governed by CAP, not owned by Quality.

## Required Changes

Implement the smallest useful version in the PR #2 branch.

Likely files:

- `skills/roster/SKILL.md`
- `README.md`
- `contexts/artifact_harness_usage_experience/README.md`
- `contexts/artifact_harness_usage_experience/README.target-user-experience.draft.md`
- `contexts/artifact_harness_usage_experience/TARGET_README_INSTRUCTION.md`
- `scripts/system_hub.py`
- `scripts/test_system_hub.py`
- this developer report or a new prompt 9 report file

Expected behavior:

1. Roster docs must say visual artifact production should include a short
   quality loop before delivery.
2. The loop should be described as:
   - produce initial artifact
   - inspect visible output
   - detect occlusion, overlap, unreadable text, contrast, missing expected
     content, and slide/video/render mismatch
   - apply focused correction
   - repeat for 2-3 bounded iterations or until no material issue remains
3. The first user-facing explanation should remain short and practical. Avoid
   exposed governance jargon unless the user asks for debug/review detail.
4. Do not say Roster cannot do slide, scene, render, or video work.
5. `packet-route --json` should expose structured advisory context for visual
   Quality loop when the utterance is a visual artifact production task or an
   explicit visual quality request.
6. The advisory context must not turn a production task into a Quality-only
   route. A concrete visual deliverable still routes to
   `artifact_harness_workflow` with `create_allowed=true`.
7. Quality-only visual prompts may route to `roster_quality_direction`, but
   should include the loop guidance as structured JSON.

Suggested JSON shape:

```json
{
  "quality_loop": {
    "detected": true,
    "artifact_mode": "visual",
    "recommended_iterations": "2-3",
    "inspection_targets": [
      "text occlusion",
      "key element occlusion",
      "layout overlap",
      "contrast/readability",
      "missing expected content",
      "slide/render/video mismatch"
    ],
    "capability_boundary": "visual inspection tools require CAP authorization when used"
  }
}
```

The exact field names can be adjusted, but keep the output parseable and
agent-friendly.

## User-Facing Example

Good ordinary response shape:

```text
我會把這類 visual artifact 預設加一個短 Quality loop：

- 先產出第一版
- 看畫面裡文字、重點元素和圖層有沒有互相遮住
- 修掉明顯的可讀性或畫面一致性問題
- 再重看 1-2 輪，沒有明顯問題才交付

如果需要播放或截圖檢查，我會把那當成工具能力來處理。
```

## Regression Tests

Add focused tests for at least:

1. Production task with visual artifact and quality:

```text
Roster, create a review-ready Lecture1 slide with Quality loop
```

Expected:

- `recommended_route == "artifact_harness_workflow"`
- `create_allowed is True`
- `quality_loop.detected is True`
- `quality_loop.recommended_iterations` indicates `2-3`

2. Pure visual quality request:

```text
Roster，幫我檢查 Lecture1 影片畫面品質
```

Expected:

- `recommended_route == "roster_quality_direction"`
- `quality_loop.detected is True`
- JSON includes occlusion/readability/overlap style inspection targets

## Verification

Run:

```bash
python3 -m py_compile scripts/system_hub.py scripts/test_system_hub.py
python3 scripts/test_system_hub.py
git diff --check
```

Manual JSON smokes:

```bash
./scripts/brain.sh packet-route "Roster, create a review-ready Lecture1 slide with Quality loop" --path /tmp --json
./scripts/brain.sh packet-route "Roster，幫我檢查 Lecture1 影片畫面品質" --path /tmp --json
```

## Deliverables

- Commit the fix on branch `gh-1-roster-quality-self-check`.
- Push the branch if verification passes.
- Update or add a developer report.
- Final response should list changed files, tests run, manual smoke results,
  and remaining risks.
