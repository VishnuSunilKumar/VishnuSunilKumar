#!/usr/bin/env python3
"""
fetch_contributions.py — Pulls real contribution data with no GitHub token
and no GraphQL API. GitHub serves the contribution calendar as public HTML
at https://github.com/users/<username>/contributions — the same fragment
the profile page itself uses.

Usage:
    python scripts/fetch_contributions.py

Writes: data/contributions.json
    {
      "username": "...",
      "days": [{"date": "YYYY-MM-DD", "count": 0, "level": 0}, ...],
      "stats": {
        "current_streak": 0,
        "longest_streak": 0,
        "best_day": {"date": "...", "count": 0},
        "monthly_totals": {"2026-01": 12, ...},
        "total_last_year": 0
      }
    }
"""

import json
import re
import sys
from collections import defaultdict
from datetime import datetime

import requests
from bs4 import BeautifulSoup

USERNAME = "VishnuSunilKumar"
URL = f"https://github.com/users/{USERNAME}/contributions"
OUT_PATH = "data/contributions.json"

# GitHub's data-level attribute maps roughly to 0 (none) .. 4 (most).
HEADERS = {"User-Agent": "Mozilla/5.0 (profile-readme-bot)"}

# Tooltip text looks like "No contributions on August 3rd." or
# "3 contributions on August 10th." — the count isn't in a data attribute
# anymore, so it has to be parsed out of the linked tool-tip's text.
COUNT_RE = re.compile(r"^(No|\d+)\s+contributions?", re.IGNORECASE)


def fetch_days(username: str):
    resp = requests.get(f"https://github.com/users/{username}/contributions", headers=HEADERS, timeout=20)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # Map cell id -> tooltip text, via the tool-tip's `for` attribute.
    tooltip_by_id = {}
    for tip in soup.select("tool-tip"):
        target = tip.get("for")
        if target:
            tooltip_by_id[target] = tip.get_text(strip=True)

    days = []
    cells = soup.select("td.ContributionCalendar-day")
    for cell in cells:
        date = cell.get("data-date")
        level = cell.get("data-level")
        if date is None:
            continue

        count = 0
        cell_id = cell.get("id")
        tooltip_text = tooltip_by_id.get(cell_id, "")
        match = COUNT_RE.match(tooltip_text)
        if match:
            raw = match.group(1)
            count = 0 if raw.lower() == "no" else int(raw)

        days.append({
            "date": date,
            "count": count,
            "level": int(level) if level is not None else 0,
        })
    return days


def compute_stats(days):
    if not days:
        return {}

    days_sorted = sorted(days, key=lambda d: d["date"])

    # Streaks
    current_streak = 0
    longest_streak = 0
    running = 0
    for d in days_sorted:
        if d["count"] > 0:
            running += 1
            longest_streak = max(longest_streak, running)
        else:
            running = 0
    # current streak: count back from the most recent day
    for d in reversed(days_sorted):
        if d["count"] > 0:
            current_streak += 1
        else:
            break

    best_day = max(days_sorted, key=lambda d: d["count"])

    monthly_totals = defaultdict(int)
    for d in days_sorted:
        month_key = d["date"][:7]
        monthly_totals[month_key] += d["count"]

    total_last_year = sum(d["count"] for d in days_sorted)

    return {
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": {"date": best_day["date"], "count": best_day["count"]},
        "monthly_totals": dict(monthly_totals),
        "total_last_year": total_last_year,
    }


def main():
    days = fetch_days(USERNAME)
    if not days:
        print("No contribution data found — GitHub markup may have changed.", file=sys.stderr)
        sys.exit(1)

    stats = compute_stats(days)
    output = {
        "username": USERNAME,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "days": days,
        "stats": stats,
    }

    with open(OUT_PATH, "w") as f:
        json.dump(output, f, indent=2)

    print(f"Wrote {OUT_PATH} — {len(days)} days, {stats.get('total_last_year', 0)} total contributions")


if __name__ == "__main__":
    main()
