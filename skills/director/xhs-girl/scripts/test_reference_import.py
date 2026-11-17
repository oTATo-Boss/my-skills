"""Exercise original-photo intake through the package validation CLI."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]


class OriginalPhotoTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "skill"
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns("__pycache__"))
        self.manifest = self.root / "assets/reference-covers/manifest.json"
        self.rows = json.loads(self.manifest.read_text())
        self.photo_rows = []
        for index, (suffix, fmt) in enumerate([( ".jpg", "JPEG"), (".png", "PNG"), (".webp", "WEBP")]):
            ref = f"R{len(self.rows) + 1:02d}"
            relative = f"assets/reference-covers/{ref}-original{suffix}"
            path = self.root / relative
            Image.new("RGB", (64 + index, 80), (20 + index, 60, 90)).save(path, format=fmt)
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            row = dict(id=ref, title="原图测试", file=relative,
                       origin_kind="original-image", source_file=f"download-{index}{suffix}",
                       source_size=[64 + index, 80], crop=[0, 0, 64 + index, 80],
                       source_sha256=digest, asset_sha256=digest,
                       batch="test-originals", tags=["近脸"], partial=False)
            self.rows.append(row)
            self.photo_rows.append(row)
        self.save()

    def save(self):
        self.manifest.write_text(json.dumps(self.rows, ensure_ascii=False))

    def check(self):
        return subprocess.run([sys.executable, "-B", str(self.root / "scripts/check_package.py")],
                              capture_output=True, text=True,
                              env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})

    def test_accepts_jpeg_png_and_webp_originals(self):
        result = self.check()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_rejects_missing_original_filename(self):
        self.photo_rows[0].pop("source_file")
        self.save()
        result = self.check()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("Invalid original source filename", result.stdout)

    def test_rejects_changed_original_bytes(self):
        row = self.photo_rows[1]
        Image.new("RGB", (65, 80), "red").save(self.root / row["file"])
        result = self.check()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("Original bytes differ", result.stdout)

    def test_decodes_webp_instead_of_only_jpegs(self):
        row = self.photo_rows[2]
        path = self.root / row["file"]
        path.write_bytes(b"broken-webp")
        row["source_sha256"] = row["asset_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
        self.save()
        result = self.check()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("Invalid image", result.stdout)

    def test_original_dimensions_must_match_metadata(self):
        self.photo_rows[0]["source_size"] = [640, 800]
        self.photo_rows[0]["crop"] = [0, 0, 640, 800]
        self.save()
        result = self.check()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("Original dimensions differ", result.stdout)


if __name__ == "__main__":
    unittest.main()
