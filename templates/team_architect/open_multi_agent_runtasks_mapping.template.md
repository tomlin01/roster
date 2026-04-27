# open-multi-agent runTasks Mapping

## Metadata

- source operating packet:
- source capability access packet:
- status: draft/reviewed/approved
- runtime adapter: open-multi-agent
- runtime mode: runTasks
- generated_by:

## Fill Notes

- Fill this mapping from the Team Operating Packet, Capability Access Packet,
  and runtime adapter policy.
- Keep this file agent-readable Markdown in the same workspace folder.
- This mapping is for optional runtime execution; it does not make the runtime
  adapter a governance owner.
- No persistent server is required by this template.

## Adapter Decision

- why `runTasks()` is appropriate:
- why `runTeam()` is not the primary mode:
- expected runtime risk:
- approval gates required: yes/no
- execution surface:
  - TypeScript API required when approval gates are required
  - CLI allowed only when no approval gates are required and no runtime object wiring is needed

## Capability Access Trace

- CAP source:
- authorized skills:
- authorized plugins:
- authorized tools:
- denied or withheld capabilities:
- CAP approval gates:
- CAP access boundaries:
- runtime exposure rule:
  - expose only capabilities listed above
  - withhold any capability not authorized by CAP

## TeamConfig

```json
{
  "name": "",
  "agents": [
    {
      "name": "",
      "provider": "",
      "model": "",
      "systemPrompt": "",
      "tools": []
    }
  ],
  "sharedMemory": true,
  "maxConcurrency": 1
}
```

## Tasks

```json
[
  {
    "title": "",
    "description": "",
    "assignee": "",
    "dependsOn": [],
    "memoryScope": "dependencies"
  }
]
```

## Artifact Mapping

- task:
  - expected artifact:
  - artifact owner:
  - acceptance check:
  - promotion rule:

## Approval Gates

- after task:
  - CAP gate source:
  - gate reason:
  - enforcement surface:
  - approved continuation:
  - rejected fallback:

If any approval gate is required, this mapping must be executed through the
TypeScript API with an enforceable approval callback. The `oma` CLI path is not
allowed for gated execution because JSON configuration cannot carry function
callbacks such as `onApproval`.

## Convergence

- stop conditions:
- fallback behavior:
- final synthesis owner:

## Runtime Notes

- preferred API surface:
- same workspace folder:
- CLI allowed:
  - yes only if no approval gates are required
  - no when CAP approval gates, runtime object wiring, or human approval are required
- expected local byproducts:
- byproducts to keep local:
