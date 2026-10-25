"""Bounded reusable steps; each click is gated, recorded and checked separately."""
import re
from pathlib import Path
import cv2
import numpy as np
from PIL import Image


def template_score(picture, template, roi):
    x, y, width, height = roi
    frame = np.asarray(picture.convert("RGB"))[y:y + height, x:x + width]
    if frame.shape[0] < template.shape[0] or frame.shape[1] < template.shape[1]:
        return -1.0
    return float(cv2.minMaxLoc(cv2.matchTemplate(frame, template, cv2.TM_CCOEFF_NORMED))[1])


def backpack_slots(picture, directory):
    kinds = ("plain", "locked")
    templates = {kind: np.asarray(Image.open(Path(directory) / ("backpack_%s.png" % kind)).convert("RGB")) for kind in kinds}
    result = []
    for y in (200, 375, 550):
        for x in (210, 400, 590, 780):
            scores = {kind: template_score(picture, template, [x-65,y-50,130,125]) for kind, template in templates.items()}
            ordered = sorted(scores, key=scores.get, reverse=True)
            if scores[ordered[0]] >= .97 and scores[ordered[0]]-scores[ordered[1]] >= .10:
                result.append({"point":[x,y], "kind":ordered[0], "scores":scores})
    return result


def free_backpack_counts(rows):
    text = " ".join(row.get("text", "") for row in rows)
    if "翻找背包" not in text:
        raise ValueError("Not the backpack screen")
    if repair_modal(rows) or "开心收下" in text or "确定现在结束游戏" in text:
        raise ValueError("Modal covers the backpack screen")
    counts = []
    for name in ("普通", "加锁"):
        found = re.search(name + r"背包\s*([0-4])\s*/\s*([1-4])", text)
        if found:
            count = int(found.group(1))
            total = int(found.group(2))
            other = "加锁" if name == "普通" else "普通"
            free_context = "可免费开启" in text or "额外开启%s背包消耗" % other in text
            if count > total or not free_context or "额外开启%s背包消耗" % name in text:
                raise ValueError("Quota out of range")
            counts.append(count)
        elif "额外开启%s背包消耗" % name in text:
            counts.append(0)
        else:
            raise ValueError("Free quota is unreadable")
    return tuple(counts)


def repair_modal(rows):
    return any("检修中" in row.get("text", "") or "指针进入绿色" in row.get("text", "") for row in rows)


def guard_modal(rows, command):
    """A visible background title does not establish that its controls are exposed."""
    text = " ".join(row.get("text", "") for row in rows)
    if "档案冲突" in text or "本次档案无法保存" in text:
        if not (command.get("server_reload_authorized") is True
                and command.get("op") == "tap_text" and command.get("expect") == "确定"):
            raise ValueError("Save conflict: stop input and obtain explicit permission to load the server save")
    if repair_modal(rows):
        expected = command.get("modal_expect", "")
        if expected not in ("检修中", "在指针进入绿色区域时点击") or not any(
                expected in row.get("text", "") for row in rows):
            raise ValueError("Repair modal present; inspect it and explicitly target its control")


def prepare_backpacks(device, recorder, session, execute):
    directory = Path(__file__).resolve().parents[3] / "assets/dudu-rescue/templates"
    actions = []
    for _ in range(4):
        picture = device.screencap()
        normal, locked = free_backpack_counts(device.vision.ocr(picture))
        kind = "plain" if normal else "locked" if locked else None
        if kind is None:
            return {"done":True,"actions":actions}
        slots = [item for item in backpack_slots(picture,directory) if item["kind"] == kind]
        if not slots:
            return {"stopped":"No verified unopened backpack","actions":actions}
        result = execute({"op":"tap","point":slots[0]["point"],"safety":"confirmed_safe",
                          "reason":"复用免费背包模块：OCR额度%s/%s，模板确认%s包" % (normal,locked,kind),
                          "note":str(slots[0]),"read_after":True},device,recorder,session)
        actions.append(result)
        if result.get("error") or result.get("ocr_error") or result.get("executed") is not True:
            return {"stopped":"Action or OCR failed","actions":actions}
        expected = (normal-1,locked) if kind == "plain" else (normal,locked-1)
        try:
            remaining = free_backpack_counts(result["ocr"])
        except ValueError as exc:
            return {"stopped":str(exc),"actions":actions}
        if remaining != expected:
            return {"stopped":"Quota did not decrement exactly once","actions":actions}
    return {("done" if remaining == (0, 0) else "stopped"):
            (True if remaining == (0, 0) else "Four-action limit reached"), "actions":actions}


def repair_plane(device,recorder,session,execute,references):
    if len(references) > 5:
        raise ValueError("At most five verified normal wrenches")
    actions = []
    for reference in references:
        picture = device.screencap()
        rows = device.vision.ocr(picture)
        text = " ".join(row.get("text", "") for row in rows)
        if repair_modal(rows):
            return {"stopped":"Repair modal needs Agent inspection","actions":actions}
        if "点击扳手" not in text or "飞机检修" not in text:
            return {"stopped":"Plane page gate failed","actions":actions}
        template = np.asarray(Image.open(reference["template"]).convert("RGB"))
        score = template_score(picture,template,reference["roi"])
        if score < .92:
            return {"stopped":"Normal wrench changed","score":score,"actions":actions}
        result = execute({"op":"tap","point":reference["point"],"safety":"confirmed_safe",
                          "reason":"复用免费检修：飞机页门禁及普通扳手模板均命中",
                          "note":"template=%s score=%.4f" % (reference["template"],score),
                          "read_after":True},device,recorder,session)
        actions.append(result)
        if result.get("error") or result.get("executed") is not True:
            return {"stopped":"Action or OCR failed","actions":actions}
    return {"done":True,"actions":actions}
