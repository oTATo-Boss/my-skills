#!/usr/bin/env python3
"""Read-only audit of a purpose-based skill library and its index graph."""
import argparse
import hashlib
import json
import os
import re
import stat
from collections import defaultdict
from datetime import date
from pathlib import Path
from urllib.parse import unquote

ENTRY = re.compile(r"^- \[([^\]]+)\]\((<[^>]+>|[^)]+)\)\s+—\s+(.+)$", re.M)
COUNT = re.compile(r"^技能数量：\s*(\d+)\s*$", re.M)
NAV_COUNT = re.compile(r"[（(](\d+)\s*个技能[）)]")
LINK = re.compile(r"\[[^\]\n]+\]\((<[^>]+>|[^)\n]+)\)")
RESOURCE_DIRS = {"assets", "references", "scripts", "examples", "agents", "shared", "node_modules"}
CACHE_DIRS = {".git", ".local", ".venv", "venv", "__pycache__", "node_modules", ".pytest_cache"}


def without_code_blocks(text):
    """Keep examples from becoming ownership declarations or navigation links."""
    lines, marker, length = [], None, 0
    for line in text.splitlines():
        fence = re.match(r"^\s*(`{3,}|~{3,})(.*)$", line)
        if fence:
            token, tail = fence.groups()
            if marker is None:
                marker, length = token[0], len(token)
            elif token[0] == marker and len(token) >= length and not tail.strip():
                marker = None
            continue
        if marker is None:
            lines.append(line)
    return "\n".join(lines)


def local_target(index, target):
    target = unquote(target.strip("<>").split("#", 1)[0])
    if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target):
        return None
    dest = Path(target)
    return dest if dest.is_absolute() else index.parent / dest


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
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in RESOURCE_DIRS | CACHE_DIRS]
        for name in dirs:
            link = directory / name
            if link.is_symlink() and not link.exists():
                errors.append(f"Broken library symlink: {link}")
        if "SKILL.md" in files:
            path = directory / "SKILL.md"
            try:
                name = skill_name(path)
                if not name:
                    errors.append(f"Missing skill name: {path}")
                found[path.resolve()] = {"name": name, "path": str(path)}
            except (OSError, UnicodeError) as exc:
                errors.append(f"Unreadable skill: {path}: {exc}")
    return found


def file_manifest(root):
    """Compare distributable files, excluding caches and local private data."""
    result = {}
    for current, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in CACHE_DIRS]
        for name in files:
            if name == ".DS_Store" or name.startswith(".env") or name.endswith((".pyc", ".pyo", ".log")):
                continue
            path = Path(current) / name
            result[str(path.relative_to(root))] = (
                hashlib.sha256(path.read_bytes()).hexdigest(),
                stat.S_IMODE(path.stat().st_mode),
            )
    return result


def check_sources(actual, errors, warnings):
    """Check portable per-skill records without inferring or fetching origins."""
    required = {"skill", "kind", "status", "source", "version", "author", "license",
                "collected_at", "recorded_at", "evidence"}
    statuses = {"confirmed": 0, "partial": 0, "unknown": 0}
    records = 0
    for info in actual.values():
        path = Path(info["path"]).parent / "SOURCE.md"
        if not path.is_file():
            errors.append(f"Missing source record: {path}")
            continue
        records += 1
        try:
            text = without_code_blocks(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError) as exc:
            errors.append(f"Unreadable source record: {path}: {exc}")
            continue
        fields = {}
        for key, value in re.findall(r"^- ([a-z_]+):[ \t]*(.*)$", text, re.M):
            if key in fields:
                errors.append(f"Duplicate source field: {path}: {key}")
            fields[key] = value.strip().strip("`")
        missing = sorted(key for key in required if not fields.get(key))
        if missing:
            errors.append(f"Incomplete source record: {path}: {missing}")
        if fields.get("skill") != info["name"]:
            errors.append(f"Wrong source identity: {path}: expected {info['name']}")
        if fields.get("kind") not in {"collected", "adapted", "local", "unknown"}:
            errors.append(f"Invalid source kind: {path}")
        status = fields.get("status")
        if status not in statuses:
            errors.append(f"Invalid source status: {path}")
        else:
            statuses[status] += 1
        try:
            recorded = fields.get("recorded_at", "")
            if date.fromisoformat(recorded).isoformat() != recorded:
                raise ValueError("Expected YYYY-MM-DD")
        except ValueError:
            errors.append(f"Invalid source record date: {path}")
        if status == "confirmed" and fields.get("source", "").lower() == "unknown":
            errors.append(f"Confirmed source has no origin: {path}")
    if statuses["partial"] or statuses["unknown"]:
        warnings.append(f"Sources needing confirmation: {statuses['partial']} partial, {statuses['unknown']} unknown")
    return {"records": records, "statuses": statuses}


def check_install_map(skills_root, actual, map_path, installed_root, compare, errors):
    data = json.loads(map_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("skills"), dict):
        errors.append(f"Invalid install map: {map_path}: expected a skills object")
        return 0
    mapping = data["skills"]
    if installed_root is None:
        value = data.get("installed_root")
        if not isinstance(value, str) or not value:
            errors.append(f"Missing installed root: {map_path}")
            return len(mapping)
        installed_root = Path(value).expanduser()
        if not installed_root.is_absolute():
            installed_root = map_path.parent / installed_root
    installed_root = Path(installed_root).expanduser().resolve()
    by_name = {info["name"]: info for info in actual.values() if info["name"]}
    for name in sorted(by_name.keys() - mapping.keys()):
        errors.append(f"Unmapped skill: {name}")
    for name in sorted(mapping.keys() - by_name.keys()):
        errors.append(f"Unknown mapped skill: {name}")
    seen_paths = {}
    for name, value in mapping.items():
        if not isinstance(value, str) or not value or Path(value).is_absolute() or ".." in Path(value).parts:
            errors.append(f"Invalid mapped path: {name}: expected a relative path inside the skill roots")
            continue
        relative = Path(value)
        if relative in seen_paths:
            errors.append(f"Duplicate mapped path: {name} and {seen_paths[relative]} -> {relative}")
        seen_paths[relative] = name
        if name not in by_name:
            continue
        source = Path(by_name[name]["path"]).parent
        if source.relative_to(skills_root) != relative:
            errors.append(f"Wrong source mapping: {name}: {relative} != {source.relative_to(skills_root)}")
        installed = installed_root / relative
        entry = installed / "SKILL.md"
        if not entry.is_file():
            errors.append(f"Missing installed skill: {name} -> {entry}")
            continue
        if skill_name(entry) != name:
            errors.append(f"Wrong installed name: {name} -> {entry}")
        if data.get("mode") == "independent-copy" and (installed.is_symlink() or installed.samefile(source)):
            errors.append(f"Installed copy is not independent: {name} -> {installed}")
        if compare:
            left, right = file_manifest(source), file_manifest(installed)
            changed = sorted(key for key in left.keys() | right.keys() if left.get(key) != right.get(key))
            if changed:
                errors.append(f"Installed copy differs: {name}: {changed}")
    return len(mapping)


def audit(skills_root, root_index, link_dirs=(), install_map=None, installed_root=None, compare_installed=False,
          check_source_records=False):
    skills_root, root_index = Path(skills_root).absolute(), Path(root_index).absolute()
    link_dirs = [Path(path).expanduser() for path in link_dirs]
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
        text = without_code_blocks(path.read_text(encoding="utf-8"))
        # Backlinks and resource links are checked but do not create ownership edges.
        missing = set()
        for target in LINK.findall(text):
            dest = local_target(path, target)
            if dest is not None and not dest.exists():
                missing.add(str(dest))
                errors.append(f"Missing index link: {path} -> {dest}")
        owned = set()
        for label, target, description in ENTRY.findall(text):
            dest = local_target(path, target)
            if dest is None:
                continue
            if not dest.is_file():
                if str(dest) not in missing:
                    errors.append(f"Missing entry: {path}: {label} -> {dest}")
                continue
            dest = dest.resolve()
            if dest.name == "SKILL.md":
                owners[dest].append(str(path))
                owned.add(dest)
            elif dest.name == "SKILLS_INDEX.md":
                children = read_index(dest)
                declared_child = NAV_COUNT.search(description)
                if declared_child and int(declared_child.group(1)) != len(children):
                    errors.append(f"Wrong navigation count: {path}: {label}: declared {declared_child.group(1)}, actual {len(children)}")
                owned |= children
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
    # Every real grouping level needs an index; a leaf skill's resource dirs do not.
    groups = defaultdict(set)
    for path, info in actual.items():
        directory = Path(info["path"]).parent
        while directory != skills_root and directory.is_relative_to(skills_root):
            groups[directory].add(path)
            directory = directory.parent
    for directory, members in sorted(groups.items()):
        is_leaf = (directory / "SKILL.md").is_file() and len(members) == 1
        if not is_leaf and not (directory / "SKILLS_INDEX.md").is_file():
            errors.append(f"Missing grouping index: {directory}")
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
            elif not link.exists():
                errors.append(f"Broken client symlink: {link}")
            elif (link / "SKILL.md").resolve() != path:
                errors.append(f"Wrong client target: {link} -> {link.resolve()}")
    mapped = None
    if install_map is not None:
        mapped = check_install_map(skills_root, actual, Path(install_map), installed_root, compare_installed, errors)
    sources = check_sources(actual, errors, warnings) if check_source_records else None
    return {"ok": not errors, "skills": len(actual), "reachable_skills": len(registered),
            "indexes": len(pages), "counts": counts, "install_map_skills": mapped,
            "installed_compared": bool(install_map is not None and compare_installed),
            "sources": sources,
            "errors": errors, "warnings": warnings}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skills-root", required=True, type=Path)
    parser.add_argument("--root-index", required=True, type=Path)
    parser.add_argument("--link-dir", action="append", default=[], type=Path)
    parser.add_argument("--install-map", type=Path)
    parser.add_argument("--installed-root", type=Path)
    parser.add_argument("--compare-installed", action="store_true")
    parser.add_argument("--check-sources", action="store_true", help="Check per-skill SOURCE.md records and report unresolved origins")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.skills_root.is_dir():
        parser.error("--skills-root must be an existing directory")
    if (args.installed_root or args.compare_installed) and not args.install_map:
        parser.error("--installed-root and --compare-installed require --install-map")
    try:
        result = audit(args.skills_root, args.root_index, args.link_dir,
                       args.install_map, args.installed_root, args.compare_installed, args.check_sources)
    except (OSError, UnicodeError, ValueError) as exc:
        result = {"ok": False, "errors": [str(exc)]}
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"{'PASS' if result['ok'] else 'FAIL'}: {result.get('skills', 0)} skills, "
              f"{result.get('reachable_skills', 0)} reachable, {result.get('indexes', 0)} indexes")
        for message in result["errors"]:
            print(message)
        for message in result.get("warnings", []):
            print(f"WARNING: {message}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
