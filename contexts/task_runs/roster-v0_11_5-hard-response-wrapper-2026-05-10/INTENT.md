# Intent

Task ID: `roster-v0_11_5-hard-response-wrapper-2026-05-10`

User observed that v0.11.4 still lets Roster drift into a generic planning
answer. The concrete failure was a fuzzy future-artifact prompt about a
floating-city night-market guide:

- useful decomposition was produced;
- `本次啟用` was missing;
- `目前階段` was missing as a stable wrapper line;
- `本次分工執行` was missing;
- internal `route check`, `preference`, and `packet` wording leaked into an
  ordinary reply.

The requested fix is to branch and implement `v0.11.5`.

## Goal

Harden the Roster ordinary-response contract so non-trivial explicit Roster
invocations must pass a visible response wrapper before sending.

## Boundaries

- Do not change packet routing, install, health, or runtime behavior.
- Do not require actual subagent spawning.
- Keep ordinary user replies concise and human-facing.
- Keep internal route, packet, preference, CAP, runtime, and control-plane
  wording out of ordinary replies.
