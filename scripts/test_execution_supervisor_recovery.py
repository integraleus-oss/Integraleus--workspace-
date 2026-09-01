#!/usr/bin/env python3
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SUPERVISOR = Path(__file__).with_name("execution-supervisor.py")
RECOVER_ALL = Path(__file__).with_name("execution-supervisor-recover-all.py")


class RecoveryFallbackTest(unittest.TestCase):
    def test_pending_delivery_then_ack(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); task = root / "task"; task.mkdir()
            evidence = task / "EVIDENCE.md"; evidence.write_text("# t\nStatus: READY\n")
            state = task / "execution-supervisor-state.json"; outbox = task / "outbox.jsonl"
            subprocess.run([sys.executable, str(SUPERVISOR), "run", "--evidence", str(evidence),
                "--state", str(state), "--outbox", str(outbox), "--timeout", "2", "--owner", "test",
                "--", sys.executable, "-c", "pass"], check=True)
            audit = subprocess.run([sys.executable, str(RECOVER_ALL), "--root", str(root)], capture_output=True, text=True)
            self.assertEqual(1, audit.returncode); self.assertIn("PENDING_NOTIFICATION", audit.stdout)
            event = json.loads(outbox.read_text().splitlines()[0])
            subprocess.run([sys.executable, str(SUPERVISOR), "ack", "--state", str(state),
                            "--notification-id", event["id"]], check=True)
            clean = subprocess.run([sys.executable, str(RECOVER_ALL), "--root", str(root)], capture_output=True, text=True)
            self.assertEqual(0, clean.returncode); self.assertIn("SUPERVISOR_RECOVERY_OK", clean.stdout)


if __name__ == "__main__": unittest.main()
