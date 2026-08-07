#!/usr/bin/env python3
"""
make_info_card.py — Hand-authors a small neofetch-style SVG info card:
a title bar, then colored key/value rows (Now / Prev / Stack / Highlights).

This is static content you edit by hand — the card is for the story
numbers the contribution graph can't tell.

Usage:
    python scripts/make_info_card.py
    STATIC=1 python scripts/make_info_card.py   # frozen frame, no animation

Writes: info-card.svg
"""

import os

# ---- Edit this to your own info -------------------------------------------
USERNAME = "VishnuSunilKumar"

FIELDS = [
    ("Now", "Building full-stack apps & exploring AI tooling"),
    ("Prev", "Shipped 10+ side projects across web & mobile"),
    ("Stack", "TypeScript, Python, React, Node, PostgreSQL"),
    ("Highlights", "Open source contributor · Hackathon builder"),
]
# -----------------------------------------------------------------------------

WIDTH = 490
LINE_HEIGHT = 26
PADDING_TOP = 56
FONT_SIZE = 14
TITLE_BAR_HEIGHT = 36

KEY_COLOR = "#79c0ff"
VAL_COLOR = "#c9d1d9"
TITLE_COLOR = "#8b949e"
BG = "#0d1117"
STATIC = os.environ.get("STATIC") == "1"

OUT_PATH = "info-card.svg"


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main():
    height = PADDING_TOP + LINE_HEIGHT * len(FIELDS) + 24

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {height}" '
        f'width="{WIDTH}" height="{height}" font-family="monospace" font-size="{FONT_SIZE}">',
        f'<rect width="{WIDTH}" height="{height}" rx="8" fill="{BG}" />',
        f'<text x="16" y="24" fill="{TITLE_COLOR}">{esc(USERNAME)}@github</text>',
        f'<line x1="16" y1="{TITLE_BAR_HEIGHT}" x2="{WIDTH - 16}" y2="{TITLE_BAR_HEIGHT}" '
        f'stroke="#30363d" stroke-width="1" />',
    ]

    for i, (key, val) in enumerate(FIELDS):
        y = PADDING_TOP + i * LINE_HEIGHT
        line = (
            f'<text x="16" y="{y}">'
            f'<tspan fill="{KEY_COLOR}">{esc(key)}:</tspan> '
            f'<tspan fill="{VAL_COLOR}">{esc(val)}</tspan>'
            f'</text>'
        )
        if not STATIC:
            begin = 0.4 + i * 0.15
            line = (
                f'<g opacity="0" transform="translate(-12,0)">'
                f'{line}'
                f'<animate attributeName="opacity" begin="{begin}s" dur="0.35s" '
                f'to="1" fill="freeze" />'
                f'<animateTransform attributeName="transform" type="translate" '
                f'begin="{begin}s" dur="0.35s" from="-12,0" to="0,0" fill="freeze" '
                f'calcMode="spline" keySplines="0.25 0.1 0.25 1" />'
                f'</g>'
            )
        parts.append(line)

    parts.append("</svg>")

    with open(OUT_PATH, "w") as f:
        f.write("\n".join(parts))
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
