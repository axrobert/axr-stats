"""Phase 2 browser palette export contract and route availability."""
from pathlib import Path
from html.parser import HTMLParser
import re
import unittest

ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/"site"

class Markup(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids=set()
        self.colors=[]
        self.presets=[]
    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        if d.get("id"): self.ids.add(d["id"])
        if "data-color" in d: self.colors.append(d["data-color"])
        if "data-theme" in d: self.presets.append(d["data-theme"])

class ThemeWorkbenchTests(unittest.TestCase):
    def test_interface_matches_python_config_schema(self):
        from sys import path
        import json
        path.insert(0,str(ROOT/"src"))
        import config
        html=(SITE/"customize/index.html").read_text(encoding="utf-8")
        dom=Markup();dom.feed(html)
        self.assertEqual(set(dom.colors),set(config.COLOR_KEYS))
        self.assertEqual(set(dom.presets),set(config.THEME_NAMES))
        for marker in ("theme-preview-image","theme-json","copy-theme","download-theme","theme-feedback"):
            self.assertIn(marker,dom.ids)
        self.assertIn('id="main-nav"',html)

    def test_browser_palette_is_static_and_has_no_secrets(self):
        js=(SITE/"customize/customize.js").read_text(encoding="utf-8")
        self.assertIn("URL.createObjectURL",js)
        self.assertIn("navigator.clipboard.writeText",js)
        self.assertNotIn("fetch(",js)
        self.assertNotIn("localStorage",js)
        self.assertNotIn("WAKATIME_OAUTH_TOKEN",js)
        self.assertNotIn("innerHTML",js)
        self.assertIn("aria-pressed",js)

    def test_phase_two_is_started_in_roadmap(self):
        html=(SITE/"roadmap/index.html").read_text(encoding="utf-8")
        self.assertIn('id="fase-2" data-rm-status="active"',html)
        self.assertIn('FASE 02 · EM ANDAMENTO',html)
        self.assertIn('href="../customize/"',html)
        self.assertIn('href="customize/"',(SITE/"index.html").read_text(encoding="utf-8"))

if __name__=="__main__":
    unittest.main()
