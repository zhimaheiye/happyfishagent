# -*- coding: utf-8 -*-
"""检测浪漫满屋右侧卡池中「卡片主体」（饱和天蓝 r<165,b>225,g-r>40）的位置。
用法: python detect_pool.py s2.png
输出每张卡片的 y 区间与图标中心估算（取卡片上 40% 高度处）。
"""
import sys
from PIL import Image

path = sys.argv[1]
im = Image.open(path).convert("RGB")
W, H = im.size
px = im.load()

X0, X1 = 1085, 1272
Y0, Y1 = 80, 560

def is_card(p):
    r, g, b = p
    return r < 165 and b > 225 and (g - r) > 40

rows = []
for y in range(Y0, Y1):
    cnt = sum(1 for x in range(X0, X1, 2) if is_card(px[x, y]))
    rows.append((y, cnt))

runs = []
cur = None
for y, c in rows:
    if c >= 8:
        if cur is None:
            cur = [y, y]
        cur[1] = y
    else:
        if cur is not None:
            if cur[1] - cur[0] >= 20:
                runs.append(tuple(cur))
            cur = None
if cur is not None and cur[1] - cur[0] >= 20:
    runs.append(tuple(cur))

print("%s  size=%dx%d  卡片数=%d" % (path, W, H, len(runs)))
for a, b in runs:
    # x 范围取卡片中部
    cy = (a + b) // 2
    xs = [x for x in range(X0, X1) if is_card(px[x, cy])]
    xa, xb = (min(xs), max(xs)) if xs else (0, 0)
    # 图标区：卡片顶部 15%~55%
    iy = a + int((b - a) * 0.30)
    print("  卡片 y %4d..%4d (h=%3d)  x %4d..%4d  圆心≈(%d,%d)  图标带y自%d起"
          % (a, b, b - a, xa, xb, (xa + xb) // 2, cy, iy))
