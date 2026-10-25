"""Publish a Recorder session as portable, pixel-exact evidence in assets/.

PNG sources become lossless WebP with every decoded pixel verified. Native Maa
logs are excluded. Original source hashes and filename mappings remain in the
manifest; flow, trace and OCR source links point at the published images.
"""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image


def archive(source, destination):
    source, destination = Path(source).resolve(), Path(destination).resolve()
    if destination.exists():
        raise FileExistsError("Choose a new archive directory")
    destination.mkdir(parents=True)
    (destination / "frames").mkdir()
    mapping, records, pixels_seen = {}, [], {}
    for original in sorted(source.rglob("*.png")):
        relative = original.relative_to(source).as_posix()
        if relative == "vision/frame.png":
            continue  # Mutable preview, not a separate recognition event.
        with Image.open(original) as picture:
            picture = picture.convert("RGB")
            pixel_hash = hashlib.sha256(str(picture.size).encode() + picture.tobytes()).hexdigest()
            target = pixels_seen.get(pixel_hash)
            if target is None:
                target = "frames/" + relative.replace("/", "--").removesuffix(".png") + ".webp"
                picture.save(destination / target, format="WEBP", lossless=True, method=4)
                with Image.open(destination / target) as decoded:
                    if decoded.convert("RGB").tobytes() != picture.tobytes():
                        raise RuntimeError("Pixel verification failed: " + relative)
                pixels_seen[pixel_hash] = target
        mapping[relative] = target
        records.append({"source": relative, "published": target, "pixel_sha256": pixel_hash,
                        "source_sha256": hashlib.sha256(original.read_bytes()).hexdigest()})

    def relocate(value):
        if isinstance(value, dict):
            return {key: relocate(item) for key, item in value.items()}
        if isinstance(value, list):
            return [relocate(item) for item in value]
        if isinstance(value, str):
            normalized = value.replace("\\", "/")
            prefix = source.as_posix() + "/"
            if normalized.startswith(prefix):
                normalized = normalized[len(prefix):]
            if normalized in mapping:
                return mapping[normalized]
            # Do not publish machine-specific session/workspace prefixes.
            return value.replace(str(source), ".").replace(source.as_posix(), ".")
        return value

    for original in sorted(source.rglob("*")):
        if not original.is_file() or original.suffix not in (".json", ".jsonl"):
            continue
        relative = original.relative_to(source)
        output = destination / relative
        output.parent.mkdir(parents=True, exist_ok=True)
        if original.suffix == ".jsonl":
            items = [relocate(json.loads(line)) for line in original.read_text(encoding="utf-8").splitlines() if line.strip()]
            output.write_text("".join(json.dumps(item, ensure_ascii=False) + "\n" for item in items), encoding="utf-8")
        else:
            item = json.loads(original.read_text(encoding="utf-8"))
            if relative.parts[0] == "vision" and isinstance(item, dict) and item.get("image"):
                item["image"] = mapping.get("vision/" + item["image"], item["image"])
            output.write_text(json.dumps(relocate(item), ensure_ascii=False, indent=2), encoding="utf-8")
    (destination / "archive_manifest.json").write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    traces = [json.loads(line) for line in (destination / "trace.jsonl").read_text(encoding="utf-8").splitlines()]
    lines = ["# 逐步动作表", "", "Recorder after 图可能仍是过渡帧；后继 before 图和 decisions/OCR 源图用于验收。", "",
             "| 状态 | 操作/坐标 | 原因 | 执行 | 前图 | 后图 |", "|---|---|---|---|---|---|"]
    for entry in traces:
        action, pictures = entry.get("action", {}), entry.get("screenshots", {})
        def link(key):
            return "[图](" + pictures[key] + ")" if key in pictures else "—"
        reason = str(action.get("reason", entry.get("safety", {}).get("reason", ""))).replace("|", "\\|").replace("\n", " ")
        lines.append("| %s→%s | %s %s | %s | %s | %s | %s |" % (
            entry.get("from_state", entry.get("state", "")), entry.get("to_state", ""),
            entry.get("type", ""), action.get("target_center_720p", action.get("standard_swipe_720p", "")),
            reason, entry.get("executed", ""), link("before"), link("after")))
    (destination / "actions.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"images": len(records), "unique_images": len(pixels_seen), "trace_entries": len(traces)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source")
    parser.add_argument("destination")
    args = parser.parse_args()
    print(json.dumps(archive(args.source, args.destination)))
