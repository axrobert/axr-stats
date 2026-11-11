"""Phase 2.3.2 — strict typography/star options, default compatibility and fixture parity."""
from __future__ import annotations
import datetime as dt
import json
from pathlib import Path
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
sys.path.insert(0,str(ROOT/"scripts"))
from axr_stats import THEMES, presentation_theme, label, cards, lifetime_card, badge_card
from config import read_config
from generate_preview_cards import build


class TypographyOptionsTests(unittest.TestCase):
    def test_schema_rejects_bogus_typography_and_star_types(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/"axr-stats.json"
            for typo in ("compact","standard","large"):
                for stars in (False,True):
                    path.write_text(json.dumps({"typography":typo,"show_rank_stars":stars}))
                    self.assertEqual(read_config(path)["typography"],typo)
                    self.assertIs(read_config(path)["show_rank_stars"],stars)
            for data in (
                {"typography":"auto"},{"typography":None},{"typography":2},
                {"show_rank_stars":0},{"show_rank_stars":"false"},{"show_rank_stars":None}
            ):
                with self.subTest(data=data):
                    path.write_text(json.dumps(data))
                    with self.assertRaises(RuntimeError):
                        read_config(path)

    def test_font_scale_does_not_mutate_global_palettes(self):
        original=dict(THEMES["midnight"])
        for preset,size in (("compact","12.6"),("standard","14"),("large","15.12")):
            theme=presentation_theme(THEMES["midnight"],preset)
            svg=label(10,30,"Metric",theme,14)
            self.assertIn('font-size="'+size+'"',svg)
            ET.fromstring("<svg>"+svg+"</svg>")
        self.assertEqual(THEMES["midnight"],original)
        with self.assertRaises(RuntimeError):
            presentation_theme(THEMES["midnight"],"fake")
        with self.assertRaises(RuntimeError):
            presentation_theme(THEMES["midnight"],"compact",0)

    def test_old_defaults_match_explicit_standard_presentation(self):
        lifetime={"data":{"total_seconds":152*3600}}
        month={"data":{"total_seconds":20000,"languages":[{"name":"Python","total_seconds":15000}]}}
        week={"data":{"total_seconds":3000,"daily_average":400}}
        summaries={"data":[]}
        today=dt.date(2026,11,11)
        old=cards(lifetime,month,week,summaries,{},today)
        new=cards(lifetime,month,week,summaries,{},today,
                  typography="standard",show_rank_stars=True)
        self.assertEqual(old,new)
        no_stars=cards(lifetime,month,week,summaries,{},today,show_rank_stars=False)
        for key in ("lifetime.svg","emblem.svg"):
            self.assertNotIn("<polygon",no_stars[key])
            self.assertIn("data:image/png;base64,",no_stars[key])
            self.assertIn("data:image/png;base64,",old[key])
        self.assertEqual(old["ranking.svg"],no_stars["ranking.svg"])
        self.assertIn("#",old["lifetime.svg"])
        self.assertIn("<polygon",old["lifetime.svg"])

    def test_all_fixture_variants_match_rendered_dimensions(self):
        with tempfile.TemporaryDirectory() as temp:
            folder=Path(temp)
            paths=build(folder)
            self.assertEqual(len(paths),6)
            self.assertEqual(len(list(folder.glob("*.svg"))),30)
            for typo in ("standard","compact","large"):
                suffix="" if typo=="standard" else "-type-"+typo
                for rows,height in ((5,335),(8,422),(10,480)):
                    stem="languages"+("-"+str(rows) if rows!=10 else "")+suffix
                    self.assertEqual(ET.parse(folder/(stem+".svg")).getroot().get("height"),str(height))
                for name in ("lifetime","emblem"):
                    art=(folder/(name+suffix+"-no-stars.svg")).read_text()
                    self.assertNotIn("<polygon",art)
                    self.assertIn("data:image/png;base64,",art)
                for name in ("activity","ranking","heatmap"):
                    self.assertTrue((folder/(name+suffix+".svg")).is_file())
            self.assertEqual(
                (folder/"lifetime.svg").read_text(),
                (folder/"lifetime.svg").read_text())


if __name__=="__main__":
    unittest.main()
