# Runtime Artifact Policy

## Purpose

This document defines which artifacts are durable guidance and which are local runtime byproducts.

The goal is to prevent future GitHub exports from mixing policy with machine noise.

## Durable By Intent

These are usually worth preserving:

- policy contracts
- reusable templates
- durable governance summaries
- benchmark baselines intended as reference
- pilot artifacts that document a reusable protocol

## Runtime / Local By Default

These are usually local or regenerated:

- browser automation output
- caches
- scratch folders
- one-machine status snapshots
- transient overlay instances

## Current Examples In This Workspace

Usually local:

- `output/playwright/`
- `__pycache__/`
- `tmp_phase3/`
- ad hoc machine artifacts such as `Rplots.pdf`
- local progress snapshots like `FOLDER_PROGRESS_*`
- local continuation dumps like `FOLDER_CONTINUE_*`

Commit selectively:

- `contexts/system_status.md`
- `contexts/system_registry.json`
- `contexts/runtime_overlay_registry.json`
- `contexts/skill_discovery_registry.json`
- `contexts/skill_route_registry.json`

These may be useful operationally, but they are not automatically the right long-term published surface.

## Decision Rule

Before versioning a runtime-derived artifact, ask:

1. does it define a reusable contract or only record one run
2. is it meaningful on another machine
3. will a future session rely on it as guidance rather than telemetry

If not, keep it local or regenerate it.
