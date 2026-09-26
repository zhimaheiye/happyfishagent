# -*- coding: utf-8 -*-
"""把 session 里 status=maa_ready 的 flow 编译成临时 Maa Pipeline。

不写 MaaHappyFish 的正式 feature 目录。
observed / proposed / confirmed 不参与生成。缺参数就失败，不补默认识别。
"""
import json
import re
from pathlib import Path

DEFAULT_RECOGNITION_TIMEOUT_MS = 8000
DEFAULT_POST_DELAY_MS = 800
TRACE_TAIL_LIMIT = 10

_ACTION_CLICK_RESULT = "ClickRecognitionResult"
_ACTION_DO_NOTHING = "DoNothing"
_FIXED_CLICK_TYPES = {"Click", "FixedClick", "fixed_click"}


class CompileError(Exception):
    def __init__(self, errors):
        self.errors = list(errors)
        super().__init__("\n".join(self.errors))


def slug_event(event):
    text = re.sub(r"[^0-9A-Za-z]+", "_", str(event or "")).strip("_")
    if not text:
        raise CompileError(["event 为空，无法生成节点名"])
    if text[0].isdigit():
        text = "e_" + text
    return text


def node_name(slug, state_id):
    return "Activity_%s_%s" % (slug, state_id)


def _is_int_list(value, length):
    return (
        isinstance(value, list)
        and len(value) == length
        and all(isinstance(item, int) and not isinstance(item, bool) for item in value)
    )


def _recognition_timeout(state):
    timing = state.get("timing") if isinstance(state.get("timing"), dict) else {}
    value = timing.get("recognition_timeout_ms")
    if value is None:
        return DEFAULT_RECOGNITION_TIMEOUT_MS
    if isinstance(value, bool) or not isinstance(value, int) or value == 0 or value < -1:
        raise CompileError(
            ["%s 的 timing.recognition_timeout_ms 不是合法毫秒数" % state.get("state")]
        )
    return value


def _post_delay(state):
    """用实测 action_to_stable_ms。Recorder 的等待超时不是这个字段，不能拿来当 post_delay。"""
    timing = state.get("timing") if isinstance(state.get("timing"), dict) else {}
    stable = timing.get("action_to_stable_ms")
    if stable is None:
        return DEFAULT_POST_DELAY_MS
    if isinstance(stable, bool) or not isinstance(stable, (int, float)) or stable < 0:
        raise CompileError(
            ["%s 的 timing.action_to_stable_ms 不是合法毫秒数" % state.get("state")]
        )
    return int(stable)


def _expected_text(recognition, state_id):
    expected = recognition.get("expected")
    if not isinstance(expected, str) or not expected:
        raise CompileError(["%s 是 maa_ready，但 recognition.expected 为空" % state_id])
    mode = recognition.get("expected_mode") or "literal"
    if mode not in ("literal", "regex"):
        raise CompileError(
            ["%s 的 expected_mode=%r，只允许 literal 或 regex" % (state_id, mode)]
        )
    if mode == "literal":
        compiled = re.escape(expected)
    else:
        compiled = expected
    try:
        re.compile(compiled)
    except re.error as exc:
        raise CompileError(["%s 的 expected 不是合法正则: %s" % (state_id, exc)])
    return compiled


def _roi(recognition, state_id):
    roi = recognition.get("recommended_roi")
    if not _is_int_list(roi, 4):
        raise CompileError(
            ["%s 是 maa_ready，但缺少 recognition.recommended_roi（4 个整数）" % state_id]
        )
    return list(roi)


def _resolve_template(recognition, state_id, session_dir):
    raw = recognition.get("template")
    if not isinstance(raw, str) or not raw.strip():
        raise CompileError(["%s 是 maa_ready，但缺少 recognition.template" % state_id])
    if "threshold" not in recognition:
        raise CompileError(["%s 是 maa_ready，但缺少 recognition.threshold" % state_id])
    threshold = recognition.get("threshold")
    if isinstance(threshold, bool) or not isinstance(threshold, (int, float)):
        raise CompileError(["%s 的 recognition.threshold 不是数字" % state_id])
    path = Path(raw)
    if not path.is_absolute():
        path = Path(session_dir) / path
    if not path.is_file():
        raise CompileError(["%s 是 maa_ready，但模板文件不存在: %s" % (state_id, raw)])
    return raw, float(threshold), str(path.resolve())


def _candidates(state):
    raw = state.get("result_candidates")
    if isinstance(raw, list) and raw:
        return [str(item) for item in raw]
    result_state = state.get("result_state")
    if isinstance(result_state, str) and result_state:
        return [result_state]
    return []


def _fixed_point(action, state_id):
    point = action.get("target_center_720p")
    if point is None:
        point = action.get("target_720p")
    if not _is_int_list(point, 2):
        raise CompileError(
            [
                "%s 是固定坐标点击，但缺少 target_center_720p。"
                "不会使用 device_tap_coordinate。" % state_id
            ]
        )
    return list(point)


def _overlap_warnings(ready_states):
    seen = {}
    warnings = []
    for state in ready_states:
        recognition = state.get("recognition") or {}
        kind = recognition.get("type")
        if kind == "OCR":
            key = ("OCR", recognition.get("expected"), recognition.get("expected_mode") or "literal")
        elif kind == "TemplateMatch":
            key = ("TemplateMatch", recognition.get("template"))
        else:
            continue
        previous = seen.get(key)
        if previous:
            warnings.append(
                "%s 与 %s 的 recognition 相同（%s），StartRouter 仍按 flow 顺序，没有改优先级"
                % (previous, state.get("state"), kind)
            )
        else:
            seen[key] = state.get("state")
    return warnings


def compile_flow(flow, session_dir, pipeline_path):
    """返回 pipeline dict。失败时 CompileError.errors 列出每个 state 缺什么。"""
    session_dir = Path(session_dir)
    pipeline_path = Path(pipeline_path)
    event = flow.get("exploration_task") or flow.get("task") or flow.get("event")
    if not event:
        raise CompileError(["flow 缺少 exploration_task / task"])
    slug = slug_event(event)
    states = flow.get("states") if isinstance(flow.get("states"), list) else []
    ready = [state for state in states if isinstance(state, dict) and state.get("status") == "maa_ready"]
    if not ready:
        raise CompileError(["没有 status=maa_ready 的状态，不生成 Pipeline"])

    errors = []
    prepared = []
    for state in ready:
        state_id = str(state.get("state") or "")
        if not re.fullmatch(r"[0-9A-Za-z_]+", state_id):
            errors.append("%s 不是可用的状态编号" % (state.get("state"),))
            continue
        try:
            prepared.append(_prepare_state(state, state_id, session_dir))
        except CompileError as exc:
            errors.extend(exc.errors)
    if errors:
        raise CompileError(errors)

    ready_ids = {item["state_id"] for item in prepared}
    warnings = _overlap_warnings(ready)
    pipeline = {
        "$meta": {
            "event": event,
            "event_slug": slug,
            "session_id": flow.get("session_id"),
            "session_dir": str(session_dir.resolve()),
            "flow_path": str((session_dir / "flow.json").resolve()),
            "pipeline_path": str(pipeline_path.resolve()),
            "warnings": warnings,
            "trace_tail_limit": TRACE_TAIL_LIMIT,
        }
    }
    router_next = []
    for item in prepared:
        state_id = item["state_id"]
        base = node_name(slug, state_id)
        error_name = base + "__TakeoverError"
        frontier_name = base + "__TakeoverFrontier"
        stop_name = base + "__Stop"
        known = []
        unknown = []
        for candidate in item["candidates"]:
            if candidate in ready_ids:
                known.append(node_name(slug, candidate))
            else:
                unknown.append(candidate)
        next_nodes = list(known)
        if unknown:
            next_nodes.append(frontier_name)
        node = dict(item["node"])
        fail_next = item.get("fail_next")
        if fail_next:
            if str(fail_next) in ready_ids:
                # 识别失败 -> 进入指定节点（如 CHECK 未命中 -> FLIP），resumable 分支用
                node["on_error"] = [node_name(slug, str(fail_next))]
            else:
                errors.append("%s 的 recognition_fail_next=%r 不是 maa_ready 状态" % (state_id, fail_next))
                continue
        else:
            node["on_error"] = [error_name]
        if next_nodes:
            node["next"] = next_nodes
        pipeline[base] = node
        router_next.append(base)

        common = {
            "event": event,
            "event_slug": slug,
            "session": flow.get("session_id"),
            "session_dir": str(session_dir.resolve()),
            "flow_path": str((session_dir / "flow.json").resolve()),
            "pipeline_path": str(pipeline_path.resolve()),
            "source_state": state_id,
            "expected": item["expected"],
            "roi": item["roi"],
            "result_candidates": item["candidates"],
        }
        if item.get("template"):
            common["template"] = item["template"]
        error_param = dict(common)
        error_param.update({"reason": "recognition_failed", "pipeline_node": error_name})
        frontier_param = dict(common)
        frontier_param.update(
            {
                "reason": "knowledge_frontier",
                "pipeline_node": frontier_name,
                "result_candidates": unknown,
            }
        )
        pipeline[error_name] = _takeover_node(error_param, stop_name, state_id, "recognition_failed")
        if unknown:
            pipeline[frontier_name] = _takeover_node(
                frontier_param, stop_name, state_id, "knowledge_frontier"
            )
        pipeline[stop_name] = {
            "recognition": "DirectHit",
            "action": "StopTask",
            "focus": {
                "Node.Action.Succeeded": "[%s] %s 已停止，不再继续点击" % (event, state_id)
            },
        }

    router = "Activity_%s_StartRouter" % slug
    router_unknown = router + "__TakeoverUnknown"
    router_stop = router + "__Stop"
    known_state_ids = [item["state_id"] for item in prepared]
    # Maa 的 next 未命中不会触发子节点 on_error，超时落在 StartRouter 自己身上。
    router_param = {
        "event": event,
        "event_slug": slug,
        "session": flow.get("session_id"),
        "session_dir": str(session_dir.resolve()),
        "flow_path": str((session_dir / "flow.json").resolve()),
        "pipeline_path": str(pipeline_path.resolve()),
        "source_state": None,
        "reason": "start_router_unmatched",
        "pipeline_node": router_unknown,
        "known_candidates": known_state_ids,
        "expected": None,
        "roi": None,
        "result_candidates": [],
    }
    pipeline[router] = {
        "recognition": "DirectHit",
        "action": "DoNothing",
        "next": router_next,
        "on_error": [router_unknown],
        "focus": {
            "Node.Action.Succeeded": "[%s] 从当前画面识别已确认状态" % event
        },
    }
    pipeline[router_unknown] = _takeover_node(
        router_param, router_stop, "StartRouter", "start_router_unmatched"
    )
    pipeline[router_stop] = {
        "recognition": "DirectHit",
        "action": "StopTask",
        "focus": {
            "Node.Action.Succeeded": "[%s] 当前画面不在已知状态中，已停止" % event
        },
    }
    pipeline["$meta"]["start_router"] = router
    return pipeline


def _prepare_state(state, state_id, session_dir):
    recognition = state.get("recognition")
    if not isinstance(recognition, dict):
        raise CompileError(["%s 是 maa_ready，但缺少 recognition" % state_id])
    kind = recognition.get("type")
    action = state.get("action") if isinstance(state.get("action"), dict) else {}
    action_type = action.get("type")
    if kind not in ("OCR", "TemplateMatch"):
        raise CompileError(
            ["%s 是 maa_ready，但 recognition.type=%r，V1 只支持 OCR / TemplateMatch" % (state_id, kind)]
        )
    if action_type in (None, ""):
        raise CompileError(["%s 是 maa_ready，但缺少 action.type" % state_id])

    roi = _roi(recognition, state_id)
    expected = None
    template = None
    node = {"roi": roi, "timeout": _recognition_timeout(state)}
    if kind == "OCR":
        expected = _expected_text(recognition, state_id)
        node.update({"recognition": "OCR", "expected": expected})
    else:
        template, threshold, _resolved = _resolve_template(recognition, state_id, session_dir)
        node.update(
            {
                "recognition": "TemplateMatch",
                "template": template,
                "threshold": threshold,
            }
        )

    if action_type == _ACTION_CLICK_RESULT:
        node["action"] = "Click"
        node["post_delay"] = _post_delay(state)
    elif action_type == _ACTION_DO_NOTHING:
        node["action"] = "DoNothing"
    elif action_type in _FIXED_CLICK_TYPES:
        node["action"] = "Click"
        node["target"] = _fixed_point(action, state_id)
        node["post_delay"] = _post_delay(state)
    else:
        raise CompileError(
            [
                "%s 的 action.type=%r，V1 只支持 ClickRecognitionResult / 固定坐标 Click / DoNothing"
                % (state_id, action_type)
            ]
        )
    node["focus"] = {
        "Node.Recognition.Succeeded": "[%s] 确认 %s" % (state_id, state_id)
    }
    return {
        "state_id": state_id,
        "node": node,
        "expected": expected,
        "roi": roi,
        "template": template,
        "candidates": _candidates(state),
        "fail_next": state.get("recognition_fail_next"),
    }


def _takeover_node(param, stop_name, state_id, reason):
    return {
        "recognition": "DirectHit",
        "action": "Custom",
        "custom_action": "DumpActivityTakeover",
        "custom_action_param": param,
        "next": [stop_name],
        "on_error": [stop_name],
        "focus": {
            "Node.Action.Succeeded": "[%s] %s %s，写入 takeover 后停止" % (state_id, state_id, reason)
        },
    }


def compile_session(session_dir):
    session_dir = Path(session_dir)
    flow_path = session_dir / "flow.json"
    if not flow_path.is_file():
        raise CompileError(["找不到 flow.json: %s" % flow_path])
    flow = json.loads(flow_path.read_text(encoding="utf-8"))
    output = session_dir / "generated" / "pipeline.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    pipeline = compile_flow(flow, session_dir, output)
    output.write_text(json.dumps(pipeline, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return output
