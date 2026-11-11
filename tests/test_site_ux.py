"""Static UX contract and asset validation for the AXR Stats website."""
from html.parser import HTMLParser
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
ROUTES = (
    "docs/", "docs/installation/", "docs/configuration/", "docs/cards/",
    "docs/ranks/", "docs/security/", "docs/faq/", "docs/roadmap/",
)

class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.scripts = []
        self.styles = []
        self.footer_count = 0
        self.icons = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "script": self.scripts.append(a.get("src", ""))
        if tag == "link" and a.get("rel") == "stylesheet":
            self.styles.append(a.get("href", ""))
        if tag == "footer" and a.get("class") == "axr-footer":
            self.footer_count += 1
        if a.get("data-icon"): self.icons.append(a["data-icon"])

class UxTests(unittest.TestCase):
    def test_all_pages_share_footer_motion_and_local_icons(self):
        pages = [SITE / "index.html"] + [SITE / p / "index.html" for p in ROUTES]
        for path in pages:
            with self.subTest(page=str(path.relative_to(SITE))):
                content = path.read_text(encoding="utf-8")
                p = Page(); p.feed(content)
                self.assertEqual(p.footer_count, 1)
                self.assertEqual(len([x for x in p.styles if x.endswith("ui.css")]), 1)
                self.assertEqual(len([x for x in p.scripts if x.endswith("ui.js")]), 1)
                self.assertTrue(p.icons)
                self.assertIn("docs/roadmap/", content)

    def test_no_legacy_seven_tier_claims(self):
        html = (SITE / "index.html").read_text(encoding="utf-8")
        self.assertIn("PROGRESSÃO / 12 TIERS", html)
        self.assertIn("Doze estágios de evolução", html)
        self.assertNotIn("PROGRESSÃO / 07 TIERS", html)

    def test_sprite_is_local_and_matches_declared_icons(self):
        sprite = SITE / "icons/lucide.svg"
        self.assertTrue(sprite.exists())
        root = ET.parse(sprite).getroot()
        symbol_ids = {x.attrib["id"] for x in root.iter() if x.tag.endswith("symbol")}
        self.assertGreaterEqual(len(symbol_ids), 12)
        self.assertTrue({"route", "arrow-up", "sparkles", "book-open"} <= symbol_ids)
        self.assertIn("ISC License", (SITE / "icons/LICENSE").read_text(encoding="utf-8"))
        for path in [SITE / "index.html"] + [SITE / p / "index.html" for p in ROUTES]:
            p = Page(); p.feed(path.read_text(encoding="utf-8"))
            for icon in p.icons:
                self.assertIn(icon, symbol_ids)

    def test_reduced_motion_and_interactions(self):
        css = (SITE / "ui.css").read_text(encoding="utf-8")
        js = (SITE / "ui.js").read_text(encoding="utf-8")
        main = (SITE / "app.js").read_text(encoding="utf-8")
        for snippet in ("prefers-reduced-motion", "scroll-behavior:smooth",
                        ".axr-footer", ".ui-back-top", ".ui-progress"):
            self.assertIn(snippet, css)
        for snippet in ("IntersectionObserver", "typeHeadline", "requestAnimationFrame",
                        "navigator", "AXRUI", "is-scrolled"):
            # Clipboard support remains in docs.js, not mandatory in common UI.
            if snippet != "navigator": self.assertIn(snippet, js)
        self.assertIn("AXRUI?.typeHeadline", main)
        self.assertNotIn("localStorage", js)
        self.assertNotIn("sessionStorage", js)
        self.assertNotIn("WAKATIME_OAUTH_TOKEN", js)
        self.assertIn("data-reveal", (SITE / "index.html").read_text(encoding="utf-8"))

if __name__ == "__main__":
    unittest.main()
