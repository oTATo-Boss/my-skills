#!/usr/bin/env python3
"""Isolated arithmetic, evidence boundary, selection and GitHub response checks."""
import copy
from datetime import date
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import URLError

from quality_registry import WEIGHTS, catalog, github_snapshot, score, select, star_points

TODAY = date(2026, 10, 30)


def record(points=None):
    return {"status": "verified", "assessed_version": "1", "review_after": "2026-11-30",
            "points": points, "evidence": [{"source": "fixture-run.json", "version": "1",
            "observed_at": "2026-10-30", "verification": "tested"}]}


def profile(identity="a", kind="original"):
    result = {"id": identity, "name": identity, "entry": f"skills/{identity}/SKILL.md",
              "version": "1", "revision": "fixture-revision-1", "scenario": "text-json",
              "evaluated_at": "2026-10-30", "upstream_repository": "fixture/export",
              "metrics": {key: record(weight) for key, weight in WEIGHTS.items() if key not in {"github", "ownership"}},
              "github": dict(record(), repository="fixture/export", stars=99999, scope="dedicated", attribution="confirmed"),
              "ownership": dict(record(), kind=kind), "runs": []}
    return result


def registry(*profiles):
    return {"schema_version": 1, "profiles": list(profiles)}


def gate(identity="a", **changes):
    return dict({"id": identity, "fit": "exact", "conditions": "ready", "version": "1",
                 "revision": "fixture-revision-1", "evidence": ["Agent read fixture entry and checked Python availability."]}, **changes)


def request(*candidates, **changes):
    return dict({"scenario": "text-json", "candidates": list(candidates)}, **changes)


class QualityTests(unittest.TestCase):
    def test_weights_and_exact_score(self):
        self.assertEqual(sum(WEIGHTS.values()), 100)
        self.assertEqual(score(profile(), TODAY)["total"], 97.5)

    def test_log_bands_interpolation_monotonicity_and_collection_scope(self):
        points = [star_points(stars, "dedicated") for stars in range(1000)]
        self.assertTrue(all(a < b for a, b in zip(points, points[1:])))
        for stars, expected in [(0, 0), (9, 7.5), (99, 10), (999, 11.25), (9999, 12), (99999, 12.5)]:
            self.assertAlmostEqual(star_points(stars, "dedicated"), expected)
            self.assertAlmostEqual(star_points(stars, "collection"), expected / 2)
        self.assertLess(star_points(99, "dedicated"), star_points(100, "dedicated"))
        self.assertLess(star_points(99999, "dedicated"), star_points(1000000, "dedicated"))
        self.assertLess(star_points(1000000, "dedicated"), 15)

    def test_invalid_star_counts_and_unknown_attribution(self):
        for bad in [True, -1, 2.5, "100"]:
            with self.assertRaises(ValueError):
                star_points(bad, "dedicated")
        for key, value in [("attribution", "unknown"), ("scope", "unknown"), ("repository", "wrong/repo")]:
            p = profile()
            p["github"][key] = value
            with self.assertRaises(ValueError):
                score(p, TODAY)

    def test_unknown_is_not_zero_or_normalized_full_score(self):
        p = profile()
        p["metrics"]["effect"] = dict(record(), status="unverified", points=None, evidence=[])
        scored = score(p, TODAY)
        self.assertIsNone(scored["total"])
        self.assertEqual((scored["known_points"], scored["possible_max"], scored["verified_weight"]), (72.5, 97.5, 75))
        p["metrics"]["effect"]["status"] = "partial"
        p["metrics"]["effect"]["points"] = 24
        self.assertEqual(score(p, TODAY)["known_points"], 72.5)

    def test_confirmed_no_github_origin_is_known_zero(self):
        p = profile()
        p["github"] = dict(record(), status="not_applicable", repository=None, stars=None)
        self.assertEqual(score(p, TODAY)["total"], 85)
        self.assertEqual(score(p, TODAY)["verified_weight"], 100)

    def test_original_deep_adaptation_and_collected(self):
        p = profile(kind="deep_adapted")
        p["ownership"]["contribution"] = 0.8
        self.assertEqual(score(p, TODAY)["dimensions"]["ownership"]["points"], 12)
        p["ownership"]["contribution"] = 1
        with self.assertRaises(ValueError):
            score(p, TODAY)
        self.assertEqual(score(profile(kind="collected"), TODAY)["total"], 82.5)

    def test_stale_version_date_and_future_evidence(self):
        for key, value in [("assessed_version", "old"), ("review_after", "2026-10-30")]:
            p = profile()
            p["metrics"]["effect"][key] = value
            asof = TODAY if key == "assessed_version" else date(2026, 10, 31)
            self.assertEqual(score(p, asof)["dimensions"]["effect"]["status"], "stale")
        p = profile()
        p["github"]["evidence"][0]["observed_at"] = "2099-01-01"
        with self.assertRaises(ValueError):
            score(p, TODAY)
        p = profile()
        p["evaluated_at"] = "2026-10-29"
        with self.assertRaises(ValueError):
            score(p, TODAY)

    def test_claims_without_tests_cannot_score_effect_and_reliability(self):
        for key in ("effect", "reliability"):
            p = profile()
            p["metrics"][key]["evidence"][0]["verification"] = "inspected"
            with self.assertRaises(ValueError):
                score(p, TODAY)
        p = profile()
        p["ownership"]["evidence"][0]["verification"] = "reported"
        with self.assertRaises(ValueError):
            score(p, TODAY)

    def test_nonfinite_out_of_range_and_duplicate_profiles_rejected(self):
        for value in (float("nan"), float("inf"), True, -1, 26):
            p = profile()
            p["metrics"]["effect"]["points"] = value
            with self.assertRaises(ValueError):
                score(p, TODAY)
        with self.assertRaises(ValueError):
            catalog(registry(profile(), profile()), TODAY)

    def test_explicit_choice_beats_score_but_cannot_override_blocked_runtime(self):
        a, b = profile(), profile("b", "collected")
        result = select(registry(a, b), request(gate(), gate("b"), explicit_id="b"), TODAY)
        self.assertEqual(result["selected"]["id"], "b")
        result = select(registry(a, b), request(gate(), gate("b", revision="updated"), explicit_id="b"), TODAY)
        self.assertEqual(result["status"], "explicit")
        self.assertIsNone(result["selected"]["score"]["total"])
        result = select(registry(a, b), request(gate(), gate("b", conditions="blocked"), explicit_id="b"), TODAY)
        self.assertEqual(result["status"], "blocked_explicit")
        self.assertIsNone(result["selected"])
        with self.assertRaises(ValueError):
            select(registry(a), request(gate(), explicit_id="missing"), TODAY)

    def test_higher_score_cannot_override_task_mismatch(self):
        result = select(registry(profile(), profile("b", "collected")), request(gate(fit="none"), gate("b")), TODAY)
        self.assertEqual(result["selected"]["id"], "b")
        self.assertEqual(result["excluded"][0]["id"], "a")

    def test_scenario_and_revision_changes_do_not_reuse_old_rankings(self):
        with self.assertRaises(ValueError):
            select(registry(profile()), request(gate(), scenario="video-render"), TODAY)
        result = select(registry(profile()), request(gate(revision="new-content")), TODAY)
        self.assertEqual(result["status"], "needs_review")
        self.assertEqual(result["pending"][0]["score"]["possible_max"], 100)

    def test_incomplete_competitor_prevents_false_winner(self):
        p = profile("b")
        p["metrics"]["effect"] = dict(record(), status="unverified", points=None, evidence=[])
        result = select(registry(profile(), p), request(gate(), gate("b")), TODAY)
        self.assertEqual(result["status"], "needs_review")
        self.assertIsNone(result["selected"])

    def test_close_scores_favor_original_and_large_gap_favors_quality(self):
        a, b = profile(), profile("b", "collected")
        a["metrics"]["effect"]["points"] = 8  # 80.5 versus 82.5
        self.assertEqual(select(registry(a, b), request(gate(), gate("b")), TODAY)["selected"]["id"], "a")
        a["metrics"]["effect"]["points"] = 2
        self.assertEqual(select(registry(a, b), request(gate(), gate("b")), TODAY)["selected"]["id"], "b")

    def test_real_usage_deduplicated_scoped_and_ahead_of_specialty(self):
        a, b = profile(), profile("b")
        run = {"id": "run-1", "source": "actual-run.json", "observed_at": "2026-10-30", "scenario": "text-json",
               "version": "1", "status": "verified", "outcome": "success"}
        b["runs"] = [run]
        self.assertEqual(select(registry(a, b), request(gate(), gate("b", fit="related")), TODAY)["selected"]["id"], "b")
        b["runs"].append(dict(run, id="run-2", version="old"))
        self.assertEqual(score(b, TODAY)["runs"], {"attempts": 1, "successes": 1})
        b["runs"].append(copy.deepcopy(run))
        with self.assertRaises(ValueError):
            score(b, TODAY)

    def test_github_api_uses_real_count_and_preserves_unknown_scope(self):
        response = io.StringIO(json.dumps({"full_name": "upstream/export", "stargazers_count": 1234, "fork": False}))
        response.status = 200
        with patch("quality_registry.urlopen", return_value=response) as opened:
            result = github_snapshot("upstream/export")
        self.assertEqual(result["stars"], 1234)
        self.assertEqual((result["scope"], result["attribution"]), ("unknown", "unknown"))
        self.assertEqual(opened.call_args.args[0].full_url, "https://api.github.com/repos/upstream/export")

    def test_github_errors_and_unsupported_counts_never_become_zero(self):
        with patch("quality_registry.urlopen", side_effect=URLError("rate limited")), patch("quality_registry.shutil.which", return_value=None):
            with self.assertRaises(URLError):
                github_snapshot("owner/repo")
        response = io.StringIO('{"full_name":"owner/repo"}')
        response.status = 200
        with patch("quality_registry.urlopen", return_value=response):
            with self.assertRaises(ValueError):
                github_snapshot("owner/repo")
        with self.assertRaises(ValueError):
            github_snapshot("https://other.example/repo")
        with self.assertRaises(ValueError):
            github_snapshot("../repo")

    def test_optional_gh_fallback_keeps_tls_and_requires_successful_data(self):
        result = subprocess.CompletedProcess([], 0, '{"full_name":"owner/repo","stargazers_count":0}', '')
        with patch("quality_registry.urlopen", side_effect=URLError("CA unavailable")), patch("quality_registry.shutil.which", return_value="gh"), patch("quality_registry.subprocess.run", return_value=result) as call:
            snapshot = github_snapshot("owner/repo")
        self.assertEqual((snapshot["transport"], snapshot["stars"]), ("gh", 0))
        self.assertEqual(call.call_args.args[0][:3], ["gh", "api", "repos/owner/repo"])
        result = subprocess.CompletedProcess([], 1, '', 'Rate limited')
        with patch("quality_registry.urlopen", side_effect=URLError("CA unavailable")), patch("quality_registry.shutil.which", return_value="gh"), patch("quality_registry.subprocess.run", return_value=result):
            with self.assertRaises(ValueError):
                github_snapshot("owner/repo")

    def test_cli_is_read_only_and_fails_on_malformed_registry(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "registry.json"
            path.write_text(json.dumps(registry(profile())))
            before = path.read_bytes()
            command = [sys.executable, "-B", str(Path(__file__).with_name("quality_registry.py")), "score", str(path), "--as-of", "2026-10-30"]
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["profiles"][0]["total"], 97.5)
            self.assertEqual(path.read_bytes(), before)
            path.write_text('{"schema_version":1,"profiles": [null]}')
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)
            self.assertFalse(json.loads(result.stdout)["ok"])

    def test_read_only_selection_accepts_request_from_stdin(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "registry.json"
            path.write_text(json.dumps(registry(profile())))
            before = path.read_bytes()
            command = [sys.executable, "-B", str(Path(__file__).with_name("quality_registry.py")), "select", str(path), "--request", "-", "--as-of", "2026-10-30"]
            result = subprocess.run(command, input=json.dumps(request(gate())), capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["selected"]["id"], "a")
            self.assertEqual(list(Path(tmp).iterdir()), [path])
            self.assertEqual(path.read_bytes(), before)
            result = subprocess.run(command, input="not JSON", capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)
            self.assertFalse(json.loads(result.stdout)["ok"])


if __name__ == "__main__":
    unittest.main()
