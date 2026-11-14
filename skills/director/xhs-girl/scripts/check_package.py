"""Check links, reference covers and that the type library matches plan_set.py.

Run from the skill root: python3 scripts/check_package.py
"""
from pathlib import Path
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import plan_set  # noqa: E402


def main():
    failures = []
    for page in ROOT.rglob("*.md"):
        for href in re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", page.read_text()):
            if re.match(r"\w+://|#", href):
                continue
            path = href.split("#")[0].strip("<>")
            if path and not (page.parent / path).exists():
                failures.append(f"Broken link: {page.relative_to(ROOT)} -> {href}")
    manifest = json.loads((ROOT / "assets/reference-covers/manifest.json").read_text())
    ids = {r["id"] for r in manifest}
    for row in manifest:
        if not (ROOT / row["file"]).is_file():
            failures.append(f"Missing cover: {row['file']}")
    library = (ROOT / "references/shot-types.md").read_text()
    for name, (_, _, refs, _) in plan_set.SHOT_TYPES.items():
        if f"**{name}**" not in library:
            failures.append(f"Type missing from shot-types.md: {name}")
        for ref in refs.split():
            if ref not in ids:
                failures.append(f"Unknown cover {ref} in type {name}")
    for season in plan_set.SEASON.values():
        for key in ("head", "props", "scenes"):
            if len(season[key]) < 4:
                failures.append(f"Season pool too small: {key}")
    if len(plan_set.TOPS) < 12 or len(plan_set.BOTTOMS) < 8 or len(plan_set.DIRECTIONS) < 8:
        failures.append("Look component pools too small")
    if failures:
        print("\n".join(failures))
        sys.exit(1)
    print(f"OK: {len(plan_set.SHOT_TYPES)} types, {len(manifest)} covers, links valid")


if __name__ == "__main__":
    main()
