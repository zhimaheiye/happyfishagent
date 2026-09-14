"""截图裁剪放大器（需要 Pillow）

用途：把截图里的一小块区域放大 N 倍另存，方便人眼/多模态确认按钮、角标、图标细节。
     判读图标与角标时必须放大，不要凭缩略图猜。

用法：
  python zoom.py <src.png> <out.png> <x0> <y0> <x1> <y1> [scale=2.0]

例：
  python zoom.py shot.png zoom.png 260 95 700 480 2.2
"""
import sys

from PIL import Image


def main():
    src, out = sys.argv[1], sys.argv[2]
    x0, y0, x1, y1 = (int(v) for v in sys.argv[3:7])
    scale = float(sys.argv[7]) if len(sys.argv) > 7 else 2.0
    im = Image.open(src).convert("RGB")
    c = im.crop((x0, y0, x1, y1))
    c = c.resize((int(c.width * scale), int(c.height * scale)), Image.LANCZOS)
    c.save(out)
    print("saved", out, c.size)


if __name__ == "__main__":
    main()
