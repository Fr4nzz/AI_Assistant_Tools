# Literature Review

Installs a Codex skill for the post-search stage of research: screening papers,
delegating full-text reading, creating markdown summaries, building a synthesis
matrix, and drafting source-grounded literature-review prose.

The skill requires a visible todo/checklist so the agent covers the pipeline
from research question, search, screening, summaries, and synthesis through
final writing. It also includes optional visual synthesis guidance for PRISMA
flows, conceptual maps, method diagrams, and evidence-gap figures.

It also supports an existing-draft audit mode for literature reviews or
deep-research reports from ChatGPT, Gemini, Claude, or similar systems. In that
mode the agent extracts claim-citation tables, verifies claims against cited
papers, checks reference formatting, searches for missing relevant work, and
triages additions/removals under word limits.

This skill is intentionally separate from `scientific-writing`. Use
`literature-review` for reading and synthesis; use `scientific-writing` for the
final style and prose pass.

It adapts ideas from K-Dense `scientific-agent-skills/literature-review` while
keeping the workflow smaller and Codex-friendly.
