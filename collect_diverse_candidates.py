"""Collect diverse, public r/worldcup candidates without authentication.

For each source post, retain only the post itself and the highest-ranked eligible
human comment. Labels are deliberately not assigned during collection.
"""

from __future__ import annotations

import csv
import re
import time
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


BASE = "https://old.reddit.com"
START = f"{BASE}/r/worldcup/new/"
USER_AGENT = "TakeMeterResearch/1.0 (public coursework dataset)"
OUTPUT = Path("diverse_candidates.csv")
TARGET_POSTS = 350
REQUEST_DELAY_SECONDS = 1.25
MAX_RETRIES = 6


def clean_text(value: str) -> str:
    return " ".join(value.split())


def fetch(session: requests.Session, url: str) -> BeautifulSoup:
    for attempt in range(MAX_RETRIES):
        response = session.get(url, timeout=30)
        if response.status_code != 429:
            response.raise_for_status()
            time.sleep(REQUEST_DELAY_SECONDS)
            return BeautifulSoup(response.text, "html.parser")
        wait = int(response.headers.get("Retry-After", 20 * (attempt + 1)))
        print(f"Rate limited; waiting {wait}s before retry {attempt + 1}/{MAX_RETRIES}")
        time.sleep(wait)
    response.raise_for_status()
    raise AssertionError("unreachable")


def listing_posts(session: requests.Session) -> list[dict[str, str]]:
    posts: list[dict[str, str]] = []
    seen: set[str] = set()
    url: str | None = START

    while url and len(posts) < TARGET_POSTS:
        soup = fetch(session, url)
        for thing in soup.select(".thing.link"):
            post_id = (thing.get("data-fullname") or "").removeprefix("t3_")
            comments = thing.select_one("a.comments")
            if not post_id or post_id in seen or comments is None:
                continue
            permalink = urljoin(BASE, comments.get("href", ""))
            if "/r/worldcup/comments/" not in permalink:
                continue
            seen.add(post_id)
            posts.append({"post_id": post_id, "source_url": permalink})
            if len(posts) >= TARGET_POSTS:
                break

        next_link = soup.select_one("span.next-button a")
        url = urljoin(BASE, next_link.get("href")) if next_link else None

    return posts


def parse_score(comment) -> int:
    score = comment.select_one(":scope > .entry .score.unvoted")
    if score is None:
        return -1
    raw = score.get("title") or score.get_text(" ", strip=True)
    match = re.search(r"-?\d+", raw.replace(",", ""))
    return int(match.group()) if match else -1


def parse_thread(
    session: requests.Session, post_id: str, source_url: str
) -> list[dict[str, str | int]]:
    soup = fetch(session, f"{source_url}?sort=top&limit=500")
    post = soup.select_one("#siteTable .thing.link")
    if post is None:
        return []

    title_node = post.select_one("a.title")
    if title_node is None:
        return []
    title = clean_text(title_node.get_text(" ", strip=True))
    body_node = post.select_one(":scope > .entry .usertext-body .md")
    body = clean_text(body_node.get_text(" ", strip=True)) if body_node else ""
    post_text = f"{title} {body}" if body and body.casefold() not in title.casefold() else title

    rows: list[dict[str, str | int]] = [
        {
            "text": post_text,
            "post_id": post_id,
            "item_type": "post",
            "reddit_id": post_id,
            "source_url": source_url,
            "score": -1,
        }
    ]

    candidates = []
    for order, comment in enumerate(soup.select(".commentarea .thing.comment")):
        author = comment.select_one(":scope > .entry .tagline .author")
        author_text = author.get_text(strip=True).casefold() if author else ""
        if author_text.endswith("bot") or author_text in {"automoderator", "remindmebot"}:
            continue
        body_node = comment.select_one(
            ":scope > .entry > .usertext .usertext-body .md"
        )
        if body_node is None:
            continue
        text = clean_text(body_node.get_text(" ", strip=True))
        reddit_id = (comment.get("data-fullname") or "").removeprefix("t1_")
        if not reddit_id or text in {"", "[deleted]", "[removed]"}:
            continue
        candidates.append((parse_score(comment), -order, reddit_id, text))

    if candidates:
        score, _, reddit_id, text = max(candidates)
        rows.append(
            {
                "text": text,
                "post_id": post_id,
                "item_type": "top_comment",
                "reddit_id": reddit_id,
                "source_url": source_url,
                "score": score,
            }
        )
    return rows


def main() -> None:
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    posts = listing_posts(session)
    print(f"Found {len(posts)} source posts")

    rows: list[dict[str, str | int]] = []
    completed: set[str] = set()
    if OUTPUT.exists():
        with OUTPUT.open(encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        completed = {str(row["post_id"]) for row in rows}
        print(f"Resuming with {len(rows)} candidates from {len(completed)} posts")

    for index, post in enumerate(posts, start=1):
        if post["post_id"] in completed:
            continue
        try:
            rows.extend(parse_thread(session, post["post_id"], post["source_url"]))
        except requests.RequestException as exc:
            print(f"Skipped {post['post_id']}: {exc}")
        if index % 25 == 0:
            print(f"Fetched {index}/{len(posts)} posts")

    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "text",
                "post_id",
                "item_type",
                "reddit_id",
                "source_url",
                "score",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} candidates from {len(posts)} source posts to {OUTPUT}")


if __name__ == "__main__":
    main()
