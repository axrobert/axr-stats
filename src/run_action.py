#!/usr/bin/env python3
"""Generate and publish a complete validated batch, preserving old output on failure."""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil
import tempfile
import xml.etree.ElementTree as ET

from PIL import Image

from axr_stats import main as generate
from render_rank_png import render
from config import read_config, choose

SVG_FILES = ("lifetime.svg", "languages.svg", "activity.svg",
             "ranking.svg", "heatmap.svg", "emblem.svg")
PNG_FILES = ("lifetime.png", "emblem.png")
OUTPUT_FILES = SVG_FILES + PNG_FILES


def validate(directory: Path) -> None:
    """Reject incomplete, malformed, or empty generated assets."""
    for filename in SVG_FILES:
        item = directory / filename
        if not item.is_file() or item.stat().st_size < 100:
            raise RuntimeError(f"Missing or empty generated SVG: {filename}")
        root = ET.parse(item).getroot()
        if root.tag != "{http://www.w3.org/2000/svg}svg":
            raise RuntimeError(f"Invalid SVG root: {filename}")
    for filename in PNG_FILES:
        item = directory / filename
        if not item.is_file():
            raise RuntimeError(f"Missing generated PNG: {filename}")
        with Image.open(item) as image:
            image.verify()


def publish(staged: Path, destination: Path) -> None:
    """Swap validated cards together while preserving unrelated user files.

    Rolls back on a swap error. Directory renames minimize partial updates,
    but a process/power crash between renames is not a durable ACID transaction.
    """
    if destination.is_symlink():
        raise RuntimeError("Refusing to publish into a symlink directory")
    destination = destination.resolve()
    if destination == Path.cwd().resolve():
        raise RuntimeError("Output must be a dedicated directory, not the repository root")
    destination.parent.mkdir(parents=True, exist_ok=True)
    candidate = Path(tempfile.mkdtemp(prefix=".axr-candidate-", dir=destination.parent))
    backup = None
    try:
        if destination.exists():
            if not destination.is_dir():
                raise RuntimeError("Output destination is not a directory")
            shutil.copytree(destination, candidate, dirs_exist_ok=True, symlinks=True)
        for filename in OUTPUT_FILES:
            shutil.copy2(staged / filename, candidate / filename)
        if destination.exists():
            backup = Path(tempfile.mkdtemp(prefix=".axr-backup-", dir=destination.parent))
            backup.rmdir()
            os.replace(destination, backup)
        try:
            os.replace(candidate, destination)
        except BaseException:
            if backup is not None and backup.exists():
                os.replace(backup, destination)
            raise
        if backup is not None:
            shutil.rmtree(backup)
    finally:
        if candidate.exists():
            shutil.rmtree(candidate)


def run(output: Path, theme: str, timezone: str, assets: Path, config: Path | None = None) -> None:
    with tempfile.TemporaryDirectory(prefix="axr-generate-") as work:
        staged = Path(work)
        args = ["--output", str(staged), "--theme", theme, "--timezone", timezone]
        if config is not None:
            args.extend(["--config", str(config)])
        generate(args)
        tier_file = staged / ".rank-level"
        if not tier_file.is_file():
            raise RuntimeError("Rank level metadata not generated")
        tier = int(tier_file.read_text(encoding="ascii").strip())
        render(staged / "lifetime.svg", tier, assets,
               staged / "lifetime.png", staged / "emblem.png")
        validate(staged)
        publish(staged, output)
    print(f"AXR Stats: published {len(OUTPUT_FILES)} validated files to {output}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Publish AXR Stats profile cards safely")
    parser.add_argument("--output", default=None, type=Path)
    parser.add_argument("--theme", default=None, choices=("midnight", "graphite", "aurora"))
    parser.add_argument("--timezone", default=None)
    parser.add_argument("--config", default=None, type=Path)
    parser.add_argument("--assets", type=Path, default=Path(__file__).resolve().parents[1] / "assets/badges/current")
    options = parser.parse_args()
    try:
        configuration = read_config(options.config)
        output = Path(choose(options.output, configuration, "output", "assets/axr-stats"))
        theme = choose(options.theme, configuration, "theme", "midnight")
        timezone = choose(options.timezone, configuration, "timezone", "UTC")
        run(output, theme, timezone, options.assets, config=options.config)
    except (RuntimeError, ValueError, OSError, ET.ParseError) as error:
        raise SystemExit(f"AXR Stats error: {error}") from None


if __name__ == "__main__":
    main()
