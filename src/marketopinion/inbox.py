"""The articles readers sent in for review.

A signed-in reader of the portal can send an article in (themarkethub.app/opinion/submit/). The
portal publishes nothing: it keeps each one in a bucket, submissions/<account>/<id>.json, and
tells the owner by email. The owner reads it. One that is to run is brought here as a draft,
finished like any other article (its tags, its cover, a last check against CLAUDE.md) and
published with the rest; then the copy in the bucket is told so, and its author sees it on the
page they sent it from.

    python -m marketopinion inbox                          what is waiting
    python -m marketopinion fetch <id>                     write inbox/<id>.md, a draft to finish
    python -m marketopinion mark <id> published <slug>     tell its author it ran, and where
    python -m marketopinion mark <id> declined             ...or that it will not

inbox/ is not committed: a draft is a reader's text until it is an article. The account behind an
article (its email) is printed for the owner to answer, and never written to a file here.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

ID = re.compile(r"[A-Za-z0-9_\-]{6,40}")
STATUSES = ("in review", "published", "declined")


def bucket_name() -> str:
    """The portal's bucket: the one its deploy script makes, unless the environment names another."""
    named = os.environ.get("SUBMISSIONS_BUCKET", "").strip()
    project = os.environ.get("GOOGLE_CLOUD_PROJECT", "").strip()
    if not named and not project:
        raise SystemExit("error: no Google Cloud project. Run it with `make`, or set GOOGLE_CLOUD_PROJECT.")
    return named or f"{project}-market-hub-submissions"


def _bucket():
    from google.cloud import storage

    return storage.Client(project=os.environ.get("GOOGLE_CLOUD_PROJECT") or None).bucket(bucket_name())


def waiting(bucket=None) -> list[dict]:
    """Every article kept, newest first."""
    bucket = bucket or _bucket()
    docs = [json.loads(b.download_as_bytes()) for b in bucket.list_blobs(prefix="submissions/") if b.name.endswith(".json")]
    return sorted(docs, key=lambda d: d.get("received_utc", ""), reverse=True)


def find(id_: str, bucket=None):
    """An article by its id, and the object it is kept in."""
    if not ID.fullmatch(id_):
        raise SystemExit(f"error: {id_!r} is not the id of an article.")
    bucket = bucket or _bucket()
    for blob in bucket.list_blobs(prefix="submissions/"):
        if blob.name.endswith(f"/{id_}.json"):
            return json.loads(blob.download_as_bytes()), blob
    raise SystemExit(f"error: no article {id_} in gs://{bucket.name}. Its author may have taken it back.")


def slug_of(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", title.lower().replace("'", "").replace("’", "")).strip("-")[:90].strip("-")


def draft(doc: dict) -> str:
    """A reader's article as a file of articles/: its own words, and the lines still to be filled."""
    one_line = lambda text: re.sub(r"\s+", " ", str(text)).strip()  # noqa: E731
    sources = "\n".join(f"  - {one_line(s['title']).replace('|', '-')} | {s['url']}" for s in doc["sources"])
    return "\n".join([
        "---",
        f"title: {one_line(doc['title'])}",
        f"dek: {one_line(doc['dek'])}",
        "kind: Reader's view",
        "tags: ",
        f"tickers: {', '.join(doc.get('tickers') or [])}",
        f"author: {one_line(doc['byline'])}",
        "published: ",
        "cover: ",
        "sources:",
        sources,
        "---",
        "",
        doc["body"].strip(),
        "",
    ])


def fetch(id_: str, folder: Path, bucket=None) -> Path:
    doc, _ = find(id_, bucket)
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{id_}.md"
    path.write_text(draft(doc), encoding="utf-8", newline="\n")
    how = "Google: a verified address" if doc.get("provider") == "google" else "an account with a password: the address is not verified"
    print(f"  {doc['title']}")
    print(f"  signed as {doc['byline']}, {doc.get('words', '?')} words, sent {doc.get('received_utc', '')[:16]}, status: {doc.get('status')}")
    print(f"  answer to: {doc.get('account_name', '')} <{doc.get('email', '')}> ({how})")
    print(f"Draft written to {path}. To publish it: fill in tags, published and cover, move it to")
    print(f"articles/<date>-{slug_of(doc['title'])}.md, draw its cover, `make check`, `make publish`, and then")
    print(f"`make mark ID={id_} STATUS=published SLUG={slug_of(doc['title'])}`.")
    return path


def mark(id_: str, status: str, slug: str | None = None, bucket=None) -> dict:
    """Say on the kept copy what became of the article: its author reads it on the portal."""
    if status not in STATUSES:
        raise SystemExit(f"error: the status is one of: {', '.join(STATUSES)}.")
    if status == "published" and not (slug and re.fullmatch(r"[a-z0-9][a-z0-9\-]{2,90}", slug)):
        raise SystemExit("error: a published article needs its slug: mark <id> published <slug>.")
    doc, blob = find(id_, bucket)
    doc.update(status=status, slug=slug if status == "published" else None)
    blob.upload_from_string(json.dumps(doc, ensure_ascii=False, indent=1), content_type="application/json; charset=utf-8")
    return doc
