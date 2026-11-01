# Changelog

## v2

Built from the user's bracketed comments on several versions of a report, checked against the chat that created v1.

The report and the manuscript chats describe unpublished work. In this public copy every example sentence is invented and every comment is paraphrased. The rules and their evidence strength are the same as in the private version.

### Added

- `references/comment-ledger.md`: rules R1–R25 with evidence strength, before and after pairs, a pushback record, and the content questions the user asks.
- `references/critic-loop.md`: two independent critics for substantial writing (GPT-6.1 Sol at medium reasoning and Claude Opus 5.5, chosen by the user and changed only by the user), plus an author-comment emulation mode.
- Evidence strength marks: A explicit and repeated, B explicit once, C inferred.
- A bracketed-comment workflow in `references/review-workflow.md`, the way the user actually reviewed the report, with a check that every comment has a decision.
- Results reporting, expectations, figures and citations sections in `references/scientific-writing.md`.
- A first section of report-specific tells in `references/anti-slop-audit.md`.

### Fixed v1 errors

Each item contradicts the user's later explicit feedback or was never asked for.

1. **Caveats and provenance preserved by default.** v1 listed "preserve every caveat" and "preserve facts and provenance" as invariants. The user cut defensive hedges and provenance notes repeatedly. v2 keeps caveats that change how a result is used and keeps provenance in records rather than reader-facing text.
2. **Personality the user never asked for.** v1 told writers to preserve "irritation and warmth", a list taken from a community humanizer rather than from the user. Trimmed to judgments, emphasis and real uncertainty.
3. **"Useful next steps" as a writing default.** The user's request was for affirmative guidance in instructions, not for next-step prose. In the report, the user removed a "Next steps" section and a promised improved model, while asking for planned work the author had decided. v2 scopes affirmative guidance to instructions and agent replies, and R20 covers plans.
4. **Gendered pronoun.** The v1 evidence ledger used a gendered pronoun for the user. Replaced with "the user".
5. **Semicolons between citations.** v1 banned all semicolons, while grouped citations need them (pandoc `[@a; @b]`). Prose semicolons stay out, citation separators are allowed.
6. **Examples.** The v1 examples are replaced with invented ones that show the same corrections.

### Calibrated v1 rules

These v1 rules were sound but too thin, and the report comments add the missing side.

1. **Development history.** v1 allowed history in progress reports. The report comments cut meta, deferral and obvious sentences rather than history as such. v2 adds R1, R2 and R21 and keeps history for changelogs, release notes, experiment records and responses to reviewers.
2. **Brevity.** v1's "prefer the shortest wording … but let accuracy set the limit" stays as R25. The comments add a counterweight, R8: keep the small words a person would keep, only where the sentence otherwise sounds compressed.
3. **Definitions.** v1 already limited explanation to terms unfamiliar to the reader. It had no example of over-defining for a committee. R12 adds one.
4. **Reminders.** v1 said to omit reminders to earlier sections when the connection is clear. v2 adds the other case: restate an earlier detail in a few words when the reader needs it (R11), and avoid bare pointers such as "the survey of step 3" (R1).
5. **Review workflow.** v1 described only paragraph-by-paragraph review. v2 adds the whole-document bracketed-comment workflow.

### Kept

The correction pairs from the manuscript chats (`references/evidence-ledger.md`, now with invented sentences), the em dash and semicolon preferences, the factual safeguards, the trigger description and `agents/openai.yaml`.

### Naming

The user asked that their name not appear in the skill, so the new ledger is `comment-ledger.md` and the emulation mode is "author-comment emulation".

### Open

- The blind test (three report paragraphs) used generous placeholders where facts were missing. That follows the flag-don't-invent rule but adds noise and can undercut a confident tone (R3).
