"""What makes an article fit to publish, and what stops it."""

from pathlib import Path

import pytest

from marketopinion.articles import Invalid, card, load, load_all

GOOD = """---
title: The jobs market is standing still
dek: Twenty-nine thousand jobs is not a fall and it is not a recovery. It is a market that has stopped moving.
kind: Analysis
tags: Macro, Labor market
tickers: aapl
published: 2026-10-06T08:00:00Z
sources:
  - The Employment Situation, September 2026 | https://www.bls.gov/news.release/archives/empsit_10022026.htm
  - Payroll employment adds 29,000 jobs | /news/article/?id=bls-1750ddcc5720
---

## A heading

{body}
"""
BODY = " ".join(["A sentence of the article, with a [link](https://example.com) in it."] * 60)


def write(folder: Path, name="2026-10-06-the-jobs-market-is-standing-still.md", text=GOOD, **changes):
    text = text.format(body=changes.pop("body", BODY))
    for old, new in changes.items():
        text = text.replace(old.replace("_", " "), new)
    path = folder / name
    path.write_text(text, encoding="utf-8")
    return path


def test_a_good_article(tmp_path):
    a = load(write(tmp_path))
    assert a["slug"] == "the-jobs-market-is-standing-still" and a["published_utc"] == "2026-10-06T08:00:00+00:00"
    assert a["tags"] == ["Macro", "Labor market"] and a["tickers"] == ["AAPL"] and a["minutes"] == 3
    assert a["sources"][1] == {"title": "Payroll employment adds 29,000 jobs", "url": "/news/article/?id=bls-1750ddcc5720"}
    assert a["body"].startswith("## A heading") and "body" not in card(a) and "sources" not in card(a)


@pytest.mark.parametrize("change, said", [
    ({"body": "Too short."}, "words"),
    ({"body": BODY + " You should buy the stock before the bell."}, "what to do with their money"),
    ({"body": BODY + " <script>alert(1)</script>"}, "not HTML"),
    ({"tags: Macro, Labor market": "tags: Jobs"}, "first tag"),
    ({"published: 2026-10-06T08:00:00Z": "published: 2026-10-06 08:00"}, "with its zone"),
    ({"published: 2026-10-06T08:00:00Z": "published: 2026-10-07T08:00:00Z"}, "date in the name"),
    ({"  - Payroll employment adds 29,000 jobs | /news/article/?id=bls-1750ddcc5720\n": ""}, "two sources"),
    ({"kind: Analysis\n": ""}, "kind"),
])
def test_what_stops_an_article(tmp_path, change, said):
    body = change.pop("body", BODY)
    path = tmp_path / "2026-10-06-the-jobs-market-is-standing-still.md"
    text = GOOD.format(body=body)
    for old, new in change.items():
        assert old in text
        text = text.replace(old, new)
    path.write_text(text, encoding="utf-8")
    with pytest.raises(Invalid, match=said):
        load(path)


def test_names_and_slugs(tmp_path):
    with pytest.raises(Invalid, match="YYYY-MM-DD"):
        load(write(tmp_path, name="The Jobs Market.md"))
    (tmp_path / "The Jobs Market.md").unlink()
    write(tmp_path)
    write(tmp_path, name="2026-10-05-an-older-one.md", **{"published: 2026-10-06T08:00:00Z": "published: 2026-10-05T08:00:00Z"})
    assert [a["slug"] for a in load_all(tmp_path)] == ["the-jobs-market-is-standing-still", "an-older-one"]  # newest first
