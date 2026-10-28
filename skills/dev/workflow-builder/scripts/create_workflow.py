#!/usr/bin/env python3
"""Generate a self-contained workflow project; never installs or marks it ready."""
from pathlib import Path
import argparse
import json
import importlib.metadata
import re
import shutil
import sys
import tempfile


def object_schema(properties):
    return {"type": "object", "properties": properties, "required": list(properties), "additionalProperties": False}


def example(name):
    inputs = object_schema({"title": {"type": "string", "minLength": 1},
                            "notes": {"type": "array", "minItems": 1, "items": {"type": "string", "minLength": 1}}})
    material = object_schema({"title": {"type": "string", "minLength": 1},
                              "notes": {"type": "array", "minItems": 1, "items": {"type": "string"}}})
    report = object_schema({"report": {"type": "string", "minLength": 1},
                            "note_count": {"type": "integer", "minimum": 1}})
    policy = {"max_attempts": 2, "timeout_seconds": 30,
              "retry_on": ["executor_failed", "timeout"], "automatic": True}
    return {"schema_version": 1, "workflow_id": name, "revision": "1",
            "goal": "Turn user-supplied notes into a verified Markdown report",
            "runtime": {"adapter": "json-subprocess-posix", "version": "0.1.0"},
            "trigger": "manual", "inputs": inputs,
            "outputs": {"report": {"step": "render", "pointer": "/report"},
                        "note_count": {"step": "render", "pointer": "/note_count"}},
            "resources": {}, "rules": ["workflow-rules.md"],
            "steps": [
                {"id": "prepare", "depends_on": [],
                 "inputs": {"title": {"input": "/title"}, "notes": {"input": "/notes"}},
                 "executor": {"kind": "script", "command": ["{python}", "scripts/report.py", "prepare"]},
                 "outputs": material, "completion": {"schema": material},
                 "failure": policy, "recovery": {"mode": "pure"}},
                {"id": "render", "depends_on": ["prepare"],
                 "inputs": {"material": {"step": "prepare", "pointer": ""}},
                 "executor": {"kind": "script", "command": ["{python}", "scripts/report.py", "render"]},
                 "outputs": report, "completion": {"artifacts": [{"pointer": "/report", "format": "text", "contains": ["# ", "- "]}]},
                 "failure": policy, "recovery": {"mode": "idempotent"}}],
            "acceptance": {"schema": report, "artifacts": [{"pointer": "/report", "format": "text", "contains": ["# ", "- "]}]}}


def create(path, name, spec=None):
    if not re.fullmatch(r"[a-z][a-z0-9_-]{0,63}", name):
        raise ValueError("Name must be a lowercase workflow ID (1-64 characters)")
    if path.exists():
        raise ValueError("Destination exists; refusing to overwrite")
    source = Path(__file__).resolve().parent.parent / "assets/project"
    path.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=".workflow-", dir=path.parent))
    try:
        shutil.copytree(source, stage, dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        if spec:
            shutil.copy2(spec, stage / "workflow.yaml")
        else:
            # JSON is a YAML subset; PyYAML also accepts user-written YAML.
            (stage / "workflow.yaml").write_text(json.dumps(example(name), ensure_ascii=False, indent=2) + "\n")
            (stage / "example-input.json").write_text(json.dumps({"title": "Project notes", "notes": ["Confirm goals", "Verify independent execution"]}, indent=2) + "\n")
        resolved = {}
        for package in ["PyYAML", "jsonschema"]:
            try:
                resolved[package] = importlib.metadata.version(package)
            except importlib.metadata.PackageNotFoundError:
                pass
        lock = {"runtime": {"version": "0.1.0", "adapter": "json-subprocess-posix"},
                "declared_requirements": ["PyYAML>=6.0,<7", "jsonschema>=4.18,<5"],
                "generator_environment_packages": resolved, "resources": []}
        (stage / "resources.lock.json").write_text(json.dumps(lock, indent=2) + "\n")
        (stage / "validation.md").write_text("# Validation\n\nStatus: generated. No independent acceptance suite has run for this project.\n")
        (stage / ".gitignore").write_text("runs/\noutputs/\n.venv/\n__pycache__/\n.env\n.env.*\n")
        # A real project-specific test is required; don't ship a false ready certificate.
        (stage / "tests").mkdir()
        (stage / "tests/acceptance-plan.md").write_text("# Required acceptance\n\nFresh-process normal run; controlled failure; bounded retry and exhaustion; interruption and resume; final artifact rejection; repeat run. Add scheduler evidence if needed.\n")
        stage.rename(path)
    finally:
        if stage.exists():
            shutil.rmtree(stage)
    return {"ok": True, "path": str(path), "status": "generated", "runtime": "json-subprocess-posix"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path", type=Path, required=True, help="New project directory; never overwritten")
    parser.add_argument("--name", required=True)
    parser.add_argument("--spec", type=Path, help="Optional existing workflow.yaml to copy; resources must be supplied separately")
    args = parser.parse_args()
    try:
        print(json.dumps(create(args.path.resolve(), args.name, args.spec)))
        return 0
    except (OSError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
