#!/usr/bin/env python3
import datetime as dt
import importlib.util
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).with_name("execution-truth-watch.py")
SPEC = importlib.util.spec_from_file_location("execution_truth_watch", SCRIPT)
MOD = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MOD)


class ExecutionTruthTests(unittest.TestCase):
    now = dt.datetime(2026, 9, 1, 15, 30)

    def evidence(self, body: str, packet: bool = True):
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        path = root / "EVIDENCE.md"
        path.write_text(body, encoding="utf-8")
        if packet:
            (root / "TASK_PACKET.md").write_text("# packet\n", encoding="utf-8")
        self.addCleanup(temp.cleanup)
        return path

    def test_terminal_status_is_ignored(self):
        path = self.evidence("Status: SUCCEEDED\n")
        self.assertEqual([], MOD.audit_file(path, self.now, 60))

    def test_missing_process_identity_is_detected(self):
        path = self.evidence("Status: RUNNING\nLast verified: 2026-09-01 15:20\n")
        self.assertIn("missing process/managed-job identity", MOD.audit_file(path, self.now, 60))

    def test_dead_pid_is_detected(self):
        path = self.evidence("Status: RUNNING\nPID: 99999999\nLast verified: 2026-09-01 15:20\n")
        self.assertIn("dead PID", MOD.audit_file(path, self.now, 60))

    def test_stale_evidence_is_detected(self):
        path = self.evidence("Status: RUNNING\nManaged job: taskflow:abc\nLast verified: 2026-09-01 12:00\n")
        self.assertIn("stale evidence", MOD.audit_file(path, self.now, 60))


if __name__ == "__main__":
    unittest.main()
