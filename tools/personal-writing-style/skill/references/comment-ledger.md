# Comment ledger

The user left 160 bracketed comments on five of the nine versions of a bilingual (Spanish and English) progress report. This file distils the style comments into rules, gives before and after pairs, and records where a writer pushed back. Use it to calibrate a draft, to check a revision, or to write comments the way the user would (see [critic-loop.md](critic-loop.md)).

The original report contains unpublished work, so this public copy paraphrases the comments and replaces every example with an invented one that makes the same point. The sentences, numbers, places and tools below are fictional. The rules, their strength and the number of comments behind each are unchanged.

## Evidence strength

- **A, explicit and repeated:** two or more comments in the same direction, or a comment the user repeated after a writer ignored it.
- **B, explicit once:** one direct comment with a clear reason.
- **C, inferred:** a pattern in how comments were resolved, never stated as a rule.

When a rule conflicts with a later comment, the later comment wins. A rule here is a default for this user's reports, theses and similar documents. The user said of one correction that it applied "just for these cases I am mentioning, we don't have to worsen writing style in other cases". Apply a rule where its reason applies.

## How the user judges a sentence

The user's recurring test is whether a human author would write the sentence. The comments say so directly: "I think a human would have avoided adding the words …", "humans tend to write so in the future", "that is how a human would write", "easier for humans to interpret". Two comments call a sentence "AI slop". One explains the mechanism: the AI read the results before writing, so it predicted what was later measured.

The comments are short questions more often than orders: "what do you mean by …", "isn't this obvious?", "shouldn't we …". In 160 comments almost every question was a request to change the text. A few are marked as questions for the user alone ("just for me, not for this document", "explain this to me in the chat response"). Those are answered in the reply and leave the document unchanged.

## Rules

| Rule | Strength | Comments |
|---|---|---|
| R1. Cut sentences about the document itself: what a section will do, where a method is explained, where a photo came from. | A | 4 |
| R2. Cut sentences that state the obvious or the expected. | A | 5 |
| R3. State settled facts plainly. Drop defensive hedges and appeals to a protocol or to confirmation still pending. | A | 4 |
| R4. No wording that blames the people running the work or makes the team, the site or partners look bad. | A | 3 |
| R5. Expectations are what the author expected before the results. No numbers taken from the results, no "as expected" after a result the author never predicted in size. | A | 3 |
| R6. State expectations in the present: "We expect", Spanish "Se espera que". | B | 1 |
| R7. In Spanish, avoid making the document the actor ("Este informe analiza … Propone"). The impersonal "se" is the writer's fix that the user accepted (C). | B | 1 |
| R8. Keep the small words a person would keep, and be slightly explicit when it reads more naturally. Only where the sentence otherwise sounds compressed ("just for these cases"). | A | 5 |
| R9. Use the everyday word every reader knows, and avoid words that collide with labels in the document. | A | 6 |
| R10. Give each thing one name, define it once, and name it by what the reader means (the site, not the equipment). | A | 7 |
| R11. When a sentence depends on an earlier detail, restate the detail in a few words instead of pointing to a section. | B | 1 |
| R12. Define only what the intended reader may not know. Defining a familiar term talks down to the reader. | A | 4 |
| R13. Every phrase needs one obvious meaning. Replace vague or internal wording with the specific thing. | A | 6 |
| R14. Drop qualifiers that imply a contrast the author did not mean. | A | 3 |
| R15. Give concrete numbers and simple counts rather than abstract descriptions or ratios alone. | A | 2 |
| R16. Write ratios above 1 by choosing the reference group, and make the words match the number. | A | 6 |
| R17. Statistics: name the test, say "not significant" with the p value, tie each p value to its comparison, and explain an unfamiliar method to the author in the reply. | A | 7 |
| R18. Give the reason for a design step when the reader would wonder why. | A | 5 |
| R19. Leave out tangents this reader does not need, even true ones. | A | 4 |
| R20. Claim only plans, numbers and actions the author has endorsed. Plans the author has made are welcome ("what is still missing"). | A | 5 |
| R21. Do not defer material to another document ("left for the thesis"). Say why it is not reported here. | B | 1 |
| R22. Cite every factual claim, cite once at the end of the sentence, and use the plain citation form. | A | 5 |
| R23. For a summary of findings, bullets rather than a table. Subfigure labels a) and b). When the user dislikes a heading style, offer options. | B | 3 |
| R24. Show with a figure what the text struggles to explain, and make each figure carry as much as it can. | A | 12 |
| R25. Cut repetition and words that add nothing, and simplify what is hard to digest. | A | 6 |

## Before and after

Each pair is invented, set in a fictional pollinator survey at two meadows, unless marked otherwise. The comment column paraphrases the kind of comment the user wrote, in the user's informal register.

### R1. Sentences about the document

| Comment | Before | After |
|---|---|---|
| "this sentence is AI slop, we don't need it" | Counts are compared within the same day, and days are the replicates. The main contrasts were set out in the study plan. | Second sentence deleted. |
| "why add anything after the heading? Just say Specific objectives" | **Specific objectives.** Each objective is listed with its expectation, and section 5 answers each one. | **Specific objectives.** |
| "do we need to say this tool is explained in step 3? we are just adding text" | … a regression on the features from the image model, the one described in step 3, and on body length … | "the one described in step 3" deleted. |
| "we don't need to say where these photos came from" | Caption ending "Photos from the public archive." | Provenance note deleted. |

### R2. The obvious and the expected

| Comment | Before | After |
|---|---|---|
| "this sounds obvious" | The species names in the field photos are still provisional. | Deleted. |
| "so we surveyed every month? Isn't that expected? Saying when the survey started would be enough" | There are survey records for every month up to the end of the season (Figure 2). | Deleted. |
| "isn't this obvious? Also why trace outlines by hand when we can make them automatically" | Because no hand-drawn outlines existed, the training outlines were generated automatically … | The training outlines were generated automatically … |
| "isn't this limitation obvious?", then again in the next version | There is only one meadow per management type, so a difference between meadows cannot be attributed to management. | Shortened after the first comment (pushback), deleted after the second. |

Limit: R2 applies to statements about the text, the setup or common knowledge. A writer who judges one of the author's hypotheses, objectives or results obvious should ask in a comment, not delete it. In a blind test, a rewrite that deleted an expectation as obvious lost content the author had kept.

### R3. Settled facts stated plainly

| Comment | Before | After |
|---|---|---|
| "state facts like this confidently, no need to justify them by citing the protocol" | According to the field protocol, each transect is walked twice a day … | Each transect is walked twice a day. |
| "why call it exploratory, why not present it as a result" | This paired analysis is exploratory. | Deleted, the result is reported as a result. |
| "don't say pending confirmation, assume it is correct, we need to sound confident" | The June visit was assigned to the upper meadow from the field notes, pending confirmation. | "pending confirmation" deleted. |
| "we don't need to say 'not from our site', or say why we had to use another source" | The thresholds were calibrated on photos from an online archive, not from the study site, so that … | Since no expert-labelled photos from the study site exist yet, the thresholds were calibrated on photos from an online archive. |

Limit: R3 removes defensive hedges. It keeps a caveat that changes how a reader should use a number, such as few survey days behind a test or a correction for many tests. Critics asked for those caveats and the user kept them.

### R4. No blame, no self-damage

| Comment | Before | After |
|---|---|---|
| "don't say the site lacks this, it makes the site look bad" | The site has no weather station of its own, so temperature and rain come from a regional dataset. | Temperature and rain come from a regional climate dataset. |
| "this hypothesis makes us look like we don't know our own protocol, assume nothing changed" | … and the pan-trap colour used last year is unconfirmed, so a change of colour remains a possible cause. | Deleted. A neutral sentence about checking the trap colour stayed (pushback), then went after two more comments. |
| "this sounds like we are blaming the people who ran the survey, it might be something natural, wasn't the weather related?" | (the same trap-colour sentence) | Replaced by the weather result: the decline remains after adjusting for each weather measure. |

### R5. No hindsight in expectations

| Comment | Before | After |
|---|---|---|
| "I expected it to be better, but not by how much, so drop the 'as expected'" | … that is, 9 percentage points higher, as expected. | "as expected" deleted. |
| "I expected more small insects in the close-ups but couldn't have predicted how many, readers would be surprised that we predicted almost what was measured, as if this was written after the analyses, which an AI does because it read the results first" | We expect close-up photos to record more insects, about three times as many per square metre, mostly small ones … | We expect close-up photos to record more insects, especially small ones … |
| "I'm tired of hearing 'the expected three times', I expected an increase but never guessed how much" | … stayed below the expected three times. | Deleted in results and conclusion. |

### R6 and R7. Tense and voice of expectations

| Comment | Before | After |
|---|---|---|
| "wouldn't it sound better to state expectations in the present, like 'we expect'? (passive voice is undesired though)" | A regional model was expected to identify species better than the general one … | We expect a regional model to identify species better than the general one … (Spanish "Se espera que …", the writer's mirror, C) |
| "it sounds like we are talking about the report in the third person, is that ok? It sounds weird" | Este informe analiza ese problema … Propone un método automático … | En este informe se analiza ese problema … Se propone un método automático … |

The English report kept "This thesis developed …" without comment, so R7 is evidence for Spanish only.

### R8. Natural small words

| Comment | Before | After |
|---|---|---|
| "aren't we missing a 'the' before 'least'? Some words humans usually keep, I like those spices of my writing style here and there, but just for these cases, and you can push back" | … when the wind disturbs the flowers least | … when the wind disturbs the flowers the least |
| "this sounds weird, I think humans write 'in the future'" | … so in future the counts can also be expressed per area. | … so in the future the counts could also be expressed per area. |
| "I would say 'at a higher altitude', that is how a human would write, maybe 'higher' already implies it, but I prefer being a bit more explicit sometimes" | … and the upper meadow is higher than the lower one. | … and the upper meadow is at a higher altitude than the lower one. |
| "then shouldn't 'respectively' go at the end?" | … with the two nearest towns about 5 and 12 km from the meadows. | … about 5 and 12 km from the upper and lower meadows, respectively. |
| "maybe be a bit more explicit about the close-ups, unless that makes it much longer" | … and what changes when the plots are photographed from closer up. | … and whether photographing the plots from closer up changes these counts and identifications. |

### R9. Everyday words without collisions

| Comment | Before | After |
|---|---|---|
| "can we say photos instead of photographs? Shorter, and everyone knows what photos are" | photographs | photos. "Photograph" stays as a verb. (Spanish "fotos" is the writer's mirror, C.) |
| "which figures are we referring to here?" | Figures in brackets are 95 % confidence intervals … | Numbers in brackets are 95 % confidence intervals … |
| "wouldn't 'insect cut-outs' be clearer?" | On cut-outs of these photos … | On insect cut-outs from these photos … |
| "'insect names'? Wouldn't 'insect identifications' sound better?" | … turns photos into counts and names of insects | … turns photos into counts and identifications of insects |
| "isn't there a better word than 'attraction', something like 'competition'?" | … so attraction to the neighbouring garden does not explain it either. | … so competition from the neighbouring garden's flowers does not explain it either. |
| "what do you mean by 'a handheld device', shouldn't we just name it?" | … recorded with a handheld device. | … recorded with a Brand-X GPS-200 handheld unit. |

### R10. One name per thing

| Comment | Before | After |
|---|---|---|
| "someone who doesn't know our two survey types wouldn't understand this" | On the transects counts are given per 100 m, and on the cameras per photo. | Two survey types are used. The first is two walked transects … The second is two automatic flower cameras. |
| "by 'transect' you mean the walked routes, and by 'camera' the automatic units, I feel this is unclear" | the transects … the cameras (undefined) | "On the walked transects (upper and lower meadow) … on the two flower cameras", with both terms defined once in the site section. |
| "'Upper'? Is that short for the upper meadow?", then "why are we calling it 'Upper'?" | the Upper | the upper meadow, never shortened |
| "by 'both transects' you mean both sites? I prefer 'both sites'" | … appeared on both transects | … appeared at both sites |
| "why did you add RT next to UMR?" | … the upper meadow reserve (UMR, RT) … | … the upper meadow reserve (UMR) … |

### R11. Restate instead of pointing

| Comment | Before | After |
|---|---|---|
| "you just say 'next to the hives', but the reader needs to remember that these are the beehives mentioned earlier" | … that transect runs next to the hives … | The result names the row of beehives again. |

Compare the step-3 example under R1: the user wants the detail repeated, not a pointer such as "the tool of step 3".

### R12. Define only what the reader may not know

| Comment | Before | After |
|---|---|---|
| "for this report we don't need to define a transect" | A transect is a fixed route along which an observer counts animals. | Definition deleted. |
| "this treats my audience as if they were dumb, my committee knows what overdispersion is" | … because the counts are overdispersed, that is, their variance is larger than their mean … | "that is, their variance is larger than their mean" deleted. |
| "this definition, on the other hand, sounds appropriate" | … 95 % confidence intervals, the range of values compatible with the data. | Kept. |

### R13. One obvious meaning

| Comment | Before | After |
|---|---|---|
| "what do you mean by 'comparable survey series'? I don't understand" | … the region lacks comparable survey series | … the region has almost no long-term insect survey records |
| "what do you mean by 'different field times'?" | … compares hours with different field times … | … compares counts made after the same time on the transect: the first 30 minutes of the morning walk with the first 30 minutes of the afternoon walk. |
| "by 'the cause' you mean the decline, not the camera settings change, right?" | The cause remains unexplained … | The cause of the decline remains unexplained … |
| "'resulting method'? What comes before doesn't produce a method" | Compare survey methods and models …, and apply the resulting method to describe … | Develop an automated method …, compare survey methods and models within it, and use it to describe … |
| "when you say 'about half of the insects of 10 mm or more' it sounds weird" | … the plot has about half of the insects of 10 mm or more that it had in the morning. | … the number of insects of 10 mm or more on the plot falls to about half of the morning count. |
| "never below genus? But I saw species predictions with high confidence" | … and never below genus. | Species names are shown with their confidence but never accepted, so no accepted name goes below genus. |

### R14. Qualifiers that imply a contrast

| Comment | Before | After |
|---|---|---|
| "does this mean pollinators are stable on other continents? Better to generalise" | Pollinators are declining on several continents … | Pollinators are declining … |
| "why add 'long-term'? Is there short-term evidence elsewhere? A human would not have added it" | … almost all long-term evidence comes from a few well-studied regions. | … almost all evidence comes from a few well-studied regions. |

### R15 and R16. Numbers the reader can use

| Comment | Before | After |
|---|---|---|
| "wouldn't it be easier to say we take 4 wide photos and 12 close-ups?" | Each wide view covers a quarter of the plot, and the close-ups cover parts of that quarter. | Four wide photos and 12 close-ups, three per quarter. |
| "shouldn't we also give the mean or median counts?" | Ratios only. | Medians added: 42 visits per plot in the morning against 26 in the afternoon. |
| "it would sound better as '1.x times more', so we don't use numbers below 1" | The lower meadow recorded 0.70 times the visits of the upper meadow (0.60–0.82) … | The upper meadow recorded 1.43 times the visits of the lower meadow (1.22–1.67) … |
| "this is 0.62 times, below 1, flip the subjects, it is easier for humans to read" | … in the afternoon there were 0.62 times as many as in the morning (0.50–0.77) … | … in the morning there were 1.61 times as many as in the afternoon (1.30–2.00) … |
| "maybe say large insects dropped to almost half" | … fell to 0.53 times the level of the previous season … | … fell to just over half (0.53 times) the level of the previous season … (the writer corrected "almost half" because 0.53 is above half) |

The user had first allowed a ratio below 1 in one case and later flipped that same ratio, so R16 applies without that exception. Flipped intervals are exact reciprocals of the unrounded estimates.

### R17. Statistics

| Comment | Before | After |
|---|---|---|
| "instead of 'the intervals include 1', say the difference is not significant? Then we'd need a p value?" | … with only six survey days, the intervals include 1. | … the difference was not significant (exploratory p = 0.21 and 0.34). |
| "so one p is for the morning comparison and the other for the afternoon? Make that explicit" | (p = 0.21 and 0.34) | (p = 0.21 for the upper against the lower meadow on morning walks, and p = 0.34 for the same comparison on afternoon walks) |
| "you mean the Benjamini–Hochberg procedure? Why not give its proper name" | … after correcting for the number of tests … | … after the Benjamini–Hochberg correction … |
| "I don't know this method, can we use simpler statistics I would feel comfortable sharing, like mixed models, ANOVA or a t test?" | Because 12 tests were run, the Benjamini–Hochberg procedure was applied … | Later versions kept the correction without its name. The user asked how it works, then which one it was, then for its name, and finally for an explanation in the chat reply rather than in the document. |

The last comment does not ban advanced methods. The method stayed, was named, and was explained to the author in private. Explanations the author needs personally go in the chat reply.

### R18. The reason behind a design step

| Comment | Before | After |
|---|---|---|
| "this is when a second observer joined so both meadows could run in parallel, we should say so" | Since spring both meadows are surveyed on the same day. | In spring a second observer joined, and since then both meadows are surveyed on the same day. |
| "by 'reset' we mean emptying the pan traps, maybe say why we do this" | … and the traps are reset at midday. | After the midday count the pan traps are emptied, so the afternoon catch only includes insects that arrived after midday. |
| "then we should say why we added this second site" | (no reason given) | The second site is there to check that the patterns recur, not to compare management types. |
| "why are the shaded points not part of the comparison?" | (no reason given) | Caption: the plots had been mown the day before those visits, so few flowers were open. |

### R19 to R21. Scope and claims

| Comment | Before | After |
|---|---|---|
| "for this report we don't need this confounding factor" | … next to a row of beehives. | Moved, then removed after a second comment. |
| "I think we can omit this and the acknowledgements" | Next steps, Acknowledgements | Both sections removed, one closing line kept. |
| "we changed the camera settings to improve the photos, which if anything would increase counts, so I don't know if we should mention this" | The cameras showed no comparable decline, but their settings also changed in winter. | Deleted from the decline paragraph. |
| "I wouldn't give a sample size, I wasn't aware of it, just say that a review by specialists is planned" | … a sample of 200 photos is already prepared … | The planned review by specialists and students, with no sample size. |
| "an improved version of the model? Do we have ideas for that? If so, which ones? I don't think we should say this" | The next steps are the specialist review and an improved version of the model … | The promise deleted. |
| "don't say this, I haven't asked anyone yet" | Whether the trap colour changed between seasons is being checked with the field team. | Deleted. |
| "we should say this is planned" | … no specialist audit exists yet … | The audit is described as planned. |
| "I wouldn't say it is left for the thesis, this document is becoming the thesis" | … so it is left for the thesis. | The comparison of community composition is not reported here, because it depends on names that still have to be validated. |

### R25. Words that add nothing

| Comment | Before | After |
|---|---|---|
| "we already said the recorders are automatic, why say again that they record by themselves" | Each recorder is switched on at dawn and records sound by itself every ten minutes. | Each recorder is switched on at dawn and records sound every ten minutes. |
| "I think we can simplify this, it is hard to digest" | … detected with a segmentation model, an edge filter and a second filter for faint edges. | Helper steps left to the appendix, the main tool named. |

Other comments made the same point about a shorter citation form, about "we are just adding text" and about using a shorter word to reduce the length of the text. R8 is the counterweight: cut what adds nothing, keep what a person would say.

### R22. Citations

| Comment | Before | After |
|---|---|---|
| "which estimate? We lack citations, we need citations for all information" | … where, according to one estimate, … | Author-year citations throughout. |
| "we are repeating the citations, I would put both at the end of the sentence" | Pollinators are declining (Author A et al. 2018; Author B et al. 2020), but almost all evidence comes from a few regions (Author B et al. 2020). | Pollinators are declining, but almost all evidence comes from a few regions (Author A et al. 2018; Author B et al. 2020). |
| "I wouldn't say 'cited by', a simpler citation saves words" | According to an estimate by C. Author, cited by Author D et al. (2015) … | According to an estimate by C. Author (Author D et al. 2015) … |
| "is there more research from our site we could cite? But don't force citations that aren't relevant" | | One relevant study from the site added. |

### R23 and R24. Format and figures

| Comment | Before | After |
|---|---|---|
| "wouldn't bullets be easier to read than this table?" | A three-column table of main findings with one sentence per cell. | Four bullets, one finding each. |
| "can we label the panels a) and b)?" | Left panel … right panel … | Panel a) … panel b) … |
| "this is hard to follow in words, could a figure show which plots were counted?" | A paragraph listing which plots were counted on which days. | A calendar figure with one row per plot and a filled cell for each day it was counted. |
| "could the figure also show the area outside the counted plot?" | Photo with the counted plot outlined. | Photo with the area outside the plot darkened and the excluded classes labelled. |

## Pushback record

The user invites pushback ("you can also push back to this if it is actually a mistake", "if you disagree then it's ok"). These cases show which pushback held. Each case keeps the original sequence of events, with invented details.

| Case | What happened | Lesson |
|---|---|---|
| An acronym | After the user questioned the second acronym (RT, the trust that runs the reserve), the writer replaced it with the trust's full name. Seeing the longer form, the user said the acronym did save words but was unsure which was better, and the next version used "the RT reserve". | A comment fixes one problem. Check that the fix does not create another, here length. |
| "Almost half" | The user suggested "almost half" for a ratio just above 0.5. The writer wrote "just over half" instead. No further comment. | Correct the user's wording when the number disagrees with it. |
| A DOI | The user flagged an odd-looking string in a reference twice. The writer kept it both times: it is part of the real DOI. | Factual pushback with evidence holds, even when the comment repeats. |
| A limitation | The writer kept a shortened limitation. The user asked again, and it was deleted. | When the user repeats a style or scope comment, comply. |
| A neutral hypothesis | The writer kept a neutral sentence about checking a possible protocol change. The user rejected it in the next round, twice. | Pushback on scope or tone is weak. Do not keep a sentence the user has asked to drop for tone. |
| A ratio below 1 | The user first allowed a ratio below 1, then asked for it to be flipped. | The later comment wins. |
| A correction method | The user asked to drop an unfamiliar correction method. The correction stayed unnamed, the user asked which one it was, then asked for its name and for an explanation in the chat. | Read the reason behind a comment (the author must be able to follow the method), not only its words. |
| A critic and a sample size | A critic objected to a sample size in the text, the writer kept it because it was documented, and the user then removed it. | Documented is not the same as endorsed by the author. |
| A critic and a confound | A critic asked to restore a confounding factor the user had removed. The writer declined. | The user's comments outrank critic suggestions on scope. |

## Content and analysis comments

These are not style rules. They show what the user asks about, which the comment-emulation mode in [critic-loop.md](critic-loop.md) needs. The examples are invented.

- **"How do you know?"** Every number needs a traceable source: how a scale was measured, how large its error is, what share of detections are debris, whether test photos were in a model's training data.
- **Missing breakdowns.** A percentage for the subgroup that matters: accepted names for large insects, close-ups by size class, medians beside ratios, whether confidence rises in close-ups.
- **Fair comparisons.** Rescore the baseline on the same species list, separate the gain from a list update from the gain from the method, ask whether competing models are public and can be run.
- **Untested explanations.** Weather with a time lag, one sampling point drawing animals away from another, a settings change shown with example photos and the settings.
- **Field facts the writer cannot know.** The user corrected sampling frequency, distances and site descriptions. A writer should flag such facts as uncertain rather than invent them.
- **Missing pieces of a method.** Name the models, say how thresholds were calibrated and how they will be validated, give the model formula, package and appendix section, add a methods box in a second version.
- **Questions for the user alone.** Answer in the reply, do not add to the document.
