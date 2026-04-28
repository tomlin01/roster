## Prompt 1: User-Facing Docs To Roster

```text
Implement the first safe rename phase: user-facing docs only.

Goal:
Make the target user-facing docs consistently present `Roster` / `@roster` as
the primary surface, while preserving `codex-cns` only as the internal repo /
historical name.

Files in scope:
- contexts/artifact_harness_usage_experience/README.target-user-experience.draft.md
- contexts/artifact_harness_usage_experience/TARGET_README_INSTRUCTION.md
- contexts/artifact_harness_usage_experience/NAMING_DECISION_DRAFT.md
- contexts/artifact_harness_usage_experience/README.md
- README.md only if you can avoid claiming unverified `@roster` behavior as
  already implemented
- AGENTS.md only if the wording is explicitly target-state or current-status
  accurate

Requirements:
- First screen tells a human to invoke `@roster`.
- Keep `HR` as staffing-only.
- Keep `PM` as an optional natural alias, not the primary name.
- Remove `@codex-*` and `@project-*` from target user-facing examples except in
  rejected-candidate history.
- Do not make shell commands the basic usage path.
- Keep reviewer/debug commands in a separate section.
- Add current-status wording wherever the implementation is not yet verified.

Verification:
- Markdown link check: missing=0.
- rg confirms no live target example uses `@codex-*` or `@project-*`.
- No code behavior changes in this phase.
```
