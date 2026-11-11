"""Phase 2.3.1: language density changes real SVG geometry without altering totals."""
from pathlib import Path
import datetime as dt
import json
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
sys.path.insert(0,str(ROOT/"scripts"))
import config
import axr_stats
from generate_preview_cards import build


class LanguageDensityTests(unittest.TestCase):
    def fixture(self):
        languages=[{"name":f"Language {i+1}","total_seconds":3600*(10-i)}
                   for i in range(10)]
        return {"data":{"total_seconds":3600*55,"languages":languages}}

    def test_config_rejects_non_whitelisted_row_counts(self):
        with tempfile.TemporaryDirectory() as tmp:
            file=Path(tmp)/"config.json"
            for value in (5,8,10):
                file.write_text(json.dumps({"language_rows":value}))
                self.assertEqual(config.read_config(file)["language_rows"],value)
            for value in (0,3,4,9,11,True,"8",None,5.0,[],{}):
                with self.subTest(value=value):
                    file.write_text(json.dumps({"language_rows":value}))
                    with self.assertRaises(RuntimeError):
                        config.read_config(file)

    def test_internal_card_heights_and_rows(self):
        fixture=self.fixture()
        for count,height in ((5,335),(8,422),(10,480)):
            with self.subTest(count=count):
                svg=axr_stats.languages_card(fixture["data"],axr_stats.THEMES["midnight"],True,count)
                root=ET.fromstring(svg)
                self.assertEqual(root.get("viewBox"),f"0 0 700 {height}")
                self.assertEqual(len([el for el in root if el.tag.endswith("text") and
                    (el.text or "").startswith("Language ")]),count)
                self.assertIn("55h",svg)
        old=axr_stats.languages_card(fixture["data"],axr_stats.THEMES["midnight"],True)
        explicit=axr_stats.languages_card(fixture["data"],axr_stats.THEMES["midnight"],True,10)
        self.assertEqual(old,explicit)

    def test_published_card_uses_configured_density(self):
        lifetime={"data":{"total_seconds":55*3600}}
        month={"data":{"total_seconds":3000,"languages":[]}}
        week={"data":{"total_seconds":0,"daily_average":0}}
        summary={"data":[]}
        for rows,height in ((5,335),(8,422),(10,480)):
            cards=axr_stats.cards(lifetime,month,week,summary,{},dt.date(2026,11,11),
                                  all_langs=self.fixture(),language_rows=rows)
            root=ET.fromstring(cards["languages.svg"])
            self.assertEqual(root.get("height"),str(height))
            self.assertEqual(len(cards),6)

    def test_static_previews_use_production_renderer(self):
        with tempfile.TemporaryDirectory() as temp:
            files=build(Path(temp))
            self.assertEqual(len(files),6)
            for rows,height in ((5,335),(8,422)):
                root=ET.parse(Path(temp)/f"languages-{rows}.svg").getroot()
                self.assertEqual(root.get("viewBox"),f"0 0 700 {height}")


if __name__=="__main__": unittest.main()
