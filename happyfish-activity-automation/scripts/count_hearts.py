# -*- coding: utf-8 -*-
"""数「鱼宝乐园」鱼宝宝头顶的心：红心(已得) / 灰心(未得)。

实测心堆模型（2026-09-19 用像素验证）：
    每条鱼头顶共 **6 颗心** = 3 步 × 2 颗，自下而上依次是
    【喂食 下 2 颗】→【玩耍 中 2 颗】→【喂奶 上 2 颗】；
    做过的变亮红 (#FF494A)，没做的保持灰褐 (#84655F)。
    → 所以「顶上还剩 2 颗灰心」= 本步做完，下一步是喂奶。

⚠️ 小图肉眼易错（09-19 把 4 心看成 3 心、据此得出错误结论），一律用本工具数。

用法:
    python count_hearts.py region <图> <x0> <y0> <x1> <y1> [--label 1号]
    python count_hearts.py scan   <图>                 # 全图找所有心堆，逐堆报数
"""
import sys
import os
from PIL import Image

V = r"C:\Users\Administrator\.workbuddy\_vgtmp"

RED = lambda r, g, b: r > 200 and g < 130 and b < 140
GREY = lambda r, g, b: abs(r - g) < 45 and abs(g - b) < 22 and 100 < r < 175


def blobs(mask, w, h, min_pix=100, max_pix=500):
    """4 邻接连通块，只保留面积在心形范围内的。"""
    seen = [False] * (w * h)
    out = []
    for i in range(w * h):
        if mask[i] and not seen[i]:
            st = [i]
            seen[i] = True
            n = sx = sy = 0
            while st:
                j = st.pop()
                y, x = divmod(j, w)
                n += 1
                sx += x
                sy += y
                for k in (j - 1 if x > 0 else -1,
                          j + 1 if x < w - 1 else -1,
                          j - w if y > 0 else -1,
                          j + w if y < h - 1 else -1):
                    if k >= 0 and mask[k] and not seen[k]:
                        seen[k] = True
                        st.append(k)
            if min_pix <= n <= max_pix:
                out.append((round(sx / n), round(sy / n), n))
    return out


def hearts_in(im, box=None):
    if box:
        im = im.crop(box)
        ox, oy = box[0], box[1]
    else:
        ox = oy = 0
    w, h = im.size
    red = [False] * (w * h)
    grey = [False] * (w * h)
    for i, (r, g, b) in enumerate(im.getdata()):
        red[i] = RED(r, g, b)
        grey[i] = GREY(r, g, b)
    R = [(x + ox, y + oy, n) for x, y, n in blobs(red, w, h)]
    G = [(x + ox, y + oy, n) for x, y, n in blobs(grey, w, h)]
    return R, G


def cluster(pts, gap=70):
    """把心按邻近关系聚成「一堆」（同一条鱼的 6 颗）。"""
    groups = []
    for x, y, n in sorted(pts, key=lambda t: (t[1], t[0])):
        for g in groups:
            if any(abs(x - a) < gap and abs(y - b) < gap for a, b, _ in g):
                g.append((x, y, n))
                break
        else:
            groups.append([(x, y, n)])
    return groups


def cmd_region(a):
    p = a[0]
    box = tuple(int(v) for v in a[1:5])
    label = a[a.index("--label") + 1] if "--label" in a else "region"
    im = Image.open(p).convert("RGB")
    R, G = hearts_in(im, box)
    out = os.path.join(V, "hearts_%s.png" % label)
    c = im.crop(box)
    c.resize((c.width * max(1, 480 // max(c.width, 1)), c.height * max(1, 480 // max(c.width, 1))),
             Image.LANCZOS).save(out)
    print("%s  区域 %s  红心=%d  灰心=%d（放大图 %s）" % (label, box, len(R), len(G), out))


def cmd_scan(a):
    p = a[0]
    im = Image.open(p).convert("RGB")
    R, G = hearts_in(im)
    print("全图：红心 %d 颗、灰心 %d 颗" % (len(R), len(G)))
    groups = cluster(R + G)
    rows = []
    for g in groups:
        red = sum(1 for t in g if t in R)
        grey = sum(1 for t in g if t in G)
        xs = [t[0] for t in g]
        ys = [t[1] for t in g]
        rows.append((min(ys), red, grey, min(xs), max(xs), min(ys), max(ys), len(g)))
    rows.sort()
    print("%-4s %-6s %-6s %s" % ("堆", "红", "灰", "bbox(x0-x1,y0-y1) 心数"))
    for i, (_, red, grey, x0, x1, y0, y1, n) in enumerate(rows, 1):
        print("%-4d %-7d %-7d (%d-%d, %d-%d)  共%d颗" % (i, red, grey, x0, x1, y0, y1, n))


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(0)
    mode = sys.argv[1]
    if mode == "region":
        cmd_region(sys.argv[2:])
    elif mode == "scan":
        cmd_scan(sys.argv[2:])
    else:
        print(__doc__)
