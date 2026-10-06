"""Check the articles, and publish them where the portal reads them.

    python -m marketopinion check              read every article; say what is wrong with any
    python -m marketopinion publish            ...and write them to the portal's Firestore
    python -m marketopinion publish --to DIR   ...or to the folder a local portal reads

The portal reads two things: one document per article ("opinion/<slug>") and one with the cards
of all of them ("opinion_state/front"), so its list is a single read. An article that is taken
out of articles/ leaves the list; its own document is left where it was.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from .articles import Invalid, card, load_all

ROOT = Path(__file__).resolve().parents[2]
DATABASE = "market-hub"  # the portal's own Firestore database


def to_folder(articles: list[dict], front: dict, folder: Path) -> None:
    (folder / "articles").mkdir(parents=True, exist_ok=True)
    for a in articles:
        (folder / "articles" / f"{a['slug']}.json").write_text(json.dumps(a), encoding="utf-8")
    (folder / "front.json").write_text(json.dumps(front), encoding="utf-8")


def to_firestore(articles: list[dict], front: dict) -> None:
    from google.cloud import firestore

    project = os.environ.get("GOOGLE_CLOUD_PROJECT", "").strip()
    if not project:
        raise SystemExit("error: no Google Cloud project. Run it with `make publish`, or set GOOGLE_CLOUD_PROJECT.")
    client = firestore.Client(project=project, database=DATABASE)
    batch = client.batch()
    for a in articles:
        batch.set(client.collection("opinion").document(a["slug"]), a)
    # The front goes last and in the same batch: the list never names an article that is not there.
    batch.set(client.collection("opinion_state").document("front"), front)
    batch.commit()


def main() -> int:
    parser = argparse.ArgumentParser(prog="marketopinion")
    parser.add_argument("action", choices=["check", "publish"])
    parser.add_argument("--to", type=Path, help="write to this folder instead of the portal's database")
    args = parser.parse_args()
    try:
        articles = load_all(ROOT / "articles")
    except Invalid as exc:
        print(exc, file=sys.stderr)
        return 1
    for a in articles:
        print(f"  {a['published_utc'][:16]}  {a['kind']:<12} {a['minutes']} min  {a['title']}")
    print(f"{len(articles)} articles, all fit to publish.")
    if args.action == "check":
        return 0
    front = {"articles": [card(a) for a in articles][:200], "updated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    if args.to:
        to_folder(articles, front, args.to)
        print(f"Written to {args.to}.")
    else:
        to_firestore(articles, front)
        print("Published to the portal.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
