#!/usr/bin/env python3
"""
Draws the trading-terminal header as several small SVG pieces
(assets/header/*.svg) and prints the README HTML that links each piece.

GitHub shows README images as plain pictures, so nothing *inside* one
SVG can be clicked. Splitting the header into pieces lets every key,
panel and cell be its own link.

Edit the TEXT section, then run:
    python3 .github/scripts/header_card.py
It rewrites the SVGs and the header block in README.md (between the
HEADER:START / HEADER:END comments).
"""
import hashlib
import math
import os
import re
from xml.sax.saxutils import escape

# ── TEXT & LINKS (edit these) ─────────────────────────────────────────────
LINKEDIN = "https://www.linkedin.com/in/karthig-rajan-s-417ab0297/"
EMAIL = "mailto:rajankarthig@gmail.com"
NAME = "KARTHIG RAJAN S"
ROLE = "Software Developer | AI Engineer | Data Analytics"
KICKER = "DEVELOPER EQUITY · SRM IST · B.TECH CSE"
PRICE_NOTE = "5 CERTS · 2 INTERNSHIPS · OPEN TO WORK"
# (label, link) — "#name" jumps to an <a name="name"> anchor in the README
FKEYS = [("F1 PROFILE", "#profile"), ("F2 PROJECTS", "#projects"),
         ("F3 EXPERIENCE", "#experience"), ("F4 STACK", "#stack"), ("F5 STATS", "#stats")]
CELLS = [("FOCUS", "Backend · AI", "#projects"), ("PRIMARY", "Java / Spring", "#stack"),
         ("DATA", "SQL · Power BI", "#data"), ("STATUS", "● SEEKING ROLES", EMAIL)]
TICKER = [("JAVA 21", "CORE"), ("SPRING BOOT 3", "DOCDRIFT"), ("WEBFLUX", "REACTIVE"),
          ("POSTGRESQL", "AI-BI"), ("PYTHON", "NLP TRIAGE"), ("GEMINI 1.5", "LLM"),
          ("SNOWFLAKE", "SNOWPRO CORE"), ("POWER BI", "MICROSOFT"),
          ("OCI AI", "ORACLE 2025"), ("REACT", "DASHBOARDS")]

# ── Terminal Amber colours ────────────────────────────────────────────────
BG, BAND, LINE = "#000000", "#1a1400", "#3a2c00"
AMBER, SOFT, GREEN, MUTED = "#ffb000", "#ffcc66", "#00ff9c", "#7a6a3a"
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"
W, CH = 860, 7.3                  # full width, approx. width of a 12px character
OUT = "assets/header"


def text(x, y, s, fill, size=12, weight="normal", anchor="start"):
    return (f'<text x="{x}" y="{y}" fill="{fill}" font-size="{size}" font-weight="{weight}" '
            f'text-anchor="{anchor}">{escape(s)}</text>')


def svg(w, h, body, title, bg=BG):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}"><title>{escape(title)}</title>'
            f'<rect width="{w}" height="{h}" fill="{bg}"/>{body}</svg>\n')


def pieces():
    """Return rows of (filename, width, svg, link, alt)."""
    rows = []

    # Row 1: function-key bar, one piece per key
    bar, h = [], 28
    bar.append(("go.svg", 86, svg(86, h, text(43, 19, "KRS <GO>", AMBER, weight="bold", anchor="middle"),
                                   "KRS GO — LinkedIn"), LINKEDIN, "LinkedIn"))
    used = 86
    for label, link in FKEYS:
        w = round(len(label) * CH + 30)
        body = (text(w / 2, 19, label, BG, weight="bold", anchor="middle")
                + f'<line x1="{w - 0.5}" x2="{w - 0.5}" y1="6" y2="{h - 6}" stroke="#c08400"/>')
        name = label.split()[0].lower() + ".svg"
        bar.append((name, w, svg(w, h, body, label, AMBER), link, label))
        used += w
    w = W - used
    status = "INDIA · IST"
    body = (text(w - 14, 19, "OPEN TO WORK", BG, weight="bold", anchor="end")
            + f'<circle cx="{w - 14 - 12 * CH - 12}" cy="14" r="4.5" fill="{BG}">'
            '<animate attributeName="opacity" values="1;0.2;1" dur="1.6s" repeatCount="indefinite"/></circle>'
            + text(w - 14 - 12 * CH - 24, 19, status, BG, weight="bold", anchor="end"))
    bar.append(("status.svg", w, svg(w, h, body, "Open to work — email", AMBER), EMAIL, "Open to work"))
    rows.append(bar)

    # Row 2: the quote screen
    h = 112
    body = (text(22, 30, KICKER, MUTED, size=11) + text(20, 72, NAME, AMBER, size=36, weight="bold")
            + text(22, 98, ROLE, SOFT, size=13)
            + text(W - 22, 98, PRICE_NOTE, MUTED, size=11, anchor="end"))
    rows.append([("quote.svg", W, svg(W, h, body, f"{NAME} — {ROLE}"), "#profile", NAME)])

    # Row 3: four info cells
    h, cw, cells = 44, W // len(CELLS), []
    for i, (k, v, link) in enumerate(CELLS):
        w = cw if i < len(CELLS) - 1 else W - cw * (len(CELLS) - 1)
        body = (f'<line x1="0" x2="{w}" y1="0.5" y2="0.5" stroke="{LINE}"/>'
                + (f'<line x1="0.5" x2="0.5" y1="0" y2="{h}" stroke="{LINE}"/>' if i else "")
                + text(14, 17, k, MUTED, size=11)
                + text(14, 34, v, GREEN if v.startswith("●") else SOFT, weight="bold"))
        cells.append((f"cell{i + 1}.svg", w, svg(w, h, body, f"{k}: {v}"), link, k))
    rows.append(cells)

    # Row 4: scrolling skills ticker (two copies slide left forever)
    h, items, x = 28, [], 0.0
    for name, tag in TICKER:
        items.append((x, name, tag)); x += (len(name) + len(tag) + 3) * CH + 34
    tape, parts = x, []
    for copy in (0, tape):
        for ix, name, tag in items:
            parts.append(text(round(ix + copy, 1), 18, name, SOFT, weight="bold"))
            parts.append(text(round(ix + copy + (len(name) + 1) * CH, 1), 18, "▲ " + tag, GREEN))
    body = (f'<line x1="0" x2="{W}" y1="0.5" y2="0.5" stroke="{LINE}"/><g>{"".join(parts)}'
            f'<animateTransform attributeName="transform" type="translate" from="14 0" to="{14 - tape:.1f} 0" '
            f'dur="{tape / 40:.0f}s" repeatCount="indefinite"/></g>')
    rows.append([("ticker.svg", W, svg(W, h, body, "Skills ticker", BAND), "#stack", "Skills ticker")])
    return rows


def readme_block(rows):
    """HTML for the README: each row on one line with no spaces between
    pieces, so they sit flush; widths are % of the full row."""
    lines = []
    for row in rows:
        cells = []
        for name, w, _, link, alt in row:
            # round DOWN so a row never adds up to more than 100% (it would wrap)
            pct = f"{math.floor(w * 100000 / W) / 1000:.3f}".rstrip("0").rstrip(".")
            cells.append(f'<a href="{link}"><img src="./{OUT}/{name}" width="{pct}%" alt="{escape(alt)}" /></a>')
        lines.append("".join(cells))
    return "<br/>".join(lines)  # rows on one line too: whitespace would add gaps


def main():
    rows = pieces()
    # Put a short fingerprint of each image's content in its file name
    # (e.g. quote-3fa9c1.svg). When the content changes the name changes,
    # so browsers can't keep showing an old cached copy.
    rows = [[(f"{name[:-4]}-{hashlib.sha1(content.encode()).hexdigest()[:6]}.svg", w, content, link, alt)
             for name, w, content, link, alt in row] for row in rows]
    os.makedirs(OUT, exist_ok=True)
    for old in os.listdir(OUT):          # remove the previous version's files
        if old.endswith(".svg"):
            os.remove(os.path.join(OUT, old))
    for row in rows:
        for name, _, content, _, _ in row:
            with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
                f.write(content)
    with open("README.md", encoding="utf-8") as f:
        readme = f.read()
    block = f"<!-- HEADER:START -->\n{readme_block(rows)}\n<!-- HEADER:END -->"
    readme, n = re.subn(r"<!-- HEADER:START -->.*?<!-- HEADER:END -->", lambda m: block, readme, flags=re.S)
    if n != 1:
        raise SystemExit("README.md needs one <!-- HEADER:START --> ... <!-- HEADER:END --> block")
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme)
    print(f"wrote {sum(len(r) for r in rows)} pieces to {OUT}/ and updated README.md")


if __name__ == "__main__":
    main()
