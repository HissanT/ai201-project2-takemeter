"""Paste after fine-tuned test inference in Colab to analyze confidence."""

import json
import numpy as np
import pandas as pd


probs = np.asarray(ft_probs, dtype=float)
true_ids = np.asarray(ft_true_ids, dtype=int)
pred_ids = probs.argmax(axis=1)
confidence = probs.max(axis=1)
correct = pred_ids == true_ids

# Ten equal-width bins for expected calibration error.
edges = np.linspace(0.0, 1.0, 11)
rows = []
ece = 0.0
for lower, upper in zip(edges[:-1], edges[1:]):
    include_right = upper == 1.0
    mask = (confidence >= lower) & (
        (confidence <= upper) if include_right else (confidence < upper)
    )
    if not mask.any():
        continue
    bin_accuracy = float(correct[mask].mean())
    mean_confidence = float(confidence[mask].mean())
    count = int(mask.sum())
    ece += count / len(confidence) * abs(bin_accuracy - mean_confidence)
    rows.append(
        {
            "confidence_range": f"{lower:.1f}-{upper:.1f}",
            "count": count,
            "mean_confidence": mean_confidence,
            "accuracy": bin_accuracy,
        }
    )

one_hot = np.eye(NUM_LABELS)[true_ids]
brier = float(np.mean(np.sum((probs - one_hot) ** 2, axis=1)))
bins = pd.DataFrame(rows)
bins.to_csv("calibration_bins.csv", index=False)

results = {
    "n": int(len(true_ids)),
    "accuracy": float(correct.mean()),
    "mean_confidence": float(confidence.mean()),
    "expected_calibration_error": float(ece),
    "multiclass_brier_score": brier,
}
with open("calibration_results.json", "w", encoding="utf-8") as handle:
    json.dump(results, handle, indent=2)

print(json.dumps(results, indent=2))
display(bins)
print("Higher-confidence predictions are better calibrated only if bin accuracy")
print("generally rises with mean confidence and the two values stay close.")
