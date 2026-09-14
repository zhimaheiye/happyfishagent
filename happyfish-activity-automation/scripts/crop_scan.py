# -*- coding: utf-8 -*-
"""从连拍序列里挑出"指定区域最清晰"的帧（用于抓一闪而过的文字水印）。

文字水印是"出现→淡出"，越早越清晰：用区域灰度标准差当清晰度指标排序。

用法:
    python crop_scan.py <dir> <x1> <y1> <x2> <y2> [start] [end] [scale]

输出:
    <dir>/_pick.txt          每帧标准差
    <dir>/pick/top*.png      最清晰的前 N 帧放大图
"""
import os
import sys
from PIL import Image, ImageStat

d = sys.argv[1]
x1, y1, x2, y2 = (int(v) for v in sys.argv[2:6])
start = int(sys.argv[6]) if len(sys.argv) > 6 else 0
end = int(sys.argv[7]) if len(sys.argv) > 7 else 10 ** 9
scale = int(sys.argv[8]) if len(sys.argv) > 8 else 4

pick_dir = os.path.join(d, "pick")
os.makedirs(pick_dir, exist_ok=True)
for f in os.listdir(pick_dir):
    os.remove(os.path.join(pick_dir, f))

files = sorted(f for f in os.listdir(d) if f.startswith("f") and f.endswith(".png"))
rows = []
for f in files:
    i = int(f[1:5])
    if not (start <= i <= end):
        continue
    im = Image.open(os.path.join(d, f)).convert("L").crop((x1, y1, x2, y2))
    sd = ImageStat.Stat(im).stddev[0]
    rows.append((sd, f, im))

rows.sort(reverse=True)
lines = ["%-14s sd=%.3f" % (f, sd) for sd, f, _ in rows]

TOPN = 5
for sd, f, im in rows[:TOPN]:
    big = im.resize((im.width * scale, im.height * scale), Image.LANCZOS)
    big.save(os.path.join(pick_dir, "top_%s" % f))

with open(os.path.join(d, "_pick.txt"), "w", encoding="utf-8") as fp:
    fp.write("\n".join(lines))

print("ok")
