"""Safety boundaries of the modular exploration console, without game input."""
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
from unittest.mock import patch
import json
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from activity_console import execute
from recorder.known_modules import backpack_slots, free_backpack_counts, guard_modal, prepare_backpacks
from archive_activity_session import archive
from recorder.maa_vision import AdbMaaDevice


def rows(text):
    return [{"text": text, "box": [0, 0, 100, 30]}]


class ModuleSafetyTests(unittest.TestCase):
    def test_unscaled_ocr_coordinates_reject_non_native_resolution(self):
        adb = Mock(serial="fake")
        adb.screencap.return_value = Image.new("RGB", (1920, 1080))
        device = AdbMaaDevice(adb, Mock())
        with self.assertRaises(RuntimeError):
            device.screencap()
        adb.tap.assert_not_called()

    def test_empty_ocr_target_never_clicks_single_result(self):
        with tempfile.TemporaryDirectory() as directory:
            device = Mock(source="fake")
            device.ocr.return_value = rows("Only result")
            recorder = Mock()
            result = execute({"op":"tap_text", "expect":""}, device, recorder,
                             SimpleNamespace(path=Path(directory)))
            self.assertIn("error", result)
            recorder.act.assert_not_called()

    def test_real_backpack_templates_reject_map_and_recognize_unopened_bags(self):
        assets = Path(__file__).resolve().parents[3] / "assets/dudu-rescue"
        evidence = assets / "evidence/20261025-172501"
        sources = {row["source"]: row["published"] for row in json.loads(
            (evidence / "archive_manifest.json").read_text(encoding="utf-8"))}
        for name, normal, locked in (("S0007_after", 5, 4), ("S0048_after", 6, 2)):
            with Image.open(evidence / sources["screenshots/" + name + ".png"]) as picture:
                found = backpack_slots(picture, assets / "templates")
            self.assertEqual(sum(item["kind"] == "plain" for item in found), normal)
            self.assertEqual(sum(item["kind"] == "locked" for item in found), locked)
        with Image.open(evidence / sources["screenshots/S0023_before.png"]) as picture:
            self.assertEqual(backpack_slots(picture, assets / "templates"), [])

    def test_free_quota_variants_and_exhaustion(self):
        for text, expected in [
            ("可免费开启普通背包3/3次,加锁背包1/1次", (3, 1)),
            ("可免费开启普通背包2/2次,加锁背包2/2次", (2, 2)),
            ("额外开启普通背包消耗2 可免费开启加锁背包1/1次", (0, 1)),
            ("额外开启普通背包消耗2 加锁背包2/2次", (0, 2)),
            ("额外开启普通背包消耗2 额外开启加锁背包消耗3", (0, 0)),
        ]:
            self.assertEqual(free_backpack_counts(rows("翻找背包 " + text)), expected)

    def test_unreadable_or_paid_positive_quota_rejected(self):
        for text in ("普通背包2/2 加锁背包2/2", "可免费开启普通背包3/2 加锁背包2/2",
                     "可免费开启普通背包2/2 加锁背包2/2 开心收下"):
            with self.assertRaises(ValueError):
                free_backpack_counts(rows("翻找背包 " + text))

    def test_underlying_title_cannot_bypass_modal(self):
        screen = rows("飞机检修 点击扳手 检修中(1/3) 在指针进入绿色区域时点击")
        with self.assertRaises(ValueError):
            guard_modal(screen, {"expect": "飞机检修"})
        guard_modal(screen, {"modal_expect": "在指针进入绿色区域时点击"})

    def test_save_conflict_requires_specific_reload_authorization(self):
        screen = rows("档案冲突，本次档案无法保存 确定")
        with self.assertRaises(ValueError):
            guard_modal(screen, {"op": "tap_text", "expect": "确定"})
        guard_modal(screen, {"op": "tap_text", "expect": "确定", "server_reload_authorized": True})

    def test_unchanged_quota_stops_after_one_click(self):
        device = Mock()
        screen = rows("翻找背包 可免费开启普通背包3/3次,加锁背包1/1次")
        device.vision.ocr.return_value = screen
        action = Mock(return_value={"executed": True, "ocr": screen})
        with patch("recorder.known_modules.backpack_slots", return_value=[{"kind":"plain", "point":[210,200]}]):
            result = prepare_backpacks(device, None, None, action)
        self.assertIn("stopped", result)
        action.assert_called_once()

    def test_archive_links_and_lossless_dedup(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source"
            (source / "screenshots").mkdir(parents=True)
            for name in ("before.png", "after.png"):
                Image.new("RGB", (8, 8), (12, 34, 56)).save(source / "screenshots" / name)
            trace = {"type":"tap", "executed":True, "screenshots":{
                "before":"screenshots/before.png", "after":"screenshots/after.png"}}
            (source / "trace.jsonl").write_text(json.dumps(trace) + "\n", encoding="utf-8")
            output = Path(directory) / "published"
            result = archive(source, output)
            self.assertEqual(result["unique_images"], 1)
            restored = json.loads((output / "trace.jsonl").read_text(encoding="utf-8"))
            self.assertTrue((output / restored["screenshots"]["after"]).is_file())
            with self.assertRaises(FileExistsError):
                archive(source, output)

    def test_zero_free_quota_never_calls_input(self):
        device = Mock()
        device.vision.ocr.return_value = rows("翻找背包 额外开启普通背包消耗2 额外开启加锁背包消耗3")
        action = Mock()
        self.assertTrue(prepare_backpacks(device, None, None, action)["done"])
        action.assert_not_called()

    def test_guard_rejects_missing_ambiguous_and_covered(self):
        for screen in (rows("other"), rows("Help") * 2, rows("Help 检修中(0/3)")):
            with tempfile.TemporaryDirectory() as directory:
                device = Mock(source="fake")
                device.ocr.return_value = screen
                recorder = Mock()
                result = execute({"op": "tap_text", "expect": "Help"}, device, recorder,
                                 SimpleNamespace(path=Path(directory)))
                self.assertIn("error", result)
                recorder.act.assert_not_called()

    def test_ocr_failure_after_click_preserves_executed_result(self):
        with tempfile.TemporaryDirectory() as directory:
            device = Mock(source="fake")
            device.ocr.side_effect = [rows("Help"), RuntimeError("recognition unavailable")]
            recorder = Mock()
            recorder.act.return_value = {"executed": True, "to_state": "S0002"}
            result = execute({"op": "tap_text", "expect": "Help", "read_after": True},
                             device, recorder, SimpleNamespace(path=Path(directory)))
            self.assertTrue(result["executed"])
            self.assertEqual(result["to_state"], "S0002")
            self.assertTrue(result["inspect_before_retry"])
            recorder.act.assert_called_once()


if __name__ == "__main__":
    unittest.main()
