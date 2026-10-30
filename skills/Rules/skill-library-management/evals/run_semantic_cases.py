#!/usr/bin/env python3
"""Build isolated evidence, or verify it after an Agent's read-only review.

This does not perform semantic classification or touch installed skill libraries.
The rollback exercise is restricted to this script's generated temporary fixture.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile

SPEC = importlib.util.spec_from_file_location(
    "audit_library", Path(__file__).resolve().parents[1] / "scripts/audit_library.py")
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)


def put(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def skill(path, name, body, description="Fixture workflow."):
    put(path / "SKILL.md", f"---\nname: {name}\ndescription: {description}\n---\n{body}\n")
    fields = dict(skill=name, kind="local", status="confirmed", source="isolated test fixture",
                  version="fixture", author="test author", license="MIT",
                  collected_at="unknown", recorded_at="2026-10-30", evidence="run_semantic_cases.py")
    put(path / "SOURCE.md", "# Source\n" + "".join(f"- {k}: `{v}`\n" for k, v in fields.items()))


def index(path, entries):
    put(path, f"# Fixture index\n\n技能数量：{len(entries)}\n\n" + "".join(
        f"- [{name}]({target}) — Fixture.\n" for name, target in entries))


def snapshot(root):
    """Include dirs, bytes, modes and original symlink text; never follow links."""
    result = {}
    for current, dirs, files in os.walk(root, followlinks=False):
        for name in sorted(dirs + files):
            path = Path(current) / name
            key = path.relative_to(root).as_posix()
            mode = stat.S_IMODE(path.lstat().st_mode)
            if path.is_symlink():
                result[key] = ["link", os.readlink(path), mode]
            elif path.is_dir():
                result[key] = ["dir", mode]
            else:
                result[key] = ["file", hashlib.sha256(path.read_bytes()).hexdigest(), mode]
    return result


def prepare():
    root = Path(tempfile.mkdtemp(prefix="skill-semantic-eval-")).resolve()
    active = root / "active"
    a = active / "01/dev/skills/A"
    skill(a, "same-name", "Input: UTF-8 text. Output: the same text as a JSON string.\nRun scripts/export.py.")
    put(a / "scripts/export.py", "import json, sys\nprint(json.dumps(sys.stdin.read(), ensure_ascii=False))\n")
    shutil.copytree(a, active / "01/install/A")
    shutil.copytree(a, active / "01/unrelated/B")
    skill(active / "01/unrelated/C", "unlisted", "Input: a list. Output: list length; independent counting workflow.")
    put(active / "01/dev/INSTALL_MAP.json", json.dumps({"installed_root": "../install", "mode": "independent-copy", "skills": {"same-name": "A"}}))
    index(active / "01/dev/SKILLS_INDEX.md", [("same-name", "skills/A/SKILL.md")])
    index(active / "01/unrelated/SKILLS_INDEX.md", [("same-name", "B/SKILL.md")])
    for client in ("client-one", "client-two"):
        link = active / "01" / client / "same-name"
        link.parent.mkdir()
        link.symlink_to("../install/A")

    shutil.copytree(active / "01/dev", active / "02/dev")
    shutil.copytree(active / "01/install", active / "02/install")
    put(active / "02/install/A/scripts/export_csv.py", "import csv, sys\nw = csv.writer(sys.stdout)\nw.writerow(['text'])\nw.writerow([sys.stdin.read()])\n")
    with (active / "02/install/A/SKILL.md").open("a") as stream:
        stream.write("Unique installed capability: CSV export via scripts/export_csv.py, header text.\n")

    for name in ("alpha", "乙"):
        folder = active / "03" / name
        skill(folder, name, "Input: any UTF-8 text from stdin. Output: a JSON string to stdout.\nRun scripts/export.py; preserve Unicode and trailing newlines.",
              "A polished workflow." if name == "alpha" else "文本序列化。")
        put(folder / "scripts/export.py", ("from missing_encoder import encode\nimport sys\nprint(encode(sys.stdin.read()))\n" if name == "alpha" else (a / "scripts/export.py").read_text()))
        put(folder / "requirements.txt", "# Python standard library only.\n")
        put(folder / "CHANGELOG.md", "Version 9 (2026).\n" if name == "alpha" else "Version 1 (2024).\n")

    skill(active / "04/director", "director", "Input: a brief. Output: shot plan using references/template.md.\nReview continuity, timing and subtitle legibility; does not render.")
    put(active / "04/director/references/template.md", "Shot | duration | action | subtitle safe area.\nAcceptance: total duration matches brief; consistent subject and location.\n")
    skill(active / "04/render", "render", "Input: approved shot plan and caption text. Output: render-job JSON including captions via scripts/job.py. Does not develop the story.")
    put(active / "04/render/scripts/job.py", "import json, sys\njob = json.load(sys.stdin)\nassert 'shots' in job and 'captions' in job\nprint(json.dumps(job))\n")
    put(active / "04/plugin.json", json.dumps({"enabled": True, "tool": "submit-render-job", "inputs": ["render-job JSON"], "provides": "render execution", "story_template": False}))

    skill(active / "05/global/A", "image-a", "Input: external photo. Output: resize plan preserving aspect ratio; no internal asset access.", "处理全部图片。")
    skill(active / "05/global/B", "image-b", "Input: vector logo. Output: color palette audit; no photo resizing.", "处理全部图片。")
    skill(active / "05/P/skills/A", "image-a", "Input: project P internal asset IDs. Output: P naming and release checklist. Project P only; no resizing.")
    put(active / "05/visibility.json", json.dumps({"P": ["global/A", "global/B", "P/skills/A"], "Q": ["global/A", "global/B"]}))

    skill(active / "06/offline", "offline", "Input: text. Output: JSON offline using Python standard library; no account or network.")
    put(active / "06/offline/scripts/export.py", (a / "scripts/export.py").read_text())
    put(active / "06/offline/CHANGELOG.md", "2022: local JSON export.\n")
    skill(active / "06/cloud", "cloud", "Input: text. Output: vendor-hosted translation. Requires vendor-sdk and an account; availability unknown.")
    put(active / "06/cloud/requirements.txt", "vendor-sdk==2099.0\n")
    put(active / "06/cloud/CHANGELOG.md", "2026: cloud workflow.\n")
    skill(active / "06/plugins/current", "cloud-helper", "Input: text. Output: vendor request payload; active release.")
    skill(active / "06/plugins/history", "cloud-helper", "Historical release; not enabled.")
    put(active / "06/registry.json", json.dumps({"enabled_plugin": "plugins/current", "historical_cache": "plugins/history", "projects": [{"path": "unavailable-project", "status": "unavailable", "reason": "fixture registry: access unavailable"}]}))

    folder = active / "07/dev/skills/A"
    skill(folder, "archive-me", "Input: text. Output: JSON string. Run scripts/export.py.")
    put(folder / "scripts/export.py", (a / "scripts/export.py").read_text())
    (folder / "scripts/export.py").chmod(0o755)
    shutil.copytree(folder, active / "07/install/A")
    put(active / "07/install/A/local-notes.txt", "Independent uncommitted installation change; preserve me.\n")
    index(active / "07/dev/SKILLS_INDEX.md", [("archive-me", "skills/A/SKILL.md")])
    index(active / "07/install/SKILLS_INDEX.md", [("archive-me", "A/SKILL.md")])
    put(active / "07/dev/INSTALL_MAP.json", json.dumps({"installed_root": "../install", "mode": "independent-copy", "skills": {"archive-me": "A"}}))
    link = active / "07/client/archive-me"
    link.parent.mkdir()
    link.symlink_to("../install/A")
    put(root / "baseline.json", json.dumps(snapshot(active), ensure_ascii=False, indent=2))
    print(root)


def execute(script, payload):
    result = subprocess.run([sys.executable, "-B", str(script)], input=payload,
                            capture_output=True, text=True, cwd=script.parent, timeout=10)
    return {"code": result.returncode, "stdout": result.stdout, "stderr": result.stderr}


def verify(root):
    if not root.name.startswith("skill-semantic-eval-") or not (root / "baseline.json").is_file():
        raise ValueError("Expected this runner's temporary fixture directory")
    active = root / "active"
    baseline = json.loads((root / "baseline.json").read_text())
    assert snapshot(active) == baseline, "Read-only review modified fixture"
    results = {"read_only_review": "PASS"}
    for case in ("01", "02"):
        base = active / case
        results[case] = AUDIT.audit(base / "dev/skills", base / "dev/SKILLS_INDEX.md",
                                   install_map=base / "dev/INSTALL_MAP.json", compare_installed=True)
    assert results["01"]["ok"], results["01"]
    assert any("Installed copy differs" in e for e in results["02"]["errors"])
    evidence = AUDIT.audit(active / "01/unrelated", active / "01/unrelated/SKILLS_INDEX.md")
    assert evidence["skills"] == 2 and any("Unindexed skill" in e for e in evidence["errors"])
    results["01_unlisted"] = evidence
    found = set()
    for relative in ("01/dev/skills", "01/install", "01/unrelated", "01/client-one", "01/client-two"):
        errors = []
        found.update(AUDIT.inventory(active / relative, errors))
        assert not errors, errors
    assert len(found) == 4
    assert (active / "01/client-one/same-name").samefile(active / "01/install/A")
    assert (active / "01/client-two/same-name").samefile(active / "01/install/A")
    results["01_counts"] = {"physical_entities": len(found), "mapped_logical_skills": 3, "client_entries": 2,
                            "basis": "4 real paths; the explicit dev/install map relates exactly 2 of them; B and C remain separate"}
    payload = '你好,"quoted"\n'
    for label, path in [("02_csv", "02/install/A/scripts/export_csv.py"), ("03_alpha", "03/alpha/scripts/export.py"),
                        ("03_乙", "03/乙/scripts/export.py"), ("06_offline", "06/offline/scripts/export.py")]:
        results[label] = execute(active / path, payload)
    assert results["03_alpha"]["code"] != 0 and "missing_encoder" in results["03_alpha"]["stderr"]
    for label in ("03_乙", "06_offline"):
        assert json.loads(results[label]["stdout"]) == payload
    import csv
    import io
    assert list(csv.reader(io.StringIO(results["02_csv"]["stdout"]))) == [["text"], [payload]]
    results["04_render"] = execute(active / "04/render/scripts/job.py", '{"shots":[1],"captions":["hello"]}')
    assert json.loads(results["04_render"]["stdout"])["captions"] == ["hello"]
    visible = json.loads((active / "05/visibility.json").read_text())
    assert "P/skills/A" in visible["P"] and "P/skills/A" not in visible["Q"]
    assert AUDIT.skill_name(active / "05/global/A/SKILL.md") == AUDIT.skill_name(active / "05/P/skills/A/SKILL.md")
    results["05_visibility"] = {"P": visible["P"], "Q": visible["Q"],
                                "fact": "Global A and project A share a name and are both visible in P; precedence unspecified"}
    registry = json.loads((active / "06/registry.json").read_text())
    assert (active / "06" / registry["enabled_plugin"] / "SKILL.md").is_file()
    assert registry["enabled_plugin"] != registry["historical_cache"]
    assert not (active / "06" / registry["projects"][0]["path"]).exists()
    results["06_discovery"] = {"active_plugin": registry["enabled_plugin"], "excluded_cache": registry["historical_cache"],
                               "limitation": "Project unavailability is simulated by registry and absent path, not an OS permission test"}
    assert snapshot(active) == baseline, "Evidence execution modified active files"

    # User authorized this isolated exercise only. Snapshot and archive retain
    # separate dev/install entities and the original relative client link.
    base = active / "07"
    before = snapshot(base)
    backup = root / "rollback-backup/07"
    shutil.copytree(base, backup, symlinks=True)
    assert snapshot(backup) == before
    journal = {"scope": "temporary fixture 07 only; isolated archive/failure/rollback exercise",
               "snapshot": before, "backup": "rollback-backup/07", "archive": "archive/07",
               "steps": [], "restore": "Restore each original entry from backup, retaining modes and symlink text; verify baseline."}
    try:
        for relative in ("dev/skills/A", "install/A"):
            dest = root / "archive/07" / relative
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(base / relative), dest)
            journal["steps"].append("archived " + relative)
        index(base / "dev/SKILLS_INDEX.md", [])
        index(base / "install/SKILLS_INDEX.md", [])
        put(base / "dev/INSTALL_MAP.json", json.dumps({"installed_root": "../install", "mode": "independent-copy", "skills": {}}))
        (base / "client/archive-me").unlink()
        assert not list(base.rglob("SKILL.md"))
        journal["steps"].append("removed active registrations and relative client entry")
        raise RuntimeError("injected failure during client switch")
    except RuntimeError as exc:
        journal["failure"] = str(exc)
        # No intervening writer in this fixture. Restore only the affected paths.
        for relative in ("dev/skills/A", "install/A"):
            shutil.copytree(backup / relative, base / relative, symlinks=True)
        for relative in ("dev/SKILLS_INDEX.md", "install/SKILLS_INDEX.md", "dev/INSTALL_MAP.json"):
            shutil.copy2(backup / relative, base / relative)
        (base / "client/archive-me").symlink_to(os.readlink(backup / "client/archive-me"))
        assert snapshot(base) == before
        journal["steps"].append("restored original bytes, modes, index/map and relative link")
    dev = AUDIT.audit(base / "dev/skills", base / "dev/SKILLS_INDEX.md", install_map=base / "dev/INSTALL_MAP.json", check_source_records=True)
    installed = AUDIT.audit(base / "install", base / "install/SKILLS_INDEX.md", link_dirs=[base / "client"], check_source_records=True)
    assert dev["ok"] and installed["ok"], (dev, installed)
    assert json.loads(execute(base / "install/A/scripts/export.py", payload)["stdout"]) == payload
    assert snapshot(active) == baseline
    results["07"] = {"rollback": "PASS: identical baseline including installed-only change and relative link", "dev": dev, "installed": installed}
    results["scope"] = "Only generated temporary fixtures were executed or changed; semantic decisions are recorded separately by the reviewing Agent."
    put(root / "rollback-journal.json", json.dumps(journal, ensure_ascii=False, indent=2))
    # Stable paths make the evidence portable after the temporary directory expires.
    output = json.dumps(results, ensure_ascii=False, indent=2).replace(str(root), "<fixture>")
    put(root / "machine-results.json", output)
    print(output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["prepare", "verify"])
    parser.add_argument("fixture", nargs="?", type=Path)
    args = parser.parse_args()
    if args.action == "prepare":
        if args.fixture:
            parser.error("prepare creates its own new temporary directory")
        prepare()
    else:
        if not args.fixture:
            parser.error("verify requires the generated temporary directory")
        verify(args.fixture.resolve())
