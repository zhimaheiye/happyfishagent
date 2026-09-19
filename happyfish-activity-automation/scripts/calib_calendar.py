#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""日历类棋盘（浪漫满屋·约会日历）网格标定 —— 输出 4 行中心 + 逐行「哪几列有内容」自校验。

⚠️ 历史更正（2026-09-19）：旧版「找最靠上的蓝色像素 = 第 1 行卡顶，再往下推 114」是**错的**。
   理由：**第 1 行可能是全空的**（这局开局就是），此时最靠上的蓝色属于第 2 行 →
   整组行坐标下移一行，还会多推出一行落到日历面板外（实测输出 294/408/522/**636**，
   其中 636 已经在底部按钮区）。这个错根源就是文档里已推翻的「行会漂 13px」
   —— 那组 168/284/400/516 正是同一个错误方法算出来的，**行其实是固定的**。
   → 现在改成：**优先用固定锚点（与 count_empty.py 同一份网格），再用像素证据校验**，
     发现对不上时**大声报警**，绝不静默给一组看着像样的错坐标。

网格事实（多帧实测）：
  - 列中心（很稳）：298 / 427 / 543 / 659 / 775 / 891 / 1007（间距 116）
  - 行中心（固定）：182 / 296 / 410 / 524（行高 114，卡片顶到行中心 ≈55）
  - 格号换算：n = (r-1)*7 + c，即 1–7 / 8–14 / 15–21 / 22–28

用法：
    python calib_calendar.py shot.png                 # 打印网格 + 逐行有内容的列
    python calib_calendar.py shot.png --grid "298,427,543,659,775,891,1007|182,296,410,524"
    python calib_calendar.py shot.png --out coords.json
"""
import argparse
import json
import sys

import numpy as np
from PIL import Image

DEFAULT_COLS = [298, 427, 543, 659, 775, 891, 1007]
DEFAULT_ROWS = [182, 296, 410, 524]

# 判「这格有内容」：与 count_empty.py 同一口径（⚠️ 不能按"是不是蓝色"判——
# **空格本身就是浅蓝色卡面**，只带一个淡粉日期数字；09-19 实测那套判据会误判）。
# 口径：格心 60×60 里「高饱和像素占比」与「暗像素占比」——空格实测 hs=0.000，非空 hs>=0.201
PATCH_HALF = 30
HS_EMPTY_MAX = 0.12
DK_EMPTY_MAX = 0.22
BLUE_MIN = 216
BLUE_GAP = 8


def cell_filled(im, x, y):
    """格中心 60×60 是否有内容（元素图标或锁格）。"""
    box = (max(0, x - PATCH_HALF), max(0, y - PATCH_HALF),
           x + PATCH_HALF, y + PATCH_HALF)
    a = np.asarray(im.crop(box).convert("RGB")).astype(np.float32) / 255.0
    mx, mn = a.max(axis=2), a.min(axis=2)
    sat = np.where(mx > 1e-6, (mx - mn) / np.maximum(mx, 1e-6), 0.0)
    hs = float(((sat > 0.45) & (mx > 0.35)).mean())
    dk = float((mx < 0.32).mean())
    return not (hs <= HS_EMPTY_MAX and dk <= DK_EMPTY_MAX)


def topmost_blue_top(a, cols, y_from=105, y_to=600, min_run=25):
    """（仅供交叉验证）最靠上的「蓝色卡底」起点 y，以及它落在哪一列。"""
    best = None
    for x in cols:
        col = a[y_from:y_to, x]
        blue = (col[:, 2] > BLUE_MIN) & (col[:, 2] > col[:, 0] + BLUE_GAP)
        ys = np.nonzero(blue)[0]
        if len(ys) == 0:
            continue
        run = 0
        for v in blue[ys[0]:]:
            if v:
                run += 1
            else:
                break
        if run >= min_run:
            t = y_from + int(ys[0])
            if best is None or t < best[0]:
                best = (t, x)
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("image")
    ap.add_argument("--grid", help='覆盖网格："x1,x2,..|y1,y2,.."')
    ap.add_argument("--out", help="把结果写成 JSON")
    args = ap.parse_args()

    im = Image.open(args.image).convert("RGB")
    a = np.array(im).astype(int)
    if im.size != (1280, 720):
        print("⚠️ 图片尺寸 %s，本脚本按 1280×720 校准，结果可能不准" % (im.size,), file=sys.stderr)

    cols, rows = list(DEFAULT_COLS), list(DEFAULT_ROWS)
    if args.grid:
        cs, rs = args.grid.split("|")
        cols = [int(v) for v in cs.split(",")]
        rows = [int(v) for v in rs.split(",")]

    print("# %s" % args.image)
    print("列中心 : %s   (锚点%s)" % (cols, "·自定义" if args.grid else ""))
    print("行中心 : %s   (锚点%s)" % (rows, "·自定义" if args.grid else ""))

    # 逐行：有多少列是「有内容」的，并列出格号
    for ri, y in enumerate(rows, 1):
        hit = [ci for ci, x in enumerate(cols, 1) if cell_filled(im, x, y)]
        nums = [(ri - 1) * 7 + ci for ci in hit]
        print("  第 %d 行 (y=%d)：有内容 %d/7 列%s"
              % (ri, y, len(hit), (" → 格 %s" % nums) if hit else " → 全空"))

    # 交叉验证：最靠上的蓝卡顶应该落在某一行中心 - 55 附近
    tb = topmost_blue_top(a, cols)
    if tb:
        t, x = tb
        nearest = min(rows, key=lambda y: abs((y - 55) - t))
        delta = t - (nearest - 55)
        print("交叉验证：最靠上的蓝卡顶 y=%d (x=%d) → 最近的行是 y=%d（卡片顶应为 %d，差 %+dpx）"
              % (t, x, nearest, nearest - 55, delta))
        if abs(delta) > 20:
            print("⚠️ 偏差 >20px：网格锚点可能对不上这帧，请人工核对后再动手！", file=sys.stderr)
    else:
        print("交叉验证：这一帧没扫到蓝色卡底（盘面无卡片？）")

    if args.out:
        json.dump({"cols": cols, "rows": rows},
                  open(args.out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print("-> %s" % args.out)


if __name__ == "__main__":
    main()
