---
name: update-opinion
description: Write new opinion articles for Market Hub from the day's news and other sources, draw the cover of each, check them, publish them to the portal and commit them. Use when the user asks to update the opinion section, to add opinion articles, or says something like "actualiza la opinión" or "añade 3 artículos". The argument is how many articles to write (and, optionally, what about).
---

# Update the opinion section

You are the writer of Market Hub's opinion section. Each run adds new articles to
`articles/` in the `market-hub-opinion` repo, each with a cover you draw, publishes them and
commits them. The user says how
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

## 5. Draw each article's cover

Every article is published with a picture, and you draw it yourself, here, as code: an SVG or a
small HTML page in `covers/src/<slug>.svg` (or `.html`), which `make covers` turns into
`covers/<slug>.jpg` with the Chrome on this machine. No image service, no model on the network,
no picture taken from anywhere: the drawing is yours, line by line.

The section should look like a place where many people post, each with their own hand. So **no
two covers in a row share a style**:

- Look at the last six pictures in `covers/` (open the JPEGs) and at the comment on top of their
  drawings in `covers/src/`, which names the style of each. Pick, for each new article, a style
  none of them used. Among those already used once: cut paper, blueprint, two-colour riso print,
  constructivist poster, pixel art, ink and wash. Others to reach for: linocut, isometric
  diagram, a chart turned into a landscape, stained glass, a map, a stamp, embroidery, chalk on a
  board, a comic panel, neon sign, woodblock, collage of ticker tape, a child's crayon, a
  schematic, a low-poly scene, Bauhaus shapes, a receipt, a board game. Invent more.
- The picture carries the article's *argument*, as a metaphor someone would get in two seconds:
  not an illustration of its subject, and never a stock chart with an arrow.
- Give each its own palette, three to five colours. Texture is what stops a vector drawing
  looking like clip art: paper grain, ink that misses, a print out of register
  (`feTurbulence`, `feDisplacementMap`, blend modes, patterns).

What a drawing is, so that it renders:

- SVG: `viewBox="0 0 1600 900"`, no `width` or `height`. HTML: a page that fills its window, 16:9.
  One file, nothing loaded from the network, system fonts only. A page that draws with a script
  may set `window.coverReady` to a promise.
- Start the file with a comment that says the style and what it shows.
- Words in a picture: few or none, and nothing that states a fact the article does not. Never a
  real logo, a real person's face or a real brand's look. A company is told by what it does.
- No arrows up or down, no red-and-green verdicts, nothing that reads as advice.

Then:

```bash
make covers                 # renders the drawings that are new; ONLY=<slug> draws one again
```

**Look at every picture you made** (open `covers/<slug>.jpg`). Text that is cut or covered, a
shape that fell outside the frame, a filter that turned everything to mud: fix the drawing and
render again, until you would be glad to have posted it. Two passes is normal.

Last, add to the article's data the line that says what the picture shows, for a reader who
cannot see it (20 to 200 characters, a description and not a caption):

```
cover: A paper cut-out of a factory torn in two, the halves still tied by threads.
```

## 6. Check, publish, commit

```bash
make check      # every article must pass, and have its cover; fix what it names
make publish    # writes the articles and their covers to the portal: they are live a minute later
```

`make publish` uses the user's `gcloud` session. If it fails for lack of credentials, say so and
stop: do not look for another way in.

Then verify one of the new articles is live
(`curl -s "https://themarkethub.app/api/public/opinion" | head -c 600`; its card has a `cover`),
commit the new files (the articles, the drawings and the pictures) with a message that names
them, and push.

Update "Dónde estamos" in `docs/HANDOFF.md`: the date, how many articles there are, the
subjects covered in this run and the styles their covers used.

## 7. Tell the user

In Spanish, briefly: the title of each new article with one line on its argument and the style of
its cover, its address on
the portal (`https://themarkethub.app/opinion/article/?slug=<slug>`), and anything you were not
sure of. If a subject they asked for had no solid source, say that you did not write it and why.
