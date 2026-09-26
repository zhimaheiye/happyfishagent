# -*- coding: utf-8 -*-
"""一个活动 session 的 flow.json + trace.jsonl。

flow 是当前结构化理解，可以随后补充 name / proposal。
trace 只追加，不改历史行。
session 目录一旦创建就不再复用为另一次录制。
"""
import json
import re
from datetime import datetime
from pathlib import Path

STATUS_LEGEND = {
    "observed": "记录器写下的原始事实。recognition 仍为空，不能交给 Maa。",
    "proposed": "AI 或人工提议。不是已确认规则。",
    "confirmed": "已经确认的规则，但还没有编译成 Pipeline。",
    "maa_ready": "已确认，并且允许映射成 Maa 节点。",
}

AUTOMATION_ROOT = Path(__file__).resolve().parents[2]


def activities_root(root=None):
    base = Path(root) if root is not None else AUTOMATION_ROOT
    return base / "activities"


def _check_event(event):
    if not event or event in (".", "..") or "/" in event or "\\" in event or ".." in event:
        raise ValueError("非法 event 名: %r" % (event,))


def new_session_id(when=None):
    moment = when or datetime.now()
    return moment.strftime("%Y%m%d-%H%M%S")


def blank_state(state_id):
    return {
        "state": state_id,
        "name": None,
        "status": "observed",
        "screenshot": None,
        "screenshots": [],
        "resolution": [1280, 720],
        "recognition": None,
        "action": {},
        "result_state": None,
        "result_candidates": [],
        "timing": {},
        "safety": {"level": "unknown", "reason": None},
        "proposals": {},
        "notes": None,
    }


def blank_flow(event, session_id, created_at):
    return {
        "schema": "happyfish.action_recorder.v0",
        "exploration_task": event,
        "task": event,
        "session_id": session_id,
        "created_at": created_at,
        "start_state": None,
        "goal_state": None,
        "semantics": {"one_round": None, "repeat_param": None},
        "status_legend": STATUS_LEGEND,
        "device": None,
        "states": [],
        "timing": [],
        "unknown_states": [],
        "notes": [
            "status=observed 只表示原始事实。AI 猜测的 ROI / expected 写入 proposals，不能直接改成 confirmed。",
        ],
    }


class Session:
    def __init__(self, path):
        self.path = Path(path)
        self.flow_path = self.path / "flow.json"
        self.trace_path = self.path / "trace.jsonl"
        self.flow = json.loads(self.flow_path.read_text(encoding="utf-8"))

    @classmethod
    def create(cls, event, root=None, when=None):
        _check_event(event)
        moment = when or datetime.now()
        session_id = new_session_id(moment)
        base = activities_root(root) / event / "sessions"
        path = base / session_id
        suffix = 2
        while path.exists():
            path = base / ("%s-%d" % (session_id, suffix))
            suffix += 1
        path.mkdir(parents=True)
        (path / "screenshots").mkdir()
        (path / "diffs").mkdir()
        (path / "takeover").mkdir()
        created_at = moment.isoformat(timespec="seconds")
        flow = blank_flow(event, path.name, created_at)
        (path / "flow.json").write_text(
            json.dumps(flow, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        session = cls(path)
        session.append_trace({"type": "session_created", "event": event, "session_id": path.name})
        return session

    @classmethod
    def open_latest(cls, event, root=None):
        _check_event(event)
        base = activities_root(root) / event / "sessions"
        if not base.is_dir():
            raise FileNotFoundError("还没有 %s 的 session，请先 init" % event)
        found = sorted(
            item for item in base.iterdir() if item.is_dir() and (item / "flow.json").is_file()
        )
        if not found:
            raise FileNotFoundError("还没有 %s 的 session，请先 init" % event)
        return cls(found[-1])

    @classmethod
    def open_id(cls, event, session_id, root=None):
        _check_event(event)
        path = activities_root(root) / event / "sessions" / session_id
        if not (path / "flow.json").is_file():
            raise FileNotFoundError("session 不存在: %s" % path)
        return cls(path)

    def save_flow(self):
        temporary = self.flow_path.with_suffix(".json.tmp")
        temporary.write_text(
            json.dumps(self.flow, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        temporary.replace(self.flow_path)

    def append_trace(self, record):
        payload = dict(record)
        payload.setdefault("ts", datetime.now().isoformat(timespec="milliseconds"))
        payload.setdefault("session_id", self.flow.get("session_id"))
        with self.trace_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
            handle.flush()
        return payload

    def states(self):
        return self.flow.setdefault("states", [])

    def next_state_id(self):
        highest = 0
        for state in self.states():
            match = re.fullmatch(r"S(\d+)", str(state.get("state", "")))
            if match:
                highest = max(highest, int(match.group(1)))
        return "S%04d" % (highest + 1)

    def state_by_id(self, state_id):
        for state in self.states():
            if state.get("state") == state_id:
                return state
        raise KeyError(state_id)

    def ensure_open_state(self):
        """返回还没有动作的当前状态。没有的话新建一个 observed 状态。"""
        rows = self.states()
        if rows and not rows[-1].get("action"):
            return rows[-1]
        state = blank_state(self.next_state_id())
        rows.append(state)
        if not self.flow.get("start_state"):
            self.flow["start_state"] = state["state"]
        return state

    def add_result_state(self):
        state = blank_state(self.next_state_id())
        self.states().append(state)
        return state

    def rel(self, path):
        return Path(path).resolve().relative_to(self.path.resolve()).as_posix()
