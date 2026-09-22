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


def check_counts(page, headline, caption):
    """Every hand-typed copy of the two count strings. Returns (report lines, number of problems)."""
    places = [
        ("meta description", r'<meta name="description" content="([^"]*)"', [headline]),
        ("og:description", r'<meta property="og:description" content="([^"]*)"', [headline]),
        ("twitter:description", r'<meta name="twitter:description" content="([^"]*)"', [headline]),
        ("hero sub-head", r'<p class="hero__sub">(.*?)</p>', [headline]),
        ("proof-strip tile", r'<a class="proof__item" href="#patents">(.*?)</a>', [headline, caption]),
    ]
    lines, problems = [], 0
    for name, pattern, wanted in places:
        m = re.search(pattern, page, re.S)
        if not m:
            lines.append(f"  MISSING   {name}: not found in index.html")
            problems += 1
            continue
        where = page.count("\n", 0, m.start(1)) + 1
        text = plain(m.group(1))
        for want in wanted:
            ok = want in text
            problems += not ok
            lines.append(f'  {"ok      " if ok else "MISMATCH"}  line {where:<5} {name}: "{want}"'
                         + ("" if ok else f'  <- found: "{text[-70:]}"'))
    # Any other "N patents" typed somewhere on the page must agree as well.
    body = plain(page)
    for stray in sorted(set(re.findall(r"\b\d+\+? patents\b", body)) - {headline}):
        lines.append(f'  MISMATCH  somewhere on the page: "{stray}" (the JSON says "{headline}")')
        problems += 1
    return lines, problems


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    data_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, "..", "data", "patents.json")
    index_path = sys.argv[2] if len(sys.argv) > 2 else os.path.join(here, "..", "index.html")
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
    lines, problems = check_counts(page, headline, caption)
    print(f'Patent counts: "{headline}" and "{caption}" are typed by hand in these places:')
    print("\n".join(lines))
    print("  (not checked: the social card assets/img/og-card.png also shows the patent count)")
    if problems:
        sys.exit(f"\nERROR: {problems} place(s) in index.html disagree with data/patents.json — edit them and run this again.")


if __name__ == "__main__":
    main()
