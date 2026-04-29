# Roster Plugin

This plugin provides a Codex-native invocation surface for Roster.

After `roster-install` registers the local marketplace and Codex reloads plugin
state, users should be able to try:

```text
@roster help me turn these meeting notes into a project plan
```

or:

```text
/roster help me turn these meeting notes into a project plan
```

The stable fallback remains ordinary natural-language invocation:

```text
Roster, help me turn these meeting notes into a project plan.
```

The plugin does not run a server, daemon, database, or separate UI. It points
Codex back to the repo-owned `brain.sh` adapters through the install manifest.
