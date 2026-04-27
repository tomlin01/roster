# Round 001 Follow-Up Prompt: HR Boundary And Same-Folder Handoff

You are continuing Artifact Harness improvement Round 001.

Do not start Prompt 2 lifecycle/status/resume work.

## Reviewer Findings To Fix

### Finding 1

- file: `agents/native/hr.md`
- priority: P2
- issue: HR tells artifact-production callers to route to `scripts/brain.sh artifact-harness "<mission>"` without an explicit `--path <workspace-folder>` target and with a cwd-sensitive script path.
- risk: a caller can follow HR guidance from the wrong cwd and write packet scaffolds into `codex-cns` rather than the artifact workspace, violating same-folder packet semantics.

Fix:

- Make HR guidance explicitly same-folder and CLI-safe.
- Preferred wording should point to either:
  - `./scripts/brain.sh artifact-harness "<mission>" --path <workspace-folder>` when run from the `codex-cns` kit root, or
  - `/Users/tom/Documents/PHD/codex-cns/scripts/brain.sh artifact-harness "<mission>" --path <artifact-workspace-folder>` when called from another workspace.
- The key invariant is: generated packets must land in the artifact workspace unless `codex-cns` is itself the target workspace.

### Finding 2

- file: `teams/human-resources/TEAM.md`
- priority: P2
- issue: HR Director still owns `team architecture`.
- risk: this conflicts with the repo-level boundary where HR owns staffing/role design only, while Team Architect owns collaboration pattern, shared artifacts, task graph, convergence, and CAP generation.

Fix:

- Replace HR-owned `team architecture` wording with staffing-only wording such as:
  - `staffing shape`
  - `role strategy`
  - `scope control`
  - `final staffing synthesis`
- Do not give HR ownership of collaboration pattern, shared artifacts, task graph, convergence, CAP, runtime mapping, tool authorization, runtime selection, or artifact acceptance.

## Constraints

- Keep this as a minimal follow-up patch.
- Do not modify generator logic unless a very small doc-string/test adjustment is necessary.
- Do not stage files.
- Do not revert unrelated worktree changes.
- Do not start Prompt 2.

## Verification

Run:

```bash
python3 -m py_compile scripts/system_hub.py scripts/test_system_hub.py
python3 scripts/test_system_hub.py
```

Also verify with `rg` or direct inspection that:

- HR-owned wording no longer says HR owns `team architecture`.
- HR artifact-harness handoff guidance includes `--path <workspace-folder>` or equivalent same-folder target guidance.

## Closeout

Append this follow-up to:

- `contexts/artifact_harness_improvement_rounds/round_001_hr_packet_slot/developer_report.md`
- `contexts/artifact_harness_improvement_rounds/round_001_hr_packet_slot/verification.md`

Keep reviewer rerun evidence marked separately if it has not been performed by the reviewer.
