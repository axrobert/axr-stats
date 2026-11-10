from html.parser import HTMLParser
from pathlib import Path
import re
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"

class Parser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.links = []
        self.images = []
        self.lang = None
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a: self.ids.add(a["id"])
        if tag == "html": self.lang = a.get("lang")
        if tag == "a": self.links.append(a.get("href", ""))
        if tag == "img": self.images.append(a.get("src", ""))

class PagesRedesignTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (SITE / "index.html").read_text(encoding="utf-8")
        cls.css = (SITE / "style.css").read_text(encoding="utf-8")
        cls.js = (SITE / "app.js").read_text(encoding="utf-8")
        cls.dom = Parser()
        cls.dom.feed(cls.html)

    def test_navigation_and_document(self):
        self.assertEqual(self.dom.lang, "pt-BR")
        for target in ("conteudo", "inicio", "explorar", "ranks", "cards", "guia",
                       "rank-grid", "rank-dialog", "rank-search", "hours-input",
                       "hero-title", "hero-medal", "sim-progress"):
            self.assertIn(target, self.dom.ids)
        for href in self.dom.links:
            if href.startswith("#"): self.assertIn(href[1:], self.dom.ids, href)
            self.assertFalse(href.startswith("http://"), href)

    def test_static_assets(self):
        ET.parse(SITE / "favicon.svg")
        for path in self.dom.images:
            self.assertTrue((ROOT / path if path.startswith("assets/") else SITE / path).exists(), path)
        images = re.findall(r'image:\s*"(0[1-7]-[a-z]+\.png)"', self.js)
        self.assertEqual(len(set(images)), 7)
        for name in images: self.assertTrue((ROOT / "assets/badges" / name).exists(), name)

    def test_accessibility_and_interaction_wiring(self):
        for target in ("rank-dialog", "rank-grid", "rank-search", "hours-input",
                       "close-dialog", "next-slide", "prev-slide", "menu-toggle"):
            self.assertTrue(target in self.html or target in self.js, target)
        for fragment in ("aria-expanded", "aria-live"): self.assertIn(fragment, self.html)
        for fragment in ("showModal()", "dialog.close()", "updateFilter",
                         "renderSimulation", "selectSlide"): self.assertIn(fragment, self.js)
        self.assertIn("prefers-reduced-motion", self.css)
        self.assertIn("@media(max-width:500px)", self.css)

    def test_no_tokens_or_remote_scripts(self):
        for fragment in ("localStorage", "sessionStorage", "WAKATIME_OAUTH_TOKEN", "eval("):
            self.assertNotIn(fragment, self.js)
        self.assertNotIn('<script src="https://', self.html)

if __name__ == "__main__":
    unittest.main()
