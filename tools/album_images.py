#!/usr/bin/env python3
"""Prepare the image files for one photo album (see README, "Add an album").

Usage (from the site root):
    python3 tools/album_images.py <album-slug> <original.jpg> [<original.jpg> ...]
                                  [--start N] [--focus ID:top|center|bottom ...] [--og ID]

For each original, in the order given, this writes into assets/albums/<album-slug>/ four files named by a
three-digit number (001, 002, ... or from --start):

    NNN-480.jpg / NNN-480.webp   the grid tile, 480x360 (4:3), cropped around --focus (default: the centre)
    NNN-full.jpg                 the original's pixels untouched - only its metadata (EXIF, XMP, comments) removed
    NNN-full.webp                the same pixels as WebP (quality 90) for browsers that support it

and prints the JSON entries for data/albums.json ("id", "full": {"w","h"}) to paste into the album's "photos" list,
leaving "title" and "alt" for you to fill in. The removal of metadata is lossless: the JPEG is copied segment by
segment, dropping only the metadata segments, so the pixels are bit-for-bit the same (the script checks this).

--og ID also cuts the album's social card, og.jpg (1200x628, the 1.91:1 crop of that photograph; it is the one
place an image is scaled up, since link previews want that size), and prints its size for the album's "og" field.

Needs Pillow (pip install pillow); nothing else.
"""
import argparse
import json
import os
import sys

try:
    from PIL import Image
except ImportError:                                    # pragma: no cover
    sys.exit("This script needs Pillow: pip install pillow")

TILE = (480, 360)
OG = (1200, 628)
JPEG_QUALITY = 85
WEBP_TILE_QUALITY = 82
WEBP_FULL_QUALITY = 90


def strip_jpeg_metadata(data):
    """Return the JPEG with its APPn/COM metadata segments removed and the compressed image data untouched.

    JFIF (APP0) and ICC colour profiles (APP2 'ICC_PROFILE') are kept: they describe how to show the pixels,
    not where or when they were taken. Everything after the first SOS marker is copied verbatim."""
    if data[:2] != b"\xff\xd8":
        raise ValueError("not a JPEG file")
    out = bytearray(b"\xff\xd8")
    i = 2
    n = len(data)
    while i < n:
        if data[i] != 0xFF:
            raise ValueError("corrupt JPEG: expected a marker")
        marker = data[i + 1]
        if marker == 0xFF:                              # fill byte
            i += 1
            continue
        if marker == 0xD8 or 0xD0 <= marker <= 0xD7 or marker == 0x01:   # standalone markers
            out += data[i:i + 2]
            i += 2
            continue
        if marker == 0xD9:                              # EOI
            out += data[i:i + 2]
            break
        if marker == 0xDA:                              # SOS: the rest is image data (+ any later segments)
            out += data[i:]
            break
        seglen = int.from_bytes(data[i + 2:i + 4], "big")
        seg = data[i:i + 2 + seglen]
        keep = True
        if 0xE0 <= marker <= 0xEF or marker == 0xFE:    # APPn or COM
            keep = (marker == 0xE0 and seg[4:9] == b"JFIF\0") or (marker == 0xE2 and seg[4:15] == b"ICC_PROFILE")
        if keep:
            out += seg
        i += 2 + seglen
    return bytes(out)


def crop_box(size, focus):
    """The largest 4:3 box inside `size`, placed around `focus` (top / center / bottom; left / center / right)."""
    w, h = size
    if w * 3 >= h * 4:                                  # wider than 4:3: full height, trim the sides
        bw, bh = h * 4 // 3, h
        slack = w - bw
        x = {"left": 0, "right": slack}.get(focus, slack // 2)
        return (x, 0, x + bw, bh)
    bw, bh = w, w * 3 // 4                              # taller than 4:3: full width, trim top and bottom
    slack = h - bh
    y = {"top": 0, "bottom": slack}.get(focus, slack // 2)
    return (0, y, bw, y + bh)


def make_tile(im, dest_stem, focus="center"):
    tile = im.crop(crop_box(im.size, focus)).resize(TILE, Image.LANCZOS)
    tile.save(dest_stem + "-480.jpg", "JPEG", quality=JPEG_QUALITY, optimize=True, progressive=True)
    tile.save(dest_stem + "-480.webp", "WEBP", quality=WEBP_TILE_QUALITY, method=6)


def make_variants(src, dest_stem, focus="center"):
    """Write the four files for one original and return {"w", "h"} of the full-size image."""
    with open(src, "rb") as fh:
        raw = fh.read()
    stripped = strip_jpeg_metadata(raw)
    with open(dest_stem + "-full.jpg", "wb") as fh:
        fh.write(stripped)
    with Image.open(src) as before, Image.open(dest_stem + "-full.jpg") as after:
        if before.size != after.size or before.tobytes() != after.tobytes():
            raise RuntimeError(f"{src}: pixels changed while stripping metadata")
        im = after.convert("RGB")
        im.save(dest_stem + "-full.webp", "WEBP", quality=WEBP_FULL_QUALITY, method=6)
        make_tile(im, dest_stem, focus)
        return {"w": im.size[0], "h": im.size[1]}


def make_og(full_jpg, dest):
    """The social card: the widest 1.91:1 crop of the photograph, centred, scaled to 1200x628."""
    with Image.open(full_jpg) as im:
        im = im.convert("RGB")
        w, h = im.size
        if w * OG[1] >= h * OG[0]:                      # wider than 1.91:1: full height
            bw, bh = h * OG[0] // OG[1], h
        else:
            bw, bh = w, w * OG[1] // OG[0]
        x, y = (w - bw) // 2, (h - bh) // 2
        im.crop((x, y, x + bw, y + bh)).resize(OG, Image.LANCZOS).save(dest, "JPEG", quality=85, optimize=True, progressive=True)
    return {"w": OG[0], "h": OG[1]}


def main(argv):
    ap = argparse.ArgumentParser(description="Prepare the image files for one photo album.")
    ap.add_argument("slug", help="the album's slug, e.g. europe")
    ap.add_argument("files", nargs="+", help="the original JPEGs, in display order")
    ap.add_argument("--start", type=int, default=1, help="number of the first photograph (default 1)")
    ap.add_argument("--focus", action="append", default=[], metavar="ID:FOCUS",
                    help="crop a portrait photograph's tile around its top / center / bottom, e.g. 007:top")
    ap.add_argument("--og", metavar="ID", help="also cut the social card og.jpg from this photograph")
    a = ap.parse_args(argv)
    focus = dict(f.split(":", 1) for f in a.focus)
    root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
    dest_dir = os.path.join(root, "assets", "albums", a.slug)
    os.makedirs(dest_dir, exist_ok=True)
    entries = []
    for n, src in enumerate(a.files, a.start):
        pid = f"{n:03d}"
        full = make_variants(src, os.path.join(dest_dir, pid), focus.get(pid, "center"))
        entries.append({"id": pid, "title": "", "alt": "", "full": full})
        print(f"  {pid}  {full['w']}x{full['h']}  <- {src}", file=sys.stderr)
    if a.og:
        og = make_og(os.path.join(dest_dir, f"{a.og}-full.jpg"), os.path.join(dest_dir, "og.jpg"))
        print(f'  og.jpg from {a.og}: "og": {json.dumps(og)}', file=sys.stderr)
    print(json.dumps(entries, indent=1))


if __name__ == "__main__":
    main(sys.argv[1:])
