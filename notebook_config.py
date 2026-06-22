"""Values to paste into the matching notebook cells."""

CSV_PATH = "/content/takemeter_labeled_simple.csv"

LABEL_MAP = {
    "substantive_discussion": 0,
    "casual_commentary": 1,
}

ID_TO_LABEL = {value: key for key, value in LABEL_MAP.items()}
NUM_LABELS = len(LABEL_MAP)

# Run this immediately after pd.read_csv(CSV_PATH). It reports configuration
# mistakes before the notebook reaches train_test_split.
def validate_and_map_labels(df):
    required = {"text", "label"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"CSV is missing required columns: {sorted(missing)}")

    unknown = set(df["label"].dropna().unique()) - set(LABEL_MAP)
    if unknown:
        raise ValueError(
            f"CSV labels do not match LABEL_MAP: {sorted(unknown)}. "
            f"Expected only: {sorted(LABEL_MAP)}"
        )

    df = df.dropna(subset=["text", "label"]).copy()
    df["label_id"] = df["label"].map(LABEL_MAP).astype(int)
    if df.empty:
        raise ValueError("No usable examples were loaded from the CSV.")
    return df

SYSTEM_PROMPT = """
You classify English posts and comments from r/worldcup.

substantive_discussion: A judgment, prediction, or interpretation supported by
a relevant football-related reason or connected evidence.
Example: "France can win because its bench gives the coach more options."

casual_commentary: A bare or weakly supported take, emotion, celebration,
frustration, joke, meme, chant, or play-by-play without a relevant reason.
Example: "England are frauds."

If the text gives a relevant reason, choose substantive_discussion.
Otherwise choose casual_commentary.

Output exactly one label and nothing else:
substantive_discussion
casual_commentary
""".strip()
