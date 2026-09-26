# -*- coding: utf-8 -*-
"""把一个 activity session 的 maa_ready flow 编译成 sessions/<id>/generated/pipeline.json。

    python flow_to_maa.py --session <session 目录>
    python flow_to_maa.py --event <event> [--session <id>]
"""
import argparse
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from recorder.flow_to_maa import CompileError, compile_session
from recorder.session import Session


def main(argv=None):
    parser = argparse.ArgumentParser(description="编译 maa_ready flow 为临时 Maa Pipeline")
    parser.add_argument("--event", default=None)
    parser.add_argument("--session", default=None, help="session id，或配合空 event 时的 session 目录")
    args = parser.parse_args(argv)
    try:
        if args.session and not args.event and Path(args.session).is_dir():
            session_dir = Path(args.session)
        elif args.event:
            if args.session:
                session_dir = Session.open_id(args.event, args.session).path
            else:
                session_dir = Session.open_latest(args.event).path
        else:
            print("请提供 --event，或 --session <目录>", file=sys.stderr)
            return 2
        output = compile_session(session_dir)
    except CompileError as exc:
        print(exc, file=sys.stderr)
        return 1
    except FileNotFoundError as exc:
        print(exc, file=sys.stderr)
        return 1
    print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
