# agency-agents Capability Diff

## Comparison Scope

This note compares three layers that are easy to conflate:

1. the vendored `agency-agents` snapshot
2. the local global operating model and workspace overlays
3. the local role-adoption workflow for turning raw prompts into workspace-owned roles

## Short Answer

- `agency-agents` gives role breadth and an upstream orchestration doctrine
- local global policy gives execution defaults and precedence rules
- local role adoption gives the bridge from borrowed prompt to canonical role

They are complementary, not interchangeable.

## Capability Diff

| Layer | Strength | Missing | Best Use |
| --- | --- | --- | --- |
| `agency-agents` snapshot | `172` role files across `15` divisions, NEXUS doctrine, handoff templates, multi-tool export scripts | no local overlay awareness, no local artifact contract, no local validator for adopted roles, many role files bundle workflow and tool assumptions | read-only source library for role prompts and doctrine examples |
| local operating model | explicit precedence, `explore -> implement -> verify/review`, `orchestrator-subagent` default, CLI-first rule | no broad imported role catalog by default | machine-wide and workspace execution discipline |
| local role-adoption workflow | reference -> adapted -> canonical flow, local ownership of role definitions, controlled promotion path | no role becomes useful until someone does the adaptation work | safe bridge from third-party role library to local active use |

## What The Snapshot Covers Well

- breadth of domain-specific role prompts
- examples of how to structure role sections inside Markdown files
- orchestration and QA doctrine as reference material
- integration/export patterns for Claude Code and other tools
- verifier and reviewer vocabulary that can be selectively borrowed

## What The Snapshot Does Not Solve

- which role definitions become part of local canonical defaults
- how borrowed roles map onto local shared artifacts or overlays
- how to separate role core from upstream NEXUS control-plane assumptions
- when an adapted role is promotable into regular use here

Those remain local responsibilities in:

- [`../../policy/GLOBAL_OPERATING_MODEL.md`](../../policy/GLOBAL_OPERATING_MODEL.md)
- [`../../policy/ROLE_LIBRARY_ADOPTION_WORKFLOW_V0.md`](../../policy/ROLE_LIBRARY_ADOPTION_WORKFLOW_V0.md)
- [`../../agents/native/team-architect.md`](../../agents/native/team-architect.md)
- [`../../templates/agent_role_adaptation/role_adaptation.template.md`](../../templates/agent_role_adaptation/role_adaptation.template.md)

## Recommended Layering

- keep `agency-agents/` read-only
- treat it as a raw role library, not a live system definition
- extract role core only from selected files
- rewrite workflow, tool, and runtime assumptions into local terms
- promote adapted roles only after bounded real use

## Good First Roles To Borrow Carefully

- [`agency-agents/testing/testing-reality-checker.md`](./agency-agents/testing/testing-reality-checker.md)
- [`agency-agents/engineering/engineering-code-reviewer.md`](./agency-agents/engineering/engineering-code-reviewer.md)
- [`agency-agents/engineering/engineering-codebase-onboarding-engineer.md`](./agency-agents/engineering/engineering-codebase-onboarding-engineer.md)
- [`agency-agents/design/design-ux-researcher.md`](./agency-agents/design/design-ux-researcher.md)
- [`agency-agents/specialized/agents-orchestrator.md`](./agency-agents/specialized/agents-orchestrator.md)

## Rule Of Thumb

If the question is "what kind of role prompt should we start from?", the snapshot helps.
If the question is "how should this workspace execute and converge?", local policy still wins.
