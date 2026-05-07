---
name: literature-review
description: Use when the user needs to read, screen, summarize, synthesize, or write from a set of academic papers after initial literature search has found candidate sources.
triggers:
  - literature review
  - read papers
  - synthesize papers
  - summarize papers
  - research synthesis
  - review matrix
argument-hint: "<research question plus paper list or folder>"
metadata:
  optional_skills: ["literature-search", "paper-fetch", "literature-appraisal", "scientific-writing", "citation-zotero"]
---

# Literature Review

Use this skill after `literature-search` has produced a candidate reading set.
Its job is to turn many papers into traceable notes, a synthesis matrix, and
source-grounded review prose.

This skill adapts the useful parts of K-Dense `literature-review`, but keeps it
lean for Codex: no mandatory figures, no mandatory paid tools, and no enormous
raw search dumps.

## When To Use

Use for:

- reading many papers after initial discovery
- screening abstracts and full texts
- extracting evidence for a thesis or manuscript section
- building a synthesis matrix
- writing a literature review from paper notes
- tracking citation roles and limitations

Use `literature-search` first when the paper set does not exist yet.
Use `scientific-writing` only for the final prose/style pass.

## Review Pipeline

Before doing substantial work, create and maintain a visible todo list for the
pipeline. Update it as phases complete. Do not jump from discovery directly to
final prose when papers still need screening, summary, appraisal, or synthesis.

Minimum todo list:

1. Define review question and scope.
2. Confirm or run initial literature search.
3. Screen and deduplicate candidate papers.
4. Retrieve PDFs or abstracts for the shortlist.
5. Cluster papers by theme/method/debate.
6. Delegate or perform paper reading.
7. Write paper summaries and topic extracts.
8. Build synthesis matrix.
9. Appraise evidence strength and limitations.
10. Draft outline.
11. Draft prose from synthesis.
12. Apply `scientific-writing` final style pass.
13. Check citations and unresolved claims.

1. Define the review question, scope, inclusion/exclusion criteria, and expected
   output before reading deeply.
2. Organize papers into clusters by theme, method, taxon/system, geography,
   data type, or debate.
3. Use parallel subagents when available. Prefer one agent per coherent cluster;
   use one agent per paper only for dense, central, or difficult papers.
4. Ask each reading agent to create two markdown artifacts per paper or cluster:
   - `paper-summary-<slug>.md`
   - `topic-extract-<slug>.md`
5. Build a synthesis matrix from the topic extracts.
6. Use `literature-appraisal` to classify keep/maybe/drop and evidence strength.
7. Draft from the synthesis matrix, not from the order papers were read.
8. Use `scientific-writing` for the final writing-style pass.
9. Use `citation-zotero` when citation keys, Zotero, BibTeX/CSL, or `.docx`
   workflows are needed.

## Parallel Reading With Subagents

If the Superpowers plugin or subagent tools are available, delegate reading.
The main agent should keep ownership of:

- the review question
- the synthesis matrix
- the final argument structure
- citation correctness
- the final written voice

Reading agents should distill evidence, not write the final review.

### Reading-Agent Brief

Give each agent:

- the review question
- the assigned paper(s) or theme cluster
- why this cluster may matter
- what counts as relevant evidence
- expected output filenames
- instruction to separate findings, interpretation, and limitations
- instruction not to overclaim beyond the paper

Ask agents to mark confidence:

- `solid`: directly supported by methods/results
- `suggestive`: plausible but indirect
- `unclear`: needs checking in full text or supplementary material
- `not relevant`: checked but not useful for this review question

## Artifact Templates

### `paper-summary-<slug>.md`

```markdown
# Paper Summary: <short citation>

- DOI / URL:
- Full citation:
- Study type:
- Research question:
- Methods and data:
- Key findings:
- Important limitations:
- Author-stated caveats:
- Useful details for citation:
- Citation role: background / method / evidence / contrast / limitation
- Confidence notes:
```

### `topic-extract-<slug>.md`

```markdown
# Topic Extract: <short citation>

## Relevance To Review Question

## Claims Supported By This Paper

| Claim | Evidence | Strength | Caveat | Citation |
|---|---|---|---|---|

## Methods Or Assumptions Worth Comparing

## Limitations Useful For The Review

## Do Not Use This Paper For
```

## Synthesis Matrix

After reading, create a matrix like:

```markdown
| Paper | Theme | Method/Data | Main Contribution | Evidence Strength | Key Limitation | Citation Role |
|---|---|---|---|---|---|---|
```

Use the matrix to group the review by ideas, not by papers.

## Visual Synthesis

Figures are optional, not mandatory. Propose one when it would clarify the
review or help the reader remember the structure.

Useful figure types:

- PRISMA-style flow diagram for systematic or scoping reviews
- search/screening flowchart
- thematic synthesis map
- conceptual framework diagram
- method comparison diagram
- evidence-gap map
- causal/mechanistic diagram for ecological or biological processes

Before generating a figure, state what question the figure answers and what
data or concepts it will contain. Prefer simple diagrams over decorative
graphics. Do not generate figures merely to satisfy a quota.

## Writing From The Matrix

Strong literature-review paragraphs usually do one job:

- introduce a problem or tension
- group papers that support a shared claim
- contrast methods or assumptions
- explain why evidence differs across studies
- identify a gap or limitation
- transition from background to the user's research question

Use citations for specific claims. Avoid paper-by-paper summaries unless the
history or chronology matters.

Before final prose, load `scientific-writing` for style and clarity.
