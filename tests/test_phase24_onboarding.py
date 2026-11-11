"""Phase 2.4: gauge geometry and onboarding import contract."""
from pathlib import Path
import sys
import unittest
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from axr_stats import THEMES, activity_card

class OnboardingLayoutTests(unittest.TestCase):
    def test_activity_gauge_does_not_intersect_main_value(self):
        for theme in THEMES:
            for seconds in (0,1800,4*3600,8*3600):
                svg=activity_card(seconds,7200,THEMES[theme])
                root=ET.fromstring(svg)
                self.assertEqual(root.get("viewBox"),"0 0 350 300")
                self.assertIn('M91 198 A84 84',svg)
                self.assertIn('y="184"',svg)
                self.assertIn('y="207"',svg)
                self.assertIn('y="280"',svg)
                self.assertNotIn('M91 218 A84 84',svg)

    def test_basic_advanced_and_import_are_accessible(self):
        html=(ROOT/"site/customize/index.html").read_text(encoding="utf-8")
        js=(ROOT/"site/customize/import.js").read_text(encoding="utf-8")
        for mark in ('id="theme-import-file"','id="theme-import-status"',
                     'id="theme-color-details"','id="theme-render-details"',
                     'id="theme-output-dir"','id="theme-timezone"',
                     'src="import.js"'):
            self.assertIn(mark,html)
        self.assertIn('role="status"',html)
        self.assertIn("file.text()",js)
        self.assertIn("64000",js)
        for forbidden in ("localStorage","sessionStorage","WAKATIME_OAUTH_TOKEN","innerHTML","fetch("):
            self.assertNotIn(forbidden,js)
        self.assertLess((ROOT/"site/style.css").stat().st_size,85000)

if __name__=="__main__":unittest.main()
