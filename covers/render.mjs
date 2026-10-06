// Turns the cover each article was drawn with (covers/src/<slug>.svg or .html) into the picture
// the portal shows (covers/<slug>.jpg, 1200x675), with the Chrome on this machine.
//
//   node render.mjs                 the covers that have no picture yet, or whose drawing is newer
//   node render.mjs <slug> ...      these ones, again
//   node render.mjs --all           every one, again
//
// A drawing is one file that needs nothing from the network: an SVG with viewBox="0 0 1600 900"
// and no width or height, or an HTML page that fills its window (16:9). A page that draws with a
// script may set window.coverReady to a promise; the picture is taken when it settles.

import { readdir, stat, writeFile } from "node:fs/promises";
import { dirname, join } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { chromium } from "playwright-core";

const here = dirname(fileURLToPath(import.meta.url));
const SIZE = { width: 1200, height: 675 };
const LIMIT = 600 * 1024;  // a cover travels in one Firestore document: well under its megabyte
const asked = process.argv.slice(2).filter((a) => !a.startsWith("--"));
const all = process.argv.includes("--all");
const age = async (path) => (await stat(path).catch(() => null))?.mtimeMs ?? 0;

const drawings = (await readdir(join(here, "src"))).filter((f) => /\.(svg|html)$/.test(f)).sort();
const todo = [];
for (const file of drawings) {
  const slug = file.replace(/\.(svg|html)$/, "");
  const [from, to] = [join(here, "src", file), join(here, `${slug}.jpg`)];
  if (asked.length ? asked.includes(slug) : all || (await age(from)) > (await age(to))) todo.push([slug, from, to]);
}
for (const slug of asked) if (!todo.some(([s]) => s === slug)) console.error(`no drawing for ${slug} in covers/src/`);
if (!todo.length) console.log("Every cover is up to date.");

if (todo.length) {
  const browser = await chromium.launch({ channel: process.env.COVER_BROWSER ?? "chrome", headless: true });
  try {
    const page = await browser.newPage({ viewport: SIZE, deviceScaleFactor: 1 });
    page.on("pageerror", (e) => console.error("  page error:", e.message));
    for (const [slug, from, to] of todo) {
      await page.goto(pathToFileURL(from).href);
      await page.evaluate(async () => { await document.fonts?.ready; await window.coverReady; });
      await page.waitForTimeout(250);
      let picture;
      for (const quality of [88, 80, 72, 62]) {
        picture = await page.screenshot({ type: "jpeg", quality });
        if (picture.length <= LIMIT) break;
      }
      await writeFile(to, picture);
      console.log(`  ${slug}.jpg  ${Math.round(picture.length / 1024)} KB`);
    }
  } finally {
    await browser.close();
  }
}
