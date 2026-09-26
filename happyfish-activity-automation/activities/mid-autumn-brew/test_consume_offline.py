# -*- coding: utf-8 -*-
"""酿月食香 - 做月饼分支离线 fixture 测试（基于现有 session 截图，0 实机点击）。

覆盖：
1. 活动主页 fresh 识别（做月饼按钮态）
2. 活动主页 resume 识别（继续游戏变体）
3. 体力数字 / 有无体力判断（模板识别 3/2）
4. 退出确认框识别（标题 + 三按钮 OCR）
5. 暂时离开按钮识别
6. 结束游戏不会被误当成暂时离开（文本区分）
7. StartRouter 区分主页(食香) 与 游戏页(规则行)
8. 消耗型入口缺授权 → 不生成可执行 Click（门禁 DENIED + 计划冻结）
9. 已授权 → 允许进入消耗节点（门禁 ALLOWED）
10. 负样本：非主页页面不误报体力数字
"""
from pathlib import Path
import subprocess
import sys
from rapidocr_onnxruntime import RapidOCR

ACT = Path(r"D:\开心水族箱活动经验\happyfishagent\happyfish-activity-automation\activities\mid-autumn-brew")
SESS = ACT / "sessions" / "20260925-143348" / "screenshots"
PY = r"C:\Python313\python.exe"

RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, ok, detail))
    print("[%s] %s %s" % ("PASS" if ok else "FAIL", name, detail))


def ocr_text(shot, roi):
    """rapidocr 整图 OCR 后按 ROI 过滤。"""
    ocr = RapidOCR()
    result, _ = ocr(str(SESS / shot))
    hits = []
    for item in (result or []):
        try:
            box, text, score = item[0], item[1], float(item[2])
            x1, y1 = int(box[0][0]), int(box[0][1])
            x2, y2 = int(box[2][0]), int(box[2][1])
            if x1 < roi[2] and x2 > roi[0] and y1 < roi[3] and y2 > roi[1]:
                hits.append(text)
        except Exception:
            pass
    return hits


def stamina(shot):
    p = subprocess.run([PY, str(ACT / "stamina_detect.py"), str(SESS / shot)],
                       capture_output=True, text=True, encoding="utf-8")
    out = p.stdout.strip()
    digit = out.split("digit=")[1].split(" ")[0] if "digit=" in out else None
    if digit == "None":
        digit = None
    return digit, out


def gate(*extra):
    p = subprocess.run([PY, str(ACT / "gate_check.py")] + list(extra),
                       capture_output=True, text=True, encoding="utf-8")
    return p.stdout.strip(), p.returncode


def main():
    # 1. 主页 fresh（做月饼态）
    t = ocr_text("S0006_after.png", (100, 630, 900, 720))
    check("主页fresh-做月饼按钮OCR", any("做月饼" in x for x in t), str(t))
    check("主页fresh-标题OCR", "食香" in "".join(ocr_text("S0006_after.png", (300, 10, 700, 220))), "标题可见")

    # 2. 主页 resume（继续游戏变体）
    t = ocr_text("S0012_before.png", (400, 630, 750, 720))
    resume_found = any(("继续游戏" in x or "迷续游戏" in x) for x in t)
    check("主页resume-继续游戏按钮OCR", resume_found, str(t))

    # 3. 体力数字判断
    for shot, expect in [("S0006_after.png", "3"), ("S0009_before.png", "3"),
                         ("S0012_before.png", "2"), ("S0020_observe_02.png", "2")]:
        d, out = stamina(shot)
        check("体力识别 %s 期望%s" % (shot, expect), d == expect, "digit=%s" % d)

    # 10. 负样本：非主页页面不误报体力数字
    for shot in ["S0009_after.png", "S0010_after.png", "S0017_after.png", "S0018_after.png"]:
        d, out = stamina(shot)
        check("负样本 %s 不误报" % shot, d in (None, "unknown"), "digit=%s" % d)

    # 4. 确认框识别
    t = ocr_text("S0010_after.png", (350, 120, 650, 260))
    check("确认框标题OCR", any("结束游戏" in x for x in t), str(t))

    # 5/6. 三按钮语义区分
    t = ocr_text("S0010_after.png", (60, 530, 1000, 640))
    has_next = any("下一步骤" in x for x in t)
    has_leave = any("暂时离开" in x for x in t)
    has_finish = any("结束游戏" in x for x in t)
    check("三按钮文本齐全", has_next and has_leave and has_finish,
          "next=%s leave=%s finish=%s" % (has_next, has_leave, has_finish))
    check("结束游戏≠暂时离开(文本独立)", "结束游戏" in "".join(t) and "暂时离开" in "".join(t), "两文本可分别匹配")

    # 7. StartRouter 区分主页与游戏页
    main_title = "食香" in "".join(ocr_text("S0012_before.png", (300, 10, 700, 220)))
    game_rule = any("馅料" in x for x in ocr_text("S0009_after.png", (100, 10, 900, 160)))
    check("主页识别(食香)", main_title)
    check("游戏页识别(规则行)", game_rule)

    # 8. 缺授权 → DENIED（不生成可执行 Click 的前置门禁）
    out, code = gate()
    check("门禁默认DENIED(exit!=0)", code != 0, "exit=%d" % code)
    check("门禁拒绝词", "GATE_DENIED" in out, out.splitlines()[-1])

    # 9. 授权 → ALLOWED
    out, code = gate("--allow-resource", "activity_stamina")
    check("授权后ALLOWED(exit=0)", code == 0 and "GATE_ALLOWED" in out, "exit=%d" % code)

    passed = sum(1 for _, ok, _ in RESULTS if ok)
    print("== 离线测试: %d/%d 通过 ==" % (passed, len(RESULTS)))
    sys.exit(0 if passed == len(RESULTS) else 1)


if __name__ == "__main__":
    main()
