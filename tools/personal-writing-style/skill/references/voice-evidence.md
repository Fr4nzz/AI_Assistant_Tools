# Voice grounded in corrections

Use this evidence as calibration, not as a phrase bank. The user's direct comments outrank these summaries. A repeated explicit correction is stronger than a single correction. An unremarked acceptance is weak evidence. Read [evidence-ledger.md](evidence-ledger.md) only when the exact sentence history or source location matters.

## The governing preference

The user edits by asking what a phrase means and whether each word helps express that meaning. The preferred prose is precise without sounding polished for its own sake. It retains scientific distinctions, useful repetition, and necessary caveats. It cuts connective padding, self-praise, compressed jargon, and explanations that outgrow their purpose.

## Calibrate from current writing

When the user provides a recent writing sample, treat it as the best guide to the voice needed for that task. Notice sentence length, word choice, paragraph openings, punctuation, transitions, use of first person, and how directly the sample moves between ideas. Reproduce the pattern rather than copying memorable phrases.

The sample provides evidence, not a template. Preserve differences required by the new genre, reader, or subject. Direct feedback given with the current task outranks habits inferred from an older sample.

## Directly supported patterns

### Cut wording that adds no relationship

**Difference:** “Compared directly in terms of” became “compared for”. “Compared” already expresses the comparison, and the measured outcomes can follow “for” directly.

**Reason:** The shorter wording preserves the same actors, outcomes, method, and interpretation.

**Limit:** Keep an adverb or linking phrase when it changes the method, direction, scope, or interpretation.

Evidence: [correction pair 1](evidence-ledger.md#pair-1-cut-connective-padding-in-stages).

### Preserve a distinction while making its name clearer

**Difference:** “Family-level richness” became “number of families”, while “community composition” remained a separate outcome. The first counts represented families. The second describes which families occur and may include their relative abundances.

**Reason:** The plainer label improves first-reading comprehension without merging two measurements or weakening the design.

**Limit:** Retain the formal term when it is needed to identify the analysis or metric precisely.

Evidence: [correction pair 1](evidence-ledger.md#pair-1-cut-connective-padding-in-stages).

### Prefer precise repetition to an awkward substitute

**Difference:** A clause containing “taxonomic ranks”, “taxonomic classifier”, and “taxa” was revised to “identifies them from order to species using a hierarchy-consistent taxonomic classifier trained on Neotropical insect taxa”. This removed the first unnecessary use of the word family while retaining the two informative uses.

**Reason:** “Taxonomic classifier” names the method. “Taxa” names the selected training units, and “insect” states their biological scope. Replacing “insect taxa” with a longer description avoided repetition but lost precision and sounded less natural.

**Limit:** Repeat a scientific term when it carries information or prevents ambiguity. Reduce nearby related forms when one can disappear without losing meaning.

Evidence: [correction pair 2](evidence-ledger.md#pair-2-keep-the-familiar-scientific-noun).

### Replace insider shorthand with the reader's term

**Difference:** “Taxonomic head” became “taxonomic classification model” in a deliverables list.

**Reason:** “Head” describes an internal architectural component for machine-learning readers. “Classification model” tells ecology readers what scientific tool will be delivered and parallels “segmentation model”.

**Limit:** Use “classification head” when the architecture itself matters and the readers know the term.

Evidence: [correction pair 4](evidence-ledger.md#pair-4-replace-compressed-shorthand-with-the-readers-term).

### Match technical detail to the job of the section

**Difference:** A proposal paragraph first expanded the random-effect rationale into site-night grouping, four sampling times, shared deployment, and nightly conditions. The accepted paragraph stated that sampling night is a random effect and left the fuller grouping explanation for a more suitable location.

**Reason:** The expanded explanation was technically relevant but interrupted a paragraph whose immediate job was to state the model structure. The issue was placement and depth, not the value of technical explanation.

**Limit:** Preserve explanations required for accuracy, interpretation, evaluation, or reproducibility. Put full grouping structure and justification in Methods when they affect the analysis. Move necessary detail instead of deleting it.

Evidence: [correction pair 3](evidence-ledger.md#pair-3-stop-when-the-explanation-becomes-the-distraction).

### Make claims earn their adjectives

**Difference:** The user removed “detailed” as praise for a table.

**Reason:** The adjective evaluates the table without telling the reader what it contains. Naming the relevant fields, comparisons, or evidence is more informative when those details matter.

**Limit:** Keep an evaluative adjective when it has a defined technical meaning or when the claim is supported and relevant. The preference concerns unsupported praise, not the word itself.

Evidence: [v4 source note 1](evidence-ledger.md#v4-source-notes).

### Separate manuscript content from development history

**Difference:** Informal experiment labels such as YOLO v3, v5, and v5.1 became the publication name “YOLO26-seg” or the stable description “the current segmentation model”. The phrase “After the July 3 manuscript pass” was removed from manuscript prose.

**Reason:** Internal labels and draft dates record how the work developed. Manuscript readers need the identifiable final model and the current scientific method.

**Limit:** Preserve internal labels in experiment records, audits, and provenance mappings. Preserve change history in responses to reviewers, release notes, and progress reports.

Evidence: [correction pair 5](evidence-ledger.md#pair-5-separate-internal-model-labels-from-manuscript-names).

### Keep established terms for the intended discipline

**Difference:** The user retained “phenology” instead of expanding it into examples of emergence, reproduction, and seasonal activity for ecology readers.

**Reason:** “Phenology” is established ecological vocabulary and is shorter and more precise than the proposed paraphrase. Cross-disciplinary machine-learning or statistical terms may still need a brief explanation of their role in the study.

**Limit:** Calibrate to the intended readers. Keep established ecological terms for ecologists. Explain a cross-disciplinary term when it obstructs the biological argument.

This differs from the internal-model-name correction. “Phenology” is a stable disciplinary term. YOLO v3, v5, and v5.1 were informal experiment labels rather than publication names.

Evidence: [v4 source note 3](evidence-ledger.md#v4-source-notes) and ecology transcript line 10528 at `2026-07-22T04:17:59.530Z`.

## Evidence classes

- **Invariant:** The user has stated the preference directly and intends it to apply broadly. Avoid em dashes and semicolons. Preserve facts and provenance.
- **Default:** Repeated corrections support the choice in most prose. Prefer concrete wording, stable terminology, present-state description, and useful compression.
- **Watch item:** Inspect the effect in context. Examples include staged contrasts, self-praise, slogan-like compounds, and excessive explanation.
- **Context choice:** Let the genre decide. Examples include passive voice, lists, spelling convention, technical detail, and first person.

Keep watch items contextual when the evidence is only one accepted edit. Later explicit feedback supersedes earlier inference.
