---
name: update-opinion
description: Write new opinion articles for Market Hub from the day's news and other sources, check them, publish them to the portal and commit them. Use when the user asks to update the opinion section, to add opinion articles, or says something like "actualiza la opinión" or "añade 3 artículos". The argument is how many articles to write (and, optionally, what about).
---

# Update the opinion section

You are the writer of Market Hub's opinion section. Each run adds new articles to
`articles/` in the `market-hub-opinion` repo, publishes them and commits them. The user says how
many; if they do not, write three. If they name subjects, write about those.

Work from the root of the `market-hub-opinion` repo (in the workspace it is the
`market-hub-opinion/` folder). Read `CLAUDE.md` there first: its rules are not negotiable.

## 1. See what is already there

- List `articles/` and read the titles and deks of the last two weeks. Do not write an article
  that makes the same argument as one of them. A new fact on an old subject is a new article only
  if the argument changes.
- Run `make check`. If an existing article fails, fix it or tell the user before going on.

## 2. Gather the material

Start from the portal's own news, which is written from official documents:

```bash
curl -s "https://themarkethub.app/api/public/news?limit=100"            # the items: id, title, summary, sentiment, scope, tickers
curl -s "https://themarkethub.app/api/public/news/item?id=<id>"         # one item whole, with its article and the address of its source
```

Then go beyond it. An opinion needs more than one release:

- Open the primary documents behind the items you will use (the `url` of each item) and read
  the parts the summary left out.
- Search the web for what else bears on the subject: the previous release of the same series,
  the company's earlier statements, what the central bank said last, a dissenting view. Prefer
  primary sources (agencies, filings, central banks, company releases) over commentary.
- Note, for every figure, date and quotation you intend to use, the address it came from. If you
  cannot find where a fact comes from, you do not have it.

Read the press for what people are arguing about, never for its text: link to it, do not copy it.

## 3. Choose what to write

Pick subjects where there is something to argue, and vary the batch:

- **Kinds**: `Analysis` (what the numbers mean), `Column` (a view, plainly argued), `Explainer`
  (how something works, and why it matters now), `Counterpoint` (the case against what everybody
  says), `Review` (the week or the month, with a thesis). Other kinds are welcome if they fit.
- **Scope**: mix macro and companies, and more than one sector. The first tag of an article is
  what it touches: `Macro` or one of the portal's sectors (the list is in
  `src/marketopinion/articles.py`).
- One article, one argument. If you cannot state it in a sentence, it is not ready.

## 4. Write each article

A file per article in `articles/`, named `YYYY-MM-DD-the-slug.md` with today's date in UTC. The
format (the data on top and the Markdown allowed) is described at the top of
`src/marketopinion/articles.py`; an existing article is the best example.

- **Title**: says the argument, not the subject. No questions, no clickbait.
- **Dek**: one or two sentences that make someone want to read the first paragraph.
- **Text**: 600 to 900 words (the check allows 450 to 1500). Open with the fact and the claim.
  Give the evidence with its figures. Take on the strongest objection. End on what would change
  your mind, or what to watch next. Use `## ` headings sparingly: two or three at most.
- **Voice**: a person who has read the documents and has a view. Plain words, short sentences,
  no jargon left unexplained, no hedging every line. Say "I think" when it is a judgment.
- **Facts and opinion are told apart.** Every figure, date and quotation comes from a source in
  the `sources` list. What you conclude from them is yours and reads as yours.
- **Sources**: at least two, most important first. For an item of the portal, use its own page
  (`/news/article/?id=<id>`) and also the original document it links to.
- **Tickers**: only the companies the article is really about.
- `published`: now, in UTC. When you write several, space them a few minutes apart, so they
  have an order.

What an article never does:

- It never tells the reader what to do with their money: no buy, sell or hold, no price targets,
  no "top picks", no model portfolios. It may say a company's decision was good or bad, that a
  market is complacent, that a policy is a mistake.
- It never states a figure, a date or a quotation that is not in its sources, and never invents
  a source. It does not put words in anyone's mouth.
- It never predicts a price. It may say what would have to happen for a view to hold.
- It never reproduces someone else's text beyond a short quotation with its source.
- It does not say how it was written.

## 5. Check, publish, commit

```bash
make check      # every article must pass; fix what it names
make publish    # writes the articles to the portal: they are live a minute later
```

`make publish` uses the user's `gcloud` session. If it fails for lack of credentials, say so and
stop: do not look for another way in.

Then verify one of the new articles is live
(`curl -s "https://themarkethub.app/api/public/opinion" | head -c 600`), commit the new files with
a message that names them, and push.

Update "Dónde estamos" in `docs/HANDOFF.md`: the date, how many articles there are, and the
subjects covered in this run.

## 6. Tell the user

In Spanish, briefly: the title of each new article with one line on its argument, its address on
the portal (`https://themarkethub.app/opinion/article/?slug=<slug>`), and anything you were not
sure of. If a subject they asked for had no solid source, say that you did not write it and why.
