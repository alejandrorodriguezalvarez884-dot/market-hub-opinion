"""A reader's article, from the portal's bucket to a draft here and back with what became of it."""

import json

import pytest

from marketopinion import inbox
from marketopinion.articles import load

DOC = {"id": "Q1NQSQSqI_kD", "user_id": "1001", "email": "ana@gmail.com", "account_name": "Ana Ruiz", "provider": "google",
       "title": "Why the quiet jobs report matters", "dek": "Twenty-nine thousand jobs is not a collapse, and the reason it is not is the interesting part.",
       "body": " ".join(["A sentence of the article."] * 120), "byline": "Ana R.", "words": 600, "tickers": ["AAPL"],
       "sources": [{"title": "Jobs | September", "url": "https://www.bls.gov/a"}, {"title": "www.bea.gov", "url": "https://www.bea.gov/b"}],
       "received_utc": "2026-10-08T10:00:00+00:00", "status": "in review", "slug": None}


class Blob:
    def __init__(self, name, doc):
        self.name, self.data = name, json.dumps(doc).encode()

    def download_as_bytes(self):
        return self.data

    def upload_from_string(self, text, content_type=""):
        self.data = text.encode()


class Bucket:
    name = "test-bucket"

    def __init__(self, *docs):
        self.blobs = [Blob(f"submissions/{d['user_id']}/{d['id']}.json", d) for d in docs]

    def list_blobs(self, prefix=""):
        return [b for b in self.blobs if b.name.startswith(prefix)]


def test_what_is_waiting_newest_first():
    older = {**DOC, "id": "older12345", "received_utc": "2026-10-01T10:00:00+00:00"}
    assert [d["id"] for d in inbox.waiting(Bucket(older, DOC))] == [DOC["id"], "older12345"]


def test_a_draft_is_an_article_once_its_blanks_are_filled(tmp_path, capsys):
    path = inbox.fetch(DOC["id"], tmp_path, Bucket(DOC))
    text = path.read_text(encoding="utf-8")
    # The account is said to the owner, and never written to the file.
    assert "ana@gmail.com" in capsys.readouterr().out and "ana@gmail.com" not in text and "1001" not in text
    assert "author: Ana R." in text and "- Jobs - September | https://www.bls.gov/a" in text
    filled = text.replace("tags: ", "tags: Macro").replace("published: ", "published: 2026-10-09T08:00:00Z")
    article = tmp_path / f"2026-10-09-{inbox.slug_of(DOC['title'])}.md"
    article.write_text(filled, encoding="utf-8")
    loaded = load(article)
    assert loaded["author"] == "Ana R." and loaded["slug"] == "why-the-quiet-jobs-report-matters" and loaded["kind"] == "Reader's view"


def test_its_author_is_told_what_became_of_it():
    bucket = Bucket(DOC)
    assert inbox.mark(DOC["id"], "published", "why-the-quiet-jobs-report-matters", bucket)["status"] == "published"
    kept = json.loads(bucket.blobs[0].data)
    assert (kept["status"], kept["slug"], kept["email"]) == ("published", "why-the-quiet-jobs-report-matters", "ana@gmail.com")
    assert inbox.mark(DOC["id"], "declined", None, bucket)["slug"] is None
    for bad in [("published", None), ("published", "Not A Slug"), ("lost", None)]:
        with pytest.raises(SystemExit):
            inbox.mark(DOC["id"], *bad, bucket)
    with pytest.raises(SystemExit):
        inbox.find("nosucharticle", bucket)
    with pytest.raises(SystemExit):
        inbox.find("../../etc", bucket)
