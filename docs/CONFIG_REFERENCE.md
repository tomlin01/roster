# Config Reference

## Purpose

This document explains the main portable and machine-specific configuration surfaces for the workspace.

Primary config file:

- [`policy/system_hub.toml`](../policy/system_hub.toml)

## What Is Machine-Specific Today

The following values are currently machine-pinned by default:

- `paths.vault_path`
- `paths.checkpoint_root`
- `paths.bridge_state`
- `paths.active_session_state`
- default desktop app path assumptions
- fallback command paths for `codex_ckpt` and `session_ckpt`

These should be expected to change on another machine.

## system_hub.toml Sections

### `[workspace]`

- `root`
  - workspace root relative to the config file

### `[paths]`

- `policy_dir`
- `contexts_dir`
- `scripts_dir`
- `codex_home`
- `skill_roots`
- `vault_path`
- `checkpoint_root`
- `bridge_state`
- `active_session_state`
- `automation_root`

Portable in principle:

- repo-relative directories
- `codex_home`
- `skill_roots`

Usually machine-specific:

- vault/checkpoint-related paths
- automation paths if the host setup differs

### `[freshness]`

- `system_hours`
- `generated_hours`
- `report_hours`

These are behavioral thresholds and are portable unless the operating model itself changes.

## Environment Variable Overrides

The runtime already supports environment overrides for major config fields.

Current override variables include:

- `SYSTEM_HUB_WORKSPACE_ROOT`
- `SYSTEM_HUB_POLICY_DIR`
- `SYSTEM_HUB_CONTEXTS_DIR`
- `SYSTEM_HUB_SCRIPTS_DIR`
- `SYSTEM_HUB_CODEX_HOME`
- `SYSTEM_HUB_SKILL_ROOTS`
- `SYSTEM_HUB_VAULT_PATH`
- `SYSTEM_HUB_CHECKPOINT_ROOT`
- `SYSTEM_HUB_BRIDGE_STATE`
- `SYSTEM_HUB_ACTIVE_SESSION_STATE`
- `SYSTEM_HUB_AUTOMATION_ROOT`
- `SYSTEM_HUB_FRESHNESS_SYSTEM_HOURS`
- `SYSTEM_HUB_FRESHNESS_GENERATED_HOURS`
- `SYSTEM_HUB_FRESHNESS_REPORT_HOURS`
- `SYSTEM_HUB_CONFIG`

Related command overrides:

- `CODEX_CKPT_CMD`
- `SESSION_CKPT_CMD`

## Recommended Portability Practice

When moving this workspace to another machine:

1. keep `policy/system_hub.toml` as the readable default
2. use environment overrides for machine-specific rebinding
3. avoid baking new absolute paths into portable policy docs unless necessary

## Known Local Defaults

The code currently assumes local defaults such as:

- `/Applications/Codex.app`
- `/Users/tom/bin/codex_ckpt`
- `/Users/tom/bin/session_ckpt`

Treat these as convenience defaults, not portable standards.
