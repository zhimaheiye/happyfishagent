#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""浪漫满屋日历棋盘：格号 ↔ 坐标换算 + 4 邻格（**禁止心算**）。

为什么要它（2026-09-19 实测事故）：
  我把卡往「c2」拖，心里算出 `(427,296)` —— 实际那是 **c9**；c2 是 `(427,182)`。
  后果：落到**非空格** → 卡片原路弹回、卡池张数不变、全盘零变化，
  看起来和「拖拽通道坏了」一模一样（文档第三节第 1 条 / 第六节的血泪）。
  规律危险点：**n = (r-1)*7 + c**，所以「第二列」在第 1 行是 c2、在第 2 行是 c9，
  心算时极易把 col 当 row 用。→ 一律用本脚本，别在脑子里换算。

用法：
    python cell_xy.py 2            # 单格
    python cell_xy.py 2 13 19      # 多格
    python cell_xy.py --col 2      # 整列（col 2 → c2/c9/c16/c23）
    python cell_xy.py --table      # 打印 4×7 全表（含坐标与邻格）
"""
import sys

COLS = [298, 427, 543, 659, 775, 891, 1007].copy()
ROWS = [182, 296, 410, 524]


def rc(n):
    return (n - 1) // 7 + 1, (n - 1) % 7 + 1


def xy(n):
    r, c = rc(n)
    return COLS[c - 1], ROWS[r - 1]


def nbrs(n):
    r, c = rc(n)
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


def show(n):
    r, c = rc(n)
    x, y = xy(n)
    print("c%-2d → r%d,c%d  (x,y) = (%d,%d)   4邻: %s"
          % (n, r, c, x, y, " ".join("c%d" % k for k in nbrs(n))))


def main():
    a = sys.argv[1:]
    if not a or a[0] in ("-h", "--help"):
        print(__doc__)
        return
    if a[0] == "--table":
        for r in range(1, 5):
            for c in range(1, 8):
                n = (r - 1) * 7 + c
                print("c%-2d (%4d,%3d)" % (n, COLS[c - 1], ROWS[r - 1]), end="   ")
            print()
        return
    if a[0] == "--col":
        c = int(a[1])
        for r in range(1, 5):
            show((r - 1) * 7 + c)
        return
    for v in a:
        show(int(v))


if __name__ == "__main__":
    main()
