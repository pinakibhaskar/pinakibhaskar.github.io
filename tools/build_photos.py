#!/usr/bin/env python3
"""Generate the photography grid in index.html from data/photos.json.

Usage (from the site root; both paths are optional):
    python3 tools/build_photos.py [data/photos.json] [index.html]

Rewrites only the tiles between these marker comments, in JSON order:

    <!-- BEGIN:PHOTOS ... -->  ...  <!-- END:PHOTOS -->

Each tile is a link to the full-size JPEG, so the grid works without JavaScript. site.js turns the
links into a lightbox; it reads the enlarged image's native size from data-w / data-h and swaps
"-full.jpg" for "-full.webp" where WebP is supported. The script stops if an image file is missing.

No third-party packages needed.
"""
import json
import os
import sys

sys.dont_write_bytecode = True   # importing the sibling script must not leave a __pycache__ folder in the site
from build_publications import esc, replace_block

PHOTO_DIR = "assets/photos"


def tile_html(photo, indent="  "):
    stem = f'{PHOTO_DIR}/{esc(photo["slug"])}'
    thumb, full = photo["thumb"], photo["full"]
    out = [
        '<li><figure class="photo">',
        f'  <a href="{stem}-full.jpg" data-w="{full["w"]}" data-h="{full["h"]}"><picture>'
        f'<source type="image/webp" srcset="{stem}-480.webp">'
        f'<img src="{stem}-480.jpg" width="{thumb["w"]}" height="{thumb["h"]}" alt="{esc(photo["alt"])}" '
        'loading="lazy" decoding="async"></picture></a>',
        f'  <figcaption>{esc(photo["caption"])}</figcaption>',
        '</figure></li>',
    ]
    return "\n".join(indent + line for line in out)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.join(here, "..")
    data_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(root, "data", "photos.json")
    index_path = sys.argv[2] if len(sys.argv) > 2 else os.path.join(root, "index.html")
    with open(data_path, encoding="utf-8") as fh:
        photos = json.load(fh)["photos"]

    missing = [f'{PHOTO_DIR}/{p["slug"]}-{size}.{ext}' for p in photos for size in ("480", "full") for ext in ("webp", "jpg")
               if not os.path.exists(os.path.join(root, PHOTO_DIR, f'{p["slug"]}-{size}.{ext}'))]
    if missing:
        sys.exit("ERROR: missing image files:\n  " + "\n  ".join(missing))

    with open(index_path, encoding="utf-8") as fh:
        page = fh.read()
    page = replace_block(page, "PHOTOS", "\n".join(tile_html(p) for p in photos))
    with open(index_path, "w", encoding="utf-8") as fh:
        fh.write(page)
    print(f"Wrote {len(photos)} photographs to {index_path}")


if __name__ == "__main__":
    main()
