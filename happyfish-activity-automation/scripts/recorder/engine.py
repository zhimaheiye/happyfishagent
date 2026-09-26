# -*- coding: utf-8 -*-
"""执行一次 tap / swipe / shot，并写下 before、after、diff、trace、flow。"""
import json
import sys
import time
from pathlib import Path

from PIL import Image, ImageChops

_SCRIPTS = Path(__file__).resolve().parents[1]
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import frame_diff  # noqa: E402

from recorder.coords import STD_H, STD_W, scale_point
from recorder.device import choose_input_resolution
from recorder.safety import SafetyRefusal, require_executable
from recorder.session import Session

# 64×36 平均绝对差上的下限。闲置噪声更高时改用噪声倍数，避免鱼缸动画被当成“一直没稳定”。
CHANGE_FLOOR = 1.5
STABLE_FLOOR = 1.2
STABLE_NEED = 3


def to_standard_image(image):
    if image.size == (STD_W, STD_H):
        return image.copy()
    return image.resize((STD_W, STD_H), Image.Resampling.LANCZOS)


def save_png(image, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, format="PNG")
    return path


def wait_settled(capture, before, idle_noise, max_wait_s, poll_s, stable_need=STABLE_NEED):
    """动作之后等待画面先变化、再相对稳定。到 max_wait_s 必须返回，禁止空转。"""
    if max_wait_s < 0:
        raise ValueError("max_wait_s must be >= 0")
    if poll_s <= 0:
        raise ValueError("poll_s must be > 0")
    started = time.monotonic()
    deadline = started + max_wait_s
    change_threshold = max(CHANGE_FLOOR, float(idle_noise) * 2.5)
    stable_threshold = max(STABLE_FLOOR, float(idle_noise) * 1.8)
    previous = before
    last = before
    first_change_at = None
    stable_run = 0
    samples = []

    def pack(timed_out, stable_at):
        return {
            "global_mean_abs": round(frame_diff.mean_abs_diff(before, last), 4),
            "changed_fraction": round(frame_diff.changed_fraction(before, last), 4),
            "bbox_720p": frame_diff.change_bbox(before, last),
            "first_change_ms": None
            if first_change_at is None
            else int(round((first_change_at - started) * 1000)),
            "stable_ms": None if stable_at is None else int(round((stable_at - started) * 1000)),
            "timed_out": timed_out,
            "idle_noise": round(float(idle_noise), 4),
            "change_threshold": round(change_threshold, 4),
            "stable_threshold": round(stable_threshold, 4),
            "max_wait_ms": int(round(max_wait_s * 1000)),
            "samples": samples,
        }

    while True:
        now = time.monotonic()
        if now >= deadline:
            return last, pack(True, None)
        remaining = deadline - now
        time.sleep(min(poll_s, remaining))
        if time.monotonic() >= deadline and samples:
            # 最后一拍如果已经越过上限，不再补截图，直接交出现场。
            return last, pack(True, None)
        frame = capture()
        last = frame
        versus_before = frame_diff.mean_abs_diff(before, frame)
        versus_prev = frame_diff.mean_abs_diff(previous, frame)
        samples.append(
            {
                "t_ms": int(round((time.monotonic() - started) * 1000)),
                "vs_before": round(versus_before, 3),
                "vs_prev": round(versus_prev, 3),
            }
        )
        previous = frame
        if first_change_at is None and versus_before >= change_threshold:
            first_change_at = time.monotonic()
        if first_change_at is not None and versus_prev <= stable_threshold:
            stable_run += 1
            if stable_run >= stable_need:
                return last, pack(False, time.monotonic())
        else:
            stable_run = 0
        if time.monotonic() >= deadline:
            return last, pack(True, None)


def _space(client, screenshot_size):
    if hasattr(client, "coordinate_space"):
        return client.coordinate_space(screenshot_size)
    wm = tuple(client.wm_size())
    chosen, source = choose_input_resolution(wm, screenshot_size, None)
    return {
        "input_resolution": [int(chosen[0]), int(chosen[1])],
        "wm_size": [int(wm[0]), int(wm[1])],
        "input_resolution_source": source,
    }


def _device_block(client, space, image_size):
    return {
        "serial": client.serial,
        "source": client.source,
        "native_resolution": list(space["input_resolution"]),
        "wm_size": list(space["wm_size"]),
        "input_resolution_source": space["input_resolution_source"],
        "screenshot_resolution": [int(image_size[0]), int(image_size[1])],
        "standard_resolution": [STD_W, STD_H],
    }


def _grab(client):
    native = client.screencap()
    return native, to_standard_image(native)


class Recorder:
    def __init__(self, client, session, max_wait_s=8.0, poll_s=0.25, idle_gap_s=0.2):
        self.client = client
        self.session = session
        self.max_wait_s = max_wait_s
        self.poll_s = poll_s
        self.idle_gap_s = idle_gap_s

    def shot(self):
        native, standard = _grab(self.client)
        space = _space(self.client, native.size)
        state = self.session.ensure_open_state()
        filename = "%s_observe_%02d.png" % (state["state"], len(state["screenshots"]) + 1)
        path = save_png(standard, self.session.path / "screenshots" / filename)
        relative = self.session.rel(path)
        state["screenshots"].append(relative)
        state["screenshot"] = relative
        state["resolution"] = [STD_W, STD_H]
        self.session.flow["device"] = _device_block(self.client, space, native.size)
        self.session.save_flow()
        trace = self.session.append_trace(
            {
                "type": "shot",
                "executed": True,
                "state": state["state"],
                "screenshot": relative,
                "device": self.session.flow["device"],
            }
        )
        return {"state": state["state"], "screenshot": relative, "trace": trace}

    def act(self, kind, points, duration_ms, coord_space, reason, safety, note):
        """points: tap 一个点，swipe 两个点。坐标先按 coord_space 解释，再换成设备像素执行。"""
        try:
            level = require_executable(safety, reason, note)
        except SafetyRefusal as refusal:
            return self._refuse(kind, refusal, reason, note)
        _early_native, early = _grab(self.client)
        space = _space(self.client, _early_native.size)
        time.sleep(self.idle_gap_s)
        native_before, before = _grab(self.client)
        idle_noise = frame_diff.mean_abs_diff(early, before)
        device_w, device_h = space["input_resolution"]
        scaled = [scale_point(x, y, device_w, device_h, coord_space) for x, y in points]
        device_points = [item[0] for item in scaled]
        standard_points = [item[1] for item in scaled]

        state = self.session.ensure_open_state()
        before_path = save_png(
            before, self.session.path / "screenshots" / ("%s_before.png" % state["state"])
        )
        before_rel = self.session.rel(before_path)
        state["screenshots"].append(before_rel)
        state["screenshot"] = before_rel
        state["resolution"] = [STD_W, STD_H]
        state["safety"] = {"level": level, "reason": reason}

        if kind == "tap":
            (x, y) = device_points[0]
            (sx, sy) = standard_points[0]
            action = {
                "type": "Click",
                "input": "tap",
                "target_center_720p": [sx, sy],
                "device_tap_coordinate": [x, y],
                "coord_space": coord_space,
                "reason": reason,
                "safety": {"level": level, "reason": reason},
                "ai_note": note,
                "confirmed": None,
            }
            self.client.tap(x, y)
        elif kind == "swipe":
            (x1, y1), (x2, y2) = device_points
            (sx1, sy1), (sx2, sy2) = standard_points
            action = {
                "type": "Swipe",
                "input": "swipe",
                "device_swipe": [x1, y1, x2, y2, int(duration_ms)],
                "standard_swipe_720p": [sx1, sy1, sx2, sy2, int(duration_ms)],
                "coord_space": coord_space,
                "reason": reason,
                "safety": {"level": level, "reason": reason},
                "ai_note": note,
                "confirmed": None,
            }
            self.client.swipe(x1, y1, x2, y2, duration_ms)
        else:
            raise ValueError("unknown action %r" % (kind,))

        state["action"] = action

        def capture_standard():
            _native, image = _grab(self.client)
            return image

        after, diff_info = wait_settled(
            capture_standard,
            before,
            idle_noise,
            max_wait_s=self.max_wait_s,
            poll_s=self.poll_s,
        )
        result = self.session.add_result_state()
        after_path = save_png(
            after, self.session.path / "screenshots" / ("%s_after.png" % state["state"])
        )
        after_rel = self.session.rel(after_path)
        result["screenshots"].append(after_rel)
        result["screenshot"] = after_rel
        result["resolution"] = [STD_W, STD_H]
        state["result_state"] = result["state"]
        state["result_candidates"] = [result["state"]]
        state["timing"] = {
            "action_to_first_change_ms": diff_info["first_change_ms"],
            "action_to_stable_ms": diff_info["stable_ms"],
            "timed_out": diff_info["timed_out"],
        }
        self.session.flow.setdefault("timing", []).append(
            {
                "from": state["state"],
                "to": result["state"],
                "action_to_first_change_ms": diff_info["first_change_ms"],
                "action_to_stable_detect_ms": diff_info["stable_ms"],
                "timed_out": diff_info["timed_out"],
            }
        )
        diff_png = self.session.path / "diffs" / ("%s.png" % state["state"])
        ImageChops.difference(before.convert("RGB"), after.convert("RGB")).save(diff_png)
        diff_json = self.session.path / "diffs" / ("%s.json" % state["state"])
        diff_payload = {
            "from": state["state"],
            "to": result["state"],
            "before": before_rel,
            "after": after_rel,
            "diff_image": self.session.rel(diff_png),
        }
        diff_payload.update(diff_info)
        diff_json.write_text(
            json.dumps(diff_payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        self.session.flow["device"] = _device_block(self.client, space, native_before.size)
        self.session.save_flow()
        trace = self.session.append_trace(
            {
                "type": kind,
                "executed": True,
                "from_state": state["state"],
                "to_state": result["state"],
                "action": action,
                "screenshots": {"before": before_rel, "after": after_rel},
                "diff": {
                    "file": self.session.rel(diff_json),
                    "global_mean_abs": diff_info["global_mean_abs"],
                    "changed_fraction": diff_info["changed_fraction"],
                    "bbox_720p": diff_info["bbox_720p"],
                    "first_change_ms": diff_info["first_change_ms"],
                    "stable_ms": diff_info["stable_ms"],
                    "timed_out": diff_info["timed_out"],
                },
                "device": self.session.flow["device"],
            }
        )
        return {
            "executed": True,
            "from_state": state["state"],
            "to_state": result["state"],
            "trace": trace,
        }

    def _refuse(self, kind, refusal, reason, note):
        try:
            native, standard = _grab(self.client)
            space = _space(self.client, native.size)
            state = self.session.ensure_open_state()
            path = save_png(
                standard,
                self.session.path / "screenshots" / ("%s_refused.png" % state["state"]),
            )
            relative = self.session.rel(path)
            state["screenshots"].append(relative)
            state["screenshot"] = relative
            state["safety"] = {"level": refusal.level, "reason": refusal.reason}
            self.session.flow["device"] = _device_block(self.client, space, native.size)
            screenshot = relative
        except Exception as exc:  # 拒绝本身必须留下；截图失败也不要变成一次点击。
            state = self.session.ensure_open_state()
            state["safety"] = {"level": refusal.level, "reason": refusal.reason}
            screenshot = None
            self.session.flow.setdefault("notes", []).append("拒绝动作时截图失败: %s" % exc)
        self.session.save_flow()
        trace = self.session.append_trace(
            {
                "type": kind,
                "executed": False,
                "state": state["state"],
                "safety": {"level": refusal.level, "reason": refusal.reason},
                "reason": reason,
                "ai_note": note,
                "screenshot": screenshot,
            }
        )
        return {
            "executed": False,
            "state": state["state"],
            "safety": {"level": refusal.level, "reason": refusal.reason},
            "trace": trace,
        }


def annotate(session, state_id, name, status, recognition):
    """recognition 是提议字段。只有显式 confirmed / maa_ready 才写进正式 recognition。"""
    state = session.state_by_id(state_id)
    proposals = state.setdefault("proposals", {})
    if name is not None:
        proposals["name"] = name
    if recognition:
        current = proposals.setdefault("recognition", {})
        current.update(recognition)
    if status in ("confirmed", "maa_ready"):
        if name is not None:
            state["name"] = name
        elif proposals.get("name") and state.get("name") is None:
            state["name"] = proposals["name"]
        if proposals.get("recognition"):
            state["recognition"] = proposals["recognition"]
        state["status"] = status
    elif status == "proposed" or name is not None or recognition:
        if state.get("status") == "observed":
            state["status"] = "proposed"
        if status == "observed":
            state["status"] = "observed"
    elif status:
        state["status"] = status
    session.save_flow()
    return session.append_trace(
        {
            "type": "annotate",
            "executed": False,
            "state": state_id,
            "status": state.get("status"),
            "name": name,
            "recognition": recognition or None,
        }
    )


def open_session(event, session_id=None, create=False, root=None):
    if create:
        return Session.create(event, root=root)
    if session_id:
        return Session.open_id(event, session_id, root=root)
    return Session.open_latest(event, root=root)
