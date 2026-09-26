# -*- coding: utf-8 -*-
"""动作安全分类。

Recorder 看不到按钮语义，不能替调用方判断“这个坐标是不是付费”。
调用方必须显式给出 safety。缺省、未知、以及文案里出现红线词，一律不执行。

允许执行：nav / close / tab / readonly / confirmed_safe
拒绝执行：unknown / pay / ad / danger / choice / irreversible / 其它
"""

SAFE_LEVELS = ("nav", "close", "tab", "readonly", "confirmed_safe")
BLOCK_LEVELS = ("unknown", "pay", "ad", "danger", "choice", "irreversible")

# 与 happyfish-activity-automation/SKILL.md 的红线用词对齐。
DANGER_WORDS = (
    "修复",
    "复活",
    "补充",
    "加速",
    "解锁",
    "续命",
    "开心宝",
    "纸币",
    "广告",
    "看视频",
)


class SafetyRefusal(RuntimeError):
    def __init__(self, level, reason):
        self.level = level
        self.reason = reason
        super().__init__("%s: %s" % (level, reason))


def normalize_level(level):
    text = (level or "unknown").strip().lower()
    if text in SAFE_LEVELS or text in BLOCK_LEVELS:
        return text
    return "unknown"


def assess(level, reason, note):
    """返回 (level, detail)。detail 在因红线词升级时说明原因。"""
    normalized = normalize_level(level)
    blob = "%s %s" % (reason or "", note or "")
    for word in DANGER_WORDS:
        if word in blob:
            return "danger", "文案命中红线词「%s」，拒绝执行" % word
    if normalized == "unknown" and (level or "").strip() and (level or "").strip().lower() not in BLOCK_LEVELS:
        return "unknown", "无法识别的 safety=%r" % level
    return normalized, None


def require_executable(level, reason, note):
    """可以执行则返回最终 level；否则抛 SafetyRefusal。不在这里点击。"""
    final, detail = assess(level, reason, note)
    if not (reason or "").strip():
        raise SafetyRefusal(final, "tap/swipe 必须写 --reason，说明为什么这下是安全的")
    if final not in SAFE_LEVELS:
        raise SafetyRefusal(final, detail or "safety=%s，默认不点" % final)
    return final
