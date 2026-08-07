#!/usr/bin/env python3
"""
render_heatmap_svg.py — Draws the classic 53-week x 7-day contribution
calendar as rounded, colored boxes using a GitHub-ish green ramp, with a
diagonal line-after-line slide-down reveal on load (freezes after playing
once — no looping "glow").

Usage:
    python scripts/render_heatmap_svg.py

Reads:  data/contributions.json
Writes: contrib-heatmap.svg
"""

import json
from datetime import datetime

# none -> brightest (level 0 is a-tone-top end)
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]

IN_PATH = "data/contributions.json"
OUT_PATH = "contrib-heatmap.svg"

BOX = 11
GAP = 3
CELL = BOX + GAP
LEFT_MARGIN = 20
TOP_MARGIN = 20
LEGEND_HEIGHT = 28
FOOTER_HEIGHT = 24
WIDTH = LEFT_MARGIN + CELL * 53 + 20


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main():
    with open(IN_PATH) as f:
        data = json.load(f)

    days = data["days"]
    stats = data.get("stats", {})

    # Bucket days into weeks (columns) based on their weekday (Sun=0..Sat=6)
    weeks = []
    week = [None] * 7
    for d in days:
        dt = datetime.strptime(d["date"], "%Y-%m-%d")
        weekday = (dt.weekday() + 1) % 7  # convert Mon=0 -> Sun=0
        week[weekday] = d
        if weekday == 6:
            weeks.append(week)
            week = [None] * 7
    if any(week):
        weeks.append(week)

    height = TOP_MARGIN + CELL * 7 + LEGEND_HEIGHT + FOOTER_HEIGHT

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {height}" '
        f'width="{WIDTH}" height="{height}" font-family="monospace" font-size="11">',
        f'<rect width="{WIDTH}" height="{height}" fill="transparent" />',
    ]

    max_diag = len(weeks) + 7  # max value of (week_idx + day_idx) for stagger timing

    for w_idx, week in enumerate(weeks):
        for d_idx, day in enumerate(week):
            if day is None:
                continue
            level = min(day.get("level", 0), len(PALETTE) - 1)
            color = PALETTE[level]
            x = LEFT_MARGIN + w_idx * CELL
            y = TOP_MARGIN + d_idx * CELL
            diag = w_idx + d_idx
            begin = 0.15 + (diag / max_diag) * 1.6
            parts.append(
                f'<rect x="{x}" y="{y - 6}" width="{BOX}" height="{BOX}" rx="2" '
                f'fill="{color}" opacity="0">'
                f'<title>{esc(day["date"])}: {day.get("count", 0)} contributions</title>'
                f'<animate attributeName="opacity" begin="{begin:.3f}s" dur="0.25s" '
                f'to="1" fill="freeze" />'
                f'<animate attributeName="y" begin="{begin:.3f}s" dur="0.25s" '
                f'from="{y - 6}" to="{y}" fill="freeze" calcMode="spline" '
                f'keySplines="0.25 0.1 0.25 1" />'
                f'</rect>'
            )

    # Less -> More legend
    legend_y = TOP_MARGIN + CELL * 7 + 14
    parts.append(f'<text x="{LEFT_MARGIN}" y="{legend_y}" fill="#8b949e">Less</text>')
    lx = LEFT_MARGIN + 34
    for level, color in enumerate(PALETTE):
        parts.append(f'<rect x="{lx}" y="{legend_y - 10}" width="{BOX}" height="{BOX}" rx="2" fill="{color}" />')
        lx += CELL
    parts.append(f'<text x="{lx + 4}" y="{legend_y}" fill="#8b949e">More</text>')

    # Footer stats
    total = stats.get("total_last_year", sum(d.get("count", 0) for d in days))
    streak = stats.get("current_streak", 0)
    footer_y = legend_y + 22
    footer_text = f"{total:,} contributions in the last year  ·  current streak {streak} day{'s' if streak != 1 else ''}"
    parts.append(f'<text x="{LEFT_MARGIN}" y="{footer_y}" fill="#c9d1d9">{esc(footer_text)}</text>')

    parts.append("</svg>")

    with open(OUT_PATH, "w") as f:
        f.write("\n".join(parts))
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
