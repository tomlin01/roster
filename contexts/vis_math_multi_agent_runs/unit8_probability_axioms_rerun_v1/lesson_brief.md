# Lesson Brief

## Chunk
- Topic: Unit 8, Probability Axioms
- Owner: Teacher
- Status: promoted
- Intent: define a cleaner rerun contract for `/Users/tom/Documents/PHD/Vis_Math/Slides/Lecture1/Lecture1_Unit8_ProbabilityAxioms.mp4`
- Target audience: beginner learner who knows basic events and sample space intuition but does not yet track dense notation well
- Estimated duration: 40 to 48 seconds

## Source Grounding
- Current render: `/Users/tom/Documents/PHD/Vis_Math/Slides/Lecture1/Lecture1_Unit8_ProbabilityAxioms.mp4`
- Existing storyboard reference: `/Users/tom/Documents/PHD/Vis_Math/Slides/Lecture1/Lecture1_storyboard_v2.md`
- Supporting source: `/Users/tom/Documents/PHD/Vis_Math/Slides/Lecture1.tex`

## Learning Goal
- By the end of this chunk, the learner should be able to say:
  - a probability function never assigns a negative value,
  - the whole sample space has total probability `1`,
  - disjoint events add,
  - the finite partition sum-to-one statement is a special case, not a fourth axiom.

## Must-Be-Correct Points
- Axiom (1): $P(C) \ge 0$ for every event $C \in \mathcal{B}$.
- Axiom (2): $P(\mathcal{C}) = 1$ means the entire sample space has total mass `1`.
- Axiom (3): for pairwise disjoint events, probability of the union equals the sum of probabilities.
- The finite partition identity $\sum_i P(C_i)=1$ should be presented only as a direct consequence of axioms (2) and (3), not as a peer formula.

## Can-Be-Simplified Points
- The rerun does not need the full countable-additivity limit notation if that notation hurts first-pass comprehension.
- The rerun may say `cannot happen together` before formally emphasizing `pairwise disjoint`.
- The rerun may defer the standard-normal histogram entirely, because it is not necessary to explain axiom (2).

## Known Problems In Current Cut
- The current duration is about `58.8s`, which is materially longer than the storyboard target `35-45s`.
- The `standard normal` visual around the axiom (2) segment risks implying that the axiom is tied to one distribution family rather than the whole sample space concept.
- The axiom (3) segment stacks the disjointness condition and the large union/sum formula too quickly for a beginner viewer.
- The later finite-partition sum-to-one line arrives without a clear bridge that marks it as a consequence rather than a new axiom.

## Teaching Order
1. Setup: probability is a function on events.
2. Axiom (1): non-negativity.
3. Axiom (2): the whole sample space has total mass `1`, using one plain coverage visual.
4. Axiom (3): first state `cannot happen together`, then show the additivity relation.
5. Recap: finite partition example as a special case of axioms (2) and (3).

## Open Questions
- none for the rerun brief; avoid the standard-normal detour in this version
