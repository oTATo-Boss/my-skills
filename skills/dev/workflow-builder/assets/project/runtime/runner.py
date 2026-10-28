#!/usr/bin/env python3
"""Portable workflow runtime. JSON subprocess protocol; no Builder dependency."""
from __future__ import annotations

import argparse
import copy
import datetime as dt
import fcntl
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import re
import signal
import shutil
import subprocess
import sys
import tempfile
import time
import uuid

try:
    import yaml
    from jsonschema import Draft202012Validator
    from jsonschema.exceptions import SchemaError
except ImportError as exc:
    print(json.dumps({"ok": False, "error": "dependency_missing", "message": str(exc),
                      "hint": "Install runtime/requirements.txt using this Python interpreter"}))
    raise SystemExit(2)

VERSION = "0.1.0"
ID = re.compile(r"^[a-z][a-z0-9_-]{0,63}$")


class Fault(Exception):
    def __init__(self, code, message, *, retryable=False):
        super().__init__(message)
        self.code, self.message, self.retryable = code, str(message), retryable

    def record(self):
        return {"code": self.code, "message": self.message, "retryable": self.retryable}


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     allow_nan=False).encode()).hexdigest()


def file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def environment():
    return {"python": sys.version.split()[0], "PyYAML": importlib.metadata.version("PyYAML"),
            "jsonschema": importlib.metadata.version("jsonschema")}


def atomic(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=".state-", dir=path.parent)
    try:
        with os.fdopen(fd, "w") as out:
            json.dump(data, out, ensure_ascii=False, indent=2, allow_nan=False)
            out.write("\n")
            out.flush()
            os.fsync(out.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def contained(root, value):
    path = (root / value).resolve()
    if not path.is_relative_to(root.resolve()):
        raise Fault("path_escape", f"Path must stay inside {root}: {value}")
    return path


def json_schema(data, schema, label):
    errors = sorted(Draft202012Validator(schema).iter_errors(data), key=lambda e: str(e.path))
    if errors:
        e = errors[0]
        raise Fault("validation_failed", f"{label} at /{'/'.join(map(str, e.path))}: {e.message}",
                    retryable=True)


def check_schema(schema):
    Draft202012Validator.check_schema(schema)
    def walk(value):
        if isinstance(value, dict):
            if "$ref" in value:
                ref = value["$ref"]
                if ref != "#" and not ref.startswith("#/"):
                    raise Fault("definition_invalid", "Only local JSON pointer Schema references are supported")
                try:
                    pointer(schema, ref[1:])
                except Fault as exc:
                    raise Fault("definition_invalid", f"Unresolved schema reference {ref}") from exc
            for item in value.values():
                walk(item)
        elif isinstance(value, list):
            for item in value:
                walk(item)
    walk(schema)


def pointer(data, path):
    if not path:
        return data
    if not path.startswith("/"):
        raise Fault("binding_invalid", f"Expected JSON pointer, got {path}")
    try:
        for part in path[1:].split("/"):
            part = part.replace("~1", "/").replace("~0", "~")
            data = data[int(part)] if isinstance(data, list) else data[part]
        return data
    except (KeyError, IndexError, ValueError, TypeError) as exc:
        raise Fault("binding_missing", f"Unresolved pointer {path}") from exc


class Runtime:
    def __init__(self, project):
        self.root = project.resolve()
        try:
            self.spec = yaml.safe_load((self.root / "workflow.yaml").read_text())
            json.dumps(self.spec, allow_nan=False)
            self.schema = json.loads((self.root / "runtime/workflow.schema.json").read_text())
            Draft202012Validator.check_schema(self.schema)
            json_schema(self.spec, self.schema, "workflow")
        except (OSError, ValueError, TypeError, yaml.YAMLError) as exc:
            raise Fault("definition_invalid", str(exc)) from exc
        self.steps = {s["id"]: s for s in self.spec["steps"]}
        if len(self.steps) != len(self.spec["steps"]):
            raise Fault("definition_invalid", "Duplicate step IDs")
        self.order = []
        pending = set(self.steps)
        while pending:
            wave = [s for s in self.steps if s in pending and
                    set(self.steps[s]["depends_on"]) <= set(self.order)]
            if not wave:
                raise Fault("definition_invalid", "Cycle or missing dependency")
            self.order.extend(wave)
            pending.difference_update(wave)
        self.resources = self.spec.get("resources", {})
        for step in self.steps.values():
            for resource in step["executor"].get("resources", []):
                if resource not in self.resources:
                    raise Fault("definition_invalid", f"Unknown resource {resource}")
            ancestors = self.ancestors(step["id"])
            for binding in step["inputs"].values():
                if "step" in binding and binding["step"] not in ancestors:
                    raise Fault("definition_invalid", f"{step['id']} reads a non-ancestor")
            check_schema(step["outputs"])
        check_schema(self.spec["inputs"])
        for binding in self.spec["outputs"].values():
            if "step" in binding and binding["step"] not in self.steps:
                raise Fault("definition_invalid", "Unknown workflow output step")
        for checks in [self.spec["acceptance"], *[s["completion"] for s in self.steps.values()]]:
            if "schema" in checks:
                check_schema(checks["schema"])
            for artifact in checks.get("artifacts", []):
                if "schema" in artifact:
                    check_schema(artifact["schema"])

    def ancestors(self, step_id):
        found, todo = set(), list(self.steps[step_id]["depends_on"])
        while todo:
            item = todo.pop()
            if item not in found:
                found.add(item)
                todo.extend(self.steps[item]["depends_on"])
        return found

    def fingerprint(self):
        """Bind checkpoints to all project source, rules, schema and resource lock."""
        files = {}
        paths = {self.root / "workflow.yaml", self.root / "resources.lock.json"}
        for directory in ["runtime", "scripts", "agents"]:
            if (self.root / directory).is_dir():
                paths.update((self.root / directory).rglob("*"))
        paths.update(contained(self.root, p) for p in self.spec["rules"])
        commands = []
        for step in self.steps.values():
            commands.append(step["executor"]["command"])
            paths.update(contained(self.root, p) for p in step["executor"].get("instructions", []))
            if "command" in step["completion"]:
                commands.append(step["completion"]["command"])
        if "command" in self.spec["acceptance"]:
            commands.append(self.spec["acceptance"]["command"])
        commands.extend(r["probe"] for r in self.resources.values() if "probe" in r)
        for command in commands:
            for token in command:
                candidate = self.root / token
                if candidate.is_file() and candidate.resolve().is_relative_to(self.root):
                    paths.add(candidate)
        for p in sorted(paths):
            relative = p.relative_to(self.root)
            if any(x in {"runs", "outputs", ".git", ".venv", "venv", "__pycache__",
                         ".pytest_cache", "node_modules"} for x in relative.parts):
                continue
            if p.name.startswith(".env"):
                continue
            if p.is_file():
                if p.is_symlink() and not p.resolve().is_relative_to(self.root):
                    raise Fault("dependency_unpinned", f"Source symlink leaves project: {relative}")
                files[str(relative)] = file_hash(p)
        external = {}
        for rid, resource in self.resources.items():
            for name in resource.get("paths", []):
                p = Path(os.path.expandvars(os.path.expanduser(name)))
                p = p if p.is_absolute() else self.root / p
                if p.is_file():
                    external[f"{rid}:{name}"] = file_hash(p)
        return digest({"definition": self.spec, "files": files, "external": external,
                       "environment": environment()})

    def argv(self, command):
        return [sys.executable if part == "{python}" else part for part in command]

    def call(self, command, envelope, timeout, log=None, on_start=None):
        """No shell. Each executor gets its own process group for timeout/interrupt cleanup."""
        try:
            process = subprocess.Popen(self.argv(command), cwd=self.root, stdin=subprocess.PIPE,
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                       text=True, start_new_session=True)
        except OSError as exc:
            raise Fault("executor_unavailable", str(exc)) from exc
        if on_start:
            on_start(process.pid)
        try:
            stdout, stderr = process.communicate(json.dumps(envelope, ensure_ascii=False), timeout=timeout)
        except (subprocess.TimeoutExpired, KeyboardInterrupt) as exc:
            os.killpg(process.pid, signal.SIGTERM)
            try:
                stdout, stderr = process.communicate(timeout=2)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                stdout, stderr = process.communicate()
            if log:
                log.with_suffix(".stdout").write_text(stdout)
                log.with_suffix(".stderr").write_text(stderr)
            if isinstance(exc, KeyboardInterrupt):
                raise
            raise Fault("timeout", f"Executor exceeded {timeout}s", retryable=True) from exc
        if log:
            log.with_suffix(".stdout").write_text(stdout)
            log.with_suffix(".stderr").write_text(stderr)
        if process.returncode:
            raise Fault("executor_failed", f"Executor exited {process.returncode}; see attempt logs",
                        retryable=True)
        try:
            result = json.loads(stdout)
            if not isinstance(result, dict):
                raise ValueError("expected JSON object")
            return result
        except ValueError as exc:
            raise Fault("invalid_output", f"Executor stdout is not a JSON object: {exc}",
                        retryable=True) from exc

    def check(self):
        evidence, errors = {}, []
        commands = [s["executor"]["command"] for s in self.steps.values()]
        commands += [s["completion"]["command"] for s in self.steps.values() if "command" in s["completion"]]
        if "command" in self.spec["acceptance"]:
            commands.append(self.spec["acceptance"]["command"])
        for command in commands:
            argv = self.argv(command)
            executable = argv[0]
            found = (self.root / executable).is_file() if "/" in executable else shutil.which(executable)
            if not found:
                errors.append({"code": "executor_unavailable", "message": executable})
            if command[0] == "{python}" and len(command) > 1 and command[1].endswith(".py"):
                if not (self.root / command[1]).is_file():
                    errors.append({"code": "executor_unavailable", "message": command[1]})
        for path in self.spec["rules"]:
            try:
                p = contained(self.root, path)
                if not p.is_file():
                    raise Fault("rules_missing", path)
            except Fault as exc:
                errors.append(exc.record())
        for step in self.steps.values():
            for path in step["executor"].get("instructions", []):
                try:
                    if not contained(self.root, path).is_file():
                        raise Fault("instructions_missing", path)
                except Fault as exc:
                    errors.append(exc.record())
        used = {r for s in self.steps.values() for r in s["executor"].get("resources", [])}
        for rid in sorted(used):
            r = self.resources[rid]
            missing = [name for name in r.get("required_env", []) if not os.environ.get(name)]
            paths = []
            for name in r.get("paths", []):
                p = Path(os.path.expandvars(os.path.expanduser(name)))
                p = p if p.is_absolute() else self.root / p
                if not p.is_file():
                    missing.append(name)
                else:
                    paths.append({"path": name, "sha256": file_hash(p)})
            evidence[rid] = {"paths": paths, "missing": missing,
                             "status": "blocked" if missing else "declared_checks_passed"}
            if missing:
                errors.append({"code": "resource_missing", "message": f"{rid}: {', '.join(missing)}"})
            elif "probe" in r:
                try:
                    probe = self.call(r["probe"], {"operation": "probe", "resource_id": rid},
                                      r.get("timeout_seconds", 15))
                    if probe.get("ok") is not True:
                        raise Fault("probe_failed", f"Probe rejected {rid}")
                    evidence[rid]["status"] = "probe_passed"
                    evidence[rid].update(checked_at=now(), result_hash=digest(probe))
                except Fault as exc:
                    errors.append(exc.record())
                    evidence[rid]["status"] = "blocked"
        return {"ok": not errors, "runtime_version": VERSION, "environment": environment(),
                "capabilities": {"script": True, "agent_json_subprocess": True,
                                 "persistent_state": True, "timeout": True, "retry": True,
                                 "resume": True, "parallel": False, "scheduler": False,
                                 "native_client_adapter": False},
                "resources": evidence, "errors": errors}

    def bind(self, bindings, state):
        values = {}
        for name, binding in bindings.items():
            if "value" in binding:
                values[name] = copy.deepcopy(binding["value"])
            elif "input" in binding:
                values[name] = pointer(state["inputs"], binding["input"])
            else:
                values[name] = pointer(state["steps"][binding["step"]]["outputs"], binding["pointer"])
        return values

    def validate_outputs(self, checks, outputs, envelope):
        if "schema" in checks:
            json_schema(outputs, checks["schema"], "acceptance")
        artifacts = []
        for item in checks.get("artifacts", []):
            value = pointer(outputs, item["pointer"])
            if not isinstance(value, str):
                raise Fault("validation_failed", "Artifact pointer must resolve to a path", retryable=True)
            p = contained(Path(envelope["output_dir"]), value)
            if not p.is_file() or p.stat().st_size < item.get("min_bytes", 1):
                raise Fault("validation_failed", f"Missing or empty artifact: {value}", retryable=True)
            if item.get("format") == "json":
                try:
                    data = json.loads(p.read_text())
                except (ValueError, UnicodeError) as exc:
                    raise Fault("validation_failed", f"Invalid JSON artifact: {value}", retryable=True) from exc
                if "schema" in item:
                    json_schema(data, item["schema"], value)
            if item.get("contains"):
                try:
                    content = p.read_text()
                except UnicodeError as exc:
                    raise Fault("validation_failed", f"Artifact is not UTF-8 text: {value}", retryable=True) from exc
                if any(text not in content for text in item["contains"]):
                    raise Fault("validation_failed", f"Artifact missing required content: {value}", retryable=True)
            artifacts.append({"path": str(p.relative_to(self.root)), "sha256": file_hash(p)})
        if "command" in checks:
            result = self.call(checks["command"], {**envelope, "outputs": outputs,
                                                  "operation": "validate"}, checks.get("timeout_seconds", 30))
            if result.get("ok") is not True:
                raise Fault("validation_failed", "Custom validator did not return ok:true", retryable=True)
            for artifact in artifacts:
                p = contained(self.root, artifact["path"])
                if not p.is_file() or file_hash(p) != artifact["sha256"]:
                    raise Fault("validation_failed", "Validator modified a checked artifact", retryable=True)
        return artifacts

    def envelope(self, state, step_id=None):
        return {"protocol_version": 1, "workflow_id": self.spec["workflow_id"],
                "run_id": state["run_id"], "step_id": step_id,
                "project_dir": str(self.root), "output_dir": str(self.root / "outputs" / state["run_id"]),
                "rules": [{"path": p, "text": contained(self.root, p).read_text()} for p in self.spec["rules"]]}

    def save(self, state, event):
        state["updated_at"] = now()
        directory = self.root / "runs" / state["run_id"]
        atomic(directory / "state.json", state)
        with (directory / "events.jsonl").open("a") as out:
            out.write(json.dumps({"at": now(), **event}, ensure_ascii=False) + "\n")
            out.flush()
            os.fsync(out.fileno())

    def load(self, run_id):
        if not ID.fullmatch(run_id):
            raise Fault("run_id_invalid", run_id)
        try:
            state = json.loads((self.root / "runs" / run_id / "state.json").read_text())
            if not isinstance(state, dict) or state.get("run_id") != run_id:
                raise Fault("state_invalid", "Run ID does not match persisted state")
            return state
        except (OSError, ValueError) as exc:
            raise Fault("run_missing", run_id) from exc

    def lock(self, run_id):
        directory = self.root / "runs" / run_id
        directory.mkdir(parents=True, exist_ok=True)
        handle = (directory / "lock").open("a")
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            handle.close()
            raise Fault("run_busy", "Run is owned by another live executor") from exc
        return handle

    def ensure_checkpoint(self, state):
        if state["fingerprint"] != self.fingerprint() or digest(state["inputs"]) != state["input_hash"]:
            raise Fault("checkpoint_mismatch", "Definition, source, resources or inputs changed; start a new run")
        for sid, record in state["steps"].items():
            if record["status"] != "passed":
                continue
            json_schema(record["outputs"], self.steps[sid]["outputs"], f"checkpoint {sid}")
            if digest(record["outputs"]) != record.get("output_hash"):
                raise Fault("checkpoint_mismatch", f"Checkpoint outputs changed: {sid}")
            for item in record.get("artifacts", []):
                p = contained(self.root, item["path"])
                if not p.is_file() or file_hash(p) != item["sha256"]:
                    raise Fault("checkpoint_mismatch", f"Artifact changed: {item['path']}; start a new run")

    def execute(self, *, inputs=None, run_id=None, operation="run", selected=None, pause_after=None):
        run_id = run_id or "r" + uuid.uuid4().hex[:20]
        if not ID.fullmatch(run_id):
            raise Fault("run_id_invalid", run_id)
        with self.lock(run_id):
            state_path = self.root / "runs" / run_id / "state.json"
            if operation == "run":
                if state_path.exists():
                    raise Fault("run_exists", "Use a new run ID or resume")
                json_schema(inputs, self.spec["inputs"], "inputs")
                state = {"run_id": run_id, "workflow_revision": self.spec["revision"],
                         "runtime_version": VERSION, "environment": environment(), "fingerprint": self.fingerprint(),
                         "inputs": inputs, "input_hash": digest(inputs), "started_at": now(),
                         "status": "pending", "steps": {sid: {"status": "pending", "attempts": []}
                                                         for sid in self.order}}
                self.save(state, {"event": "created"})
            else:
                state = self.load(run_id)
                self.ensure_checkpoint(state)
                if state["status"] == "succeeded":
                    return state
                for sid, record in state["steps"].items():
                    if record["status"] in {"running", "interrupted"}:
                        pid = record["attempts"][-1].get("pid") if record["attempts"] else None
                        if pid:
                            try:
                                os.kill(pid, 0)
                            except ProcessLookupError:
                                pass
                            else:
                                raise Fault("executor_still_running", f"Step {sid} executor PID {pid} still exists; reconcile before resume")
                        record["status"] = "interrupted"
                        if record["attempts"]:
                            record["attempts"][-1].update(status="interrupted", ended_at=now())
                        if self.steps[sid]["recovery"]["mode"] == "manual":
                            record["status"] = "blocked"
                            state["status"] = "blocked"
                            state["error"] = {"code": "outcome_unknown", "message":
                                              f"Reconcile external effect for {sid}; start a new run after reconciliation"}
                            record["error"] = state["error"]
                            self.save(state, {"event": "outcome_unknown", "step": sid})
                            return state
                if operation == "retry":
                    if selected not in self.steps:
                        raise Fault("step_missing", str(selected))
                    record = state["steps"][selected]
                    if record["status"] != "failed" or not record.get("error", {}).get("retryable"):
                        raise Fault("retry_not_allowed", "Only a retryable failed step can be retried")
                    if len(record["attempts"]) >= self.steps[selected]["failure"]["max_attempts"]:
                        raise Fault("retry_exhausted", "Attempt budget is exhausted; revise definition and start a new run")
                    record["status"] = "pending"
                elif any(r["status"] == "failed" for r in state["steps"].values()):
                    raise Fault("retry_required", "Use retry --step for a failed run")
            preflight = self.check()
            state["preflight"] = preflight
            if not preflight["ok"]:
                state.update(status="blocked", error={"code": "preflight_failed", "message": preflight["errors"]})
                self.save(state, {"event": "blocked"})
                return state
            state.update(status="running")
            state.pop("error", None)
            (self.root / "outputs" / run_id).mkdir(parents=True, exist_ok=True)
            self.save(state, {"event": "started", "operation": operation})
            active = None
            try:
                for sid in self.order:
                    active = sid
                    step, record = self.steps[sid], state["steps"][sid]
                    if record["status"] == "passed":
                        continue
                    if any(state["steps"][d]["status"] != "passed" for d in step["depends_on"]):
                        record["status"] = "blocked"
                        continue
                    if record["status"] == "blocked" and record.get("error", {}).get("code") == "outcome_unknown":
                        state.update(status="blocked", error=record["error"])
                        self.save(state, {"event": "outcome_unknown", "step": sid})
                        return state
                    record["status"] = "ready"
                    self.save(state, {"event": "ready", "step": sid})
                    if not self.run_step(state, step, record):
                        for later in self.order:
                            if sid in self.ancestors(later) and state["steps"][later]["status"] != "passed":
                                state["steps"][later]["status"] = "blocked"
                        self.save(state, {"event": "stopped", "step": sid})
                        return state
                    if sid == pause_after:
                        state["status"] = "interrupted"
                        self.save(state, {"event": "checkpoint_pause", "step": sid})
                        return state
                outputs = self.bind(self.spec["outputs"], state)
                env = self.envelope(state)
                artifacts = self.validate_outputs(self.spec["acceptance"], outputs, env)
                state.update(status="succeeded", outputs=outputs,
                             acceptance={"passed": True, "at": now(), "artifacts": artifacts})
                self.save(state, {"event": "succeeded"})
            except KeyboardInterrupt:
                if active and state["steps"][active]["status"] == "running":
                    state["steps"][active]["status"] = "interrupted"
                    state["steps"][active]["attempts"][-1].update(status="interrupted", ended_at=now())
                state["status"] = "interrupted"
                self.save(state, {"event": "interrupted"})
            except (Fault, OSError, ValueError) as exc:
                if not isinstance(exc, Fault):
                    exc = Fault("runtime_io_error", str(exc))
                state.update(status="failed", error=exc.record(), acceptance={"passed": False})
                self.save(state, {"event": "failed", "error": exc.record()})
            return state

    def run_step(self, state, step, record):
        policy = step["failure"]
        while len(record["attempts"]) < policy["max_attempts"]:
            attempt = {"attempt_id": len(record["attempts"]) + 1, "status": "running", "started_at": now()}
            record["attempts"].append(attempt)
            record["status"] = "running"
            self.save(state, {"event": "attempt_started", "step": step["id"], "attempt": attempt["attempt_id"]})
            log = self.root / "runs" / state["run_id"] / f"{step['id']}-{attempt['attempt_id']}"
            try:
                env = self.envelope(state, step["id"])
                env.update(inputs=self.bind(step["inputs"], state), attempt=attempt["attempt_id"],
                           idempotency_key=f"{state['run_id']}:{step['id']}")
                env["resources"] = {}
                if step["executor"]["kind"] == "agent":
                    env["agent"] = {"role": step["executor"]["role"], "instructions": [
                        {"path": p, "text": contained(self.root, p).read_text()}
                        for p in step["executor"].get("instructions", [])]}
                for rid in step["executor"].get("resources", []):
                    resource = self.resources[rid]
                    if resource["kind"] == "skill":
                        texts = []
                        for name in resource.get("paths", []):
                            path = Path(os.path.expandvars(os.path.expanduser(name)))
                            path = path if path.is_absolute() else self.root / path
                            texts.append({"path": str(path), "text": path.read_text()})
                        env["resources"][rid] = {"kind": "skill", "documents": texts}
                    else:
                        env["resources"][rid] = {"kind": resource["kind"], "required_env": resource.get("required_env", [])}
                def started(pid):
                    attempt["pid"] = pid
                    self.save(state, {"event": "executor_started", "step": step["id"], "pid": pid})
                outputs = self.call(step["executor"]["command"], env, policy["timeout_seconds"], log, started)
                json_schema(outputs, step["outputs"], step["id"])
                artifacts = self.validate_outputs(step["completion"], outputs, env)
                record.update(status="passed", outputs=outputs, output_hash=digest(outputs), artifacts=artifacts)
                record.pop("error", None)
                attempt.update(status="passed", ended_at=now())
                self.save(state, {"event": "passed", "step": step["id"]})
                return True
            except (Fault, OSError, ValueError) as exc:
                if not isinstance(exc, Fault):
                    exc = Fault("executor_io_error", str(exc))
                # Writes with unknown outcomes never automatically replay.
                safe = step["recovery"]["mode"] != "manual"
                retryable = safe and exc.retryable and exc.code in policy["retry_on"]
                error = {**exc.record(), "retryable": retryable}
                attempt.update(status="failed", ended_at=now(), error=error)
                record.update(status="failed", error=error)
                self.save(state, {"event": "attempt_failed", "step": step["id"], "error": error})
                if not retryable or not policy.get("automatic", True):
                    break
                if len(record["attempts"]) < policy["max_attempts"]:
                    time.sleep(policy.get("backoff_seconds", 0))
        state.update(status="failed", error=record.get("error", {"code": "retry_exhausted"}))
        return False

    def validate_run(self, run_id):
        with self.lock(run_id):
            state = self.load(run_id)
            try:
                if state["status"] == "running":
                    raise Fault("run_incomplete", "Run was interrupted; resume and reconcile before validation")
                self.ensure_checkpoint(state)
                if any(r["status"] != "passed" for r in state["steps"].values()):
                    raise Fault("run_incomplete", "Every required step must pass before final acceptance")
                for sid, record in state["steps"].items():
                    self.validate_outputs(self.steps[sid]["completion"], record["outputs"], self.envelope(state, sid))
                outputs = self.bind(self.spec["outputs"], state)
                artifacts = self.validate_outputs(self.spec["acceptance"], outputs, self.envelope(state))
                state.update(status="succeeded", outputs=outputs,
                             acceptance={"passed": True, "at": now(), "artifacts": artifacts})
                state.pop("error", None)
                self.save(state, {"event": "revalidated"})
                return state
            except KeyboardInterrupt:
                state.update(status="interrupted", acceptance={"passed": False, "at": now()})
                self.save(state, {"event": "validation_interrupted"})
                return state
            except (Fault, OSError, ValueError) as exc:
                if not isinstance(exc, Fault):
                    exc = Fault("validation_io_error", str(exc))
                state.update(status="failed", error=exc.record(), acceptance={"passed": False, "at": now()})
                self.save(state, {"event": "validation_failed", "error": exc.record()})
                return state


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=Path(__file__).resolve().parent.parent)
    commands = parser.add_subparsers(dest="operation", required=True)
    commands.add_parser("check")
    run = commands.add_parser("run")
    run.add_argument("--input", type=Path, required=True, help="JSON input file")
    run.add_argument("--run-id")
    run.add_argument("--pause-after", help="Stop after a committed step checkpoint")
    for name in ["status", "resume", "retry", "validate"]:
        sub = commands.add_parser(name)
        sub.add_argument("--run-id", required=True)
        if name == "retry":
            sub.add_argument("--step", required=True)
    args = parser.parse_args()
    def interrupt(_signum, _frame):
        raise KeyboardInterrupt
    signal.signal(signal.SIGTERM, interrupt)
    try:
        runtime = Runtime(args.project)
        if args.operation == "check":
            result = runtime.check()
            code = 0 if result["ok"] else 3
        elif args.operation == "status":
            result, code = runtime.load(args.run_id), 0
        else:
            if args.operation == "validate":
                result = runtime.validate_run(args.run_id)
            elif args.operation == "run":
                if args.pause_after and args.pause_after not in runtime.steps:
                    raise Fault("step_missing", args.pause_after)
                result = runtime.execute(inputs=json.loads(args.input.read_text()), run_id=args.run_id,
                                         pause_after=args.pause_after)
            else:
                result = runtime.execute(run_id=args.run_id, operation=args.operation,
                                         selected=getattr(args, "step", None))
            code = {"succeeded": 0, "blocked": 3, "interrupted": 4}.get(result["status"], 1)
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
        return code
    except Fault as exc:
        print(json.dumps({"ok": False, "error": exc.record()}, ensure_ascii=False))
        return 2
    except KeyboardInterrupt:
        print(json.dumps({"ok": False, "error": {"code": "interrupted", "message": "Operation interrupted"}}))
        return 4
    except (OSError, ValueError, yaml.YAMLError, SchemaError) as exc:
        print(json.dumps({"ok": False, "error": {"code": "input_error", "message": str(exc)}}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
