# -*- coding: utf-8 -*-
"""浪漫满屋：**逐格数元素个数**（不是数颜色种类）。

为什么存在（2026-09-21）：
  我在这盘上反复数错 —— 把「格25 = KG×1 + 相机×1」看成「相机×3」，由此推错了落子预测。
  `rh_scan_board.py` 数的是**颜色类别数**，不是**图标个数**，答不了"这格有几个相机"。
  芝麻的纪律是「数个数一律用工具」→ 这个脚本就是那把尺子。

原理（比颜色阈值稳）：
  1. 取格心 patch（half=48 → 96×96，把溢出格子的图标一起收进来）；
  2. 求 patch 的**众数色 = 该格的卡底**，据此判**色族**（蓝卡 / 黄卡=大日程 / 粉白空格）；
  3. 背景 = 「与该色族同族」的像素 ∪ 「与众数色 L1 距离 < tol」的像素 ——
     ⭐ 这一步是关键：卡底自带**深浅两档蓝 + 大圆花纹**，只按"离众数色多远"判会把
     整块卡底当成一个大图标（v1 就这么挂的）。
  4. 前景做 8 连通域 → 面积过关的算一个图标；
  5. 过滤**网格四角的装饰小珍珠**（淡奶油色、面积小）→ 否则每格会多报 1~4 个。

用法:
    python count_icons.py <截图.png>                    # 扫全部 28 格（只报"有内容"的）
    python count_icons.py <截图.png> --cells 15,16,17,24,25
    python count_icons.py <截图.png> --verbose          # 空格也报
    python count_icons.py <截图.png> --crop out.png     # 标注图（每格标 N 个 + 淡紫点标图标心）
    python count_icons.py <截图.png> --half 48 --tol 30 --min-area 450

⚠️ 已知局限（下结论时要带着说）：
  - **两个图标贴在一起 → 算成 1 个**（看 area 明显偏大就能察觉）。
  - 它只回答"几个"，**不回答"是什么"**（认名字仍用 element_chart.py + 人工）。
  - 大日程（黄卡）上那个"金色大图标"本身 1 个，但它算 5+ 个元素 —— **本工具数的是图标数，不是元素数**，
    所以黄卡格要单独按"已完成合并"读，别拿它的个数跟蓝卡比。
"""
import argparse
import sys

import numpy as np
from PIL import Image, ImageDraw

COLS = [298, 427, 543, 659, 775, 891, 1007]
ROWS = [182, 296, 410, 524]


def cell_center(n):
    r, c = (n - 1) // 7 + 1, (n - 1) % 7 + 1
    return COLS[c - 1], ROWS[r - 1]


def label(mask):
    """8 连通域标记（纯 numpy + 显式栈，不依赖 scipy）。"""
    h, w = mask.shape
    lab = np.zeros((h, w), dtype=np.int32)
    cur = 0
    for y0 in range(h):
        row = mask[y0]
        for x0 in range(w):
            if not row[x0] or lab[y0, x0]:
                continue
            cur += 1
            stack = [(y0, x0)]
            lab[y0, x0] = cur
            while stack:
                y, x = stack.pop()
                for dy in (-1, 0, 1):
                    ny = y + dy
                    if not (0 <= ny < h):
                        continue
                    for dx in (-1, 0, 1):
                        nx = x + dx
                        if 0 <= nx < w and mask[ny, nx] and not lab[ny, nx]:
                            lab[ny, nx] = cur
                            stack.append((ny, nx))
    return lab, cur


def name_color(r, g, b):
    if r > 200 and g < 140 and b < 140:
        return '红'
    if r > 210 and 140 <= g < 215 and b < 150:
        return '橙黄'
    if g > 150 and g - r > 20 and g - b > 20:
        return '绿'
    if r < 115 and g < 115 and b < 140:
        return '深黑'
    if min(r, g, b) > 225:
        return '白'
    if r > 200 and b > 190 and g < 200:
        return '粉紫'
    if b > r + 15:
        return '蓝'
    return '其他'


def bg_family(r, g, b):
    """由众数色推卡底色族。"""
    if b >= r and b >= g and (b - r) >= 10:
        return 'blue'
    if r > 200 and g > 170 and g >= b:
        return 'yellow'
    return 'pale'


def scan_cell(im, n, half, tol, min_area):
    cx, cy = cell_center(n)
    x0, y0 = max(0, cx - half), max(0, cy - half)
    x1, y1 = min(im.width, cx + half), min(im.height, cy + half)
    a = np.asarray(im.crop((x0, y0, x1, y1)).convert('RGB')).astype(np.int16)
    flat = a.reshape(-1, 3)
    q = (flat // 8).astype(np.int32)
    key = q[:, 0] * 65536 + q[:, 1] * 256 + q[:, 2]
    vals, cnts = np.unique(key, return_counts=True)
    k = int(vals[cnts.argmax()])
    bg = np.array([(k // 65536) % 256, (k // 256) % 256, k % 256], dtype=np.int16) * 8 + 4
    bg_ratio = float(cnts.max()) / len(flat)

    R, G, B = a[..., 0], a[..., 1], a[..., 2]
    fam = bg_family(int(bg[0]), int(bg[1]), int(bg[2]))
    if fam == 'blue':
        isbg = (B - R >= 8) & (B > 160)
    elif fam == 'yellow':
        isbg = (R > 212) & (G > 172) & (B < 198)
    else:
        isbg = (np.minimum(np.minimum(R, G), B) > 172)
    dist = np.abs(a - bg).sum(axis=2)
    fg = ~(isbg | (dist < tol))

    lab, ncomp = label(fg)
    icons = []
    for i in range(1, ncomp + 1):
        m = lab == i
        area = int(m.sum())
        if area < min_area:
            continue
        ys, xs = np.nonzero(m)
        mr, mg, mb = [int(a[..., ch][m].mean()) for ch in range(3)]
        # 网格四角的装饰小珍珠：淡奶油色 + 面积小 → 不是图标
        if min(mr, mg, mb) > 195 and area < 900:
            continue
        icons.append({
            'area': area, 'color': name_color(mr, mg, mb),
            'cx': x0 + int(xs.mean()), 'cy': y0 + int(ys.mean()),
            'rgb': (mr, mg, mb),
        })
    icons.sort(key=lambda d: (d['cy'] // 20, d['cx']))
    return {'n': n, 'center': (cx, cy), 'bg': tuple(int(v) for v in bg),
            'fam': fam, 'bg_ratio': bg_ratio, 'icons': icons}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('image')
    ap.add_argument('--cells', help='只扫这些格，逗号分隔，如 15,16,17')
    ap.add_argument('--half', type=int, default=48, help='采样半径（默认 48）')
    ap.add_argument('--tol', type=int, default=30, help='与众数色的 L1 距离阈值（默认 30）')
    ap.add_argument('--min-area', type=int, default=450, help='最小图标面积（默认 450）')
    ap.add_argument('--verbose', action='store_true', help='空格也打印')
    ap.add_argument('--crop', help='输出标注图')
    args = ap.parse_args()

    im = Image.open(args.image).convert('RGB')
    if im.size != (1280, 720):
        print('⚠️ 尺寸 %s，本脚本按 1280×720 校准' % (im.size,), file=sys.stderr)

    cells = ([int(v) for v in args.cells.split(',')] if args.cells else list(range(1, 29)))
    print('# %s   (half=%d tol=%d min_area=%d)' % (args.image, args.half, args.tol, args.min_area))
    print('%-4s %-10s %-6s %-5s %-4s %s'
          % ('格', '中心', '色族', '底占比', '个数', '图标(色 area@中心)'))

    results = []
    for n in cells:
        r = scan_cell(im, n, args.half, args.tol, args.min_area)
        results.append(r)
        if not r['icons'] and not args.verbose:
            continue
        det = ' '.join('%s %d@(%d,%d)' % (i['color'], i['area'], i['cx'], i['cy'])
                       for i in r['icons'])
        print('%-4d %-10s %-6s %-5.2f %-4d %s'
              % (n, '%d,%d' % r['center'], r['fam'], r['bg_ratio'], len(r['icons']), det or '—'))

    if args.crop:
        c = im.copy()
        d = ImageDraw.Draw(c)
        for r in results:
            cx, cy = r['center']
            d.text((cx - 46, cy - 62), '%d:%d' % (r['n'], len(r['icons'])), fill=(200, 0, 0))
            for i in r['icons']:
                d.ellipse([i['cx'] - 4, i['cy'] - 4, i['cx'] + 4, i['cy'] + 4], fill=(255, 0, 255))
        c.save(args.crop)
        print('-> %s' % args.crop)


if __name__ == '__main__':
    main()
