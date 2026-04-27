# Reviewer Notes

## Findings

No blocking P0/P1/P2 findings remain after the follow-up fix.

The initial Round 003 implementation introduced a P1 read-boundary issue: `artifact-harness replay` trusted manifest-derived packet paths, so a corrupted manifest could point a packet field outside the target workspace and have replay read it for heuristics. The follow-up moved manifest packet path validation into `load_artifact_harness_lifecycle_state()`, so `status`, `resume`, and `replay` now reject those paths before exposing packet summaries or reading packet contents.

## Review Summary

- `artifact-harness replay` remains an observation/continuity layer, not runtime execution, approval, or acceptance.
- Manifest packet paths are now resolved and checked under the target workspace before lifecycle commands use them.
- Refusal JSON is structured with `reason=manifest_packet_path_outside_target_workspace`, `offending_packet_key`, and `attempted_path`.
- Existing replay evidence is not rewritten when replay refuses a corrupted manifest path.
- The Vis_Math Lecture1 smoke output remains in `/Users/tom/Documents/PHD/Vis_Math/Slides/Lecture1/contexts/`, which matches the same-workspace model.

## Verification

- `python3 -m py_compile scripts/system_hub.py scripts/test_system_hub.py` passed.
- `python3 scripts/test_system_hub.py` passed.
- Independent temp reproduction passed: corrupted manifest SPEC path to `../outside_secret.md`; replay/status both returned non-zero parseable JSON refusal; outside file content was not leaked; heuristic packet fields were not emitted; prior replay evidence was unchanged.
- Repo-local smoke cleanup check passed: no `contexts/artifact_harness_registry.json` or `contexts/artifact_harness_runs/` output remained under `codex-cns`.
- Vis_Math registry and replay evidence both parsed as valid JSON.

## Remaining Risks

- Replay evidence JSON is still an implementation contract, not a separate versioned schema.
- Open-field counts are shallow heuristics and must not be treated as artifact acceptance.
- Existing older runs without `packet_status.json` still fail fast rather than being migrated.
- Replay evidence overwrites the current evidence snapshot for a run; it does not keep revision history.
