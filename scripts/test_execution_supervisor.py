#!/usr/bin/env python3
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).with_name("execution-supervisor.py")


class SupervisorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.root = Path(self.temp.name)
        self.evidence = self.root / "EVIDENCE.md"; self.evidence.write_text("# Test\n\nStatus: READY\n", encoding="utf-8")
        self.state = self.root / "state.json"; self.outbox = self.root / "outbox.jsonl"; self.terminal = self.root / "terminal.json"

    def tearDown(self): self.temp.cleanup()

    def launch(self, code, timeout=2, terminal=False):
        command = [sys.executable, str(SCRIPT), "run", "--evidence", str(self.evidence), "--state", str(self.state),
                   "--outbox", str(self.outbox), "--timeout", str(timeout), "--poll", ".02", "--owner", "test"]
        if terminal: command += ["--terminal-evidence", str(self.terminal)]
        command += ["--", sys.executable, "-c", code]
        return subprocess.run(command, capture_output=True, text=True, timeout=8)

    def status(self): return json.loads(self.state.read_text())["status"]

    def test_success(self): self.assertEqual(0, self.launch("pass").returncode); self.assertEqual("SUCCEEDED", self.status())
    def test_crash(self): self.assertEqual(4, self.launch("raise SystemExit(7)").returncode); self.assertEqual("CRASHED", self.status())
    def test_timeout(self): self.assertEqual(124, self.launch("import time; time.sleep(2)", .05).returncode); self.assertEqual("TIMED_OUT", self.status())
    def test_escalation_terminal_evidence(self):
        code = f"import json,pathlib,time; pathlib.Path({str(self.terminal)!r}).write_text(json.dumps({{'status':'ESCALATED'}})); time.sleep(2)"
        self.assertEqual(4, self.launch(code, terminal=True).returncode); self.assertEqual("ESCALATED", self.status())
    def test_notification_exactly_once_after_recovery(self):
        self.launch("pass"); before = self.outbox.read_text().splitlines()
        subprocess.run([sys.executable, str(SCRIPT), "recover", "--state", str(self.state)], check=True)
        self.assertEqual(before, self.outbox.read_text().splitlines())
    def test_delivery_ack_is_persisted(self):
        self.launch("pass"); event = json.loads(self.outbox.read_text().splitlines()[0])
        result = subprocess.run([sys.executable, str(SCRIPT), "ack", "--state", str(self.state), "--notification-id", event["id"]])
        self.assertEqual(0, result.returncode); self.assertTrue(json.loads(self.state.read_text())["notificationDelivered"])


if __name__ == "__main__": unittest.main()
