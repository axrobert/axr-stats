"""Phase 2: secure configuration parsing and personalized theme smoke tests."""
from pathlib import Path
from unittest import mock
import json
import os
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
import config
import axr_stats
import run_action


def fixture(path,token,params=None):
    if token!="test-token-only": raise AssertionError("Missing fixture token")
    stats={"data":{"total_seconds":3600,"daily_average":160,
                   "languages":[{"name":"Rust","total_seconds":1800}]}}
    return {
        "users/current/all_time_since_today":{"data":{"total_seconds":475*3600}},
        "users/current/stats/last_30_days":stats,
        "users/current/stats/last_7_days":stats,
        "users/current/stats/all_time":stats,
        "users/current/summaries":{"data":[]},
        "leaders":{"data":{"current_user":{"rank":9876}}},
    }[path]

class ConfigTests(unittest.TestCase):
    def config_path(self, folder, settings):
        path=Path(folder)/"axr-stats.json"
        path.write_text(json.dumps(settings),encoding="utf-8")
        return path

    def test_user_palette_changes_real_svg_without_changing_data(self):
        with tempfile.TemporaryDirectory() as folder:
            path=self.config_path(folder,{
                "theme":"aurora","timezone":"UTC","colors":{
                    "background":"#0A1022","accent":"#F39CAB","text":"#FFFFFF"
                }
            })
            target=Path(folder)/"generated"
            with mock.patch.object(axr_stats,"api",side_effect=fixture),mock.patch.dict(os.environ,{"WAKATIME_OAUTH_TOKEN":"test-token-only"}):
                axr_stats.main(["--config",str(path),"--output",str(target)])
            svg=(target/"lifetime.svg").read_text(encoding="utf-8")
            self.assertIn("#0A1022",svg)
            self.assertIn("#F39CAB",svg)
            self.assertIn("475h",svg)
            self.assertEqual(len(list(target.glob("*.svg"))),6)

    def test_composite_generation_preserves_output_and_colors(self):
        with tempfile.TemporaryDirectory() as folder:
            path=self.config_path(folder,{"theme":"graphite","colors":{"accent":"#E0AABB"}})
            target=Path(folder)/"consumer"
            with mock.patch.object(axr_stats,"api",side_effect=fixture),mock.patch.dict(os.environ,{"WAKATIME_OAUTH_TOKEN":"test-token-only"}):
                run_action.run(target,"graphite","UTC",ROOT/"assets/badges/current",config=path)
            self.assertIn("#E0AABB",(target/"lifetime.svg").read_text())
            self.assertEqual(len([f for f in target.iterdir() if f.suffix in (".svg",".png")]),8)

    def test_reject_invalid_or_sensitive_settings(self):
        with tempfile.TemporaryDirectory() as folder:
            for sample in [
                {"theme":"production"},
                {"colors":{"accent":"javascript:alert(1)"}},
                {"colors":{"unknown":"#FFFFFF"}},
                {"output":"../secret"},
                {"output":"/home/user"},
                {"WAKATIME_OAUTH_TOKEN":"should-not-be-in-config"},
                ["unexpected-list"],
            ]:
                with self.subTest(sample=str(sample)[:50]):
                    path=self.config_path(folder,sample)
                    with self.assertRaises(RuntimeError):
                        config.read_config(path)
            self.assertEqual(config.read_config(self.config_path(folder,{})),{})

    def test_cli_precedence_over_config(self):
        config_obj={"theme":"aurora","timezone":"America/Maceio","output":"badges/"}
        self.assertEqual(config.choose("midnight",config_obj,"theme","graphite"),"midnight")
        self.assertEqual(config.choose(None,config_obj,"theme","graphite"),"aurora")
        self.assertEqual(config.choose(None,config_obj,"timezone","UTC"),"America/Maceio")

if __name__=="__main__":
    unittest.main()
