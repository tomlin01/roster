# Stable Core Contract

## Purpose

This document defines the parts of the central nervous system that should be treated as stable by default.
It exists so future sessions do not mistake implementation experiments for globally safe defaults.

## Stable Core Scope

The current stable core in this workspace is:

- memory routing
- benchmark / policy / overlay contract
- reconciliation / status / capability surfaces

These are stable because they already act as shared infrastructure for multiple workflows.

## Core Invariants

### 1. Source-of-truth discipline

- `Obsidian` remains the source of truth for long-lived knowledge.
- Session state is transient and cannot silently replace canonical artifacts.
- Retrieval or indexing layers support continuity but do not override source-of-truth facts.

### 2. Policy layering

Priority order remains:

1. user explicit instruction
2. workspace facts and local overlays
3. global defaults
4. transient session state

No local change here should silently invert that ordering.

### 3. Contract compatibility

Changes to the stable core must preserve:

- global contract field shape
- benchmark report schema shape
- benchmark runner interface
- canonical status and reconciliation surfaces

### 4. Auditable promotion

Anything promoted from this repo outward must leave auditable evidence behind.
One successful experiment is not enough.

## Memory Routing Contract

For runtime continuity in this repo, prefer:

- `overlay`
- `closeout`
- `session-gate`

`memory-triage` is governance-facing, not the normal daily runtime path.

Do not force-resume stale sessions by default.
When the stale threshold is crossed, prefer a new session with a curated brief or summary.

## Benchmark / Overlay Contract

This workspace is where changes to policy and overlay interpretation converge before wider promotion.

Default expectations:

- overlays specialize behavior without breaking shared schemas
- overlay-sensitive evaluation should read actual overlay content, not just file presence
- benchmark realism should remain comparable across workspace types

## Status / Capability Surfaces

The status layer should remain trustworthy as a shared operational snapshot.

That includes:

- `system_status.md`
- `system_registry.json`
- reconciliation artifacts
- capability summaries

These surfaces may evolve, but they should not become ambiguous or purely narrative.

## Change Discipline

If a change touches stable core behavior, treat it as governance work.
That means:

- define the intended contract first
- validate locally
- preserve canonical outputs and interfaces
- record whether the capability is stable, converging, or experimental

## What Does Not Belong Here

The stable core contract should not absorb:

- narrow domain tactics
- one-off implementation workarounds
- unresolved experimental router behavior
- ad hoc multi-agent pilots

Those may influence the future, but they are not part of the stable core until proven.
