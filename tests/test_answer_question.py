import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "answer_question.py"
SPEC = importlib.util.spec_from_file_location("answer_question", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class AnswerQuestionTest(unittest.TestCase):
    def test_question_from_issue_uses_title_and_body(self):
        event = {"issue": {"title": "[Knowledge] Agent changes", "body": "What changed?"}}
        question = MODULE.question_from_event(event)
        self.assertIn("Agent changes", question)
        self.assertIn("What changed?", question)

    def test_question_from_follow_up_removes_ask_command(self):
        event = {"issue": {}, "comment": {"body": "/ask What about organizations?"}}
        self.assertEqual(MODULE.question_from_event(event), "What about organizations?")

    def test_rank_candidates_prefers_matching_vector(self):
        items = [
            {"id": "close", "title": "agents", "summary": "", "entities": [], "claims": []},
            {"id": "far", "title": "other", "summary": "", "entities": [], "claims": []},
        ]
        ranked = MODULE.rank_candidates(
            "agents",
            [1.0, 0.0],
            items,
            {"close": [1.0, 0.0], "far": [0.0, 1.0]},
            2,
        )
        self.assertEqual(ranked[0][1]["id"], "close")

    def test_render_answer_appends_verified_repository_and_source_links(self):
        item = {
            "id": "item-1",
            "title": "A release",
            "event_date": "2026-08-23",
            "source_path": "aI_knowledge/2026/0823.md",
            "source_urls": ["https://example.com/source"],
            "summary": "summary",
            "entities": [],
            "claims": [],
        }
        rendered = MODULE.render_answer(
            {
                "answer_markdown": "Answer [K1]",
                "cited_item_ids": ["item-1", "unknown"],
                "insufficient_knowledge": False,
            },
            [(0.9, item)],
            repository="owner/repo",
            knowledge_generated_at="2026-08-23T00:00:00Z",
        )
        self.assertIn("https://github.com/owner/repo/blob/main/aI_knowledge/2026/0823.md", rendered)
        self.assertIn("https://example.com/source", rendered)
        self.assertNotIn("unknown", rendered)


if __name__ == "__main__":
    unittest.main()
