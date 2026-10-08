# Market Hub: Opinion

The opinion articles of [Market Hub](https://themarkethub.app/opinion/). They are written here,
one Markdown file each, checked here and published from here to the portal, which shows them and
keeps the readers' comments.

- [`articles/`](articles/): one file per article, `YYYY-MM-DD-the-slug.md`. Its format is at the
  top of [`src/marketopinion/articles.py`](src/marketopinion/articles.py).
- [`covers/`](covers/): the cover of each article. `covers/src/<slug>.svg` (or `.html`) is the
  drawing, written by hand as code, each in a style of its own; `covers/<slug>.jpg` is the picture
  made from it, which is what the portal shows.
- [`.claude/skills/update-opinion/`](.claude/skills/update-opinion/SKILL.md): the Claude Code
  skill that writes new articles from the day's news and other sources, and draws their covers.
- [`CLAUDE.md`](CLAUDE.md): the rules an article keeps.

## Day to day

In Claude Code, from this folder or from the `market-hub` workspace:

```
/update-opinion 3
```

writes three new articles, draws their covers, checks them, publishes them and commits them. By
hand:

```bash
make covers     # turn the new drawings in covers/src/ into pictures (uses this machine's Chrome)
make check      # read every article and say what is wrong with any of them
make preview    # write them where a local portal reads them (../market-hub-landing/data/opinion)
make publish    # publish them to the portal (needs gcloud signed in)
```

## Readers' articles

A signed-in reader can send an article in from the portal
([themarkethub.app/opinion/submit/](https://themarkethub.app/opinion/submit/)). The portal
publishes nothing: it keeps the article in a private bucket, where the owner reads it.
One that is to run goes through this repo, like every other article:

```bash
make inbox                    # what readers have sent in, newest first
make fetch ID=<id>            # write inbox/<id>.md, a draft; prints whose it is (never saved)
#   finish it: tags, published, the cover and its line; move it to articles/<date>-<slug>.md
make covers && make check && make publish
make mark ID=<id> STATUS=published SLUG=<slug>    # its author sees "Published" and the link
make mark ID=<id> STATUS=declined                 # ...or that it will not run
```

`inbox/` is not committed. A reader's article carries an `author:` line, the name they signed it
with, and the portal shows it. The rules in [`CLAUDE.md`](CLAUDE.md) hold for it as for any other.

Publishing writes to the portal's Firestore database: one document per article, one with the
list and one per cover. The portal needs no redeploy for a new article.
