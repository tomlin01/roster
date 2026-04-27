# Role Library Adoption Workflow v0

## Purpose

This note defines the default workflow for adopting third-party role libraries into this workspace without importing upstream control planes by accident.

The current motivating snapshot is:

- [`../references/third_party/agency-agents/`](../references/third_party/agency-agents/)

This workflow is local and experimental.

## Core Rule

Treat third-party role libraries as `raw role sources`, not as active workspace policy.

Do not collapse these layers:

- upstream role library
- local orchestration and overlay policy
- local canonical role definitions

## Role Statuses

### `reference`

- upstream snapshot only
- read-only
- not used directly as a local default

### `borrowed`

- used as a quick one-off reference or temporary prompt seed
- may be used directly for low-risk work
- not yet a local owned definition

### `adapted`

- copied into a workspace-owned draft
- rewritten to match local role boundaries and local orchestration assumptions
- suitable for bounded trials

### `canonical`

- local owned role definition
- has survived repeated bounded use
- safe to treat as a regular building block in this workspace

## Default Workflow

1. identify one upstream candidate role
2. create a workspace-owned draft from [`../templates/agent_role_adaptation/role_adaptation.template.md`](../templates/agent_role_adaptation/role_adaptation.template.md)
3. extract the role core:
   - mission
   - scope
   - deliverables
   - must-not-do constraints
4. remove or rewrite upstream assumptions:
   - orchestration doctrine
   - retry and gate logic
   - stack-specific tool requirements
   - runtime-specific command patterns
5. bind the draft to local execution surfaces:
   - local preferred runtime
   - local artifact handoff expectations
   - local verification style
6. use the adapted role in one bounded task
7. promote to `canonical` only if repeated use shows the role remains stable

## Install Boundary

`install` is the last step, not the first step.

Do not install a whole upstream role library into live agent directories just because it is available.

Install only when:

- the role is already workspace-owned
- the role has reached `canonical`
- the destination runtime is the intended long-term home for that role

## Hard Rules

- keep the upstream snapshot unchanged
- do not import upstream orchestration doctrine as local default policy
- do not treat upstream verifier commands or stack assumptions as universal
- do not promote a role because it is well-written; promote it because it works under local contracts

## Local Interpretation Rule

When an upstream role bundles `role + workflow + tool + gate logic` in the same file:

- keep the role core
- rewrite the workflow in local terms
- drop tool commands that are only examples or environment-specific
- let local policy continue to control orchestration, handoff, and convergence
