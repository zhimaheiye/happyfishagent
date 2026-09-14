# -*- coding: utf-8 -*-
"""边走边拍：执行一次滑动的同时连续截图，用来摸清整段走廊走向、判断何时撞墙。

为什么需要：单次「滑一下→截一张」的迭代太慢，一次只能看一个瞬间。
本工具在滑动的同一时间轴里连拍，事后靠帧间差异就能看出「哪一帧起画面不动了 = 撞墙」。

用法:
    python sweep_move.py <x1> <y1> <x2> <y2> <dur_ms> <total_s> [out_dir]

    x1,y1,x2,y2  滑动起止点（设备坐标 1280x720）
    dur_ms       滑动时长（毫秒）
    total_s      连拍总时长（秒），建议 >= dur_ms/1000 + 0.8

输出:
    <out_dir>/f0000.png ...   连续帧
    <out_dir>/_log.txt        帧时间戳 + 每帧与前一帧的平均像素差(MAD)
                              MAD 突然掉到接近 0 → 画面不再滚动 → 大概率撞墙了
"""
import os
import subprocess
import sys
import threading
import time

from PIL import Image, ImageChops, ImageStat

ADB = r"D:\MuMuPlayer\nx_device\15.0\shell\adb.exe"
DEV = "127.0.0.1:7555"
DEFAULT_OUT = r"C:\Users\Administrator\.workbuddy\_vgtmp\sweep"


def shot(idx, out):
    path = os.path.join(out, "f%04d.png" % idx)
    with open(path, "wb") as fp:
        subprocess.run([ADB, "-s", DEV, "exec-out", "screencap", "-p"],
                       stdout=fp, stderr=subprocess.DEVNULL, timeout=40)
    return path


def do_swipe(x1, y1, x2, y2, dur):
    subprocess.run([ADB, "-s", DEV, "shell", "input", "swipe",
                    str(x1), str(y1), str(x2), str(y2), str(dur)],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)


def mad(a, b):
    """两图平均像素差，越小越像。"""
    try:
        ia = Image.open(a).convert("L")
        ib = Image.open(b).convert("L")
        if ia.size != ib.size:
            return -1.0
        d = ImageChops.difference(ia, ib)
        return sum(ImageStat.Stat(d).mean) / 1.0
    except Exception:
        return -1.0


def main():
    x1, y1, x2, y2 = (int(v) for v in sys.argv[1:5])
    dur = int(sys.argv[5])
    total = float(sys.argv[6])
    out = sys.argv[7] if len(sys.argv) > 7 else DEFAULT_OUT
    os.makedirs(out, exist_ok=True)
    for f in os.listdir(out):
        if f.endswith(".png"):
            os.remove(os.path.join(out, f))

    subprocess.run([ADB, "connect", DEV], capture_output=True, timeout=25)

    th = threading.Thread(target=do_swipe, args=(x1, y1, x2, y2, dur))
    t0 = time.time()
    th.start()

    idx = 0
    stamps = []
    while time.time() - t0 < total:
        shot(idx, out)
        stamps.append(time.time() - t0)
        idx += 1
    th.join()

    lines = []
    lines.append("frames=%d total=%.2fs fps=%.2f" % (idx, time.time() - t0, idx / max(0.001, time.time() - t0)))
    lines.append("swipe=(%d,%d)->(%d,%d) dur=%dms" % (x1, y1, x2, y2, dur))
    lines.append("idx  t(s)   MAD(与上一帧)")
    prev = None
    for i in range(idx):
        p = os.path.join(out, "f%04d.png" % i)
        m = mad(prev, p) if prev else -1.0
        lines.append("f%04d  %.2f   %.2f" % (i, stamps[i], m))
        prev = p

    with open(os.path.join(out, "_log.txt"), "w", encoding="utf-8") as fp:
        fp.write("\n".join(lines))
    print("\n".join(lines[:3]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
