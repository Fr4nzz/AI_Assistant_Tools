# Voice grounded in corrections

Use this evidence as calibration, not as a phrase bank. The user's direct comments outrank these summaries. Two bodies of evidence exist:

- **Manuscript and thesis proposal chats.** A few correction sequences, kept with full sentences in [evidence-ledger.md](evidence-ledger.md).
- **A progress report.** 160 bracketed comments on five of nine versions, distilled in [comment-ledger.md](comment-ledger.md) as rules R1–R25 with before and after pairs.

The examples in this public copy are invented and make the same point as the originals. Strength marks: **A** explicit and repeated, **B** explicit once, **C** inferred.

## The governing preference

The user reads a draft by asking two questions of each phrase: what does it mean, and would a person have written it? The preferred prose is precise without sounding polished for its own sake, and confident without overstating. It keeps scientific distinctions, useful repetition and the caveats that change a conclusion. It cuts connective padding, sentences about the text, defensive hedging, self-praise, insider shorthand and explanations that outgrow their purpose.

Two pressures pull against each other, and both are real. The user cuts words that add nothing ("directly", "in terms of", "records sound by itself"), and the user restores small words that a person would keep ("the least", "in the future", "at a higher altitude"). The deciding question is whether the reader loses anything or whether the sentence starts to sound machine-compressed.

## Calibrate from current writing

When the user provides a recent writing sample, treat it as the best guide to the voice for that task. Notice sentence length, word choice, paragraph openings, transitions and use of the first person. Reproduce the pattern rather than memorable phrases. Direct feedback on the current task outranks habits inferred from an older sample.

## Patterns from the progress report

Each pattern gives the difference, the reason and the limit. The full pairs are in the comment ledger.

### Sound sure of what the evidence shows (A, R3 and R4)

**Difference:** "According to the field protocol, each transect is walked …" became "Each transect is walked …". "Pending confirmation" and "this analysis is exploratory" were cut. A sentence saying the site lacks its own weather station was cut, and so were hypotheses that implied the team did not know its own protocol.

**Reason:** The report went to a funding panel and a thesis committee. Defensive qualifiers make settled work sound unsure, and some caveats read as blame on the people who ran the survey.

**Limit:** Keep a caveat that changes how a reader should use a number: few survey days behind a test, a multiple-test correction, an unvalidated name. Report an unexplained result as unexplained. The point is tone and scope, not hiding evidence.

### Expectations written before the results (A, R5 and R6)

**Difference:** "about three times as many per square metre" was removed from a prediction, and "as expected" after a gain of 9 percentage points was cut. Expectations moved from "was expected" to "We expect".

**Reason:** The author expected an increase but never predicted its size. A prediction that matches the measurement makes readers suspect it was written afterwards, which is what an AI does when it has read the results first.

**Limit:** A prediction that was made in advance, with a size, can say so.

### Natural words over compressed ones (A, R8 and R9)

**Difference:** "disturbs the flowers least" became "disturbs the flowers the least", "higher" became "at a higher altitude", "photographs" became "photos", "attraction" became "competition from the neighbouring garden's flowers".

**Reason:** These are the words a person uses. The user called the small words "spices of my writing style" and said "I prefer being a bit more explicit sometimes".

**Limit:** The user added "just for these cases". Do not pad other sentences. Cut a repetition that adds nothing, such as saying that an automatic recorder records "by itself".

### One name, defined once, meaning what the reader means (A, R10 to R12)

**Difference:** "the transects" and "the cameras" were defined once as the two survey types and used consistently. A shortened place name was written out in full every time. "Both transects" became "both sites". "The tool of step 3" was cut, while a reminder of what the row of beehives was stayed.

**Reason:** A reader who does not know the field setup cannot map shortened or equipment-based labels to places and methods. A short restatement helps, a pointer to a section only adds text.

**Limit:** Define a term only if the intended reader may not know it. Defining overdispersion for a committee treats the audience as if it did not know the field, while a one-line meaning of a confidence interval "sounds appropriate".

### Numbers a reader can read at once (A, R15 to R17)

**Difference:** "0.70 times" became "1.43 times" with the groups swapped. "The intervals include 1" became "not significant (p = 0.21 for the upper against the lower meadow on morning walks, and p = 0.34 for the same comparison on afternoon walks)". Medians were added beside ratios, and "after correcting for the number of tests" became the named correction.

**Reason:** Ratios above 1 are easier to read, named tests are honest, and a p value without its comparison makes the reader guess.

**Limit:** The user asked to drop an unfamiliar correction method, but the correction stayed. The user then asked which correction it was, asked for its name, and asked for it to be explained in the chat. Name the method, and give the author the explanation in the reply, not in the document.

## Patterns from the manuscript chats

### Cut wording that adds no relationship (A)

**Difference:** "compared directly in terms of" became "compared for".

**Reason:** "Compared" already states the comparison, and the outcomes can follow "for" directly.

**Limit:** Keep an adverb or linking phrase when it changes the method, direction, scope or interpretation.

### Preserve a distinction while naming it plainly (B)

**Difference:** "Family-level richness" became "number of families", while "community composition" stayed a separate outcome.

**Reason:** The plainer label reads faster without merging two measurements.

**Limit:** Keep the formal term when it identifies a metric precisely.

### Precise repetition over an awkward substitute (B)

**Difference:** A clause with "taxonomic ranks", "taxonomic classifier" and "taxa" became "identifies them from family to species using a taxonomic classifier trained on plant taxa recorded in local seedling plots".

**Reason:** The first repetition added nothing. "Taxa" names the selected units and "plant" states their scope, so both stayed.

**Limit:** Reduce nearby related forms when one can go without loss. Keep the noun that carries information.

### The reader's term over insider shorthand (B)

**Difference:** "Taxonomic head" became "taxonomic classification model" in a deliverables list.

**Reason:** "Head" is an architecture term. An ecology reader needs to know what tool is delivered.

**Limit:** Use "classification head" where the architecture matters and the readers know the term.

### Detail where it does its job (B)

**Difference:** A proposal paragraph that expanded a random-effect rationale into walk times, the plot visit and the weather was cut back to "survey day is a random effect".

**Reason:** The paragraph's job was to state the model. The rationale belongs in Methods.

**Limit:** Move necessary detail rather than delete it. Accuracy, interpretation and reproducibility set the floor.

### Claims earn their adjectives (B)

**Difference:** The user removed "detailed" as praise for a table.

**Reason:** The adjective grades the table without saying what it contains.

**Limit:** Keep an evaluative word with a defined technical meaning or a supported claim.

### The finished work, not its history (A)

**Difference:** Internal version labels for successive training attempts became the publication name or "the current segmentation model". A dated phrase about an earlier manuscript pass was removed. In the progress report, "Because no hand-drawn outlines existed" became a plain statement of how the outlines were made.

**Reason:** Readers need the final method, not the drafting or experiment sequence.

**Limit:** Keep internal labels in experiment records, audit trails and changelogs, and keep change history in responses to reviewers and release notes.

### Established terms for the discipline (B)

**Difference:** The user kept "phenology" rather than a paraphrase.

**Reason:** It is the shorter and more precise ecological term.

**Limit:** Explain a term from another discipline when it would block an ecology reader.

## Evidence classes

- **Invariant:** stated directly and meant broadly. Avoid em dashes and prose semicolons. Preserve facts and their strength.
- **Default (A):** repeated explicit comments. Most of R1–R25 and the padding and history rules from the manuscript chats.
- **Single comment (B):** apply where the same reason holds.
- **Inferred (C):** reading questions as requests, first person plural in English reports. Check against the user's next comments.

Later explicit feedback supersedes earlier inference.
