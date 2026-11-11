#!/usr/bin/env python3
"""Reproducibly rasterize the five original vector stage marks.

SVG is the editable source; PNG is an optimized transparent export. This does
not touch rank badges, their thresholds, WakaTime OAuth or unrelated images.
"""
from pathlib import Path
from io import BytesIO
from PIL import Image
import cairosvg

BASE=Path(__file__).resolve().parents[1]/"site/roadmap/icons"

def build():
    sources=sorted(BASE.glob("*.svg"))
    if len(sources)!=5:
        raise RuntimeError("Expected exactly five original roadmap SVG marks")
    for source in sources:
        png=cairosvg.svg2png(url=str(source),output_width=228,output_height=208)
        image=Image.open(BytesIO(png)).convert("RGBA")
        if image.getbbox() is None:
            raise RuntimeError(f"Empty icon: {source.name}")
        target=source.with_suffix(".png")
        image.save(target,format="PNG",optimize=True,compress_level=9)
        with Image.open(target) as check:
            check.verify()
        print(f"{source.name} -> {target.name} ({target.stat().st_size} bytes)")

if __name__=="__main__":
    build()
