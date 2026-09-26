# -*- coding: utf-8 -*-
"""设备像素与项目标准 1280×720 坐标系的互换。

MaaHappyFish 的探索包（例如开贝壳）把点击同时记成
target_center_720p 和 device_tap_coordinate。这里用半入（0.5 进 1）而不是
Python 内置 round 的银行家舍入，否则 635 * 1080/720 = 952.5 会变成 952，
对不上开贝壳记录里的 953。
"""
import math

STD_W = 1280
STD_H = 720


def _half_up(value):
    return int(math.floor(float(value) + 0.5))


def to_standard(x, y, device_w, device_h):
    if device_w <= 0 or device_h <= 0:
        raise ValueError("device resolution must be positive")
    sx = _half_up(float(x) * STD_W / float(device_w))
    sy = _half_up(float(y) * STD_H / float(device_h))
    return sx, sy


def to_device(x, y, device_w, device_h):
    if device_w <= 0 or device_h <= 0:
        raise ValueError("device resolution must be positive")
    dx = _half_up(float(x) * float(device_w) / STD_W)
    dy = _half_up(float(y) * float(device_h) / STD_H)
    return dx, dy


def scale_point(x, y, device_w, device_h, space):
    """CLI 坐标 -> (device_xy, standard_xy)。space 为 device 或 720p。"""
    if space == "device":
        standard = to_standard(x, y, device_w, device_h)
        return (int(x), int(y)), standard
    if space == "720p":
        device = to_device(x, y, device_w, device_h)
        return device, (int(x), int(y))
    raise ValueError("coord space must be device or 720p")
