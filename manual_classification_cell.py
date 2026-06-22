"""Paste this cell after fine-tuned inference in Colab and run it."""

import pandas as pd
import torch


def classify_finetuned(text):
    trained_model = trainer.model
    trained_model.eval()
    encoded = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=256,
    )
    encoded = {key: value.to(trained_model.device) for key, value in encoded.items()}

    with torch.no_grad():
        logits = trained_model(**encoded).logits
        probabilities = torch.softmax(logits, dim=-1)[0]

    predicted_id = int(torch.argmax(probabilities).item())
    return ID_TO_LABEL[predicted_id], float(probabilities[predicted_id].item())


# These positions deliberately include clear examples and previously difficult
# cases. Change the numbers to classify other rows from test_df.
sample_positions = [27, 46, 30, 21, 28]

rows = []
for position in sample_positions:
    example = test_df.iloc[position]
    predicted_label, confidence = classify_finetuned(example["text"])
    gold_label = example["label"]
    rows.append(
        {
            "test_position": position,
            "post": example["text"],
            "gold_label": gold_label,
            "predicted_label": predicted_label,
            "confidence": round(confidence, 3),
            "correct": predicted_label == gold_label,
        }
    )

sample_results = pd.DataFrame(rows)
display(sample_results)
sample_results.to_csv("manual_sample_classifications.csv", index=False)
print("Saved manual_sample_classifications.csv")

# To classify text you type yourself, uncomment and edit this:
# my_text = "France can win because its bench gives the coach more options."
# label, confidence = classify_finetuned(my_text)
# print({"text": my_text, "predicted_label": label, "confidence": confidence})
