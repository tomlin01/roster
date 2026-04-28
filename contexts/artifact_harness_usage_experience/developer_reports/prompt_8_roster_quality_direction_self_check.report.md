# Prompt 8 Report: Roster Quality Direction And Self-Check

## Issue

GitHub GH-1 asked for Quality to become a first-class Roster behavior. The
missing behavior was not Harness SPEC acceptance itself, but Roster's ability to
set a practical Quality direction, split immediate fixes from durable workflow
improvements, and answer in plain user-facing language.

## Baseline Finding

Before editing, this prompt:

```text
Roster，幫我看 Lecture1 的 Quality 要怎麼設定
```

only matched the generic `Roster` front door in `packet-route`. It did not
surface Quality direction, short-term vs long-term self-check behavior, or a
direct no-packet response path.

## Changes

- Added Quality direction and self-check guidance to `skills/roster/SKILL.md`.
- Added a root README `Quality Direction` section with the expected short
  Chinese first-touch response shape.
- Updated the target UX README and target README instruction so user-facing
  Quality examples stay plain and avoid internal packet/runtime jargon.
- Added a `packet-route` classification for Roster Quality direction prompts.
  These prompts now return `recommended_route: roster_quality_direction`,
  `user_intent: quality_direction`, no create command, and structured short-term
  and long-term self-check focus.
- Added a regression test for the issue prompt.

## PR Review Follow-Up

The follow-up Developer pass tightened the route precedence and self-check
matcher after review found that Quality direction could intercept concrete
artifact work.

- `packet-route` now evaluates artifact-production intent before Quality-only
  direction. A concrete request such as `Roster, create a review-ready methods
  appendix with Quality settings` routes to `artifact_harness_workflow`, keeps
  `create_allowed=true`, and leaves `quality_direction` attached as advisory
  self-check context.
- Quality-only prompts still answer directly through
  `roster_quality_direction`.
- Added common self-check action terms: `check`, `review`, `inspect`, `run`,
  `做`, `檢查`, and `檢視`.
- Added regression coverage for the artifact-plus-Quality route and the Chinese
  self-check prompts `Roster，幫我檢查 Lecture1 的品質` and
  `Roster，幫我做自我檢查`.

## Boundary Preservation

- Harness SPEC remains the acceptance source of truth when a packet exists.
- Quality consumes acceptance checks and turns them into self-check behavior.
- Quality does not replace SPEC, CAP, runtime authorization, tool ownership, or
  final acceptance.
- First-touch Quality examples do not expose HR, Team Architect, CAP, runtime
  adapter, control-plane, or packet-chain terms.

## Validation

Passed:

- `python3 -m py_compile scripts/system_hub.py scripts/test_system_hub.py`
- `python3 scripts/test_system_hub.py`
- `git diff --check`
- `./scripts/brain.sh packet-route "Roster，幫我看 Lecture1 的 Quality 要怎麼設定" --path /tmp --json`
- `./scripts/brain.sh packet-route "Roster, create a review-ready methods appendix with Quality settings" --path /tmp --json`
- `./scripts/brain.sh packet-route "Roster，幫我檢查 Lecture1 的品質" --path /tmp --json`
- `./scripts/brain.sh packet-route "Roster，幫我做自我檢查" --path /tmp --json`

Expected refusal passed:

- `./scripts/brain.sh packet-route "Roster，幫我看 Lecture1 的 Quality 要怎麼設定" --path /tmp --create --json`
  refused with `create_not_allowed_for_recommended_route` and wrote no packet
  output.

## Remaining Risk

This adds deterministic routing and documentation for Quality direction. It
does not make ordinary Codex chat automatically intercept every Quality phrase;
Codex still has to use the Roster skill instructions or call the route helper
when deterministic evidence is needed.
