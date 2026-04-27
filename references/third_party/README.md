# Third-Party References

This folder stores read-only third-party reference snapshots that may inform local design work.

These snapshots are:

- reference material, not active workspace contract
- kept separate from local `templates/` and `policy/`
- not promoted into active use until they are mapped into local artifacts and rules

Current snapshots:

- [`agency-agents/`](./agency-agents/)
  - upstream Markdown role library plus NEXUS orchestration doctrine and integration scripts
- [`agency-agents.index.md`](./agency-agents.index.md)
  - local provenance and usage notes for treating the snapshot as a read-only role library
- [`agency-agents.capability-diff.md`](./agency-agents.capability-diff.md)
  - comparison of The Agency snapshot, local operating model, and local role-adoption workflow
- [`open-multi-agent/`](./open-multi-agent/)
  - upstream TypeScript multi-agent runtime framework snapshot
- [`open-multi-agent.index.md`](./open-multi-agent.index.md)
  - local provenance and usage notes for treating the snapshot as a runtime reference
- [`open-multi-agent.runtime-diff.md`](./open-multi-agent.runtime-diff.md)
  - comparison of the runtime framework against local `HR`, `Team Architect`, and coordination-policy boundaries

Do not treat anything under this folder as the system definition by default.
For active multi-agent work in this repo, local policy still lives under [`../../policy/`](../../policy/) and local artifact scaffolds still live under [`../../templates/`](../../templates/).
