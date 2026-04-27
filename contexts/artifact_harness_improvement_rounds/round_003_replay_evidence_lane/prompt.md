# Prompt 3: Artifact Harness Replay Evidence Lane

## Context

We are continuing `codex-cns` Artifact Harness improvement rounds.

`codex-cns` is a Codex-native agent coordination kit. It does not assume a
persistent server and does not require users to leave Codex CLI/GUI. It turns
artifact-production quality contracts, staffing, capability authorization, and
runtime mapping into agent-readable files and templates so Codex can assemble
task forms and execution boundaries inside the same working folder.

Round 001 added the missing `hr_staffing_packet` slot.
Round 002 added lifecycle/status/resume metadata and commands.

For this round, focus only on replay evidence: proving that a real artifact
mission can be scaffolded, inspected, and recorded as evidence without turning
the evidence lane into governance or execution ownership.

## Real Test Workspace

Use this workspace as the primary smoke/replay target:

```text
/Users/tom/Documents/PHD/Vis_Math/Slides/Lecture1
```

This is intentionally a simpler task. It already had an earlier attempt to
assemble a team; this round should make the packet/evidence path explicit and
replayable without requiring the user to manage chat-only continuity.

Do not modify existing lecture artifacts unless the command being tested
explicitly generates packet/evidence files under the target workspace's
`contexts/` area.

## Problem

The current Artifact Harness command can create packets and lifecycle status,
but there is no repo-native way to preserve a replay record that answers:

- what user mission was tested
- which workspace was targeted
- which packet id and packet files were produced
- which fields were scaffolded vs still open
- which lifecycle state was observed
- which commands were run
- what friction or follow-up was found

Without that, future reviewers still have to infer whether this is just static
documentation or a repeatable Codex-native artifact-production workflow.

## Goal

Add a minimal replay/evidence lane for Artifact Harness packet runs.

The lane should be CLI/GUI-friendly, same-folder, no-server, and agent-readable.
It should help a later Codex session inspect a real packet run and understand
what happened without scraping free-form chat history.

## Required Behavior

1. Add a repo-native replay/evidence command or subcommand.
   - Suggested form:
     - `./scripts/brain.sh artifact-harness replay --path <workspace> --id <packet-id> --json`
     - or another predictable command if it fits the existing parser better.
   - It should not invoke an agent, execute a runtime adapter, or approve
     anything.
   - It should inspect existing packet outputs and lifecycle metadata.
   - It should return structured JSON when `--json` is supplied.

2. Persist replay evidence inside the target workspace.
   - Prefer a small Markdown or JSON artifact under the existing packet run
     directory, for example:
     - `artifact_replay_evidence.md`
     - `artifact_replay_evidence.json`
   - The evidence file must be derived from existing packet files, manifest,
     registry, lifecycle state, and command metadata.
   - It must not rewrite packet Markdown forms.

3. Record field-completion state at a practical level.
   - Minimal acceptable implementation:
     - list packet files
     - mark each packet as `exists`
     - count obvious open-question markers or empty bullet fields
     - report whether lifecycle status exists and what it is
   - Do not overfit to perfect Markdown parsing. Prefer transparent heuristics
     and record them in the evidence.

4. Keep ownership boundaries clear.
   - Replay evidence is observation/continuity only.
   - It does not accept the artifact.
   - It does not approve capabilities.
   - It does not select runtime.
   - It does not replace SPEC, HR, Team Architect, CAP, runtime mapping, or
     verification/review.

5. Use the Vis_Math Lecture1 workspace for a real smoke.
   - Create or reuse a packet run under:
     - `/Users/tom/Documents/PHD/Vis_Math/Slides/Lecture1/contexts/artifact_harness_runs/<packet-id>/`
   - Use a stable packet id such as:
     - `vis-math-lecture1-team-smoke`
   - Choose a simple mission consistent with the workspace, for example:
     - `Prepare a review-ready team operating packet for Lecture 1 visual math slide/video artifact production`
   - If an existing same-id packet run exists, do not overwrite it. Use the
     rerun guard and either inspect it or choose a new id. Do not force unless
     the prompt requires it.

6. Update docs minimally.
   - README / AGENTS / workflow policy should mention replay evidence only if
     necessary.
   - Do not market this as complete automation.

## Constraints

- Do not start Prompt 4.
- Do not add a server, daemon, database, or persistent orchestration UI.
- Do not stage files.
- Do not revert unrelated worktree changes.
- Do not write durable smoke packet output under the `codex-cns` repo
  `contexts/` directory.
- The real Vis_Math packet/evidence output is allowed because the prompt names
  that target workspace explicitly.

## Exchange Artifacts

Write:

- `contexts/artifact_harness_improvement_rounds/round_003_replay_evidence_lane/developer_report.md`
- `contexts/artifact_harness_improvement_rounds/round_003_replay_evidence_lane/verification.md`

Use the round 000 protocol spirit:

- Findings Addressed
- Changed Files
- Generated Artifacts
- Verification Commands
- Known Non-Goals
- Remaining Risks

## Verification

Run at minimum:

```bash
python3 -m py_compile scripts/system_hub.py scripts/test_system_hub.py
python3 scripts/test_system_hub.py
```

Also verify:

- temp workspace replay command returns parseable JSON
- replay evidence is written under the target workspace packet run directory
- replay does not rewrite packet Markdown
- missing packet run returns structured refusal JSON under `--json`
- Vis_Math Lecture1 smoke succeeds or fails fast with a clear structured reason
- `find contexts -maxdepth 3 \( -path '*artifact_harness_runs*' -o -name 'artifact_harness_registry.json' \) -print` returns no codex-cns repo smoke output

## Acceptance

- There is a repeatable CLI path from a packet run to replay evidence.
- JSON output includes at least:
  - `id`
  - `target_path`
  - `run_dir`
  - `manifest`
  - `status`
  - `packets`
  - `evidence_path`
  - `refused`
  - `reason`
- Evidence records packet presence and simple completion/open-field heuristics.
- The Vis_Math Lecture1 workspace has a real allowed packet/evidence smoke or a
  documented structured refusal.
- Round 003 has developer report and verification evidence.
