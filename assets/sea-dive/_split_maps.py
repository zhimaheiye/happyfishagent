# -*- coding: utf-8 -*-
"""把博主攻略拼图（3列x2行）切成单张地图，输出到 maps/。

布局：左上/中上/右上/左下/中下 = 5 张地图，右下 = 封面（跳过）。
输出做 2 倍放大，便于人工对照路线细节。
"""
import os
from PIL import Image

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "maps")
os.makedirs(OUT, exist_ok=True)

# 每张拼图 -> 5 个地图名（按 左上/中上/右上/左下/中下 顺序）
LAYOUT = {
    "攻略原图-100-200.png": ("100-200", ["初始之地", "弹弹乐", "海草海", "海胆之家", "心海"]),
    "攻略原图-200-300.jpg": ("200-300", ["冰天雪地", "层层海", "电电之谷", "星光点点", "摇篮"]),
    "攻略原图-300-400.png": ("300-400", ["刻型之路", "气泡海", "熔岩谷", "小迷宫", "灼热之海"]),
    "攻略原图-400-500.png": ("400-500", ["博雅台", "玲珑灯", "六角亭", "平衡之塔", "曲折之径"]),
}

CELL_POS = [(0, 0), (1, 0), (2, 0), (0, 1), (1, 1)]
SCALE = 2

for fname, (band, names) in LAYOUT.items():
    path = os.path.join(BASE, fname)
    if not os.path.exists(path):
        print("MISSING:", path)
        continue
    im = Image.open(path).convert("RGB")
    W, H = im.size
    cw, ch = W / 3.0, H / 2.0
    for (c, r), nm in zip(CELL_POS, names):
        box = (int(round(c * cw)), int(round(r * ch)),
               int(round((c + 1) * cw)), int(round((r + 1) * ch)))
        tile = im.crop(box)
        tile = tile.resize((tile.width * SCALE, tile.height * SCALE), Image.LANCZOS)
        tile.save(os.path.join(OUT, "%s_%s.png" % (band, nm)))
    print("split:", fname, im.size)

print("done")
