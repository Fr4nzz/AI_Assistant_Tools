---
name: literature-search
description: Use when the user asks to find papers for a literature review, compare search methods, discover academic sources by topic, or build an initial reading set before downloading PDFs.
triggers:
  - literature review
  - find papers
  - search papers
  - paper discovery
  - academic sources
  - research topic
argument-hint: "<research question or topic>"
metadata:
  optional_bins: ["paper-search", "parallel-cli"]
---

# Literature Search

Use this skill for initial paper discovery. It coordinates several search
routes, then uses `paper-fetch` / `paper-search metadata-dois` only after
candidate papers or DOIs are identified.

## Default Discovery Pattern

For an important literature-review seed search, run these in parallel when
available:

1. Native Codex/web search: best for current web coverage, disambiguation, and
   source inspection.
2. Parallel search (`parallel-cli search`): useful second opinion and broader
   web retrieval when the user has configured Parallel.
3. Paper-search topic search (`paper-search search`): slower and less reliable
   as a primary search, but useful as a supplemental academic-index pass. Start
   it in the background first when doing a three-engine comparison.
4. Exa search, if installed/configured: optional comparison source. Do not run
   it by default for every literature search because it consumes paid credits
   and early benchmarks showed high overlap with native/Parallel results for
   academic paper discovery. Use it when the user asks to compare engines, when
   native/Parallel results are weak, or when searching for code/package docs.

If time, accounts, or paid credits are limited, use native search first and add
Parallel or paper-search only when the topic is broad, high stakes, or the user
explicitly wants a more exhaustive search. Treat Exa as opt-in unless the user
has asked for a benchmark or a broader search-engine comparison.

## Query Strategy

Break the research question into 3-5 complementary prompts:

- core concept query
- method or model query
- review/meta-analysis query
- recent-years query
- domain-specific synonym query

Run the same prompt set across the available engines when benchmarking engines.
For normal work, adapt prompts per engine after the first pass.

## Consolidation

Create a candidate table with:

- title
- DOI or stable URL
- year
- venue
- why it matters
- source engine(s) that found it
- whether full text seems available

Deduplicate by DOI first, then normalized title.

## Metadata And Ranking

When there are multiple DOI candidates, call:

```bash
paper-search metadata-dois --input dois.txt --output metadata.json
```

Use the metadata to triage, not as a final judgement. The ranking is a
deterministic helper based on literature fit, recency, citation signal,
metadata confidence, and open PDF availability across checked OA sources
(`oa_pdf_sources`). It is not query-aware semantic relevance.

## Reporting

Report:

- which engines were used or skipped and why
- elapsed time when benchmarking
- overlapping papers across engines
- unique high-quality papers found by each engine
- recommended next reading set

Avoid claiming a paper is central only because it ranked high mechanically.
Open and inspect abstracts or key sections before making strong claims.
