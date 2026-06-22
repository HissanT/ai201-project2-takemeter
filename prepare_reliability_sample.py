"""Create a blind, balanced 40-item sheet for a second annotator."""

import pandas as pd


LABELS = ["substantive_discussion", "casual_commentary"]

df = pd.read_csv("takemeter_labeled_simple.csv")
parts = [
    df[df["label"] == label].sample(n=20, random_state=2026)
    for label in LABELS
]
sample = pd.concat(parts).sample(frac=1, random_state=2026).reset_index(drop=True)
sample.insert(0, "item_id", [f"R{i:02d}" for i in range(1, 41)])

sample[["item_id", "text"]].assign(second_label="").to_csv(
    "reliability_blind.csv", index=False, encoding="utf-8-sig"
)
sample[["item_id", "label"]].rename(columns={"label": "first_label"}).to_csv(
    "reliability_key.csv", index=False, encoding="utf-8-sig"
)

print("Created reliability_blind.csv for the second annotator.")
print("Keep reliability_key.csv private until independent labeling is complete.")
