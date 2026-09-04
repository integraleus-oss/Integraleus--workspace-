#!/usr/bin/env python3
import json
import hashlib
import base64
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

SCRIPT = Path(__file__).with_name("execution-supervisor.py")


class SupervisorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.root = Path(self.temp.name)
        self.evidence = self.root / "EVIDENCE.md"; self.evidence.write_text("# Test\n\nStatus: READY\n", encoding="utf-8")
        self.state = self.root / "execution-supervisor-state.json"; self.outbox = self.root / "outbox.jsonl"; self.terminal = self.root / "RESULT.json"
        self.private_key = Ed25519PrivateKey.generate()
        self.private_der = self.private_key.private_bytes(serialization.Encoding.DER, serialization.PrivateFormat.PKCS8, serialization.NoEncryption())
        self.public_b64 = base64.b64encode(self.private_key.public_key().public_bytes(serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo)).decode()

    def tearDown(self): self.temp.cleanup()

    def launch(self, code, timeout=2, terminal=False, strict=False):
        command = [sys.executable, str(SCRIPT), "run", "--evidence", str(self.evidence), "--state", str(self.state),
                   "--outbox", str(self.outbox), "--timeout", str(timeout), "--poll", ".02", "--owner", "test"]
        if terminal: command += ["--terminal-evidence", str(self.terminal)]
        if strict: command += ["--require-validated-terminal"]
        command += ["--", sys.executable, "-c", code]
        if terminal:
            read_fd, write_fd = os.pipe(); os.write(write_fd, self.private_der); os.close(write_fd)
            env = os.environ.copy(); env["MANAGED_SUPERVISOR_PRIVATE_FD"] = str(read_fd)
            try: return subprocess.run(command, capture_output=True, text=True, timeout=8, env=env, pass_fds=(read_fd,))
            finally: os.close(read_fd)
        return subprocess.run(command, capture_output=True, text=True, timeout=8)

    def status(self): return json.loads(self.state.read_text())["status"]

    def signed_child(self, status, exit_code=0, summary=None):
        return ("import base64,json,os,pathlib; from cryptography.hazmat.primitives.serialization import load_der_private_key; "
                "k=load_der_private_key(os.read(int(os.environ['MANAGED_TERMINAL_FD']),256),None); "
                "n=os.environ['MANAGED_RUN_NONCE']; "
                f"s={status!r}; c={exit_code}; m={summary!r}; p=json.dumps([s,True,c,n,None,None,None,None,m,None,None,None,None],ensure_ascii=False,separators=(',',':')).encode(); "
                f"pathlib.Path({str(self.terminal)!r}).write_text(json.dumps({{'terminalStatus':s,'contractValidated':True,'exitCode':c,'runNonce':n,'taskDigest':None,'planDigest':None,'outcomeDigest':None,'finishedAt':None,'summary':m,'slices':None,'outcomePath':None,'agentOutputPath':None,'independentReviewPaths':None,'terminalSignature':base64.b64encode(k.sign(p)).decode()}},ensure_ascii=False))")

    def test_exit_zero_without_objective_contract_fails(self): self.assertEqual(4, self.launch("pass").returncode); self.assertEqual("FAILED", self.status())
    def test_child_cannot_forge_success_in_state(self):
        forged = {"status": "SUCCEEDED", "exitCode": 0}
        code = f"import json,pathlib; p=pathlib.Path({str(self.state)!r}); s=json.loads(p.read_text()); s.update({forged!r}); p.write_text(json.dumps(s))"
        self.assertEqual(4, self.launch(code, terminal=True, strict=True).returncode)
        self.assertEqual("FAILED", self.status())
    def test_strict_exit_zero_without_validated_terminal_fails(self):
        self.assertEqual(4, self.launch("pass", terminal=True, strict=True).returncode); self.assertEqual("FAILED", self.status())
    def test_malformed_terminal_signature_fails_closed(self):
        code = f"import json,os,pathlib; pathlib.Path({str(self.terminal)!r}).write_text(json.dumps({{'terminalStatus':'SUCCEEDED','contractValidated':True,'exitCode':0,'runNonce':os.environ['MANAGED_RUN_NONCE'],'terminalSignature':'invalid'}}))"
        self.assertEqual(4, self.launch(code, terminal=True, strict=True).returncode)
        self.assertEqual("FAILED", self.status())
    def test_strict_validated_terminal_succeeds(self):
        code = self.signed_child("SUCCEEDED")
        self.assertEqual(0, self.launch(code, terminal=True, strict=True).returncode); self.assertEqual("SUCCEEDED", self.status())
        state = json.loads(self.state.read_text()); self.assertRegex(state["runNonce"], r"^[a-f0-9]{32}$"); self.assertEqual(state["terminalPublicKey"], self.public_b64); self.assertTrue(state["terminalKeyId"])
        self.assertEqual(state["runNonce"], json.loads(self.terminal.read_text())["runNonce"])
    def test_utf8_summary_signature_succeeds(self):
        self.assertEqual(0, self.launch(self.signed_child("SUCCEEDED", summary="Готово: план выполнен"), terminal=True, strict=True).returncode)
        self.assertEqual("SUCCEEDED", self.status())
    def test_forged_terminal_is_not_accepted_while_child_is_running(self):
        code = f"import json,pathlib,time; pathlib.Path({str(self.terminal)!r}).write_text(json.dumps({{'terminalStatus':'SUCCEEDED','contractValidated':True,'terminalNonce':'forged'}})); time.sleep(2)"
        self.assertEqual(124, self.launch(code, timeout=.05, terminal=True, strict=True).returncode)
        self.assertEqual("TIMED_OUT", self.status())
    def test_strict_stale_terminal_is_removed_before_launch(self):
        self.terminal.write_text(json.dumps({"terminalStatus": "SUCCEEDED", "contractValidated": True, "terminalNonce": "stale"}))
        self.assertEqual(4, self.launch("pass", terminal=True, strict=True).returncode); self.assertEqual("FAILED", self.status())
    def test_signed_terminal_from_prior_run_is_rejected(self):
        self.assertEqual(0, self.launch(self.signed_child("SUCCEEDED"), terminal=True, strict=True).returncode)
        stale = self.terminal.read_text()
        code = f"import pathlib; pathlib.Path({str(self.terminal)!r}).write_text({stale!r})"
        self.assertEqual(4, self.launch(code, terminal=True, strict=True).returncode)
        self.assertEqual("FAILED", self.status())
    def test_crash(self): self.assertEqual(4, self.launch("raise SystemExit(7)").returncode); self.assertEqual("CRASHED", self.status())
    def test_timeout(self): self.assertEqual(124, self.launch("import time; time.sleep(2)", .05).returncode); self.assertEqual("TIMED_OUT", self.status())
    def test_escalation_terminal_evidence(self):
        code = self.signed_child("ESCALATED", 4)
        self.assertEqual(4, self.launch(code, terminal=True).returncode); self.assertEqual("ESCALATED", self.status())
    def test_blocked_terminal_evidence(self):
        code = self.signed_child("BLOCKED", 4)
        self.assertEqual(4, self.launch(code, terminal=True).returncode); self.assertEqual("BLOCKED", self.status())
    def test_notification_exactly_once_after_recovery(self):
        self.launch("pass"); before = self.outbox.read_text().splitlines()
        subprocess.run([sys.executable, str(SCRIPT), "recover", "--state", str(self.state), "--terminal-public-key", self.public_b64], check=True)
        self.assertEqual(before, self.outbox.read_text().splitlines())
    def test_outbox_deduplicates_after_state_intent_loss(self):
        self.launch("pass"); before = self.outbox.read_text().splitlines()
        state = json.loads(self.state.read_text()); state["notificationId"] = None; state["notificationDelivered"] = False
        self.state.write_text(json.dumps(state))
        subprocess.run([sys.executable, str(SCRIPT), "recover", "--state", str(self.state), "--terminal-public-key", self.public_b64], check=True)
        self.assertEqual(before, self.outbox.read_text().splitlines())
    def test_delivery_ack_is_persisted(self):
        self.launch("pass"); event = json.loads(self.outbox.read_text().splitlines()[0])
        result = subprocess.run([sys.executable, str(SCRIPT), "ack", "--state", str(self.state), "--notification-id", event["id"]])
        self.assertEqual(0, result.returncode); self.assertTrue(json.loads(self.state.read_text())["notificationDelivered"])

    def test_delivery_claim_is_interprocess_safe(self):
        self.launch("pass"); event = json.loads(self.outbox.read_text().splitlines()[0])
        first = subprocess.run([sys.executable, str(SCRIPT), "claim-delivery", "--state", str(self.state),
                                "--notification-id", event["id"]], capture_output=True, text=True)
        second = subprocess.run([sys.executable, str(SCRIPT), "claim-delivery", "--state", str(self.state),
                                 "--notification-id", event["id"]])
        self.assertEqual(0, first.returncode); self.assertEqual(3, second.returncode)
        wrong = subprocess.run([sys.executable, str(SCRIPT), "ack", "--state", str(self.state),
                                "--notification-id", event["id"], "--claim-id", "wrong"])
        self.assertEqual(3, wrong.returncode)
        accepted = subprocess.run([sys.executable, str(SCRIPT), "ack", "--state", str(self.state),
                                   "--notification-id", event["id"], "--claim-id", first.stdout.strip()])
        self.assertEqual(0, accepted.returncode); self.assertTrue(json.loads(self.state.read_text())["notificationDelivered"])

    def test_delivery_context_is_persisted(self):
        delivery = {"channel": "telegram", "accountId": "default", "to": "telegram:-100:topic:14", "threadId": 14}
        command = [sys.executable, str(SCRIPT), "run", "--evidence", str(self.evidence), "--state", str(self.state),
                   "--outbox", str(self.outbox), "--timeout", "2", "--owner", "test",
                   "--session-key", "agent:main:test", "--delivery-json", json.dumps(delivery),
                   "--", sys.executable, "-c", "pass"]
        result = subprocess.run(command, capture_output=True, text=True, timeout=8)
        self.assertEqual(4, result.returncode, result.stderr)
        self.assertEqual(delivery, json.loads(self.state.read_text())["deliveryContext"])

    def test_recovery_fails_closed_without_live_private_trust_root(self):
        private = Ed25519PrivateKey.generate(); public = private.public_key().public_bytes(serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo)
        nonce = "0123456789abcdef0123456789abcdef"
        payload = json.dumps(["SUCCEEDED", True, 0, nonce, None, None, None, None, None, None, None, None, None], separators=(",", ":")).encode()
        self.terminal.write_text(json.dumps({"terminalStatus": "SUCCEEDED", "contractValidated": True,
                                             "terminalSignature": base64.b64encode(private.sign(payload)).decode(), "exitCode": 0, "runNonce": nonce}))
        state = {"schemaVersion": 1, "runId": "recover-success", "status": "RUNNING",
                 "startedAt": "2026-09-04T12:00:00+03:00", "lastVerified": "2026-09-04T12:00:00+03:00",
                 "finishedAt": None, "pid": 99999999, "pidStartTicks": 1, "exitCode": None,
                 "command": [sys.executable, "/tmp/custom-runner.mjs", "--result", str(self.terminal)],
                 "timeoutSeconds": 3600, "evidencePath": str(self.evidence), "statePath": str(self.state),
                 "terminalEvidencePath": str(self.terminal), "outboxPath": str(self.outbox),
                 "notificationId": None, "notificationDelivered": False, "owner": "test", "flowId": "flow",
                 "sessionKey": "test", "requireValidatedTerminal": True,
                 "terminalKeyId": hashlib.sha256(public).hexdigest(), "runNonce": nonce, "deliveryContext": None}
        self.state.write_text(json.dumps(state))
        subprocess.run([sys.executable, str(SCRIPT), "recover", "--state", str(self.state),
                        "--terminal-public-key", self.public_b64], check=True)
        self.assertEqual("CRASHED", self.status())

    def test_recovery_preserves_persisted_success_and_delivery_ack(self):
        self.assertEqual(0, self.launch(self.signed_child("SUCCEEDED"), terminal=True, strict=True).returncode)
        event = json.loads(self.outbox.read_text().splitlines()[0])
        subprocess.run([sys.executable, str(SCRIPT), "ack", "--state", str(self.state), "--notification-id", event["id"]], check=True)
        before = self.outbox.read_text()
        subprocess.run([sys.executable, str(SCRIPT), "recover", "--state", str(self.state),
                        "--terminal-public-key", self.public_b64], check=True)
        recovered = json.loads(self.state.read_text())
        self.assertEqual("SUCCEEDED", recovered["status"]); self.assertTrue(recovered["notificationDelivered"])
        self.assertEqual(before, self.outbox.read_text())

    def test_recovery_revalidates_delivered_success(self):
        self.assertEqual(0, self.launch(self.signed_child("SUCCEEDED"), terminal=True, strict=True).returncode)
        event = json.loads(self.outbox.read_text().splitlines()[0])
        subprocess.run([sys.executable, str(SCRIPT), "ack", "--state", str(self.state), "--notification-id", event["id"]], check=True)
        self.terminal.write_text(json.dumps({"terminalStatus": "SUCCEEDED", "contractValidated": True, "exitCode": 0,
                                             "runNonce": "forged", "terminalSignature": "invalid"}))
        subprocess.run([sys.executable, str(SCRIPT), "recover", "--state", str(self.state),
                        "--terminal-public-key", self.public_b64], check=True)
        self.assertEqual("CRASHED", self.status())

    def test_corrupt_state_does_not_orphan_runner(self):
        code = f"import pathlib,time; time.sleep(.1); pathlib.Path({str(self.state)!r}).write_text('{{'); time.sleep(7)"
        result = self.launch(code, timeout=6, terminal=True, strict=True)
        self.assertEqual(4, result.returncode); self.assertEqual("FAILED", self.status())


if __name__ == "__main__": unittest.main()
