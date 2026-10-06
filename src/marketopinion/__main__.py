"""Check the articles, and publish them where the portal reads them.

    python -m marketopinion check              read every article; say what is wrong with any
    python -m marketopinion publish            ...and write them to the portal's Firestore
    python -m marketopinion publish --to DIR   ...or to the folder a local portal reads

The portal reads three things: one document per article ("opinion/<slug>"), one with the cards
of all of them ("opinion_state/front"), so its list is a single read, and the cover of each
("opinion_covers/<slug>", the JPEG itself). An article that is taken
out of articles/ leaves the list; its own document is left where it was.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from .articles import Invalid, card, load_all, picture

ROOT = Path(__file__).resolve().parents[2]
COVERS = ROOT / "covers"
DATABASE = "market-hub"  # the portal's own Firestore database


def to_folder(articles: list[dict], front: dict, folder: Path) -> None:
    (folder / "articles").mkdir(parents=True, exist_ok=True)
    (folder / "covers").mkdir(parents=True, exist_ok=True)
    for a in articles:
        (folder / "articles" / f"{a['slug']}.json").write_text(json.dumps(a), encoding="utf-8")
        (folder / "covers" / f"{a['slug']}.jpg").write_bytes(picture(COVERS, a))
    (folder / "front.json").write_text(json.dumps(front), encoding="utf-8")


def to_firestore(articles: list[dict], front: dict) -> None:
    from google.cloud import firestore

    project = os.environ.get("GOOGLE_CLOUD_PROJECT", "").strip()
    if not project:
        raise SystemExit("error: no Google Cloud project. Run it with `make publish`, or set GOOGLE_CLOUD_PROJECT.")
    client = firestore.Client(project=project, database=DATABASE)
    # The covers first, one by one (each is a large document), and only those that are new or were
    # drawn again: what is published says which version of each it has.
    was = client.collection("opinion_state").document("front").get()
    had = {c["slug"]: (c.get("cover") or {}).get("v") for c in ((was.to_dict() or {}).get("articles", []) if was.exists else [])}
    for a in articles:
        if had.get(a["slug"]) != a["cover"]["v"]:
            client.collection("opinion_covers").document(a["slug"]).set({"jpeg": picture(COVERS, a), "v": a["cover"]["v"]})
            print(f"  cover  {a['slug']}")
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
        articles = load_all(ROOT / "articles", COVERS)
    except Invalid as exc:
        print(exc, file=sys.stderr)
        return 1
    for a in articles:
        print(f"  {a['published_utc'][:16]}  {a['kind']:<12} {a['minutes']} min  {a['title']}")
    print(f"{len(articles)} articles, each with its cover, all fit to publish.")
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
