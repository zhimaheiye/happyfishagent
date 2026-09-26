# -*- coding: utf-8 -*-
"""V1.1 StartRouter 零点击 smoke：构造不可能命中的 OCR flow，跑 StartRouter → start_router_unmatched → takeover → StopTask。

要求 0 Click、0 资源消耗。不改活动现场（不进游戏点击）。
"""
import json
import sys
from datetime import datetime
from pathlib import Path

from PIL import Image

MAA_ROOT = Path(r"D:\happyfishgame")
AGENT_ROOT = Path(r"D:\开心水族箱活动经验\happyfishagent")
SCRIPTS = AGENT_ROOT / "happyfish-activity-automation" / "scripts"
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(MAA_ROOT / "agent"))
sys.path.insert(0, str(MAA_ROOT))

import maa
import maa.agent.agent_server as agent_server_mod
from maa.library import Library


def _passthrough(name):
    def wrap(obj):
        return obj
    return wrap


agent_server_mod.AgentServer.custom_action = _passthrough
agent_server_mod.AgentServer.custom_recognition = _passthrough

from maa.controller import AdbController
from maa.resource import Resource
from maa.tasker import Tasker
from maa.toolkit import Toolkit

from activity_takeover import DumpActivityTakeover
from my_action import _capture_720p
from recorder.device import open_client
from recorder.flow_to_maa import compile_session


def _node_names(detail):
    names = []
    nodes = getattr(detail, "nodes", None) or []
    for node in nodes:
        name = getattr(node, "name", None)
        if name:
            names.append(name)
    return names


def main():
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    session = (
        AGENT_ROOT
        / "happyfish-activity-automation"
        / "activities"
        / "startrouter-smoke"
        / "sessions"
        / stamp
    )
    (session / "screenshots").mkdir(parents=True)
    (session / "diffs").mkdir()
    (session / "takeover").mkdir(parents=True)
    flow = {
        "exploration_task": "startrouter-smoke",
        "session_id": stamp,
        "states": [
            {
                "state": "S0001",
                "name": None,
                "status": "maa_ready",
                "recognition": {
                    "type": "OCR",
                    "expected": "__MHF_ROUTER_IMPOSSIBLE_A__",
                    "expected_mode": "literal",
                    "recommended_roi": [0, 0, 1280, 720],
                },
                "action": {"type": "DoNothing"},
                "result_candidates": [],
                "timing": {"recognition_timeout_ms": 2500},
                "safety": {"level": "readonly", "reason": "不可能命中的字面量"},
            },
            {
                "state": "S0002",
                "name": None,
                "status": "maa_ready",
                "recognition": {
                    "type": "OCR",
                    "expected": "__MHF_ROUTER_IMPOSSIBLE_B__",
                    "expected_mode": "literal",
                    "recommended_roi": [0, 0, 1280, 720],
                },
                "action": {"type": "DoNothing"},
                "result_candidates": [],
                "timing": {"recognition_timeout_ms": 2500},
                "safety": {"level": "readonly", "reason": "不可能命中的字面量"},
            },
        ],
    }
    (session / "flow.json").write_text(
        json.dumps(flow, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    pipeline_path = compile_session(session)
    pipeline = json.loads(pipeline_path.read_text(encoding="utf-8"))
    runnable = {key: value for key, value in pipeline.items() if not key.startswith("$")}
    for node in runnable.values():
        if node.get("action") == "Click":
            raise SystemExit("smoke Pipeline 含 Click，拒绝实机运行")
    entry = pipeline["$meta"]["start_router"]
    print("entry", entry, flush=True)
    print("click_nodes", sum(1 for node in runnable.values() if node.get("action") == "Click"), flush=True)

    client = open_client()
    print("device", client.serial, client.source, flush=True)
    Library.open(Path(maa.__file__).parent / "bin", agent_server=False)
    Toolkit.init_option(str(MAA_ROOT))
    controller = AdbController(client.adb_path, client.serial)
    controller.set_screenshot_target_short_side(720)
    connected = controller.post_connection().wait()
    if not connected.succeeded:
        raise SystemExit("adb 控制器连接失败")

    resource = Resource()
    model = resource.post_ocr_model(MAA_ROOT / "assets" / "resource" / "model" / "ocr").wait()
    if not model.succeeded:
        raise SystemExit("OCR 模型加载失败")
    action = DumpActivityTakeover()
    action.capture = _capture_720p
    if not resource.register_custom_action("DumpActivityTakeover", action):
        raise SystemExit("注册 DumpActivityTakeover 失败")

    tasker = Tasker()
    if not tasker.bind(resource, controller):
        raise SystemExit("Tasker 绑定失败")
    job = tasker.post_task(entry, runnable).wait()
    detail = job.get()
    names = _node_names(detail)
    print("task_succeeded", job.succeeded, "nodes", names, flush=True)

    packages = sorted((session / "takeover").iterdir())
    packages = [item for item in packages if item.is_dir() and (item / "meta.json").is_file()]
    if not packages:
        raise SystemExit("没有生成 takeover package")
    latest = packages[-1]
    meta = json.loads((latest / "meta.json").read_text(encoding="utf-8"))
    image = Image.open(latest / "current.png")
    print("package", latest, flush=True)
    print(json.dumps(meta, ensure_ascii=False, indent=2), flush=True)

    problems = []
    if meta.get("reason") != "start_router_unmatched":
        problems.append("reason=%s" % meta.get("reason"))
    if meta.get("source_state") is not None:
        problems.append("source_state=%s" % meta.get("source_state"))
    if sorted(meta.get("known_candidates") or []) != ["S0001", "S0002"]:
        problems.append("known_candidates=%s" % meta.get("known_candidates"))
    if not str(meta.get("pipeline_node") or "").endswith("__TakeoverUnknown"):
        problems.append("pipeline_node=%s" % meta.get("pipeline_node"))
    if image.size != (1280, 720):
        problems.append("screenshot=%s" % (image.size,))
    if names:
        if not any(name.endswith("__TakeoverUnknown") for name in names):
            problems.append("task detail 没有 TakeoverUnknown: %s" % names)
        if not names[-1].endswith("__Stop"):
            problems.append("最后节点不是 StopTask: %s" % names)
    if problems:
        raise SystemExit("SMOKE_FAIL: " + "; ".join(problems))
    print("SMOKE_OK", latest, flush=True)


if __name__ == "__main__":
    main()
