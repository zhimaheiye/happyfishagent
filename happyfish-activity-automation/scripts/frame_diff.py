# -*- coding: utf-8 -*-
"""帧差分析：定位连拍序列里的界面变化点（找"一闪而过"的内容）。

输出 <dir>/_diff.txt：序号 / 文件名 / 与前一帧的平均像素差（0~255）。
差值大的位置 = 界面在变（动画、切屏、闪现文字）。
"""
import os
import sys
from PIL import Image, ImageChops

d = sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\Administrator\.workbuddy\_vgtmp\burst"
files = sorted(f for f in os.listdir(d) if f.startswith("f") and f.endswith(".png"))

CT = (64, 36)
lines = []
prev = None
for i, f in enumerate(files):
    im = Image.open(os.path.join(d, f)).convert("L").resize(CT)
    if prev is not None:
        diff = ImageChops.difference(im, prev)
        data = diff.getdata()
        s = sum(data) / float(CT[0] * CT[1])
        bar = "#" * int(min(s, 60))
        lines.append("%3d %s %7.2f %s" % (i, f, s, bar))
    prev = im

with open(os.path.join(d, "_diff.txt"), "w", encoding="utf-8") as fp:
    fp.write("frames=%d\n" % len(files))
    fp.write("\n".join(lines))
print("ok")
