# Storyboard Draft

## Chunk
- Topic: Unit 8, Probability Axioms
- Draft owner: Video Producer
- Status: proposed for rerun
- Intent: convert the rerun lesson brief into a shorter and more readable cut
- Version: rerun v1

## Source Grounding
- Current render to replace: `/Users/tom/Documents/PHD/Vis_Math/Slides/Lecture1/Lecture1_Unit8_ProbabilityAxioms.mp4`
- Current cue frames inspected:
  - `/Users/tom/Documents/PHD/Vis_Math/Slides/Lecture1/Unit8_check_8s.png`
  - `/Users/tom/Documents/PHD/Vis_Math/Slides/Lecture1/Unit8_check_17s.png`
  - `/Users/tom/Documents/PHD/Vis_Math/Slides/Lecture1/Unit8_latest_25s.png`
  - `/Users/tom/Documents/PHD/Vis_Math/Slides/Lecture1/Unit8_latest_40s.png`
  - `/Users/tom/Documents/PHD/Vis_Math/Slides/Lecture1/Unit8_latest_47s.png`

## Scene Plan
| Scene | Time | On-Screen Content | Spoken/Narration Intent | Visual Notes |
| --- | --- | --- | --- | --- |
| 1 | `00-05s` | Title `Probability Axioms` plus `P:\mathcal{B}\to\mathbb{R}` | Frame probability as a rule that assigns values to events | Keep one setup line only |
| 2 | `05-12s` | Axiom (1): $P(C)\ge 0$ | Any event probability is never negative | Keep one formula row plus a tiny non-negative bar cue |
| 3 | `12-20s` | Axiom (2): $P(\mathcal{C})=1$ with one full-coverage bar or box | The whole sample space carries total mass `1` | Remove the standard-normal histogram from this beat |
| 4 | `20-31s` | Axiom (3) split in two beats: `cannot happen together` first, then the additivity expression | Disjoint events add because there is no overlap to double-count | Delay the large union/sum formula until after the plain-language line lands |
| 5 | `31-42s` | Recap: finite partition example `P(C_1)+P(C_2)+P(C_3)=1` | This is the special case where disjoint pieces cover the whole sample space | Label it explicitly as `special case`, not `axiom` |

## Readability Risks
- Scene 4 can still become dense if the disjointness condition and the union/sum formula appear simultaneously.
- Scene 5 should keep only one recap formula and one short caption.

## Transition Risks
- The move from axiom (2) to axiom (3) needs a visible reset so the learner does not experience it as one continuous formula wall.
- The recap should visually separate itself from the axioms to avoid looking like axiom (4).

## Producer Decisions Already Locked
- Do not use the standard-normal histogram in the rerun.
- Use the plain phrase `cannot happen together` before the formal disjointness notation.
- Keep the partition recap in a visually distinct lower slot with a `special case` label.

## Open Questions
- none for the next production pass
