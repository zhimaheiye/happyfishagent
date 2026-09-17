#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""日历类棋盘（浪漫满屋·约会日历）网格自动标定 —— 只求「行」，列用锚点。

为什么需要它（2026-09-17 血泪）：
  - **列很稳**（4 张截图实测都是 298/427/543/659/775/891/1007，±3px）。
  - **行会漂**：同一活动同一界面，两张截图的行中心实测差 **13px**
    （168/284/400/516 vs 181/296/410/524）→ 跨帧沿用坐标必错。
  - 目测行中心同样偏十几像素，足以让拖拽落在格子外沿。
  -> 规矩：**每帧重标行。** 这个脚本 2 秒出结果。

原理（纯像素扫描，不猜）：
  在**列中心**上扫「蓝色卡底」的纵向连通段，合并被图标打断的缺口，得到 4 个行区间。
  ⚠️ 不能用全宽投影：行间缝隙只有几像素，投影会把 4 行糊成一段。

用法：
    python calib_calendar.py shot.png
    python calib_calendar.py shot.png --out coords.json
    python calib_calendar.py shot.png --cols 298,427,543,659,775,891,1007
"""
import argparse
import json
import sys

import numpy as np
from PIL import Image

# 列中心实测锚点（1280×720 MuMu，多帧稳定）
DEFAULT_COLS = [298, 427, 543, 659, 775, 891, 1007]


# 卡片几何（1280×720 实测）：行高 114；卡片顶到行中心约 55
PITCH = 114
HALF = 55


def find_rows(a, cols, y_from=105, y_to=600, expect=4,
              blue_min=216, blue_gap=8, min_run=25):
    """求出 4 个行中心。

    做法：逐列找「蓝色卡底」最靠上的像素 = 第一行卡片顶（任一行 1 有卡的列都行），
    再按固定行高 PITCH 往下推。
    ⚠️ 不能按"连通段"切：**行与行之间的缝隙只有约 5px**，比卡片内被图标打断的
    缺口（~30px）还小，任何 gap 合并都会把 4 行糊成 1 段。
    """
    tops, used = [], []
    for x in cols:
        col = a[y_from:y_to, x]
        blue = (col[:, 2] > blue_min) & (col[:, 2] > col[:, 0] + blue_gap)
        ys = np.nonzero(blue)[0]
        if len(ys) == 0:
            continue
        # 要求首个蓝像素之后有一段像样的连续蓝（>= min_run），排除零星噪点
        run = 0
        for v in blue[ys[0]:]:
            if v:
                run += 1
            else:
                break
        if run >= min_run:
            tops.append(y_from + int(ys[0]))
            used.append(x)
    if not tops:
        return [], None

    top = min(tops)
    rows = [top + HALF + PITCH * k for k in range(expect)]
    return rows, f"顶={top} (列 {[used[i] for i, t in enumerate(tops) if t == top]})"


def check_columns(a, cols, y=105, tol=18):
    """在表头一带扫白线，校验列锚点是否还对得上。"""
    row = a[y]
    white = (row[:, 0] > 236) & (row[:, 1] > 236) & (row[:, 2] > 236)
    lines, s = [], None
    for x in range(150, 1080):
        if white[x] and s is None:
            s = x
        elif not white[x] and s is not None:
            if x - s <= 6:
                lines.append((s + x - 1) // 2)
            s = None
    bad = [c for c in cols if not any(abs(c - l) <= tol for l in lines)]
    return lines, bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("image")
    ap.add_argument("--cols", help="逗号分隔的列中心 x，覆盖默认锚点")
    ap.add_argument("--out", help="把结果写成 JSON")
    args = ap.parse_args()

    im = Image.open(args.image).convert("RGB")
    a = np.array(im).astype(int)
    if im.size != (1280, 720):
        print(f"⚠️ 图片尺寸 {im.size}，本脚本按 1280×720 校准，结果可能不准", file=sys.stderr)

    cols = ([int(v) for v in args.cols.split(",")] if args.cols else DEFAULT_COLS)
    rows, used_x = find_rows(a, cols)

    print(f"# {args.image}")
    print(f"列中心 : {cols}   (锚点{'·自定义' if args.cols else ''})")
    print(f"行中心 : {rows}" + (f"   (取自 x={used_x})" if used_x else ""))
    if len(rows) >= 2:
        print(f"行间距 : {[rows[i + 1] - rows[i] for i in range(len(rows) - 1)]}")

    if len(rows) != 4:
        print(f"⚠️ 只找到 {len(rows)} 行（应为 4）—— 可能界面不在日历小游戏页，或该帧布局特殊，请人工核对",
              file=sys.stderr)
    lines, bad = check_columns(a, cols)
    if bad:
        print(f"⚠️ 这些列锚点在 y=105 上没有对应的白色分隔线：{bad}", file=sys.stderr)
        print(f"   实测白线：{lines}", file=sys.stderr)

    if args.out:
        json.dump({"cols": cols, "rows": rows},
                  open(args.out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print(f"-> {args.out}")


if __name__ == "__main__":
    main()
