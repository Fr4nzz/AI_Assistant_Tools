---
name: academic-research
description: Use when the user asks for academic paper discovery, literature reviews, research synthesis, paper appraisal, citation workflows, Zotero/docx bibliography work, scientific writing, or citation/audit checks for drafts and deep-research reports.
triggers:
  - literature review
  - find papers
  - search papers
  - academic sources
  - research synthesis
  - read papers
  - summarize papers
  - review matrix
  - verify citations
  - deep research
  - draft audit
  - zotero
  - citation
  - bibliography
  - scientific writing
  - manuscript
  - thesis writing
  - reviewer response
  - appraise literature
  - evidence strength
argument-hint: "<research question, paper list, draft, DOI list, or writing task>"
metadata:
  optional_bins: ["paper-search", "parallel-cli", "pandoc"]
  optional_skills: ["paper-fetch"]
---

# Academic Research

Use this skill as the unified workflow for academic research tasks. It merges
literature discovery, multi-paper reading, appraisal, Zotero/citation planning,
and scientific writing into one skill so the agent follows a single pipeline.

Use `paper-fetch` / `paper-search` as the operational tool for known DOI
metadata and PDF retrieval. Do not use paper-search as the only discovery
route unless the user asks for a quick single-tool search.

## Tool Authentication

Some optional tools listed in `optional_bins` require setup before first use.

- **parallel-cli**: Requires login. Choose the flow that matches your environment:
  - **Desktop / local GUI**: run `parallel-cli login` (opens browser automatically).
  - **Headless / SSH / remote server / Hermes Agent**: run `parallel-cli login --device`, then complete authentication on another device by visiting the printed URL and entering the code.

## Default Workflow

Before substantial work, create and maintain a visible todo list. Update it as
phases complete. Do not jump from search directly to final prose when papers
still need screening, summary, appraisal, or synthesis.

Minimum todo list:

1. Define review question, scope, audience, output, and word limit.
2. Identify source material: draft, bibliography, deep-research reports,
   paper list, PDFs, notes, and required citation style.
3. Run or update literature search.
4. Screen and deduplicate candidate papers.
5. Retrieve PDFs or abstracts for the shortlist.
6. Enrich DOI metadata when useful.
7. Cluster papers by theme, method, debate, taxon/system, geography, or data.
8. Delegate or perform paper reading.
9. Write paper summaries and topic extracts.
10. Build a synthesis matrix.
11. Appraise evidence strength, limitations, and citation value.
12. Verify important claims and references.
13. Decide what to add, cut, merge, or reframe under any word limit.
14. Draft outline or revision plan.
15. Draft prose from the synthesis.
16. Apply the scientific writing style pass.
17. Check citations and unresolved claims.

## Literature Discovery

For an important literature-review seed search, run these in parallel when
available:

1. Native web/search tools: best for current web coverage, disambiguation, and
   source inspection.
2. Parallel search (`parallel-cli search`): useful second opinion and broader
   web retrieval when the user has configured Parallel.
3. Paper-search topic search (`paper-search search`): slower and less reliable
   as a primary search, but useful as a supplemental academic-index pass. Start
   it in the background first when doing a three-engine comparison.

If time, accounts, or paid credits are limited, use native search first and add
Parallel or paper-search only when the topic is broad, high stakes, or the user
explicitly wants a more exhaustive search.

Break the research question into 3-5 complementary prompts:

- core concept query
- method or model query
- review/meta-analysis query
- recent-years query
- domain-specific synonym query

Create a candidate table with title, DOI or stable URL, year, venue, why it
matters, source engine(s), and full-text availability. Deduplicate by DOI first,
then normalized title.

When there are multiple DOI candidates, call:

```bash
paper-search metadata-dois --input dois.txt --output metadata.json
```

Use metadata ranking as triage only. Citation counts, recency, or PDF
availability are not proof of relevance or quality.

## Multi-Paper Reading

Do not read many papers one by one in the main agent if subagents are
available. Use one subagent per coherent cluster; use one subagent per paper only for
dense, central, or difficult papers.

The main agent owns the review question, synthesis matrix, final argument,
citation correctness, and final written voice. Reading agents distill evidence;
they do not write the final review.

Ask each reading agent to create two markdown artifacts per paper or cluster:

- `paper-summary-<slug>.md`
- `topic-extract-<slug>.md`

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

### Paper Summary Template

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

### Topic Extract Template

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

After reading, build a synthesis matrix:

```markdown
| Paper | Theme | Method/Data | Main Contribution | Evidence Strength | Key Limitation | Citation Role |
|---|---|---|---|---|---|---|
```

Use the matrix to group the review by ideas, not by papers.

## Existing Draft / Deep-Research Audit

Use this mode when the user already has a literature-review draft, notes, or
deep-research reports from ChatGPT, Gemini, Claude, Perplexity, or similar
systems.

Do not assume those reports are correct. They may have used only abstracts,
mixed ideas between papers, invented details, cited the right paper for the
wrong claim, or missed recent/relevant work.

Audit steps:

1. Extract a claim-citation table from the draft/report.
2. Prioritize claims that are central, surprising, quantitative,
   controversial, or repeated in the argument.
3. Check the cited source's abstract and, when needed, methods/results/
   discussion using `paper-fetch` or available PDFs.
4. Mark each claim as `supported`, `partly supported`, `unsupported`,
   `wrong source`, `needs full text`, or `citation missing`.
5. Check whether the draft mixed findings from one paper while citing another.
6. Check that references are real, complete, non-duplicated, and formatted in
   the requested style.
7. Run a fresh targeted literature search to find missing papers, newer
   reviews, stronger evidence, or contrary findings.
8. Produce an editorial triage table: keep, revise wording, replace citation,
   add source, remove claim, or add caveat.

Claim-citation audit table:

```markdown
| Draft claim | Current citation | Verification status | What the source actually supports | Fix |
|---|---|---|---|---|
```

Reference checks should cover author spellings, year, title, journal/source,
volume/issue/pages/article number, DOI/URL, APA or requested style consistency,
whether in-text citations match the reference list, and whether every
reference is cited.

## Appraisal

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

For each paper, report keep/maybe/drop, reason in one sentence, evidence
strength, main limitation, whether to read abstract only, skim, or read fully,
and citation role if used.

## Word-Limit Triage

If the user has a word limit, do not just append new findings. Weigh each idea
against the review question.

Prioritize content that directly answers the question, changes interpretation,
strengthens a weak claim, adds an important caveat, updates outdated evidence,
or resolves a contradiction.

Cut or compress content that repeats a point, is unnecessary background, cites
weak evidence where stronger evidence is available, is peripheral, or
over-explains a method already familiar to the target audience.

Use this compact tradeoff table:

```markdown
| Change | Add/cut/compress | Reason | Word impact |
|---|---|---|---|
```

## Citation And Zotero Workflows

Do not promise fully automatic live Zotero fields in arbitrary Word or Google
Docs files. Prepare reliable citation workflows first; use active-citation
conversion only through verified Zotero integrations.

Capability levels:

1. Safe library work: pyzotero/Zotero API can create, update, search, tag, and
   export Zotero items.
2. Citation placeholders: insert Pandoc-style keys such as `[@smith2020]` only
   after validating the key against Zotero, Better BibTeX, or an exported
   bibliography.
3. Static document citations: Pandoc can generate `.docx` files with formatted
   citations and bibliographies from Markdown plus CSL/BibTeX/CSL JSON.
4. User-finalized active citations: ODF/DOCX Scan for Zotero can convert
   markers into active Zotero citations when the user has Zotero, the relevant
   word-processor plugin, and the scan plugin installed.
5. Google Docs live Zotero citations: no stable public Google Docs API path is
   assumed. Prepare sources/markers and let Zotero Connector handle final
   insertion unless the user explicitly approves UI automation.

Before editing a `.docx`, inspect the document and ask what output is desired:
live Zotero fields, static formatted citations and bibliography, or
comments/placeholders for manual Zotero insertion.

Never invent a citation for a claim; add a TODO or comment when the source is
missing.

## Scientific Writing

Write like a careful scientist explaining the work clearly. Accuracy comes
before elegance; concision comes before decoration.

When the task is style-sensitive or the user asks to humanize academic
biology/ecology prose, also load `references/humanizer.md`.

Core rules:

- Preserve technical meaning, caveats, methods, and citations.
- Remove filler, vague praise, and generic AI phrases.
- Keep standard technical terms when they are the precise terms researchers use.
- Explain terms on first use when the intended reader may not know them.
- Avoid overclaiming. Match claims to evidence and citations.
- Prefer manuscript prose over bullet lists unless lists genuinely improve
  methods, comparisons, reviewer responses, or working notes.
- Do not use em dashes in manuscript text.

For literature reviews, prioritize clear synthesis over paper-by-paper
summaries, comparison of mechanisms/methods/datasets/limitations, explicit
transitions, and citations attached to specific claims.

Preserve precise biology/ecology terms such as occurrence records, coordinate
uncertainty, spatial thinning, presence-only data, background points,
accessible area, target-group background, habitat suitability, species
distribution modelling, taxonomic curation, data source, and data provenance.

Before returning revised academic text, check that there are no em dashes, no
generic AI phrases, no unnecessary filler, preserved or defined technical
terms, defensible claims, necessary caveats, and no invented citations.

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
