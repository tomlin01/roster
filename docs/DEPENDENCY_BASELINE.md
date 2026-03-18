# Dependency Baseline

## Purpose

This document explains the minimum dependency story for the portable CNS export.

## Current Baseline

The core governance scripts currently included in this repo are intentionally lightweight.

For the main exported script set:

- [`scripts/system_hub.py`](../scripts/system_hub.py)
- [`scripts/run_agent_benchmark.py`](../scripts/run_agent_benchmark.py)
- [`scripts/overlay_policy.py`](../scripts/overlay_policy.py)
- related test scripts

the implementation is currently based on the Python standard library.

That means a second machine can inspect and reason about the exported system without first recreating a heavy Python package environment.

## Minimum Practical Requirement

- Python `3.11+` is recommended

This is mainly because:

- `tomllib` is used directly
- the repo assumes a modern Python runtime

## Optional External Runtime Dependencies

These are not required just to understand the framework, but they matter for full operational behavior:

- Codex Desktop
- `codex_ckpt`
- `session_ckpt`
- an Obsidian vault and checkpoint tree

These belong to the runtime integration layer, not the portable contract layer.

## Verification Baseline

For the portable export, the first verification pass should usually be:

1. `python3 -m py_compile scripts/*.py`
2. `python3 scripts/test_overlay_policy.py`
3. `python3 scripts/test_run_agent_benchmark.py`
4. `python3 scripts/test_system_hub.py`

If those pass, the exported framework is at least internally coherent at the script-and-contract level.

## What Is Still Missing

This repo still does not claim to provide:

- a fully pinned package manifest
- a turnkey runtime environment
- guaranteed parity with the original machine's continuity stack

That is acceptable for the current goal:

- make the system understandable
- make the contracts portable
- make the core framework reproducible enough for another LLM or machine to extend safely
