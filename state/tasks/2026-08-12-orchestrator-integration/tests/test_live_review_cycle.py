from __future__ import annotations

import json
import stat
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import agent_launcher
import test_integration
from live_review_cycle import run_cycle
from managed_policy_review import admit_live_review


class LiveReviewCycleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.helper = test_integration.LocalIntegrationTests(methodName="test_runner_snapshots_inputs_and_returns_rework")
        self.helper.setUp()
        self.root = self.helper.root
        self.verdict = self.helper.verdict

    def tearDown(self) -> None:
        self.helper.tearDown()

    def wrapper_for(self, verdict: dict, exit_code: int = 0) -> Path:
        path = self.root / "claude-wrapper"
        envelope = json.dumps({"result": json.dumps(verdict)})
        path.write_text(
            "#!/bin/sh\nset -eu\n"
            + f"printf '%s' {json.dumps(envelope)} > \"$3\"\n"
            + f"exit {exit_code}\n",
            encoding="utf-8",
        )
        path.chmod(path.stat().st_mode | stat.S_IXUSR)
        return path

    def test_cycle_launches_projects_and_returns_policy_decision(self) -> None:
        bundle = self.helper._run_bundle("live-rework")
        bundle_value = json.loads(bundle.read_text())
        Path(self.root / "inputs/verdict.json").unlink()
        prompt = self.root / "prompt.md"
        prompt.write_text("Review synthetic fixture and return exact JSON.")
        with patch.object(agent_launcher, "CLAUDE_WRAPPER", self.wrapper_for(self.verdict)):
            result = run_cycle(self.root, prompt, bundle, self.root / "cycle")
        self.assertEqual(result["status"], "DECIDED")
        self.assertEqual(result["decision"]["outcome"], "REWORK")
        self.assertFalse((self.root / bundle_value["review_verdict"]).exists())
        self.assertTrue((self.root / "cycle/claude-launch/launch-result.json").exists())

    def test_policy_decision_is_admitted_with_derived_rework_packet(self) -> None:
        bundle = self.helper._run_bundle("managed-live-rework")
        Path(self.root / "inputs/verdict.json").unlink()
        prompt = self.root / "prompt.md"
        prompt.write_text("Review synthetic fixture and return exact JSON.")
        cycle_root = self.root / "cycle"
        with patch.object(agent_launcher, "CLAUDE_WRAPPER", self.wrapper_for(self.verdict)):
            live_result = run_cycle(self.root, prompt, bundle, cycle_root)
        admitted = admit_live_review(live_result, cycle_root)
        self.assertEqual((admitted["outcome"], admitted["rule_id"]), ("REWORK", "R11_OPEN_FINDINGS"))
        self.assertIn("fnd_b5ea59e6b40ea0e2265bd03f438a00e3", admitted["rework_packet"])

    def test_failed_launch_never_runs_policy(self) -> None:
        bundle = self.helper._run_bundle("never-policy")
        Path(self.root / "inputs/verdict.json").unlink()
        prompt = self.root / "prompt.md"
        prompt.write_text("Review.")
        with patch.object(agent_launcher, "CLAUDE_WRAPPER", self.wrapper_for(self.verdict, exit_code=9)):
            result = run_cycle(self.root, prompt, bundle, self.root / "cycle")
        self.assertEqual(result["status"], "FAILED_LAUNCH")
        self.assertIsNone(result["decision"])
        self.assertFalse((self.root / "cycle/policy-runs").exists())

    def test_invalid_verdict_writes_failed_admission_record(self) -> None:
        bundle = self.helper._run_bundle("bad-admission")
        Path(self.root / "inputs/verdict.json").unlink()
        prompt = self.root / "prompt.md"
        prompt.write_text("Review.")
        with patch.object(agent_launcher, "CLAUDE_WRAPPER", self.wrapper_for({"bad": True})):
            with self.assertRaises(Exception):
                run_cycle(self.root, prompt, bundle, self.root / "cycle")
        record = json.loads((self.root / "cycle/cycle-result.json").read_text())
        self.assertEqual(record["status"], "FAILED_ADMISSION")
        self.assertIsNone(record["decision"])

    def test_symlinked_verdict_path_is_rejected(self) -> None:
        bundle = self.helper._run_bundle("symlink-escape")
        bundle_value = json.loads(bundle.read_text())
        Path(self.root / "inputs/verdict.json").unlink()
        outside_temp = tempfile.TemporaryDirectory(dir=self.root.parent)
        self.addCleanup(outside_temp.cleanup)
        outside = Path(outside_temp.name)
        (self.root / "link").symlink_to(outside, target_is_directory=True)
        bundle_value["review_verdict"] = "link/verdict.json"
        bundle.write_text(json.dumps(bundle_value))
        prompt = self.root / "prompt.md"
        prompt.write_text("Review.")
        with patch.object(agent_launcher, "CLAUDE_WRAPPER", self.wrapper_for(self.verdict)):
            with self.assertRaises(Exception):
                run_cycle(self.root, prompt, bundle, self.root / "cycle")
        self.assertFalse((outside / "verdict.json").exists())


if __name__ == "__main__":
    unittest.main()
