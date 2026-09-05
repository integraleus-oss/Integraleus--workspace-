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
            launched = subprocess.run([sys.executable, str(SUPERVISOR), "run", "--evidence", str(evidence),
                "--state", str(state), "--outbox", str(outbox), "--timeout", "2", "--owner", "test",
                "--", sys.executable, "-c", "pass"])
            self.assertEqual(4, launched.returncode)
            audit = subprocess.run([sys.executable, str(RECOVER_ALL), "--root", str(root)], capture_output=True, text=True)
            self.assertEqual(1, audit.returncode); self.assertIn("PENDING_NOTIFICATION", audit.stdout)
            event = json.loads(outbox.read_text().splitlines()[0])
            subprocess.run([sys.executable, str(SUPERVISOR), "ack", "--state", str(state),
                            "--notification-id", event["id"]], check=True)
            clean = subprocess.run([sys.executable, str(RECOVER_ALL), "--root", str(root)], capture_output=True, text=True)
            self.assertEqual(0, clean.returncode); self.assertIn("SUPERVISOR_RECOVERY_OK", clean.stdout)

    def test_unsafe_terminal_delivered_legacy_state_is_nonfatal(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); task = root / "legacy"; task.mkdir()
            state = task / "execution-supervisor-state.json"
            state.write_text(json.dumps({
                "status": "SUCCEEDED",
                "statePath": str(state.resolve()),
                "outboxPath": str((task / "legacy-notification-outbox.jsonl").resolve()),
                "evidencePath": str((task / "EVIDENCE.md").resolve()),
                "notificationId": "legacy-success",
                "notificationDelivered": True,
            }))
            result = subprocess.run([sys.executable, str(RECOVER_ALL), "--root", str(root)], capture_output=True, text=True)
            self.assertEqual(0, result.returncode)
            self.assertIn("RECOVERY_SKIPPED_UNSAFE_TERMINAL", result.stdout)

    def test_unsafe_pending_legacy_state_still_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); task = root / "legacy"; task.mkdir()
            state = task / "execution-supervisor-state.json"
            state.write_text(json.dumps({
                "status": "SUCCEEDED",
                "statePath": str(state.resolve()),
                "outboxPath": str((task / "legacy-notification-outbox.jsonl").resolve()),
                "evidencePath": str((task / "EVIDENCE.md").resolve()),
                "notificationId": "legacy-success",
                "notificationDelivered": False,
            }))
            result = subprocess.run([sys.executable, str(RECOVER_ALL), "--root", str(root)], capture_output=True, text=True)
            self.assertEqual(2, result.returncode)
            self.assertIn("RECOVERY_FAILED", result.stdout)


if __name__ == "__main__": unittest.main()
