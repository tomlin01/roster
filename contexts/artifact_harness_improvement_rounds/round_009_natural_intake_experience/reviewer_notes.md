# Reviewer Notes

## Findings

No P0/P1/P2 blocking findings after reviewer completion.

### P3 - Natural intake coverage is intentionally heuristic

- File: `scripts/system_hub.py`
- Observation: Prompt 9 uses deterministic term lists rather than a semantic classifier. This keeps the command inspectable and no-server, but it will miss some natural phrasings and may need curated additions.
- Assessment: Acceptable for Prompt 9. The safer behavior is to miss and let the user continue ordinary intake rather than silently create a weak packet run.

## Review Summary

Prompt 9 is materially complete. The route command now has a more natural front
door while keeping the explicit, same-folder, no-server model.

The core behavior is covered:

- ordinary artifact task phrases can route without internal keywords
- English and Chinese examples are covered by regression tests
- underspecified artifact hints ask for clarification and refuse `--create`
- user-facing JSON fields expose intent, confidence, next-step label, message,
  visible action, and natural triggers
- Markdown now shows a `## Next Step` section before internal candidate routes
- HR-only requests remain HR-only
- downstream-only runtime mapping remains non-create-ready
- generated commands remain absolute and copy-paste safe
- route output remains advisory unless `--create` writes forms
- no runtime execution, approval, artifact acceptance, or ownership transfer is implied

## Verification

Reviewer reruns:

- `python3 -m py_compile scripts/system_hub.py scripts/test_system_hub.py` passed
- `python3 scripts/test_system_hub.py` passed
- natural Markdown smoke for `make a review-ready methods appendix` passed
- underspecified `can you help with this artifact? --create --json` refused with `reason=needs_clarification`
- Chinese natural route smoke for `幫我整理這個投影片任務` passed
- temp workspace natural `--create --json` wrote packet output only under the temp target workspace
- Vis_Math Lecture1 natural route smoke returned parseable JSON and did not create packet output
- non-reference Markdown link check passed: `missing=0 files_checked=97`
- repo-local artifact-harness packet output check returned empty:
  - `find contexts -maxdepth 3 \( -path '*artifact_harness_runs*' -o -name 'artifact_harness_registry.json' \) -print`

## Remaining Risks

- Natural phrasing coverage should be tuned from real misses and false positives.
- The route still exposes internal ids later in Markdown for auditability; this is useful for agents but not fully invisible UX.
- `packet-route` remains explicit and agent-called. It still does not intercept arbitrary Codex GUI/CLI text automatically.
- The codex-cns worktree remains dirty with pre-existing unrelated changes and untracked files; no staging was performed.
