# -*- coding: utf-8 -*-
"""Read-only MFA error evidence collector; creates sanitized ZIP, NEVER controls game.

Run on the Windows host; schedule/orchestrator belongs to the existing local Agent.
Examples:
  python collect_mfa_errors.py --log-dir "D:\\happyfishgame\\client_avalonia\\logs" --output-dir mfa-evidence --hours 48

The uploader/Agent must review the archive and push it; this script does not
connect to GitHub or any network, and does not enable MFA recovery.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import zipfile
from pathlib import Path

ERROR_RX = re.compile(
    r"\b(?:ERROR|FATAL|CRITICAL|Traceback|Exception|SafetyRefusal)\b|"
    r"任务失败|任务运行失败|运行失败|门禁未通过|识别失败|截图超时|已断开连接|异常中断|安全失败",
    re.IGNORECASE,
)
SECRET_RX = [
    re.compile(r"(?i)\b(authorization|api[_-]?key|access[_-]?token|refresh[_-]?token|password|passwd|secret|cookie|sessionkey)\b\s*[:=]\s*([^\s,;]+)"),
    re.compile(r"(?i)(bearer\s+)[a-z0-9._~+/-]{12,}"),
    re.compile(r"(?i)(你的\s*ID\s*为\s*[:：]?\s*)\d+"),
    re.compile(r"(?i)\b([a-z0-9._%+-]+)@([a-z0-9.-]+\.[a-z]{2,})\b"),
    re.compile(r"(?i)([a-z]:\\\\Users\\\\)[^\\\\\s]+"),
    re.compile(r"(/(?:home|Users)/)[^/\s]+"),
]
DEFAULT_LOG_DIR = r"D:\\happyfishgame\\client_avalonia\\logs"


def sanitize(line: str) -> str:
    line = SECRET_RX[0].sub(lambda m: m.group(1) + "=<REDACTED>", line)
    line = SECRET_RX[1].sub(lambda m: m.group(1) + "<REDACTED>", line)
    line = SECRET_RX[2].sub(lambda m: m.group(1) + "<REDACTED>", line)
    line = SECRET_RX[3].sub("<REDACTED_EMAIL>", line)
    line = SECRET_RX[4].sub(lambda m: m.group(1) + "<USER>", line)
    line = SECRET_RX[5].sub(lambda m: m.group(1) + "<USER>", line)
    return line


def windows(lines: list[str], before: int = 8, after: int = 18) -> tuple[list[str], int]:
    matched = [i for i, line in enumerate(lines) if ERROR_RX.search(line)]
    if not matched:
        return [], 0
    ranges = []
    for idx in matched:
        a, b = max(idx - before, 0), min(idx + after + 1, len(lines))
        if ranges and a <= ranges[-1][1]:
            ranges[-1] = (ranges[-1][0], max(ranges[-1][1], b))
        else:
            ranges.append((a, b))
    out = []
    for a, b in ranges:
        out.append(f"--- lines {a+1}..{b} ---")
        out.extend(f"{i+1}: {sanitize(lines[i].rstrip())}" for i in range(a, b))
    return out, len(matched)


def collect(log_dir: Path, out_dir: Path, hours: int, now: dt.datetime | None = None) -> dict:
    now = now or dt.datetime.now().astimezone()
    cutoff = now - dt.timedelta(hours=hours)
    if hours < 1 or hours > 24 * 14:
        raise ValueError("--hours must be from 1 through 336")
    sources = sorted(p for p in log_dir.glob("log-*.log") if p.is_file()) if log_dir.is_dir() else []
    if not sources:
        return {"status": "missing_logs", "log_dir": str(log_dir), "files": 0}
    excerpts = []
    total = 0
    selected = []
    for p in sources:
        # File selection by modified time avoids only-filename assumptions.
        # Large histories are not uploaded: collect only errors and nearby context.
        try:
            modified = dt.datetime.fromtimestamp(p.stat().st_mtime, tz=now.tzinfo)
            if modified < cutoff:
                continue
            lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        portion, count = windows(lines)
        if count:
            selected.append({"file": p.name, "lines": len(lines), "error_hits": count})
            excerpts.append((p.name + ".excerpt.txt", "\n".join(portion) + "\n"))
            total += count
    if not total:
        return {"status": "no_errors", "log_dir": str(log_dir), "files_scanned": len(sources), "error_hits": 0}
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = now.strftime("%Y%m%d_%H%M%S")
    identity = hashlib.sha256("\n".join(part for _, part in excerpts).encode()).hexdigest()[:12]
    dest = out_dir / f"MFA_errors_{stamp}_{identity}.zip"
    manifest = {
        "schema": "mfa-error-evidence-v1",
        "generated_at": now.isoformat(),
        "window_hours": hours,
        "error_hits": total,
        "sources": selected,
        "sha256_excerpt": identity,
        "note": "read-only error-window extracts, redacted; not proof of failure/retry authorization",
        "privacy": "Inspect archive before upload. No raw full-day logs are included.",
    }
    with zipfile.ZipFile(dest, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
        for name, body in excerpts:
            zf.writestr(name, body)
    return {"status": "created", "zip": str(dest), "error_hits": total, "file_count": len(excerpts)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--log-dir", type=Path, default=Path(DEFAULT_LOG_DIR))
    parser.add_argument("--output-dir", type=Path, default=Path("mfa-evidence"))
    parser.add_argument("--hours", type=int, default=48)
    args = parser.parse_args()
    print(json.dumps(collect(args.log_dir, args.output_dir, args.hours), ensure_ascii=False))


if __name__ == "__main__":
    main()
