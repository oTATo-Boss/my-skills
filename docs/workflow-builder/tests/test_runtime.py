"""Black-box independent-project acceptance, not tests of prompt wording."""
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[3]
SKILL = ROOT / "skills/dev/workflow-builder"
GENERATOR = SKILL / "scripts/create_workflow.py"

WORKER = '''import json,os,sys,time
from pathlib import Path
if len(sys.argv)>1 and sys.argv[1]=='probe':
 print(json.dumps({'ok':True}));raise SystemExit(0)
j=json.load(sys.stdin)
mode=j['inputs'].get('mode','ok')
out=Path(j['output_dir'])
if mode=='wait' and j['attempt']==1:
 (out/'started').write_text(str(os.getpid()))
 time.sleep(30)
if mode=='fail' or (mode=='once' and j['attempt']==1):raise SystemExit(7)
if mode=='invalid':print('not json');raise SystemExit(0)
if mode=='skill':
 assert 'sample-skill' in j['resources']['knowledge']['documents'][0]['text']
 assert j['rules'][0]['text']
 assert j['agent']['role']=='report-writer'
 assert 'report role' in j['agent']['instructions'][0]['text']
p=out/'report.md';p.write_text('# Test report\\n- Verified\\n' if mode!='bad' else '')
print(json.dumps({'report':'report.md','note_count':1}))
'''


class Acceptance(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name) / "project"
        result = subprocess.run([sys.executable, str(GENERATOR), "--path", str(self.project),
                                 "--name", "test-workflow"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.runner = self.project / "runtime/runner.py"
        (self.project / "tests/worker.py").write_text(WORKER)
        self.spec = json.loads((self.project / "workflow.yaml").read_text())

    def write_spec(self):
        (self.project / "workflow.yaml").write_text(json.dumps(self.spec, indent=2))

    def cli(self, *args, expected=0, env=None):
        # Fresh process, unrelated cwd, no Builder import path or retained Python state.
        result = subprocess.run([sys.executable, str(self.runner), *args], cwd=self.temp.name,
                                capture_output=True, text=True, timeout=20, env=env)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return json.loads(result.stdout)

    def worker(self, mode, *, automatic=True, attempts=2, recovery="idempotent"):
        step = self.spec["steps"][-1]
        step["executor"]["command"] = ["{python}", "tests/worker.py"]
        step["inputs"]["mode"] = {"value": mode}
        step["failure"].update(max_attempts=attempts, automatic=automatic,
                               retry_on=["executor_failed", "timeout", "invalid_output", "validation_failed"])
        step["recovery"]["mode"] = recovery
        self.write_spec()

    def run_job(self, *, expected=0, run_id="example", env=None, extra=()):
        return self.cli("run", "--input", str(self.project / "example-input.json"),
                        "--run-id", run_id, *extra, expected=expected, env=env)

    def wait_started(self, process, run_id="example"):
        marker = self.project / "outputs" / run_id / "started"
        deadline = time.monotonic() + 10
        while not marker.exists() and time.monotonic() < deadline:
            if process.poll() is not None:
                stdout, stderr = process.communicate()
                self.fail(stdout + stderr)
            time.sleep(.03)
        self.assertTrue(marker.exists())
        return int(marker.read_text())

    def start_waiting(self):
        proc = subprocess.Popen([sys.executable, str(self.runner), "run", "--input",
                                 str(self.project / "example-input.json"), "--run-id", "example"],
                                cwd=self.temp.name, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.addCleanup(lambda: proc.poll() is None and proc.kill())
        return proc

    def test_normal_and_repeat_runs_are_independent(self):
        self.assertTrue(self.cli("check")["ok"])
        one = self.run_job()
        two = self.run_job(run_id="second")
        self.assertEqual(one["status"], "succeeded")
        self.assertNotEqual(one["run_id"], two["run_id"])
        for run in ["example", "second"]:
            p = self.project / "outputs" / run / "report.md"
            self.assertIn("# Project notes", p.read_text())
        self.assertTrue(self.cli("validate", "--run-id", "example")["acceptance"]["passed"])
        self.assertEqual(self.cli("status", "--run-id", "second")["status"], "succeeded")

    def test_definition_and_input_rejected(self):
        (self.project / "bad.json").write_text('{"title":"missing notes"}')
        result = self.cli("run", "--input", str(self.project / "bad.json"), expected=2)
        self.assertEqual(result["error"]["code"], "validation_failed")
        self.spec["steps"][0]["depends_on"] = ["render"]
        self.write_spec()
        result = self.cli("check", expected=2)
        self.assertEqual(result["error"]["code"], "definition_invalid")

    def test_automatic_retry(self):
        self.worker("once")
        state = self.run_job()
        self.assertEqual([a["status"] for a in state["steps"]["render"]["attempts"]], ["failed", "passed"])
        self.assertEqual(len(state["steps"]["prepare"]["attempts"]), 1)

    def test_explicit_retry_and_exhaustion(self):
        self.worker("once", automatic=False)
        self.run_job(expected=1)
        self.cli("resume", "--run-id", "example", expected=2)
        result = self.cli("retry", "--run-id", "example", "--step", "render")
        self.assertEqual(result["status"], "succeeded")
        self.worker("fail")
        state = self.run_job(run_id="exhausted", expected=1)
        self.assertEqual(len(state["steps"]["render"]["attempts"]), 2)
        result = self.cli("retry", "--run-id", "exhausted", "--step", "render", expected=2)
        self.assertEqual(result["error"]["code"], "retry_exhausted")

    def test_checkpoint_resume_in_new_process(self):
        state = self.run_job(expected=4, extra=("--pause-after", "prepare"))
        self.assertEqual(state["steps"]["prepare"]["status"], "passed")
        result = self.cli("resume", "--run-id", "example")
        self.assertEqual(result["status"], "succeeded")
        self.assertEqual(len(result["steps"]["prepare"]["attempts"]), 1)

    def test_unrelated_input_file_does_not_invalidate_checkpoint(self):
        self.run_job(expected=4, extra=("--pause-after", "prepare"))
        (self.project / "next-input.json").write_text('{"title":"next job","notes":["future"]}')
        result = self.cli("resume", "--run-id", "example")
        self.assertEqual(result["status"], "succeeded")

    def test_sigterm_and_lock(self):
        self.worker("wait")
        proc = self.start_waiting()
        self.wait_started(proc)
        result = self.cli("resume", "--run-id", "example", expected=2)
        self.assertEqual(result["error"]["code"], "run_busy")
        proc.terminate()
        stdout, stderr = proc.communicate(timeout=8)
        self.assertEqual(proc.returncode, 4, stdout + stderr)
        state = json.loads(stdout)
        self.assertEqual(state["status"], "interrupted")
        result = self.cli("resume", "--run-id", "example")
        self.assertEqual(result["steps"]["render"]["attempts"][0]["status"], "interrupted")

    def test_unknown_side_effect_not_replayed(self):
        self.worker("wait", recovery="manual")
        proc = self.start_waiting()
        self.wait_started(proc)
        proc.terminate()
        proc.communicate(timeout=8)
        state = self.cli("resume", "--run-id", "example", expected=3)
        self.assertEqual(state["error"]["code"], "outcome_unknown")
        state = self.cli("resume", "--run-id", "example", expected=3)
        self.assertEqual(len(state["steps"]["render"]["attempts"]), 1)
        self.assertEqual(self.cli("status", "--run-id", "example")["status"], "blocked")

    def test_orphan_executor_blocks_resume(self):
        self.worker("wait")
        proc = self.start_waiting()
        pid = self.wait_started(proc)
        self.addCleanup(lambda: self.kill_group(pid))
        proc.kill()
        # Child inherited stdout? Runtime's child pipes are separate, so communicate returns.
        proc.communicate(timeout=8)
        state = self.cli("resume", "--run-id", "example", expected=2)
        self.assertEqual(state["error"]["code"], "executor_still_running")

    @staticmethod
    def kill_group(pid):
        try:
            os.killpg(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass

    def test_invalid_output_and_timeout(self):
        self.worker("invalid", attempts=1)
        state = self.run_job(expected=1)
        self.assertEqual(state["error"]["code"], "invalid_output")
        self.worker("wait", attempts=1)
        self.spec["steps"][-1]["failure"]["timeout_seconds"] = .2
        self.write_spec()
        state = self.run_job(expected=1, run_id="timeout")
        self.assertEqual(state["error"]["code"], "timeout")

    def test_artifact_and_final_acceptance(self):
        self.worker("bad", attempts=1)
        state = self.run_job(expected=1)
        self.assertEqual(state["steps"]["render"]["status"], "failed")
        self.worker("ok")
        self.spec["acceptance"]["artifacts"][0]["contains"] = ["Missing business requirement"]
        self.write_spec()
        state = self.run_job(expected=1, run_id="rejected")
        self.assertTrue(all(r["status"] == "passed" for r in state["steps"].values()))
        self.assertFalse(state["acceptance"]["passed"])

    def test_changed_source_and_checkpoint_artifact(self):
        self.run_job(expected=4, extra=("--pause-after", "prepare"))
        with (self.project / "scripts/report.py").open("a") as out:
            out.write("\n# changed source\n")
        result = self.cli("resume", "--run-id", "example", expected=2)
        self.assertEqual(result["error"]["code"], "checkpoint_mismatch")
        self.run_job(run_id="fresh")
        (self.project / "outputs/fresh/report.md").write_text("tampered")
        state = self.cli("validate", "--run-id", "fresh", expected=1)
        self.assertEqual(state["status"], "failed")
        self.assertFalse(state["acceptance"]["passed"])

    def test_missing_resource_and_then_reconnect(self):
        self.spec["resources"] = {"service": {"kind": "tool", "required_env": ["WORKFLOW_TEST_CREDENTIAL"],
                                               "probe": ["{python}", "tests/worker.py", "probe"]}}
        self.spec["steps"][-1]["executor"]["resources"] = ["service"]
        self.write_spec()
        clean = dict(os.environ)
        clean.pop("WORKFLOW_TEST_CREDENTIAL", None)
        state = self.run_job(expected=3, env=clean)
        self.assertTrue(all(r["status"] == "pending" for r in state["steps"].values()))
        clean["WORKFLOW_TEST_CREDENTIAL"] = "test-only-not-a-real-key"
        state = self.cli("resume", "--run-id", "example", env=clean)
        self.assertEqual(state["preflight"]["resources"]["service"]["status"], "probe_passed")

    def test_agent_adapter_gets_skill_and_rules(self):
        (self.project / "tests/knowledge.md").write_text("sample-skill: produce a report")
        (self.project / "tests/role.md").write_text("report role: write a concise report")
        self.worker("skill")
        self.spec["resources"] = {"knowledge": {"kind": "skill", "paths": ["tests/knowledge.md"]}}
        self.spec["steps"][-1]["executor"].update(kind="agent", role="report-writer",
                                                  instructions=["tests/role.md"], resources=["knowledge"])
        self.write_spec()
        state = self.run_job()
        self.assertEqual(state["status"], "succeeded")

    def test_preflight_rejects_missing_executor(self):
        self.spec["steps"][-1]["executor"]["command"] = ["workflow-missing-executable"]
        self.write_spec()
        state = self.run_job(expected=3)
        self.assertEqual(state["preflight"]["errors"][0]["code"], "executor_unavailable")

    def test_schema_cannot_fetch_remote_references(self):
        self.spec["steps"][0]["outputs"]["properties"]["title"] = {"$ref": "https://example.invalid/schema"}
        self.write_spec()
        result = self.cli("check", expected=2)
        self.assertEqual(result["error"]["code"], "definition_invalid")

    def test_unresolved_local_schema_rejected_before_execution(self):
        self.spec["steps"][0]["outputs"]["properties"]["title"] = {"$ref": "#/$defs/missing"}
        self.write_spec()
        result = self.cli("check", expected=2)
        self.assertEqual(result["error"]["code"], "definition_invalid")

    def test_validator_cannot_change_a_checked_artifact(self):
        (self.project / "tests/mutating.py").write_text("import json,sys\nfrom pathlib import Path\nj=json.load(sys.stdin)\n(Path(j['output_dir'])/'report.md').write_text('invalid')\nprint(json.dumps({'ok':True}))\n")
        self.spec["acceptance"]["command"] = ["{python}", "tests/mutating.py"]
        self.write_spec()
        state = self.run_job(expected=1)
        self.assertFalse(state["acceptance"]["passed"])
        self.assertEqual(state["error"]["code"], "validation_failed")

    def test_yaml_non_json_literal_is_definition_error(self):
        import yaml
        (self.project / "workflow.yaml").write_text(yaml.safe_dump(self.spec) + '\nextra_date: 2026-10-28\n')
        result = self.cli("check", expected=2)
        self.assertEqual(result["error"]["code"], "definition_invalid")

    def test_generator_wont_overwrite(self):
        result = subprocess.run([sys.executable, str(GENERATOR), "--path", str(self.project),
                                 "--name", "test-workflow"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)


if __name__ == "__main__":
    unittest.main()
