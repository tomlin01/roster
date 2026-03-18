# Portability Guide

## Purpose

This guide explains what should be portable when this workspace is moved to GitHub or cloned onto another machine.

The goal is not to preserve every local artifact.
The goal is to preserve the operating system of the workspace:

- governance contracts
- stable policies
- reusable templates
- validated workflow structure

## Current Reality

This folder is not currently a Git repository.
That means portability has to be designed intentionally rather than assumed.

If this workspace is later pushed to GitHub, the export boundary should be explicit.

## Portable By Default

These are good GitHub candidates:

- `AGENTS.md`
- `PRINCIPLES.md`
- `README.md`
- `PORTABILITY_GUIDE.md`
- `policy/`
- `templates/`
- selected reusable scripts
- selected durable context docs that explain system behavior rather than one machine's transient state

## Usually Local Or Regenerated

These should usually be treated as local, generated, or selectively committed:

- machine-specific status snapshots
- ephemeral runtime overlays
- temporary debug output
- browser automation output
- cache directories
- ad hoc scratch artifacts

Examples in this workspace:

- `output/playwright/`
- `__pycache__/`
- `tmp_phase3/`
- machine-generated operational snapshots under `contexts/` when they only describe one machine's current run state

## Context Artifacts: Commit Selectively

Not all `contexts/` files serve the same role.

Good candidates to keep:

- durable governance summaries
- benchmark baselines intended as reference
- multi-agent pilot artifacts that explain a reusable protocol

Be careful with:

- `system_status.md`
- machine-local route/discovery snapshots
- generated registry dumps
- runtime overlay instances

These may be useful locally without being the right thing to version long-term.

## Absolute Path Warning

Many current artifacts contain local absolute paths such as `/Users/tom/...`.

That is acceptable for local operations, but not ideal for portable documentation.
Before promoting a document to GitHub-facing status, prefer:

- relative references where practical
- description of role and purpose instead of machine-specific path dependence

## What Another Machine Must Be Able To Reconstruct

A new machine does not need every historical runtime artifact.
It should be able to reconstruct:

- what this workspace is for
- what is stable vs experimental
- how memory is expected to work
- how skills move through lifecycle stages
- how central sessions should re-enter

That is why the most important portable files are the contract and brief documents.

## Minimal Portable Set

If you want a conservative first GitHub version, start with:

- `AGENTS.md`
- `PRINCIPLES.md`
- `README.md`
- `PORTABILITY_GUIDE.md`
- `policy/CENTRAL_NERVOUS_SYSTEM_BRIEF.md`
- `policy/STABLE_CORE_CONTRACT.md`
- `policy/SKILL_LIFECYCLE_CONTRACT.md`
- `policy/GLOBAL_OPERATING_MODEL.md`
- `policy/VIS_MATH_MULTI_AGENT_PILOT_V0.md`
- `templates/`
- only the scripts that are actually part of the intended portable system

Then add more artifacts intentionally, not by default.

## Promotion Rule For GitHub

Before treating a file as part of the portable repo contract, ask:

1. Does it explain a stable or intentionally reusable behavior?
2. Is it still meaningful on another machine?
3. Does it avoid depending on transient local runtime state?
4. Would a future session rely on it as guidance, not just as a log?

If the answer is mostly no, keep it local or regenerate it.
