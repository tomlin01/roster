# Setup and Portability

## Purpose

This document explains how to make this workspace usable on another machine without copying the original machine state blindly.

## Current State

- this folder is not yet a Git repository
- some policies and scripts are portable
- some runtime assumptions are still machine-pinned

Portability is therefore possible, but it must be intentional.

## Minimum Runtime Expectations

At minimum, another machine should have:

- `python3`
- a shell capable of running [`scripts/brain.sh`](../scripts/brain.sh)
- access to this workspace's `policy/`, `scripts/`, and `templates/`

Optional but important for full CNS behavior:

- Codex Desktop app
- `codex_ckpt`
- `session_ckpt`
- an Obsidian vault that plays the source-of-truth role

## First-Run Commands

After cloning or copying the workspace, the safest first-run sequence is:

1. `./scripts/brain.sh doctor`
2. `./scripts/brain.sh capabilities`
3. `./scripts/brain.sh refresh`

These commands reveal whether machine-specific paths and continuity tools are available.

## Machine-Specific Paths You Should Expect To Rebind

Current defaults include local paths such as:

- Obsidian vault and checkpoint roots
- desktop app path
- fallback continuity command paths

Do not assume those paths are valid on a second machine.
Instead, override them through environment variables or local config changes.

## Recommended Porting Sequence

### 1. Copy the portable contract layer first

Bring over at least:

- `AGENTS.md`
- `PRINCIPLES.md`
- `README.md`
- `PORTABILITY_GUIDE.md`
- `policy/`
- `templates/`

### 2. Rebind machine-specific configuration

Before expecting continuity or automations to work, configure:

- vault path
- checkpoint root
- bridge state path
- active session state path
- automation root
- continuity command locations

See [`CONFIG_REFERENCE.md`](./CONFIG_REFERENCE.md).

### 3. Verify runtime health

Run:

- `./scripts/brain.sh doctor`
- `./scripts/brain.sh capabilities`

Only after these are reasonable should this machine be treated as a reliable CNS node.

## What Should Not Be Copied Blindly

Do not treat these as required portable state:

- browser automation output
- caches
- temporary scratch folders
- machine-specific status snapshots
- one-off local progress dumps

See [`RUNTIME_ARTIFACT_POLICY.md`](./RUNTIME_ARTIFACT_POLICY.md).

## Current Limitation

This workspace does not yet have a pinned dependency manifest such as `requirements.txt` or `pyproject.toml`.
That means runtime recreation still depends partly on command availability and local environment knowledge.

This is acceptable for now, but it should be considered an incomplete portability layer.
