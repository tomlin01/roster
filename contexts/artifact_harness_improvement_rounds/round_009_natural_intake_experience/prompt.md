# Prompt 9: Natural Intake Experience

## Context

We are continuing `codex-cns` Artifact Harness improvement rounds.

`codex-cns` is a Codex-native agent coordination kit. It does not assume a
persistent server and does not require users to leave Codex CLI/GUI. It turns
artifact-production quality contracts, staffing, capability authorization,
runtime mapping, approval evidence, and runtime invocation boundaries into
agent-readable files and templates inside the same working folder.

Completed rounds:

- Round 000 established the improvement-round evidence exchange.
- Round 001 added the explicit `hr_staffing_packet` slot.
- Round 002 added lifecycle/status/resume metadata and commands.
- Round 003 added replay evidence and fixed the manifest-derived packet path
  read boundary.
- Round 004 added provenance/source tracking for existing packet runs.
- Round 005 added non-executing runtime readiness preflight evidence.
- Round 006 added deterministic keyword intake/front-door routing.
- Round 007 added lightweight schema compatibility and migration tools.
- Round 008 added approval evidence and a guarded runtime invocation dry-run
  envelope.

Prompt 9 focuses on human experience. The current command surface is safe, but
still too much like an internal router. A normal user should be able to describe
an artifact task in ordinary language and receive a natural next step without
having to remember terms like `Artifact Harness SPEC`, `CAP`, or `runtime
mapping`.

## Problem

`packet-route` currently works when the utterance contains registered keywords
such as `requirement form`, `CAP`, `runtime mapping`, or `HR`. It misses plain
artifact-production requests such as:

- `make a review-ready methods appendix`
- `make this lecture slide task organized`
- `幫我整理這個投影片任務`

It also renders Markdown that starts with internal route IDs. That is useful for
agents, but not natural for daily Codex CLI/GUI use.

The desired UX is not automatic interception of all chat. The route command
remains explicit and CLI/agent-called. The improvement is that, once called, it
should explain the next step in user-facing language first and expose packet
internals as supporting detail.

## Goal

Make `packet-route` feel like a natural intake helper while preserving the
existing safety boundaries and machine-readable JSON.

Keep the existing command:

```bash
./scripts/brain.sh packet-route "<utterance>" --path <workspace-folder> --json
./scripts/brain.sh packet-route "<utterance>" --path <workspace-folder> --create --json
```

Do not add a server, daemon, database, orchestration UI, or dependency.

## Required Behavior

1. Add conservative natural artifact-mission detection.
   - Detect artifact-production intent from deterministic term combinations,
     not an LLM call.
   - Require at least a deliverable noun plus a production/quality/process cue.
   - Examples that should route to the Artifact Harness workflow:
     - `make a review-ready methods appendix`
     - `draft a methods appendix`
     - `prepare lecture slides`
     - `make this lecture slide task organized`
     - `幫我整理這個投影片任務`
   - Examples that should not route:
     - `what time is the meeting tomorrow`
     - `walk me through runtime mapping` should stay downstream-only and must
       not become a create-ready artifact mission
     - `ask HR to check staffing` should stay HR-only

2. Keep underspecified artifact references from creating misleading packets.
   - `can you help with this artifact?` may be recognized as an artifact hint,
     but it should require clarification before `--create`.
   - JSON should expose `needs_clarification=true` and a short
     `clarifying_questions` list.
   - `--create` must refuse for underspecified hints.

3. Add natural user-facing fields to JSON.
   - Preserve existing JSON keys from Round 006.
   - Add stable fields:
     - `user_intent`
     - `confidence`
     - `needs_clarification`
     - `clarifying_questions`
     - `natural_triggers`
     - `next_step_label`
     - `user_message`
     - `visible_next_action`
   - JSON remains parseable for success and refusal paths.

4. Improve Markdown output without removing machine detail.
   - Keep `# Packet Route` for compatibility.
   - Put a natural `## Next Step` section before internal candidate routes.
   - Internal route IDs, recognized front doors, and matched keywords can remain
     in later sections for agents/reviewers.
   - Avoid visible claims that routing approves capabilities, executes
     runtimes, accepts artifacts, or moves ownership boundaries.

5. Preserve SPEC-first and ownership boundaries.
   - Artifact-production requests still start with the Artifact Harness chain.
   - HR-only requests stay HR-only.
   - Downstream packet requests without an existing packet id do not bypass
     upstream packets.
   - Runtime-related requests do not execute runtime adapters.

6. Keep commands copy-paste safe.
   - Emitted commands must use the absolute `brain.sh` path.
   - `--path <workspace-folder>` remains the target workspace and packet output
     root.

7. Update docs minimally.
   - README, AGENTS, and named-team routing policy should describe the natural
     intake layer as deterministic, explicit, and advisory unless `--create`
     writes a packet chain.
   - Do not claim fully automatic interception of arbitrary Codex GUI/CLI text.

## Required Tests

Add regression tests using temporary workspaces for at least:

1. `packet-route "make a review-ready methods appendix" --json` routes to
   `artifact_harness_workflow`, sets `user_intent=artifact_production`, and
   allows creation.
2. `packet-route "make this lecture slide task organized" --json` routes to
   `artifact_harness_workflow`, sets natural triggers, and allows creation.
3. `packet-route "幫我整理這個投影片任務" --json` routes to the Artifact Harness
   workflow without requiring English keywords.
4. `packet-route "can you help with this artifact?" --create --json` refuses
   with `needs_clarification=true` and does not write packet output.
5. HR-only routing remains HR-only.
6. Downstream-only runtime mapping remains non-create-ready.
7. Existing command compatibility and absolute command behavior remain intact.
8. Repo-local artifact-harness output check stays empty.

## Real Workspace Smoke

Use the existing simple target workspace:

- `/Users/tom/Documents/PHD/Vis_Math/Slides/Lecture1`

Run `packet-route` with a natural utterance such as:

```text
make this lecture slide task organized
```

Expected behavior:

- parseable JSON
- route to Artifact Harness workflow
- do not create packet output unless `--create` is explicitly used
- no runtime execution
- no packet Markdown rewrite

## Constraints

- Do not start Prompt 10.
- Do not stage files.
- Do not revert unrelated worktree changes.
- Do not write durable smoke packet output under the `codex-cns` repo
  `contexts/` directory.
- Do not run external runtime adapters.
- Do not add a server, daemon, database, orchestration UI, or dependency.
- Do not weaken rerun guards, path guards, schema-check/migrate behavior,
  approval evidence behavior, or runtime invocation dry-run behavior.

## Exchange Artifacts

Create or update:

- `contexts/artifact_harness_improvement_rounds/round_009_natural_intake_experience/developer_report.md`
- `contexts/artifact_harness_improvement_rounds/round_009_natural_intake_experience/verification.md`
- `contexts/artifact_harness_improvement_rounds/round_009_natural_intake_experience/reviewer_notes.md`

Use the Round 000 protocol spirit:

- Findings Addressed
- Changed Files
- Generated Artifacts
- Verification Commands
- Known Non-Goals
- Remaining Risks
