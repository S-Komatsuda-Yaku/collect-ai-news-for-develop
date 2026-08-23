import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "update_knowledge.py"
SPEC = importlib.util.spec_from_file_location("update_knowledge", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class KnowledgeIndexTest(unittest.TestCase):
    def test_parse_markdown_extracts_only_numbered_h2_sections(self):
        content = """---
date: 2026-08-23
---
## 今日の注目ポイント
summary
## 1. Model X released
- **発表日:** 2026-08-22
- **出典:** [Official](https://example.com/release)
## 確認した主要情報源
sources
"""
        with tempfile.TemporaryDirectory(dir=MODULE.ROOT) as directory:
            path = Path(directory) / "0823.md"
            path.write_text(content, encoding="utf-8")
            article = MODULE.parse_markdown(path)[0]
        self.assertEqual(article["title"], "Model X released")
        self.assertEqual(article["event_date"], "2026-08-22")
        self.assertEqual(article["source_urls"], ["https://example.com/release"])

    def test_high_confidence_update_supersedes_old_item(self):
        old = {"id": "old", "status": "active", "superseded_by": None}
        new = {"id": "new"}
        MODULE.apply_relation(
            [old],
            new,
            {"relation": "update", "target_id": "old", "confidence": 0.95, "reason": "GA release"},
            0.90,
        )
        self.assertEqual(old["status"], "superseded")
        self.assertEqual(old["superseded_by"], "new")
        self.assertEqual(new["status"], "active")
        self.assertEqual(new["supersedes"], ["old"])

    def test_low_confidence_update_keeps_both_items_active(self):
        old = {"id": "old", "status": "active", "superseded_by": None}
        new = {"id": "new"}
        MODULE.apply_relation(
            [old],
            new,
            {"relation": "update", "target_id": "old", "confidence": 0.70, "reason": "maybe"},
            0.90,
        )
        self.assertEqual(old["status"], "active")
        self.assertEqual(new["status"], "active")
        self.assertFalse(new["automatic_action_applied"])

    def test_duplicate_keeps_old_item_active(self):
        old = {"id": "old", "status": "active", "superseded_by": None}
        new = {"id": "new"}
        MODULE.apply_relation(
            [old],
            new,
            {"relation": "duplicate", "target_id": "old", "confidence": 0.97, "reason": "same facts"},
            0.90,
        )
        self.assertEqual(old["status"], "active")
        self.assertEqual(new["status"], "duplicate")


if __name__ == "__main__":
    unittest.main()
