# -*- coding: utf-8 -*-
"""酿月食香 - 资源消费门禁检查（第一版，二态）。

职责：对消耗型入口动作做授权判定。默认 permission=false（禁止）。
授权入口：CLI --allow-resource activity_stamina（一次性传入）或编辑 metadata.json permissions。
用法：
  python gate_check.py                       # 输出各资源默认状态（应全部 DENIED）
  python gate_check.py --allow-resource activity_stamina   # 模拟已授权
输出 GATE_DENIED / GATE_ALLOWED，供零消耗实机验证用。
"""
from pathlib import Path
import json
import sys

META = Path(__file__).resolve().parent / "metadata.json"


def main():
    meta = json.loads(META.read_text(encoding="utf-8"))
    perms = dict(meta["permissions"])
    allow = set()
    if "--allow-resource" in sys.argv:
        i = sys.argv.index("--allow-resource")
        allow.update(sys.argv[i + 1].split(","))
    verdicts = []
    for name, default in perms.items():
        if name == "note":
            continue
        granted = default is True or name in allow
        verdicts.append((name, granted))
    for name, granted in verdicts:
        print("[%s] %s -> %s" % ("GATE_ALLOWED" if granted else "GATE_DENIED", name,
                                 "(默认禁止)" if not granted else "(已授权)"))
    any_allowed = any(g for _, g in verdicts)
    print("GATE_%s" % ("ALLOWED" if any_allowed else "DENIED"))
    sys.exit(0 if any_allowed else 1)


if __name__ == "__main__":
    main()
