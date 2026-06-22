"""Build the manually reviewed, topic-diverse TakeMeter dataset.

Each integer below is a row in diverse_candidates.csv that was read and reviewed
against planning.md. The collector supplies no more than a post and its highest-
ranked eligible comment for any source topic.
"""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


INPUT = Path("diverse_candidates.csv")
OUTPUT = Path("takemeter_labeled_simple.csv")

LABEL_GROUPS = {
    "analysis": "substantive_discussion",
    "reasoned_opinion": "substantive_discussion",
    "unsupported_take": "casual_commentary",
    "reaction_banter": "casual_commentary",
}

SELECTIONS = {
    "analysis": [
        3, 6, 12, 13, 14, 20, 27, 29, 31, 51, 58, 66, 68, 72, 76,
        78, 87, 88, 99, 100, 111, 112, 128, 131, 136, 144, 148, 150,
        173, 183, 189, 194, 204, 206, 209, 214, 233, 234, 235, 247,
        258, 263, 274, 291, 293, 304, 308, 315, 320, 321, 323, 325,
        327, 334, 341, 357, 367, 384, 387, 391,
        436, 437, 442, 448, 452, 457, 463, 467, 474, 494, 505, 513,
        530, 535, 550, 560, 561, 571, 584, 615,
    ],
    "reasoned_opinion": [
        7, 11, 19, 24, 26, 28, 30, 44, 45, 50, 52, 56, 59, 60, 74,
        80, 84, 94, 102, 105, 110, 115, 124, 127, 129, 135, 140, 141,
        145, 146, 163, 177, 181, 191, 195, 215, 229, 241, 251, 253,
        255, 267, 300, 302, 313, 316, 318, 322, 326, 335, 340, 343,
        351, 353, 359, 389, 418, 420, 422, 187,
        447, 459, 482, 492, 506, 523, 529, 531, 539, 555, 588, 594,
        600, 612, 628, 641, 656, 670, 674, 683,
    ],
    "unsupported_take": [
        0, 2, 8, 9, 10, 18, 34, 35, 42, 46, 49, 54, 62, 67, 82,
        90, 92, 98, 103, 142, 143, 147, 155, 158, 161, 175, 179, 197,
        211, 219, 220, 225, 227, 232, 242, 249, 250, 269, 278, 298,
        307, 310, 314, 319, 330, 331, 332, 344, 346, 350, 352, 354,
        358, 363, 373, 396, 397, 400, 416, 423,
        444, 451, 460, 461, 465, 488, 519, 549, 551, 580, 582, 598,
        601, 608, 618, 638, 649, 666, 682, 685,
    ],
    "reaction_banter": [
        16, 22, 36, 37, 39, 40, 61, 63, 64, 70, 77, 79, 81, 86, 96,
        104, 109, 114, 116, 118, 126, 130, 134, 152, 156, 169, 170,
        171, 193, 199, 201, 205, 207, 218, 237, 239, 245, 257, 259,
        261, 265, 271, 273, 275, 280, 282, 289, 295, 297, 306, 324,
        329, 333, 345, 355, 364, 365, 369, 371, 425,
        432, 438, 470, 472, 473, 476, 477, 480, 484, 498, 502, 511,
        515, 521, 525, 527, 557, 563, 576, 610,
    ],
}

DIFFICULT_NOTES = {
    7: "Paused between reasoned_opinion and unsupported_take; it gives a relevant general principle—that only the score ultimately determines the result—even though it dismisses richer evidence.",
    18: "The transitive comparison is logically insufficient evidence, so the substantive implied claim is unsupported_take despite the joking delivery.",
    19: "The post gives a general rationale about incentives and player pressure but no concrete match evidence, so reasoned_opinion rather than analysis.",
    28: "The proposed seeding principle has a relevant rationale but relies on a hypothetical rather than observed tournament evidence, so reasoned_opinion.",
    35: "The headline is primarily an unevidenced evaluation of a shared parent-child moment, so unsupported_take rather than reaction_banter.",
    37: "The comment primarily expresses excitement and gratitude about a first World Cup experience, so reaction_banter rather than reasoned_opinion.",
    46: "The comment implies that knockout matches are stronger, but supplies no meaningful support for dismissing the group stage, so unsupported_take.",
    50: "The argument for attending a child's birth is logically relevant but general rather than evidence-based, so reasoned_opinion.",
    59: "The prediction is supported by broad references to tactics, training, and a long-term plan, not concrete results or events, so reasoned_opinion.",
    67: "Salary, treatment, and public hope do not demonstrate poor play; the supporting details are decorative, so unsupported_take.",
    84: "Kits, quick counterattacks, and fan support explain the preference but remain general observations, so reasoned_opinion.",
    96: "The goalkeeper's quoted 'never again' line is humorous celebration of a turnaround, so reaction_banter rather than analysis.",
    105: "Food, hydration, and the party atmosphere provide a relevant rationale for calling the experience incredible, so reasoned_opinion.",
    111: "Named teams that secured first place after two matches are concrete evidence for the tiebreaker criticism, so analysis.",
    116: "The Vozinha comparison is primarily a joke about an unrealistically high standard, so reaction_banter.",
    135: "The teammates' support and shared recovery experience provide a relevant general rationale for calling the reunion touching, so reasoned_opinion.",
    140: "The historical explanation is causally relevant but broad and uncited, so reasoned_opinion rather than analysis.",
    145: "The Vini reference motivates the rule preference, but the post supplies no recoverable details of that event; the usable rationale is general, so reasoned_opinion.",
    181: "The direct-opponent principle is a relevant general rationale illustrated hypothetically, so reasoned_opinion.",
    187: "The approval of Scottish fans is supported by the general rationale that they voiced opposition to the player, so reasoned_opinion.",
    219: "The post makes a recoverable claim that anthem booing is normalized among England fans but offers no rationale, so unsupported_take.",
    235: "The Qatar alcohol restriction is a specific historical comparison supporting the claim about fan experience, so analysis.",
    247: "The recurring frequency of similar fouls is connected to the conclusion that the injury was accidental, so analysis.",
    278: "Calling the supporters hooligans is a contestable judgment without any rationale, so unsupported_take rather than reaction_banter.",
    313: "The team-versus-individual scoring distinction supplies a relevant general rationale, so reasoned_opinion rather than unsupported_take.",
    315: "Capacity crowds, named star performances, and match characteristics are specific evidence connected to the 'best ever' judgment, so analysis.",
    373: "The rhetorical joke still contains a contestable judgment about England's style, so unsupported_take rather than reaction_banter.",
    397: "The claim that European teams are underestimating African opponents supplies no examples or meaningful rationale, so unsupported_take.",
    416: "The observable offside-positioning claim implies a football judgment, but does not explain or substantiate it further, so unsupported_take.",
    422: "The smaller nations' opportunity to participate supplies a relevant value-based rationale without detailed evidence, so reasoned_opinion.",
    425: "The comment primarily expresses an emotional response and support for the player, so reaction_banter.",
}

# Only cases that remain ambiguous across the final two-label boundary are
# exposed in the final CSV. The detailed four-way audit above is retained as
# annotation provenance.
FINAL_DIFFICULT_NOTES = {
    7: "The comment dismisses richer evidence but still gives a relevant score-based rationale, so it is substantive_discussion.",
    37: "The comment mainly expresses excitement and gratitude, so it is casual_commentary despite mentioning a first World Cup experience.",
    105: "Food, hydration, and the party atmosphere give relevant reasons for the positive judgment, so it is substantive_discussion.",
    187: "The fans' stated opposition to the player provides a relevant reason for approving of them, so it is substantive_discussion.",
    425: "The comment primarily expresses emotion and support for the player without a relevant rationale, so it is casual_commentary.",
}


def main() -> None:
    with INPUT.open(encoding="utf-8-sig", newline="") as handle:
        candidates = list(csv.DictReader(handle))

    rows = []
    selected_indices = []
    for label, indices in SELECTIONS.items():
        assert len(indices) == 80, (label, len(indices))
        for index in indices:
            candidate = candidates[index]
            selected_indices.append(index)
            rows.append(
                {
                    "text": candidate["text"],
                    "label": LABEL_GROUPS[label],
                    "notes": FINAL_DIFFICULT_NOTES.get(index, ""),
                    "reddit_id": candidate["reddit_id"],
                    "source_url": candidate["source_url"],
                    "post_id": candidate["post_id"],
                    "item_type": candidate["item_type"],
                }
            )

    label_counts = Counter(row["label"] for row in rows)
    topic_counts = Counter(row["post_id"] for row in rows)
    item_counts = Counter(row["item_type"] for row in rows)
    normalized_text = {" ".join(row["text"].casefold().split()) for row in rows}

    assert len(rows) == 320
    assert len(selected_indices) == len(set(selected_indices))
    assert label_counts == Counter(
        {"substantive_discussion": 160, "casual_commentary": 160}
    )
    assert max(topic_counts.values()) <= 2
    assert len(topic_counts) >= 120
    assert len(normalized_text) == len(rows)
    assert all(row["text"].strip() for row in rows)

    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "text",
                "label",
                "notes",
                "reddit_id",
                "source_url",
                "post_id",
                "item_type",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} reviewed rows from {len(topic_counts)} topics")
    print("Labels:", dict(sorted(label_counts.items())))
    print("Item types:", dict(sorted(item_counts.items())))
    print("Maximum rows from one topic:", max(topic_counts.values()))


if __name__ == "__main__":
    main()
