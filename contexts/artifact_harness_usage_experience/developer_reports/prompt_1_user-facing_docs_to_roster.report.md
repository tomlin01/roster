Implemented docs-only rename phase.

Changed:
- [README.md](/Users/tom/Documents/PHD/codex-cns/README.md:1): first screen now presents `Roster` / target `@roster`, keeps `codex-cns` as internal/historical, and moves shell commands under reviewer/debug wording.
- [README.md](/Users/tom/Documents/PHD/codex-cns/contexts/artifact_harness_usage_experience/README.md:1): added first-screen `@roster` target invocation and current-status caveat.
- [README.target-user-experience.draft.md](/Users/tom/Documents/PHD/codex-cns/contexts/artifact_harness_usage_experience/README.target-user-experience.draft.md:1): tightened `@roster` target wording, added `PM` as optional, kept `HR` staffing-only.
- [TARGET_README_INSTRUCTION.md](/Users/tom/Documents/PHD/codex-cns/contexts/artifact_harness_usage_experience/TARGET_README_INSTRUCTION.md:1): updated target requirements/examples for `Roster`, optional `PM`, and staffing-only `HR`.
- [NAMING_DECISION_DRAFT.md](/Users/tom/Documents/PHD/codex-cns/contexts/artifact_harness_usage_experience/NAMING_DECISION_DRAFT.md:1): clarified `PM` optional alias and added current-status wording for unverified `@roster`.

Verification:
- Markdown link check on changed docs: `missing=0 files_checked=5`.
- Live target examples check: no `@codex-*` or `@project-*` hits outside rejected-candidate history. The only remaining hit is `@project-office` in the rejected `Project Office` candidate.
- `git diff --check`: passed.
- No code, JSON, TOML, tests, registry, or runtime behavior changed. `AGENTS.md` was left unchanged.

