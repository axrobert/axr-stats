"""Validate the public roadmap without depending on JavaScript execution."""
from html.parser import HTMLParser
from pathlib import Path
import json
import re
import unittest

ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/"site"

class Check(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids=set()
        self.anchors=[]
        self.buttons=[]
        self.elements=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if "id" in a: self.ids.add(a["id"])
        if tag=="a": self.anchors.append(a.get("href",""))
        if tag=="button": self.buttons.append(a)
        if "data-rm-status" in a: self.elements.append(a["data-rm-status"])

class RoadmapTests(unittest.TestCase):
    def test_public_route_and_evidence(self):
        page=(SITE/"roadmap/index.html").read_text(encoding="utf-8")
        dom=Check();dom.feed(page)
        self.assertEqual(dom.elements,["done","active","active","planned","planned"])
        self.assertEqual(len([x for x in dom.buttons if "data-rm-filter" in x]),4)
        for anchor in ("fase-0","fase-1","fase-1-5","fase-2","fase-3","trajetoria","detalhes","release"):
            self.assertIn(anchor,dom.ids)
            if anchor.startswith("fase-"): self.assertIn("#"+anchor,dom.anchors)
        self.assertIn("https://github.com/axrobert/axrobert/actions/runs/42962893687",page)
        self.assertIn("https://github.com/axrobert/axr-stats/issues/13",page)
        self.assertNotIn("8.000h",page) # no fabricated completion or coding stats

    def test_reduced_motion_and_self_contained_js(self):
        css=(SITE/"style.css").read_text(encoding="utf-8")
        js=(SITE/"roadmap/roadmap.js").read_text(encoding="utf-8")
        self.assertIn("@media(prefers-reduced-motion:reduce)",css)
        self.assertIn(".rm-map--ready",css)
        self.assertIn("IntersectionObserver",js)
        self.assertIn("aria-pressed",js)
        self.assertNotIn("innerHTML",js)
        self.assertNotIn("localStorage",js)
        self.assertNotIn("WAKATIME_OAUTH_TOKEN",js)
        icons=set(re.findall(r'<symbol id="([^"]+)"',(SITE/"icons/lucide.svg").read_text()))
        page=(SITE/"roadmap/index.html").read_text()
        self.assertTrue(set(re.findall(r'data-icon="([^"]+)"',page)) <= icons)
        self.assertTrue((SITE/"roadmap/roadmap.js").is_file())

    def test_nav_links_to_roadmap(self):
        self.assertIn('href="roadmap/"',(SITE/"index.html").read_text())
        self.assertIn('href="../../roadmap/"',(SITE/"docs/roadmap/index.html").read_text())
        entries=json.loads((SITE/"docs/search-index.json").read_text())["pages"]
        self.assertTrue(any(p["href"]=="docs/roadmap/" for p in entries))

if __name__=="__main__":
    unittest.main()
