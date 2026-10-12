#!/usr/bin/env python3
"""Read-only audit of a purpose-based skill library and its index graph."""
import argparse
import json
import os
import re
from collections import defaultdict
from pathlib import Path
from urllib.parse import unquote

ENTRY = re.compile(r"^- \[([^\]]+)\]\((<[^>]+>|[^)]+)\)\s+—\s+(.+)$", re.M)
COUNT = re.compile(r"^技能数量：\s*(\d+)\s*$", re.M)
RESOURCE_DIRS = {"assets", "references", "scripts", "examples", "agents", "node_modules"}


def skill_name(path):
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return None
    front = text.split("---", 2)[1]
    match = re.search(r"^name:\s*([^\n]+)", front, re.M)
    return match.group(1).strip().strip("\"'") if match else None


def inventory(root, errors):
    found, visited = {}, set()
    for current, dirs, files in os.walk(root, followlinks=True):
        directory = Path(current)
        real = directory.resolve()
        if real in visited:
            dirs[:] = []
            continue
        visited.add(real)
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        if "SKILL.md" in files:
            path = directory / "SKILL.md"
            try:
                name = skill_name(path)
                if not name:
                    errors.append(f"Missing skill name: {path}")
                found[path.resolve()] = {"name": name, "path": str(path)}
            except (OSError, UnicodeError) as exc:
                errors.append(f"Unreadable skill: {path}: {exc}")
            dirs[:] = [d for d in dirs if d not in RESOURCE_DIRS]
    return found


def audit(skills_root, root_index, link_dirs):
    errors, warnings = [], []
    actual = inventory(skills_root, errors)
    pages, owners, counts = {}, defaultdict(list), {}
    active = set()

    def read_index(path):
        path = path.resolve()
        if path in active:
            errors.append(f"Index navigation cycle: {path}")
            return set()
        if path in pages:
            return pages[path]
        if not path.is_file():
            errors.append(f"Missing index: {path}")
            return set()
        active.add(path)
        text = path.read_text(encoding="utf-8")
        owned = set()
        for label, target, _ in ENTRY.findall(text):
            target = unquote(target.strip("<>").split("#", 1)[0])
            if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target):
                continue
            dest = Path(target)
            if not dest.is_absolute():
                dest = path.parent / dest
            if not dest.is_file():
                errors.append(f"Missing entry: {path}: {label} -> {dest}")
                continue
            dest = dest.resolve()
            if dest.name == "SKILL.md":
                owners[dest].append(str(path))
                owned.add(dest)
            elif dest.name == "SKILLS_INDEX.md":
                owned |= read_index(dest)
        declared = COUNT.search(text)
        if not declared:
            errors.append(f"Missing skill count: {path}")
        elif int(declared.group(1)) != len(owned):
            errors.append(f"Wrong count: {path}: declared {declared.group(1)}, actual {len(owned)}")
        active.remove(path)
        pages[path] = owned
        counts[str(path)] = len(owned)
        return owned

    registered = read_index(root_index)
    for path in sorted(actual.keys() - registered):
        errors.append(f"Unindexed skill: {actual[path]['path']}")
    for path in sorted(registered - actual.keys()):
        errors.append(f"Indexed outside library: {path}")
    for path, locations in owners.items():
        if len(locations) > 1:
            errors.append(f"Duplicate ownership: {path}: {locations}")
    for category in sorted(skills_root.iterdir()):
        if category.is_dir() and not category.name.startswith("."):
            if not (category / "SKILLS_INDEX.md").is_file():
                errors.append(f"Missing category index: {category}")
    by_name = defaultdict(list)
    for path, info in actual.items():
        by_name[info["name"]].append(path)
    for name, paths in by_name.items():
        if name and len(paths) > 1:
            errors.append(f"Duplicate skill name: {name}: {[str(p) for p in paths]}")
    for link_dir in link_dirs:
        for path, info in actual.items():
            if not info["name"]:
                continue
            link = link_dir / info["name"]
            if not link.is_symlink():
                errors.append(f"Missing client symlink: {link}")
            elif (link / "SKILL.md").resolve() != path:
                errors.append(f"Wrong client target: {link} -> {link.resolve()}")
    return {"ok": not errors, "skills": len(actual), "reachable_skills": len(registered),
            "indexes": len(pages), "counts": counts, "errors": errors, "warnings": warnings}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skills-root", required=True, type=Path)
    parser.add_argument("--root-index", required=True, type=Path)
    parser.add_argument("--link-dir", action="append", default=[], type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.skills_root.is_dir():
        parser.error("--skills-root must be an existing directory")
    try:
        result = audit(args.skills_root, args.root_index, args.link_dir)
    except (OSError, UnicodeError, ValueError) as exc:
        result = {"ok": False, "errors": [str(exc)]}
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"{'PASS' if result['ok'] else 'FAIL'}: {result.get('skills', 0)} skills, "
              f"{result.get('reachable_skills', 0)} reachable, {result.get('indexes', 0)} indexes")
        for message in result["errors"]:
            print(message)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
