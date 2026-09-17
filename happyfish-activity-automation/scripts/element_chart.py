#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""给一帧截图生成「元素并排对照图」——每局开局的第一步。

为什么需要它（2026-09-17 血泪）：
  浪漫满屋**同一局只用 4~5 种元素，跨局会换池**，所以「背图标清单」没用。
  唯一可靠的流程是：每局开局把「需求列 3 个 + 盘面出现的每个元素」裁出来拼成一张
  **并排对照图**，把名字定死，再往下算可行性。
  09-17 我就是跳过这一步，把盘面上的「橙色方块小机器人」叫成「相机」、
  又归进「非需求色」，于是误判「机器人一个都没有，这槽做不了」，白绕两小时。

用法：
    python element_chart.py shot.png out.png 相机=cell24 小机器人=cell13 保龄球=need1
    python element_chart.py shot.png out.png 相机=cell24 --per-row 5 --scale 4

定位写法（左边名字随便起，右边是"从哪里切"）：
    cellN        棋盘第 N 格（1–28，N=(行-1)*7+列），行坐标自动标定
    needN        需求列第 N 张黄卡（1–3）
    cx,cy        以该点为心的方框
    x0,y0,x1,y1  直接给矩形

输出：
    - 对照图（带中文标注）
    - stdout 打印每个条目的中心坐标，方便紧接着写拖拽命令
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from calib_calendar import DEFAULT_COLS, find_rows  # noqa: E402

# 需求列 3 张黄卡的中心（09-17 实测，间距 118；相对界面固定）
NEED_X = 137
NEED_YS = [174, 292, 410]

HALF = 52          # 半边长：格子/槽位的采样半径
FONT_CANDIDATES = [
    r"C:\Windows\Fonts\msyh.ttc",
    r"C:\Windows\Fonts\msyhbd.ttc",
    r"C:\Windows\Fonts\simhei.ttf",
    "/System/Library/Fonts/PingFang.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]


def load_font(size):
    for p in FONT_CANDIDATES:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()


def parse_item(text, cols, rows):
    """'名字=定位' -> (名字, (cx, cy))"""
    if "=" not in text:
        raise SystemExit(f"条目 {text!r} 缺少 '='，格式：名字=cellN / 名字=needN / 名字=cx,cy")
    name, spec = text.split("=", 1)
    name, spec = name.strip(), spec.strip()
    if spec.startswith("cell"):
        n = int(spec[4:])
        r, c = (n - 1) // 7, (n - 1) % 7
        if not (0 <= r < 4):
            raise SystemExit(f"cell{n} 超出 1–28")
        return name, (cols[c], rows[r]), f"cell{n}"
    if spec.startswith("need"):
        n = int(spec[4:])
        if not (1 <= n <= len(NEED_YS)):
            raise SystemExit(f"need{n} 超出 1–{len(NEED_YS)}")
        return name, (NEED_X, NEED_YS[n - 1]), f"need{n}"
    parts = [int(v) for v in spec.split(",")]
    if len(parts) == 2:
        return name, (parts[0], parts[1]), spec
    if len(parts) == 4:
        x0, y0, x1, y1 = parts
        return name, ((x0 + x1) // 2, (y0 + y1) // 2), spec
    raise SystemExit(f"定位 {spec!r} 无法解析")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("image")
    ap.add_argument("out")
    ap.add_argument("items", nargs="+", help="名字=定位，如 相机=cell24")
    ap.add_argument("--cols", help="逗号分隔列中心，覆盖默认锚点")
    ap.add_argument("--rows", help="逗号分隔行中心，覆盖自动标定")
    ap.add_argument("--scale", type=int, default=4)
    ap.add_argument("--per-row", type=int, default=5)
    ap.add_argument("--half", type=int, default=HALF, help="采样半径（默认 52）")
    args = ap.parse_args()

    im = Image.open(args.image).convert("RGB")
    a = np.array(im).astype(int)
    if im.size != (1280, 720):
        print(f"⚠️ 图片尺寸 {im.size}，脚本按 1280×720 校准", file=sys.stderr)

    cols = [int(v) for v in args.cols.split(",")] if args.cols else DEFAULT_COLS
    if args.rows:
        rows = [int(v) for v in args.rows.split(",")]
        row_src = "自定义"
    else:
        rows, row_src = find_rows(a, cols)
        if len(rows) != 4:
            raise SystemExit("⚠️ 行标定失败（应为 4 行）—— 确认界面在约会日历页，或用 --rows 手给")

    print(f"# {args.image}")
    print(f"列 {cols}")
    print(f"行 {rows}   ({row_src})")

    tiles = []
    for text in args.items:
        name, (cx, cy), spec = parse_item(text, cols, rows)
        h = args.half
        box = (max(0, cx - h), max(0, cy - h), min(im.width, cx + h), min(im.height, cy + h))
        tiles.append((name, spec, im.crop(box), (cx, cy)))
        print(f"  {name:<10} {spec:<14} 中心 ({cx}, {cy})")

    side = args.half * 2 * args.scale
    per = min(args.per_row, len(tiles))
    nrow = (len(tiles) + per - 1) // per
    pad, cap = 12, int(side * 0.16)
    cv = Image.new("RGB", (side * per + pad * (per + 1), (side + cap) * nrow + pad * (nrow + 1)),
                   (242, 242, 242))
    d = ImageDraw.Draw(cv)
    font = load_font(max(18, int(cap * 0.62)))
    for i, (name, spec, tile, _c) in enumerate(tiles):
        r_, c_ = i // per, i % per
        px = pad + c_ * (side + pad)
        py = pad + r_ * (side + cap + pad)
        cv.paste(tile.resize((side, side), Image.LANCZOS), (px, py + cap))
        d.text((px + 4, py + 2), f"{name} ({spec})", fill=(25, 25, 25), font=font)
    cv.save(args.out)
    print(f"-> {args.out}  {cv.size}")


if __name__ == "__main__":
    main()
