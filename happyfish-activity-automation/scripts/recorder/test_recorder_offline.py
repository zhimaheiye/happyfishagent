# -*- coding: utf-8 -*-
"""Recorder V0 离线测试。不连接模拟器，也不消耗游戏资源。

覆盖：flow 读写、状态编号、1920×1080 → 1280×720、帧差、session 目录、
安全拒绝、画面一直在变时的超时、设备解析不回退到历史端口。
"""
import json
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from PIL import Image

SCRIPTS = Path(__file__).resolve().parents[1]
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import frame_diff  # noqa: E402
from recorder.coords import to_standard  # noqa: E402
from recorder.device import (  # noqa: E402
    choose_input_resolution,
    parse_adb_devices,
    parse_logical_frame,
    parse_wm_size,
    resolve_serial,
)
from recorder.engine import Recorder, annotate  # noqa: E402
from recorder.session import STATUS_LEGEND, Session, blank_state  # noqa: E402

OPEN_SHELL = Path(r"D:\happyfishgame\dev\exploration\open_shell")

REQUIRED_STATE_FIELDS = (
    "state",
    "name",
    "status",
    "screenshots",
    "recognition",
    "action",
    "result_candidates",
    "timing",
    "safety",
)


class FakeDevice:
    def __init__(self, frames, resolution=(1280, 720)):
        self.frames = list(frames)
        self.resolution = resolution
        self.serial = "fake-serial"
        self.source = "test"
        self.taps = []
        self.swipes = []
        self.index = 0

    def wm_size(self):
        return self.resolution

    def screencap(self):
        image = self.frames[min(self.index, len(self.frames) - 1)]
        self.index += 1
        return image.copy()

    def tap(self, x, y):
        self.taps.append((x, y))

    def swipe(self, x1, y1, x2, y2, duration_ms):
        self.swipes.append((x1, y1, x2, y2, duration_ms))


def solid(color, size=(1280, 720)):
    return Image.new("RGB", size, color)


class CoordAndOpenShellTest(unittest.TestCase):
    def test_open_shell_coordinates_match_flow(self):
        # 开贝壳 flow.json 里同时记了 1080p 实点和 720p 中心。
        self.assertEqual(to_standard(960, 953, 1920, 1080), (640, 635))
        self.assertEqual(to_standard(1284, 980, 1920, 1080), (856, 653))
        self.assertEqual(to_standard(669, 980, 1920, 1080), (446, 653))

    def test_open_shell_flow_shape(self):
        flow = json.loads((OPEN_SHELL / "flow.json").read_text(encoding="utf-8"))
        self.assertEqual(flow["device"]["standard_resolution"], [1280, 720])
        self.assertEqual(flow["states"][0]["state"], "A")
        self.assertIn("recognition", flow["states"][0])
        self.assertIn("target_center_720p", flow["states"][0]["action"])
        self.assertIn("device_tap_coordinate", flow["states"][0]["action"])

    def test_open_shell_frame_diff(self):
        before = OPEN_SHELL / "screenshots" / "A_001.png"
        after = OPEN_SHELL / "screenshots" / "B_001.png"
        same = frame_diff.mean_abs_diff(before, before)
        changed = frame_diff.mean_abs_diff(before, after)
        self.assertLess(same, 0.05)
        self.assertGreater(changed, 5)
        box = frame_diff.change_bbox(before, after)
        self.assertIsNotNone(box)
        self.assertEqual(len(box), 4)
        self.assertGreater(frame_diff.changed_fraction(before, after), 0.05)


class FrameDiffCliTest(unittest.TestCase):
    def test_burst_report_still_writes_scores(self):
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            solid((0, 0, 0)).save(directory / "f0000.png")
            solid((255, 255, 255)).save(directory / "f0001.png")
            frame_diff.main([str(directory)])
            text = (directory / "_diff.txt").read_text(encoding="utf-8")
        self.assertIn("frames=2", text)
        self.assertIn("f0001.png", text)


class DeviceResolveTest(unittest.TestCase):
    def test_env_wins_and_does_not_guess(self):
        def boom():
            raise AssertionError("不应再去枚举设备")

        serial, source = resolve_serial(
            {"HAPPYFISH_ADB_DEV": "env-serial"},
            list_online=boom,
            mumu_pick=boom,
        )
        self.assertEqual(serial, "env-serial")
        self.assertEqual(source, "env:HAPPYFISH_ADB_DEV")

    def test_single_online_device(self):
        serial, source = resolve_serial({}, list_online=lambda: ["only-one"], mumu_pick=None)
        self.assertEqual((serial, source), ("only-one", "adb_devices"))

    def test_many_devices_refuse(self):
        with self.assertRaises(Exception):
            resolve_serial({}, list_online=lambda: ["a", "b"], mumu_pick=None)

    def test_none_online_refuse(self):
        with self.assertRaises(Exception):
            resolve_serial({}, list_online=lambda: [], mumu_pick=None)

    def test_source_has_no_historical_port_literal(self):
        text = Path(__file__).resolve().parents[0].joinpath("device.py").read_text(encoding="utf-8")
        for banned in ("7555", "16384", "16416"):
            self.assertNotIn(banned, text)

    def test_wm_size_prefers_override(self):
        text = "Physical size: 1920x1080\nOverride size: 1280x720\n"
        self.assertEqual(parse_wm_size(text), (1280, 720))
        self.assertEqual(
            parse_adb_devices("List of devices attached\n127.0.0.1:9\tdevice\n"),
            ["127.0.0.1:9"],
        )

    def test_landscape_tap_space_is_not_unrotated_wm_size(self):
        sample = "Viewport INTERNAL: logicalFrame=[0, 0, 1280, 720], deviceSize=[1280, 720]"
        logical = parse_logical_frame(sample)
        self.assertEqual(logical, (1280, 720))
        chosen, source = choose_input_resolution((720, 1280), (1280, 720), logical)
        self.assertEqual(chosen, (1280, 720))
        self.assertEqual(source, "dumpsys_input.logicalFrame")
        fallback, fallback_source = choose_input_resolution((720, 1280), (1280, 720), None)
        self.assertEqual(fallback, (1280, 720))
        self.assertEqual(fallback_source, "screenshot_rotated_from_wm")


class SessionRecorderTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.session = Session.create(
            "unit-event",
            root=self.root,
            when=datetime(2026, 9, 25, 12, 0, 0),
        )

    def tearDown(self):
        self.temp.cleanup()

    def test_session_layout_and_schema(self):
        self.assertTrue((self.session.path / "flow.json").is_file())
        self.assertTrue((self.session.path / "trace.jsonl").is_file())
        self.assertTrue((self.session.path / "screenshots").is_dir())
        self.assertTrue((self.session.path / "diffs").is_dir())
        self.assertTrue((self.session.path / "takeover").is_dir())
        state = blank_state("S0001")
        for field in REQUIRED_STATE_FIELDS:
            self.assertIn(field, state)
        self.assertEqual(state["status"], "observed")
        self.assertIsNone(state["recognition"])
        self.assertEqual(set(STATUS_LEGEND), {"observed", "proposed", "confirmed", "maa_ready"})
        created = json.loads(self.session.flow_path.read_text(encoding="utf-8"))
        self.assertEqual(created["schema"], "happyfish.action_recorder.v0")
        self.assertEqual(created["task"], "unit-event")

    def test_second_session_does_not_overwrite(self):
        other = Session.create(
            "unit-event",
            root=self.root,
            when=datetime(2026, 9, 25, 12, 0, 0),
        )
        self.assertNotEqual(self.session.path, other.path)
        self.assertTrue(self.session.flow_path.is_file())

    def test_tap_records_both_coordinate_spaces(self):
        frames = [
            solid((0, 0, 0), (1920, 1080)),
            solid((0, 0, 0), (1920, 1080)),
            solid((255, 255, 255), (1920, 1080)),
            solid((255, 255, 255), (1920, 1080)),
            solid((250, 250, 250), (1920, 1080)),
            solid((250, 250, 250), (1920, 1080)),
        ]
        device = FakeDevice(frames, resolution=(1920, 1080))
        recorder = Recorder(device, self.session, max_wait_s=2.0, poll_s=0.01, idle_gap_s=0)
        result = recorder.act(
            "tap",
            [(640, 635)],
            None,
            "720p",
            "打开活动入口",
            "nav",
            "离线夹具",
        )
        self.assertTrue(result["executed"])
        self.assertEqual(device.taps, [(960, 953)])
        self.assertEqual(result["from_state"], "S0001")
        self.assertEqual(result["to_state"], "S0002")
        flow = json.loads(self.session.flow_path.read_text(encoding="utf-8"))
        action = flow["states"][0]["action"]
        self.assertEqual(action["device_tap_coordinate"], [960, 953])
        self.assertEqual(action["target_center_720p"], [640, 635])
        self.assertIsNone(action["confirmed"])
        self.assertEqual(flow["states"][0]["status"], "observed")
        self.assertIsNone(flow["states"][0]["recognition"])
        self.assertTrue((self.session.path / "screenshots" / "S0001_before.png").is_file())
        self.assertTrue((self.session.path / "screenshots" / "S0001_after.png").is_file())
        self.assertTrue((self.session.path / "diffs" / "S0001.json").is_file())
        diff = json.loads((self.session.path / "diffs" / "S0001.json").read_text(encoding="utf-8"))
        self.assertGreater(diff["global_mean_abs"], 5)
        self.assertIsNotNone(diff["bbox_720p"])
        self.assertFalse(diff["timed_out"])
        self.assertIsNotNone(diff["first_change_ms"])
        self.assertIsNotNone(diff["stable_ms"])
        lines = [
            json.loads(line)
            for line in self.session.trace_path.read_text(encoding="utf-8").splitlines()
        ]
        taps = [line for line in lines if line["type"] == "tap"]
        self.assertEqual(len(taps), 1)
        self.assertEqual(taps[0]["action"]["device_tap_coordinate"], [960, 953])
        self.assertEqual(taps[0]["device"]["native_resolution"], [1920, 1080])
        self.assertEqual(taps[0]["device"]["standard_resolution"], [1280, 720])

    def test_unstable_screen_times_out(self):
        # 动作前两帧静止，阈值才不会被抬高；动作后每一帧都和上一帧差很多。
        frames = [solid((0, 0, 0)), solid((0, 0, 0))]
        for index in range(40):
            frames.append(solid(((index * 80) % 256, (index * 40) % 256, 30)))
        device = FakeDevice(frames)
        recorder = Recorder(device, self.session, max_wait_s=0.35, poll_s=0.05, idle_gap_s=0)
        started = __import__("time").monotonic()
        result = recorder.act(
            "tap",
            [(10, 10)],
            None,
            "device",
            "点空白处",
            "nav",
            None,
        )
        elapsed = __import__("time").monotonic() - started
        self.assertTrue(result["executed"])
        self.assertLess(elapsed, 2.0)
        diff = json.loads((self.session.path / "diffs" / "S0001.json").read_text(encoding="utf-8"))
        self.assertTrue(diff["timed_out"])
        self.assertTrue((self.session.path / "screenshots" / "S0001_after.png").is_file())

    def test_unknown_safety_does_not_tap(self):
        device = FakeDevice([solid((0, 0, 0))])
        recorder = Recorder(device, self.session, idle_gap_s=0)
        result = recorder.act("tap", [(1, 1)], None, "device", "看不懂", "unknown", None)
        self.assertFalse(result["executed"])
        self.assertEqual(device.taps, [])
        self.assertTrue((self.session.path / "screenshots" / "S0001_refused.png").is_file())

    def test_danger_word_overrides_nav(self):
        device = FakeDevice([solid((0, 0, 0))])
        recorder = Recorder(device, self.session, idle_gap_s=0)
        result = recorder.act(
            "tap",
            [(1, 1)],
            None,
            "device",
            "这里写着修复潜艇",
            "nav",
            None,
        )
        self.assertFalse(result["executed"])
        self.assertEqual(device.taps, [])
        self.assertEqual(result["safety"]["level"], "danger")

    def test_annotate_does_not_confirm_a_guess(self):
        device = FakeDevice([solid((1, 1, 1))])
        Recorder(device, self.session, idle_gap_s=0).shot()
        annotate(
            self.session,
            "S0001",
            "活动首页",
            None,
            {"type": "OCR", "expected": "开始", "bbox": [1, 2, 3, 4]},
        )
        flow = json.loads(self.session.flow_path.read_text(encoding="utf-8"))
        state = flow["states"][0]
        self.assertEqual(state["status"], "proposed")
        self.assertIsNone(state["name"])
        self.assertIsNone(state["recognition"])
        self.assertEqual(state["proposals"]["recognition"]["expected"], "开始")
        annotate(self.session, "S0001", None, "maa_ready", None)
        flow = json.loads(self.session.flow_path.read_text(encoding="utf-8"))
        state = flow["states"][0]
        self.assertEqual(state["status"], "maa_ready")
        self.assertEqual(state["name"], "活动首页")
        self.assertEqual(state["recognition"]["expected"], "开始")


if __name__ == "__main__":
    unittest.main()
