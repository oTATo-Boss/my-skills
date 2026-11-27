"""Behavioral checks for zero-input reference drawing."""
import importlib.util
import json
from pathlib import Path
import random
import unittest

ENGINE = Path(__file__).with_name("draw_refs.py")
FACETS = ("styling", "scene", "background", "expression", "pose", "composition", "lighting", "finish")


def record(ref, scene="室内", partial=False, hidden=()):
    return {"id": ref, "title": "抽取测试", "file": f"assets/{ref}.jpg", "partial": partial, "visual": {
        "facets": {key: ({"tags": [], "observation": "看不见", "evidence": "not_visible"} if key in hidden
                         else {"tags": [scene] if key == "scene" else [key],
                               "observation": f"{key} 观察", "evidence": "observed"})
                   for key in FACETS},
        "transferable_mechanism": "测试机制", "limitations": ["合成记录"]}}


class DrawRefsTests(unittest.TestCase):
    def setUp(self):
        spec = importlib.util.spec_from_file_location("draw_refs", ENGINE)
        self.engine = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.engine)

    def test_draw_returns_distinct_roles_with_paths(self):
        rows = [record(f"R{i:02d}") for i in range(1, 9)]
        picks = self.engine.draw(rows, random.Random(1))
        self.assertEqual([p["role"] for p in picks], list(self.engine.ROLES))
        self.assertEqual(len({p["id"] for p in picks}), len(picks))
        self.assertTrue(all(p["file"].endswith(".jpg") for p in picks))

    def test_primary_needs_known_scene_and_whole_image(self):
        rows = [record("R01", "场景不明"), record("R02", partial=True), record("R03", hidden=("lighting",)),
                record("R04")]
        for seed in range(20):
            self.assertEqual(self.engine.draw(rows, random.Random(seed))[0]["id"], "R04")

    def test_finish_reference_matches_primary_scene_class(self):
        rows = [record("R01", "室外"), record("R02", "室内"), record("R03", "室内"), record("R04", "室外")]
        for seed in range(20):
            picks = {p["role"]: p for p in self.engine.draw(rows, random.Random(seed))}
            if "质感参考" in picks:
                primary = next(r for r in rows if r["id"] == picks["主参考"]["id"])
                finish = next(r for r in rows if r["id"] == picks["质感参考"]["id"])
                self.assertEqual(self.engine.scene_class(primary), self.engine.scene_class(finish))

    def test_exclude_is_respected_and_empty_pool_fails(self):
        rows = [record("R01"), record("R02")]
        picks = self.engine.draw(rows, random.Random(3), exclude=["R01"])
        self.assertNotIn("R01", [p["id"] for p in picks])
        with self.assertRaises(ValueError):
            self.engine.draw(rows, random.Random(3), exclude=["R01", "R02"])

    def test_same_seed_repeats_and_draws_vary(self):
        rows = [record(f"R{i:02d}") for i in range(1, 30)]
        first = self.engine.draw(rows, random.Random(5))
        self.assertEqual(first, self.engine.draw(rows, random.Random(5)))
        primaries = {self.engine.draw(rows, random.Random(s))[0]["id"] for s in range(30)}
        self.assertGreater(len(primaries), 5)

    def test_real_library_draw_points_to_existing_files(self):
        root = ENGINE.resolve().parents[1]
        rows = json.loads((root / "assets/reference-covers/manifest.json").read_text())
        for seed in range(10):
            for pick in self.engine.draw(rows, random.Random(seed)):
                self.assertTrue(Path(pick["file"]).is_file(), pick["file"])


if __name__ == "__main__":
    unittest.main()
