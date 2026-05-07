---
name: literature-appraisal
description: Use when evaluating papers, deciding which papers to read or cite, assessing evidence strength, critiquing methods, or comparing studies for a literature review.
triggers:
  - evaluate papers
  - appraise literature
  - critical thinking
  - paper quality
  - evidence strength
  - should I cite
argument-hint: "<paper, DOI list, or appraisal question>"
---

# Literature Appraisal

Use this skill after candidate papers have been found. It helps decide which
papers deserve close reading, citation, or exclusion.

## Appraisal Dimensions

Assess each paper on:

- relevance to the user's research question
- study type: empirical, review, method, dataset, opinion, preprint
- data quality and sample size
- methodological fit and assumptions
- statistical/model validation
- causal strength versus association
- reproducibility: code, data, protocol, preregistration when relevant
- citation context: foundational, recent, controversial, or niche
- limitations and likely biases
- full-text availability

## Ranking Policy

Use automated metadata ranking only as a triage signal. Do not treat citation
counts, recency, or PDF availability as proof of relevance or quality.

For important claims, inspect the abstract, methods, results, and limitations.
When possible, compare at least one review paper, one recent empirical paper,
and one methods paper.

## Output Format

For each paper, report:

- keep / maybe / drop
- reason in one sentence
- evidence strength
- main limitation
- whether to read abstract only, skim, or read fully
- citation role if used

When evidence is uncertain, say what would need to be checked next.
