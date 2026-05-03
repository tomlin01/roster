# Roster v0.10.0 Capability-Aware Role Execution

Date: `2026-05-03`
Status: `implemented surface`

## Purpose

Define the next Roster stage after `v0.9.0` Role Interaction Patterns.

`v0.9.0` answers:

```text
Who works with whom, around which artifact, and with what interaction pattern?
```

`v0.10.0` should answer:

```text
What platform capabilities does each role need to actually do its work?
```

This moves Roster from role planning toward execution planning without turning
Roster into a new runtime or tool owner.

## Core Definition

`v0.10.0` is:

```text
Capability-Aware Role Execution
```

Roster should plan roles by:

```text
role -> work -> interaction -> capability need -> availability -> fallback
```

This is broader than subagents. Subagents are one possible execution capability,
not the whole topic.

## Why This Matters

The user should be able to delegate a Roster task and not manually manage which
role needs which LLM platform tool.

Examples:

- A Research Reviewer may need web search or browser lookup.
- A Source Verifier may need citations and access dates.
- A Visual QA role may need screenshot, render, OCR, playback, or CV review.
- A Slide Producer may need a presentation plugin or PPTX skill.
- A Skill Reviewer may need filesystem read access and patch/review evidence.
- A Statistical Reviewer may need Python, R, or a statistics skill.
- A Coordinator may need subagents only when separate execution improves quality
  more than it adds coordination cost.

Roster should make those needs explicit internally, then use the current host
capabilities when available.

## Capability Categories

Use these categories as the initial vocabulary:

- `reasoning_only`
  - no special tool needed;
  - useful for simulated perspectives, critique, planning, and synthesis.
- `filesystem_read`
  - inspect local files, skill docs, packets, source artifacts, or repo state.
- `filesystem_write`
  - create or modify local artifacts.
- `code_execution`
  - run scripts, tests, data processing, local validation, or conversion.
- `web_search`
  - look up current or external public information.
- `browser`
  - inspect pages, docs, local apps, rendered outputs, or visual web artifacts.
- `visual_capture`
  - screenshot, render/export, playback frame, or screen evidence acquisition.
- `vision_review`
  - OCR, image inspection, visual overlap/readability checks, or CV review.
- `specialist_skill`
  - use another installed skill as a bounded producer, verifier, or source
    reference.
- `plugin_or_connector`
  - use an installed plugin, app connector, or external service integration.
- `subagent_execution`
  - split work into a separate agent only when runtime support exists and the
    quality gain justifies coordination cost.

## Availability States

For each needed capability, Roster should be able to describe one of these
states:

- `available`
  - current host/runtime can use it now.
- `available_after_reload`
  - installed or registered, but the host likely needs reload/restart.
- `available_if_approved`
  - capability exists but should wait for an approval gate or explicit user
    approval.
- `unknown`
  - Roster cannot determine availability from local evidence.
- `unavailable`
  - current host/runtime does not expose this capability.

This availability state should inform execution and fallback, not ordinary
first-touch verbosity.

## Capability-Aware Work Card Extension

When a role is expanded into a work card, `v0.10.0` should allow capability
planning fields such as:

```yaml
capability_needs:
  - capability: web_search
    purpose: verify current public source claims
    availability: available | unknown | unavailable | available_if_approved
    evidence_expected: URLs, source dates, short source summary
    fallback: ask user for sources or use local files only
  - capability: specialist_skill
    skill: visual-presentation-system
    purpose: plan presentation artifact strategy
    availability: available
    evidence_expected: chosen artifact form and handoff packet
    fallback: manual artifact strategy note
```

This extends work cards without replacing the existing role, interaction, CAP,
runtime, verification, or acceptance boundaries.

## User-Facing Behavior

Ordinary users should not see a capability matrix by default.

Good first-touch shape:

```text
這個任務需要內容整理、資料查證和交付檢查。
我會先用本機資料整理第一版；如果需要外部查證，我會讓查證角色去找來源並留下引用。
如果目前環境不能查，我會改請你提供來源。
```

For visual work:

```text
這個任務需要看畫面。
我會先嘗試用既有輸出、截圖或 render 做檢查；如果環境拿不到畫面，再請你提供截圖。
```

For specialist skills:

```text
這個任務需要簡報策略和成品檢查。
我會讓 Roster 負責隊形和品質線，讓簡報相關 skill 處理專門產出，再把結果交回 Quality 檢查。
```

Do not expose internal labels such as `available_if_approved`,
`subagent_execution`, or `Capability Access Packet` unless the user asks for
debug, review, governance, or implementation detail.

## Subagent Policy As A Subsection

Subagents should be treated as one capability, not the headline.

Use subagents when:

- the role needs a clearly separate work product;
- independent context reduces drift or error;
- parallel execution reduces wall time;
- the runtime supports safe delegation;
- the expected quality gain is larger than coordination cost.

Do not use subagents when:

- the task is small enough for one agent to cover all layers;
- the role is only a simulated perspective;
- handoff cost would exceed quality gain;
- runtime support is unknown or unavailable;
- the user needs a quick answer more than formal decomposition.

Fallback when subagents are unavailable:

```text
Simulate separated perspectives inside one agent, but keep their checks
explicit.
```

## Relationship To CAP

Capability-aware role execution does not grant authority.

Boundary:

- Roster identifies capability needs.
- Team Architect can place those needs into the task graph.
- CAP authorizes skills, plugins, tools, approval gates, and runtime allowlists.
- Runtime adapters execute only after the relevant boundary is satisfied.

Do not let Roster say that a role has tool authority just because it needs a
tool.

## Example Role Cards

### Research Reviewer

- responsibility: verify external claims and current context;
- capability_needs: `web_search`, `browser`;
- evidence_expected: URLs, dates, source summaries;
- fallback: ask user for sources or use local documents only.

### Visual QA

- responsibility: inspect visual clarity and delivery artifacts;
- capability_needs: `visual_capture`, `vision_review`, `browser`;
- evidence_expected: screenshot, render, frame, OCR/CV finding;
- fallback: ask user for screenshot or mark visual acceptance as limited.

### Slide Producer

- responsibility: produce the presentation artifact;
- capability_needs: `specialist_skill`, `plugin_or_connector`, possibly
  `filesystem_write`;
- evidence_expected: generated deck or slide artifact plus verification result;
- fallback: outline or HTML draft when editable deck tooling is unavailable.

### Skill Reviewer

- responsibility: review another skill or workflow;
- capability_needs: `filesystem_read`, possibly `filesystem_write` for patches;
- evidence_expected: diagnosis, role/team review, optional file-line findings;
- fallback: plain-language diagnosis without patch.

### Statistical Reviewer

- responsibility: check scoring, data assumptions, or analysis outputs;
- capability_needs: `code_execution`, `specialist_skill`;
- evidence_expected: reproducible check, test cases, assumption notes;
- fallback: conceptual review only.

## Acceptance Signals

`v0.10.0` is successful when:

- Roster docs state that roles carry capability needs, not just
  responsibilities.
- Work cards can express needed platform capabilities and fallback behavior.
- First-touch replies stay human-facing and do not expose capability tables by
  default.
- Health or capability reporting can describe whether key capability classes
  are known, available, unavailable, or require approval where practical.
- Subagent use is described as conditional capability use, not as a default for
  every role.
- Existing boundaries remain intact: Roster plans needs, CAP authorizes access,
  runtime executes.

## Implemented Surface

The v0.10.0 implementation surface is intentionally small:

- Roster skill and plugin docs explain Capability-Aware Role Execution while
  keeping first-touch replies short and non-mechanical.
- Team Operating Packet work cards can record `capability_needs` with
  capability, purpose, availability, evidence expected, and fallback.
- `roster-health --json` reports a conservative `capability_summary` over the
  v0.10 categories and uses `unknown` for host-dependent capabilities that the
  repo-local health check cannot prove.
- `roster-health` does not implement or invoke new web search, browser, visual
  capture, CV, connector, or subagent adapters.

The health summary follows the boundary:

```text
Roster plans capability needs; CAP authorizes access; runtime executes.
```

## Out Of Scope

Do not implement these in `v0.10.0`:

- new web-search adapter shipped inside Roster;
- new persistent runtime service;
- Rust rewrite;
- automatic connector login or external actions;
- replacing CAP with Roster;
- forcing every role into a separate subagent;
- guaranteeing identical behavior across Codex, Claude, and other hosts.

## Open Questions

- Should capability availability be recorded in packet artifacts, or remain a
  runtime diagnostic beyond the current `roster-health --json` summary?
- Should Roster ask the user before using web search for low-risk public lookup,
  or only disclose when it does so?
- How much of this belongs in public README versus internal skill docs?
