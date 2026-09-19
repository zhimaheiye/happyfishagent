# -*- coding: utf-8 -*-
"""检测浪漫满屋右侧卡池中「卡片主体」（饱和天蓝 r<165,b>225,g-r>40）的位置。

用法: python detect_pool.py s2.png

输出：卡片数 + 每张卡的 y 区间 / x 区间 / 卡片顶。

⚠️⚠️ 两个已修正的坑（2026-09-19）：
  1. **假阳性**：卡池顶部有一条 ~20px 高的蓝色装饰带，旧版阈值 `h>=20` 会把它算成一张卡
     → 「卡片数」+1。而**卡片张数是判「拖拽有没有生效」的第一手证据**（技能第三节第 1 条），
     张数错了会把「拖拽成功」误判成失败（或反过来）。→ 现在要求 `h>=40 且 x跨度>=90`。
  2. **旧版打印的「图标中心估算」是错的**：它按 `卡片顶 + 卡高*30%` 算，但实测**图标会凸出到卡片顶之上**
     （如卡片主体 y160..230，图标中心却在 y≈141~143）→ 拿这个坐标去拖拽，起点会落在卡片上沿之外。
     → 现在**不再给图标坐标**，只给卡片 y 区间；图标中心**必须裁图放大实测**（zoom.py，4×）。
       经验值：图标中心 ≈ 卡片主体顶部 **-15 ~ +45px** 区间内，一张卡 1~3 个图标。
"""
import sys
from PIL import Image

MIN_H = 40          # 卡片主体最小高度（真卡 ≥69；顶部装饰带只有 ~20）
MIN_W = 90          # 卡片主体最小 x 跨度（真卡 ≥148）

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
            runs.append(tuple(cur))
            cur = None
if cur is not None:
    runs.append(tuple(cur))

cards = []
for a, b in runs:
    cy = (a + b) // 2
    xs = [x for x in range(X0, X1) if is_card(px[x, cy])]
    xa, xb = (min(xs), max(xs)) if xs else (0, 0)
    if (b - a) >= MIN_H and (xb - xa) >= MIN_W:
        cards.append((a, b, xa, xb))

print("%s  size=%dx%d  卡片数=%d" % (path, W, H, len(cards)))
for a, b, xa, xb in cards:
    print("  卡片 主体y %4d..%4d (h=%3d)  x %4d..%4d  顶=%d"
          % (a, b, b - a, xa, xb, a))
print("⚠️ 图标中心请用 zoom.py 4× 裁图实测（图标会凸出卡片顶之上），别用「卡高百分比」推。")
