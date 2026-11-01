# Evidence ledger

These correction sequences come from chats in which the user revised a manuscript and a proposal. The originals describe unpublished work, so this public copy replaces them with invented sentences from unrelated fields that show the same kind of correction. The user's reasons and the limits are kept.

## Contents

- [Cut connective padding in stages](#pair-1-cut-connective-padding-in-stages)
- [Keep the familiar precise noun](#pair-2-keep-the-familiar-precise-noun)
- [Stop when the explanation becomes the distraction](#pair-3-stop-when-the-explanation-becomes-the-distraction)
- [Replace compressed shorthand with the reader's term](#pair-4-replace-compressed-shorthand-with-the-readers-term)
- [Separate internal model labels from manuscript names](#pair-5-separate-internal-model-labels-from-manuscript-names)
- [Other early notes](#other-early-notes)
- [Current explicit instructions](#current-explicit-instructions)

## Pair 1: Cut connective padding in stages

An invented sentence in the same shape:

> The two checkout designs are evaluated directly in terms of completion time, number of errors and the kinds of error users make.

The user's correction removed the linking words one at a time, first "directly" and then "in terms of":

> The two checkout designs are evaluated for completion time, number of errors and the kinds of error users make.

This is direct, repeated correction evidence. The user also kept two outcomes that look redundant at first sight.

Why the outcome names remained: "number of errors" and "the kinds of error" are not two names for the same measurement. The first is a count. The second records which errors occurred. The revision kept both outcomes and removed only the words that carried no relationship.

Limit of the inference: "directly" and "in terms of" were redundant in the original sentence because the plain preposition expressed the full relationship. This does not make either expression globally forbidden.

## Pair 2: Keep the familiar precise noun

An invented crowded version:

> Build an open-source tool that sorts archive letters into catalogue levels from collection to item using a catalogue model trained on catalogued sources.

Three nearby words come from the same family: "catalogue levels", "catalogue model" and "catalogued". The first revision reduced that crowding but lost precision:

> Build an open-source tool that sorts archive letters into levels from collection to item using a hierarchical model trained on old letters.

The preferred version restored the precise noun for the units and kept the word that states the scope:

> Build an open-source tool that sorts archive letters from collection to item using a hierarchical model trained on catalogued archive records.

This pattern supports useful repetition and familiar precise nouns, not unrestricted repetition.

Why the final wording works better: the first half no longer repeats the same word family. At the end, "records" names the curated units precisely, and "archive" states their scope. The final version keeps repetition that carries meaning after removing repetition that only made the sentence heavy.

Limit of the inference: repeat a precise noun when it is the clearest name for the same object. This does not justify dense repetition of related word forms within one clause.

## Pair 3: Stop when the explanation becomes the distraction

An invented over-detailed explanation:

> Participant is a random effect because the three tasks each person completes share the same device, the same session and the same level of experience.

The preferred version only states the model structure:

> Interface and task order are fixed effects, and participant is a random effect.

This supports restraint in technical explanation within a paragraph whose job is to state a model.

Why the shorter version works better: the user had first asked for more than the obvious statement that observations from one person are not independent. The attempted answer then listed every shared condition. That detail answered several implementation questions at once, but it interrupted a paragraph whose immediate purpose was to state the model structure. Naming the random effect was enough there.

Limit of the inference: the rejected details may still belong in a Methods section. The lesson is to place explanation where the reader needs it, not to omit the rationale everywhere.

## Pair 4: Replace compressed shorthand with the reader's term

An invented deliverables phrase with insider shorthand:

> checkpoints for the speech encoder and the LM head

A reader outside machine learning would find the shorthand odd. The revision names what is delivered:

> The project delivers the code and trained weights for the transcription and language models, the word list used in training, and the evaluation scripts.

Why the revision works better: "head" and "checkpoint" are meaningful in an architecture discussion. In a deliverables list, "language model" and "trained weights" tell a general reader what will be delivered, and the two model names now match each other. As in the original exchange, the deliverables were first made concrete and then the explanation was shortened once they were identifiable.

Limit of the inference: use "head" in an architecture discussion when that component distinction matters. Prefer the model's role when referring to it as a deliverable or tool.

## Pair 5: Separate internal model labels from manuscript names

The manuscript and its handoff materials used internal labels such as:

> trial amber, trial violet and trial violet-2

These were informal development names for successive training attempts, not names chosen for publication. The replacement was the published architecture name or, where the exact architecture name was unnecessary:

> the current segmentation model

The user also rejected a manuscript phrase of the form:

> After the second manuscript pass

Why the correction matters: the internal labels preserve experimental provenance, but they misidentify the final model when presented to manuscript readers. The dated phrase similarly records the editing process instead of describing the current science. Publication prose should use a stable model name or functional description and state the present method directly.

Limit of the inference: preserve internal labels in experiment tracking, audit trails and mappings that connect the published model to its development history. Remove them only from contexts where readers would mistake them for final scientific names.

## Other early notes

1. The user warned that one improved phrase should not become a ban and that an accepted edit may only have escaped notice during a quick review. "Detailed" was the example of unnecessary self-praise.
2. The user rejected manuscript wording that read like an update log and separated internal iteration labels from manuscript-facing model names. Pair 5 shows the pattern.
3. A writing sample that the user identified as strong favoured exact technical terms with brief explanations for the field's readers, justified importance claims, citations close to claims, and operational Methods.

## Current explicit instructions

The user stated directly that they always want em dashes avoided. This is an invariant and supersedes older guidance that treated em dashes only as a tendency.

The user also said that they do not use semicolons and prefer that the skill does not use them. This supports avoiding semicolons as a personal punctuation preference.
