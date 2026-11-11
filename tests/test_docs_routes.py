"""Static GitHub Pages route and link integrity checks (no network)."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import unittest

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
ROUTES = (
    "docs/",
    "docs/installation/",
    "docs/configuration/",
    "docs/cards/",
    "docs/ranks/",
    "docs/security/",
    "docs/faq/",
    "docs/roadmap/",
)

class Tags(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.links = []
        self.assets = []
        self.titles = []
        self.lang = None

    def handle_starttag(self, tag, attrs):
        fields = dict(attrs)
        if fields.get("id"):
            self.ids.add(fields["id"])
        if tag == "html":
            self.lang = fields.get("lang")
        if tag == "a":
            self.links.append(fields.get("href", ""))
        if tag in ("img", "script", "link"):
            source = fields.get("src") or fields.get("href")
            if source:
                self.assets.append(source)
        if tag == "h1":
            self.titles.append(tag)

def local_target(document, link):
    parsed = urlsplit(link)
    if parsed.scheme or parsed.netloc or link.startswith("//"):
        return None
    if parsed.path.startswith("/"):
        raise AssertionError(f"Site must use project-relative paths, not {link}")
    if parsed.path:
        target = (document.parent / unquote(parsed.path)).resolve()
    else:
        target = document.resolve()
    # Pages copies repository assets/ to the site root during deployment.
    # Validate against the source assets for routes that reference that copy.
    try:
        relative = target.relative_to(SITE.resolve())
        if relative.parts and relative.parts[0] == "assets":
            target = ROOT / relative
    except ValueError:
        pass
    if target.is_dir():
        target = target / "index.html"
    return target

class DocsRoutingTests(unittest.TestCase):
    def test_every_expected_route_exists(self):
        for route in ROUTES:
            with self.subTest(route=route):
                self.assertTrue((SITE / route / "index.html").is_file())
        self.assertTrue((SITE / "docs/docs.css").is_file())
        self.assertTrue((SITE / "docs/docs.js").is_file())
        self.assertTrue((SITE / "refinement.css").is_file())

    def test_all_local_links_and_assets_resolve(self):
        documents = [SITE / "index.html"] + [SITE / r / "index.html" for r in ROUTES]
        for file in documents:
            dom = Tags()
            dom.feed(file.read_text(encoding="utf-8"))
            with self.subTest(page=str(file.relative_to(SITE))):
                self.assertEqual(dom.lang, "pt-BR")
                self.assertIn("main-content" if file.parent.name != "site" else "conteudo", dom.ids)
                for href in dom.links + dom.assets:
                    if href.startswith("#"):
                        self.assertIn(href[1:], dom.ids, href)
                        continue
                    target = local_target(file, href)
                    if target is None:
                        continue
                    self.assertTrue(target.is_file(), f"{file.relative_to(SITE)} -> {href}")

    def test_docs_have_headings_and_sidebar(self):
        for route in ROUTES:
            text = (SITE / route / "index.html").read_text(encoding="utf-8")
            with self.subTest(route=route):
                self.assertIn('<h1>', text)
                self.assertIn('id="docs-search"', text)
                self.assertIn('class="docs-sidebar"', text)
                self.assertIn('class="docs-toc"', text)
                self.assertIn('data-base=', text)

    def test_search_and_code_copy_do_not_use_credentials(self):
        js = (SITE / "docs/docs.js").read_text(encoding="utf-8")
        self.assertIn("navigator.clipboard.writeText", js)
        self.assertIn("renderResults", js)
        self.assertNotIn("WAKATIME_OAUTH_TOKEN", js)
        self.assertNotIn("localStorage", js)
        self.assertNotIn("eval(", js)

if __name__ == "__main__":
    unittest.main()
