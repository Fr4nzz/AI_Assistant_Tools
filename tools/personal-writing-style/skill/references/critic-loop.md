# Independent critics

A writer cannot see their own blind spots, and a model that drafted a text shares the assumptions that produced it. For substantial writing (a thesis chapter, a report, a paper, a long email that matters), get two independent reviews before the text goes to the user or out of the door.

## Which critics

Critics: GPT-6.1 Sol (reasoning medium) and Claude Opus 5.5. The user chose them as the best intelligence per price. Only the user changes this choice. Never move to a newer or more expensive model on your own (for example Claude Fable or GPT-6.1 Astra). If a new model looks better, suggest it to the user.

The pair is one critic from another vendor and one fresh model from the writer's family. The cross-vendor critic catches what the writer's family tends to miss. The fresh critic shares none of the writer's context. If one critic is unavailable, continue with the other and say so. Silence is not approval.

## How to run them

Start both critics in parallel with the same brief. If a `dual-critic-loop` skill is installed, follow its mechanics (brief, severities, merging, the two-round budget and the stop rule) rather than a copy here. Otherwise ask each critic for findings graded blocker, should or nit, merge the two lists, and stop after two rounds. Add to the brief:

- the intended reader and the purpose of the document
- the path to this skill's [comment-ledger.md](comment-ledger.md), with the instruction to check the text against its rules
- earlier decisions the user made on the same document, so critics do not reopen them
- when the text answers the user's comments, the comment list and the decision table, with the instruction to mark each comment ok, partial or missing.

Then fix each blocker and should with the smallest change, or push back with evidence, and re-check. The user's own comments outrank critic suggestions on scope and tone: when a critic asks to restore something the user removed, decline and cite the user's comment.

## Author-comment emulation

This mode predicts how the user would comment on a draft, so a writer can fix the obvious points before the user spends time on them. Run it as a fresh Claude Opus 5.5 agent, or do it yourself for a quick pass.

The reviewer reads [comment-ledger.md](comment-ledger.md) first, especially the rules, the pushback record and the list of content questions. Then it writes comments in square brackets inline, right after the words they concern, the way the user writes them:

- in the first person and informal, often as a question, with the reason given ("I think a human would have avoided …", "isn't this obvious?")
- on style: meta sentences, obvious sentences, hedges, blame, hindsight predictions, compressed or unclear wording, drifting names, ratios below 1, p values without their comparisons
- on content, which the user raises as often as style: "how do you know this?", a missing breakdown ("could we give this for the largest group too?"), an unfair comparison ("shouldn't the old version get the same test data?"), an untested explanation ("could something else explain this?"), a figure that would show it better
- on field facts the writer could not know (distances, dates, site descriptions): flag them for the user to check rather than correcting them
- marking questions meant only for the author: "[just for me, not for this document: …]".

The emulated comments are a prediction, not the user's judgement. Label them as emulated, keep them separate from the user's real comments, and never record them in the ledger as evidence.

Example, on an invented sentence:

> The new pipeline is robust [robust how? which check did we run?], and the old labels were poor because the previous team labelled them in a hurry [I wouldn't say this, it blames the previous team, can we just say which labels we corrected?].
