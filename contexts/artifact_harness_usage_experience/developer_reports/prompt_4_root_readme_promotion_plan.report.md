Implemented the root README promotion in [README.md](/Users/tom/Documents/PHD/codex-cns/README.md:1).

Changed:
- First screen now leads with `Roster` as a human staffing-and-coordination surface.
- Basic use starts with natural Codex language, not shell commands.
- `@roster` is clearly labeled as target invocation, not verified installed mention/skill/plugin/app/slash behavior.
- Current verified fallback is separated under `Current Verified Fallback`.
- Workspace/output semantics now say the target workspace must already exist.
- Formal packet/governance boundaries are linked after the human usage path.

Verification:
- Markdown link check: `missing=0`
- Overclaim review via `rg`: `@roster`, install, plugin/skill/slash, LLM/provider claims are caveated.
- `git diff --check -- README.md`: passed
- `python3 -m py_compile scripts/system_hub.py scripts/test_system_hub.py`: passed
- `python3 scripts/test_system_hub.py`: passed
- `python3 scripts/test_overlay_policy.py`: passed
- `python3 scripts/test_run_agent_benchmark.py`: passed
- `packet-route` verified both `Roster, ...` and `@roster ...` route to Artifact Harness.
- `roster-health` verified route visibility and smoke packet create/cleanup; status was `degraded` only because no provider was configured (`missing_provider`), matching the README caveat.

Remaining risks:
- `@roster` is still not verified as an installed Codex mention/skill/plugin/app/slash surface.
- Natural no-id active-run discovery remains target behavior; current verified resume path still needs `--id`.
- Cross-machine setup is currently repo-native reconstruction plus health check, not a finished install/register layer.

Note: other worktree changes already existed outside this README edit (`AGENTS.md`, routing config, scripts/tests, and the untracked usage-experience context). I left those untouched.