---
name: scientific-writing
description: Use when drafting, revising, or polishing academic scientific prose, thesis sections, literature reviews, methods/results/discussion text, abstracts, or reviewer responses.
triggers:
  - scientific writing
  - thesis writing
  - manuscript
  - literature review draft
  - reviewer response
  - academic prose
argument-hint: "<draft text or writing task>"
---

# Scientific Writing

Write like a careful scientist explaining the work clearly. Accuracy comes
before elegance; concision comes before decoration.

When the task is style-sensitive or the user asks to humanize academic
biology/ecology prose, also load `references/humanizer.md`.

## Core Rules

- Preserve technical meaning, caveats, methods, and citations.
- Remove filler, vague praise, and generic AI phrases.
- Keep standard technical terms when they are the precise terms researchers use.
- Explain terms on first use when the intended reader may not know them.
- Avoid overclaiming. Match claims to evidence and citations.
- Prefer manuscript prose over bullet lists unless lists genuinely improve
  methods, comparisons, reviewer responses, or working notes.
- Do not use em dashes in manuscript text.

## Workflow

1. Identify the genre: abstract, introduction, literature review, methods,
   results, discussion, thesis prose, reviewer response, or email.
2. Preserve claims and evidence before changing style.
3. Improve paragraph logic: topic sentence, evidence, limitation or implication.
4. Tighten sentences by removing redundancy, not by deleting reasoning.
5. Run a final academic-humanizer pass if the user asks for naturalness.

## Literature Review Prose

For literature reviews, prioritize:

- clear synthesis over paper-by-paper summaries
- comparison of mechanisms, methods, datasets, and limitations
- explicit transitions that explain why the next source matters
- citations attached to specific claims

Avoid saying a field is "rapidly evolving" or "increasingly important" unless
the paragraph gives concrete evidence.

## Ecology / Biology Preferences

Preserve precise terms such as occurrence records, coordinate uncertainty,
spatial thinning, presence-only data, background points, accessible area,
target-group background, habitat suitability, species distribution modelling,
taxonomic curation, data source, and data provenance.

When writing about species distribution models, describe outputs as relative
habitat suitability unless true occurrence probabilities were estimated.

## Final Check

Before returning revised academic text, check:

- no em dashes
- no generic AI phrases
- no unnecessary filler
- technical terms preserved or defined
- claims are specific and defensible
- caveats remain where they prevent overclaiming
- citations are not invented
