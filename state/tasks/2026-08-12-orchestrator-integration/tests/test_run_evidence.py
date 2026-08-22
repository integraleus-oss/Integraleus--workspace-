import json
import tempfile
import unittest
from pathlib import Path

from run_evidence import EvidenceError, EvidenceStream


class RunEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "RUN_EVIDENCE.jsonl"

    def tearDown(self):
        self.temp.cleanup()

    def test_create_and_append_are_versioned_monotonic_and_append_only(self):
        stream = EvidenceStream.create(self.path, task_id="task-1", profile="standard")
        stream.append("agent_launch", {"role": "codex", "status": "OK", "duration_ms": 12})
        stream.append("terminal", {"status": "ACCEPTED"})
        events = [json.loads(line) for line in self.path.read_text().splitlines()]
        self.assertEqual([item["sequence"] for item in events], [1, 2, 3])
        self.assertEqual({item["schema_version"] for item in events}, {"1.0.0"})
        self.assertEqual(events[0]["event"], "start")
        self.assertEqual(events[-1]["event"], "terminal")
        with self.assertRaises(EvidenceError):
            EvidenceStream.create(self.path, task_id="task-1", profile="standard")

    def test_open_rejects_malformed_or_non_monotonic_stream(self):
        self.path.write_text('{"sequence":2}\n', encoding="utf-8")
        with self.assertRaises(EvidenceError):
            EvidenceStream.open(self.path)
        self.path.write_text("not json\n", encoding="utf-8")
        with self.assertRaises(EvidenceError):
            EvidenceStream.open(self.path)

    def test_payload_rejects_secrets_prompts_and_unsupported_values(self):
        stream = EvidenceStream.create(self.path, task_id="task-1", profile="standard")
        for payload in ({"prompt": "private"}, {"api_key": "secret"}, {"value": object()},
                        {"value": float("nan")}):
            with self.subTest(payload=payload):
                with self.assertRaises(EvidenceError):
                    stream.append("agent_launch", payload)
        self.assertEqual(len(self.path.read_text().splitlines()), 1)

    def test_terminal_is_single_and_seals_stream(self):
        stream = EvidenceStream.create(self.path, task_id="task-1", profile="standard")
        stream.append("terminal", {"status": "INTERRUPTED", "exit_code": 130})
        with self.assertRaises(EvidenceError):
            stream.append("terminal", {"status": "ERROR"})
        with self.assertRaises(EvidenceError):
            stream.append("gate", {"status": "PASS"})

    def test_append_rejects_stream_tampering_after_creation(self):
        stream = EvidenceStream.create(self.path, task_id="task-1", profile="standard")
        original = self.path.read_text()
        self.path.write_text(original.replace('"task-1"', '"task-2"'), encoding="utf-8")
        with self.assertRaises(EvidenceError):
            stream.append("terminal", {"status": "ERROR"})
        self.assertEqual(len(self.path.read_text().splitlines()), 1)


if __name__ == "__main__":
    unittest.main()
