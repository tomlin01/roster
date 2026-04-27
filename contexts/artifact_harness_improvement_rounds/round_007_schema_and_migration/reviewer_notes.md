# Reviewer Notes

## Findings

No P0/P1/P2 blocking findings.

### P3 - `compatible` is a schema-compatibility signal, not full manifest completeness

- File: `scripts/system_hub.py:7028`
- File: `scripts/system_hub.py:7111`
- Observation: `schema-check` reports `missing_required_fields`, but `compatible` and `migration_safe` are derived from blocking findings and missing required files only. In an independent temp smoke, removing `mission` from `packet_manifest.json` was reported in `missing_required_fields`, while `compatible=true` and `migration_safe=true`.
- Assessment: This is not blocking for Prompt 7 because the prompt asks for a lightweight compatibility contract and not a formal JSON Schema validator. It should be clarified before future automation treats `compatible=true` as proof of full packet completeness.

## Review Summary

Prompt 7 is materially complete. The implementation adds same-workspace schema compatibility tooling without introducing a server, database, runtime adapter, new dependency, or governance owner. The new commands are CLI/GUI friendly:

- `./scripts/brain.sh artifact-harness schema-check --path <workspace-folder> --id <packet-id> --json`
- `./scripts/brain.sh artifact-harness migrate --path <workspace-folder> --id <packet-id> --json`

The implementation preserves the core separation:

- schema tools are compatibility/evidence tools only
- migration updates only JSON compatibility surfaces
- filled packet Markdown is not rewritten
- manifest-derived packet paths are validated under the target workspace before use
- missing required packet files and outside-target manifest packet paths are refused with parseable JSON
- Vis_Math Lecture1 receives only expected same-workspace schema metadata/manifest/registry updates

The new schema contract is documented in `policy/ARTIFACT_HARNESS_SCHEMA_V0.md` and referenced from README, AGENTS, and the workflow policy.

## Verification

Reviewer reruns:

- `python3 -m py_compile scripts/system_hub.py scripts/test_system_hub.py` passed
- `python3 scripts/test_system_hub.py` passed
- independent temp workspace create/schema-check/migrate/idempotence smoke passed
- independent sentinel check confirmed schema-check and migrate did not rewrite packet Markdown
- independent missing required packet migrate refusal returned parseable JSON with `reason=schema_migration_blocked`
- independent missing manifest field check confirmed the field is reported in `missing_required_fields`
- Vis_Math Lecture1 schema-check returned parseable JSON with `compatible=true`, `migration_required=false`, and no blocking findings
- non-reference Markdown link check passed: `missing=0 files_checked=88`
- repo-local artifact-harness packet output check returned empty:
  - `find contexts -maxdepth 3 \( -path '*artifact_harness_runs*' -o -name 'artifact_harness_registry.json' \) -print`

## Remaining Risks

- The schema contract remains intentionally lightweight and does not deeply validate every nested generated report field.
- `compatible=true` should be interpreted as schema/run compatibility, not as proof that every packet field is complete.
- Vis_Math workspace now has durable schema metadata changes for the named smoke run; this was allowed by Prompt 7, but it is still target-workspace state.
- The codex-cns worktree remains dirty with pre-existing unrelated changes and untracked files; no staging was performed.
