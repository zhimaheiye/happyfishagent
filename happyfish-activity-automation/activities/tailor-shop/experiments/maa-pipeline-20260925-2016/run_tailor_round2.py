# -*- coding: utf-8 -*-
"""巧手裁缝铺主活动第 2 局（授权消耗最后 1 体力）：
入口=StartRouter，从活动主界面(精选布料,体力1)启动，Maa 自动:
  精选布料(耗1体力)→免费剪刀档→剪布循环(OCR动态定位最左堆,next链先查剪刀0防死循环)
  →完成本关→结算→[遭遇弹窗B/AC frontier→DumpActivityTakeover→Stop]
剪刀0或弹窗等 frontier 时 AI 接手处理，处理完可重跑本脚本继续（StartRouter 从当前画面续路由）。
使用 maa-pipeline-20260925-2016/generated/pipeline.json（模板绝对路径）。
"""
import json
import sys
from pathlib import Path

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


def _node_names(detail):
    names = []
    nodes = getattr(detail, "nodes", None) or []
    for node in nodes:
        name = getattr(node, "name", None)
        if name:
            names.append(name)
    return names


def main():
    experiment = Path(
        r"D:\开心水族箱活动经验\happyfishagent\happyfish-activity-automation"
        r"\activities\tailor-shop\experiments\maa-pipeline-20260925-2016"
    )
    pipeline_path = experiment / "generated" / "pipeline.json"
    pipeline = json.loads(pipeline_path.read_text(encoding="utf-8"))
    runnable = {key: value for key, value in pipeline.items() if not key.startswith("$")}
    entry = pipeline["$meta"]["start_router"]

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
    print("entry", entry, flush=True)
    job = tasker.post_task(entry, runnable).wait()
    detail = job.get()
    names = _node_names(detail)
    print("task_succeeded", job.succeeded, "nodes", names, flush=True)

    session_dir = Path(pipeline["$meta"]["session_dir"])
    packages = sorted((session_dir / "takeover").iterdir()) if (session_dir / "takeover").is_dir() else []
    packages = [item for item in packages if item.is_dir() and (item / "meta.json").is_file()]
    if packages:
        latest = packages[-1]
        meta = json.loads((latest / "meta.json").read_text(encoding="utf-8"))
        print("TAKEOVER", latest, flush=True)
        print(json.dumps(meta, ensure_ascii=False, indent=2), flush=True)
    else:
        print("NO_TAKEOVER_PACKAGE", flush=True)


if __name__ == "__main__":
    sys.exit(main())
