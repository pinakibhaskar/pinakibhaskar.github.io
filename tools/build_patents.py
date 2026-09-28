#!/usr/bin/env python3
"""Generate the patents table rows in index.html from data/patents.json, and check the patent counts.

Usage (from the site root; both paths are optional):
    python3 tools/build_patents.py [data/patents.json] [index.html]

1. Rewrites only the rows between these marker comments (one row per entry, in JSON order):

       <!-- BEGIN:PATENTS ... -->  ...  <!-- END:PATENTS -->

   The only links written are the ones in each entry's "links".

2. Checks the two count strings, summary.headline (such as "7 patents") and summary.caption
   (such as "US, PCT, China & India · 5 granted"), against every place they are typed by hand in index.html,
   prints where those places are, and exits with an error if any of them disagrees with the JSON.

No third-party packages needed.
"""
import html
import glob
import json
import os
import re
import sys

sys.dont_write_bytecode = True   # importing the sibling script must not leave a __pycache__ folder in the site
from build_publications import NEW_TAB_NOTE, esc, replace_block


def text_html(text):
    """Escaped running text with the page's typography: curly apostrophes, and no line break inside
    "May&nbsp;2024", "WO&nbsp;2023/277342", "No.&nbsp;10/2024" or before the kind code in "... 0187343&nbsp;A1"."""
    out = esc(text).replace("&#x27;", "’")
    out = re.sub(r" (\d{4})\b", r"&nbsp;\1", out)
    out = re.sub(r"\bNo\. (?=\d)", "No.&nbsp;", out)
    return re.sub(r"(?<=\d) ([AB]\d)\b", r"&nbsp;\1", out)


def row_html(n, pat, indent="  "):
    pid = f"pat{n}"   # short ids (pat1-n, pat1-l1 ...): they only tie a link chip to its row's patent number
    state, _, where = pat["status_chip"].partition(" · ")
    status = [f'<span class="status__state">{esc(state)}</span>']
    if where:
        status.append(f'<span class="status__sep"> · </span><span class="status__where">{text_html(where)}</span>')
    if pat.get("status_meta"):
        status.append(f'<span class="status__sep"> · </span><span class="status__meta">{text_html(pat["status_meta"])}</span>')

    number = [f'<span class="patents__id" id="{pid}-n">{esc(pat["number"])}</span>']
    if pat.get("also"):
        number.append(f'<span class="patents__also">{text_html(pat["also"])}</span>')
    if pat.get("links"):
        # Accessible name = label + patent number ("Google Patents US 11,989,193 B2").
        chips = "".join(
            f'<li><a class="chip chip--quiet" href="{esc(l["url"])}" id="{pid}-l{i}" aria-labelledby="{pid}-l{i} {pid}-n" '
            f'target="_blank" rel="noopener noreferrer" aria-describedby="{NEW_TAB_NOTE}">{esc(l["label"])}</a></li>'
            for i, l in enumerate(pat["links"], 1))
        number.append(f'<ul class="chips chips--tight">{chips}</ul>')

    out = [
        '<tr role="row">',
        f'  <td role="cell" class="patents__no">{n}</td>',
        '  <th role="rowheader" scope="row" class="patents__invention">',
        f'    <span class="patents__title">{esc(pat["title"])}</span>',
        f'    <span class="patents__desc">{text_html(pat["description"])}</span>',
        '  </th>',
        f'  <td role="cell" class="patents__num">{" ".join(number)}</td>',
        f'  <td role="cell" class="patents__status"><span class="status status--{esc(pat["status"])}">{"".join(status)}</span></td>',
        '</tr>',
    ]
    return "\n".join(indent + line for line in out)


def plain(fragment):
    """Visible text of an HTML fragment: tags dropped, entities decoded, white space collapsed."""
    text = html.unescape(re.sub(r"<[^>]+>", " ", fragment)).replace("\u00a0", " ")
    return re.sub(r"\s+", " ", text).strip()


def check_counts(root, headline, caption):
    """Every mention of a patent count in the site's copy must agree with the JSON.
    Scans each page's visible text and meta descriptions for "<number> patents" (and the
    spelled-out "seven patents" form used in prose). Returns (report lines, number of problems)."""
    words = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10}
    want = int(re.match(r"\d+", headline).group())
    lines, problems = [], 0
    pages = sorted(p for p in glob.glob(os.path.join(root, "**", "*.html"), recursive=True)
                   if os.sep + "Pinaki_Bhaskar" + os.sep not in p and not p.endswith("404.html"))
    for path in pages:
        with open(path, encoding="utf-8") as fh:
            html = fh.read()
        text = re.sub(r"<[^>]+>", " ", re.sub(r"<!--.*?-->", "", html, flags=re.S))
        found = re.findall(r"\b(\d+|one|two|three|four|five|six|seven|eight|nine|ten)\+? patents?\b", text, re.I)
        found += re.findall(r'content="[^"]*\b(\d+)\+? patents\b', html)
        rel = os.path.relpath(path, root)
        if not found:
            continue
        counts = {int(f) if f.isdigit() else words[f.lower()] for f in found}
        bad = sorted(c for c in counts if c != want)
        if bad:
            problems += 1
            lines.append(f"  MISMATCH  {rel}: says {bad} patents; data/patents.json says {want}")
        else:
            lines.append(f"  ok        {rel}: {len(found)} mention(s) of {want} patents")
    if caption and not any(caption in open(p, encoding="utf-8").read() for p in pages):
        lines.append(f'  note      the caption "{caption}" is not used on any page (fine)')
    return lines, problems


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    data_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, "..", "data", "patents.json")
    index_path = sys.argv[2] if len(sys.argv) > 2 else os.path.join(here, "..", "patents", "index.html")
    with open(data_path, encoding="utf-8") as fh:
        data = json.load(fh)
    patents, summary = data["patents"], data["summary"]

    with open(index_path, encoding="utf-8") as fh:
        page = fh.read()
    page = replace_block(page, "PATENTS", "\n".join(row_html(n, p) for n, p in enumerate(patents, 1)))
    with open(index_path, "w", encoding="utf-8") as fh:
        fh.write(page)
    print(f"Wrote {len(patents)} patent rows to {index_path}")

    # The counts are typed by hand in the copy; the JSON is the source of truth.
    granted = sum(1 for p in patents if p["status"] == "granted")
    if (summary.get("inventions"), summary.get("granted")) != (len(patents), granted):
        print(f'WARNING: patents.json summary says {summary.get("inventions")} inventions / {summary.get("granted")} granted, '
              f"but the list holds {len(patents)} / {granted}. Check the summary and its two strings.")
    headline, caption = summary["headline"], summary["caption"]
    lines, problems = check_counts(os.path.join(here, ".."), headline, caption)
    print(f'Patent counts: "{headline}" (and "{caption}") are typed by hand in the copy. Every page checked:')
    print("\n".join(lines))
    print("  (not checked: the social card assets/img/og-card.png also shows the patent count)")
    if problems:
        sys.exit(f"\nERROR: {problems} place(s) disagree with data/patents.json — edit them and run this again.")


if __name__ == "__main__":
    main()
