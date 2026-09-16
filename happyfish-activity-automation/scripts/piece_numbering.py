# -*- coding: utf-8 -*-
"""拼块编号工具（跨活动通用）——把散落的拼块按「正确排布」编号并导出 MAA 可用模板。

思路（2026-09-15 实测有效，NCC 0.93 vs 次佳 0.53）：
  1) 「未开始帧」的中央 2x2 就是正确排布，但正中压着金色 ▶ 圆钮 -> 用圆形掩膜挖掉
  2) 打乱后帧里逐格判「是拼块还是灰格」
  3) 枚举 24 种排布，与未开始帧做**归一化互相关(NCC)**（自带亮度/对比度归一化，
     能吃掉两帧之间的明暗差异；纯 MAE 会被亮度差淹没，不可用）
  4) 最优排布按「左→右、上→下」编号 1~4，从打乱后帧裁出即得干净模板

判空判据（2026-09-16 修正）：
  灰格是**中性灰遮罩**（几乎无彩色像素、纹理平坦）；拼块是彩色图像。故取
      score = frac(sat>40) + 灰度std/100
  实测「星空鱼」：拼块 1.39~1.70，灰格 0.17~0.35，断层极大。
  ⚠️ 早期用「饱和度均值」判空，会被**深蓝星空**这种「均值不高但彩色像素很多」的
  拼块骗过（自动阈值 86.2 只找到 2/4 块）——别退回那个判据。

用法:
  python piece_numbering.py --idle idle.png --shuffled shuf.png \
      --xs 431,570,709,847 --ys 150,288,427,565 --cell 138 \
      --btn 639.5,357.5 --btn-r 95 \
      --out-dir "D:/.../拼块模板/蛋糕鱼_20260915" --prefix 蛋糕鱼 --label 蛋糕鱼

自动判块失灵时（打印 diagnostic 表后仍不对）：
  --cells "r1c2,r1c3,r3c4,r4c4"   手动指定 4 块所在格
  --sat 45                        退回旧的 sat 均值阈值模式
"""
import argparse
import itertools
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

MIN_TOP4_GAP = 0.30   # top-4 与第 5 名的分差下限，低于此值提示人工核对


def load_rgb(p):
    return np.asarray(Image.open(p).convert("RGB")).astype(float)


def cell_score(cel):
    """判「拼块 vs 灰格」：彩色像素占比 + 灰度标准差/100。

    灰格 = 中性灰遮罩 -> 两项都低；拼块 = 彩色图像 -> 至少一项高。
    单看 sat 均值会漏掉深蓝星空（均值低、彩像素多）。
    """
    sat = cel.max(axis=2) - cel.min(axis=2)
    frac = float((sat > 40).mean())
    gray = cel.mean(axis=2)
    return frac + float(gray.std()) / 100.0


def find_blocks(shuf, xs, ys, cell, sat_thr=None, cells=None):
    items = []
    for r in range(len(ys)):
        for c in range(len(xs)):
            x0, y0 = int(xs[c] - cell / 2), int(ys[r] - cell / 2)
            cel = shuf[y0:y0 + cell, x0:x0 + cell]
            sat = cel.max(axis=2) - cel.min(axis=2)
            items.append(((r + 1, c + 1), cell_score(cel), float(sat.mean()), cel))

    if cells:
        want = {s.strip() for s in cells.split(",")}
        blocks = {"r%dc%d" % pos: cel
                  for pos, sc, sm, cel in items if "r%dc%d" % pos in want}
        print("（手动指定）拼块 %d 块：%s" % (len(blocks), list(blocks.keys())))
    elif sat_thr is not None:
        blocks = {"r%dc%d" % pos: cel
                  for pos, sc, sm, cel in items if sm > sat_thr}
        print("（旧判据 sat 均值 > %.1f）拼块 %d 块：%s"
              % (sat_thr, len(blocks), list(blocks.keys())))
    else:
        print("=== 逐格判分（score = 彩色像素占比 + 灰度std/100）===")
        for pos, sc, sm, cel in sorted(items):
            print("  r%dc%d  score=%5.3f  satMean=%5.1f" % (pos[0], pos[1], sc, sm))
        srt = sorted(items, key=lambda t: -t[1])
        gap = srt[3][1] - srt[4][1]
        print("top4 切分间隙 = %.3f%s"
              % (gap, "（干净）" if gap >= MIN_TOP4_GAP else "  ⚠️ 偏小，务必人工核对！"))
        blocks = {"r%dc%d" % pos: cel for pos, sc, sm, cel in srt[:4]}
        print("自动判定拼块 4 块：%s" % list(blocks.keys()))

    if len(blocks) != 4:
        print("⚠️ 不是 4 块（%d），请人工核对；可用 --cells 手动指定。" % len(blocks))
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
    ap.add_argument("--cells", default=None, help="手动指定 4 块所在格，如 r1c2,r1c3,r3c4,r4c4")
    ap.add_argument("--sat", type=float, default=None, help="退回旧判据：sat 均值阈值")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--prefix", default="piece")
    ap.add_argument("--label", default="", help="示意图上的中文标题，如「蛋糕鱼」")
    a = ap.parse_args()

    xs = [float(v) for v in a.xs.split(",")]
    ys = [float(v) for v in a.ys.split(",")]
    cell = a.cell
    bx, by = [float(v) for v in a.btn.split(",")]

    idle, shuf = load_rgb(a.idle), load_rgb(a.shuffled)
    blocks = find_blocks(shuf, xs, ys, cell, a.sat, a.cells)
    if len(blocks) != 4:
        raise SystemExit("拼块数不是 4，停手（请看上面的逐格判分表，用 --cells 指定）")
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
