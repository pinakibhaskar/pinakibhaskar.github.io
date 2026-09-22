#!/usr/bin/env python3
"""Generate the publication markup in index.html from publications.json.

Usage:
    python3 tools/build_publications.py [path/to/publications.json] [path/to/index.html]

With no arguments it reads data/publications.json and writes index.html, like its two siblings.

The script rewrites only the text between these marker comments in index.html, so it is safe
to run again whenever publications.json changes:

    <!-- BEGIN:PUBS-SELECTED ... -->  ... <!-- END:PUBS-SELECTED -->   items with "selected": true
    <!-- BEGIN:PUBS-ALL ... -->       ... <!-- END:PUBS-ALL -->        every item, newest first
    <!-- BEGIN:PUBS-TYPES ... -->     ... <!-- END:PUBS-TYPES -->      type filter buttons with counts
    <!-- BEGIN:PUBS-TOPICS ... -->    ... <!-- END:PUBS-TOPICS -->     topic <option>s with counts

It also keeps the visible totals in step ("Showing N of N", "N items, newest first", "Show all N").
All publications are written into the page; site.js only clips and filters what is already there.

Sibling generators reuse esc() and replace_block() from this file:
    tools/build_patents.py   patents table + patent-count check   (data/patents.json)
    tools/build_photos.py    photography grid                     (data/photos.json)

No third-party packages needed.
"""
import html
import json
import os
import re
import sys
from collections import Counter

OWNER = "Pinaki Bhaskar"
TYPE_ORDER = ["Conference", "Workshop", "Shared task", "Journal", "Book"]
# Terms in a note that must not break at their hyphen: shown with a non-breaking hyphen (U+2011).
# The JSON keeps the plain hyphen, and site.js turns U+2011 back into "-" for search.
KEEP_TOGETHER = ["1-hop", "IIT-CNR"]
# Separator between the parts of a line. The no-break space ties the dot to the word before it, so the
# line can only wrap after the dot and never starts with one.
DOT = '&nbsp;<span class="dot" aria-hidden="true">·</span> '
# Id of the one hidden "opens in a new tab" note in index.html; every new-tab link points to it.
NEW_TAB_NOTE = "new-tab"


def esc(text):
    return html.escape(str(text), quote=True)


def note_html(note):
    out = esc(note)
    for term in KEEP_TOGETHER:
        out = out.replace(term, term.replace("-", "\u2011"))
    return out


def authors_html(authors):
    parts = []
    for name in authors:
        parts.append(f"<strong>{esc(name)}</strong>" if name == OWNER else esc(name))
    return ", ".join(parts)


def link_html(link, link_id, title_id):
    """Link chip. Its accessible name is its label plus the paper's title ("PDF" + title), so the
    many "PDF" / "ACL Anthology" links can be told apart in a screen reader's list of links.
    External links open in a new tab (announced through NEW_TAB_NOTE); site.css draws their arrow."""
    url = link["url"]
    external = url.startswith(("http://", "https://"))
    attrs = f' id="{link_id}" aria-labelledby="{link_id} {title_id}"'
    if external:
        attrs += f' target="_blank" rel="noopener noreferrer" aria-describedby="{NEW_TAB_NOTE}"'
    return f'<li><a class="chip chip--quiet" href="{esc(url)}"{attrs}>{esc(link["label"])}</a></li>'


def item_html(pub, prefix, heading, filterable=True, indent="  "):
    """One <li class="pub">. `prefix` keeps ids unique between the two lists.
    Only the full list is filterable, so only it carries the data-* attributes
    (site.js builds the search text from the visible text of each item)."""
    topics = pub.get("topics", [])
    item_id = prefix + esc(pub["id"])
    data = f' data-type="{esc(pub["type"])}" data-topics="{esc("|".join(topics))}"' if filterable else ""
    venue = esc(pub["venue"]).replace("vol. ", "vol.&nbsp;")   # keep a volume number with its label
    if pub.get("pages"):
        # the page reference stays on one line ("pp." never parts from its numbers), and the separator
        # is tied to the word before it, so a wrapped line never starts with a dot
        venue += f'{DOT}<span class="nowrap">pp. {esc(pub["pages"])}</span>'
    out = [
        f'<li class="pub row" id="{item_id}"{data}>',
        f'  <p class="pub__meta"><span class="pub__year">{pub["year"]}</span> '
        f'<span class="pub__type">{esc(pub["type"])}</span></p>',
        '  <div class="pub__body">',
        f'    <{heading} class="pub__title" id="{item_id}-t">{esc(pub["title"])}</{heading}>',
        f'    <p class="pub__authors">{authors_html(pub["authors"])}</p>',
        f'    <p class="pub__venue">{venue}</p>',
    ]
    if pub.get("note"):
        out.append(f'    <p class="pub__note">{note_html(pub["note"])}</p>')
    if topics:
        out.append('    <p class="pub__topics"><span class="vh">Topics: </span>'
                   + DOT.join(esc(t) for t in topics) + "</p>")
    if pub.get("links"):
        out.append('    <ul class="chips chips--tight">'
                   + "".join(link_html(l, f"{item_id}-l{n}", f"{item_id}-t")
                             for n, l in enumerate(pub["links"], 1)) + "</ul>")
    out += ["  </div>", "</li>"]
    return "\n".join(indent + line for line in out)


def replace_block(page, name, body):
    pattern = re.compile(rf"(<!-- BEGIN:{name}\b.*?-->\n)(.*?)(^[ \t]*<!-- END:{name} -->)", re.S | re.M)
    if not pattern.search(page):
        sys.exit(f"Marker {name} not found in index.html")
    return pattern.sub(lambda m: m.group(1) + body + "\n" + m.group(3), page, count=1)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    data_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, "..", "data", "publications.json")
    index_path = sys.argv[2] if len(sys.argv) > 2 else os.path.join(here, "..", "index.html")
    with open(data_path, encoding="utf-8") as fh:
        pubs = json.load(fh)
    # Newest first; stable, so the order inside a year follows the JSON file.
    pubs = sorted(pubs, key=lambda p: -int(p["year"]))

    selected = "\n".join(item_html(p, "sel-", "h4", filterable=False) for p in pubs if p.get("selected"))
    everything = "\n".join(item_html(p, "pub-", "h4") for p in pubs)

    type_counts = Counter(p["type"] for p in pubs)
    types = [t for t in TYPE_ORDER if t in type_counts] + sorted(set(type_counts) - set(TYPE_ORDER))
    btn = ('        <button class="filter-btn" type="button" data-pub-type="{val}" aria-pressed="{on}">'
           '{label} <span class="filter-btn__n">{n}</span></button>')
    type_html = "\n".join([btn.format(val="all", on="true", label="All", n=len(pubs))] + [
        btn.format(val=esc(t), on="false", label=esc(t), n=type_counts[t]) for t in types])

    topic_counts = Counter(t for p in pubs for t in p.get("topics", []))
    opt = '              <option value="{val}">{label}</option>'
    topic_html = "\n".join([opt.format(val="all", label="All topics")] + [
        opt.format(val=esc(t), label=f"{esc(t)} ({n})") for t, n in topic_counts.most_common()])

    with open(index_path, encoding="utf-8") as fh:
        page = fh.read()
    page = replace_block(page, "PUBS-SELECTED", selected)
    page = replace_block(page, "PUBS-ALL", everything)
    page = replace_block(page, "PUBS-TYPES", type_html)
    page = replace_block(page, "PUBS-TOPICS", topic_html)
    # Keep the visible totals in step with the data.
    page = re.sub(r"Showing \d+ of \d+", f"Showing {len(pubs)} of {len(pubs)}", page)
    page = re.sub(r"\d+ items, newest first", f"{len(pubs)} items, newest first", page)
    page = re.sub(r"Show all \d+", f"Show all {len(pubs)}", page)
    with open(index_path, "w", encoding="utf-8") as fh:
        fh.write(page)
    print(f"Wrote {len(pubs)} publications ({sum(1 for p in pubs if p.get('selected'))} selected) to {index_path}")


if __name__ == "__main__":
    main()
