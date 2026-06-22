"""Score the completed blind reliability sheet."""

import json
import pandas as pd
from sklearn.metrics import cohen_kappa_score, confusion_matrix


LABELS = ["substantive_discussion", "casual_commentary"]
blind = pd.read_csv("reliability_blind.csv")
key = pd.read_csv("reliability_key.csv")

if len(blind) < 30:
    raise ValueError("Reliability requires at least 30 independently labeled rows.")
if blind["second_label"].isna().any() or blind["second_label"].eq("").any():
    raise ValueError("The second annotator must label every row in second_label.")
unknown = set(blind["second_label"]) - set(LABELS)
if unknown:
    raise ValueError(f"Unknown second-annotator labels: {sorted(unknown)}")

scored = key.merge(blind, on="item_id", validate="one_to_one")
agreement = float((scored["first_label"] == scored["second_label"]).mean())
kappa = float(cohen_kappa_score(scored["first_label"], scored["second_label"]))
matrix = confusion_matrix(
    scored["first_label"], scored["second_label"], labels=LABELS
).tolist()

disagreements = scored[scored["first_label"] != scored["second_label"]].copy()
disagreements.to_csv("reliability_disagreements.csv", index=False)

results = {
    "n": len(scored),
    "agreement": agreement,
    "cohen_kappa": kappa,
    "labels": LABELS,
    "confusion_matrix": matrix,
    "disagreement_count": len(disagreements),
}
with open("reliability_results.json", "w", encoding="utf-8") as handle:
    json.dump(results, handle, indent=2)

print(json.dumps(results, indent=2))
print("Review reliability_disagreements.csv and write why each boundary differed.")
