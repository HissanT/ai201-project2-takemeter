"""Paste this cell after both model evaluations in Colab, then run it."""

import json
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

label_names = [ID_TO_LABEL[i] for i in range(NUM_LABELS)]

# The starter notebook stores only parseable Groq results in `valid`.
# Each item is expected to contain its test index and predicted label ID.
if "bl_pred_ids" not in globals() or "bl_true_ids" not in globals():
    if "valid" not in globals():
        raise RuntimeError("Run the Groq baseline evaluation before this cell.")

    # Support the common starter-notebook representation: a dataframe or a
    # list of dictionaries. If your notebook already created the arrays, this
    # block is skipped.
    valid_df = pd.DataFrame(valid)
    pred_column = next(
        (c for c in ["pred_id", "prediction_id", "label_id"] if c in valid_df),
        None,
    )
    true_column = next(
        (c for c in ["true_id", "gold_id", "true_label_id"] if c in valid_df),
        None,
    )
    if pred_column is None or true_column is None:
        raise RuntimeError(
            "Could not infer baseline columns. Use the bl_true_ids and "
            "bl_pred_ids arrays already used by classification_report()."
        )
    bl_pred_ids = valid_df[pred_column].to_numpy(dtype=int)
    bl_true_ids = valid_df[true_column].to_numpy(dtype=int)

required = ["test_df", "ft_true_ids", "ft_pred_ids", "ft_probs"]
missing = [name for name in required if name not in globals()]
if missing:
    raise RuntimeError(f"Run fine-tuned inference first; missing variables: {missing}")

ft_true_ids = np.asarray(ft_true_ids)
ft_pred_ids = np.asarray(ft_pred_ids)
ft_probs = np.asarray(ft_probs)
bl_true_ids = np.asarray(bl_true_ids)
bl_pred_ids = np.asarray(bl_pred_ids)

summary = {
    "labels": label_names,
    "test_size": int(len(ft_true_ids)),
    "baseline_parseable": int(len(bl_true_ids)),
    "baseline_accuracy": float(accuracy_score(bl_true_ids, bl_pred_ids)),
    "finetuned_accuracy": float(accuracy_score(ft_true_ids, ft_pred_ids)),
    "baseline_report": classification_report(
        bl_true_ids,
        bl_pred_ids,
        labels=list(range(NUM_LABELS)),
        target_names=label_names,
        output_dict=True,
        zero_division=0,
    ),
    "finetuned_report": classification_report(
        ft_true_ids,
        ft_pred_ids,
        labels=list(range(NUM_LABELS)),
        target_names=label_names,
        output_dict=True,
        zero_division=0,
    ),
    "finetuned_confusion_matrix": confusion_matrix(
        ft_true_ids, ft_pred_ids, labels=list(range(NUM_LABELS))
    ).tolist(),
}

prediction_rows = []
for position, (_, row) in enumerate(test_df.reset_index(drop=False).iterrows()):
    predicted_id = int(ft_pred_ids[position])
    gold_id = int(ft_true_ids[position])
    prediction_rows.append(
        {
            "test_position": position,
            "original_index": row["index"],
            "text": row["text"],
            "gold_label": ID_TO_LABEL[gold_id],
            "predicted_label": ID_TO_LABEL[predicted_id],
            "confidence": float(ft_probs[position, predicted_id]),
            "correct": gold_id == predicted_id,
            "source_url": row.get("source_url", ""),
            "post_id": row.get("post_id", ""),
        }
    )

with open("evaluation_details.json", "w", encoding="utf-8") as handle:
    json.dump(summary, handle, indent=2)

pd.DataFrame(prediction_rows).to_csv(
    "test_predictions.csv", index=False, encoding="utf-8-sig"
)

print("Created evaluation_details.json and test_predictions.csv")
print(json.dumps(summary, indent=2))
