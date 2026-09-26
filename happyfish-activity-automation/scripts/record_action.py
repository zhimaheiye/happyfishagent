# -*- coding: utf-8 -*-
"""AI Action Recorder V0。探索时用它代替裸的 adb input tap。

示例（在 scripts 目录下）：

    python record_action.py --event sea-dive init
    python record_action.py --event sea-dive shot
    python record_action.py --event sea-dive --safety nav --reason "打开活动入口" tap 905 593
    python record_action.py --event sea-dive --safety nav --reason "拖动列表" swipe 640 500 640 200 400

坐标默认是设备像素（adb input 的坐标系）。如果看的是本工具存下来的 1280×720 截图，加 --coord-space 720p。

安全级别缺省是 unknown，未知 / 付费 / 广告 / 危险词不会真正点击。
"""
import argparse
import json
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from recorder.device import DeviceError, open_client
from recorder.engine import Recorder, annotate, open_session
from recorder.safety import SAFE_LEVELS


def build_parser():
    parser = argparse.ArgumentParser(description="记录一次开心水族箱探索动作，并保存前后证据")
    parser.add_argument("--event", required=True, help="活动目录名，例如 sea-dive")
    parser.add_argument("--session", default=None, help="指定 session id；默认用该活动最新一次")
    parser.add_argument("--reason", default=None, help="为什么要点这一下")
    parser.add_argument(
        "--safety",
        default="unknown",
        help="nav/close/tab/readonly/confirmed_safe 才会执行；未知和付费默认拒绝",
    )
    parser.add_argument("--note", default=None, help="AI 备注，只记录，不当成已确认规则")
    parser.add_argument(
        "--coord-space",
        choices=("device", "720p"),
        default="device",
        help="传入坐标的坐标系。存盘时两种都会写",
    )
    parser.add_argument("--max-wait", type=float, default=8.0, help="等待画面稳定的最长时间（秒）")
    parser.add_argument("--poll", type=float, default=0.25, help="稳定检测的采样间隔（秒）")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("init", help="新建一个不会覆盖旧证据的 session")
    sub.add_parser("shot", help="只截图并记成当前 observed 状态")

    tap = sub.add_parser("tap", help="点击并保存 before/after")
    tap.add_argument("x", type=int)
    tap.add_argument("y", type=int)

    swipe = sub.add_parser("swipe", help="滑动并保存 before/after")
    swipe.add_argument("x1", type=int)
    swipe.add_argument("y1", type=int)
    swipe.add_argument("x2", type=int)
    swipe.add_argument("y2", type=int)
    swipe.add_argument("duration", type=int, help="毫秒")

    note = sub.add_parser("annotate", help="补充状态名或识别提议。默认只记为 proposed")
    note.add_argument("--state", required=True)
    note.add_argument("--name", default=None)
    note.add_argument(
        "--status",
        choices=("observed", "proposed", "confirmed", "maa_ready"),
        default=None,
    )
    note.add_argument("--recognition-type", default=None)
    note.add_argument("--expected", default=None)
    note.add_argument("--bbox", nargs=4, type=int, default=None)
    note.add_argument("--roi", nargs=4, type=int, default=None)
    return parser


def _print_result(session, payload):
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    print("session", session.path)


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        if args.command == "init":
            session = open_session(args.event, create=True)
            _print_result(session, {"created": session.flow["session_id"], "flow": str(session.flow_path)})
            return 0

        session = open_session(args.event, session_id=args.session)
        if args.command == "annotate":
            recognition = {}
            if args.recognition_type:
                recognition["type"] = args.recognition_type
            if args.expected:
                recognition["expected"] = args.expected
            if args.bbox:
                recognition["bbox"] = list(args.bbox)
            if args.roi:
                recognition["recommended_roi"] = list(args.roi)
            trace = annotate(session, args.state, args.name, args.status, recognition or None)
            _print_result(session, {"trace": trace})
            return 0

        client = open_client()
        recorder = Recorder(client, session, max_wait_s=args.max_wait, poll_s=args.poll)
        if args.command == "shot":
            _print_result(session, recorder.shot())
            return 0
        if args.command == "tap":
            result = recorder.act(
                "tap",
                [(args.x, args.y)],
                None,
                args.coord_space,
                args.reason,
                args.safety,
                args.note,
            )
        else:
            result = recorder.act(
                "swipe",
                [(args.x1, args.y1), (args.x2, args.y2)],
                args.duration,
                args.coord_space,
                args.reason,
                args.safety,
                args.note,
            )
        _print_result(session, result)
        if not result.get("executed"):
            print("已拒绝执行。允许的 safety: %s" % ", ".join(SAFE_LEVELS), file=sys.stderr)
            return 2
        return 0
    except DeviceError as exc:
        print("设备错误: %s" % exc, file=sys.stderr)
        return 3
    except (FileNotFoundError, KeyError, ValueError) as exc:
        print(exc, file=sys.stderr)
        return 4


if __name__ == "__main__":
    sys.exit(main())
