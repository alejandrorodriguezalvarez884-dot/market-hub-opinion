"""An opinion article: a Markdown file in articles/, with a few lines of data on top.

    ---
    title: The jobs market is not falling. It is standing still
    dek: One or two sentences under the title.
    kind: Analysis
    tags: Macro, Labor market
    tickers: AAPL, MSFT
    published: 2026-10-06T08:00:00Z
    cover: What the article's picture shows, for a reader who cannot see it.
    author: Ana R.
    sources:
      - What the link says | https://example.gov/release
      - A news item of the portal | /news/article/?id=bls-1750ddcc5720
    ---

    The text, in a small part of Markdown: paragraphs, "## " headings, "> " quotes, "- " lists,
    **bold**, *emphasis* and [links](address).

The file's name is its date and its slug: 2026-10-06-the-jobs-market-is-standing-still.md. The
slug is the article's address on the portal and never changes once published.

``author`` is only there when a reader of the portal wrote the article and sent it in (inbox.py):
it is the name they signed it with, and the portal shows it. The articles written here have none.

An article has a cover: a picture, covers/<slug>.jpg, made from the drawing in covers/src/ (see
covers/render.mjs). The ``cover`` line says in words what it shows.

``load`` reads one and refuses it, saying why, when it is not fit to publish.
"""

from __future__ import annotations

import hashlib
import math
import re
from datetime import datetime, timezone
from pathlib import Path

NAME = re.compile(r"(\d{4}-\d{2}-\d{2})-([a-z0-9][a-z0-9\-]{2,90})\.md")
WORDS = (450, 1500)  # shorter is a note, longer is not read
WORDS_PER_MINUTE = 220
COVER_BYTES = 600 * 1024  # a cover travels in one document of the portal's database
# What an article touches, said by its first tag: the economy, the markets as a whole, or one of
# the portal's sectors.
SCOPES = ["Macro", "Markets", "Technology", "Communication Services", "Consumer Cyclical", "Consumer Defensive", "Financial Services",
          "Healthcare", "Industrials", "Energy", "Utilities", "Real Estate", "Basic Materials"]
# An article argues; it does not tell a reader what to do with their money.
ADVICE = re.compile(r"\b(you should (buy|sell|hold)|we recommend|(buy|sell|hold) rating|strong buy|price target of|our (price )?target"
                    r"|time to (buy|sell)|must[- ]own|top picks?|buy (it |them )?now|guaranteed returns?)\b", re.I)


class Invalid(ValueError):
    """An article that is not fit to publish, with what is wrong with it."""


def _head(text: str, name: str) -> tuple[dict, str]:
    """The data on top of the file and the text under it."""
    if not text.startswith("---\n"):
        raise Invalid(f"{name}: the file must start with its data between two lines of ---")
    top, sep, body = text[4:].partition("\n---\n")
    if not sep:
        raise Invalid(f"{name}: the data on top is not closed with ---")
    data: dict = {}
    key = None
    for n, line in enumerate(top.split("\n"), 2):
        if not line.strip():
            continue
        if line.startswith("  - "):
            if key is None or not isinstance(data.get(key), list):
                raise Invalid(f"{name}:{n}: a list item with no list above it")
            data[key].append(line[4:].strip())
        elif ":" in line and not line.startswith(" "):
            key, _, value = line.partition(":")
            key = key.strip()
            data[key] = value.strip() if value.strip() else []
        else:
            raise Invalid(f"{name}:{n}: not 'key: value' and not a list item")
    return data, body.strip()


def _list(value) -> list[str]:
    return [v.strip() for v in value.split(",") if v.strip()] if isinstance(value, str) else []


def load(path: Path) -> dict:
    name = path.name
    named = NAME.fullmatch(name)
    if not named:
        raise Invalid(f"{name}: the name must be YYYY-MM-DD-the-slug.md, in lower case")
    data, body = _head(path.read_text(encoding="utf-8").replace("\r\n", "\n"), name)
    problems = []
    title, dek, kind = (str(data.get(k) or "").strip() for k in ("title", "dek", "kind"))
    if not 10 <= len(title) <= 110:
        problems.append("the title needs 10 to 110 characters")
    if not 60 <= len(dek) <= 260:
        problems.append("the dek (the line under the title) needs 60 to 260 characters")
    if not 3 <= len(kind) <= 30:
        problems.append("the kind is missing (Analysis, Column, Explainer...)")
    tags = _list(data.get("tags"))
    if not tags or tags[0] not in SCOPES:
        problems.append(f"the first tag must be what the article touches: one of {', '.join(SCOPES)}")
    cover = str(data.get("cover") or "").strip()
    if cover and not 20 <= len(cover) <= 200:
        problems.append("the cover line (what the picture shows) needs 20 to 200 characters")
    author = re.sub(r"\s+", " ", str(data.get("author") or "")).strip()
    if author and not 2 <= len(author) <= 40:
        problems.append("the author (the name a reader signed with) needs 2 to 40 characters")
    tickers = [t.upper() for t in _list(data.get("tickers"))]
    if any(not re.fullmatch(r"[A-Z][A-Z0-9.\-]{0,9}", t) for t in tickers):
        problems.append("a ticker is not a ticker")
    try:
        published = datetime.fromisoformat(str(data.get("published", "")).replace("Z", "+00:00"))
        if published.tzinfo is None:
            raise ValueError
    except ValueError:
        published = None
        problems.append("published must be a time with its zone, like 2026-10-06T08:00:00Z")
    if published and published.date().isoformat() != named.group(1):
        problems.append("the date in the name is not the day it was published (in UTC)")
    sources = []
    for line in data.get("sources") if isinstance(data.get("sources"), list) else []:
        what, sep, url = line.rpartition("|")
        what, url = what.strip(), url.strip()
        if not sep or not what or not (url.startswith(("https://", "http://")) or url.startswith("/")):
            problems.append(f"a source must be 'what it is | its address': {line[:60]!r}")
        else:
            sources.append({"title": what, "url": url})
    if len(sources) < 2:
        problems.append("an article names at least two sources")
    words = len(re.findall(r"\b[\w'’%$.,-]+\b", re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", body)))
    if not WORDS[0] <= words <= WORDS[1]:
        problems.append(f"the text has {words} words; it needs {WORDS[0]} to {WORDS[1]}")
    advice = ADVICE.search(f"{title} {dek} {body}")
    if advice:
        problems.append(f"it tells the reader what to do with their money: {advice.group(0)!r}")
    if re.search(r"<[a-zA-Z/!]", body):
        problems.append("the text is Markdown, not HTML")
    if problems:
        raise Invalid(f"{name}: " + "; ".join(problems))
    return {"slug": named.group(2), "title": title, "dek": dek, "kind": kind, "tags": tags, "tickers": tickers,
            "published_utc": published.astimezone(timezone.utc).isoformat(timespec="seconds"),
            "minutes": max(1, math.ceil(words / WORDS_PER_MINUTE)), "body": body, "sources": sources,
            "cover": {"alt": cover} if cover else None, "author": author or None}


def picture(covers: Path, article: dict) -> bytes:
    """The cover of an article, as it will be published. Refused when it is missing or unfit."""
    name = f"covers/{article['slug']}.jpg"
    path = covers / f"{article['slug']}.jpg"
    if not article.get("cover"):
        raise Invalid(f"{article['slug']}: it has no 'cover:' line saying what its picture shows")
    if not path.exists():
        raise Invalid(f"{name} is missing: draw it in covers/src/ and run `make covers`")
    data = path.read_bytes()
    if not data.startswith(b"\xff\xd8\xff"):
        raise Invalid(f"{name} is not a JPEG")
    if len(data) > COVER_BYTES:
        raise Invalid(f"{name} weighs {len(data) // 1024} KB; a cover can weigh up to {COVER_BYTES // 1024}")
    return data


def load_all(folder: Path, covers: Path | None = None) -> list[dict]:
    """Every article, newest first. One bad article, or two with the same slug, stops them all.
    Given the folder of the covers, every article must have its own, and is told its version."""
    problems, out, seen = [], [], {}
    for path in sorted(folder.glob("*.md")):
        try:
            article = load(path)
        except Invalid as exc:
            problems.append(str(exc))
            continue
        if article["slug"] in seen:
            problems.append(f"{path.name}: the same slug as {seen[article['slug']]}")
        seen[article["slug"]] = path.name
        if covers is not None:
            try:
                # The version is the picture itself: draw it again and browsers ask for it again.
                article["cover"] = {**(article["cover"] or {}), "v": hashlib.sha256(picture(covers, article)).hexdigest()[:12]}
            except Invalid as exc:
                problems.append(str(exc))
        out.append(article)
    if problems:
        raise Invalid("\n".join(problems))
    return sorted(out, key=lambda a: a["published_utc"], reverse=True)


def card(article: dict) -> dict:
    """What the list of articles shows: everything but the text and the sources."""
    return {k: v for k, v in article.items() if k not in ("body", "sources")}
