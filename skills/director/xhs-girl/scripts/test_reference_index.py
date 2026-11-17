"""Behavioral checks for evidence-aware, multi-facet reference discovery."""
import copy
import importlib.util
from pathlib import Path
import unittest

ENGINE = Path(__file__).with_name("reference_index.py")
FACETS = ("styling", "scene", "background", "expression", "pose", "composition", "lighting", "finish")


def reference(ref, scene="室外", lighting="冷光"):
    return {"id": ref, "title": "检索测试", "file": f"assets/{ref}.jpg", "visual": {
        "schema_version": 1,
        "facets": {key: {"tags": [scene if key == "scene" else lighting if key == "lighting" else key],
                            "observation": "可以在测试图片中观察到的关系", "evidence": "observed"}
                   for key in FACETS},
        "transferable_mechanism": "测试只验证检索行为，不代表真实照片分析。",
        "limitations": ["合成测试记录"],
        "review": {"date": "2026-11-17", "method": "visual-inspection", "image_sha256": "a" * 64}}}


class ReferenceIndexTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(ENGINE.is_file(), "Reference index engine is not implemented")
        spec = importlib.util.spec_from_file_location("reference_index", ENGINE)
        self.engine = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.engine)

    def test_complete_facets_and_hash_are_required(self):
        row = reference("R01")
        self.assertEqual(self.engine.validate_visual(row, "a" * 64), [])
        bad = copy.deepcopy(row)
        del bad["visual"]["facets"]["background"]
        self.assertTrue(self.engine.validate_visual(bad, "a" * 64))
        self.assertTrue(self.engine.validate_visual(row, "b" * 64))

    def test_unseen_expression_cannot_carry_guessed_tags(self):
        row = reference("R01")
        row["visual"]["facets"]["expression"] = {
            "tags": [], "observation": "面部在画外", "evidence": "not_visible"}
        self.assertEqual(self.engine.validate_visual(row), [])
        row["visual"]["facets"]["expression"]["tags"] = ["微笑"]
        self.assertTrue(self.engine.validate_visual(row))

    def test_facet_filters_are_conjunctive(self):
        rows = [reference("R01"), reference("R02", "室内", "冷光"), reference("R03", "室外", "暖光")]
        found = self.engine.search(rows, filters={"scene": "室外", "lighting": "冷光"})
        self.assertEqual([r["id"] for r in found], ["R01"])

    def test_unknown_scene_does_not_match_indoor_from_uncertainty_text(self):
        row = reference("R01", "场景不明")
        row["visual"]["facets"]["scene"]["observation"] = "无法确定具体室内外"
        self.assertEqual(self.engine.search([row], filters={"scene": "室内"}), [])
        self.assertEqual(len(self.engine.search([row], filters={"scene": "场景不明"})), 1)

    def test_no_match_does_not_fall_back_to_generic_locations(self):
        self.assertEqual(self.engine.search([reference("R01", "咖啡馆")], query="雪地"), [])

    def test_search_can_use_expression_independently_of_scene(self):
        row = reference("R01", "咖啡馆")
        row["visual"]["facets"]["expression"]["tags"] = ["嘴角上扬", "直视"]
        self.assertEqual(self.engine.search([row], filters={"expression": "嘴角上扬"})[0]["id"], "R01")

    def test_unknown_facet_and_empty_intent_fail(self):
        with self.assertRaises(ValueError):
            self.engine.search([reference("R01")], filters={"brand": "unknown"})
        with self.assertRaises(ValueError):
            self.engine.search([reference("R01")])

    def test_exclusion_and_stable_ties_do_not_randomly_pick(self):
        rows = [reference("R12"), reference("R02"), reference("R01")]
        result = self.engine.search(rows, filters={"scene": "室外"}, exclude=["R01"])
        self.assertEqual([r["id"] for r in result], ["R02", "R12"])

    def test_multiple_query_terms_all_need_support(self):
        row = reference("R01", "室外 雪地", "柔光")
        self.assertEqual(len(self.engine.search([row], query="雪地 柔光")), 1)
        self.assertEqual(self.engine.search([row], query="雪地 硬光"), [])


if __name__ == "__main__":
    unittest.main()
