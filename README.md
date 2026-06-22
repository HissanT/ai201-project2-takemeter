# TakeMeter: r/worldcup Discourse Classification

TakeMeter classifies English-language r/worldcup posts and comments by whether they contribute a supported football-related point or function mainly as an unsupported take or reaction. The final task intentionally uses two labels: `substantive_discussion` and `casual_commentary`. This simpler boundary is more reproducible than the original four-way taxonomy and is suitable for a small pilot dataset.

## Community and Intended Use

r/worldcup is event-driven and mixes tactical explanations, statistical arguments, predictions, personal observations, jokes, celebrations, and unsupported claims in the same threads. That variation makes it useful for studying discourse quality. A community tool could use TakeMeter to help readers find substantive discussion, but it should not hide comments or make moderation decisions automatically: the classifier measures whether a relevant reason is present, not whether a position is correct or popular.

## Labels

### `substantive_discussion`

A judgment, prediction, or interpretation supported by a relevant football-related reason or connected evidence such as tactics, statistics, match events, lineups, or historical comparisons.

- "France is more likely to win because its bench gives the coach more ways to change the match."
- "Spain played 120 minutes three days ago while Brazil finished in regulation, so Brazil should have the physical advantage late in the match."

### `casual_commentary`

A bare or weakly supported take, emotion, celebration, frustration, mockery, meme, chant, or play-by-play comment without a relevant supporting reason.

- "England are frauds and will lose to the first good team."
- "GOOOOOAL! What a finish!"

The operational rule is: if a claim has a relevant reason, label it `substantive_discussion`; otherwise label it `casual_commentary`. Length, tone, popularity, and eventual correctness do not determine the label. Full boundary rules and examples are in [planning.md](planning.md).

## Data

The final dataset is [takemeter_labeled_simple.csv](takemeter_labeled_simple.csv). It contains 320 public r/worldcup examples, balanced at 160 per label.

| Property | Value |
|---|---:|
| Total examples | 320 |
| `substantive_discussion` | 160 |
| `casual_commentary` | 160 |
| Distinct source topics | 249 |
| Posts | 94 |
| Top comments | 226 |
| Maximum examples from one topic | 2 |
| Duplicate normalized texts | 0 |

Candidates came from unauthenticated, publicly accessible old Reddit HTML pages during the 2026 World Cup. Collection retained at most the post and highest-ranked eligible human comment from each source topic. Usernames were omitted. Deleted, removed, bot-generated, non-English, duplicate, link-only, administrative, pure information-request, and irrecoverably context-dependent items were excluded when identified.

The notebook used a stratified 70/15/15 split with random state 42: 224 training examples, 48 validation examples, and 48 test examples. Each test label had support 24. The test set was used only for final reporting, although the later manual audit found annotation concerns discussed below.

## Annotation Process

The first taxonomy separated analysis, reasoned opinions, unsupported takes, and reactions. Boundary testing and early evaluation showed that the analysis/reasoned and unsupported/reaction distinctions were too subjective for this dataset size. The final two labels merge those adjacent categories while preserving the main practical distinction: relevant support versus no relevant support.

An AI tool proposed initial labels and boundary cases. Every selected item was then reviewed against the written definitions, and five cases that remained difficult across the final two-label boundary have notes in the CSV. This is AI-assisted annotation, not independent human annotation. A second-annotator reliability score was not available for this report, so human reproducibility remains an open limitation.

### Difficult annotation decisions

1. **"Data is irrelevant, in the end all that matters is the score."** This could be casual dismissal, but "the score is what determines the result" is a relevant general rationale. I labeled it `substantive_discussion` while noting that its support is minimal.
2. **"This was my first world cup experience ... now I am obsessed!!!"** The personal history partially explains the reaction, but the post mainly expresses excitement and thanks rather than a football-related judgment. I labeled it `casual_commentary`.
3. **"This morning at Rice University ... Great food, keeping people hydrated and making a party atmosphere ..."** Although emotional, the post names concrete reasons for calling the experience incredible. I labeled it `substantive_discussion`; emotional tone does not erase relevant support.

## Models

### Fine-tuned model

I fine-tuned `distilbert-base-uncased` in Google Colab with Hugging Face Transformers and a two-class sequence-classification head. Text was truncated to 256 tokens. Training used:

| Setting | Value |
|---|---:|
| Epochs | 8 |
| Training batch size | 8 |
| Evaluation batch size | 8 |
| Learning rate | 1e-5 |
| Weight decay | 0.01 |
| Warmup ratio | 0.10 |
| Evaluation/save frequency | Every epoch |
| Best-model criterion | Validation accuracy |

Validation accuracy reached 0.854 at epochs 3 and 4. Training loss continued to decrease afterward while validation accuracy fluctuated between 0.792 and 0.812, which suggests that additional epochs were no longer improving generalization. Loading the best validation checkpoint limited the effect of that overfitting.

I reduced the usual BERT fine-tuning learning rate from 2e-5 to 1e-5 and the batch size from 16 to 8 to make updates less abrupt on a small dataset. I allowed up to eight epochs because of the smaller learning rate, but saved every epoch and loaded the checkpoint with the best validation accuracy rather than automatically using epoch 8.

### Zero-shot baseline

The baseline used Groq's `llama-3.3-70b-versatile` at temperature 0. Its prompt defined both labels, supplied one example for each, applied the relevant-reason decision rule, and required exactly one label as output. All 48 responses were parseable.

The classification prompt was:

```text
You classify English-language posts and comments from r/worldcup.

substantive_discussion: A judgment, prediction, or interpretation supported by
a relevant football-related reason or connected evidence.
Example: "France can win because its bench gives the coach more options."

casual_commentary: A bare or weakly supported take, emotion, celebration,
frustration, joke, meme, chant, or play-by-play without a relevant reason.
Example: "England are frauds."

If the text provides a relevant reason, choose substantive_discussion.
Otherwise choose casual_commentary.

Respond with only one exact label name and nothing else.
```

Each untouched test text was sent once as the user message. Responses were normalized to lowercase and accepted only when they matched a valid label; accuracy and per-class metrics were calculated over all 48 parseable responses.

## Reproduction

Set no credentials for dataset construction. The Groq baseline requires `GROQ_API_KEY` in Colab Secrets or an environment variable.

```bash
# Recollect the public candidate pool. Network access is required.
python collect_diverse_candidates.py

# Rebuild and validate the reviewed dataset.
python build_reviewed_dataset.py
```

In the notebook, use:

```python
CSV_PATH = "/content/takemeter_labeled_simple.csv"
LABEL_MAP = {
    "substantive_discussion": 0,
    "casual_commentary": 1,
}
```

The complete label map and zero-shot prompt are also preserved in [notebook_config.py](notebook_config.py).

## Evaluation Results

The fine-tuned model improved accuracy by 0.062 over the zero-shot baseline. It also improved macro-F1 from 0.74 to 0.81. Its weakest result was substantive-discussion recall: it recognized 17 of 24 substantive examples.

### Overall comparison

| Model | Accuracy | Macro precision | Macro recall | Macro F1 |
|---|---:|---:|---:|---:|
| Groq zero-shot baseline | 0.750 | 0.80 | 0.75 | 0.74 |
| Fine-tuned DistilBERT | **0.812** | **0.83** | **0.81** | **0.81** |

### Per-class metrics

| Model | Label | Precision | Recall | F1 | Support |
|---|---|---:|---:|---:|---:|
| Groq baseline | `substantive_discussion` | 0.93 | 0.54 | 0.68 | 24 |
| Groq baseline | `casual_commentary` | 0.68 | 0.96 | 0.79 | 24 |
| Fine-tuned DistilBERT | `substantive_discussion` | 0.89 | 0.71 | 0.79 | 24 |
| Fine-tuned DistilBERT | `casual_commentary` | 0.76 | 0.92 | 0.83 | 24 |

### Fine-tuned confusion matrix

Rows are gold labels and columns are predictions.

| Gold \ Predicted | `substantive_discussion` | `casual_commentary` |
|---|---:|---:|
| `substantive_discussion` | 17 | 7 |
| `casual_commentary` | 2 | 22 |

Seven of the nine errors went in the same direction: substantive posts were called casual. The model was too cautious about recognizing a supporting reason.

## AI-assisted Failure Analysis

I gave the notebook's printed error list to an AI tool and asked it to check for repeated label confusion, short posts, emotional wording, implied reasons, lists, questions, and inconsistent labels. It suggested three patterns: reasons were often implied instead of stated in a neat explanation, emotional posts were often called casual, and the mistakes looked shorter than the test set overall.

I rebuilt the random-state-42 test split and reread every printed error. The listed errors averaged 21 words, compared with 41 words for the whole test set, so length mattered somewhat. Still, several errors were 30-44 words, so "the model only fails on short posts" was too strong and I discarded it. Football vocabulary was not enough to explain the errors either. I also found questionable gold labels. For example, "Would love to see Scotland-Norway - must be a fantastic stadium experience" gives no supporting reason and fits `casual_commentary` better than its stored label. That is a labeling problem, not a clean model error.

The PDF's printed inspection cell lists 11 wrong examples, while its aggregate report and confusion counts imply nine errors. The aggregate metrics are internally consistent—39/48 correct—and are therefore used for all numeric reporting. The printed examples are used only for qualitative analysis. A future run should export one prediction table immediately after inference so metrics and examples cannot become stale across cell reruns.

### Three specific errors

1. **"Because China has to go through Japan, South Korea, Australia, Saudi Arabia to qualify. That ain't happening."** Gold: `substantive_discussion`; prediction: `casual_commentary` at 0.64 confidence. The prediction misses a concise list-based rationale: the named qualification opponents are the reason for the conclusion. The informal ending likely resembles unsupported banter, and the model appears to overweight that tone. This is primarily a data-distribution problem; training needs more short, informal substantive examples whose evidence is a comparison or list rather than a formal explanation.

2. **"People need to stop talking about Senegal like they are massive underdogs when in reality it's one of the best African teams of all time."** Gold: `substantive_discussion`; prediction: `casual_commentary` at 0.56 confidence. The second clause supplies a relevant historical-strength rationale, although it does not cite statistics. The model seems to require more concrete evidence than the final definition does. More training examples with valid general rationales would clarify that substantiation does not require numbers.

3. **"This morning at Rice University in Houston ... Great food, keeping people hydrated and making a party atmosphere ..."** Gold: `substantive_discussion`; prediction: `casual_commentary` at 0.57 confidence. Food, hydration, and atmosphere support the judgment that the event was an incredible experience. The positive, thankful tone resembles reaction posts, so the model follows emotional style rather than the relationship between observations and conclusion. Training should include more emotional comments that remain substantive because they explain the reaction.

A fourth case—"Spain isn't even playing good, Saudi's are just bad"—was initially surfaced as a model error, but manual review did not retain it as strong evidence. It contains two bare judgments and no concrete explanation, so the gold substantive label is questionable under the final rule. This is exactly the kind of correction the independent verification step was intended to catch.

## Sample Classifications

The notebook PDF retained confidence values only for its printed error inspection, not for correct predictions. The following rows therefore document available fine-tuned outputs without inventing missing confidence values.

To produce the final 3–5-row table with at least one formally correct example, run [manual_classification_cell.py](manual_classification_cell.py) after the notebook's fine-tuned inference cell. It classifies five fixed test rows, displays the gold and predicted labels with exact softmax confidence, marks correctness, and saves `manual_sample_classifications.csv`. The final README table should be refreshed from that CSV rather than estimating a missing confidence.

| Post | Gold label | Predicted label | Confidence | Review |
|---|---|---|---:|---|
| "Because China has to go through Japan, South Korea, Australia, Saudi Arabia to qualify. That ain't happening." | `substantive_discussion` | `casual_commentary` | 0.64 | Incorrect; the opponent list is a relevant rationale. |
| "People need to stop talking about Senegal like they are massive underdogs when in reality it's one of the best African teams of all time." | `substantive_discussion` | `casual_commentary` | 0.56 | Incorrect; the second clause supports the first. |
| "This was my first world cup experience and it was truly amazing ... now I am obsessed!!!" | `casual_commentary` | `substantive_discussion` | 0.52 | Formally incorrect, but manual review found the boundary ambiguous because the personal history partially explains the reaction. |
| "Spain isn't even playing good, Saudi's are just bad." | `substantive_discussion` | `casual_commentary` | 0.64 | Formally incorrect; the model's choice is reasonable because both clauses are unsupported judgments. |
| "Both 0-0 matches had a veteran goalkeeper that played at an MVP level." | `substantive_discussion` | `casual_commentary` | 0.61 | Incorrect under the stored label; the implied connection is easy to miss. |

The Spain/Saudi prediction is reasonable even though it disagrees with the stored gold label: under the final definition, calling both teams bad without explaining why fits casual commentary. A clean export of all probabilities is still required to add a formally correct example with its exact confidence score.

## What the Model Captured Versus What Was Intended

I wanted the model to ask one basic question: does the post give a relevant reason for its claim? It learned that distinction fairly well, reaching 0.81 macro-F1, but it also relied on writing style. Long, formal posts with statistics were easy. Short, informal, or emotional posts were more likely to be called casual even when they contained a real reason.

The model sometimes treated length and formality as signs of quality instead of checking whether the reason supported the claim. It also missed that a general reason can count even without statistics. Reviewing the errors also showed that a few stored labels did not follow the final rule consistently.

## Definition of Success

The preregistered pilot criteria were accuracy and macro-F1 of at least 0.75 and F1 of at least 0.70 for both labels. The fine-tuned model met all three performance thresholds: accuracy 0.812, macro-F1 0.81, substantive F1 0.79, and casual F1 0.83. It also exceeded the zero-shot baseline on accuracy and macro-F1. The project cannot claim that it met the planned reliability or calibration thresholds because no second-annotator or calibration results were retained.

## Stretch Features

### Inter-annotator reliability

This bonus is prepared but not yet complete. Run `python prepare_reliability_sample.py`, give only `reliability_blind.csv` to a second person, and ask them to fill all 40 `second_label` cells without seeing the key. After they return it, run `python score_reliability.py`. The script reports percentage agreement, Cohen's kappa, a disagreement matrix, and a CSV of the exact disagreements to discuss here. I do not report a made-up agreement score before a second person completes that work.

### Confidence calibration

This bonus is also prepared but not yet complete. After the fine-tuned inference cell in Colab, upload and run `calibration_cell.py`. It saves ten-bin accuracy versus confidence, expected calibration error, and multiclass Brier score. The final report should state whether accuracy generally rises across confidence bins and whether average confidence is close to observed accuracy. The current PDF did not retain every prediction's confidence, so no calibration result is claimed yet.

## Limitations and Next Steps

- The dataset contains only 320 examples from one tournament period and one English-language subreddit.
- AI-assisted annotation was reviewed but not independently duplicated, and the audit found remaining inconsistencies.
- The notebook used a row-level stratified split. Although source contribution was capped, a grouped source-topic split would provide a stricter generalization test.
- The error list and aggregate metrics became inconsistent after notebook cell reruns; future evaluation should export predictions, metrics, and confidences atomically.
- The confidence scores have not been calibrated, so they should not be interpreted as probabilities of correctness.
- Truncation at 256 tokens may remove evidence from long posts.

The next iteration should adjudicate the questionable gold labels without using model predictions as the deciding rule, collect more short and emotional substantive examples, split by source topic, select checkpoints by validation macro-F1 rather than accuracy, and export a complete prediction table. It should then rerun the untouched evaluation with a newly locked test set.

## Specification Reflection

The specification helped by requiring explicit label definitions and boundary cases before full evaluation. That requirement exposed that the original four-way taxonomy depended on distinctions that were difficult to apply consistently, leading to a clearer operational rule.

The implementation diverged from the initial four-class plan by using two labels. The assignment permits two to four labels, and the merge was made because a 320-example dataset could more reliably learn supported versus unsupported discourse than evidential-depth sublevels. The implementation also used the notebook's stratified row split instead of the initially proposed thread-grouped split because the provided workflow performed splitting automatically; this is documented as a limitation.

## AI Usage

1. **Definition stress testing:** I directed OpenAI Codex to inspect the four original labels for overlap and generate boundary examples. It identified recurring ambiguity between analysis and reasoned opinion and between unsupported takes and reactions. I accepted the overlap finding but replaced the proposed fine-grained fixes with a two-label taxonomy that was easier to apply consistently.

2. **Annotation assistance:** Codex organized public candidates and proposed initial labels. I reviewed every selected example against the definitions, removed ineligible or context-dependent items, corrected proposed labels, and retained notes for five cases that remained difficult. The final CSV is therefore AI-assisted and manually reviewed, not independently human-labeled.

3. **Failure-pattern discovery:** I asked an AI tool to inspect the complete printed wrong-prediction list for length, tone, implicit reasoning, and directional confusion. It suggested that shortness and emotional language were dominant. Manual verification narrowed that conclusion: the printed errors were shorter on average, but not uniformly short, and several supposed model errors were better explained by inconsistent gold labels. Those discarded or corrected hypotheses are included above rather than silently omitted.

## Repository Files

- [planning.md](planning.md): taxonomy, boundary rules, collection plan, success criteria, and AI plan.
- [takemeter_labeled_simple.csv](takemeter_labeled_simple.csv): final labeled dataset.
- [collect_diverse_candidates.py](collect_diverse_candidates.py): public candidate collection.
- [build_reviewed_dataset.py](build_reviewed_dataset.py): reviewed selection and dataset validation.
- [notebook_config.py](notebook_config.py): final label map and Groq prompt.
- [evaluation_export_cell.py](evaluation_export_cell.py): atomic evaluation export cell for future runs.
- [manual_classification_cell.py](manual_classification_cell.py): reproducible manual sample-classification cell.
- [prepare_reliability_sample.py](prepare_reliability_sample.py): creates the blind 40-item reliability sheet.
- [score_reliability.py](score_reliability.py): calculates agreement and Cohen's kappa after the second annotation.
- [calibration_cell.py](calibration_cell.py): measures whether higher confidence corresponds to higher test accuracy.
