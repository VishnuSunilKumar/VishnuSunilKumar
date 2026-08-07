#!/usr/bin/env python3
"""
make_ascii_svg.py — Downsample a prepped grayscale image to a character
grid and render it as a self-typing monochrome SVG.

Usage:
    python scripts/make_ascii_svg.py

Reads:  source-prepped.png
Writes: avi-ascii.svg   (rename OUT_PATH below if you want a different name)
"""

from PIL import Image

# Sparse (bright) -> dense (dark). Leading space clears the background to
# nothing so the portrait "prints" on transparent/white.
RAMP = " .:-=+*#%@"

GRID_W = 100
GRID_H = 56
CHAR_W = 7      # px per character cell (monospace-ish)
CHAR_H = 11
GAMMA = 0.85    # <1 spreads midtones out a little instead of clumping dark
FONT_SIZE = 12
FILL = "#8b949e"     # single light-gray fill — monochrome, high contrast
BG = "transparent"

IN_PATH = "source-prepped.png"
OUT_PATH = "avi-ascii.svg"


def pixel_to_char(value: int) -> str:
    """0 (black) -> dense glyph, 255 (white) -> space.
    Gamma-corrects the brightness before mapping so midtones (facial
    features, jacket folds) get spread across more of the ramp instead
    of clumping at the dense end.
    """
    darkness = (255 - value) / 255       # 0 = white/background, 1 = black
    darkness = darkness ** GAMMA
    idx = int(darkness * (len(RAMP) - 1))
    return RAMP[idx]


def image_to_ascii_rows(img: Image.Image, cols: int, rows: int):
    img = img.convert("L").resize((cols, rows), Image.LANCZOS)
    pixels = list(img.getdata())
    grid = []
    for r in range(rows):
        row_chars = []
        for c in range(cols):
            row_chars.append(pixel_to_char(pixels[r * cols + c]))
        grid.append("".join(row_chars))
    return grid


def render_svg(rows, cols_w, rows_h, char_w, char_h, font_size, fill):
    width = cols_w * char_w
    height = rows_h * char_h

    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}" font-family="monospace" font-size="{font_size}">',
        f'<style>.row {{ fill: {fill}; white-space: pre; }}</style>',
    ]

    for i, row in enumerate(rows):
        y = (i + 1) * char_h
        escaped = (
            row.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )
        row_id = f"row{i}"
        svg_parts.append(
            f'<text id="{row_id}" class="row" x="0" y="{y}" '
            f'clip-path="url(#clip{i})" opacity="0">{escaped}'
            f'<animate attributeName="opacity" begin="{i * 0.03}s" '
            f'dur="0.01s" to="1" fill="freeze" />'
            f'</text>'
        )
        # horizontal "wipe" clip that reveals the row left-to-right
        svg_parts.append(
            f'<clipPath id="clip{i}"><rect x="0" y="{y - char_h}" width="0" height="{char_h}">'
            f'<animate attributeName="width" begin="{i * 0.03}s" dur="0.6s" '
            f'from="0" to="{width}" fill="freeze" calcMode="spline" '
            f'keySplines="0.25 0.1 0.25 1" />'
            f'</rect></clipPath>'
        )

    svg_parts.append("</svg>")
    return "\n".join(svg_parts)


def main():
    img = Image.open(IN_PATH)
    rows = image_to_ascii_rows(img, GRID_W, GRID_H)
    svg = render_svg(rows, GRID_W, GRID_H, CHAR_W, CHAR_H, FONT_SIZE, FILL)
    with open(OUT_PATH, "w") as f:
        f.write(svg)
    print(f"Wrote {OUT_PATH} writes avi-ascii.svg  ({GRID_W}x{GRID_H} chars)")


if __name__ == "__main__":
    main()
