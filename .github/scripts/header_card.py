#!/usr/bin/env python3
"""
Draws the trading-terminal header (assets/header-terminal.svg).

Edit the TEXT section below and run:
    python3 .github/scripts/header_card.py
to redraw it. The skills ticker scrolls on its own (SVG animation).
"""
from xml.sax.saxutils import escape

# ── TEXT (edit these) ─────────────────────────────────────────────────────
NAME = "KARTHIG RAJAN S"
ROLE = "Software Developer | AI Engineer | Data Analytics"
KICKER = "DEVELOPER EQUITY · SRM IST · B.TECH CSE"
PRICE, PRICE_LABEL = "9.09", "▲ CGPA"
PRICE_NOTE = "5 CERTS · 2 INTERNSHIPS · OPEN TO WORK"
FKEYS = ["F1 PROFILE", "F2 PROJECTS", "F3 EXPERIENCE", "F4 STACK"]
STATUS = "INDIA · IST"
CELLS = [("FOCUS", "Backend · AI"), ("PRIMARY", "Java / Spring"),
         ("DATA", "SQL · Power BI"), ("STATUS", "● SEEKING ROLES")]
TICKER = [("JAVA 21", "CORE"), ("SPRING BOOT 3", "DOCDRIFT"), ("WEBFLUX", "REACTIVE"),
          ("POSTGRESQL", "AI-BI"), ("PYTHON", "NLP TRIAGE"), ("GEMINI 1.5", "LLM"),
          ("SNOWFLAKE", "SNOWPRO CORE"), ("POWER BI", "MICROSOFT"),
          ("OCI AI", "ORACLE 2025"), ("REACT", "DASHBOARDS")]

# ── Terminal Amber colours ────────────────────────────────────────────────
BG, BAND, LINE = "#000000", "#1a1400", "#3a2c00"
AMBER, SOFT, GREEN, MUTED = "#ffb000", "#ffcc66", "#00ff9c", "#7a6a3a"
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"
W, H, CH = 860, 214, 7.3        # width, height, approx. width of a 12px character


def text(x, y, s, fill, size=12, weight="normal", anchor="start", extra=""):
    return (f'<text x="{x}" y="{y}" fill="{fill}" font-size="{size}" font-weight="{weight}" '
            f'text-anchor="{anchor}"{extra}>{escape(s)}</text>')


def build():
    o = []
    # Function-key bar
    o.append(f'<rect x="0" y="0" width="{W}" height="28" fill="{AMBER}"/>')
    o.append(f'<rect x="0" y="0" width="86" height="28" fill="{BG}"/>')
    o.append(text(12, 19, "KRS <GO>", AMBER, weight="bold"))
    x = 104
    for k in FKEYS:
        o.append(text(x, 19, k, BG, weight="bold")); x += len(k) * CH + 26
    o.append(text(W - 14, 19, "OPEN TO WORK", BG, weight="bold", anchor="end"))
    dot_x = W - 14 - len("OPEN TO WORK") * CH - 12
    o.append(f'<circle cx="{dot_x}" cy="14" r="4.5" fill="{BG}">'
             '<animate attributeName="opacity" values="1;0.2;1" dur="1.6s" repeatCount="indefinite"/></circle>')
    o.append(text(dot_x - 12, 19, STATUS, BG, weight="bold", anchor="end"))

    # Quote screen
    o.append(text(22, 56, KICKER, MUTED, size=11))
    o.append(text(20, 98, NAME, AMBER, size=36, weight="bold"))
    o.append(text(22, 124, ROLE, SOFT, size=13))
    o.append(text(W - 22, 98, PRICE_LABEL, GREEN, size=15, weight="bold", anchor="end"))
    o.append(text(W - 22 - len(PRICE_LABEL) * 9.2 - 10, 98, PRICE, GREEN, size=34, weight="bold", anchor="end",
                  extra=''))
    o.append(text(W - 22, 124, PRICE_NOTE, MUTED, size=11, anchor="end"))

    # Info cells
    top = 142
    o.append(f'<line x1="0" x2="{W}" y1="{top}" y2="{top}" stroke="{LINE}"/>')
    cw = W / len(CELLS)
    for i, (k, v) in enumerate(CELLS):
        cx = i * cw
        if i:
            o.append(f'<line x1="{cx}" x2="{cx}" y1="{top}" y2="{top + 44}" stroke="{LINE}"/>')
        o.append(text(cx + 14, top + 17, k, MUTED, size=11))
        o.append(text(cx + 14, top + 34, v, GREEN if v.startswith("●") else SOFT, weight="bold"))

    # Scrolling skills ticker: two copies side by side, slid left forever.
    band = top + 44
    o.append(f'<rect x="0" y="{band}" width="{W}" height="{H - band}" fill="{BAND}"/>')
    o.append(f'<line x1="0" x2="{W}" y1="{band}" y2="{band}" stroke="{LINE}"/>')
    items, x = [], 0.0
    for name, tag in TICKER:
        items.append((x, name, tag)); x += (len(name) + len(tag) + 3) * CH + 34
    tape = x
    parts = []
    for copy in (0, tape):
        for ix, name, tag in items:
            parts.append(text(round(ix + copy, 1), band + 18, name, SOFT, weight="bold"))
            parts.append(text(round(ix + copy + (len(name) + 1) * CH, 1), band + 18, "▲ " + tag, GREEN))
    o.append(f'<g clip-path="url(#tape)"><g>{"".join(parts)}'
             f'<animateTransform attributeName="transform" type="translate" from="14 0" to="{14 - tape:.1f} 0" '
             f'dur="{tape / 40:.0f}s" repeatCount="indefinite"/></g></g>')

    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
            f'font-family="{FONT}">'
            f'<title>{escape(NAME)} — {escape(ROLE)}</title>'
            f'<defs><clipPath id="card"><rect width="{W}" height="{H}" rx="8"/></clipPath>'
            f'<clipPath id="tape"><rect x="0" y="0" width="{W}" height="{H}"/></clipPath></defs>'
            f'<g clip-path="url(#card)"><rect width="{W}" height="{H}" fill="{BG}"/>{"".join(o)}</g>'
            f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="8" fill="none" stroke="{LINE}"/>'
            '</svg>\n')


if __name__ == "__main__":
    with open("assets/header-terminal.svg", "w", encoding="utf-8") as f:
        f.write(build())
    print("wrote assets/header-terminal.svg")
