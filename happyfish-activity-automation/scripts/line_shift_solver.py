# -*- coding: utf-8 -*-
"""整行/整列循环平移棋盘的 BFS 求解器（跨活动通用）。

棋盘是 N x N 的环面（toros）：滑动某一行 → 该行循环横移；滑动某一列 → 该列循环纵移。
用来解「每日魔幻拼图」这类题：把若干拼块摆回正确的 2x2（或指定形状）。

用法（示例：4x4，4 块，目标 C=TL A=TR D=BL B=BR）:
  python line_shift_solver.py --n 4 \
      --at A=2,2 B=3,2 C=4,2 D=4,4 \
      --shape "TL=C TR=A BL=D BR=B"

坐标一律 1 起。--shape 支持 TL/TR/BL/BR（2x2）。
不给 --R/--C 时默认要求还原到中央 2x2；给 --anywhere 则任意位置即可。
"""
import argparse
from collections import deque

CELLS = {"TL": (0, 0), "TR": (0, 1), "BL": (1, 0), "BR": (1, 1)}


def build_shape(spec):
    """spec: 'TL=C TR=A BL=D BR=B' -> [(dr,dc,piece), ...]"""
    out = []
    for tok in spec.split():
        key, _, piece = tok.partition("=")
        dr, dc = CELLS[key.strip().upper()]
        out.append((dr, dc, piece.strip()))
    return out


def goal_ok(pos, shape, R0, C0, N):
    pieces = [p for _, _, p in shape]
    if len(set(pieces)) != len(pieces):
        return False
    for dr, dc, p in shape:
        if pos[p] != ((R0 + dr) % N, (C0 + dc) % N):
            return False
    return True


def neighbours(st, N):
    res = []
    for i in range(N):
        for k in (1, 2, 3):
            res.append(("行%d 右移%d" % (i + 1, k),
                        tuple((p[0], (p[1] + k) % N) if p[0] == i else p for p in st)))
            res.append(("行%d 左移%d" % (i + 1, k),
                        tuple((p[0], (p[1] - k) % N) if p[0] == i else p for p in st)))
            res.append(("列%d 下移%d" % (i + 1, k),
                        tuple(((p[0] + k) % N, p[1]) if p[1] == i else p for p in st)))
            res.append(("列%d 上移%d" % (i + 1, k),
                        tuple(((p[0] - k) % N, p[1]) if p[1] == i else p for p in st)))
    return res


def solve(N, pos0, shape, target=None, anywhere=False):
    order = list(pos0.keys())
    start = tuple(pos0[p] for p in order)

    def ok(st):
        pos = dict(zip(order, st))
        if anywhere:
            return any(goal_ok(pos, shape, r, c, N) for r in range(N) for c in range(N))
        return goal_ok(pos, shape, target[0], target[1], N)

    if ok(start):
        return [], start

    prev = {start: (None, None)}
    q = deque([start])
    while q:
        s = q.popleft()
        for desc, ns in neighbours(s, N):
            if ns in prev:
                continue
            prev[ns] = (s, desc)
            if ok(ns):
                path, cur = [], ns
                while prev[cur][1] is not None:
                    ps, d = prev[cur]
                    path.append(d)
                    cur = ps
                path.reverse()
                return path, ns
            q.append(ns)
    return None, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=4)
    ap.add_argument("--at", required=True, help="A=2,2 B=3,2 C=4,2 D=4,4")
    ap.add_argument("--shape", required=True, help='"TL=C TR=A BL=D BR=B"')
    ap.add_argument("--to", default="center", help="center 或 r,c（1 起，2x2 左上角）")
    ap.add_argument("--anywhere", action="store_true")
    a = ap.parse_args()

    pos0 = {}
    for tok in a.at.split():
        k, _, v = tok.partition("=")
        rr, cc = v.split(",")
        pos0[k.strip()] = (int(rr) - 1, int(cc) - 1)

    shape = build_shape(a.shape)
    if a.anywhere:
        target, anywhere = None, True
    else:
        anywhere = False
        if a.to == "center":
            target = ((a.n - 2) // 2, (a.n - 2) // 2)
        else:
            rr, cc = a.to.split(",")
            target = (int(rr) - 1, int(cc) - 1)

    path, end = solve(a.n, pos0, shape, target, anywhere)
    if path is None:
        print("无解")
        return 1
    print("起始: %s" % {k: (v[0] + 1, v[1] + 1) for k, v in pos0.items()})
    print("目标: %s%s" % ("任意 2x2" if anywhere else "2x2 左上角 = %s" % (target,),
                          "   排布 " + a.shape))
    print("步数: %d" % len(path))
    order = list(pos0.keys())
    cur = tuple(pos0[p] for p in order)
    for i, d in enumerate(path, 1):
        for dd, ns in neighbours(cur, a.n):
            if dd == d:
                cur = ns
                break
        pos = {k: (v[0] + 1, v[1] + 1) for k, v in zip(order, cur)}
        print("  %d) %-12s -> %s" % (i, d, pos))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
