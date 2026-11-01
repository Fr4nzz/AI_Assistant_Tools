# Comment ledger

The user left more than a hundred bracketed comments on several versions of a report. This file distils the style comments into rules, gives before and after pairs, and records where a writer pushed back. Use it to calibrate a draft, to check a revision, or to write comments the way the user would (see [critic-loop.md](critic-loop.md)).

The original report contains unpublished work, so this public copy paraphrases the comments and replaces every example and every incident with an invented one that makes the same point. The sentences, numbers, places, tools and events below are fictional. The rules and their evidence strength are unchanged.

## Evidence strength

- **A, explicit and repeated:** two or more comments in the same direction, or a comment the user repeated after a writer ignored it.
- **B, explicit once:** one direct comment with a clear reason.
- **C, inferred:** a pattern in how comments were resolved, never stated as a rule.

When a rule conflicts with a later comment, the later comment wins. A rule here is a default for this user's reports, theses and similar documents. The user said of one correction that it applied only to the cases they had pointed out, not to every sentence. Apply a rule where its reason applies.

## How the user judges a sentence

The user's recurring test is whether a human author would write the sentence. The comments say so directly, for example by asking whether a person would have added a word, or by saying that a phrasing is how a person would write it. Some comments call a sentence "AI slop". One explains the mechanism: the AI read the results before writing, so it predicted what was later measured.

The comments are short questions more often than orders: "what do you mean by …", "isn't this obvious?", "shouldn't we …". Almost every question was a request to change the text. A few are marked as questions for the user alone ("just for me, not for this document", "explain this to me in the chat"). Those are answered in the reply and leave the document unchanged.

## Rules

| Rule | Strength |
|---|---|
| R1. Cut sentences about the document itself: what a section will do, where a method is explained, where a photo came from. | A |
| R2. Cut sentences that state the obvious or the expected. | A |
| R3. State settled facts plainly. Drop defensive hedges and appeals to a protocol or to confirmation still pending. | A |
| R4. No wording that blames the people running the work or makes the team, the site or partners look bad. | A |
| R5. Expectations are what the author expected before the results. No numbers taken from the results, no "as expected" after a result the author never predicted in size. | A |
| R6. State expectations in the present: "We expect", Spanish "Se espera que". | B |
| R7. In Spanish, avoid making the document the actor ("Este informe analiza … Propone"). The impersonal "se" is the writer's fix that the user accepted (C). | B |
| R8. Keep the small words a person would keep, and be slightly explicit when it reads more naturally. Only where the sentence otherwise sounds compressed. | A |
| R9. Use the everyday word every reader knows, and avoid words that collide with labels in the document. | A |
| R10. Give each thing one name, define it once, and name it by what the reader means (the site, not the equipment). | A |
| R11. When a sentence depends on an earlier detail, restate the detail in a few words instead of pointing to a section. | B |
| R12. Define only what the intended reader may not know. Defining a familiar term talks down to the reader. | A |
| R13. Every phrase needs one obvious meaning. Replace vague or internal wording with the specific thing. | A |
| R14. Drop qualifiers that imply a contrast the author did not mean. | A |
| R15. Give concrete numbers and simple counts rather than abstract descriptions or ratios alone. | A |
| R16. Write ratios above 1 by choosing the reference group, and make the words match the number. | A |
| R17. Statistics: name the test, say "not significant" with the p value, tie each p value to its comparison, and explain an unfamiliar method to the author in the reply. | A |
| R18. Give the reason for a design step when the reader would wonder why. | A |
| R19. Leave out tangents this reader does not need, even true ones. | A |
| R20. Claim only plans, numbers and actions the author has endorsed. Plans the author has made are welcome ("what is still missing"). | A |
| R21. Do not defer material to another document ("left for the thesis"). Say why it is not reported here. | B |
| R22. Cite every factual claim, cite once at the end of the sentence, and use the plain citation form. | A |
| R23. For a summary of findings, bullets rather than a table. Subfigure labels a) and b). When the user dislikes a heading style, offer options. | B |
| R24. Show with a figure what the text struggles to explain, and make each figure carry as much as it can. | A |
| R25. Cut repetition and words that add nothing, and simplify what is hard to digest. | A |

## Before and after

The pairs are invented. Most are set in a fictional bird survey at two lakes, with observers doing point counts and automatic sound recorders, and a few in a lab or software setting. The comment column paraphrases the kind of comment the user wrote, in an informal register.

### R1. Sentences about the document

| Comment | Before | After |
|---|---|---|
| "this sentence is AI slop, we don't need it" | Counts are compared within the same morning, and mornings are the replicates. The main contrasts were set out in the study plan. | Second sentence deleted. |
| "why add anything after the heading? Just say Specific objectives" | **Specific objectives.** Each objective is listed with its expectation, and section 5 answers each one. | **Specific objectives.** |
| "do we need to say this survey is explained in step 3? we are just adding text" | … a regression on the shoreline variables from the habitat survey, the one described in step 3, and on lake depth … | "the one described in step 3" deleted. |
| "we don't need to say where these photos came from" | Caption ending "Photos from the public archive." | Provenance note deleted. |

### R2. The obvious and the expected

| Comment | Before | After |
|---|---|---|
| "this sounds obvious" | The species list for the recordings is still provisional. | Deleted. |
| "so we surveyed every month? Isn't that expected? Saying when the survey started would be enough" | There are survey records for every month up to the end of the season (Figure 2). | Deleted. |
| "isn't this obvious? Also why label calls by hand when a tool can do it" | Because no manual labels existed, the call labels were produced automatically … | The call labels were produced automatically … |
| "isn't this limitation obvious?", then again in the next version | There is only one lake per water-level regime, so a difference between lakes cannot be attributed to the regime. | Shortened after the first comment (pushback), deleted after the second. |

Limit: R2 applies to statements about the text, the setup or common knowledge. A writer who judges one of the author's hypotheses, objectives or results obvious should ask in a comment, not delete it. In a blind test, a rewrite that deleted an expectation as obvious lost content the author had kept.

### R3. Settled facts stated plainly

| Comment | Before | After |
|---|---|---|
| "state facts like this confidently, no need to justify them by citing the protocol" | According to the field protocol, each point is counted for ten minutes … | Each point is counted for ten minutes. |
| "why call it exploratory, why not present it as a result" | This paired analysis is exploratory. | Deleted, the result is reported as a result. |
| "don't say pending confirmation, assume it is correct, we need to sound confident" | The June count was assigned to the north lake from the field notes, pending confirmation. | "pending confirmation" deleted. |
| "we don't need to say 'not from our site', or say why we had to use another source" | The call detector was tuned on recordings from a public sound library, not from the study lakes, so that … | Since no expert-labelled recordings from the study lakes exist yet, the call detector was tuned on recordings from a public sound library. |

Limit: R3 removes defensive hedges. It keeps a caveat that changes how a reader should use a number, such as few survey mornings behind a test or a correction for many tests. Critics asked for those caveats and the user kept them.

### R4. No blame, no self-damage

| Comment | Before | After |
|---|---|---|
| "don't say the reserve lacks this, it makes the reserve look bad" | The reserve keeps no visitor records of its own, so visitor numbers come from the regional park office. | Visitor numbers come from the regional park office. |
| "this makes us look like we don't know our own lab procedure, assume nothing changed" (lab setting) | … and the reagent batch used last year was not recorded, so a batch mix-up remains a possible cause of the lower yield. | Deleted. A neutral sentence about checking the batch stayed (pushback), then went after more comments. |
| "this sounds like we are blaming the technicians, could it be something else, like room temperature?" (lab setting) | (the same batch sentence) | Replaced by the temperature result: the lower yield remains after adjusting for room temperature. |

### R5. No hindsight in expectations

| Comment | Before | After |
|---|---|---|
| "I expected it to be better, but not by how much, so drop the 'as expected'" | … that is, 9 percentage points higher, as expected. | "as expected" deleted. |
| "I expected the cache to help but couldn't have predicted by how much, readers would wonder how we predicted almost exactly what was measured, as if this was written after the tests, which an AI does because it read the results first" (software setting) | We expect the cache to make pages load faster, about four times faster, mostly for large pages … | We expect the cache to make pages load faster, especially large pages … |
| "I'm tired of hearing 'the expected four times', I expected an improvement but never guessed how much" (software setting) | … stayed below the expected four times. | Deleted in results and conclusion. |

### R6 and R7. Tense and voice of expectations

| Comment | Before | After |
|---|---|---|
| "wouldn't it sound better to state expectations in the present, like 'we expect'? (passive voice is undesired though)" | A regional call detector was expected to perform better than the general one … | We expect a regional call detector to perform better than the general one … (Spanish "Se espera que …", the writer's mirror, C) |
| "it sounds like we are talking about the report in the third person, is that ok? It sounds weird" | Este informe analiza ese problema … Propone un método automático … | En este informe se analiza ese problema … Se propone un método automático … |

The English version kept "This thesis developed …" without comment, so R7 is evidence for Spanish only.

### R8. Natural small words

| Comment | Before | After |
|---|---|---|
| "aren't we missing a 'the' before 'least'? Some small words people keep, and I like them here and there, but only in these cases, and you can push back" | … when boat traffic disturbs the birds least | … when boat traffic disturbs the birds the least |
| "this sounds weird, I think people write 'in the future'" | … so in future the counts can also be expressed per hectare. | … so in the future the counts could also be expressed per hectare. |
| "I would say 'at a higher altitude', that is how a person would write, maybe 'higher' already implies it, but I prefer being a bit more explicit sometimes" | … and the north lake is higher than the south lake. | … and the north lake is at a higher altitude than the south lake. |
| "then shouldn't 'respectively' go at the end?" | … with the two nearest towns about 5 and 12 km from the lakes. | … about 5 and 12 km from the north and south lakes, respectively. |
| "maybe be a bit more explicit about the longer counts, unless that makes it much longer" | … and what changes when points are counted for longer. | … and whether counting each point for longer changes these counts and identifications. |

### R9. Everyday words without collisions

| Comment | Before | After |
|---|---|---|
| "can we say photos instead of photographs? Shorter, and everyone knows what photos are" | photographs | photos. "Photograph" stays as a verb. (Spanish "fotos" is the writer's mirror, C.) |
| "which figures are we referring to here?" | Figures in brackets are 95 % confidence intervals … | Numbers in brackets are 95 % confidence intervals … |
| "wouldn't 'call clips' be clearer?" | On clips of these recordings … | On call clips from these recordings … |
| "'bird names'? Wouldn't 'bird identifications' sound better?" | … turns recordings into counts and names of birds | … turns recordings into counts and identifications of birds |
| "isn't there a better word than 'attraction', something like 'competition'?" | … so attraction to the neighbouring feeders does not explain it either. | … so competition from the neighbouring feeders does not explain it either. |
| "what do you mean by 'a handheld device', shouldn't we just name it?" | … recorded with a handheld device. | … recorded with a Brand-X GPS-200 handheld unit. |

### R10. One name per thing

| Comment | Before | After |
|---|---|---|
| "someone who doesn't know our two survey types wouldn't understand this" | On the points counts are given per ten minutes, and on the recorders per hour. | Two survey types are used. The first is point counts by observers … The second is automatic sound recorders. |
| "by 'points' you mean the observer counts, and by 'units' the recorders, I feel this is unclear" | the points … the units (undefined) | "In the point counts (north and south lake) … on the four sound recorders", with both terms defined once in the site section. |
| "'North'? Is that short for the north lake?", then "why are we calling it 'North'?" | the North | the north lake, never shortened |
| "by 'both recorders' you mean both lakes? I prefer 'both sites'" | … was heard on both recorders | … was heard at both sites |
| "why did you add RT next to NLR?" | … the north lake reserve (NLR, RT) … | … the north lake reserve (NLR) … |

### R11. Restate instead of pointing

| Comment | Before | After |
|---|---|---|
| "you just say 'near the jetty', but the reader needs to remember that this is the jetty with the boat traffic mentioned earlier" | … that point is near the jetty … | The result names the busy boat jetty again. |

Compare the step-3 example under R1: the user wants the detail repeated, not a pointer such as "the survey of step 3".

### R12. Define only what the reader may not know

| Comment | Before | After |
|---|---|---|
| "for this report we don't need to define a point count" | A point count is a fixed spot where an observer records every bird for a set time. | Definition deleted. |
| "this treats my readers as if they didn't know the field, my committee knows what overdispersion is" | … because the counts are overdispersed, that is, their variance is larger than their mean … | "that is, their variance is larger than their mean" deleted. |
| "this definition, on the other hand, sounds appropriate" | … 95 % confidence intervals, the range of values compatible with the data. | Kept. |

### R13. One obvious meaning

| Comment | Before | After |
|---|---|---|
| "what do you mean by 'comparable survey series'? I don't understand" | … the region lacks comparable survey series | … the region has almost no long-term bird survey records |
| "what do you mean by 'different recording times'?" | … compares hours with different recording times … | … compares recordings made after the same time since the recorder started: the first hour after dawn with the first hour after dusk. |
| "by 'the cause' you mean the lower yield, not the supplier change, right?" (lab setting) | The cause remains unexplained … | The cause of the lower yield remains unexplained … |
| "'resulting method'? What comes before doesn't produce a method" | Compare survey methods and detectors …, and apply the resulting method to describe … | Develop an automated method …, compare survey methods and detectors within it, and use it to describe … |
| "when you say 'about half of the calls of 3 seconds or more' it sounds weird" | … the recorder has about half of the calls of 3 seconds or more that it had at dawn. | … the number of calls of 3 seconds or more on the recorder falls to about half of the dawn count. |
| "never deletes? But I saw it remove files" (software setting) | … and the tool never deletes files. | The tool removes only the temporary files it created, and never deletes the user's files. |

### R14. Qualifiers that imply a contrast

| Comment | Before | After |
|---|---|---|
| "does this mean wetland birds are stable on other continents? Better to generalise" | Wetland birds are declining on several continents … | Wetland birds are declining … |
| "why add 'long-term'? Is there short-term evidence elsewhere? A person would not have added it" | … almost all long-term evidence comes from a few well-studied regions. | … almost all evidence comes from a few well-studied regions. |

### R15 and R16. Numbers the reader can use

| Comment | Before | After |
|---|---|---|
| "wouldn't it be easier to say how many points we count on each lake?" | The points cover the shoreline at regular intervals, with extra points in the reed beds. | Eight shoreline points and four reed-bed points per lake. |
| "shouldn't we also give the mean or median counts?" | Ratios only. | Medians added: 42 birds per point at dawn against 26 at midday. |
| "it would sound better as '1.x times more', so we don't use numbers below 1" | The south lake recorded 0.70 times the birds of the north lake (0.60–0.82) … | The north lake recorded 1.43 times the birds of the south lake (1.22–1.67) … |
| "this is 0.62 times, below 1, flip the subjects, it is easier to read" | … at midday there were 0.62 times as many as at dawn (0.50–0.77) … | … at dawn there were 1.61 times as many as at midday (1.30–2.00) … |
| "maybe say the count dropped to almost half" | … fell to 0.53 times the level of the previous season … | … fell to just over half (0.53 times) the level of the previous season … (the writer corrected "almost half" because 0.53 is above half) |

The user had first allowed a ratio below 1 in one case and later flipped that same ratio, so R16 applies without that exception. Flipped intervals are exact reciprocals of the unrounded estimates.

### R17. Statistics

| Comment | Before | After |
|---|---|---|
| "instead of 'the intervals include 1', say the difference is not significant? Then we'd need a p value?" | … with only six survey mornings, the intervals include 1. | … the difference was not significant (exploratory p = 0.21 and 0.34). |
| "so one p is for the dawn comparison and the other for midday? Make that explicit" | (p = 0.21 and 0.34) | (p = 0.21 for the north against the south lake at dawn, and p = 0.34 for the same comparison at midday) |
| "you mean a specific correction? Why not give its proper name" | … after correcting for the number of tests … | … after the Benjamini–Hochberg correction … |
| "I don't know this method, can we use simpler statistics I would feel comfortable presenting?" | A method the author had not met before, named in the text. | The method stayed and was named, and the writer explained it to the author in the chat reply rather than in the document. |

The last comment does not ban advanced methods. The author must be able to follow and defend the method, so explanations the author needs personally go in the chat reply.

### R18. The reason behind a design step

| Comment | Before | After |
|---|---|---|
| "this is when a second observer joined so both lakes could be counted in parallel, we should say so" | Since spring both lakes are counted on the same morning. | In spring a second observer joined, and since then both lakes are counted on the same morning. |
| "by 'reset' we mean clearing the memory cards, maybe say why we do this" | … and the recorders are reset each week. | Each week the memory cards are swapped, so a recorder never stops because its card is full. |
| "then we should say why we added this second site" | (no reason given) | The second site is there to check that the patterns recur, not to compare water-level regimes. |
| "why are the shaded points not part of the comparison?" | (no reason given) | Caption: strong wind on those mornings made the calls inaudible. |

### R19 to R21. Scope and claims

| Comment | Before | After |
|---|---|---|
| "for this report we don't need this confounding factor" | … near a feeding station run by a neighbour. | Moved, then removed after a second comment. |
| "I think we can omit this and the acknowledgements" | Next steps, Acknowledgements | Both sections removed, one closing line kept. |
| "we upgraded the build machine to make it faster, which if anything would speed up the tests, so I don't know if we should mention this" (software setting) | The test suite showed no comparable slowdown, but the build machine was also replaced in winter. | Deleted from the slowdown paragraph. |
| "I wouldn't give a sample size, I wasn't aware of it, just say that a review by specialists is planned" | … a sample of 200 recordings is already prepared … | The planned review by specialists and students, with no sample size. |
| "an improved version of the detector? Do we have ideas for that? If so, which ones? I don't think we should say this" | The next steps are the specialist review and an improved version of the detector … | The promise deleted. |
| "don't say this, I haven't asked anyone yet" | Whether the recorder positions changed between seasons is being checked with the field team. | Deleted. |
| "we should say this is planned" | … no specialist audit exists yet … | The audit is described as planned. |
| "I wouldn't say it is left for the thesis, this document is becoming the thesis" | … so it is left for the thesis. | The comparison of community composition is not reported here, because it depends on identifications that still have to be validated. |

### R25. Words that add nothing

| Comment | Before | After |
|---|---|---|
| "we already said the recorders are automatic, why say again that they record by themselves" | Each recorder is switched on at dawn and records sound by itself every ten minutes. | Each recorder is switched on at dawn and records sound every ten minutes. |
| "I think we can simplify this, it is hard to digest" | … detected with a call detector, a noise gate and a second filter for faint calls. | Helper steps left to the appendix, the main tool named. |

Other comments made the same point about a shorter citation form, about "we are just adding text" and about using a shorter word to reduce the length of the text. R8 is the counterweight: cut what adds nothing, keep what a person would say.

### R22. Citations

| Comment | Before | After |
|---|---|---|
| "which estimate? We lack citations, we need citations for all information" | … where, according to one estimate, … | Author-year citations throughout. |
| "we are repeating the citations, I would put both at the end of the sentence" | Wetland birds are declining (Author A et al. 2018; Author B et al. 2020), but almost all evidence comes from a few regions (Author B et al. 2020). | Wetland birds are declining, but almost all evidence comes from a few regions (Author A et al. 2018; Author B et al. 2020). |
| "I wouldn't say 'cited by', a simpler citation saves words" | According to an estimate by C. Author, cited by Author D et al. (2015) … | According to an estimate by C. Author (Author D et al. 2015) … |
| "is there more research from our site we could cite? But don't force citations that aren't relevant" | | One relevant study from the site added. |

### R23 and R24. Format and figures

| Comment | Before | After |
|---|---|---|
| "wouldn't bullets be easier to read than this table?" | A three-column table of main findings with one sentence per cell. | Four bullets, one finding each. |
| "can we label the panels a) and b)?" | Left panel … right panel … | Panel a) … panel b) … |
| "this is hard to follow in words, could a figure show which points were counted?" | A paragraph listing which points were counted on which mornings. | A calendar figure with one row per point and a filled cell for each morning it was counted. |
| "could the map also show the area we did not survey?" | Map with the survey points marked. | Map with the unsurveyed shoreline greyed out and the excluded points labelled. |

## Pushback record

The user invites pushback, saying that a writer may push back when a suggestion is actually a mistake. These cases show which pushback held. The incidents are invented and keep only the lesson of the original.

| Case | What happened | Lesson |
|---|---|---|
| A units note | The user asked to remove a units note from a table header. The writer moved the units into every cell, which doubled the width of the table. The user then asked for a single units line under the table. | A comment fixes one problem. Check that the fix does not create another. |
| "Almost half" | The user suggested "almost half" for a ratio just above 0.5. The writer wrote "just over half" instead. No further comment. | Correct the user's wording when the number disagrees with it. |
| A package name | The user flagged the odd capitalisation of a software package name more than once. The writer kept it each time: it is the package's official spelling. | Factual pushback with evidence holds, even when the comment repeats. |
| A limitation | The writer kept a shortened limitation. The user asked again, and it was deleted. | When the user repeats a style or scope comment, comply. |
| A neutral hypothesis | The writer kept a neutral sentence about checking a possible procedure change. The user rejected it in the next round. | Pushback on scope or tone is weak. Do not keep a sentence the user has asked to drop for tone. |
| A ratio below 1 | The user first allowed a ratio below 1, then asked for it to be flipped. | The later comment wins. |
| An unfamiliar method | The user asked for simpler statistics instead of an unfamiliar method. Dropping the method would have weakened the result, so the writer kept it, named it and explained it to the user in the reply. | Read the reason behind a comment (the author must be able to follow the method), not only its words. |
| A critic and a sample size | A critic objected to a sample size in the text, the writer kept it because it was documented, and the user then removed it. | Documented is not the same as endorsed by the author. |
| A critic and a confound | A critic asked to restore a confounding factor the user had removed. The writer declined. | The user's comments outrank critic suggestions on scope. |

## Content and analysis comments

These are not style rules. They show what the user asks about, which the comment-emulation mode in [critic-loop.md](critic-loop.md) needs. The examples are invented.

- **"How do you know?"** Every number needs a traceable source: how a distance was measured, how large its error is, what share of detections are noise, whether test data were in a model's training data.
- **Missing breakdowns.** A percentage for the subgroup that matters: identifications for the rarest species, counts by distance class, medians beside ratios, whether confidence rises with longer counts.
- **Fair comparisons.** Rescore the baseline on the same species list, separate the gain from a list update from the gain from the method, ask whether competing tools are public and can be run.
- **Untested explanations.** Weather with a time lag, one survey point drawing animals away from another, an equipment change shown with examples and its settings.
- **Field facts the writer cannot know.** The user corrected sampling frequency, distances and site descriptions. A writer should flag such facts as uncertain rather than invent them.
- **Missing pieces of a method.** Name the models, say how thresholds were set and how they will be validated, give the model formula, package and appendix section, add a methods box in a second version.
- **Questions for the user alone.** Answer in the reply, do not add to the document.
