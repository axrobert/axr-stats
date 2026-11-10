from pathlib import Path
from html.parser import HTMLParser
import unittest
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]

class ImageCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.images=[]
    def handle_starttag(self,tag,attrs):
        if tag=="img":
            src=dict(attrs).get("src","")
            if src: self.images.append(src)

class SiteTest(unittest.TestCase):
    def test_site_and_core_assets_exist(self):
        page=ROOT/"site/index.html"
        self.assertTrue(page.exists())
        collector=ImageCollector()
        collector.feed(page.read_text(encoding="utf-8"))
        self.assertTrue(collector.images)
        self.assertTrue((ROOT/"site/style.css").exists())
        self.assertTrue((ROOT/"site/app.js").exists())
        for image in collector.images:
            self.assertTrue((ROOT/image.replace("assets/","assets/",1)).exists(),image)
        names=["01-novice","02-explorer","03-artisan","04-specialist",
               "05-veteran","06-master","07-legend"]
        for name in names:
            svg=ROOT/"assets/badges/legacy"/(name+".svg")
            self.assertTrue(svg.exists(),name)
            self.assertTrue((ROOT/"assets/badges"/(name+".png")).exists(),name)
            self.assertEqual(ET.parse(svg).getroot().tag,
                             "{http://www.w3.org/2000/svg}svg")
