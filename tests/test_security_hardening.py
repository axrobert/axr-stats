"""Security regression tests: API origin, limits, safe file publishing and novice config."""
from __future__ import annotations

from pathlib import Path
import json
import math
import sys
import tempfile
import unittest
from unittest import mock
import urllib.error
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
import axr_stats
import config
import run_action


class APIResponse:
    def __init__(self, content: bytes, status=200):
        self.content = content
        self.status = status
    def __enter__(self): return self
    def __exit__(self, *args): return False
    def read(self, max_bytes):
        return self.content[:max_bytes]


class SecurityTests(unittest.TestCase):
    def test_api_redirect_must_remain_same_https_origin(self):
        handler=axr_stats.WakaTimeRedirectHandler()
        request=urllib.request.Request(
            "https://api.wakatime.com/api/v1/users/current",
            headers={"Authorization":"Bearer test-secret"}
        )
        for url in (
            "https://evil.example.net/steal",
            "http://api.wakatime.com/api/v1/",
            "https://api.wakatime.com.evil.example.net/",
            "https://api.wakatime.com:444/api/v1/",
            "https://user:pass@api.wakatime.com/api/v1/"
        ):
            with self.subTest(url=url), self.assertRaises(RuntimeError):
                handler.redirect_request(request,None,302,"Found",{},url)
        accepted=handler.redirect_request(
            request,None,302,"Found",{},"https://api.wakatime.com/api/v1/users/current?x=1"
        )
        self.assertEqual(accepted.full_url,"https://api.wakatime.com/api/v1/users/current?x=1")

    def test_api_rejects_oversized_json_and_invalid_payload(self):
        with mock.patch.object(urllib.request,"build_opener") as factory:
            opener=factory.return_value
            opener.open.return_value=APIResponse(b"x"*(axr_stats.MAX_API_RESPONSE_BYTES+1))
            with self.assertRaisesRegex(RuntimeError,"safe size limit"):
                axr_stats.api("users/current", "test-secret")
            opener.open.return_value=APIResponse(b"[]")
            with self.assertRaisesRegex(RuntimeError,"response object"):
                axr_stats.api("users/current","test-secret")

    def test_api_errors_are_actionable_and_do_not_echo_token(self):
        with mock.patch.object(urllib.request,"build_opener") as factory:
            factory.return_value.open.side_effect=urllib.error.HTTPError(
                "https://api.wakatime.com/api/v1/users/current",401,"Unauthorized",{},None
            )
            with self.assertRaises(RuntimeError) as error:
                axr_stats.api("users/current","private-token-value")
        message=str(error.exception)
        self.assertIn("OAuth token",message)
        self.assertNotIn("private-token-value",message)

    def test_duration_rejects_nonfinite_or_negative_numbers(self):
        for value in (float("nan"),float("inf"),float("-inf"),-1,"abc",{},[]):
            with self.subTest(value=value),self.assertRaises(RuntimeError):
                axr_stats.duration(value)
        self.assertEqual(axr_stats.duration(3660),"1h 01m")

    def test_cli_rejects_unsafe_destinations(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            for value in ("../outside",".",".git/cards",".github/workflows","cards/../elsewhere"):
                with self.subTest(output=value):
                    with mock.patch("pathlib.Path.cwd",return_value=root):
                        with self.assertRaises(RuntimeError):
                            run_action.check_output_path(Path(value),require_relative=True)
            for value in ("/tmp/external",):
                with self.subTest(output=value):
                    with self.assertRaises(RuntimeError):
                        run_action.check_output_path(Path(value),require_relative=True)

    def test_symlink_ancestor_and_managed_link_refused_or_replaced(self):
        with tempfile.TemporaryDirectory() as temp:
            base=Path(temp)
            real=base/"real"
            real.mkdir()
            alias=base/"alias"
            alias.symlink_to(real,target_is_directory=True)
            with self.assertRaisesRegex(RuntimeError,"symlink"):
                run_action.publish(base/"staged",alias/"generated")

            destination=base/"cards"
            destination.mkdir()
            outside=base/"protected.svg"
            outside.write_text("protected")
            (destination/"lifetime.svg").symlink_to(outside)
            staged=base/"staged"
            staged.mkdir()
            (staged/"lifetime.svg").write_text("new valid content")
            run_action.publish(staged,destination,("lifetime.svg",))
            self.assertEqual(outside.read_text(),"protected")
            self.assertEqual((destination/"lifetime.svg").read_text(),"new valid content")
            self.assertFalse((destination/"lifetime.svg").is_symlink())

    def test_reject_unsafe_json_paths(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/"settings.json"
            for output in (".git/cards",".github/actions","cards/../elsewhere","cards\\nname"):
                with self.subTest(output=output):
                    path.write_text(json.dumps({"output":output}))
                    with self.assertRaises(RuntimeError):
                        config.read_config(path)


if __name__=="__main__":
    unittest.main()
