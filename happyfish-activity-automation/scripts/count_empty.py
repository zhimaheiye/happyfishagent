#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""浪漫满屋 · 盘面状态扫描：数出空格数 E（本局最稀缺的资源）。

为什么需要它：
    技能文档第四节第 9 条（空格预算管理）要求**每轮开局先数空格数 E**。
    盘面元素不可拖动 → 空格不可再生 → E 就是这局的"命"。
    09-17 靠目测数格既慢又容易错 → 做成工具。

用法：
    python scripts/count_empty.py 截图.png
    python scripts/count_empty.py 截图.png --pool 2      # 已知卡池张数 → 自动判预警线
    python scripts/count_empty.py 截图.png --debug       # 附每格原始指标

输出：
    E = 空格数 + 空格格号清单 + 每个空格的 4 邻格号（堆产区前先看这个）
    带 --pool 时给出 🚨 预警：E <= 卡池张数 + 1 → 进入「空格保卫战」
        （此后只允许两种落法：零成本清池 / 能当场推进产区，见技能文档第四节第 9 条）

判定口径（09-17 校准，1280×720 截图）：
    - 空格：浅底 + 只有粉色日期数字 → 高饱和像素极少（实测 hs = 0.000）
    - 非空：卡片（元素图标色浓）**或锁格**（🔒 锁头本身是高饱和亮蓝，实测 hs≈0.48~0.55）
    ⚠️ 本工具**不区分"卡片"和"锁格"** —— 二者都拒收卡片，对"能不能落卡"是等价的，
       所以归为同一类不影响 E 的正确性。锁格仍需靠肉眼看图确认位置。
"""

import sys
from PIL import Image
import numpy as np

# ---- 网格（09-17 脚本实测 + 技能文档第五节）----
COLS = [298, 427, 543, 659, 775, 891, 1007]
ROWS = [182, 296, 410, 524]
HALF = 30            # 取格心 60×60；格间距 116×114，留足边距不碰格线

# 阈值（09-17 校准：空格 hs 恒为 0.000，非空的 hs 最低 0.201）
HS_EMPTY_MAX = 0.12
DK_EMPTY_MAX = 0.22


def cell_box(idx):
    """idx: 1-28 → 返回裁剪框 (left, top, right, bottom)"""
    r = (idx - 1) // 7 + 1
    c = (idx - 1) % 7 + 1
    x, y = COLS[c - 1], ROWS[r - 1]
    return (x - HALF, y - HALF, x + HALF, y + HALF)


def metrics(img, box):
    a = np.asarray(img.crop(box).convert("RGB")).astype(np.float32) / 255.0
    mx = a.max(axis=2)
    mn = a.min(axis=2)
    sat = np.where(mx > 1e-6, (mx - mn) / np.maximum(mx, 1e-6), 0.0)
    val = mx
    high_sat = float(((sat > 0.45) & (val > 0.35)).mean())
    dark = float((val < 0.32).mean())
    return high_sat, dark


def classify(hs, dk):
    """→ 'empty' / 'filled'（含锁格）"""
    if hs <= HS_EMPTY_MAX and dk <= DK_EMPTY_MAX:
        return "empty"
    return "filled"


def neighbours(n):
    """格的 4 邻格号"""
    r = (n - 1) // 7 + 1
    c = (n - 1) % 7 + 1
    out = []
    if r > 1:
        out.append(n - 7)
    if r < 4:
        out.append(n + 7)
    if c > 1:
        out.append(n - 1)
    if c < 7:
        out.append(n + 1)
    return out


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    args = sys.argv[1:]
    path = args[0]
    debug = "--debug" in args
    pool = None
    if "--pool" in args:
        i = args.index("--pool")
        pool = int(args[i + 1])

    img = Image.open(path)
    if img.size != (1280, 720):
        img = img.resize((1280, 720))

    rows = []
    for idx in range(1, 29):
        hs, dk = metrics(img, cell_box(idx))
        rows.append((idx, classify(hs, dk), hs, dk))

    empties = [r[0] for r in rows if r[1] == "empty"]
    filled = [r[0] for r in rows if r[1] == "filled"]

    print("图: %s" % path)
    print("空格 E = %d   %s" % (len(empties), empties))
    print("非空   = %d" % len(filled))

    print("\n空格明细（列出 4 邻格号，堆产区/选落点前先看）:")
    for n in empties:
        print("  c%-2d  4邻: %s" % (n, " ".join("c%d" % k for k in neighbours(n))))

    if pool is not None:
        print("\n卡池 C = %d，空格 E = %d" % (pool, len(empties)))
        if len(empties) <= pool + 1:
            print("🚨 【空格保卫战】E <= C+1 —— 此后只允许两种落法：")
            print("   1) 零成本清池（落点格元素全被邻格吸走 → 还原空白，E 不减）")
            print("   2) 能当场推进产区（邻格已有 3~4 个同色 → 成大日程 → 大概率被需求收走 → 反而 +1）")
            print("   🚫 红线：绝不为了清空卡池把废卡塞进空格（E 永久 -1）")
        else:
            print("✅ 空格尚宽裕（E > C+1）")

    if debug:
        print("\n--- debug: idx / verdict / high_sat / dark ---")
        for idx, v, hs, dk in rows:
            print("  c%-2d %-7s hs=%.3f dk=%.3f" % (idx, v, hs, dk))
    return 0


if __name__ == "__main__":
    sys.exit(main())
