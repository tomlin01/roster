# Global Agent Operating Model

## Purpose

Define a machine-wide default behavior model with explicit workspace overlays.
This model prevents any single workspace from silently becoming the de facto global standard.

## Responsibility Layers

### 1) Global defaults

Global defaults are machine-wide policy primitives:

- multi-agent sequencing default
- contract schema
- benchmark schema
- report schema
- baseline metric priority
- fallback policy

Global defaults apply first for every workspace.

### 2) Folder overlays

Folder overlays are local constraints and preferences:

- domain-specific style and terminology
- output format and artifact location preferences
- risk sensitivity and review strictness
- source ordering preferences
- benchmark-relevant execution constraints parsed from local rule content

Folder overlays may specialize behavior but may not break compatibility with global schemas.
Overlay evaluation must prefer actual `AGENTS.md` and `PRINCIPLES.md` content over file-presence heuristics.

### 3) Session state

Session state is short-lived continuity:

- transient assumptions
- temporary clarifications
- in-flight task memory

Session state cannot replace global defaults or folder overlays.

## Priority and Conflict Resolution

Priority order is strict:

1. user explicit instruction
2. workspace facts and local overlay rules
3. global defaults
4. session transient state

Compatibility constraints:

- local overlays must preserve global contract schema fields
- local overlays must preserve benchmark report schema shape
- local overlays must not redefine benchmark runner interface

## Agent Workflow Defaults

- Non-trivial tasks default to `explorer -> worker -> reviewer -> main synthesis`.
- Trivial tasks default to single-agent direct execution.
- High-impact ambiguity requires a short discussion checkpoint before implementation unless user explicitly asks for direct execution.

## Contract Requirements

The contract must include:

- `goal`
- `inputs`
- `constraints`
- `out_of_scope`
- `acceptance_checks`
- `verification_steps`
- `fallback_policy`

## Benchmark Requirements

Benchmark cases must include:

- `id`
- `category`
- `prompt`
- `required_mode`
- `expected_flow`
- `acceptance_checks`
- `network_needed`
- `workspace_sensitivity`
- `notes`

Required benchmark output for each case:

- `global_default_result`
- `workspace_overlay_result`
- `delta`

V1 benchmark note:

- The first baseline is policy-simulation based.
- It validates global-default vs overlay behavior deterministically before any live telemetry loop is introduced.
- Reports must carry a machine-readable simulation marker so they are not mistaken for live runtime telemetry.

Benchmark modes:

- `policy_simulation`: deterministic presence-based overlay model for compatibility baselines.
- `parsed_overlay`: parse local `AGENTS.md` and `PRINCIPLES.md` content into benchmark-relevant signals while remaining non-telemetry.

## Baseline Metric Priority

1. `task_success_rate`
2. `route_match_rate`
3. `manual_intervention_rate`
4. `median_wall_time_sec`
5. `avg_tool_calls`

## Promotion Rule

A policy change may be promoted to global defaults only if:

- it improves or preserves benchmark quality across at least two workspace types
- it does not introduce schema or interface incompatibility
