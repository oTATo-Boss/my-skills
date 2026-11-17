"""Validate links, reference provenance, image decoding and planner resources.

Run from the skill root: python3 scripts/check_package.py (requires Pillow).
"""
from pathlib import Path
from collections import Counter
import hashlib
import json
import re
import sys

from PIL import Image, ImageFile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import plan_set  # noqa: E402


def main():
    failures = []
    manifest = json.loads((ROOT / "assets/reference-covers/manifest.json").read_text())
    ids = {r["id"] for r in manifest}
    for key in ("id", "file"):
        for value, count in Counter(r[key] for r in manifest).items():
            if count > 1:
                failures.append(f"Duplicate {key}: {value}")
    if ids != {f"R{i:02d}" for i in range(1, len(manifest) + 1)}:
        failures.append("Reference IDs must be continuous from R01")
    crops, hashes = set(), {}
    for r in manifest:
        path = (ROOT / r["file"]).resolve()
        if not path.is_relative_to(ROOT) or not path.is_file():
            failures.append(f"Invalid cover path: {r['file']}")
            continue
        w, h = r["source_size"]
        left, top, right, bottom = r["crop"]
        if not (0 <= left < right <= w and 0 <= top < bottom <= h):
            failures.append(f"Invalid crop: {r['id']}")
        if not re.fullmatch(r"[0-9a-f]{64}", r["source_sha256"]):
            failures.append(f"Invalid source hash: {r['id']}")
        crop_key = (r["source_sha256"], *r["crop"])
        if crop_key in crops:
            failures.append(f"Duplicate source crop: {r['id']}")
        crops.add(crop_key)
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest in hashes:
            failures.append(f"Duplicate image bytes: {hashes[digest]} and {r['id']}")
        hashes[digest] = r["id"]
        if int(r["id"][1:]) >= 31:
            if not r.get("batch") or not r.get("tags") or not isinstance(r.get("partial"), bool):
                failures.append(f"Missing batch/tags/partial: {r['id']}")
            if r.get("origin_kind") == "original-image":
                name = r.get("source_file")
                if not isinstance(name, str) or not name or Path(name).name != name:
                    failures.append(f"Invalid original source filename: {r['id']}")
                if digest != r["source_sha256"] or digest != r.get("asset_sha256"):
                    failures.append(f"Original bytes differ: {r['id']}")
                if r["crop"] != [0, 0, w, h]:
                    failures.append(f"Original image must remain uncropped: {r['id']}")
                try:
                    with Image.open(path) as image:
                        if image.size != (w, h):
                            failures.append(f"Original dimensions differ: {r['id']}")
                except (OSError, ValueError):
                    pass  # Report decoding failures in the full image check below.
            elif r.get("source_file") != f"{r.get('screen')}.webp":
                failures.append(f"Invalid source filename: {r['id']}")
    ImageFile.LOAD_TRUNCATED_IMAGES = False
    images = [p for p in (ROOT / "assets/reference-covers").iterdir()
              if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}]
    for path in images:
        try:
            with Image.open(path) as image:
                image.verify()
            with Image.open(path) as image:
                image.load()
            if path.suffix.lower() in {".jpg", ".jpeg"} and not path.read_bytes().endswith(b"\xff\xd9"):
                failures.append(f"Missing JPEG end marker: {path.name}")
        except (OSError, ValueError) as exc:
            failures.append(f"Invalid image {path.name}: {exc}")
    for page in ROOT.rglob("*.md"):
        text = page.read_text()
        for href in re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", text):
            if re.match(r"\w+://|#", href):
                continue
            path = href.split("#")[0].strip("<>")
            if path and not (page.parent / path).exists():
                failures.append(f"Broken link: {page.relative_to(ROOT)} -> {href}")
        for ref in set(re.findall(r"\bR\d+\b", text)):
            if ref not in ids:
                failures.append(f"Unknown reference {ref}: {page.relative_to(ROOT)}")
    library = (ROOT / "references/shot-types.md").read_text()
    for name, (_, _, refs, required) in plan_set.SHOT_TYPES.items():
        match = re.search(rf"\*\*{re.escape(name)}\*\* · ([^\n]+)", library)
        if not match or set(re.findall(r"R\d+", match[1])) != set(refs.split()):
            failures.append(f"Type or reference mismatch: {name}")
        for ref in refs.split():
            if ref not in ids:
                failures.append(f"Unknown cover {ref} in type {name}")
        if not any(required <= features for _, features in plan_set.SCENES.values()):
            failures.append(f"No compatible scene: {name}")
    for season in plan_set.SEASON.values():
        for key in ("head", "props", "scenes"):
            if len(season[key]) < 4:
                failures.append(f"Season pool too small: {key}")
        for scene in season["scenes"]:
            if scene not in plan_set.SCENES:
                failures.append(f"Scene lacks anchors: {scene}")
    if len(plan_set.TOPS) < 12 or len(plan_set.BOTTOMS) < 8 or len(plan_set.DIRECTIONS) < 8:
        failures.append("Look component pools too small")
    if failures:
        print("\n".join(failures))
        sys.exit(1)
    print(f"OK: {len(plan_set.SHOT_TYPES)} types, {len(manifest)} covers, "
          f"{len(plan_set.SCENES)} scenes, {len(images)} images decoded; provenance and links valid")


if __name__ == "__main__":
    main()
