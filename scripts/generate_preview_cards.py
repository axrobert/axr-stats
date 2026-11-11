#!/usr/bin/env python3
"""Build deterministic, fictional SVG previews from the production AXR renderer.

This script never accesses WakaTime, secrets, or the network. It is invoked
during static site deployment and browser QA, not by the public browser.
"""
from __future__ import annotations

import argparse
import datetime as dt
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from axr_stats import THEMES, activity_card, cards

FILES = ("lifetime.svg", "languages.svg", "activity.svg",
         "ranking.svg", "heatmap.svg", "emblem.svg")

def build(output: Path) -> list[Path]:
    # All values below are explicit demonstration data; no real user statistics.
    today = dt.date(2026, 11, 11)
    lifetime = {"data": {"total_seconds": 152 * 3600 + 29 * 60}}
    languages = [
        {"name": "JavaScript", "total_seconds": 51 * 3600 + 42 * 60},
        {"name": "Python", "total_seconds": 15 * 3600 + 32 * 60},
        {"name": "Markdown", "total_seconds": 15 * 3600 + 26 * 60},
        {"name": "HTML", "total_seconds": 13 * 3600 + 54 * 60},
        {"name": "CSS", "total_seconds": 13 * 3600 + 14 * 60},
        {"name": "TypeScript", "total_seconds": 10 * 3600 + 37 * 60},
        {"name": "Bash", "total_seconds": 6 * 3600 + 35 * 60},
        {"name": "Rust", "total_seconds": 4 * 3600 + 49 * 60},
        {"name": "SQL", "total_seconds": 4 * 3600 + 32 * 60},
    ]
    month = {"data": {"total_seconds": 14 * 3600 + 25 * 60,
                      "daily_average": 1600, "languages": languages}}
    week = {"data": {"total_seconds": 5 * 3600 + 2 * 60,
                     "daily_average": 5 * 3600 + 2 * 60}}
    all_langs = {"data": {"total_seconds": lifetime["data"]["total_seconds"],
                          "languages": languages}}
    pattern = (0, 1500, 5000, 7200, 2500, 0, 8400)
    summaries = {"data": [
        {"range": {"date": (today - dt.timedelta(days=29-i)).isoformat()},
         "grand_total": {"total_seconds": pattern[i % len(pattern)]}}
        for i in range(30)
    ]}
    leaders = {"current_user": {"rank": 2841}}  # FICTIONAL example, never official.
    content = cards(lifetime, month, week, summaries, leaders, today,
                    theme="midnight", all_langs=all_langs)
    content["activity.svg"] = activity_card(3 * 3600 + 15 * 60,
                                            week["data"]["daily_average"],
                                            THEMES["midnight"])
    output.mkdir(parents=True, exist_ok=True)
    result = []
    for filename in FILES:
        svg = content[filename]
        ET.fromstring(svg)
        path = output / filename
        path.write_text(svg, encoding="utf-8")
        result.append(path)
    return result

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path,
                        default=ROOT / "site/customize/previews")
    options = parser.parse_args()
    files = build(options.output)
    print("Generated six fictional card previews using AXR Stats' production renderer:")
    for file in files:
        print(" ", file)

if __name__ == "__main__":
    main()
