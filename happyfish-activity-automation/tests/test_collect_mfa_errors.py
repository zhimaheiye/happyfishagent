# -*- coding: utf-8 -*-
"""Offline tests: no MFA/game/ADB/GitHub access."""
import datetime as dt
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from collect_mfa_errors import collect, windows, sanitize  # noqa: E402


class CollectMfaErrorsTests(unittest.TestCase):
    def test_no_logs_does_not_claim_success(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            self.assertEqual(collect(base / "not_exist", base / "evidence", 48)["status"], "missing_logs")

    def test_clean_log_creates_no_zip(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            (base / "log-20261011.log").write_text("INFO: 任务已全部完成！\n", encoding="utf-8")
            result = collect(base, base / "evidence", 48)
            self.assertEqual(result["status"], "no_errors")
            self.assertEqual(list((base / "evidence").glob("*.zip")) if (base / "evidence").exists() else [], [])

    def test_error_excerpt_redacts_secrets_and_packages(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            source = base / "log-20261011.log"
            source.write_text(
                "INFO: begin\n"
                "Authorization: Bearer abcdefghijklmnopqrstuvwxyz\n"
                "ERROR: 任务失败：收鱼产物\n"
                "api_key=SECRET12345\n"
                "你的ID为：1234567\n"
                "INFO: stopped\n", encoding="utf-8",
            )
            result = collect(base, base / "evidence", 48)
            self.assertEqual(result["status"], "created")
            with zipfile.ZipFile(result["zip"]) as zf:
                self.assertEqual(json.loads(zf.read("manifest.json"))["error_hits"], 1)
                excerpt = zf.read("log-20261011.log.excerpt.txt").decode()
                self.assertIn("任务失败：收鱼产物", excerpt)
                self.assertNotIn("SECRET12345", excerpt)
                self.assertNotIn("1234567", excerpt)
                self.assertNotIn("abcdefghijklmnopqrstuvwxyz", excerpt)

    def test_same_error_window_is_not_archived_twice(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            (base / "log-20261011.log").write_text("ERROR: 任务失败：X\\n", encoding="utf-8")
            first = collect(base, base / "evidence", 48)
            second = collect(base, base / "evidence", 48)
            self.assertEqual(first["status"], "created")
            self.assertEqual(second["status"], "already_archived")
            self.assertEqual(first["zip"], second["zip"])
            self.assertEqual(len(list((base / "evidence").glob("*.zip"))), 1)

    def test_no_normal_completion_as_error(self):
        self.assertEqual(windows(["INFO: 任务已全部完成！", "INFO: 无需操作"]), ([], 0))

    def test_overlapping_error_context_merged(self):
        excerpt, count = windows(["INFO", "ERROR: first", "ERROR: second", "END"], 1, 1)
        self.assertEqual(count, 2)
        self.assertEqual(sum(line.startswith("--- lines") for line in excerpt), 1)

    def test_direct_redaction(self):
        text = sanitize("password: abc123 api_key=TOKEN123 你的ID为：1234")
        self.assertNotIn("abc123", text)
        self.assertNotIn("TOKEN123", text)
        self.assertNotIn("1234", text)

    def test_invalid_hours(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):
                collect(Path(temp), Path(temp), 0)
            with self.assertRaises(ValueError):
                collect(Path(temp), Path(temp), 337)


if __name__ == "__main__":
    unittest.main()
