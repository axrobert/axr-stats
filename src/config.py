"""Small, validated configuration contract for AXR Stats Phase 2.

Configuration changes presentation and output, never credentials or WakaTime data.
"""
from __future__ import annotations

import json
from pathlib import Path
import re

THEME_NAMES = frozenset(("midnight", "graphite", "aurora"))
COLOR_KEYS = frozenset(("background", "surface", "outline", "text", "muted", "accent", "success"))
ROOT_KEYS = frozenset(("theme", "timezone", "output", "colors"))
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
        if relative.is_absolute() or ".." in relative.parts or str(relative) in (".", ""):
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
    return data


def choose(cli_value, config: dict, key: str, fallback):
    return cli_value if cli_value is not None else config.get(key, fallback)
