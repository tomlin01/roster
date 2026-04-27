# Artifact Harness Future Angles

Captured: 2026-04-27

## Context

Current Artifact Harness work has mostly validated the wiring:

- Artifact Harness SPEC, HR, Team Architect, CAP, runtime mapping, and verification are separated.
- `artifact-harness` and `packet-route` now provide a CLI-friendly packet scaffold path.
- Packet output is same-workspace, reruns are guarded, and JSON mode is available for agent use.

The next useful step is not more static template expansion. It is proving how this coordination kit is adopted, resumed, verified, and evolved across real artifact-production work.

## Open Angles

1. Adoption model
   - Decide whether other workspaces use `codex-cns` through an absolute CLI path, installed command, Codex skill, copied instruction snippet, or target-workspace bootstrap.
   - Clarify whether `codex-cns` is a central kit, portable package, or both.

2. Trigger semantics
   - Define when Codex should proactively call `packet-route` or `artifact-harness` from ordinary user language.
   - Avoid making users remember internal packet names when the mission is clear.

3. Packet lifecycle
   - Define statuses beyond creation: draft, filled, reviewed, approved, executed, verified, superseded, archived.
   - Add resume and revision rules so packet directories remain trustworthy continuity evidence.

4. End-to-end proof
   - Run 2-3 real artifact-production replay cases from user mission to filled packets and final review.
   - Record which fields can be inferred, which require user approval, and which remain brittle.

5. Evidence model
   - Track whether each important claim comes from user instruction, repo evidence, inference, runtime output, test result, or human approval.
   - Consider a small evidence ledger rather than spreading provenance only across packet fields.

6. Security and prompt-injection model
   - Treat target-workspace instructions and files as potentially untrusted inputs when capability authorization is involved.
   - Define who can request, approve, deny, or escalate skills, plugins, tools, network use, and writes.

7. Schema and migration
   - Version the JSON output and packet schemas once the shape stabilizes.
   - Define compatibility and migration rules for older packet runs.

8. Runtime execution proof
   - Prove that CAP approval gates constrain actual runtime execution, not only the runtime mapping document.
   - Keep runtime adapters as execution layers, with evidence returned to local packets.

9. Human UX
   - Decide what the user should see in normal use and which internal names should remain background mechanics.
   - Keep the front door operational: artifact mission first, packet internals only when useful.

10. Failure recovery
    - Define repair paths for partially filled packets, inconsistent HR/TOP/CAP outputs, denied capabilities, or runtime mapping failures.
    - Prefer explicit fail-fast and resume behavior over silent compensation.

## Suggested Next Validation

Create an `artifact-harness replay` or benchmark lane with a small set of real tasks. For each replay, preserve:

- input user mission
- generated packet directory
- fields auto-filled vs manually clarified
- approvals or denied capabilities
- runtime mapping decision
- final artifact/review result
- failure or friction notes

This should answer whether the kit is only well-documented or actually useful for repeated Codex-native artifact production.
