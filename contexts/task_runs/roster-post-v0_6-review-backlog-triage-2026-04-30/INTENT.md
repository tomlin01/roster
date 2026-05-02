# Intent Record

Task ID: `roster-post-v0_6-review-backlog-triage-2026-04-30`
Date: `2026-04-30`
Workspace: `/Users/tom/Documents/PHD/codex-cns`
Main Thread: `current Codex thread`
Source: `chat review findings`

## Purpose

Preserve the user's request to turn a mixed set of historical and current Roster review findings into a bounded follow-up packet. This file is intent evidence, not the implementation contract.

## Original User Language

```text
用 thread_packet_workflow 幫我把這個任務開成 packet
```

The user attached review findings covering:

- Roster preference-memory routing.
- Invalid `roster_preferences.json` diagnostics.
- Quality routing versus concrete artifact production.
- Quality self-check phrase recognition.
- Runtime mapping traceability to CAP.
- CAP/runtime/verification ownership boundaries.
- Approval-gated runtime execution.
- Template-first workflow provenance and autofill.
- Keyword alias routing, artifact packet entrypoints, HR SPEC-first handoff.
- Field-level source hints, packet location/naming.
- User-facing README invocation, install, workspace, and debug command clarity.

## User Outcome

What the user wants to be true after the work:

- The mixed finding list is converted into a clean, bounded task packet.
- A developer can start from the packet without reading the full chat history.
- The task does not reopen already-fixed issues unless they still fail on `main` after `v0.6.0`.

## Why It Matters

What problem this solves for the user's workflow:

- Roster has reached a usable `v0.6.0` milestone, but review findings from multiple rounds are mixed together.
- A packet prevents a future developer thread from treating stale findings as current truth or widening the scope.
- The user wants file-grounded continuity rather than chat-only continuity.

## Main-Thread Interpretation

Translate the user's language into practical engineering meaning:

- Build a `thread_packet_workflow` packet under `contexts/task_runs/`.
- Treat this as a triage-and-fix task, not a direct patch request.
- First verify each finding against current `main` at `v0.6.0`.
- Fix only findings that still reproduce on current `main`.

## Ambiguities

Items that are not yet fully specified:

- Whether the developer should fix all still-current findings in one pass or split after triage.
- Whether this task should produce a PR immediately or only a review report and next prompt.
- Whether historical docs under `contexts/artifact_harness_usage_experience/developer_reports/` should be rewritten, archived, or left as history.

## Constraints From User

Hard constraints:

- Use `thread_packet_workflow`.
- Preserve the distinction between current repo behavior and stale historical review findings.
- Do not assume previous thread design is correct without current verification.

Soft preferences:

- Keep Roster human-facing and avoid leaking internal control-plane terms in ordinary user paths.
- Prefer concrete, executable checks over conceptual config-only claims.
- Keep same-folder, no persistent server semantics.

## Parent Spec Check

Is this too broad for one developer pass?

- Parent spec: `yes`
- If yes, child spec for this pass: `Triage the attached findings against Roster v0.6.0 and fix only any still-current P1/P2 issues that are directly reproducible without redesign.`

## Do Not Infer

Things the developer/reviewer must not assume:

- Do not assume all listed findings are still valid.
- Do not assume `@roster` or `/roster` UI visibility is proven without local install and Codex reload verification.
- Do not treat historical developer reports as active user-facing docs.
- Do not widen this into a new architecture redesign unless triage finds a current blocking defect.
