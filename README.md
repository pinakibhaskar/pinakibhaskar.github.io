# pinakibhaskar.github.io

Personal website of Dr. Pinaki Bhaskar — <https://pinakibhaskar.github.io/>
(`www.pinakibhaskar.com` forwards here).

Plain static files: no framework, no build step, no third-party requests. Push to `master` and GitHub
Pages serves it.

## Layout

| Path | What it is |
| --- | --- |
| `index.html` | The home page (About): portrait, the story, three work cards, current research, six photographs, contact. |
| `work/`, `research/`, `patents/`, `recognition/`, `background/`, `photography/` | The other pages, one `index.html` each. The site header is copied into every page — if you change the menu, change it in all seven files, then run `python3 tools/build_albums.py` so the album pages pick it up. |
| `photography/<album>/` | One generated page per photo album (`tools/build_albums.py`) — do not edit by hand. |
| `assets/css/site.css` | Styles. Design tokens (colours, type scale, spacing) are at the top. |
| `assets/js/site.js` | Progressive enhancement only: theme toggle, mobile menu, publication list (clipped until “Show all”, filters, search), copy-address button, photography lightbox. The page works without it. |
| `assets/fonts/` | Self-hosted Fraunces + Inter (SIL Open Font License), latin subset, trimmed to the weights the site uses (Fraunces 300–600, optical size 12–72; Inter 400–700). Stay inside those ranges in `site.css`, or replace the files with the full variable fonts. |
| `assets/img/` | Favicon, the social-share card (`og-card.png`), the portrait (`pinaki-bhaskar-320/640`), the award photo (`pinaki-bhaskar-zinnov-2022-480/960/full`) and `cards/` (the three home-page card images), each as WebP + JPEG. |
| `assets/photos/` | The Photography page's selected images: `<slug>-480.{webp,jpg}` (grid tile) and `<slug>-full.{webp,jpg}` (enlarged view). |
| `assets/albums/<album>/` | The albums' images: `<id>-480.{webp,jpg}` (grid tile), `<id>-full.{webp,jpg}` (the enlarged view — the original pixels, metadata removed) and `og.jpg` (the social card, cut from the cover). Made by `tools/album_images.py`. |
| `assets/awards/` | Award certificates and photos: `<slug>-240.{webp,jpg}` (thumbnail) and `<slug>-full.{webp,jpg}`. |
| `assets/certificates/` | Course certificates: the PDF plus a rendered `-480` thumbnail and `-full` image. |
| `assets/talks/` | Invited-talk photographs, `<slug>-480.{webp,jpg}` (480×360 tile) and `<slug>-full.{webp,jpg}`, plus slide decks as PDF. |
| `assets/community/` | Photographs for the Jury & mentoring entries, same two sizes. |
| `data/publications.json` | Every publication, with links, type, topics and the `selected` flag. |
| `data/patents.json` | Every patent (one entry per invention) with status, official links, and the two headline count strings. |
| `data/photos.json` | The selected photographs, in display order, with caption and alt text. |
| `data/albums.json` | The albums: title, intro, cover, and every photograph with its title and alt text. |
| `data/awards.json` | Awards & recognition, in two groups, with optional certificate images. |
| `tools/build_publications.py` | Regenerates the publication lists in `research/index.html`. |
| `tools/build_patents.py` | Regenerates the patents table in `patents/index.html`, and checks every mention of a patent count across the site. |
| `tools/build_photos.py` | Regenerates the selected-photographs grid in `photography/index.html` and the six-photo strip on the home page. |
| `tools/album_images.py` | Prepares an album's image files (tiles, metadata-free full size, social card) from the originals. |
| `tools/build_albums.py` | Regenerates the album cards in `photography/index.html`, every `photography/<album>/index.html`, and adds new album pages to `sitemap.xml`. |
| `tools/build_awards.py` | Regenerates the award lists in `recognition/index.html`. |
| `404.html`, `robots.txt`, `sitemap.xml`, `.nojekyll` | Hosting housekeeping. |
| `Pinaki_Bhaskar/` | The retired 2014 iWeb site. Its pages now redirect here (the old album pages to the new albums); `Publication_files/*.pdf` are still linked from the publication list, so keep them. |

## Common edits

### Add or change a publication

1. Edit `data/publications.json` (copy an existing entry; set `"selected": true` to feature it).
2. Run `python3 tools/build_publications.py`
3. The script keeps "37 items", "Showing 37 of 37" and "Show all 37" in step; update the prose counts
   by hand if they changed ("35" on the home page and in the research metrics).

### Add or change a patent

1. Edit `data/patents.json`: one entry per invention. Set `status` to `granted` or `pending`, and update
   `summary.headline` / `summary.caption` (e.g. "7 patents" / "US, PCT, China & India · 5 granted").
2. Run `python3 tools/build_patents.py`. It rewrites the table and then checks every page for a mention of
   a patent count ("7 patents", "seven patents"); it exits with an error until they all agree with the JSON.
3. The count also appears on the social card `assets/img/og-card.png` — update that too.

Only link patent-office pages (USPTO, WIPO Patentscope) or Google Patents. Never link a WO/PCT PDF or a
third-party mirror: some of them print inventors' home addresses.

### Add or change a photograph

1. Export two sizes into `assets/photos/`: `<slug>-480.webp` + `.jpg` (480×360, the grid tile) and
   `<slug>-full.webp` + `.jpg` (the enlarged view — never larger than the original). Keep 4:3, and strip
   EXIF (it can carry GPS coordinates).
2. Add or reorder the entry in `data/photos.json` (`slug`, `caption`, `alt`, and the two sizes).
3. Run `python3 tools/build_photos.py`. The first six photographs in the JSON also appear on the home page.

The current twelve came from old 720–800 px web albums. Originals at 1600 px or more would look much
better: export `-full` at up to 1600 px wide and the section will use them as they are.

### Add an album

1. Put the originals in a folder, in the order they should appear, and run
   `python3 tools/album_images.py <album-slug> <folder>/*.jpg` (needs Pillow: `pip install pillow`).
   It writes `assets/albums/<album-slug>/<id>-480.{webp,jpg}` (480×360 tiles) and `<id>-full.{webp,jpg}` — the
   full size keeps the original's pixels and drops only its metadata (EXIF can carry GPS coordinates) — and prints
   the `"photos"` entries. Pass `--focus 007:top` for a portrait photograph whose subject is near the top (or
   `bottom`), so the tile is cropped around it; `--og 012` cuts the social card `og.jpg` from that photograph.
2. Add the album to `data/albums.json`: `slug`, `title`, `card_line` (one line for the card), `when` (or `""`),
   `intro` (two or three sentences), `cover` (a photo id), `og` (the social card's size, printed by the script),
   and the printed `photos` list with a short `title` and an `alt` sentence for every photograph. Keep titles and
   alt text free of people's names.
3. Run `python3 tools/build_albums.py`. It writes the cards on the Photography page, one page per album, and
   adds the new page to `sitemap.xml`. To retire an album, delete its entry and its `photography/<slug>/` folder.

### Add or change an award

1. Edit `data/awards.json` (two groups: External, Samsung internal — keep them separate). An award can
   carry an `image`: export the certificate or photo to `assets/awards/` as `<slug>-240.{webp,jpg}`
   (240 px wide thumbnail) and `<slug>-full.{webp,jpg}` (at most 1600 px on the long side; never upscale),
   strip EXIF, and record the pixel sizes in the JSON. Check the image first: some certificates print
   employee IDs, addresses or dates of birth.
2. Run `python3 tools/build_awards.py`.

### Add a course certificate

The Certificates list on the Background page is hand-written in `background/index.html` (search for
`class="ruled-list certs"`). Copy the Coursera row: put the PDF in `assets/certificates/`, render its
first page to `<name>-480.{webp,jpg}` and `<name>-full.{webp,jpg}`, and link the provider's own
verification page when there is one.

### Add a talk

The Invited talks list on the Background page is hand-written in `background/index.html` (search for
`id="talks"`). Copy an existing entry: the date in `entry__dates`, the talk title in `entry__org`, the
occasion and host in `entry__role`, a short paragraph on what was covered, then the photographs as a
`photos--strip` (three across) and any links as chips — a few words each (chips do not wrap), one chip per
destination, and short figcaptions (they are set in uppercase and read out by the lightbox). Export each photograph to `assets/talks/` as
`<slug>-480.{webp,jpg}` (480×360, the tile — crop to 4:3) and `<slug>-full.{webp,jpg}` (at most 1600 px on
the long side; never upscale), strip EXIF, and put the full image's pixel size in `data-w` / `data-h`.
A slide deck goes in `assets/talks/` as a PDF; read it first for anything that should not be public
(phone numbers, addresses, unreleased work) and for scripts or fonts fetched from other sites.

The Jury & mentoring section below it (`id="jury"`) uses the same entry pattern, with its images in
`assets/community/`.

### Edit the story on the home page

The three paragraphs under the name in `index.html` are the only place the site tells the story in
prose; everything else is evidence. Keep them short (the page is meant to read like a profile, not a
CV), and keep their facts consistent with the Work, Background and Patents pages.

### Replace the portrait

The portrait is `assets/img/pinaki-bhaskar-320.{webp,jpg}` and `-640.{webp,jpg}`, 4:5 portrait
(320×400 and 640×800). Export a new photo at those two sizes under the same names (strip EXIF); if the
proportions change, update `width`/`height` on the `<img>` in `index.html`. Re-render the social card
too (it shows the portrait).
The JSON-LD block at the top of `index.html` points at the 640 px JPEG.

### Change wording

Edit the page's `index.html` directly. A link that leaves the site takes three attributes, copied from any
existing one: `target="_blank" rel="noopener noreferrer" aria-describedby="new-tab"` (the last one
makes screen readers say "opens in a new tab"; the publication script adds all three by itself).

Keep the same facts in each page's `<meta name="description">` and Open Graph tags, and in the JSON-LD
block at the top of the home page.

### Refresh the "last updated" date

The footer of each page (search for “Last updated”) and `sitemap.xml`.

## Privacy

By design the site carries no phone number, street address, date of birth, marital status
or employer e-mail address. Please keep it that way when editing.

## Preview locally

```sh
python3 -m http.server 8000   # then open http://localhost:8000
```
