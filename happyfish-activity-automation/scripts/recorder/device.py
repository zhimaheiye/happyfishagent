# -*- coding: utf-8 -*-
"""解析 adb 设备。不把某一个历史实例端口写死成默认值。

顺序：
  1. 环境变量 HAPPYFISH_ADB_DEV，其次 ADB_DEV（仅当进程环境里真的设置了）
  2. 项目已有的 tools/mumu_dev.py:pick_device（由 MuMuManager 报端口）
  3. 当前 `adb devices` 里唯一的在线设备

多台在线且没有环境变量、也没有 mumu_dev 时直接失败，禁止猜第一台。
"""
import importlib.util
import os
import re
import shutil
import subprocess
from pathlib import Path


class DeviceError(RuntimeError):
    pass


def _workspace_mumu_path():
    # recorder/device.py -> scripts -> happyfish-activity-automation -> happyfishagent -> 工作区
    here = Path(__file__).resolve()
    candidates = []
    env = os.environ.get("HAPPYFISH_MUMU_DEV")
    if env:
        candidates.append(Path(env))
    candidates.append(here.parents[4] / "tools" / "mumu_dev.py")
    for path in candidates:
        if path.is_file():
            return path
    return None


def load_mumu_dev():
    path = _workspace_mumu_path()
    if path is None:
        return None
    spec = importlib.util.spec_from_file_location("mumu_dev", str(path))
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def resolve_adb_path(environ=None, mumu=None):
    environ = os.environ if environ is None else environ
    env = environ.get("ADB_PATH")
    if env:
        return env
    if mumu is None:
        try:
            mumu = load_mumu_dev()
        except Exception:
            mumu = None
    if mumu is not None:
        candidate = getattr(mumu, "ADB", None)
        if candidate and Path(candidate).is_file():
            return candidate
    found = shutil.which("adb")
    if found:
        return found
    bundled = Path(r"D:\MuMuPlayer\nx_device\15.0\shell\adb.exe")
    if bundled.is_file():
        return str(bundled)
    raise DeviceError("找不到 adb。请设置 ADB_PATH，或把 adb 放到 PATH。")


def parse_adb_devices(text):
    online = []
    for line in (text or "").splitlines()[1:]:
        parts = line.split()
        if len(parts) >= 2 and parts[1] == "device":
            online.append(parts[0])
    return online


def resolve_serial(environ=None, list_online=None, mumu_pick=None):
    """返回 (serial, source)。list_online / mumu_pick 便于离线测试注入。"""
    environ = os.environ if environ is None else environ
    happy = (environ.get("HAPPYFISH_ADB_DEV") or "").strip()
    if happy:
        return happy, "env:HAPPYFISH_ADB_DEV"
    adb_dev = (environ.get("ADB_DEV") or "").strip()
    if adb_dev:
        return adb_dev, "env:ADB_DEV"
    if mumu_pick is not None:
        serial = mumu_pick()
        if serial:
            return str(serial).strip(), "mumu_dev"
    if list_online is None:
        raise DeviceError("没有可用的设备发现函数")
    online = list(list_online())
    if len(online) == 1:
        return online[0], "adb_devices"
    if len(online) > 1:
        raise DeviceError(
            "多台 adb 设备在线，拒绝猜测。请设置 HAPPYFISH_ADB_DEV。当前: %s"
            % ", ".join(online)
        )
    raise DeviceError(
        "没有在线 adb 设备。请先连接模拟器，或设置 HAPPYFISH_ADB_DEV / ADB_DEV。"
    )


def parse_logical_frame(text):
    """dumpsys input 里的 logicalFrame=[left, top, right, bottom]，这才是 input tap 的坐标系。"""
    found = []
    for match in re.finditer(
        r"logicalFrame=\[\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\]",
        text or "",
    ):
        left, top, right, bottom = (int(item) for item in match.groups())
        width = right - left
        height = bottom - top
        if width > 0 and height > 0:
            found.append((width, height))
    if not found:
        return None
    return found[-1]


def choose_input_resolution(wm_size, screenshot_size, logical_size):
    """tap 坐标跟截图像素对齐。wm size 在横屏时经常仍是未旋转的竖屏物理尺寸。"""
    if logical_size:
        return logical_size, "dumpsys_input.logicalFrame"
    if (
        screenshot_size
        and wm_size == (screenshot_size[1], screenshot_size[0])
        and wm_size != screenshot_size
    ):
        return screenshot_size, "screenshot_rotated_from_wm"
    return wm_size, "wm_size"


def parse_wm_size(text):
    """adb shell wm size。有 Override size 时以它为准（这才是 input tap 的坐标系）。"""
    override = None
    physical = None
    for line in (text or "").splitlines():
        marker = None
        lowered = line.lower()
        if "override" in lowered:
            marker = "override"
        elif "physical" in lowered or "size" in lowered:
            marker = "physical"
        else:
            continue
        digits = []
        token = ""
        for char in line:
            if char.isdigit():
                token += char
            elif token:
                digits.append(int(token))
                token = ""
        if token:
            digits.append(int(token))
        if len(digits) < 2:
            continue
        pair = (digits[-2], digits[-1])
        if marker == "override":
            override = pair
        else:
            physical = pair
    if override:
        return override
    if physical:
        return physical
    raise DeviceError("无法从 wm size 解析分辨率: %r" % (text,))


class AdbClient:
    def __init__(self, adb_path, serial, source):
        self.adb_path = adb_path
        self.serial = serial
        self.source = source

    def run(self, *args, timeout=30):
        command = [self.adb_path, "-s", self.serial, *args]
        completed = subprocess.run(command, capture_output=True, timeout=timeout)
        if completed.returncode != 0:
            err = completed.stderr.decode("utf-8", "replace").strip()
            raise DeviceError("adb %s 失败 (%s): %s" % (" ".join(args[:2]), completed.returncode, err))
        return completed

    def connect_if_tcp(self):
        if ":" not in self.serial:
            return
        completed = subprocess.run(
            [self.adb_path, "connect", self.serial],
            capture_output=True,
            timeout=30,
        )
        text = (completed.stdout or b"").decode("utf-8", "replace")
        err = (completed.stderr or b"").decode("utf-8", "replace")
        blob = (text + err).lower()
        if completed.returncode != 0 or ("failed" in blob and "connected" not in blob):
            raise DeviceError("adb connect %s 失败: %s" % (self.serial, (text + err).strip()))

    def wm_size(self):
        completed = self.run("shell", "wm", "size")
        return parse_wm_size(completed.stdout.decode("utf-8", "replace"))

    def logical_display_size(self):
        completed = self.run("shell", "dumpsys", "input", timeout=25)
        return parse_logical_frame(completed.stdout.decode("utf-8", "replace"))

    def coordinate_space(self, screenshot_size):
        wm = self.wm_size()
        logical = None
        try:
            logical = self.logical_display_size()
        except DeviceError:
            logical = None
        chosen, source = choose_input_resolution(wm, screenshot_size, logical)
        return {
            "input_resolution": [int(chosen[0]), int(chosen[1])],
            "wm_size": [int(wm[0]), int(wm[1])],
            "input_resolution_source": source,
        }

    def screencap(self):
        """pull 到 ASCII 临时文件。session 目录可能含中文，adb pull 不能直接写到那里。"""
        import tempfile

        from PIL import Image

        remote = "/sdcard/_hf_recorder.png"
        local = Path(tempfile.gettempdir()) / "_hf_recorder.png"
        self.run("shell", "screencap", "-p", remote, timeout=40)
        self.run("pull", remote, str(local), timeout=40)
        image = Image.open(local)
        image.load()
        return image.copy()

    def tap(self, x, y):
        self.run("shell", "input", "tap", str(int(x)), str(int(y)))

    def swipe(self, x1, y1, x2, y2, duration_ms):
        self.run(
            "shell",
            "input",
            "swipe",
            str(int(x1)),
            str(int(y1)),
            str(int(x2)),
            str(int(y2)),
            str(int(duration_ms)),
        )


def open_client(environ=None):
    environ = os.environ if environ is None else environ
    mumu = None
    try:
        mumu = load_mumu_dev()
    except Exception:
        mumu = None
    adb_path = resolve_adb_path(environ, mumu=mumu)

    def list_online():
        completed = subprocess.run([adb_path, "devices"], capture_output=True, timeout=25)
        return parse_adb_devices(completed.stdout.decode("utf-8", "replace"))

    def mumu_pick():
        if mumu is None or not hasattr(mumu, "pick_device"):
            return None
        return mumu.pick_device(quiet=True)

    # 环境变量优先于 mumu_pick；mumu 不可用时才退到 adb devices。
    pick = mumu_pick if mumu is not None else None
    serial, source = resolve_serial(environ, list_online=list_online, mumu_pick=pick)
    client = AdbClient(adb_path, serial, source)
    client.connect_if_tcp()
    return client
