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
from config import read_config, choose, CARD_IDS
from layouts import selected_files, snippet

SVG_FILES = ("lifetime.svg", "languages.svg", "activity.svg",
             "ranking.svg", "heatmap.svg", "emblem.svg")
PNG_FILES = ("lifetime.png", "emblem.png")
OUTPUT_FILES = SVG_FILES + PNG_FILES
SNIPPET_FILE = "README-snippet.md"
MANAGED_FILES = OUTPUT_FILES + (SNIPPET_FILE,)


def check_output_path(destination: Path, *, require_relative: bool = False) -> Path:
    """Reject repository-root, Git internals, traversal and symlink ancestors.

    Only the CLI requires a relative directory. Library calls can use absolute
    temporary directories for isolated tests.
    """
    destination = Path(destination)
    if (require_relative and destination.is_absolute()) or ".." in destination.parts:
        raise RuntimeError("Output must be a dedicated relative directory inside the repository")
    if any(part.lower() in (".git", ".github") for part in destination.parts):
        raise RuntimeError("Output cannot target Git or GitHub internals")
    if destination == Path("."):
        raise RuntimeError("Output must not target the repository root")
    for node in (destination, *destination.parents):
        if node.is_symlink():
            raise RuntimeError("Output path contains a symlink directory")
    resolved = destination.resolve()
    if resolved == Path.cwd().resolve():
        raise RuntimeError("Output must be a dedicated directory, not the repository root")
    if require_relative:
        root = Path.cwd().resolve()
        if not resolved.is_relative_to(root):
            raise RuntimeError("Output directory must remain inside the repository")
    return resolved



def validate(directory: Path, published: tuple[str, ...] | None = None) -> None:
    """Reject incomplete, malformed, or empty generated assets."""
    published = OUTPUT_FILES if published is None else tuple(published)
    if not published or any(name not in MANAGED_FILES for name in published):
        raise RuntimeError("Invalid selected output files")
    for filename in SVG_FILES:
        if filename not in published:
            continue
        item = directory / filename
        if not item.is_file() or item.stat().st_size < 100:
            raise RuntimeError(f"Missing or empty generated SVG: {filename}")
        root = ET.parse(item).getroot()
        if root.tag != "{http://www.w3.org/2000/svg}svg":
            raise RuntimeError(f"Invalid SVG root: {filename}")
    for filename in PNG_FILES:
        if filename not in published:
            continue
        item = directory / filename
        if not item.is_file():
            raise RuntimeError(f"Missing generated PNG: {filename}")
        with Image.open(item) as image:
            image.verify()

    if SNIPPET_FILE in published:
        item = directory / SNIPPET_FILE
        if not item.is_file() or item.stat().st_size < 50:
            raise RuntimeError("Missing README snippet")


def publish(staged: Path, destination: Path, published: tuple[str, ...] | None = None) -> None:
    """Swap validated cards together while preserving unrelated user files.

    Rolls back on a swap error. Directory renames minimize partial updates,
    but a process/power crash between renames is not a durable ACID transaction.
    """
    published = OUTPUT_FILES if published is None else tuple(published)
    if not published or any(name not in MANAGED_FILES for name in published):
        raise RuntimeError("Invalid publication selection")
    destination = check_output_path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    candidate = Path(tempfile.mkdtemp(prefix=".axr-candidate-", dir=destination.parent))
    backup = None
    try:
        if destination.exists():
            if not destination.is_dir():
                raise RuntimeError("Output destination is not a directory")
            shutil.copytree(destination, candidate, dirs_exist_ok=True, symlinks=True)
        # Remove *only* previously generated names that are now deselected.
        # Never remove unrelated user content, including any other files.
        for filename in MANAGED_FILES:
            if filename not in published:
                (candidate / filename).unlink(missing_ok=True)
        for filename in published:
            target = candidate / filename
            # copytree(..., symlinks=True) preserves attacker-controlled links.
            # Copying over those links would write *outside* the staging directory.
            if target.is_symlink():
                target.unlink()
            elif target.exists() and not target.is_file():
                raise RuntimeError(f"Managed output name is not a regular file: {filename}")
            shutil.copy2(staged / filename, target)
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
    settings = read_config(config)
    selection = settings.get("cards", CARD_IDS)
    expected = selected_files(selection)
    has_readme = "layout" in settings or "size" in settings
    if has_readme:
        expected += (SNIPPET_FILE,)
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
        if "lifetime" in selection or "emblem" in selection:
            render(staged / "lifetime.svg", tier, assets,
                   staged / "lifetime.png", staged / "emblem.png")
        if has_readme:
            (staged / SNIPPET_FILE).write_text(
                snippet(selection, settings.get("layout", "stacked"),
                        settings.get("size", "standard"), output),
                encoding="utf-8")
        validate(staged, expected)
        publish(staged, output, expected)
    print(f"AXR Stats: published {len(expected)} validated files to {output}")


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
        check_output_path(output, require_relative=True)
        theme = choose(options.theme, configuration, "theme", "midnight")
        timezone = choose(options.timezone, configuration, "timezone", "UTC")
        run(output, theme, timezone, options.assets, config=options.config)
    except (RuntimeError, ValueError, OSError, ET.ParseError) as error:
        raise SystemExit(f"AXR Stats error: {error}") from None


if __name__ == "__main__":
    main()
