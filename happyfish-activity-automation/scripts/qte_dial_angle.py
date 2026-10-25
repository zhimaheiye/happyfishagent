# -*- coding: utf-8 -*-
"""指针检修 QTE 只读探针：报告表盘指针角度与绿区角度，不点击、不发送游戏输入。

为什么需要它（2026-10-25 实测）：
- 不发任何输入时，连续 screencap 可能拿到同一张旧帧，看起来"指针不动"（假象）。
  本脚本每帧前发一次无害 `input keyevent 0` 唤醒渲染，避免误判机制。
- 指针约 280~390°/s 顺时针旋转，绿区每次点击后重掷，需要实时读数才能判断能否命中。

用法：
  python qte_dial_angle.py --event dudu-rescue [--n 8] [--center 674,382]
输出每帧：时间戳 / 指针角度 / 绿区起止 / 是否落在绿区。
"""
import argparse
import io
import math
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from recorder.device import open_client  # noqa: E402


def grab(adb):
    adb.run("shell", "input", "keyevent", "0")   # 无害按键，仅唤醒渲染
    raw = adb.run("exec-out", "screencap", "-p").stdout
    return Image.open(io.BytesIO(raw)).convert("RGB"), time.time()


def measure(im, cx, cy):
    a = np.asarray(im).astype(int)
    r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    h, w = r.shape
    yy, xx = np.mgrid[0:h, 0:w]
    dist = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    # 奶白色箭头本体（不是金色枢纽；用枢纽质心当圆心会偏出几十度）
    cream = (r > 228) & (g > 218) & (b > 168) & (r - b > 28) & (r - b < 90) & (g - b > 18)
    cream &= (dist > 10) & (dist < 50)
    green = (g > 150) & (g - r > 40) & (g - b > 60) & (dist > 30) & (dist < 62)
    ys, xs = np.nonzero(cream)
    needle = None
    if len(xs) >= 15:
        ang = np.radians(np.degrees(np.arctan2(ys - cy, xs - cx)) % 360)
        vx, vy = np.cos(ang).mean(), np.sin(ang).mean()
        needle = math.degrees(math.atan2(vy, vx)) % 360
    ys, xs = np.nonzero(green)
    span = None
    if len(xs) >= 60:
        angs = np.array([math.degrees(math.atan2(y - cy, x - cx)) % 360 for x, y in zip(xs, ys)])
        hist = np.zeros(360, dtype=int)
        for t in angs:
            for k in (-2, -1, 0, 1, 2):
                hist[int((t + k) % 360)] += 1
        ok = list(hist > max(3, len(xs) * 0.02))
        if all(ok):
            span = (0, 359, 360)
        else:
            start = next(i for i, v in enumerate(ok) if not v)
            seq = ok[start:] + ok[:start]
            run = rs = 0
            best = (0, 0, 0)
            for i, v in enumerate(seq):
                if v:
                    if run == 0:
                        rs = i
                    run += 1
                    if run > best[2]:
                        best = (rs, rs + run - 1, run)
                else:
                    run = 0
            span = ((start + best[0]) % 360, (start + best[1]) % 360, best[2])
    hit = None
    if needle is not None and span:
        a0, a1, n = span
        hit = True if n >= 360 else (a0 <= needle <= a1 if a0 <= a1 else (needle >= a0 or needle <= a1))
    return needle, span, hit


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--event", default="dudu-rescue")
    ap.add_argument("--n", type=int, default=8)
    ap.add_argument("--center", default="674,382", help="表盘中心 720p 坐标，按当前图实测")
    args = ap.parse_args()
    cx, cy = [int(v) for v in args.center.split(",")]
    adb = open_client()
    print("device=%s center=(%d,%d)" % (adb.serial, cx, cy))
    for _ in range(args.n):
        im, ts = grab(adb)
        needle, span, hit = measure(im, cx, cy)
        if span is None:
            print("%.3f not-on-qte (没找到绿色弧: 当前不在“检修中”浮层页, 或圆心坐标不对)" % ts, flush=True)
            continue
        print("%.3f needle=%s green=%s hit=%s" % (
            ts, "None" if needle is None else round(needle, 1), span, hit), flush=True)


if __name__ == "__main__":
    main()
