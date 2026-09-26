# -*- coding: utf-8 -*-
"""酿月食香 - 体力角标数字识别器（活动专用，第一版）。

方法：红圆 ColorMatch 定位角标 → 白字二值 mask → 与数字模板(0/2/3) NCC 匹配。
输出：
  - "0".."9" 命中模板
  - "unknown" 角标存在但数字无模板（如 1/4/5/...）
  - None     未检测到角标（红圆缺失）
用法：
  python stamina_detect.py <截图路径720p>
  python stamina_detect.py <截图路径720p> --area 670,520,830,670 --templates <dir>
"""
from pathlib import Path
import sys
import numpy as np
from PIL import Image

DEFAULT_AREA = (670, 520, 830, 670)  # 体力角标大区域（720p）
TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"
NCC_THRESHOLD = 0.80  # 低于该值视为 unknown


def digit_mask_from(img_rgb, area):
    a = np.asarray(img_rgb.crop(area), dtype=np.float32)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    red = (r > 150) & (r - g > 40) & (r - b > 40)
    white = (r > 215) & (g > 215) & (b > 215)
    ys, xs = np.where(red)
    if not len(xs):
        return None
    cx, cy = (xs.min() + xs.max()) / 2, (ys.min() + ys.max()) / 2
    rr = (xs.max() - xs.min()) / 2
    wy, wx = np.where(white)
    inner = (wx - cx) ** 2 + (wy - cy) ** 2 < (rr * 0.5) ** 2
    mask = np.zeros((area[3] - area[1], area[2] - area[0]), dtype=np.float32)
    mask[wy[inner], wx[inner]] = 1.0
    ys2, xs2 = np.where(mask > 0)
    if not len(ys2):
        return None
    m = mask[ys2.min():ys2.max() + 1, xs2.min():xs2.max() + 1]
    im = Image.fromarray((m * 255).astype(np.uint8))
    im = im.resize((32, 32), Image.Resampling.NEAREST)
    return np.asarray(im, dtype=np.float32) / 255.0


def _ncc(a, b):
    a, b = a.reshape(-1), b.reshape(-1)
    return float((a * b).sum() / (np.sqrt((a * a).sum() * (b * b).sum()) + 1e-9))


def load_templates(tdir):
    temps = {}
    for p in sorted(Path(tdir).glob("digit_*.png")):
        digit = p.stem.replace("digit_", "")
        m = np.asarray(Image.open(p).convert("L"), dtype=np.float32) / 255.0
        temps[digit] = m
    return temps


def detect(image_path, area=DEFAULT_AREA, tdir=TEMPLATE_DIR):
    img = Image.open(image_path).convert("RGB")
    m = digit_mask_from(img, area)
    if m is None:
        return None, {}
    temps = load_templates(tdir)
    scores = {d: _ncc(m, t) for d, t in sorted(temps.items())}
    best = max(scores, key=scores.get)
    if scores[best] < NCC_THRESHOLD:
        return "unknown", scores
    return best, scores


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    image_path = args[0] if args else None
    if not image_path:
        print("usage: stamina_detect.py <截图路径> [--area x1,y1,x2,y2]")
        sys.exit(2)
    area = DEFAULT_AREA
    if "--area" in sys.argv:
        i = sys.argv.index("--area")
        area = tuple(int(v) for v in sys.argv[i + 1].split(","))
    digit, scores = detect(image_path, area=area)
    print("image=%s digit=%s scores=%s" % (image_path, digit, {k: round(v, 3) for k, v in scores.items()}))


if __name__ == "__main__":
    main()
