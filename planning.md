# TakeMeter Planning

## Community

TakeMeter focuses on English-language comments from **r/worldcup**, a large event-driven community where supporters discuss national teams, players, tactics, match events, and predictions. This community is a strong fit because a single thread can contain detailed tactical analysis, reasonable but general opinions, unsupported hot takes, and emotional match-day banter. Distinguishing these forms of discourse can help readers find substantive discussion and help researchers or moderators describe conversation quality without treating popularity or correctness as quality.

## Labels

Labels are applied in the priority order shown below. A comment's length, tone, popularity, or ultimate correctness does not determine its label.

### 1. `analysis`

`analysis` is a judgment or prediction supported by connected, specific evidence, such as tactics, statistics, match events, lineups, or historical comparisons; the comment must state or clearly imply how the evidence supports its conclusion.

- “Morocco's press keeps failing because the wingers jump forward while the midfield stays deep, leaving the opposing pivot free to turn.”
- “Spain played 120 minutes three days ago while Brazil finished in regulation, so Brazil should have the physical advantage late in the match.”

### 2. `reasoned_opinion`

`reasoned_opinion` is a judgment or prediction supported by a relevant rationale that remains general and does not cite concrete, verifiable evidence.

- “I would start the faster winger because this opponent leaves space behind its fullbacks.”
- “France is more likely to win because its bench gives the coach more ways to change the match.”

### 3. `unsupported_take`

`unsupported_take` is a contestable judgment or prediction with no meaningful rationale, including claims supported only by decorative facts or reasoning that does not logically establish the conclusion.

- “England are frauds and will lose to the first good team.”
- “He has zero goals, so he has been useless all tournament.”

### 4. `reaction_banter`

`reaction_banter` primarily expresses emotion, celebration, frustration, mockery, a meme, a chant, or play-by-play without making a substantive contestable claim.

- “GOOOOOAL! What a finish!”
- “Someone check on the crossbar after that rocket.”

## Hard Edge Cases and Annotation Rules

The hardest boundary is between `analysis` and `reasoned_opinion`: a rationale may sound football-specific without containing evidence concrete enough to verify. The boundary between `unsupported_take` and `reaction_banter` is also difficult when an insult implicitly judges a player or team. I will use the following rules:

- Evidence qualifies for `analysis` only if it identifies an observable detail and connects that detail to a conclusion. Football vocabulary alone is not evidence.
- A relevant causal rationale without a concrete observation is `reasoned_opinion`.
- A bare or weakly supported contestable claim is `unsupported_take`, even if it is emotional or insulting.
- Pure emotion or mockery with no recoverable substantive claim is `reaction_banter`.
- Sarcasm is labeled by its recoverable implied claim. If that meaning depends on missing context, the comment is excluded.
- Deleted, removed, bot-generated, non-English, duplicate, link-only, ticket/travel, administrative, pure information-request, and irrecoverably context-dependent comments are excluded.

For genuinely ambiguous comments, I will record the proposed label, the competing label, and a short reason in an annotation-notes field. I will apply the written priority rules first, flag low-confidence cases for adjudication, and update the guidelines only when the same ambiguity recurs systematically; any changed rule will then be applied consistently to earlier annotations.

### Boundary Stress Test

The following synthetic posts test the definitions before collection. Each has a predetermined resolution, which makes the boundary operational rather than relying on intuition during annotation.

| Boundary post | Competing labels | Resolution |
|---|---|---|
| “They will struggle because their midfield is too passive.” | `analysis` / `reasoned_opinion` | `reasoned_opinion`: relevant rationale, but no specific observable event or pattern. |
| “Their midfield completed only two passes into the final third after halftime, so they could not sustain attacks.” | `analysis` / `reasoned_opinion` | `analysis`: a concrete statistic is causally connected to the judgment. |
| “That high line is going to get punished.” | `reasoned_opinion` / `unsupported_take` | `reasoned_opinion`: the high line supplies a relevant tactical rationale, although it is general. |
| “Germany had 70% possession, so they were obviously brilliant.” | `analysis` / `unsupported_take` | `unsupported_take`: the statistic is decorative because possession alone does not support “brilliant.” |
| “This goalkeeper is a disaster.” | `unsupported_take` / `reaction_banter` | `unsupported_take`: it contains a recoverable contestable judgment. |
| “My grandmother saves that!” | `unsupported_take` / `reaction_banter` | `reaction_banter`: the primary function is comic frustration, with no sufficiently precise claim. |
| “Great defending 🙄” | `unsupported_take` / `reaction_banter` | Exclude if isolated: the sarcastic target and implied event cannot be recovered from the text alone. |
| “Three runners attacked the near post and nobody covered the cutback; that is why the equalizer was inevitable.” | `analysis` / `reasoned_opinion` | `analysis`: specific positioning and a match event are explicitly connected. |

If annotators cannot independently apply these resolutions, I will tighten the corresponding rule and rerun the stress test before full annotation. A 40-comment pilot will follow; if more than 10% of eligible comments remain low-confidence or one label pair shows systematic disagreement, full annotation pauses for another guideline revision.

## Data Collection Plan

I will collect comments through Reddit's authenticated, read-only API from multiple r/worldcup match threads and team-discussion threads during the 2026 World Cup. Credentials will be supplied through environment variables, usernames will not be retained, and each retained record will include Reddit comment ID, text, thread ID, permalink, timestamp, final label, annotation confidence, and split. Per-thread caps and duplicate-text checks will prevent one match, team, or fanbase from dominating the dataset.

The final dataset will contain **240 comments: 60 per label**. After the first 200 eligible candidates, I will compare label counts with the target distribution. If a label is underrepresented, I will use targeted but rule-based collection from thread types likely to contain it—for example, post-match tactical threads for `analysis` or live match threads for `reaction_banter`—while keeping the same eligibility and labeling standards; I will not relabel borderline examples to fill a quota. If targeted collection still cannot yield 60 defensible examples, I will document the natural imbalance and reduce all classes to the largest equal, adequately supported count rather than fabricate balance.

The data will be split approximately 70/15/15 into train, validation, and test sets while preserving class balance. Splitting will be grouped by source thread, and neither a thread nor exact or normalized duplicate text may cross splits. The test set will remain untouched until model and prompt choices are final.

## Evaluation Metrics

I will report **accuracy** for overall correctness and **macro-F1** as the primary metric because each discourse type matters equally and a model should not appear strong by favoring easier or more common labels. Per-class precision, recall, and F1 will show whether the model over-assigns or misses a particular discourse type; this is especially important for the adjacent `analysis`/`reasoned_opinion` and `unsupported_take`/`reaction_banter` boundaries. A confusion matrix will expose which distinctions fail, while concrete error review will test whether failures follow predictable linguistic patterns.

I will also evaluate confidence using reliability bins, expected calibration error, multiclass Brier score, and accuracy by confidence band. Raw fine-tuned-model confidence will be compared with temperature-scaled confidence, with the temperature fitted only on validation predictions and assessed once on the test set. For the 40 comments independently labeled by a second annotator, I will report percentage agreement, Cohen's kappa, disagreements by label pair, and adjudicated labels; model performance is not credible if humans cannot apply the taxonomy reliably.

## Definition of Success

The experiment will count as successful if the held-out, thread-isolated test set achieves all of the following:

- macro-F1 of at least **0.75** and accuracy of at least **0.78**;
- no class F1 below **0.65**;
- second-annotator Cohen's kappa of at least **0.70**;
- calibrated expected calibration error no greater than **0.10**, with calibration not reducing test macro-F1 because it must not change predicted classes;
- a documented improvement over the Groq zero-shot baseline in macro-F1, or a clear cost/latency advantage if performance is statistically indistinguishable.

For deployment in a real community tool, I would require the stricter standard of macro-F1 at least **0.80**, every class F1 at least **0.72**, kappa at least **0.75**, and calibrated ECE at most **0.08**. Predictions below a validation-selected confidence threshold must be shown as uncertain or sent for review rather than presented as authoritative. These thresholds make the final decision objective, although results from only 240 comments will still be treated as a pilot rather than evidence of broad generalization across future tournaments or communities.

## AI Tool Plan

Before annotation, I will ask an LLM to critique the label definitions for overlap, missing cases, reliance on unstated context, and rules that cannot be applied consistently. I will also ask it to generate 5–10 boundary posts without assigning labels; I will classify them using the guidelines and tighten any definition that does not produce a clean, defensible answer. The eight-post stress test above records this process's initial boundary set and the resulting explicit resolutions.

I will use **Groq's `llama-3.3-70b-versatile`** to pre-label candidate comments, but its output will be treated only as an annotation aid. Every comment will be reviewed and labeled by a human without changing standards to match the model. The dataset will contain `prelabel`, `prelabel_model`, `prelabel_prompt_version`, `human_label`, and `prelabel_changed` fields so the AI-assisted workflow can be disclosed and agreement between pre-labels and final labels can be audited. The independent reliability subset will be exported without pre-labels so the second annotator remains blind.

The same model will serve as a zero-shot baseline on the untouched test set using taxonomy definitions, no examples, temperature 0, and strict structured output. Baseline outputs and parsing failures will be retained so malformed responses cannot silently disappear from evaluation.

## Failure Analysis Plan

Evaluation will produce a machine-readable table of every test prediction containing text, gold label, predicted label, confidence, correct/incorrect status, source thread, and annotation notes. A failure-analysis script will validate the table and generate counts by gold/predicted label pair, confidence band, text length, question/sarcasm markers, evidence cues such as numbers and tactical terms, and thread; it will also output the highest-confidence errors and representative examples from each major confusion pair. The script must use the complete test set rather than a hand-selected error sample.

I will give the LLM my complete list of wrong predictions and ask it to propose recurring patterns, focusing on decorative statistics, implicit causal links, sarcasm, emotional substantive claims, context dependence, and football vocabulary mistaken for evidence. I will treat those suggestions as hypotheses: each claimed pattern must be verified against the original comments, counted with explicit inclusion criteria, checked for counterexamples among correct predictions, and rejected if it cannot be reproduced. The final report will include at least three concrete errors with causal explanations, systematic pattern counts, parsing failures, and differences between the fine-tuned and zero-shot systems; the LLM will not decide whether an error pattern is real.
