"""Regression checks for Phase 2.1: real, offline production-rendered SVG previews."""
from __future__ import annotations

import importlib.util
from html.parser import HTMLParser
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
sys.path.insert(0,str(ROOT/"scripts"))
import axr_stats
import config
from generate_preview_cards import FILES, build

class Controls(HTMLParser):
    def __init__(self):
        super().__init__();self.cards=[];self.ids=set()
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if "id" in a:self.ids.add(a["id"])
        if "data-preview-card" in a:self.cards.append(a["data-preview-card"])

class PreviewTests(unittest.TestCase):
    def test_fixture_uses_production_renderer_without_wakatime(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(axr_stats,"api",side_effect=AssertionError("Must be offline")):
                paths=build(Path(tmp))
            self.assertEqual(set(path.name for path in paths),set(FILES))
            for path in paths:
                root=ET.parse(path).getroot()
                self.assertEqual(root.tag,"{http://www.w3.org/2000/svg}svg")
                self.assertGreater(path.stat().st_size,100)
            lifetime=(Path(tmp)/"lifetime.svg").read_text()
            self.assertIn("data:image/png;base64,",lifetime)
            self.assertIn("152h 29m",lifetime)
            self.assertIn("Student",lifetime)
            ranking=(Path(tmp)/"ranking.svg").read_text()
            self.assertIn("#2841",ranking)
            self.assertIn("WakaTime public leaderboard",ranking)
            languages=(Path(tmp)/"languages.svg").read_text()
            self.assertIn("All-time coding languages",languages)
            self.assertIn("JavaScript",languages)

    def test_same_offline_fixture_is_deterministic(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            first=build(Path(a));second=build(Path(b))
            for left,right in zip(first,second):
                self.assertEqual(left.read_bytes(),right.read_bytes())

    def test_markup_matches_production_schema(self):
        text=(ROOT/"site/customize/index.html").read_text()
        dom=Controls();dom.feed(text)
        self.assertEqual(dom.cards,["lifetime","languages","activity","ranking","heatmap","emblem"])
        self.assertTrue({"theme-preview-image","theme-preview-message","download-preview","theme-preview-note"} <= dom.ids)
        js=(ROOT/"site/customize/preview.js").read_text()
        self.assertIn("new DOMParser()",js)
        self.assertIn("URL.createObjectURL",js)
        self.assertIn('data:image/png;base64,', (ROOT/"src/axr_stats.py").read_text())
        self.assertNotIn("WAKATIME_OAUTH_TOKEN",js)
        self.assertNotIn("eval(",js)
        self.assertNotIn("innerHTML",js)
        self.assertNotIn("localStorage",js)
        self.assertIn("new CustomEvent", (ROOT/"site/customize/customize.js").read_text())
        self.assertEqual(set(config.COLOR_KEYS),{"background","surface","outline","text","muted","accent","success"})

    def test_static_deploy_builds_preview_artifacts(self):
        for workflow in ("pages.yml","visual-qa.yml"):
            contents=(ROOT/".github/workflows"/workflow).read_text()
            self.assertIn("python3 scripts/generate_preview_cards.py --output _site/customize/previews",contents)
        self.assertIn("node --check site/customize/preview.js",(ROOT/".github/workflows/test.yml").read_text())

if __name__=="__main__":
    unittest.main()
