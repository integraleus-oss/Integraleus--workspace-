import json
import tempfile
import unittest
from pathlib import Path

from trusted_test_broker import GateFailure, reset_writable_dirs, run_sealed_gate


class TrustedTestBrokerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "repo"
        self.out = Path(self.temp.name) / "evidence"
        self.root.mkdir()

    def tearDown(self):
        self.temp.cleanup()

    def test_passes_deterministic_execution_context(self):
        gate = {"id": "context", "argv": ["python3", "-c",
            "import os,sys; sys.exit(0 if os.environ['ORCHESTRATOR_PROJECT_ROOT'] == os.getcwd() "
            "and os.environ['ORCHESTRATOR_FIXTURE_ROOT'] == os.getcwd() else 1)"]}
        record = run_sealed_gate(self.root, gate, self.out, 10)
        self.assertEqual((record["exit_code"], record["timed_out"]), (0, False))

    def test_exit_one_is_repairable_and_evidence_is_bounded(self):
        gate = {"id": "focused", "argv": ["python3", "-c",
            "import sys; print('assertion failed'); sys.exit(1)"]}
        with self.assertRaises(GateFailure) as raised:
            run_sealed_gate(self.root, gate, self.out, 10)
        failure = raised.exception
        self.assertEqual(failure.classification, "IMPLEMENTATION_FAILURE")
        self.assertIn("assertion failed", failure.repair_packet)
        record = json.loads((self.out / "gates/focused/result.json").read_text())
        self.assertEqual(record["exit_code"], 1)

        bounded_out = Path(self.temp.name) / "bounded-evidence"
        noisy = {"id": "noisy", "argv": ["python3", "-c",
            "import sys; print('Ж' * 10000); sys.exit(1)"]}
        with self.assertRaises(GateFailure) as bounded:
            run_sealed_gate(self.root, noisy, bounded_out, 10)
        self.assertLess(len(bounded.exception.repair_packet.encode("utf-8")), 8192)

    def test_tool_or_timeout_failure_is_not_repairable(self):
        gate = {"id": "tool", "argv": ["python3", "-c", "raise SystemExit(127)"]}
        with self.assertRaises(GateFailure) as raised:
            run_sealed_gate(self.root, gate, self.out, 10)
        self.assertEqual(raised.exception.classification, "INFRASTRUCTURE_FAILURE")
        self.assertIsNone(raised.exception.repair_packet)

    def test_shell_signal_and_test_count_mismatch_are_not_repairable(self):
        signal_gate = {"id": "signal", "argv": ["bash", "-lc", "exit 137"]}
        with self.assertRaises(GateFailure) as signal_failure:
            run_sealed_gate(self.root, signal_gate, self.out, 10)
        self.assertEqual(signal_failure.exception.classification, "INFRASTRUCTURE_FAILURE")

        count_out = Path(self.temp.name) / "count-evidence"
        count_gate = {"id": "count", "argv": ["python3", "-c", "print('# tests 1')"],
                      "expected_test_count": 2}
        with self.assertRaises(GateFailure) as count_failure:
            run_sealed_gate(self.root, count_gate, count_out, 10)
        self.assertEqual(count_failure.exception.classification, "SAFETY_FAILURE")
        self.assertIsNone(count_failure.exception.repair_packet)

    def test_environment_is_scrubbed_and_writable_root_is_reset(self):
        writable = Path(self.temp.name) / "writable"
        writable.mkdir()
        (writable / "agent-planted-result").write_text("fake")
        reset_writable_dirs([writable])
        self.assertEqual(list(writable.iterdir()), [])
        gate = {"id": "env", "argv": ["python3", "-c",
            "import os,sys; sys.exit(0 if 'OPENAI_API_KEY' not in os.environ "
            "and os.environ['ORCHESTRATOR_RUN_ID'] == 'run-2' else 1)"]}
        run_sealed_gate(self.root, gate, self.out, 10, run_id="run-2")

    def test_broker_home_is_reset_before_every_gate(self):
        plant = {"id": "plant", "argv": ["python3", "-c",
            "import os,pathlib; (pathlib.Path(os.environ['HOME'])/'planted').write_text('x')"]}
        run_sealed_gate(self.root, plant, self.out, 10)
        clean_out = Path(self.temp.name) / "clean-evidence"
        verify = {"id": "verify", "argv": ["python3", "-c",
            "import os,pathlib,sys; sys.exit(1 if (pathlib.Path(os.environ['HOME'])/'planted').exists() else 0)"]}
        run_sealed_gate(self.root, verify, clean_out, 10)

    def test_exit_one_with_count_mismatch_is_safety_failure(self):
        gate = {"id": "count-red", "argv": ["python3", "-c",
            "import sys; print('# tests 1'); sys.exit(1)"], "expected_test_count": 2}
        with self.assertRaises(GateFailure) as raised:
            run_sealed_gate(self.root, gate, self.out, 10)
        self.assertEqual(raised.exception.classification, "SAFETY_FAILURE")
        self.assertIsNone(raised.exception.repair_packet)

    def test_rejects_executable_from_untrusted_path(self):
        gate = {"id": "path", "argv": ["/tmp/python3", "-c", "pass"]}
        with self.assertRaises(GateFailure) as raised:
            run_sealed_gate(self.root, gate, self.out, 10)
        self.assertEqual(raised.exception.classification, "SAFETY_FAILURE")

    def test_reset_rejects_symlink_and_path_outside_tmp(self):
        outside = Path("/var/tmp/orchestrator-broker-outside")
        with self.assertRaises(GateFailure) as outside_failure:
            reset_writable_dirs([outside])
        self.assertEqual(outside_failure.exception.classification, "SAFETY_FAILURE")

        target = Path(self.temp.name) / "target"
        target.mkdir()
        link = Path(self.temp.name) / "link"
        link.symlink_to(target, target_is_directory=True)
        with self.assertRaises(GateFailure) as symlink_failure:
            reset_writable_dirs([link])
        self.assertEqual(symlink_failure.exception.classification, "SAFETY_FAILURE")


if __name__ == "__main__":
    unittest.main()
