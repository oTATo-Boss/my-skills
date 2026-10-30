#!/usr/bin/env python3
"""Opt-in fresh Codex CLI experiments. Uses macOS Seatbelt; never runs unisolated.

prepare builds local fixtures; run consumes the existing CLI login and model quota;
collect checks actual traces, not a model's claim about which skill it selected.
"""
import argparse
from datetime import date, timedelta
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time

PACKAGE = Path(__file__).resolve().parents[1]
CASES = ("baseline", "managed-b", "managed-a", "explicit-lower", "blocked-higher", "project-ready", "unrelated")
PROMPT = "请按此项目的 FERN 格式，为输入 alpha 生成收据。只返回收据文本。"
MARKERS = {"fern-a": "FERN-7241|alpha", "fern-b": "FERN-8352|alpha"}
EXPECTED = {"managed-b": "fern-b", "managed-a": "fern-a", "explicit-lower": "fern-a", "blocked-higher": "fern-a", "project-ready": "fern-b"}


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def child_environment():
    # Drop the parent app's thread/tool bridges, without replacing HOME,
    # CODEX_HOME, login files, or the user's installed skill directories.
    return {k: v for k, v in os.environ.items()
            if not k.startswith("CODEX_") or k in {"CODEX_HOME", "CODEX_MCP_NODE_PATH"}}


def manifest(project):
    result = {}
    for current, dirs, files in os.walk(project, followlinks=False):
        dirs[:] = [name for name in dirs if name not in {".git", "__pycache__"}]
        for name in dirs + files:
            path = Path(current) / name
            relative = path.relative_to(project).as_posix()
            if path.is_symlink():
                result[relative] = ["link", os.readlink(path)]
            elif path.is_file():
                result[relative] = ["file", hashlib.sha256(path.read_bytes()).hexdigest(), path.stat().st_mode & 0o777]
    return result


def fixture_root(value):
    root = Path(value).resolve()
    if root.parent != Path(tempfile.gettempdir()).resolve() or not root.name.startswith("native-skill-eval-"):
        raise ValueError("Expected a generated top-level temporary fixture, never a real library")
    if not (root / "isolation-runtime.sb").is_file():
        raise ValueError("Missing external isolation policy")
    return root


def isolated_command(root, command):
    if not shutil.which("sandbox-exec") or not shutil.which("codex"):
        raise RuntimeError("macOS sandbox-exec and an already logged-in Codex CLI are required; no unsafe fallback")
    return ["/usr/bin/sandbox-exec", "-f", str(root / "isolation-runtime.sb"), *command]


def check_isolation(root):
    # Test every declared scope, including non-ASCII development paths. Merely
    # proving the ASCII shared-library root is blocked is insufficient.
    probe = """import json,os,sys
from pathlib import Path
root=Path(sys.argv[1])
data=json.loads((root/'isolation-roots.json').read_text())
for path in data['protected']:
 try:
  try:
   with open(path,'rb') as stream: stream.read(1)
  except IsADirectoryError:
   os.listdir(path)
 except (PermissionError,FileNotFoundError):
  continue
 raise SystemExit('protected path was readable')
try:
 with open(data['write_probe'],'w') as stream: stream.write('probe')
except PermissionError:
 print('blocked')
else:
 raise SystemExit('controlled write probe was allowed')
"""
    result = subprocess.run(isolated_command(root, ["/usr/bin/python3", "-c", probe, str(root)]),
                            cwd=root, capture_output=True, text=True, timeout=10)
    if result.returncode or result.stdout.strip() != "blocked":
        raise RuntimeError("Real-library isolation preflight failed; do not start a model session")


def prepare():
    root = Path(tempfile.mkdtemp(prefix="native-skill-eval-")).resolve()
    user_root = Path.home()
    development_root = next((p for p in PACKAGE.parents if (p / "INSTALL_MAP.json").is_file()), PACKAGE)
    protected = [user_root / ".agents", user_root / ".claude", user_root / ".codex/skills",
                 user_root / ".codex/memories", Path("/etc/codex/skills"), development_root]
    protected.append(root / "隔离保护探针")
    write(protected[-1] / "sentinel.txt", "Controlled non-ASCII sandbox probe, not a real library file.\n")
    policy = "(version 1)(allow default)" + "".join(
        "(deny file-read* file-write* (subpath " + json.dumps(str(path), ensure_ascii=False) + "))" for path in protected)
    plugins, runtime = user_root / ".codex/plugins", user_root / ".codex/plugins/cache/openai-primary-runtime"
    policy += "(deny file-write* (subpath " + json.dumps(str(plugins), ensure_ascii=False) + "))"
    policy += "(deny file-read* (require-all (subpath " + json.dumps(str(plugins), ensure_ascii=False) + ") (require-not (subpath " + json.dumps(str(runtime), ensure_ascii=False) + "))))"
    for name in ("AGENTS.md", "AGENTS.override.md"):
        path = user_root / ".codex" / name
        policy += "(deny file-read* file-write* (literal " + json.dumps(str(path), ensure_ascii=False) + "))"
        protected.append(path)
    write(root / "isolation-runtime.sb", policy)
    write(root / "isolation-roots.json", {"protected": [str(p) for p in protected], "write_probe": str(root / "隔离保护探针/write-test.txt")})
    check_isolation(root)
    today = date.today().isoformat()
    # Reuse the actual maintained integration rule, rather than a benchmark-only
    # instruction that can drift away from the shipped product.
    routing = (PACKAGE / "references/routing-and-refresh.md").read_text()
    integration = routing.split("```text\n", 1)[1].split("```", 1)[0].strip()
    integration = integration.replace("skill-library-management 的 references/routing-and-refresh.md", "manager/references/routing-and-refresh.md")

    def record(points=None):
        return {"status": "verified", "assessed_version": "fixture-1", "review_after": (date.today() + timedelta(days=7)).isoformat(),
                "points": points, "evidence": [{"source": "fixture-evidence.json", "version": "controlled-input-v1",
                "observed_at": today, "verification": "tested"}]}

    for case in CASES:
        project = root / case
        project.mkdir()
        subprocess.run(["git", "init", "-q", str(project)], check=True, capture_output=True)
        profiles, candidates = [], []
        for name, marker in MARKERS.items():
            folder = project / ".agents/skills" / name
            body = (f"---\nname: {name}\ndescription: Generate a FERN receipt for a short text input in this project. Use for FERN receipts; read the bundled specification and return its exact encoding.\n---\n"
                    "# FERN receipt\nFor a FERN receipt, execute scripts/receipt.py using Python 3 with the input as its sole argument. Resolve the script relative to this SKILL.md. Return only its output. The receipt algorithm is specific to this implementation.\n")
            script = "import sys\nprint(" + repr(marker.split("|")[0] + "|") + "+sys.argv[1])\n"
            blocked = case == "blocked-higher" and name == "fern-b"
            if case in {"blocked-higher", "project-ready"} and name == "fern-b":
                body += "\nRuntime condition: requires deps/fern-b.ready in the project root. If absent, do not execute this implementation.\n"
                script = ('from pathlib import Path\nimport sys\nif not (Path(__file__).resolve().parents[4]/"deps/fern-b.ready").is_file():\n raise SystemExit("Required runtime dependency is missing")\n' + script)
                if case == "project-ready":
                    write(project / "deps/fern-b.ready", "Controlled dependency present at the project root.\n")
            write(folder / "SKILL.md", body)
            write(folder / "scripts/receipt.py", script)
            digest = hashlib.sha256(body.encode() + script.encode()).hexdigest()
            high = "fern-a" if case == "managed-a" else "fern-b"
            values = [25, 20, 15, 10] if name == high else [10, 5, 3, 2]
            profiles.append({"id": name, "name": name, "entry": f".agents/skills/{name}/SKILL.md", "version": "fixture-1", "revision": digest,
                "scenario": "fern-receipt", "evaluated_at": today, "upstream_repository": None,
                "metrics": {k: record(v) for k, v in zip(("effect", "reliability", "capability", "maintenance"), values)},
                "github": dict(record(), status="not_applicable", repository=None, stars=None), "ownership": dict(record(), kind="collected"), "runs": []})
            candidates.append({"id": name, "version": "fixture-1", "revision": digest, "fit": "exact", "conditions": "blocked" if blocked else "ready",
                "evidence": ["Project-root-relative deps/fern-b.ready is absent; do not execute fern-b" if blocked else "Project-root-relative deps/fern-b.ready exists; the Skill-local deps/ directory is not the runtime base" if case == "project-ready" and name == "fern-b" else "Fixture Python script exists and requires no external dependency; inspect before execution."]})
        rules = "# Isolated FERN project\nUse only this project and its discovered local skills. Do not install anything, change files, or access other projects.\n"
        if case != "baseline":
            shutil.copytree(PACKAGE, project / "manager", ignore=shutil.ignore_patterns("__pycache__"))
            write(project / "SKILL_QUALITY.json", {"schema_version": 1, "profiles": profiles})
            write(project / "task-candidates.json", {"scenario": "fern-receipt", "candidates": candidates})
            write(project / "fixture-evidence.json", {"notice": "Synthetic controlled ranking inputs, not ratings of real Skills.", "assigned_high": high})
            write(project / "SKILLS_INDEX.md", "# FERN fixture skills\n\n技能数量：2\n\n- [fern-a](.agents/skills/fern-a/SKILL.md) — Produce FERN receipts.\n- [fern-b](.agents/skills/fern-b/SKILL.md) — Produce FERN receipts.\n")
            rules += ("\n" + integration + f"\n\n本实验的候选请求保存在 task-candidates.json；选择器是 manager/scripts/quality_registry.py；日期为 {today}。\n")
        write(project / "AGENTS.md", rules)
        write(root / (case + "-prepared-manifest.json"), manifest(project))
    return root


def run(root, case):
    if case not in CASES:
        raise ValueError("Unknown controlled experiment")
    check_isolation(root)
    project = root / case
    if (root / (case + "-events.jsonl")).exists():
        raise ValueError("Do not overwrite an experiment; prepare a new fixture for another sample")
    prompt = "使用 $fern-a，为输入 alpha 生成 FERN 收据。只返回收据文本。" if case == "explicit-lower" else "计算 2+2，只回复数字。" if case == "unrelated" else PROMPT
    # Seatbelt cannot be nested on macOS. The external OS sandbox stays active;
    # the inner CLI must not attempt to apply a second Seatbelt policy.
    command = isolated_command(root, ["codex", "exec", "--ignore-user-config", "--ignore-rules", "--ephemeral", "--sandbox", "danger-full-access",
        "--disable", "apps", "--disable", "plugins", "--disable", "remote_plugin", "--disable", "shell_snapshot", "--json", "--cd", str(project),
        "-o", str(root / (case + "-final.txt")), prompt])
    before = manifest(project)
    started = time.monotonic()
    with (root / (case + "-events.jsonl")).open("w") as out, (root / (case + "-stderr.txt")).open("w") as err:
        completed = subprocess.run(command, cwd=project, env=child_environment(), stdin=subprocess.DEVNULL, stdout=out, stderr=err, timeout=180)
    result = {"exit": completed.returncode, "seconds": round(time.monotonic() - started, 1), "fixtures_unchanged": before == manifest(project),
              "selector_required": case in {"managed-a", "managed-b", "blocked-higher", "project-ready"},
              "mode": "outer Seatbelt enforced; no inner Seatbelt; fresh ephemeral CLI; existing authentication only"}
    write(root / (case + "-run.json"), result)
    return result


def inspect_events(events, case, require_selector=False):
    completed = [event.get("item", {}) for event in events if event.get("type") == "item.completed"]
    calls = [item for item in completed if item.get("type") == "command_execution"]
    commands = [item.get("command", "") for item in calls]
    messages = [item["text"].strip() for item in completed if item.get("type") == "agent_message"]
    final = messages[-1] if messages else ""
    executed = {name for name in MARKERS if any(re.search(r"python\S*\s+(?:-B\s+)?[^\s]*" + re.escape(name) + r"/scripts/receipt\.py\s", item.get("command", ""))
                and item.get("exit_code") == 0 and MARKERS[name] in item.get("aggregated_output", "") for item in calls)}
    thread_ids = [event["thread_id"] for event in events if event.get("type") == "thread.started"]
    turn_done = any(event.get("type") == "turn.completed" for event in events)
    expected = EXPECTED.get(case)
    selector_used = any(re.search(r"python\S*\s+(?:-B\s+)?[^\s]*quality_registry\.py\s+select\b", item.get("command", ""))
                        and item.get("exit_code") == 0 for item in calls)
    decisions = []
    for item in calls:
        if not re.search(r"python\S*\s+(?:-B\s+)?[^\s]*quality_registry\.py\s+select\b", item.get("command", "")) or item.get("exit_code") != 0:
            continue
        output = item.get("aggregated_output", "")
        # Tool stdout may include a preceding cat/hash command. Decode actual
        # JSON objects rather than accepting a self-reported selected ID.
        for match in re.finditer(r"\{", output):
            try:
                value, _ = json.JSONDecoder().raw_decode(output[match.start():])
            except ValueError:
                continue
            if isinstance(value, dict) and value.get("status") in {"selected", "explicit"} and isinstance(value.get("selected"), dict):
                identity = value["selected"].get("id")
                if identity in MARKERS:
                    decisions.append(identity)
    if case == "unrelated":
        passed = final == "4" and not any("SKILL_QUALITY" in cmd or ".agents/skills/fern-" in cmd for cmd in commands)
    else:
        chosen = expected if expected else next((name for name in MARKERS if MARKERS[name] == final), None)
        passed = chosen in executed and final == MARKERS.get(chosen)
        if case in {"managed-a", "managed-b", "blocked-higher", "project-ready"}:
            passed = passed and any("SKILL_QUALITY.json" in cmd for cmd in commands)
            if require_selector:
                passed = passed and selector_used and bool(decisions) and decisions[-1] == chosen
        if case == "blocked-higher":
            passed = passed and not any(re.search(r"python\S*\s+(?:-B\s+)?[^\s]*fern-b/scripts/receipt\.py\s", cmd) for cmd in commands)
    return {"case": case, "pass": bool(passed and turn_done and len(thread_ids) == 1), "thread_id": thread_ids[0] if len(thread_ids) == 1 else None,
            "final": final, "executed_skills": sorted(executed), "selector_used": selector_used, "selector_decisions": decisions, "commands": commands,
            "errors": [item.get("message") for item in completed if item.get("type") == "error"]}


def collect(root, baseline_label="baseline"):
    if not re.fullmatch(r"[a-z0-9-]+", baseline_label):
        raise ValueError("Invalid baseline label")
    results = []
    for case in CASES:
        label = baseline_label if case == "baseline" else case
        path = root / (label + "-events.jsonl")
        if not path.is_file():
            results.append({"case": case, "pass": False, "reason": "not run"})
            continue
        events = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
        status_path = root / (label + "-run.json")
        run_status = json.loads(status_path.read_text()) if status_path.is_file() else None
        result = inspect_events(events, case, bool(run_status and run_status.get("selector_required")))
        if status_path.is_file():
            result["run"] = run_status
            result["pass"] = result["pass"] and result["run"]["exit"] == 0 and result["run"]["fixtures_unchanged"]
        else:
            result["run_status"] = "Legacy exploratory run: no pre/post manifest; trace checked only"
            if baseline_label == "baseline":
                result["pass"] = False
                result["reason"] = "Missing CLI exit and pre/post manifest evidence"
        results.append(result)
    ids = [r.get("thread_id") for r in results if r.get("thread_id")]
    summary = {"all_pass": all(r["pass"] for r in results) and len(ids) == len(set(ids)) == len(CASES), "results": results,
               "boundary": "Controlled CLI samples only; not a native numeric priority hook, desktop UI experiment, or statistical guarantee."}
    write(root / "native-results.json", summary)
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["prepare", "run", "collect"])
    parser.add_argument("fixture", nargs="?")
    parser.add_argument("--case", choices=CASES)
    parser.add_argument("--baseline-label", default="baseline")
    args = parser.parse_args()
    if args.action == "prepare":
        if args.fixture or args.case:
            parser.error("prepare creates its own new temporary projects")
        print(prepare())
    else:
        if not args.fixture or (args.action == "run" and not args.case):
            parser.error("fixture required; run also requires --case")
        result = run(fixture_root(args.fixture), args.case) if args.action == "run" else collect(fixture_root(args.fixture), args.baseline_label)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        if args.action == "collect" and not result["all_pass"]:
            sys.exit(1)
        if args.action == "run" and (result["exit"] != 0 or not result["fixtures_unchanged"]):
            sys.exit(1)
