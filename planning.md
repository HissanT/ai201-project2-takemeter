# TakeMeter Planning

## Community

TakeMeter studies English-language posts and comments from **r/worldcup**, where supporters discuss teams, players, tactics, results, and the experience of watching the World Cup. The community is a good classification target because it mixes explanations and arguments with quick reactions, jokes, and unsupported claims. Distinguishing those modes can help readers find substantive discussion without treating popularity or agreement as quality.

## Labels

The final task uses two labels so that the distinction is clear enough to learn reliably from a small dataset.

### `substantive_discussion`

`substantive_discussion` is a judgment, prediction, or interpretation supported by a relevant football-related reason or by connected evidence such as tactics, statistics, match events, lineups, or historical comparisons.

- "France is more likely to win because its bench gives the coach more ways to change the match."
- "Spain played 120 minutes three days ago while Brazil finished in regulation, so Brazil should have the physical advantage late in the match."

### `casual_commentary`

`casual_commentary` is a bare or weakly supported take, emotion, celebration, frustration, mockery, meme, chant, or play-by-play comment that does not provide a relevant reason for its judgment.

- "England are frauds and will lose to the first good team."
- "GOOOOOAL! What a finish!"

Length, popularity, tone, and whether an opinion is ultimately correct do not determine the label.

## Hard Edge Cases

The genuine boundary is a short comment that appears to give a reason but does not clearly support its conclusion. I will label it `substantive_discussion` only when the text contains a relevant because-style rationale or connects an observable detail to its claim. A fact that is merely decorative remains `casual_commentary`; for example, "He has zero goals, so he has been useless" does not establish overall usefulness. Sarcasm is labeled by its recoverable meaning, while deleted, bot-generated, non-English, duplicate, link-only, pure information-request, and irrecoverably context-dependent comments are excluded.

For any case that causes genuine hesitation, the CSV notes record the competing interpretation and final decision. Repeated ambiguity triggers a guideline review, after which the same rule must be applied to earlier examples rather than only to new ones.

### Boundary Stress Test

| Post | Decision |
|---|---|
| "They will struggle because their midfield is too passive." | `substantive_discussion`: it gives a relevant tactical reason. |
| "Their midfield is terrible." | `casual_commentary`: it is a bare judgment. |
| "Germany had 70% possession, so they were obviously brilliant." | `casual_commentary`: possession alone is decorative and does not establish brilliance. |
| "Germany kept creating overloads on the left, which forced the fullback into two-on-one situations." | `substantive_discussion`: the observation is connected to the conclusion. |
| "My grandmother saves that!" | `casual_commentary`: it is comic frustration without an actual rationale. |
| "I would start the faster winger because this opponent leaves space behind its fullbacks." | `substantive_discussion`: it gives a relevant tactical rationale. |

## Data Collection Plan

I collected unauthenticated, publicly accessible r/worldcup posts and comments from old Reddit HTML pages during the 2026 World Cup. Each source topic contributes at most the post itself and its highest-ranked eligible human comment. No login, private content, or username was used or retained.

The final file is `takemeter_labeled_simple.csv`. It contains **320 examples: 160 per label**, drawn from **249 different source topics**. It includes 94 posts and 226 top comments, with no duplicate text and no more than two rows from one topic. The initial pool was extended from 220 to 350 source posts when clearer examples were needed; if a label had still been underrepresented after 200 reviewed examples, I would have targeted thread types likely to contain that label rather than lowering the annotation standard.

The notebook will perform a stratified 70/15/15 train/validation/test split. Model and prompt choices must be made without changing individual labels in response to test predictions.

## Evaluation Metrics

I will report accuracy, but **macro-F1** is the main metric because both labels must work well and a majority-class strategy should not look successful. Per-class precision, recall, and F1 will show whether the system misses substantive discussion or incorrectly promotes casual commentary. A confusion matrix and a complete error table will make the direction of mistakes visible.

For confidence quality, I will report reliability bins, expected calibration error, multiclass Brier score, and accuracy by confidence band. Temperature scaling will be fitted only on validation predictions and evaluated on the test set. On 40 blind, independently labeled examples, I will report percentage agreement, Cohen's kappa, disagreements, and adjudicated labels.

## Definition of Success

The experiment succeeds if the untouched test set reaches:

- accuracy and macro-F1 of at least **0.75**;
- F1 of at least **0.70 for both labels**;
- Cohen's kappa of at least **0.70** for the second-annotator subset; and
- calibrated expected calibration error no greater than **0.10**.

For real deployment, I would require macro-F1 of at least 0.80, both class F1 scores of at least 0.75, kappa of at least 0.75, and low-confidence predictions routed for human review. These thresholds are fixed in advance, so the final result can be judged objectively.

## AI Tool Plan

I used OpenAI Codex to check the label definitions for overlap and generate boundary cases. The stress test above exposed that the original four labels required two subjective distinctions from only a few hundred examples, so the final taxonomy combines supported analysis and reasoned opinions as `substantive_discussion`, and combines unsupported takes and reactions as `casual_commentary`.

Codex also organized the public candidate pool and proposed labels. Every selected example was then reviewed against the definitions, and genuine difficult cases were recorded in the notes column. This AI-assisted annotation must be disclosed in the final report. The second annotator's 40-item sheet will be blind and will not include proposed labels or notes.

## Stretch Feature Plans

These entries were written before implementing either stretch feature so that the methods and success rules are not chosen after seeing test results.

### Stretch Feature 1: Inter-annotator Reliability

**Pre-implementation entry (June 21, 2026).** A second annotator will independently label 40 examples sampled evenly across the two final labels. The sheet will contain only an anonymous item ID and text; it will not expose the existing label, AI proposal, confidence, notes, source popularity, or model prediction. I will preserve both original decisions before discussion, then calculate raw percentage agreement, Cohen's kappa, a two-by-two disagreement table, and disagreements by boundary type. Every disagreement will receive an adjudicated label and short rationale, but adjudication will not overwrite the two independent label columns.

Kappa is necessary because percentage agreement does not account for chance agreement. A kappa of at least 0.70 is the pilot target. If kappa is lower, the taxonomy is not reliable enough for deployment even if model accuracy is high; the definitions must be revised and a new blind subset annotated. The present report does not claim this feature as completed because no independent annotation file or reliability output was retained.

### Stretch Feature 2: Confidence Calibration

**Pre-implementation entry (June 21, 2026).** I will save the fine-tuned model's logits for every validation and test item. Raw softmax confidence will be evaluated with 10 reliability bins, expected calibration error, multiclass Brier score, and accuracy in low, medium, and high confidence bands. I will fit one positive temperature parameter using validation logits and labels only, then apply that fixed temperature once to test logits. Temperature scaling may change confidence values but must not change predicted classes.

The comparison will report raw versus calibrated ECE and Brier score on the same test examples, plus a reliability table or diagram. The pilot target is calibrated ECE no greater than 0.10 without worse Brier score. A confidence threshold for human review may be selected using validation data, never test outcomes. The present report does not claim calibration results because the required validation/test logits and atomic confidence export were not retained.

## Failure Analysis Plan

A failure-analysis script will create one row for every test prediction with its text, gold label, prediction, confidence, correctness, and source topic. It will summarize the confusion matrix, confidence bands, text length, question and sarcasm markers, evidence cues, and the highest-confidence errors; it will never use only hand-picked mistakes.

I will provide the complete wrong-prediction list to an AI tool and ask it to propose patterns involving decorative evidence, implicit reasoning, sarcasm, context dependence, and emotional claims. I will verify each proposed pattern against the original comments, count it using an explicit rule, search correct predictions for counterexamples, and reject patterns that cannot be reproduced. The final evaluation will include at least three concrete errors and a comparison between the fine-tuned and zero-shot systems.
