"""Single-step modular exploration console with Recorder evidence; no business Pipeline.

Run with --event SLUG, then send one JSON object per line on stdin.
Examples: {"op":"read"}, {"op":"tap","point":[100,200],
"safety":"nav","reason":"Open help","expect":"Help"}.
The calling Agent owns decisions; this process never loops gameplay itself.
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from recorder.device import open_client
from recorder.engine import Recorder, open_session


def emit(value):
    if isinstance(value, dict) and "actions" in value:
        value = {**value, "actions": [{key: item.get(key) for key in ("executed", "from_state", "to_state", "image", "error") if key in item} for item in value["actions"]]}
    print(json.dumps(value, ensure_ascii=False, default=str), flush=True)


def ocr_matches(rows, expected):
    if not isinstance(expected, str) or not expected.strip():
        raise ValueError("OCR target text must not be empty")
    return [row for row in rows if isinstance(row, dict)
            and expected in str(row.get("text", ""))]


def execute(command, device, recorder, session):
    op = command.get("op")
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    decision = {"ts": datetime.now().isoformat(), "backend": device.source, "command": command}
    log = session.path / "decisions.jsonl"
    with log.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps({**decision, "phase": "before"}, ensure_ascii=False) + "\n")
    try:
        if op in ("known_prepare", "known_repair"):
            from recorder.known_modules import prepare_backpacks, repair_plane
            if op == "known_prepare":
                result = prepare_backpacks(device, recorder, session, execute)
            else:
                result = repair_plane(device, recorder, session, execute, command["references"])
        elif op in ("read", "shot"):
            result = recorder.shot()
        elif op in ("tap", "tap_text", "swipe"):
            from recorder.known_modules import guard_modal
            full_rows = device.ocr()
            source = getattr(getattr(device, "vision", None), "last_ocr_image", None)
            if source:
                decision["guard_image"] = str(source)
            guard_modal(full_rows, command)
            if op == "tap_text" or command.get("expect"):
                rows = device.ocr(command["roi"]) if command.get("roi") else full_rows
                matches = ocr_matches(rows, command.get("expect", ""))
                if len(matches) != 1:
                    raise ValueError("Expected exactly one OCR match; got %s: %s" % (len(matches), rows))
                if op == "tap_text":
                    x, y, width, height = matches[0]["box"]
                    command = {**command, "point": [round(x + width / 2), round(y + height / 2)]}
                decision["recognition"] = {"expected": command["expect"], "matches": matches}
            points = [command["point"]] if op != "swipe" else command["points"]
            result = recorder.act("swipe" if op == "swipe" else "tap", points,
                                  command.get("duration", 700), "720p", command.get("reason"),
                                  command.get("safety", "unknown"), command.get("note"))
        else:
            raise ValueError("Unknown operation: %s" % op)
        if result.get("trace", {}).get("screenshots"):
            result["image"] = str(session.path / result["trace"]["screenshots"]["after"])
        elif result.get("screenshot"):
            result["image"] = str(session.path / result["screenshot"])
        if op == "read" or command.get("read_after"):
            try:
                rows = device.ocr(command.get("read_roi"))
            except Exception as exc:
                # The click may already have happened. Preserve that fact and
                # its screenshot instead of reporting a generic failed action.
                result["ocr_error"] = str(exc)
                result["inspect_before_retry"] = True
                decision["result"] = result
                return result
            ocr_dir = session.path / "ocr"
            ocr_dir.mkdir(exist_ok=True)
            ocr_path = ocr_dir / (stamp + ".json")
            ocr_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
            result["ocr"] = rows
            result["ocr_file"] = str(ocr_path)
            source = getattr(getattr(device, "vision", None), "last_ocr_image", None)
            if source:
                result["recorder_image"] = result.get("image")
                result["image"] = str(source)
        decision["result"] = result
        return result
    except Exception as exc:
        decision["error"] = str(exc)
        return {"error": str(exc), "inspect_before_retry": True}
    finally:
        with log.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps({**decision, "phase": "after"}, ensure_ascii=False, default=str) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--event", required=True)
    parser.add_argument("--session")
    parser.add_argument("--max-wait", type=float, default=2)
    parser.add_argument("--ocr-model-dir", default="D:/happyfishgame/assets/resource/model/ocr")
    parser.add_argument("--command", help="One JSON command; otherwise read JSON lines from stdin")
    args = parser.parse_args()
    from recorder.maa_vision import MaaVision, AdbMaaDevice
    adb = open_client()
    session = open_session(args.event, session_id=args.session)
    device = AdbMaaDevice(adb, MaaVision(session.path, args.ocr_model_dir, adb))
    recorder = Recorder(device, session, max_wait_s=args.max_wait, poll_s=0.35)
    emit({"ready": True, "backend": device.source, "device": adb.serial, "session": str(session.path)})
    if args.command:
        emit(execute(json.loads(args.command), device, recorder, session))
        return
    for line in sys.stdin:
        try:
            command = json.loads(line)
            if command.get("op") == "quit":
                break
            emit(execute(command, device, recorder, session))
        except Exception as exc:
            emit({"error": str(exc)})
    return


if __name__ == "__main__":
    main()
