"""Offline consumer-like integration tests for staged AXR Stats publishing."""
from pathlib import Path
from unittest import mock
import os
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import axr_stats as axr
import run_action
from PIL import Image


def fake_api(path, token, params=None):
    if token != "test-only-placeholder":
        raise AssertionError("Unexpected fixture token")
    stats = {"data": {
        "total_seconds": 7200,
        "daily_average": 800,
        "languages": [{"name": "Python", "total_seconds": 6400}]
    }}
    fixtures = {
        "users/current/all_time_since_today": {"data": {"total_seconds": 175 * 3600}},
        "users/current/stats/last_30_days": stats,
        "users/current/stats/all_time": stats,
        "users/current/stats/last_7_days": stats,
        "users/current/summaries": {"data": [
            {"range": {"date": "2026-11-11"},
             "grand_total": {"total_seconds": 3000}}
        ]},
        "leaders": {"data": {"current_user": {"rank": 1234}}},
    }
    return fixtures[path]


class ConsumerReleaseTests(unittest.TestCase):
    def test_consumer_repo_generates_eight_valid_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "consumer" / "assets" / "axr-stats"
            folder.mkdir(parents=True)
            (folder / "keep.txt").write_text("user content")
            with mock.patch.object(axr, "api", side_effect=fake_api), \
                    mock.patch.dict(os.environ, {"WAKATIME_OAUTH_TOKEN": "test-only-placeholder"}):
                run_action.run(folder, "midnight", "UTC", ROOT / "assets/badges/current")
            self.assertEqual((folder / "keep.txt").read_text(), "user content")
            self.assertFalse((folder / ".rank-level").exists())
            for name in run_action.SVG_FILES:
                self.assertEqual(ET.parse(folder / name).getroot().tag, "{http://www.w3.org/2000/svg}svg")
            for name in run_action.PNG_FILES:
                with Image.open(folder / name) as image:
                    image.verify()
            self.assertIn("Python", (folder / "languages.svg").read_text())
            self.assertIn("Student", (folder / "lifetime.svg").read_text())

    def test_failure_keeps_previous_cards_intact(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "existing"
            folder.mkdir()
            (folder / "lifetime.svg").write_text("previous-good-card")
            (folder / "emblem.png").write_bytes(b"previous-badge")
            with mock.patch.object(axr, "api", side_effect=RuntimeError("temporary outage")), \
                    mock.patch.dict(os.environ, {"WAKATIME_OAUTH_TOKEN": "test-only-placeholder"}):
                with self.assertRaises(RuntimeError):
                    run_action.run(folder, "aurora", "UTC", ROOT / "assets/badges/current")
            self.assertEqual((folder / "lifetime.svg").read_text(), "previous-good-card")
            self.assertEqual((folder / "emblem.png").read_bytes(), b"previous-badge")

    def test_repeated_publication_preserves_other_user_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            target = base / "consumer"
            target.mkdir()
            (target / "personal.md").write_text("keep this")
            generated = base / "generated"
            generated.mkdir()
            for name in run_action.OUTPUT_FILES:
                (generated / name).write_text("first")
            run_action.publish(generated, target)
            for name in run_action.OUTPUT_FILES:
                (generated / name).write_text("second")
            run_action.publish(generated, target)
            self.assertEqual((target / "lifetime.svg").read_text(), "second")
            self.assertEqual((target / "personal.md").read_text(), "keep this")

    def test_validation_rejects_incomplete_batch(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(RuntimeError):
                run_action.validate(Path(tmp))

    def test_action_contract_no_token_interpolation_in_shell(self):
        action = (ROOT / "action.yml").read_text(encoding="utf-8")
        self.assertIn("src/run_action.py", action)
        self.assertIn("WAKATIME_OAUTH_TOKEN: " + "$" + "{{ inputs.wakatime-oauth-token }}", action)
        self.assertIn("assets/badges/current", action)
        self.assertNotIn('echo "$WAKATIME_OAUTH_TOKEN"', action)

if __name__ == "__main__":
    unittest.main()
