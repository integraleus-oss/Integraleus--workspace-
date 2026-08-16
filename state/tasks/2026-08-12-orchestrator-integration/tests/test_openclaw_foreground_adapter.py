import tempfile
import hashlib
import json
import unittest
from pathlib import Path
from unittest.mock import patch

import openclaw_foreground_adapter as adapter
from openclaw_foreground_adapter import AdapterError, run_one


class ForegroundAdapterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.packet = self.root / "task.json"
        self.packet.write_text("{}")
        self.authorization = self.root / "authorization.json"
        self.authorization.write_text(json.dumps({
            "document_type": "manual_foreground_authorization", "schema_version": "1.0.0",
            "packet_digest": "sha256:" + hashlib.sha256(self.packet.read_bytes()).hexdigest(),
            "approved_by": "Stanislav Pavlovskiy", "source_message_id": "3293"}))
        self.registry = self.root / "registry.json"
        self.registry.write_text(json.dumps({"authorizations": [{
            "authorization_digest": "sha256:" + hashlib.sha256(self.authorization.read_bytes()).hexdigest(),
            "packet_digest": "sha256:" + hashlib.sha256(self.packet.read_bytes()).hexdigest(),
            "source_message_id": "3293"}]}))
        self.root_patch = patch.object(adapter, "APPROVED_PACKET_ROOT", self.root)
        self.root_patch.start()
        self.registry_patch = patch.object(adapter, "AUTHORIZATION_REGISTRY", self.registry)
        self.registry_patch.start()
        self.ledger_patch = patch.object(adapter, "AUTHORIZATION_LEDGER", self.root / "used")
        self.ledger_patch.start()

    def tearDown(self):
        self.ledger_patch.stop()
        self.registry_patch.stop()
        self.root_patch.stop()
        self.temp.cleanup()

    @patch("openclaw_foreground_adapter.production_cycle_cli.run_packet")
    @patch("openclaw_foreground_adapter.production_cycle_cli.load_packet")
    def test_runs_exactly_one_manual_packet_in_foreground(self, load, run):
        load.return_value = {"schema_version": "1.3.0", "control_mode": "manual"}
        run.return_value = {"status": "ACCEPTED"}
        result = run_one(self.packet, self.authorization)
        self.assertEqual(result["status"], "ACCEPTED")
        self.assertTrue(Path(result["manual_authorization_marker"]).is_file())
        run.assert_called_once_with(self.packet.resolve(), foreground_authorized=True)

    @patch("openclaw_foreground_adapter.production_cycle_cli.run_packet", return_value={"status": "ACCEPTED"})
    @patch("openclaw_foreground_adapter.production_cycle_cli.load_packet",
           return_value={"schema_version": "1.3.0", "control_mode": "manual"})
    def test_authorization_copy_cannot_replay(self, load, run):
        run_one(self.packet, self.authorization)
        copied = self.root / "copied-authorization.json"
        copied.write_bytes(self.authorization.read_bytes())
        with self.assertRaisesRegex(AdapterError, "already used"):
            run_one(self.packet, copied)

    @patch("openclaw_foreground_adapter.production_cycle_cli.load_packet")
    def test_rejects_old_or_non_manual_packet(self, load):
        for version, mode in (("1.2.0", "manual"), ("1.3.0", "automatic")):
            load.return_value = {"schema_version": version, "control_mode": mode}
            with self.subTest(version=version, mode=mode), self.assertRaises(AdapterError):
                run_one(self.packet, self.authorization)

    def test_rejects_packet_outside_approved_root(self):
        outside = self.root.parent / "outside-packet.json"
        outside.write_text("{}")
        try:
            with self.assertRaisesRegex(AdapterError, "outside"):
                run_one(outside, self.authorization)
        finally:
            outside.unlink()


if __name__ == "__main__":
    unittest.main()
