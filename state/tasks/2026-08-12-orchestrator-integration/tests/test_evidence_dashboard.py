import json
import tempfile
import unittest
from pathlib import Path

from evidence_dashboard import DashboardError, file_digest, generate_dashboard


class EvidenceDashboardTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.evidence = self.root / "evidence.json"
        self.value = {"stage": "blind_acceptance", "terminal_state": "ACCEPTED", "attempts": 1,
                      "cycles": 2, "duration_ms": 1234,
                      "requirements": [{"requirement_id": "R01", "outcome": "pass", "evidence": "test"}],
                      "tasks": [{"task_id": "task", "requirement_ids": ["R01"], "status": "done"}],
                      "tests": [{"gate_id": "unit", "status": "PASS", "details": "10/10"}],
                      "review_findings": [], "artifacts": [{"label": "result", "path": "result.json"}]}
        self.evidence.write_text(json.dumps(self.value), encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def test_generates_static_digest_labelled_view(self):
        output = self.root / "dashboard.html"
        generate_dashboard(self.evidence, output, file_digest(self.evidence))
        text = output.read_text()
        self.assertIn("1/1", text)
        self.assertIn("ACCEPTED", text)
        self.assertIn(file_digest(self.evidence), text)
        self.assertNotIn("<script", text)

    def test_digest_mismatch_and_overwrite_fail_closed(self):
        with self.assertRaisesRegex(DashboardError, "digest mismatch"):
            generate_dashboard(self.evidence, self.root / "bad.html", "sha256:" + "0" * 64)
        output = self.root / "existing.html"
        output.write_text("user data")
        with self.assertRaisesRegex(DashboardError, "must be new"):
            generate_dashboard(self.evidence, output, file_digest(self.evidence))

    def test_escapes_untrusted_evidence(self):
        self.value["terminal_state"] = "<script>alert(1)</script>"
        self.evidence.write_text(json.dumps(self.value), encoding="utf-8")
        output = self.root / "escaped.html"
        generate_dashboard(self.evidence, output, file_digest(self.evidence))
        text = output.read_text()
        self.assertNotIn("<script>alert", text)
        self.assertIn("&lt;script&gt;", text)


if __name__ == "__main__":
    unittest.main()
