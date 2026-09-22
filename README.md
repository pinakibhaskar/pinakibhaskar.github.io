# pinakibhaskar.github.io

Personal website of Dr. Pinaki Bhaskar — <https://pinakibhaskar.github.io/>
(`www.pinakibhaskar.com` forwards here).

Plain static files: no framework, no build step, no third-party requests. Push to `master` and GitHub
Pages serves it.

## Layout

| Path | What it is |
| --- | --- |
| `index.html` | The whole site (one scrolling page). All copy lives here. |
| `assets/css/site.css` | Styles. Design tokens (colours, type scale, spacing) are at the top. |
| `assets/js/site.js` | Progressive enhancement only: theme toggle, mobile menu, publication list (clipped until “Show all”, filters, search), copy-address button, photography lightbox. The page works without it. |
| `assets/fonts/` | Self-hosted Fraunces + Inter (SIL Open Font License), latin subset, trimmed to the weights the site uses (Fraunces 300–600, optical size 12–72; Inter 400–700). Stay inside those ranges in `site.css`, or replace the files with the full variable fonts. |
| `assets/img/` | Favicon, the social-share card (`og-card.png`), the hero portrait (`pinaki-bhaskar-320/640`) and the award photo (`pinaki-bhaskar-zinnov-2022-480/960`), each as WebP + JPEG. |
| `assets/photos/` | The Photography section's images: `<slug>-480.{webp,jpg}` (grid tile) and `<slug>-full.{webp,jpg}` (enlarged view). |
| `assets/Pinaki_Bhaskar_CV.pdf` | **Not there yet.** The place for the downloadable CV — see “Add the CV” below. |
| `data/publications.json` | Every publication, with links, type, topics and the `selected` flag. |
| `data/patents.json` | Every patent (one entry per invention) with status, official links, and the two headline count strings. |
| `data/photos.json` | The photographs, in display order, with caption and alt text. |
| `tools/build_publications.py` | Regenerates the publication markup inside `index.html` from the JSON. |
| `tools/build_patents.py` | Regenerates the patents table, and checks the patent counts typed elsewhere on the page. |
| `tools/build_photos.py` | Regenerates the photography grid. |
| `404.html`, `robots.txt`, `sitemap.xml`, `.nojekyll` | Hosting housekeeping. |
| `Pinaki_Bhaskar/` | The retired 2014 iWeb site. Its pages now redirect here; `Publication_files/*.pdf` are still linked from the publication list, so keep them. |

## Common edits

### Add or change a publication

1. Edit `data/publications.json` (copy an existing entry; set `"selected": true` to feature it).
2. Run `python3 tools/build_publications.py data/publications.json index.html`
3. The script keeps "37 items", "Showing 37 of 37" and "Show all 37" in step; update the prose counts
   by hand if they changed ("35+" in the hero, proof strip, research metrics and meta description).

### Add or change a patent

1. Edit `data/patents.json`: one entry per invention. Set `status` to `granted` or `pending`, and update
   `summary.headline` / `summary.caption` (e.g. "7 patents" / "US, PCT, China & India · 5 granted").
2. Run `python3 tools/build_patents.py data/patents.json index.html`. It rewrites the table and then lists
   every place the two count strings are typed by hand (meta description, social tags, hero, proof strip);
   it exits with an error until they all agree with the JSON.
3. The count also appears on the social card `assets/img/og-card.png` — update that too.

Only link patent-office pages (USPTO, WIPO Patentscope) or Google Patents. Never link a WO/PCT PDF or a
third-party mirror: some of them print inventors' home addresses.

### Add or change a photograph

1. Export two sizes into `assets/photos/`: `<slug>-480.webp` + `.jpg` (480×360, the grid tile) and
   `<slug>-full.webp` + `.jpg` (the enlarged view — never larger than the original). Keep 4:3, and strip
   EXIF (it can carry GPS coordinates).
2. Add or reorder the entry in `data/photos.json` (`slug`, `caption`, `alt`, and the two sizes).
3. Run `python3 tools/build_photos.py data/photos.json index.html`.

The current twelve came from old 720–800 px web albums. Originals at 1600 px or more would look much
better: export `-full` at up to 1600 px wide and the section will use them as they are.

### Add the CV

The site is built with a CV slot that is switched off until a PDF exists, so nothing links to a missing
file. To switch it on:

1. Save the CV as `assets/Pinaki_Bhaskar_CV.pdf` (that exact name). Before exporting, make sure it
   carries no phone number, street address, date of birth or marital status — the site deliberately
   publishes none of these — and check the PDF's document properties (Title/Author) for the same.
2. Open `assets/css/site.css` and delete the short block at the top marked **CV SLOT** (the single rule
   `[data-cv-slot] { display: none !important; }`).
3. The “Download CV (PDF)” button in the hero, the “CV (PDF)” button in the side rail / phone menu, and
   the “CV (PDF)” chip in Contact all reappear.
4. Add the PDF to `sitemap.xml` if you want search engines to index it:
   `<url><loc>https://pinakibhaskar.github.io/assets/Pinaki_Bhaskar_CV.pdf</loc></url>`.

Keep the facts in the CV in step with the site (patent and publication counts, dates, titles).

### Replace the portrait

The hero portrait is `assets/img/pinaki-bhaskar-320.{webp,jpg}` and `-640.{webp,jpg}` (square). Export a
new square photo at those two sizes under the same names (strip EXIF) and nothing else needs to change.
The JSON-LD block at the top of `index.html` points at the 640 px JPEG.

### Change wording

Edit `index.html` directly. A link that leaves the site takes three attributes, copied from any
existing one: `target="_blank" rel="noopener noreferrer" aria-describedby="new-tab"` (the last one
makes screen readers say "opens in a new tab"; the publication script adds all three by itself).

Keep the same facts in the `<meta name="description">`, the Open Graph tags and the JSON-LD block at
the top of `index.html` in step (and in the CV, once it exists).

### Refresh the "last updated" date

Footer of `index.html` and `sitemap.xml`.

## Privacy

By design the site carries no phone number, street address, date of birth, marital status
or employer e-mail address. Please keep it that way when editing.

## Preview locally

```sh
python3 -m http.server 8000   # then open http://localhost:8000
```
