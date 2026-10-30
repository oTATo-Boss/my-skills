#!/usr/bin/env python3
"""Offline acceptance-checker tests; these never start model sessions."""
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import shutil
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location("native_invocation", Path(__file__).resolve().parents[1] / "evals/native_invocation.py")
NATIVE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(NATIVE)


def events(final="FERN-8352|alpha", commands=()):
    result = [{"type": "thread.started", "thread_id": "fixture-new-thread"}, {"type": "turn.started"}]
    for command, output, code in commands:
        result.append({"type": "item.completed", "item": {"type": "command_execution", "command": command, "aggregated_output": output, "exit_code": code}})
    result.extend([{"type": "item.completed", "item": {"type": "agent_message", "text": final}}, {"type": "turn.completed"}])
    return result


SELECT = ("python3 -B manager/scripts/quality_registry.py select SKILL_QUALITY.json --request task-candidates.json", '{"status":"selected","selected":{"id":"fern-b"}}', 0)
RUN_A = ("python3 .agents/skills/fern-a/scripts/receipt.py alpha", "FERN-7241|alpha\n", 0)
RUN_B = ("python3 .agents/skills/fern-b/scripts/receipt.py alpha", "FERN-8352|alpha\n", 0)


class NativeEvidenceTests(unittest.TestCase):
    def test_self_report_without_execution_is_not_a_pass(self):
        self.assertFalse(NATIVE.inspect_events(events(), "managed-b")["pass"])

    def test_wrong_execution_cannot_be_hidden_by_expected_final_text(self):
        self.assertFalse(NATIVE.inspect_events(events(commands=[SELECT, RUN_A]), "managed-b", True)["pass"])

    def test_selector_execution_is_required_for_hardened_integration(self):
        commands = [("cat SKILL_QUALITY.json", "fixture input", 0), RUN_B]
        self.assertTrue(NATIVE.inspect_events(events(commands=commands), "managed-b")["pass"])
        self.assertFalse(NATIVE.inspect_events(events(commands=commands), "managed-b", True)["pass"])
        self.assertTrue(NATIVE.inspect_events(events(commands=[SELECT, RUN_B]), "managed-b", True)["pass"])

    def test_explicit_choice_does_not_require_score_selector(self):
        self.assertTrue(NATIVE.inspect_events(events(final="FERN-7241|alpha", commands=[RUN_A]), "explicit-lower", True)["pass"])

    def test_attempting_blocked_skill_then_falling_back_is_not_a_pass(self):
        failed = (RUN_B[0], "Missing dependency", 1)
        selected_a = (SELECT[0], '{"status":"selected","selected":{"id":"fern-a"}}', 0)
        self.assertFalse(NATIVE.inspect_events(events(final="FERN-7241|alpha", commands=[selected_a, failed, RUN_A]), "blocked-higher", True)["pass"])

    def test_selector_output_must_match_the_executed_skill(self):
        wrong = (SELECT[0], '{"status":"selected","selected":{"id":"fern-a"}}', 0)
        self.assertFalse(NATIVE.inspect_events(events(commands=[wrong, RUN_B]), "managed-b", True)["pass"])

    def test_unrelated_task_must_not_load_scores(self):
        self.assertTrue(NATIVE.inspect_events(events(final="4"), "unrelated")["pass"])
        self.assertFalse(NATIVE.inspect_events(events(final="4", commands=[SELECT]), "unrelated")["pass"])

    def test_missing_completion_or_multiple_thread_starts_fail(self):
        valid = events(commands=[SELECT, RUN_B])
        self.assertFalse(NATIVE.inspect_events(valid[:-1], "managed-b", True)["pass"])
        valid.append({"type": "thread.started", "thread_id": "another-thread"})
        self.assertFalse(NATIVE.inspect_events(valid, "managed-b", True)["pass"])

    def test_real_project_root_is_rejected_and_legacy_label_cannot_escape(self):
        with self.assertRaises(ValueError):
            NATIVE.fixture_root(Path.cwd())
        with self.assertRaises(ValueError):
            NATIVE.collect(Path.cwd(), "../outside")

    def test_parent_app_bridges_are_removed_without_replacing_user_home(self):
        with patch.dict(os.environ, {"CODEX_THREAD_ID": "parent-thread", "CODEX_APP_TOOLS_PIPE_PATH": "parent-pipe"}):
            child = NATIVE.child_environment()
            self.assertNotIn("CODEX_THREAD_ID", child)
            self.assertNotIn("CODEX_APP_TOOLS_PIPE_PATH", child)
            for key in ("HOME", "CODEX_HOME"):
                self.assertEqual(child.get(key), os.environ.get(key))

    def test_manifest_detects_changed_inputs_but_ignores_python_cache(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "score.json").write_text("original")
            original = NATIVE.manifest(root)
            (root / "__pycache__").mkdir()
            (root / "__pycache__/cache.pyc").write_bytes(b"cache")
            self.assertEqual(original, NATIVE.manifest(root))
            (root / "score.json").write_text("changed")
            self.assertNotEqual(original, NATIVE.manifest(root))

    def test_collection_requires_process_and_manifest_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            import json
            root = Path(tmp)
            (root / "managed-b-events.jsonl").write_text("\n".join(json.dumps(e) for e in events(commands=[SELECT, RUN_B])))
            result = NATIVE.collect(root)
            self.assertFalse(next(r for r in result["results"] if r["case"] == "managed-b")["pass"])

    def test_collect_cli_returns_nonzero_for_unrun_cases(self):
        with tempfile.TemporaryDirectory(prefix="native-skill-eval-") as tmp:
            root = Path(tmp)
            (root / "isolation-runtime.sb").write_text("placeholder: collect never launches a process")
            result = subprocess.run([sys.executable, "-B", str(Path(NATIVE.__file__)), "collect", str(root)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)
            self.assertIn('"all_pass": false', result.stdout)

    def test_real_seatbelt_preflight_covers_unicode_and_shared_roots(self):
        root = NATIVE.prepare()
        self.addCleanup(shutil.rmtree, root)
        policy = (root / "isolation-runtime.sb").read_text()
        self.assertIn("隔离保护探针", policy)
        self.assertNotIn("\\u9694", policy)
        NATIVE.check_isolation(root)
        self.assertFalse((root / "隔离保护探针/write-test.txt").exists())


if __name__ == "__main__":
    unittest.main()
