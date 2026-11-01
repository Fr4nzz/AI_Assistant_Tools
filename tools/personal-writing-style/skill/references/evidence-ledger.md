# Evidence ledger

These correction sequences come from the chats in which the user revised a manuscript and a thesis proposal. The original sentences describe unpublished work, so this public copy replaces them with invented sentences that show the same correction. The order of the corrections, the user's reasons and the limits are unchanged.

## Contents

- [Cut connective padding in stages](#pair-1-cut-connective-padding-in-stages)
- [Keep the familiar scientific noun](#pair-2-keep-the-familiar-scientific-noun)
- [Stop when the explanation becomes the distraction](#pair-3-stop-when-the-explanation-becomes-the-distraction)
- [Replace compressed shorthand with the reader's term](#pair-4-replace-compressed-shorthand-with-the-readers-term)
- [Separate internal model labels from manuscript names](#pair-5-separate-internal-model-labels-from-manuscript-names)
- [Other early notes](#other-early-notes)
- [Current explicit instructions](#current-explicit-instructions)

## Pair 1: Cut connective padding in stages

The proposed sentence was:

> **Morning versus afternoon.** The morning and afternoon walks are compared directly in terms of pollinator abundance, number of families and community composition. Time of day is the fixed effect and survey day is random, following the shared analytical framework described above.

The user first asked whether "directly" was necessary, then said that "in terms of" also felt bloated. The resulting sentence was:

> **Morning versus afternoon.** The morning and afternoon walks are compared for pollinator abundance, number of families and community composition. Time of day is the fixed effect and survey day is random, following the shared analytical framework described above.

This is direct, repeated correction evidence. It also shows the user retaining "number of families" after questioning whether family-level richness and community composition were redundant.

Why the outcome names remained: "number of families" and "community composition" are not two names for the same measurement. The first is a count of represented families. The second records their identities and may include their relative abundances. The revision improved access to the richness measure while preserving both scientific outcomes.

Limit of the inference: "directly" and "in terms of" were redundant in this sentence because "compared for" expressed the full relationship. This does not make either expression globally forbidden.

## Pair 2: Keep the familiar scientific noun

The crowded version was:

> Build and test an open-source tool that detects seedlings in drone images and assigns them to taxonomic ranks from family to species using a taxonomic classifier trained on locally recorded taxa.

The user noticed three nearby uses of the same word family: "taxonomic ranks", "taxonomic classifier" and "taxa". The first revision reduced that crowding:

> Build and test an open-source tool that detects seedlings in drone images and identifies them at ranks from family to species using a taxonomic classifier trained on plants recorded in local seedling plots.

The user decided that restoring "taxa" sounded better, then preferred the version that also retained "plant":

> Build and test an open-source tool that detects seedlings in drone images and identifies them from family to species using a taxonomic classifier trained on plant taxa recorded in local seedling plots.

This is a direct correction sequence. It supports useful repetition and familiar scientific nouns, not unrestricted repetition.

Why the final wording worked better: the first half no longer repeats "taxonomic" around "ranks" and "classifier". At the end, "plant taxa" is more precise than using "plants" for a curated set of taxonomic units. "Plant" also makes the biological scope explicit. The final version keeps repetition that carries meaning after removing repetition that only made the sentence heavy.

Limit of the inference: repeat a scientific noun when it is the clearest name for the same object. This example does not justify dense repetition of related word forms within one clause.

## Pair 3: Stop when the explanation becomes the distraction

The proposed explanation was:

> Survey day within site is a random effect because counts at the two walks of a day share the same observer, plot visit and weather.

The user said it was too detailed. The accepted simplification was:

> **Through the day and across months.** Time of day and month are fixed effects, while survey day is a random effect. Marginal and conditional R² describe the variation explained by the fixed effects and by the complete model, respectively (Nakagawa & Schielzeth, 2013).

This directly supports restraint in technical explanation. It does not establish that the entire paragraph was written by the user.

Why the shorter version worked better: the user had first asked for more than the obvious statement that counts from one day were not independent. The attempted answer then introduced the walk times, the plot visit, the weather and nesting within sites. That detail answered several implementation questions at once, but it interrupted a proposal paragraph whose immediate purpose was to state the model structure. Naming survey day as the random effect was enough there.

Limit of the inference: the rejected details may still belong in a Methods section. The lesson is to place explanation where the reader needs it, not to omit the rationale everywhere.

## Pair 4: Replace compressed shorthand with the reader's term

The proposed wording was:

> code and weights for the seedling detection model and taxonomic head

The user said "taxonomic head" sounded weird. The revision was:

> Deliverables are code and trained weights for the seedling detection and taxonomic classification models, the training taxon list, and the evaluation scripts.

This is direct correction evidence for an ecology-facing technical context.

Why the revision worked better: "head" is meaningful when discussing the internal architecture attached to an encoder. In a deliverables list, "taxonomic classification model" tells an ecology reader what will be delivered and matches the parallel phrase "seedling detection model". The revision also followed an earlier correction in the same exchange. The user first made "model weights" and "taxon lists" concrete, then asked to shorten the explanation once the deliverables were identifiable.

Limit of the inference: use "classification head" in an architecture discussion when that component distinction matters. Prefer "classification model" when referring to the usable model as a deliverable or scientific tool.

## Pair 5: Separate internal model labels from manuscript names

The manuscript and its handoff materials used labels such as:

> trial amber, trial violet and trial violet-2

The user explained that these were informal development names for successive training attempts. They were not names chosen for publication. The requested replacement was the published architecture name or, where the exact architecture name was unnecessary:

> the current segmentation model

The user also rejected a manuscript phrase of the form:

> After the second manuscript pass

Why the correction matters: the internal labels preserve experimental provenance, but they misidentify the final model when presented to manuscript readers. The dated phrase similarly records the editing process instead of describing the current science. Publication prose should use a stable model name or functional description and state the present method directly.

Limit of the inference: preserve internal labels in experiment tracking, audit trails and mappings that connect the published model to its development history. Remove them only from contexts where readers would mistake them for final scientific names.

## Other early notes

1. The user warned that one improved phrase should not become a ban and that an accepted edit may only have escaped notice during a quick review. "Detailed" was the example of unnecessary self-praise.
2. The user rejected manuscript wording that read like an update log and separated internal iteration labels from manuscript-facing model names. The full example appears in pair 5.
3. A writing sample that the user identified as strong favoured exact technical terms with brief explanations for ecologists, justified importance claims, citations close to claims, and operational Methods.

## Current explicit instructions

The user stated: "I prefer to always avoid em dashes." This is an invariant and supersedes older guidance that treated em dashes only as a tendency.

The user also stated: "I actually dont use semicolons so I actually prefer that we havent included semicolons in the skill." This supports avoiding semicolons as a personal punctuation preference.
