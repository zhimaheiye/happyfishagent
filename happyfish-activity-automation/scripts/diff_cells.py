# -*- coding: utf-8 -*-
"""比较两张截图，按 28 格报告平均色差，找出变化的格。
用法: python diff_cells.py a.png b.png
"""
import sys
from PIL import Image

a = Image.open(sys.argv[1]).convert("RGB")
b = Image.open(sys.argv[2]).convert("RGB")
pa, pb = a.load(), b.load()

c = [301, 427, 544, 660, 777, 893, 1009]
r = [182, 297, 409, 521]
HALF = 34

res = []
for ri, cy in enumerate(r, 1):
    for ci, cx in enumerate(c, 1):
        n = (ri - 1) * 7 + ci
        tot = 0
        cnt = 0
        for y in range(cy - HALF, cy + HALF, 3):
            for x in range(cx - HALF, cx + HALF, 3):
                ra, ga, ba = pa[x, y]
                rb, gb, bb = pb[x, y]
                tot += abs(ra - rb) + abs(ga - gb) + abs(ba - bb)
                cnt += 1
        res.append((tot / cnt / 3.0, n))

res.sort(reverse=True)
print("%s -> %s" % (sys.argv[1], sys.argv[2]))
print("变化最大的格：")
for d, n in res[:12]:
    print("  %2d 号格   平均色差 %.1f" % (n, d))
print("未变化的格（色差<2）：", [n for d, n in res if d < 2])
