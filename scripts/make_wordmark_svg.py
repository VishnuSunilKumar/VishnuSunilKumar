#!/usr/bin/env python3
"""
make_wordmark_svg.py — Renders your initials as a 3D isometric ASCII
wordmark (via pyfiglet's 'isometric1' font) as a self-animating SVG:
the block letters wipe in left-to-right like the portrait, then rock
gently on their vertical axis before settling upright.

Usage:
    python scripts/make_wordmark_svg.py
    python scripts/make_wordmark_svg.py --mode rock   # default
    python scripts/make_wordmark_svg.py --mode static # no rock, just wipe-in
    STATIC=1 python scripts/make_wordmark_svg.py       # frozen single frame

Writes: wordmark.svg
"""

import argparse
import os

import pyfiglet

TEXT = "VSK"
FONT = "isometric1"

CHAR_W = 8
CHAR_H = 15
FONT_SIZE = 15
FILL = "#22d3ee"      # cyan accent, matches the "Live Terminal" badge
BG = "transparent"

OUT_PATH = "wordmark.svg"
STATIC_FRAME = os.environ.get("STATIC") == "1"


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def render_svg(rows, mode: str):
    cols = max(len(r) for r in rows)
    width = cols * CHAR_W
    height = len(rows) * CHAR_H + 20  # headroom for the rock animation

    wipe_dur = 0.6
    stagger = 0.05
    total_wipe = stagger * len(rows) + wipe_dur

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}" font-family="monospace" font-size="{FONT_SIZE}">',
        f'<style>.row {{ fill: {FILL}; white-space: pre; }}</style>',
        f'<g transform="translate({width/2},{height/2})" style="transform-box: fill-box; '
        f'transform-origin: center;">',
        f'<g transform="translate({-width/2},{-height/2})">',
    ]

    for i, row in enumerate(rows):
        y = (i + 1) * CHAR_H
        escaped = esc(row)
        begin = i * stagger

        if STATIC_FRAME:
            parts.append(f'<text class="row" x="0" y="{y}">{escaped}</text>')
            continue

        row_id = f"wrow{i}"
        parts.append(
            f'<text id="{row_id}" class="row" x="0" y="{y}" '
            f'clip-path="url(#wclip{i})" opacity="0">{escaped}'
            f'<animate attributeName="opacity" begin="{begin:.3f}s" '
            f'dur="0.01s" to="1" fill="freeze" />'
            f'</text>'
        )
        parts.append(
            f'<clipPath id="wclip{i}"><rect x="0" y="{y - CHAR_H}" width="0" height="{CHAR_H}">'
            f'<animate attributeName="width" begin="{begin:.3f}s" dur="{wipe_dur}s" '
            f'from="0" to="{width}" fill="freeze" calcMode="spline" '
            f'keySplines="0.25 0.1 0.25 1" />'
            f'</rect></clipPath>'
        )

    parts.append("</g>")  # inner translate

    if not STATIC_FRAME and mode == "rock":
        # Rock on the vertical axis (skewX fakes a turn), then settle upright.
        rock_begin = total_wipe + 0.1
        parts.append(
            f'<animateTransform attributeName="transform" type="skewX" '
            f'begin="{rock_begin:.3f}s" dur="1.6s" fill="freeze" '
            f'values="0;10;-8;5;-3;1;0" '
            f'keyTimes="0;0.18;0.4;0.6;0.78;0.92;1" '
            f'calcMode="spline" '
            f'keySplines="0.3 0 0.7 1;0.3 0 0.7 1;0.3 0 0.7 1;0.3 0 0.7 1;0.3 0 0.7 1;0.3 0 0.7 1" />'
        )

    parts.append("</g>")  # outer translate (rock pivot)
    parts.append("</svg>")
    return "\n".join(parts)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["rock", "static"], default="rock")
    parser.add_argument("--text", default=TEXT)
    args = parser.parse_args()

    art = pyfiglet.figlet_format(args.text, font=FONT)
    rows = art.rstrip("\n").split("\n")
    # drop fully-blank leading/trailing rows for a tighter box
    while rows and not rows[0].strip():
        rows.pop(0)
    while rows and not rows[-1].strip():
        rows.pop()

    svg = render_svg(rows, args.mode)
    with open(OUT_PATH, "w") as f:
        f.write(svg)
    print(f"Wrote {OUT_PATH} ({len(rows)} rows, mode={args.mode})")


if __name__ == "__main__":
    main()
