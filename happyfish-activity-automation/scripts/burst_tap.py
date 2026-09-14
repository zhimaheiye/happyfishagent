# -*- coding: utf-8 -*-
"""连拍 + 定时点击：捕捉一闪而过的界面文字（如进图瞬间的地图名）。

为什么不用 MCP：MCP 每帧要走一次工具调用往返（秒级），抓不到闪烁内容。
这里直接在本地用 adb exec-out 循环截图，帧率由 adb 客户端启动开销决定（通常 3~8 fps）。

用法:
    python burst_tap.py <x> <y> <tap_at> <total> [out_dir]

    x, y      点击坐标（设备坐标，1280x720）
    tap_at    在第几秒执行点击（例 1.5）
    total     连拍总时长（秒）
    out_dir   输出目录（默认 ASCII 隔离目录，规避 adb 不认中文路径）

流程日志写 <out_dir>/_log.txt（本机 PowerShell 工具的 stdout 捕获不可靠，统一走文件）。
"""
import os
import subprocess
import sys
import time
import shutil

ADB = r"D:\MuMuPlayer\nx_device\15.0\shell\adb.exe"
DEV = "127.0.0.1:7555"
DEFAULT_OUT = r"C:\Users\Administrator\.workbuddy\_vgtmp\burst"

LOG = []


def log(msg):
    LOG.append(str(msg))
    print(msg)


def shot(idx, out):
    path = os.path.join(out, "f%04d.png" % idx)
    with open(path, "wb") as fp:
        subprocess.run([ADB, "-s", DEV, "exec-out", "screencap", "-p"],
                       stdout=fp, stderr=subprocess.DEVNULL, timeout=40)
    return path


def main():
    x = int(sys.argv[1])
    y = int(sys.argv[2])
    tap_at = float(sys.argv[3])
    total = float(sys.argv[4])
    out = sys.argv[5] if len(sys.argv) > 5 else DEFAULT_OUT
    os.makedirs(out, exist_ok=True)
    for f in os.listdir(out):
        if f.endswith(".png"):
            os.remove(os.path.join(out, f))

    subprocess.run([ADB, "connect", DEV], capture_output=True, timeout=25)

    t0 = time.time()
    idx = 0
    tapped = False
    tap_frame = None
    tap_time = None

    while True:
        now = time.time() - t0
        if now >= total:
            break
        if not tapped and now >= tap_at:
            subprocess.run([ADB, "-s", DEV, "shell", "input", "tap", str(x), str(y)],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=25)
            tapped = True
            tap_frame = idx
            tap_time = now
        shot(idx, out)
        idx += 1

    dt = time.time() - t0
    log("frames=%d elapsed=%.2fs fps=%.2f" % (idx, dt, (idx / dt) if dt else 0))
    log("tap at %.2fs -> next frame f%04d.png" % (tap_time or -1, tap_frame or -1))
    log("OUT=%s" % out)

    with open(os.path.join(out, "_log.txt"), "w", encoding="utf-8") as fp:
        fp.write("\n".join(LOG))

    # 同时把帧复制一份到会话可读的临时目录，方便直接 Read
    return 0


if __name__ == "__main__":
    sys.exit(main())
