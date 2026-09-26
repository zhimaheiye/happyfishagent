# -*- coding: utf-8 -*-
"""帧差分析：定位连拍序列里的界面变化点（找"一闪而过"的内容）。

输出 <dir>/_diff.txt：序号 / 文件名 / 与前一帧的平均像素差（0~255）。
差值大的位置 = 界面在变（动画、切屏、闪现文字）。

也可作为库使用：mean_abs_diff / change_bbox。算法与下面的命令行一致，
Recorder 不要再写一套平行的差分。
"""
import os
import sys

from PIL import Image, ImageChops

# 与历史命令行相同的降采样尺寸。分数是这块小图上的平均绝对差，范围 0~255。
DIFF_SIZE = (64, 36)


def _as_image(source):
    if isinstance(source, Image.Image):
        return source
    return Image.open(source)


def open_gray_small(source, size=DIFF_SIZE):
    return _as_image(source).convert("L").resize(size)


def mean_abs_diff(a, b, size=DIFF_SIZE):
    """两帧平均绝对差（0~255）。与本文件命令行写进 _diff.txt 的分数同一口径。"""
    diff = ImageChops.difference(open_gray_small(a, size), open_gray_small(b, size))
    data = diff.getdata()
    return sum(data) / float(size[0] * size[1])


def change_bbox(a, b, pixel_threshold=24, grid=(160, 90)):
    """变化区域的包围盒 [x, y, w, h]，坐标系跟源图一致。没有明显变化时返回 None。"""
    im_a = _as_image(a).convert("L")
    im_b = _as_image(b).convert("L")
    small_a = im_a.resize(grid)
    small_b = im_b.resize(grid)
    diff = ImageChops.difference(small_a, small_b)
    width, height = grid
    xs = []
    ys = []
    for index, value in enumerate(diff.getdata()):
        if value >= pixel_threshold:
            xs.append(index % width)
            ys.append(index // width)
    if not xs:
        return None
    left, right = min(xs), max(xs)
    top, bottom = min(ys), max(ys)
    src_w, src_h = im_a.size
    x = int(round(left * src_w / float(width)))
    y = int(round(top * src_h / float(height)))
    box_w = int(round((right - left + 1) * src_w / float(width)))
    box_h = int(round((bottom - top + 1) * src_h / float(height)))
    return [x, y, max(1, box_w), max(1, box_h)]


def changed_fraction(a, b, pixel_threshold=24, grid=(160, 90)):
    """降采样格子里超过阈值的像素占比，0~1。"""
    im_a = _as_image(a).convert("L").resize(grid)
    im_b = _as_image(b).convert("L").resize(grid)
    diff = ImageChops.difference(im_a, im_b)
    total = grid[0] * grid[1]
    changed = sum(1 for value in diff.getdata() if value >= pixel_threshold)
    return changed / float(total)


def write_burst_report(directory):
    """保持原命令行行为：只认 f*.png，写 <dir>/_diff.txt。"""
    files = sorted(
        name for name in os.listdir(directory) if name.startswith("f") and name.endswith(".png")
    )
    lines = []
    prev = None
    for index, name in enumerate(files):
        current = open_gray_small(os.path.join(directory, name))
        if prev is not None:
            score = mean_abs_diff(prev, current, size=current.size)
            bar = "#" * int(min(score, 60))
            lines.append("%3d %s %7.2f %s" % (index, name, score, bar))
        prev = current
    with open(os.path.join(directory, "_diff.txt"), "w", encoding="utf-8") as handle:
        handle.write("frames=%d\n" % len(files))
        handle.write("\n".join(lines))
    return len(files)


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    directory = args[0] if args else r"C:\Users\Administrator\.workbuddy\_vgtmp\burst"
    write_burst_report(directory)
    print("ok")


if __name__ == "__main__":
    main()
