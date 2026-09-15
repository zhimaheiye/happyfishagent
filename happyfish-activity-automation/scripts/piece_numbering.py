# -*- coding: utf-8 -*-
"""拼块编号工具（跨活动通用）——把散落的拼块按「正确排布」编号并导出 MAA 可用模板。

思路（2026-09-15 实测有效，NCC 0.93 vs 次佳 0.53）：
  1) 「未开始帧」的中央 2x2 就是正确排布，但正中压着金色 ▶ 圆钮 -> 用圆形掩膜挖掉
  2) 打乱后帧里逐格按饱和度找出 4 块拼块
  3) 枚举 24 种排布，与未开始帧做**归一化互相关(NCC)**（自带亮度/对比度归一化，
     能吃掉两帧之间的明暗差异；纯 MAE 会被亮度差淹没，不可用）
  4) 最优排布按「左→右、上→下」编号 1~4，从打乱后帧裁出即得干净模板

用法:
  python piece_numbering.py --idle idle.png --shuffled shuf.png \
      --xs 431,570,709,847 --ys 150,288,427,565 --cell 138 \
      --btn 639.5,357.5 --btn-r 95 \
      --out-dir "D:/.../拼块模板/蛋糕鱼_20260915" --prefix 蛋糕鱼
"""
import argparse
import itertools
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

EMPTY_SAT_GAP_MIN = 12.0   # 灰格与拼块的饱和度至少要拉开这么多才认


def load_rgb(p):
    return np.asarray(Image.open(p).convert("RGB")).astype(float)


def find_blocks(shuf, xs, ys, cell, sat_thr=None):
    """逐格判空：灰底反光 sat 明显低，拼块 sat 明显高。阈值自动取最大间隙中点。"""
    items = []
    for r in range(len(ys)):
        for c in range(len(xs)):
            x0, y0 = int(xs[c] - cell / 2), int(ys[r] - cell / 2)
            cel = shuf[y0:y0 + cell, x0:x0 + cell]
            sat = float((cel.max(axis=2) - cel.min(axis=2)).mean())
            items.append(((r + 1, c + 1), sat, cel))

    if sat_thr is None:
        vals = sorted(i[1] for i in items)
        gap, idx = -1.0, -1
        for k in range(len(vals) - 1):
            if vals[k + 1] - vals[k] > gap:
                gap, idx = vals[k + 1] - vals[k], k
        if gap < EMPTY_SAT_GAP_MIN:
            raise SystemExit("饱和度没有明显断层（最大间隙 %.1f），拼块位置判不出来，请手动看 p*_cells 图后传 --sat"
                             % gap)
        sat_thr = (vals[idx] + vals[idx + 1]) / 2
        print("自动阈值 sat > %.1f（断层 %.1f）" % (sat_thr, gap))

    blocks = {}
    for pos, sat, cel in items:
        if sat > sat_thr:
            blocks["r%dc%d" % pos] = cel
    print("拼块 %d 块：%s" % (len(blocks), list(blocks.keys())))
    if len(blocks) != 4:
        print("⚠️ 不是 4 块，请人工确认（其余可能是灰底反光/被遮挡）")
    return blocks


def assemble(blocks, names, order, cell):
    out = np.zeros((2 * cell, 2 * cell, 3))
    out[0:cell, 0:cell] = blocks[names[order[0]]]
    out[0:cell, cell:] = blocks[names[order[1]]]
    out[cell:, 0:cell] = blocks[names[order[2]]]
    out[cell:, cell:] = blocks[names[order[3]]]
    return out


def ncc_region(a, b, mask):
    vals = []
    for ch in range(3):
        x = a[:, :, ch][mask]
        y = b[:, :, ch][mask]
        x = x - x.mean()
        y = y - y.mean()
        d = np.linalg.norm(x) * np.linalg.norm(y)
        vals.append(float(x @ y / d) if d > 0 else 0.0)
    return float(np.mean(vals))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--idle", required=True, help="未开始帧（有 ▶ 圆钮那张）")
    ap.add_argument("--shuffled", required=True, help="打乱后帧（素材源）")
    ap.add_argument("--xs", required=True, help="列中心 x，逗号分隔")
    ap.add_argument("--ys", required=True, help="行中心 y，逗号分隔")
    ap.add_argument("--cell", type=int, default=138)
    ap.add_argument("--btn", default="639.5,357.5", help="▶ 圆钮中心 x,y")
    ap.add_argument("--btn-r", type=float, default=95.0, help="▶ 掩膜半径")
    ap.add_argument("--sat", type=float, default=None, help="手动指定饱和度阈值")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--prefix", default="piece")
    ap.add_argument("--label", default="", help="示意图上的中文标题，如「蛋糕鱼」")
    a = ap.parse_args()

    xs = [float(v) for v in a.xs.split(",")]
    ys = [float(v) for v in a.ys.split(",")]
    cell = a.cell
    bx, by = [float(v) for v in a.btn.split(",")]

    idle, shuf = load_rgb(a.idle), load_rgb(a.shuffled)
    blocks = find_blocks(shuf, xs, ys, cell, a.sat)
    names = sorted(blocks.keys())

    # 未开始帧的中央 2x2 = 正确排布；挖掉 ▶ 圆
    ox, oy = int(xs[1] - cell / 2), int(ys[1] - cell / 2)
    ref = idle[oy:oy + 2 * cell, ox:ox + 2 * cell]
    yy, xx = np.mgrid[0:2 * cell, 0:2 * cell]
    mask = ((xx - (bx - ox)) ** 2 + (yy - (by - oy)) ** 2) > a.btn_r ** 2

    res = []
    for perm in itertools.permutations(range(4)):
        res.append((ncc_region(assemble(blocks, names, perm, cell), ref, mask), perm))
    res.sort(key=lambda t: -t[0])

    print("\n=== 排布打分（NCC，越大越对；用未开始帧中央 2x2 当标准答案）===")
    for s, perm in res[:5]:
        tag = " ".join("%s=%s" % (k, names[perm[i]]) for i, k in enumerate(["TL", "TR", "BL", "BR"]))
        print("  NCC=%.3f   %s" % (s, tag))

    best_s, best = res[0]
    margin = res[0][0] - res[1][0]
    print("\n★ 最佳 NCC=%.3f  次佳 %.3f  领先 %.3f %s"
          % (best_s, res[1][0], margin, "(信号强)" if margin > 0.15 else "(⚠️ 信号弱，务必人工看图核对)"))
    print("   1号左上=%s  2号右上=%s  3号左下=%s  4号右下=%s"
          % (names[best[0]], names[best[1]], names[best[2]], names[best[3]]))

    os.makedirs(a.out_dir, exist_ok=True)
    ordered = {}
    for no, slot in ((1, 0), (2, 1), (3, 2), (4, 3)):
        arr = blocks[names[best[slot]]]
        ordered[no] = arr
        path = os.path.join(a.out_dir, "%s_%d.png" % (a.prefix, no))
        Image.fromarray(arr.astype(np.uint8)).save(path)   # RGB PNG，无 alpha，MAA 可直接用
        print("  写出 %s  (来自 %s)" % (os.path.basename(path), names[best[slot]]))

    # 编号示意图
    S = cell * 3
    sheet = Image.new("RGB", (2 * S, 2 * S), (255, 255, 255))
    for no, (cx, cy) in ((1, (0, 0)), (2, (1, 0)), (3, (0, 1)), (4, (1, 1))):
        sheet.paste(Image.fromarray(ordered[no].astype(np.uint8)).resize((S, S), Image.LANCZOS),
                    (cx * S, cy * S))
    dr = ImageDraw.Draw(sheet)
    dr.line([(S, 0), (S, 2 * S)], fill=(255, 255, 255), width=3)
    dr.line([(0, S), (2 * S, S)], fill=(255, 255, 255), width=3)
    try:
        f_big = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 64)
        f_sm = ImageFont.truetype(r"C:\Windows\Fonts\msyh.ttc", 18)
    except Exception:
        f_big = f_sm = ImageFont.load_default()
    POS = {1: ("左上", 0, 0), 2: ("右上", 1, 0), 3: ("左下", 0, 1), 4: ("右下", 1, 1)}
    for no, (cn, cx, cy) in POS.items():
        t = ("%s " % a.label if a.label else "") + "%d号·%s" % (no, cn)
        tx, ty = cx * S + 12, cy * S + 10
        dr.rectangle([tx - 6, ty - 4, tx + 8 * len(t), ty + 22], fill=(0, 0, 0))
        dr.text((tx, ty), t, fill=(0, 255, 0), font=f_sm)
        mx, my = cx * S + S // 2, cy * S + S // 2
        for dx, dy in [(-4, 0), (4, 0), (0, -4), (0, 4), (-3, -3), (3, 3), (-3, 3), (3, -3)]:
            dr.text((mx + dx, my + dy), str(no), fill=(0, 0, 0), font=f_big, anchor="mm")
        dr.text((mx, my), str(no), fill=(255, 220, 0), font=f_big, anchor="mm")
    sheet.save(os.path.join(a.out_dir, "%s_编号示意图.png" % a.prefix))
    print("  写出 %s_编号示意图.png" % a.prefix)
    return 0


if __name__ == "__main__":
    sys.exit(main())
