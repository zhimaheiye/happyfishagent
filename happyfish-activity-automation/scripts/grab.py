"""adb 截图助手（开心水族箱活动自动化专用）

用途：连接 MuMu 模拟器 -> screencap -> pull 到 ASCII 隔离目录。
     规避「adb 不认中文路径」和「daemon 重启丢连接」两个坑（connect 与操作写在同一进程里）。

用法：
  python grab.py                          # 截全屏 -> _vgtmp/shot.png
  python grab.py g1.png                   # 指定文件名
  python grab.py g1.png 270 95 700 480    # 截图并裁剪（放大交给 zoom.py）

adb 路径可用环境变量覆盖：ADB_PATH / ADB_DEV
"""
import os
import subprocess
import sys

ADB = os.environ.get("ADB_PATH", r"D:\MuMuPlayer\nx_device\15.0\shell\adb.exe")
DEV = os.environ.get("ADB_DEV", "127.0.0.1:7555")
TMP = os.environ.get("VGTMP", r"C:\Users\Administrator\.workbuddy\_vgtmp")


def adb(*args):
    """执行 adb 命令，返回 CompletedProcess。"""
    return subprocess.run([ADB, *args], capture_output=True, text=True)


def grab(name="shot.png"):
    """截图并 pull 到隔离目录，返回本地路径。"""
    os.makedirs(TMP, exist_ok=True)
    out = os.path.join(TMP, name)
    adb("connect", DEV)                                   # 必须与后续操作同进程
    adb("-s", DEV, "shell", "screencap -p /sdcard/_s.png")
    adb("-s", DEV, "pull", "/sdcard/_s.png", out)
    return out


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else "shot.png"
    out = grab(name)
    print("saved", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
