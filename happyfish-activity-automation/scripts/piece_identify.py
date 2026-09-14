# -*- coding: utf-8 -*-
"""棋盘拼块识别（跨活动通用）。

给定一张棋盘截图 + 格子坐标 + 每块拼图的模板图，
逐格判出「空格」还是「哪一块」，输出棋盘地图。

模板目录里每个 png 的文件名就是该拼块的名字（不含扩展名）。
模板图尺寸需与 --cell 一致（默认 138）。

用法:
  python piece_identify.py shot.png --tpl-dir D:/tpl \
      --xs 431,570,709,847 --ys 150,288,427,565 --cell 138
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

INSET = 10          # 去掉格子四周的格线/描边后再比对
EMPTY_SAT = 30      # 饱和度低于此值 + 匹配差大 => 判为空灰格
MATCH_OK = 30       # 匹配差低于此值 => 认作该拼块


def load_templates(d, cell, inset=INSET):
    tpl = {}
    for f in sorted(os.listdir(d)):
        if not f.lower().endswith(".png"):
            continue
        nm = os.path.splitext(f)[0]
        im = np.asarray(Image.open(os.path.join(d, f)).convert("RGB")).astype(float)
        if im.shape[0] != cell or im.shape[1] != cell:
            im = np.asarray(
                Image.fromarray(im.astype(np.uint8)).resize((cell, cell), Image.LANCZOS)
            ).astype(float)
        tpl[nm] = im[inset:cell - inset, inset:cell - inset]
    return tpl


def identify(shot, tpl_dir, xs, ys, cell=138, inset=INSET):
    arr = np.asarray(Image.open(shot).convert("RGB")).astype(float)
    tpl = load_templates(tpl_dir, cell, inset)
    nr, nc = len(ys), len(xs)
    grid, detail = [], []
    for r in range(nr):
        row = []
        for c in range(nc):
            x0 = int(xs[c] - cell / 2)
            y0 = int(ys[r] - cell / 2)
            cel = arr[y0 + inset:y0 + cell - inset, x0 + inset:x0 + cell - inset]
            sat = float((cel.max(axis=2) - cel.min(axis=2)).mean())
            best, bn = 1e9, "-"
            for nm, t in tpl.items():
                h = min(cel.shape[0], t.shape[0])
                w = min(cel.shape[1], t.shape[1])
                d = float(np.abs(cel[:h, :w] - t[:h, :w]).mean())
                if d < best:
                    best, bn = d, nm
            if best > MATCH_OK and sat < EMPTY_SAT:
                row.append(".")
                detail.append("r%dc%d 空位" % (r + 1, c + 1))
            else:
                tag = bn if best <= MATCH_OK else bn + "?"
                row.append(tag)
                detail.append("r%dc%d %s diff=%.1f sat=%.0f" % (r + 1, c + 1, bn, best, sat))
        grid.append(row)

    width = max([len(x) for row in grid for x in row] + [1])
    print("棋盘 %dx%d  cell=%d" % (nr, nc, cell))
    print("模板: %s" % list(tpl.keys()))
    print()
    for row in grid:
        print("  ".join(x.ljust(width) for x in row))
    print()
    for d in detail:
        print(" ", d)
    return grid


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("shot")
    ap.add_argument("--tpl-dir", required=True)
    ap.add_argument("--xs", required=True, help="列中心 x，逗号分隔")
    ap.add_argument("--ys", required=True, help="行中心 y，逗号分隔")
    ap.add_argument("--cell", type=int, default=138)
    a = ap.parse_args()
    identify(a.shot, a.tpl_dir,
             [float(v) for v in a.xs.split(",")],
             [float(v) for v in a.ys.split(",")],
             a.cell)


if __name__ == "__main__":
    sys.exit(main())
