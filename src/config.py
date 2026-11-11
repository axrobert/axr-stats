"""Small, validated configuration contract for AXR Stats Phase 2.

Configuration changes presentation and output, never credentials or WakaTime data.
"""
from __future__ import annotations

import json
from pathlib import Path
import re

THEME_NAMES = frozenset(("midnight", "graphite", "aurora"))
COLOR_KEYS = frozenset(("background", "surface", "outline", "text", "muted", "accent", "success"))
CARD_IDS = ("lifetime", "languages", "activity", "ranking", "heatmap", "emblem")
LAYOUTS = frozenset(("stacked", "paired"))
SIZES = frozenset(("compact", "standard", "large"))
ROOT_KEYS = frozenset(("theme", "timezone", "output", "colors", "cards", "layout", "size", "language_rows", "typography", "show_rank_stars"))
HEX = re.compile(r"#[0-9a-fA-F]{6}\Z")


def read_config(path: Path | None) -> dict:
    if path is None:
        return {}
    file = Path(path)
    if not file.is_file():
        raise RuntimeError(f"AXR configuration not found: {file}")
    if file.stat().st_size > 64_000:
        raise RuntimeError("AXR config exceeds 64 KB; expected a small JSON object")
    try:
        data = json.loads(file.read_text(encoding="utf-8"))
    except (ValueError, UnicodeError) as exc:
        raise RuntimeError("AXR configuration must be valid UTF-8 JSON") from None
    if not isinstance(data, dict):
        raise RuntimeError("AXR config must contain a JSON object")
    unknown = sorted(set(data) - ROOT_KEYS)
    if unknown:
        raise RuntimeError(f"Unknown AXR configuration fields: {', '.join(unknown)}")
    theme = data.get("theme")
    if theme is not None and theme not in THEME_NAMES:
        raise RuntimeError("Theme must be midnight, graphite or aurora")
    timezone = data.get("timezone")
    if timezone is not None and (not isinstance(timezone, str) or not timezone or len(timezone) > 100):
        raise RuntimeError("Timezone must be a valid IANA timezone name")
    output = data.get("output")
    if output is not None:
        if not isinstance(output, str) or not output or len(output) > 200:
            raise RuntimeError("Output must be a relative destination directory")
        relative = Path(output)
        if (relative.is_absolute() or ".." in relative.parts or
                any(part.lower() in (".git", ".github") for part in relative.parts) or
                str(relative) in (".", "") or
                '\\' in output or any(ord(char) < 32 for char in output)):
            raise RuntimeError("Output must be a dedicated relative directory")
    colors = data.get("colors", {})
    if not isinstance(colors, dict):
        raise RuntimeError("Colors must be an object of hex color values")
    invalid = sorted(set(colors) - COLOR_KEYS)
    if invalid:
        raise RuntimeError(f"Unknown AXR color tokens: {', '.join(invalid)}")
    for name, value in colors.items():
        if not isinstance(value, str) or not HEX.fullmatch(value):
            raise RuntimeError(f"AXR color '{name}' must use #RRGGBB")
    selected = data.get("cards")
    if selected is not None:
        if (not isinstance(selected, list) or not selected or
                len(selected) > len(CARD_IDS) or
                any(not isinstance(item, str) or item not in CARD_IDS for item in selected) or
                len(selected) != len(set(selected))):
            raise RuntimeError("Cards must be a non-empty, unique list of supported card names")
    if "layout" in data and (not isinstance(data["layout"], str) or data["layout"] not in LAYOUTS):
        raise RuntimeError("Layout must be stacked or paired")
    if "size" in data and (not isinstance(data["size"], str) or data["size"] not in SIZES):
        raise RuntimeError("Size must be compact, standard or large")
    if "language_rows" in data:
        value = data["language_rows"]
        if type(value) is not int or value not in (5, 8, 10):
            raise RuntimeError("language_rows must be 5, 8 or 10")
    if "typography" in data and (not isinstance(data["typography"], str) or
                                 data["typography"] not in ("compact", "standard", "large")):
        raise RuntimeError("typography must be compact, standard or large")
    if "show_rank_stars" in data and type(data["show_rank_stars"]) is not bool:
        raise RuntimeError("show_rank_stars must be true or false")
    return data


def choose(cli_value, config: dict, key: str, fallback):
    return cli_value if cli_value is not None else config.get(key, fallback)
