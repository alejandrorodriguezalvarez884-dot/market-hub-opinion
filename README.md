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

Publishing writes to the portal's Firestore database: one document per article, one with the
list and one per cover. The portal needs no redeploy for a new article.
