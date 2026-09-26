# -*- coding: utf-8 -*-
"""flow → 临时 Pipeline 的离线测试。不改 open_shell 原文件，也不连模拟器。"""
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from recorder.flow_to_maa import CompileError, compile_flow, compile_session, slug_event

MAA_ROOT = Path(r"D:\happyfishgame")
TEMPLATE = MAA_ROOT / "assets" / "resource" / "image" / "开贝壳_入口.png"
SCHEMA_TOOL = MAA_ROOT / "tools" / "validate_schema.py"
SCHEMA_DIR = MAA_ROOT / "deps" / "tools"


def _state(state_id, status, recognition, action, candidates=None, timing=None):
    return {
        "state": state_id,
        "name": None,
        "status": status,
        "recognition": recognition,
        "action": action,
        "result_candidates": candidates or [],
        "timing": timing or {},
        "safety": {"level": "unknown", "reason": None},
    }


def _ocr(expected, mode=None, roi=None):
    payload = {
        "type": "OCR",
        "expected": expected,
        "recommended_roi": roi or [10, 20, 30, 40],
    }
    if mode:
        payload["expected_mode"] = mode
    return payload


class CompileRulesTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="flowmaa_", dir=r"D:\开心水族箱活动经验")
        self.session = Path(self.temp.name)
        self.pipeline_path = self.session / "generated" / "pipeline.json"

    def tearDown(self):
        self.temp.cleanup()

    def _compile(self, states, event="open-shell"):
        flow = {
            "exploration_task": event,
            "session_id": "20260925-000000",
            "states": states,
        }
        return compile_flow(flow, self.session, self.pipeline_path)

    def test_only_maa_ready_is_compiled(self):
        pipeline = self._compile(
            [
                _state("S0001", "observed", _ocr("观察"), {"type": "DoNothing"}),
                _state("S0002", "proposed", _ocr("提议"), {"type": "DoNothing"}),
                _state("S0003", "confirmed", _ocr("确认"), {"type": "DoNothing"}),
                _state("S0004", "maa_ready", _ocr("可以"), {"type": "DoNothing"}),
            ]
        )
        names = [key for key in pipeline if not key.startswith("$")]
        blob = " ".join(names)
        self.assertNotIn("S0001", blob)
        self.assertNotIn("S0002", blob)
        self.assertNotIn("S0003", blob)
        self.assertIn("Activity_open_shell_S0004", names)
        self.assertEqual(pipeline["$meta"]["event"], "open-shell")
        self.assertEqual(pipeline["$meta"]["event_slug"], "open_shell")

    def test_missing_recognition_fails_clearly(self):
        with self.assertRaises(CompileError) as caught:
            self._compile([_state("S0007", "maa_ready", None, {"type": "DoNothing"})])
        self.assertIn("S0007", str(caught.exception))
        self.assertIn("recognition", str(caught.exception))

    def test_ocr_literal_is_escaped_and_regex_is_not(self):
        pipeline = self._compile(
            [
                _state(
                    "S0001",
                    "maa_ready",
                    _ocr("开始(1)+?"),
                    {"type": "ClickRecognitionResult"},
                ),
                _state(
                    "S0002",
                    "maa_ready",
                    _ocr("^进入$", "regex"),
                    {"type": "ClickRecognitionResult"},
                    ["S0001"],
                ),
            ]
        )
        literal = pipeline["Activity_open_shell_S0001"]
        regex_node = pipeline["Activity_open_shell_S0002"]
        self.assertEqual(literal["expected"], re.escape("开始(1)+?"))
        self.assertNotIn("target", literal)
        self.assertEqual(literal["action"], "Click")
        self.assertEqual(regex_node["expected"], "^进入$")
        re.compile(literal["expected"])
        re.compile(regex_node["expected"])

    def test_missing_template_is_rejected(self):
        recognition = {
            "type": "TemplateMatch",
            "template": "does-not-exist.png",
            "threshold": 0.8,
            "recommended_roi": [1, 2, 3, 4],
        }
        with self.assertRaises(CompileError) as caught:
            self._compile(
                [_state("S0001", "maa_ready", recognition, {"type": "ClickRecognitionResult"})]
            )
        self.assertIn("模板文件不存在", str(caught.exception))
        self.assertIn("S0001", str(caught.exception))

    def test_template_file_and_fixed_720p_target(self):
        self.assertTrue(TEMPLATE.is_file(), TEMPLATE)
        recognition = {
            "type": "TemplateMatch",
            "template": str(TEMPLATE),
            "threshold": 0.8,
            "recommended_roi": [289, 492, 168, 139],
        }
        action = {
            "type": "Click",
            "target_center_720p": [640, 635],
            "device_tap_coordinate": [960, 953],
        }
        pipeline = self._compile(
            [_state("S0001", "maa_ready", recognition, action)],
            event="shell",
        )
        node = pipeline["Activity_shell_S0001"]
        self.assertEqual(node["target"], [640, 635])
        self.assertNotIn(960, node["target"])
        self.assertNotIn(953, node["target"])
        self.assertEqual(node["template"], str(TEMPLATE))
        self.assertEqual(node["roi"], [289, 492, 168, 139])

    def test_known_successor_and_frontier_and_per_state_error(self):
        states = [
            _state(
                "S0001",
                "maa_ready",
                _ocr("甲"),
                {"type": "ClickRecognitionResult"},
                ["S0002"],
                {"action_to_stable_ms": 1500},
            ),
            _state(
                "S0002",
                "maa_ready",
                _ocr("乙"),
                {"type": "DoNothing"},
                ["S0003"],
                {"timed_out": True, "action_to_stable_ms": None},
            ),
            _state("S0003", "proposed", _ocr("丙"), {"type": "DoNothing"}),
        ]
        pipeline = self._compile(states, event="evt")
        first = pipeline["Activity_evt_S0001"]
        second = pipeline["Activity_evt_S0002"]
        self.assertEqual(first["next"], ["Activity_evt_S0002"])
        self.assertNotIn("Activity_evt_S0001__TakeoverFrontier", pipeline)
        self.assertEqual(first["post_delay"], 1500)
        self.assertEqual(first["timeout"], 8000)
        self.assertEqual(
            second["next"],
            ["Activity_evt_S0002__TakeoverFrontier"],
        )
        self.assertEqual(second["timeout"], 8000)
        self.assertNotIn("post_delay", second)
        frontier = pipeline["Activity_evt_S0002__TakeoverFrontier"]["custom_action_param"]
        self.assertEqual(frontier["reason"], "knowledge_frontier")
        self.assertEqual(frontier["source_state"], "S0002")
        self.assertEqual(frontier["result_candidates"], ["S0003"])
        error = pipeline["Activity_evt_S0001__TakeoverError"]["custom_action_param"]
        self.assertEqual(error["reason"], "recognition_failed")
        self.assertEqual(error["source_state"], "S0001")
        self.assertEqual(error["expected"], re.escape("甲"))
        self.assertEqual(
            pipeline["Activity_evt_S0001__TakeoverError"]["on_error"],
            ["Activity_evt_S0001__Stop"],
        )
        self.assertEqual(
            pipeline["Activity_evt_S0002__TakeoverError"]["next"],
            ["Activity_evt_S0002__Stop"],
        )
        self.assertEqual(pipeline["Activity_evt_S0001__Stop"]["action"], "StopTask")
        router = pipeline["Activity_evt_StartRouter"]
        self.assertEqual(
            router["next"],
            ["Activity_evt_S0001", "Activity_evt_S0002"],
        )
        self.assertEqual(router["on_error"], ["Activity_evt_StartRouter__TakeoverUnknown"])
        unknown = pipeline["Activity_evt_StartRouter__TakeoverUnknown"]
        self.assertEqual(unknown["custom_action"], "DumpActivityTakeover")
        self.assertEqual(unknown["next"], ["Activity_evt_StartRouter__Stop"])
        self.assertEqual(unknown["on_error"], ["Activity_evt_StartRouter__Stop"])
        router_param = unknown["custom_action_param"]
        self.assertEqual(router_param["reason"], "start_router_unmatched")
        self.assertIsNone(router_param["source_state"])
        self.assertEqual(router_param["known_candidates"], ["S0001", "S0002"])
        self.assertEqual(router_param["event"], "evt")
        self.assertEqual(router_param["session"], "20260925-000000")
        self.assertTrue(router_param["flow_path"].endswith("flow.json"))
        self.assertTrue(router_param["pipeline_path"].endswith("pipeline.json"))
        self.assertEqual(pipeline["Activity_evt_StartRouter__Stop"]["action"], "StopTask")
        self.assertNotIn("DirectHit", [pipeline[name].get("recognition") for name in router["next"]])

    def test_overlap_warns_without_reordering(self):
        pipeline = self._compile(
            [
                _state("S0001", "maa_ready", _ocr("相同"), {"type": "DoNothing"}),
                _state("S0002", "maa_ready", _ocr("相同"), {"type": "DoNothing"}),
            ],
            event="evt",
        )
        self.assertEqual(
            pipeline["Activity_evt_StartRouter"]["next"],
            ["Activity_evt_S0001", "Activity_evt_S0002"],
        )
        self.assertTrue(pipeline["$meta"]["warnings"])

    def test_windows_session_path_roundtrips(self):
        pipeline = self._compile(
            [_state("S0001", "maa_ready", _ocr("路径"), {"type": "DoNothing"})]
        )
        text = json.dumps(pipeline, ensure_ascii=False)
        loaded = json.loads(text)
        param = loaded["Activity_open_shell_S0001__TakeoverError"]["custom_action_param"]
        self.assertEqual(param["session_dir"], str(self.session.resolve()))
        self.assertIn("开心水族箱活动经验", param["session_dir"])
        self.assertIn("\\", param["session_dir"])

    def test_slug(self):
        self.assertEqual(slug_event("sea-dive"), "sea_dive")


class SchemaValidationTest(unittest.TestCase):
    def test_generated_pipeline_passes_maa_schema_and_regex(self):
        with tempfile.TemporaryDirectory(prefix="schema_", dir=r"D:\开心水族箱活动经验") as temp:
            session = Path(temp)
            states = [
                _state(
                    "S0001",
                    "maa_ready",
                    _ocr("开始(1)"),
                    {"type": "ClickRecognitionResult"},
                    ["S0009"],
                )
            ]
            flow = {"exploration_task": "schema-check", "session_id": "s", "states": states}
            output = session / "generated" / "pipeline.json"
            pipeline = compile_flow(flow, session, output)
            output.parent.mkdir(parents=True)
            output.write_text(json.dumps(pipeline, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            for node in pipeline.values():
                if isinstance(node, dict) and isinstance(node.get("expected"), str):
                    re.compile(node["expected"])
            resource_dir = session / "resource"
            resource_dir.mkdir()
            (resource_dir / "pipeline.json").write_text(output.read_text(encoding="utf-8"), encoding="utf-8")
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCHEMA_TOOL),
                    "--schema-dir",
                    str(SCHEMA_DIR),
                    "--resource-dirs",
                    str(resource_dir),
                    "--interface-files",
                    str(MAA_ROOT / "assets" / "interface.json"),
                ],
                cwd=str(MAA_ROOT),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            self.assertEqual(
                completed.returncode,
                0,
                completed.stdout + "\n" + completed.stderr,
            )
            self.assertIn("[OK]", completed.stdout)

    def test_compile_session_writes_generated_pipeline(self):
        with tempfile.TemporaryDirectory(prefix="sess_", dir=r"D:\开心水族箱活动经验") as temp:
            session = Path(temp)
            flow = {
                "exploration_task": "demo",
                "session_id": "1",
                "states": [_state("S0001", "maa_ready", _ocr("甲"), {"type": "DoNothing"})],
            }
            (session / "flow.json").write_text(
                json.dumps(flow, ensure_ascii=False),
                encoding="utf-8",
            )
            output = compile_session(session)
            self.assertTrue(output.is_file())
            self.assertEqual(output.parent.name, "generated")


if __name__ == "__main__":
    unittest.main()
