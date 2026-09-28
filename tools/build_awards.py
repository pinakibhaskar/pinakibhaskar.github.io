#!/usr/bin/env python3
"""Generate the Awards & recognition lists in index.html from data/awards.json.

Usage (from the site root; both paths are optional):
    python3 tools/build_awards.py [data/awards.json] [recognition/index.html]

Rewrites only the markup between these marker comments, one group after another:

    <!-- BEGIN:AWARDS ... -->  ...  <!-- END:AWARDS -->

An award with an "image" gets a small framed thumbnail that links to the full-size JPEG (so it works
without JavaScript); site.js turns those links into the same lightbox the photographs use. The script
stops if an image file is missing.

No third-party packages needed.
"""
import json
import os
import sys

sys.dont_write_bytecode = True   # importing the sibling script must not leave a __pycache__ folder in the site
from build_publications import esc, replace_block

AWARD_DIR = "/assets/awards"
SRIB = '<abbr title="Samsung R&amp;D Institute India – Bangalore">SRI-B</abbr>'
NEW_TAB = 'target="_blank" rel="noopener noreferrer" aria-describedby="new-tab"'


def detail_html(text):
    # Escape first, then put the one allowed piece of markup back.
    return esc(text).replace("{SRI-B}", SRIB)


def item_html(item):
    text = f'<strong>{esc(item["title"])}</strong>'
    if item.get("detail"):
        text += f', {detail_html(item["detail"])}'
    src = item.get("source")
    if src:
        text += f' <span class="source">Source: <a href="{esc(src["url"])}" {NEW_TAB}>{esc(src["label"])}</a></span>'
    img = item.get("image")
    if not img:
        return f"      <li>{text}</li>"
    stem = f'{AWARD_DIR}/{esc(img["slug"])}'
    thumb, full = img["thumb"], img["full"]
    plate = (
        f'<a class="exhibit__plate plate" href="{stem}-full.jpg" data-w="{full["w"]}" data-h="{full["h"]}" '
        f'data-caption="{esc(img["caption"])}" aria-label="{esc(img["caption"])} (opens the image)">'
        f'<picture><source type="image/webp" srcset="{stem}-240.webp">'
        f'<img src="{stem}-240.jpg" width="{thumb["w"]}" height="{thumb["h"]}" alt="{esc(img["alt"])}" '
        'loading="lazy" decoding="async"></picture></a>'
    )
    return (
        '      <li class="exhibit">\n'
        f'        <div class="exhibit__text">{text}</div>\n'
        f'        {plate}\n'
        '      </li>'
    )


def group_html(group):
    title = esc(group["title"])
    if group.get("qualifier"):
        title += f' <span class="awards__qual">{esc(group["qualifier"])}</span>'
    items = "\n".join(item_html(i) for i in group["items"])
    return (
        '  <div class="awards row" data-reveal>\n'
        f'    <h3 class="awards__group">{title}</h3>\n'
        '    <ul class="ruled-list">\n'
        f'{items}\n'
        '    </ul>\n'
        '  </div>'
    )


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.join(here, "..")
    data_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(root, "data", "awards.json")
    index_path = sys.argv[2] if len(sys.argv) > 2 else os.path.join(root, "recognition", "index.html")
    with open(data_path, encoding="utf-8") as fh:
        groups = json.load(fh)["groups"]

    images = [i["image"] for g in groups for i in g["items"] if i.get("image")]
    missing = [f'{AWARD_DIR}/{img["slug"]}-{size}.{ext}' for img in images for size in ("240", "full") for ext in ("webp", "jpg")
               if not os.path.exists(os.path.join(root, AWARD_DIR.lstrip("/"), f'{img["slug"]}-{size}.{ext}'))]
    if missing:
        sys.exit("ERROR: missing image files:\n  " + "\n  ".join(missing))

    with open(index_path, encoding="utf-8") as fh:
        page = fh.read()
    page = replace_block(page, "AWARDS", "\n\n".join(group_html(g) for g in groups))
    with open(index_path, "w", encoding="utf-8") as fh:
        fh.write(page)
    n = sum(len(g["items"]) for g in groups)
    print(f"Wrote {n} awards in {len(groups)} groups ({len(images)} with images) to {index_path}")


if __name__ == "__main__":
    main()
