"""Put generated images next to real Xiaohongshu covers at feed size.

Run from the skill root:
  python3 scripts/compare_sheet.py out1.jpg out2.jpg ... [--refs R03 R22] [--output sheet.jpg]

Top row: generated images. Bottom row: reference covers (default 6 random, or the ids given).
Every tile is scaled to the same height, roughly the size of one card in the feed.
"""
import argparse
import json
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFile

# Flow downloads are occasionally a few bytes short; still show them, but say so.
ImageFile.LOAD_TRUNCATED_IMAGES = True

ROOT = Path(__file__).resolve().parents[1]
H = 400
GAP = 12


def tile(path, label):
    data = Path(path).read_bytes()
    if not data.rstrip(b"\x00").endswith(b"\xff\xd9") and str(path).lower().endswith((".jpg", ".jpeg")):
        print(f"warning: {path} looks truncated (no JPEG end marker)")
        label += " TRUNC"
    im = Image.open(path).convert("RGB")
    im = im.resize((round(im.width * H / im.height), H))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 8 + 9 * len(label), 22], fill=(0, 0, 0))
    d.text((4, 4), label, fill=(255, 255, 255))
    return im


def row(tiles):
    w = sum(t.width for t in tiles) + GAP * (len(tiles) - 1)
    canvas = Image.new("RGB", (w, H), (30, 30, 30))
    x = 0
    for t in tiles:
        canvas.paste(t, (x, 0))
        x += t.width + GAP
    return canvas


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("images", nargs="+")
    ap.add_argument("--refs", nargs="*", help="reference ids such as R03 R22")
    ap.add_argument("--output", default="compare-sheet.jpg")
    a = ap.parse_args()
    manifest = {r["id"]: r for r in json.loads((ROOT / "assets/reference-covers/manifest.json").read_text())}
    ids = a.refs or random.sample(sorted(manifest), min(6, len(manifest)))
    top = row([tile(p, f"OUT {i}") for i, p in enumerate(a.images, 1)])
    bottom = row([tile(ROOT / manifest[i]["file"], i) for i in ids])
    sheet = Image.new("RGB", (max(top.width, bottom.width), H * 2 + GAP), (30, 30, 30))
    sheet.paste(top, (0, 0))
    sheet.paste(bottom, (0, H + GAP))
    sheet.save(a.output, quality=88)
    print(a.output)


if __name__ == "__main__":
    main()
