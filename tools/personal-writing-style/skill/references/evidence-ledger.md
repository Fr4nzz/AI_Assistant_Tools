# Evidence ledger

These examples come from the chats used to build Writing Style v4 and its ecology supplement. They are included here so the personal skill remains usable without its original workspace. The source locations remain the audit trail.

## Contents

- [Cut connective padding in stages](#pair-1-cut-connective-padding-in-stages)
- [Keep the familiar scientific noun](#pair-2-keep-the-familiar-scientific-noun)
- [Stop when the explanation becomes the distraction](#pair-3-stop-when-the-explanation-becomes-the-distraction)
- [Replace compressed shorthand with the reader's term](#pair-4-replace-compressed-shorthand-with-the-readers-term)
- [Separate internal model labels from manuscript names](#pair-5-separate-internal-model-labels-from-manuscript-names)
- [V4 source notes](#v4-source-notes)
- [Current explicit instructions](#current-explicit-instructions)

Ecology transcript:

`~/.codex/sessions/2026/07/16/rollout-2026-07-16T16-10-25-019f6cc4-3595-7d01-a357-5f1d19efa953.jsonl`

## Pair 1: Cut connective padding in stages

The proposed sentence was:

> **Canopy versus understory.** The canopy and understory cameras are compared directly in terms of insect abundance, number of families and community composition. Vertical stratum is the fixed effect and night is random, following the shared analytical framework described above.

The user first asked whether “directly” was necessary, then said that “in terms of” also felt bloated. The resulting sentence was:

> **Canopy versus understory.** The canopy and understory cameras are compared for insect abundance, number of families and community composition. Vertical stratum is the fixed effect and night is random, following the shared analytical framework described above.

Sources: JSONL line 11641 at `2026-07-23T14:19:42.734Z` and line 11650 at `2026-07-23T14:20:10.227Z`. This is direct, repeated correction evidence. It also shows the user retaining “number of families” after questioning whether family-level richness and community composition were redundant at line 11631, `2026-07-23T14:19:04.536Z`.

Why the outcome names remained: “number of families” and “community composition” are not two names for the same measurement. The first is a count of represented families. The second records their identities and may include their relative abundances. The revision improved access to the richness measure while preserving both scientific outcomes.

Limit of the inference: “directly” and “in terms of” were redundant in this sentence because “compared for” expressed the full relationship. This does not make either expression globally forbidden.

## Pair 2: Keep the familiar scientific noun

The crowded version was:

> Develop and evaluate an open-source pipeline that segments insects from light-trap photographs and assigns them to taxonomic ranks from order to species using a hierarchy-consistent taxonomic classifier trained on light-trap-relevant Neotropical taxa.

The user noticed three nearby uses of the same word family: “taxonomic ranks”, “taxonomic classifier”, and “taxa”. The first revision reduced that crowding:

> Develop and evaluate an open-source pipeline that segments insects from light-trap photographs and identifies them at ranks from order to species using a hierarchy-consistent taxonomic classifier trained on Neotropical insects relevant to nocturnal light-trap monitoring.

The user decided that restoring “taxa” sounded better, then preferred the version that also retained “insect”:

> Develop and evaluate an open-source pipeline that segments insects from light-trap photographs and identifies them from order to species using a hierarchy-consistent taxonomic classifier trained on Neotropical insect taxa relevant to nocturnal light-trap monitoring.

Sources: JSONL lines 10440, 10450, and 10459, from `2026-07-22T02:27:30.814Z` to `2026-07-22T02:29:00.191Z`. This is a direct correction sequence. It supports useful repetition and familiar scientific nouns, not unrestricted repetition.

Why the final wording worked better: the first half no longer repeats “taxonomic” around “ranks” and “classifier”. At the end, “insect taxa” is more precise than using “insects” for a curated set of taxonomic units. “Insect” also makes the biological scope explicit. The final version keeps repetition that carries meaning after removing repetition that only made the sentence heavy.

Limit of the inference: repeat a scientific noun when it is the clearest name for the same object. This example does not justify dense repetition of related word forms within one clause.

## Pair 3: Stop when the explanation becomes the distraction

The proposed explanation was:

> Sampling night within site is a random effect because observations at 20:00, 22:00, 03:00 and 05:00 share the same trap deployment and broader nightly conditions.

The user said it was too detailed. The accepted simplification was:

> **Through the night and across months.** Sampling hour and month are fixed effects, while sampling night is a random effect. Marginal and conditional R² describe the variation explained by the fixed effects and by the complete model, respectively (Nakagawa & Schielzeth, 2013).

Source: JSONL line 11806, `2026-07-23T14:52:17.366Z`, followed by the proposed simplification at `2026-07-23T14:52:26.865Z`. This directly supports restraint in technical explanation. It does not establish that the entire paragraph was written by the user.

Why the shorter version worked better: the user had first asked for more than the obvious statement that observations from one night were not independent. The attempted answer then introduced the four clock times, trap deployment, nightly conditions, and nesting within sites. That detail answered several implementation questions at once, but it interrupted a proposal paragraph whose immediate purpose was to state the model structure. Naming sampling night as the random effect was enough there.

Limit of the inference: the rejected details may still belong in a Methods section. The lesson is to place explanation where the reader needs it, not to omit the rationale everywhere.

## Pair 4: Replace compressed shorthand with the reader's term

The proposed wording was:

> code and weights for the insect segmentation model and taxonomic head

The user said “taxonomic head” sounded weird. The revision was:

> Deliverables include code and weights for the insect segmentation and taxonomic classification models, the curated TreeOfLife training taxa, and reproducible evaluation scripts.

Source: JSONL line 12025, `2026-07-23T15:24:08.716Z`, followed by the revision at `2026-07-23T15:24:14.476Z`. This is direct correction evidence for an ecology-facing technical context.

Why the revision worked better: “head” is meaningful when discussing the internal architecture attached to an encoder. In a deliverables list, “taxonomic classification model” tells an ecology reader what will be delivered and matches the parallel phrase “insect segmentation model”. The revision also followed an earlier correction in the same exchange. The user first made “model weights” and “taxon lists” concrete, then asked to shorten the explanation once the deliverables were identifiable.

Limit of the inference: use “classification head” in an architecture discussion when that component distinction matters. Prefer “classification model” when referring to the usable model as a deliverable or scientific tool.

## Pair 5: Separate internal model labels from manuscript names

The manuscript and its handoff materials used labels such as:

> YOLO v3, YOLO v5, and YOLO v5.1

The user explained that these were informal development names for successive segmentation-training attempts. They were not names chosen for publication. The requested replacement was:

> YOLO26-seg

or, where the exact architecture name was unnecessary:

> the current segmentation model

He also rejected the manuscript phrase:

> After the July 3 manuscript pass

Why the correction matters: the internal labels preserve experimental provenance, but they misidentify the final model when presented to manuscript readers. The dated phrase similarly records the editing process instead of describing the current science. Publication prose should use a stable model name or functional description and state the present method directly.

Limit of the inference: preserve internal labels in experiment tracking, audit trails, and mappings that connect the published model to its development history. Remove them only from contexts where readers would mistake them for final scientific names.

Source: original v4 transcript line 1878, `2026-07-08T20:04:37.293Z`. The follow-up instruction mapping internal labels to manuscript wording appears at `2026-07-08T20:05:25.004Z`.

## V4 source notes

Original v4 transcript:

`~/.codex/sessions/2026/07/07/rollout-2026-07-07T08-56-06-019f3cdd-579a-71f2-b769-642131541739.jsonl`

1. The user warned that one improved phrase should not become a ban and that an accepted edit may only have escaped notice during a quick review. “Detailed” was the example of unnecessary self-praise. Source: line 571, `2026-07-07T14:58:41.085Z`.
2. The user rejected manuscript wording that read like an update log and separated internal iteration labels from manuscript-facing model names. The full example now appears in correction pair 5. Source: line 1878, `2026-07-08T20:04:37.293Z`.
3. The InsectAI material that the user identified as a strong example favored exact technical terms with brief explanations for ecologists, justified importance claims, citations close to claims, and operational Methods. Source summary: `~/Documents/CodeProjs/ithomiini_maps/context/chat_context/agent_outputs/claude_b98ce9f5_insectai_thesis_writing_style.md`, especially lines 43 to 65 and 79 to 95.

## Current explicit instructions

The user stated on 15 August 2026: “I prefer to always avoid em dashes.” This is an invariant and supersedes older guidance that treated em dashes only as a tendency.

The user stated on 17 August 2026: “I actually dont use semicolons so I actually prefer that we havent included semicolons in the skill.” This supports avoiding semicolons as a personal punctuation preference.
