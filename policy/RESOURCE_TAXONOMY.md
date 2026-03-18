# Agent Resource Taxonomy

This taxonomy is the canonical layer map for machine-wide policy design.
It is used for planning and evaluation only. It does not introduce runtime dependencies.

## Layers

1. `access/retrieval`
2. `capability adapters/skill packs`
3. `orchestration/control plane`
4. `evaluation/observability`
5. `memory/continuity`
6. `human-in-the-loop/operator UX`
7. `workflow contract/spec`
8. `methodology/playbook`

## Resource Mapping

| Name | Primary Layer | Secondary Tags | Problem Solved | Adopt Now | Defer Reason | Repo Implication |
| --- | --- | --- | --- | --- | --- | --- |
| Symphony | orchestration/control plane | issue runner, workspace isolation, retries, observability | Coordinate long-running multi-agent execution from issue streams | no | Engineering preview, tied integration contracts | Use as control-plane reference for retry/reconcile and observability fields |
| OpenViking | orchestration/control plane | memory, permissions, GUI | Manage agent workforce with shared memory and agent registry concepts | no | Not required for v1 loop, larger integration surface | Use as reference for role separation and memory boundaries |
| Paperclip | orchestration/control plane | governance, operator UX, observability | Organize agent teams with budgets, approvals, and operator controls | no | Overweight for current v1 benchmark-first scope | Use as reference for governance and intervention metrics |
| agent-spec | workflow contract/spec | acceptance gates, verification | Define contract-first execution and machine-checkable completion criteria | yes | n/a | Adopt contract schema fields and acceptance check discipline |
| systematicls thread | methodology/playbook | context isolation, contract discipline | Clarify operating heuristics for session separation and done criteria | yes | n/a | Adopt principles in operating model and benchmark acceptance strategy |
| openai-cua-sample-app | capability adapters/skill packs | browser execution harness, observability, operator UX | Demonstrate run-scoped browser execution, replay, and verification around CUA workflows | no | Reference-only until browser/computer-use lane becomes an explicit benchmark target | Keep as browser-runner reference for future replay and verification design |
| Agent-Reach | access/retrieval | external browsing bridge | Expand external web reach for agents | no | Not needed to validate policy loop | Keep as deferred capability extension |
| Apify agent-skills | capability adapters/skill packs | tool wrappers, actor adapters | Package external capabilities into reusable agent skills | no | V1 focus is policy and benchmark, not new adapters | Keep as deferred adapter catalog reference |
| peon-ping | human-in-the-loop/operator UX | notification routing, attention management | Reduce idle waiting and improve operator response timing | no | Useful after core loop metrics stabilize | Keep as deferred UX layer reference |

## Decision Rule

- Promote a resource pattern into machine-wide defaults only after it is reflected in benchmark metrics across at least two workspace types.
- Keep external frameworks in reference mode unless a policy gap cannot be solved by repo-native artifacts.
