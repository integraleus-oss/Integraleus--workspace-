import tempfile
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
        self.root_patch = patch.object(adapter, "APPROVED_PACKET_ROOT", self.root)
        self.root_patch.start()

    def tearDown(self):
        self.root_patch.stop()
        self.temp.cleanup()

    @patch("openclaw_foreground_adapter.production_cycle_cli.run_packet")
    @patch("openclaw_foreground_adapter.production_cycle_cli.load_packet")
    def test_runs_exactly_one_manual_packet_in_foreground(self, load, run):
        load.return_value = {"schema_version": "1.3.0", "control_mode": "manual"}
        run.return_value = {"status": "ACCEPTED"}
        result = run_one(self.packet)
        self.assertEqual(result["status"], "ACCEPTED")
        run.assert_called_once_with(self.packet.resolve(), foreground_authorized=True)

    @patch("openclaw_foreground_adapter.production_cycle_cli.load_packet")
    def test_rejects_old_or_non_manual_packet(self, load):
        for version, mode in (("1.2.0", "manual"), ("1.3.0", "automatic")):
            load.return_value = {"schema_version": version, "control_mode": mode}
            with self.subTest(version=version, mode=mode), self.assertRaises(AdapterError):
                run_one(self.packet)

    def test_rejects_packet_outside_approved_root(self):
        outside = self.root.parent / "outside-packet.json"
        outside.write_text("{}")
        try:
            with self.assertRaisesRegex(AdapterError, "outside"):
                run_one(outside)
        finally:
            outside.unlink()


if __name__ == "__main__":
    unittest.main()
