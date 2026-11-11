"""Regression checks for the Visual Foundation and static documentation index."""
from html import unescape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
ROUTES = ("docs/", "docs/installation/", "docs/configuration/", "docs/cards/",
          "docs/ranks/", "docs/security/", "docs/faq/", "docs/roadmap/")

def normalize_text(value):
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", value))).strip()

class Sheets(HTMLParser):
    def __init__(self):
        super().__init__()
        self.styles = []
        self.inputs = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "link" and a.get("rel") == "stylesheet":
            self.styles.append(a.get("href", ""))
        if tag == "input" and a.get("id") == "docs-search":
            self.inputs.append(a)

class VisualFoundationTests(unittest.TestCase):
    def test_one_stylesheet_for_all_pages(self):
        pages = [SITE / "index.html"] + [SITE / route / "index.html" for route in ROUTES]
        for page in pages:
            with self.subTest(page=str(page)):
                parsed = Sheets()
                parsed.feed(page.read_text(encoding="utf-8"))
                self.assertEqual(len(parsed.styles), 1)
                self.assertTrue(parsed.styles[0].endswith("style.css"))
        for legacy in ("refinement.css", "ui.css", "docs/docs.css"):
            self.assertFalse((SITE / legacy).exists(), legacy)
        content = (SITE / "style.css").read_text(encoding="utf-8")
        self.assertIn("prefers-reduced-motion", content)
        self.assertIn(".docs-content h2", content)
        self.assertIn(".hero-stage", content)
        self.assertLess(len(content.encode("utf-8")), 85000)

    def test_search_index_covers_all_eight_docs_and_headings(self):
        obj = json.loads((SITE / "docs/search-index.json").read_text(encoding="utf-8"))
        self.assertEqual(obj["version"], 1)
        self.assertEqual(len(obj["pages"]), 8)
        self.assertEqual({p["href"] for p in obj["pages"]}, set(ROUTES))
        for page in obj["pages"]:
            source = (SITE / page["href"] / "index.html").read_text(encoding="utf-8")
            match = re.search(r'<article class="docs-content">([\s\S]*?)</article>', source)
            self.assertIsNotNone(match, page["href"])
            article = match.group(1)
            headings = {id: normalize_text(title) for id, title in
                        re.findall(r'<h2 id="([^"]+)">([\s\S]*?)</h2>', article)}
            self.assertEqual({s["id"] for s in page["sections"]}, set(headings), page["href"])
            for section in page["sections"]:
                self.assertEqual(section["title"], headings[section["id"]])
                self.assertGreater(len(section["text"]), 20)
                self.assertIn(section["text"][:30], normalize_text(article))

    def test_docs_search_aria_contract(self):
        for route in ROUTES:
            doc = Sheets()
            doc.feed((SITE / route / "index.html").read_text(encoding="utf-8"))
            self.assertEqual(len(doc.inputs), 1)
            self.assertEqual(doc.inputs[0].get("role"), "combobox")
            self.assertEqual(doc.inputs[0].get("aria-expanded"), "false")
            self.assertEqual(doc.inputs[0].get("aria-controls"), "docs-results")
        js = (SITE / "docs/docs.js").read_text(encoding="utf-8")
        self.assertIn("search-index.json", js)
        self.assertIn('event.key==="ArrowDown"', js)
        self.assertIn('event.key==="Enter"', js)

if __name__ == "__main__":
    unittest.main()
