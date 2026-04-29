# Roster

Roster helps Codex organize artifact work into a working team, a short quality
loop, and clear tool boundaries.

Use it when a task is more than a one-shot answer: slides, videos, documents,
datasets, code changes, reviews, or any project artifact that benefits from
roles, checks, and handoff continuity.

Roster is Codex-native. It does not require a persistent server, daemon,
database, or separate orchestration UI. It writes task packets into the same
workspace where the work happens.

## Install

Clone the kit and install the local `roster` skill into your Codex home:

```bash
git clone https://github.com/tomlin01/roster.git
cd roster
./scripts/brain.sh roster-install --codex-home ~/.codex --json
```

Check that Roster can see a target workspace and write/clean a smoke packet
there:

```bash
./scripts/brain.sh roster-health --codex-home ~/.codex --path <workspace-folder> --json
```

If your workflow needs provider-backed LLM or vision/CV checks, configure local
Codex auth or a provider environment variable, then include it in health:

```bash
./scripts/brain.sh roster-health --codex-home ~/.codex --path <workspace-folder> --provider openai --auth-env OPENAI_API_KEY --json
```

`roster-health` checks local setup only. It does not print secrets and does not
make a remote model call.

## Use

Open Codex in the project workspace and say:

```text
Roster, help me plan this slide task.
```

or:

```text
Roster, 幫我把這個影片任務安排好。
```

Roster should answer in plain project language: what team shape it will use,
what quality checks matter, and what the next useful phrase is. You should not
need to say internal workflow names during normal use.

Current truthful invocation:

```text
Roster, <your task>
```

`@roster` is a future product target, not a verified installed Codex mention,
plugin/app mention, or slash command. The route helper can recognize the
literal text `@roster`, but that is not the same as Codex mention interception.

## What Roster Does

For a non-trivial artifact task, Roster helps Codex:

- clarify the task and output boundary
- choose a working team or review perspectives
- decide what quality checks apply now
- keep tool and provider access explicit
- write resumable task packets under the target workspace
- preserve enough context for future Codex sessions or reviewers

Packet output stays with the work:

```text
<workspace>/contexts/artifact_harness_runs/<packet-id>/
<workspace>/contexts/artifact_harness_registry.json
```

If Codex cannot tell which workspace should receive files, it should ask one
short location question before writing.

## Quality

Quality is built into Roster as a short self-check loop.

For text and planning work, Roster should check whether the current artifact is
clear, internally consistent, and ready to hand off.

For visual work, such as slides, screenshots, rendered scenes, videos, UI, or
presentations, Roster should try to inspect actual visual evidence before
calling the output done. A typical loop is:

1. produce the first version
2. inspect a screenshot, render, frame, or playback segment
3. catch text occlusion, key element overlap, poor readability, missing
   content, or slide/render/video mismatch
4. make a focused correction
5. repeat for 2-3 bounded iterations, or stop earlier when no material issue
   remains

When Roster cannot obtain visual evidence itself, it should say that visual
quality is limited and ask for a screenshot or frame as the fallback.

## Preferences

Roster can keep a tiny workspace-local preference file for explicit future
coordination preferences:

```text
Roster, 記住以後 Lecture1 的影片任務都先檢查文字遮擋。
```

The adapter writes:

```text
<workspace>/contexts/roster_preferences.json
```

This is not general chat memory. Use it for recurring Roster preferences such
as team shape, quality focus, visual inspection habits, naming conventions, or
preferred coordination wording.

## Uninstall

Remove the installed skill from a Codex home:

```bash
./scripts/brain.sh roster-uninstall --codex-home ~/.codex --json
```

By default, uninstall only removes a Roster skill installed by this kit. If a
different same-name skill exists, it refuses unless `--force` is explicit.

## Debug Commands

These commands are for setup, reviewers, and debugging. They are not the normal
chat path.

```bash
./scripts/brain.sh packet-route "<utterance>" --path <workspace-folder> --json
./scripts/brain.sh packet-route "<utterance>" --path <workspace-folder> --create --json
./scripts/brain.sh artifact-harness "<mission>" --path <workspace-folder> --json
./scripts/brain.sh roster-preferences list --path <workspace-folder> --json
```

For deeper internal architecture, packet lifecycle, runtime checks, and policy
references, see [docs/DEVELOPER_REFERENCE.md](./docs/DEVELOPER_REFERENCE.md).

## Credits And Third-Party References

Roster includes local reference notes and adaptation history informed by
[msitarzewski/agency-agents](https://github.com/msitarzewski/agency-agents),
an MIT-licensed AI agent role library.

The vendored snapshot under
[`references/third_party/agency-agents/`](./references/third_party/agency-agents/)
is kept as read-only reference material. It is not installed by
`roster-install`, and it is not the active Roster runtime.

Roster's active roles, quality behavior, packet workflow, and installation
surface are local adaptations under this repository's own workflow boundaries.

See [THIRD_PARTY_NOTICES.md](./THIRD_PARTY_NOTICES.md) for provenance and
license details.
