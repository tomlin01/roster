# Artifact Harness Improvement Rounds

This folder is a lightweight evidence exchange surface for iterative
artifact-harness improvement rounds.

It is not a governance owner, runtime owner, approval authority, or persistent
orchestration system. It only preserves work evidence and review handoff
material in same-folder Markdown or JSON so a later Codex or external reviewer
can replay a round without relying on chat memory.

## Round Layout

Use one folder per round:

```text
round_001_short_slug/
  prompt.md
  developer_report.md
  reviewer_notes.md
  verification.md
```

`round_000_protocol/` defines the current exchange protocol and reusable
templates.

## Required Evidence

Each round must preserve:

- the original prompt exactly enough for replay
- the developer report
- reviewer notes
- verification evidence
- links or paths to any generated artifacts

Generated runtime outputs, packet runs, and test workspaces should remain in
temporary workspaces unless the round explicitly needs a durable artifact. Do
not use this folder as an artifact-harness packet output root.

## Review Rule

Reviewers must not rely only on the developer report. A review must inspect the
actual diff, rerun the necessary tests when possible, and inspect generated or
claimed artifacts before accepting the round.

Review notes must be findings-first, severity ordered, and line anchored:

- `P0`: blocks correctness, safety, or data integrity
- `P1`: blocks the stated acceptance criteria
- `P2`: meaningful workflow, maintainability, or verification gap
- `P3`: wording, polish, or low-risk drift

Each finding should include a file path and line number when the issue is tied
to a file.

## Non-Goals

- no server
- no daemon
- no database
- no hidden approval system
- no replacement for Artifact Harness SPEC, HR, Team Architect, CAP, runtime
  adapter policy, or verification/review ownership

