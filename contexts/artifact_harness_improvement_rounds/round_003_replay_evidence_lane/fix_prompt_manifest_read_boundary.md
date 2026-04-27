# Round 003 Follow-up Fix Prompt: Manifest Packet Read Boundary

## Context

Round 003 added `artifact-harness replay --path <workspace> --id <packet-id> [--json]`.
The core product boundary is same-folder, CLI/GUI-friendly artifact packet assembly:
generated packet state and replay evidence must stay inside the target workspace
and must not silently read packet paths outside that workspace.

## Reviewer Finding

[P1] Replay trusts manifest-derived packet paths outside the target workspace.

In `scripts/system_hub.py`, lifecycle state builds packet paths from:

```python
packets = {
    key: str((target / rel).resolve())
    for key, rel in manifest.get("packets", {}).items()
    if isinstance(rel, str)
}
```

Then `build_artifact_harness_replay_evidence()` reads those paths via
`artifact_harness_packet_completion_heuristics(path)`.

I reproduced that a manifest entry such as:

```json
"artifact_harness_spec": "../outside_secret.md"
```

causes `artifact-harness replay --json` to return success and report the
outside file path and open-question counts in `artifact_replay_evidence.json`.

That violates the same-workspace boundary and makes replay a possible
out-of-workspace file probe.

## Required Fix

1. Validate every manifest-derived packet path before exposing it through
   lifecycle state or replay evidence.
2. A manifest packet path must resolve under the target workspace after
   symlink/path normalization. Preferably keep canonical packet keys under the
   packet run directory when practical, but the minimum required invariant is
   no resolved path outside `--path <workspace>`.
3. On violation, fail fast with non-zero exit.
4. Under `--json`, return structured refusal JSON instead of only stderr.
5. Use a clear reason, for example:
   - `manifest_packet_path_outside_target_workspace`
6. Include the offending packet key and attempted path in the refusal payload if
   possible.
7. Do not write or update `artifact_replay_evidence.json` on refusal.
8. Keep replay as observation/continuity only. Do not add runtime execution,
   capability approval, artifact acceptance, or silent migration.

## Regression Tests

Add tests in `scripts/test_system_hub.py` that:

1. Create an artifact-harness run in a temp workspace.
2. Edit `packet_manifest.json` so one packet path points outside the target
   workspace, for example `../outside_secret.md`.
3. Create that outside file with recognizable text.
4. Run:

```bash
./scripts/brain.sh artifact-harness replay --path <target> --id <id> --json
```

5. Assert:
   - return code is non-zero
   - stdout is parseable JSON
   - `refused=true`
   - `reason=manifest_packet_path_outside_target_workspace`
   - payload identifies the offending packet key/path
   - `artifact_replay_evidence.json` was not written or rewritten
   - replay output does not include heuristic counts for the outside file

Also consider whether `artifact-harness status/resume --json` should fail on
the same invalid manifest path. If the validation is centralized in lifecycle
state loading, add or update tests accordingly.

## Documentation

Update docs only if needed. If you add a new refusal reason, mention it in the
Round 003 developer report and verification notes.

## Required Closeout

Write/update:

- `contexts/artifact_harness_improvement_rounds/round_003_replay_evidence_lane/developer_report.md`
- `contexts/artifact_harness_improvement_rounds/round_003_replay_evidence_lane/verification.md`

Run at minimum:

- `python3 -m py_compile scripts/system_hub.py scripts/test_system_hub.py`
- `python3 scripts/test_system_hub.py`
- A direct temp-workspace reproduction of the invalid manifest boundary case
- The existing repo-local smoke cleanup check:

```bash
find contexts -maxdepth 3 \( -path '*artifact_harness_runs*' -o -name 'artifact_harness_registry.json' \) -print
```

Do not stage files. Do not start Prompt 4.
