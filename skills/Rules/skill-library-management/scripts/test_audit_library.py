#!/usr/bin/env python3
"""Behavioral regression checks for library ownership and install mappings."""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from audit_library import audit, file_manifest


class LibraryAuditTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name) / "project"
        self.root = self.project / "skills"
        self.index = self.project / "SKILLS_INDEX.md"
        self.client = Path(self.temp.name) / "client"
        self.client.mkdir()
        self.installed = Path(self.temp.name) / "installed"

    def skill(self, relative, name):
        folder = self.root / relative
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "SKILL.md").write_text(f"---\nname: {name}\ndescription: A test workflow.\n---\n\n# Workflow\n")
        return folder

    def page(self, path, count, entries):
        path.parent.mkdir(parents=True, exist_ok=True)
        text = f"# Skills\n\n技能数量：{count}\n\n"
        text += "".join(f"- [{name}]({target}) — {description}\n" for name, target, description in entries)
        path.write_text(text)

    def layout(self):
        self.skill("video/ai/first", "first")
        self.skill("image/second", "second")
        self.skill("documentation/pack", "router")
        self.skill("documentation/pack/topic", "topic")
        self.skill("documentation/pack/examples/sample", "resource-example")
        self.page(self.root / "video/ai/SKILLS_INDEX.md", 1, [("first", "first/SKILL.md", "Workflow.")])
        self.page(self.root / "video/SKILLS_INDEX.md", 1, [("ai", "ai/SKILLS_INDEX.md", "AI。（1 个技能）")])
        self.page(self.root / "image/SKILLS_INDEX.md", 1, [("second", "second/SKILL.md", "Workflow.")])
        self.page(self.root / "documentation/pack/SKILLS_INDEX.md", 1, [("topic", "topic/SKILL.md", "Topic.")])
        self.page(self.root / "documentation/SKILLS_INDEX.md", 2, [
            ("router", "pack/SKILL.md", "Router."),
            ("topics", "pack/SKILLS_INDEX.md", "Topics。（1 个技能）"),
        ])
        self.page(self.index, 4, [
            ("video", "skills/video/SKILLS_INDEX.md", "Video。（1 个技能）"),
            ("image", "skills/image/SKILLS_INDEX.md", "Image。（1 个技能）"),
            ("documentation", "skills/documentation/SKILLS_INDEX.md", "Docs。（2 个技能）"),
        ])
        self.mapping = {"first": "video/ai/first", "second": "image/second", "router": "documentation/pack", "topic": "documentation/pack/topic"}

    def install(self):
        for name, relative in self.mapping.items():
            dest = self.installed / relative
            if not dest.exists():
                shutil.copytree(self.root / relative, dest)
            (self.client / name).symlink_to(dest)
        self.map_file = self.project / "INSTALL_MAP.json"
        self.map_data = {"installed_root": str(self.installed), "mode": "independent-copy", "skills": dict(self.mapping)}
        self.save_map()

    def save_map(self):
        self.map_file.write_text(json.dumps(self.map_data))

    def check(self, **kwargs):
        return audit(self.root, self.index, **kwargs)

    def fails_with(self, result, reason):
        self.assertFalse(result["ok"], result)
        self.assertTrue(any(reason in error for error in result["errors"]), result)

    def test_optional_subcategories_and_nested_packages(self):
        self.layout()
        result = self.check()
        self.assertTrue(result["ok"], result)
        self.assertEqual((result["skills"], result["reachable_skills"], result["indexes"]), (4, 4, 6))

    def test_flat_leaf_skills_do_not_need_extra_indexes(self):
        self.skill("one", "one")
        self.page(self.index, 1, [("one", "skills/one/SKILL.md", "Workflow.")])
        self.assertTrue(self.check()["ok"])

    def test_spaces_case_backlinks_and_code_examples(self):
        self.layout()
        self.skill("web design/effects/visual", "visual")
        self.page(self.root / "web design/effects/SKILLS_INDEX.md", 1, [("visual", "visual/SKILL.md", "Visual.")])
        self.page(self.root / "web design/SKILLS_INDEX.md", 1, [("effects", "effects/SKILLS_INDEX.md", "Effects.")])
        self.skill("Rules/manage", "manage")
        self.page(self.root / "Rules/SKILLS_INDEX.md", 1, [("manage", "manage/SKILL.md", "Manage.")])
        text = self.index.read_text().replace("技能数量：4", "技能数量：6")
        text += "- [web design](<skills/web design/SKILLS_INDEX.md>) — Visual.\n- [Rules](skills/Rules/SKILLS_INDEX.md) — Management.\n"
        text += "\n```markdown\n技能数量：999\n- [fake](missing/SKILL.md) — Example.\n```\n"
        self.index.write_text(text)
        p = self.root / "video/ai/SKILLS_INDEX.md"
        p.write_text(p.read_text() + "\n[返回总入口](../../../SKILLS_INDEX.md)\n")
        self.assertTrue(self.check()["ok"])

    def test_missing_second_level_index(self):
        self.layout()
        (self.root / "video/ai/SKILLS_INDEX.md").unlink()
        self.fails_with(self.check(), "Missing grouping index")

    def test_incorrect_navigation_count(self):
        self.layout()
        self.index.write_text(self.index.read_text().replace("Video。（1 个技能）", "Video。（9 个技能）"))
        self.fails_with(self.check(), "Wrong navigation count")

    def test_duplicate_ownership(self):
        self.layout()
        self.index.write_text(self.index.read_text() + "- [first again](skills/video/ai/first/SKILL.md) — Duplicate.\n")
        self.fails_with(self.check(), "Duplicate ownership")

    def test_duplicate_skill_names(self):
        self.layout()
        self.skill("image/other", "second")
        self.fails_with(self.check(), "Duplicate skill name")

    def test_unindexed_skill(self):
        self.layout()
        self.skill("image/unlisted", "unlisted")
        self.fails_with(self.check(), "Unindexed skill")

    def test_ownership_cycle(self):
        self.layout()
        p = self.root / "video/SKILLS_INDEX.md"
        p.write_text(p.read_text() + "- [parent](../../SKILLS_INDEX.md) — Ownership cycle.\n")
        self.fails_with(self.check(), "Index navigation cycle")

    def test_wrong_client_target(self):
        self.layout()
        self.install()
        (self.client / "first").unlink()
        (self.client / "first").symlink_to(self.root / "image/second")
        self.fails_with(self.check(link_dirs=[self.client]), "Wrong client target")

    def test_broken_client_target(self):
        self.layout()
        self.install()
        (self.client / "first").unlink()
        (self.client / "first").symlink_to(self.project / "missing")
        self.fails_with(self.check(link_dirs=[self.client]), "Broken client symlink")

    def test_valid_independent_install_map(self):
        self.layout()
        self.install()
        result = self.check(install_map=self.map_file, compare_installed=True)
        self.assertTrue(result["ok"], result)
        self.assertEqual(result["install_map_skills"], 4)
        self.assertTrue(result["installed_compared"])

    def test_map_coverage_and_path_escape(self):
        self.layout()
        self.install()
        del self.map_data["skills"]["second"]
        self.map_data["skills"]["first"] = "../outside"
        self.map_data["skills"]["unknown"] = "image/unknown"
        self.save_map()
        result = self.check(install_map=self.map_file)
        for reason in ["Unmapped skill", "Unknown mapped skill", "Invalid mapped path"]:
            self.fails_with(result, reason)

    def test_wrong_source_mapping(self):
        self.layout()
        self.install()
        self.map_data["skills"]["first"] = "video/first"
        self.save_map()
        self.fails_with(self.check(install_map=self.map_file), "Wrong source mapping")

    def test_development_symlink_is_not_an_independent_copy(self):
        self.layout()
        self.install()
        dest = self.installed / "image/second"
        shutil.rmtree(dest)
        dest.symlink_to(self.root / "image/second")
        self.fails_with(self.check(install_map=self.map_file), "Installed copy is not independent")

    def test_content_permissions_and_extra_files_are_compared(self):
        self.layout()
        self.install()
        p = self.installed / "image/second/SKILL.md"
        p.write_text(p.read_text() + "\nInstalled-only change.\n")
        (p.parent / "extra.txt").write_text("Extra resource")
        self.fails_with(self.check(install_map=self.map_file, compare_installed=True), "Installed copy differs")
        shutil.rmtree(p.parent)
        shutil.copytree(self.root / "image/second", p.parent)
        p.chmod(0o700)
        self.fails_with(self.check(install_map=self.map_file, compare_installed=True), "Installed copy differs")

    def test_caches_and_private_configs_do_not_make_copies_different(self):
        self.layout()
        self.install()
        folder = self.installed / "image/second"
        (folder / ".env.local").write_text("PRIVATE_TEST_VALUE=example")
        (folder / "__pycache__").mkdir()
        (folder / "__pycache__/runtime.pyc").write_bytes(b"cache")
        self.assertTrue(self.check(install_map=self.map_file, compare_installed=True)["ok"])

    def test_cli_is_read_only_and_returns_failure_status(self):
        self.layout()
        before = file_manifest(self.project)
        command = [sys.executable, str(Path(__file__).with_name("audit_library.py")), "--skills-root", str(self.root), "--root-index", str(self.index), "--json"]
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(json.loads(result.stdout)["ok"])
        self.assertEqual(before, file_manifest(self.project))
        self.index.write_text(self.index.read_text().replace("技能数量：4", "技能数量：9"))
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertFalse(json.loads(result.stdout)["ok"])


if __name__ == "__main__":
    unittest.main()
