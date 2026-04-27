# Reviewer Notes

## Round Metadata

- round: `round_006_keyword_intake_front_door`
- reviewer: `Codex`
- date: `2026-04-27`

## Findings

No blocking P0/P1/P2 findings remain after the follow-up boundary-match fix.

The initial review found one P1 false-positive route: `HR` matched inside `through`, causing `walk me through runtime mapping` to route as `human_resources`. That was sent back as a follow-up and is now resolved by boundary-aware keyword matching plus regression coverage.

## Review Summary

Round006 now provides an executable, deterministic, CLI/GUI-friendly `packet-route` front door for registered Artifact Harness, HR, Team Architect, CAP, runtime mapping, and requirement-form language.

Artifact-production utterances remain SPEC-first. HR-only staffing utterances stay HR-only. Downstream-only packet requests do not create new chains unless an artifact mission or existing packet id justifies a safe path.

## Verification

- `python3 -m py_compile scripts/system_hub.py scripts/test_system_hub.py` passed.
- `python3 scripts/test_system_hub.py` passed.
- Temp workspace smoke passed for HR artifact, HR-only, requirement-form create, Team Architect, CAP, runtime mapping downstream-only, unmatched utterance, HR-only create refusal, absolute command shape, and existing-id runtime-check routing.
- Follow-up boundary smoke passed:
  - `walk me through runtime mapping` recognized `runtime_mapping` only, did not recognize `human_resources`, and did not allow create.
  - `walk through the requirement form` recognized `artifact_harness_workflow`, did not recognize `human_resources`, and allowed create.
  - `ask HR to check staffing` still recognized `human_resources`.
  - `HR, help me design roles for this artifact` still routes SPEC-first with HR handoff.
- `find contexts -maxdepth 3 \( -path '*artifact_harness_runs*' -o -name 'artifact_harness_registry.json' \) -print` returned empty.

## Remaining Risks

- Routing remains deterministic keyword matching, not a broad natural-language classifier.
- HR-only output is advisory because there is no separate executable HR packet command yet.
- JSON output is implementation-stable for current tests but not yet a versioned schema.
