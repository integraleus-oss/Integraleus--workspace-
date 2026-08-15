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
from review_projection import ContractValidationError


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

    def format_retry_wrapper(self, verdict: dict, *, retry_exact: bool = True) -> Path:
        path = self.root / "claude-format-retry-wrapper"
        malformed = json.dumps({"result": "Review complete.\n" + json.dumps(verdict)})
        exact = json.dumps({"result": json.dumps(verdict) if retry_exact else "Still not JSON"})
        path.write_text(
            "#!/bin/sh\nset -eu\n"
            + "case \"$2\" in\n"
            + f"  *claude-format-retry*) printf '%s' {json.dumps(exact)} > \"$3\" ;;\n"
            + f"  *) printf '%s' {json.dumps(malformed)} > \"$3\" ;;\n"
            + "esac\n",
            encoding="utf-8",
        )
        path.chmod(path.stat().st_mode | stat.S_IXUSR)
        return path

    def contract_retry_wrapper(self, verdict: dict, *, repair_valid: bool = True) -> Path:
        path = self.root / "claude-contract-retry-wrapper"
        invalid = json.loads(json.dumps(verdict))
        invalid["conclusion"].pop("unable_to_complete_reason", None)
        repaired = verdict if repair_valid else invalid
        first = json.dumps({"result": json.dumps(invalid)})
        retry = json.dumps({"result": json.dumps(repaired)})
        path.write_text(
            "#!/bin/sh\nset -eu\n"
            + "case \"$2\" in\n"
            + f"  *claude-contract-retry*) printf '%s' {json.dumps(retry)} > \"$3\" ;;\n"
            + f"  *) printf '%s' {json.dumps(first)} > \"$3\" ;;\n"
            + "esac\n",
            encoding="utf-8",
        )
        path.chmod(path.stat().st_mode | stat.S_IXUSR)
        return path

    def contract_retry_with_prose_wrapper(self, verdict: dict, *, final_exact: bool = True) -> Path:
        path = self.root / "claude-contract-retry-with-prose-wrapper"
        invalid = json.loads(json.dumps(verdict))
        invalid["conclusion"].pop("unable_to_complete_reason", None)
        first = json.dumps({"result": json.dumps(invalid)})
        repair_with_prose = json.dumps({"result": "Contract repaired.\n" + json.dumps(verdict)})
        final = json.dumps({"result": json.dumps(verdict) if final_exact else "Still not exact JSON"})
        path.write_text(
            "#!/bin/sh\nset -eu\n"
            + "case \"$2\" in\n"
            + f"  *claude-contract-format-retry*) printf '%s' {json.dumps(final)} > \"$3\" ;;\n"
            + f"  *claude-contract-retry*) printf '%s' {json.dumps(repair_with_prose)} > \"$3\" ;;\n"
            + f"  *) printf '%s' {json.dumps(first)} > \"$3\" ;;\n"
            + "esac\n",
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

    def test_post_review_verifier_runs_before_verdict_or_policy(self) -> None:
        bundle = self.helper._run_bundle("tampered-input")
        verdict_path = Path(self.root / "inputs/verdict.json")
        verdict_path.unlink()
        prompt = self.root / "prompt.md"
        prompt.write_text("Review.")
        verified = []
        def reject_tamper():
            verified.append(True)
            raise RuntimeError("sealed input changed after review")
        with patch.object(agent_launcher, "CLAUDE_WRAPPER", self.wrapper_for(self.verdict)):
            with self.assertRaisesRegex(RuntimeError, "sealed input changed"):
                run_cycle(self.root, prompt, bundle, self.root / "cycle",
                          pre_admission_verify=reject_tamper)
        self.assertEqual(verified, [True])
        self.assertTrue((self.root / "cycle/claude-launch/launch-result.json").is_file())
        self.assertFalse(verdict_path.exists())
        self.assertFalse((self.root / "cycle/policy-runs").exists())

    def test_one_format_only_retry_preserves_exact_json_admission(self) -> None:
        bundle = self.helper._run_bundle("format-retry")
        Path(self.root / "inputs/verdict.json").unlink()
        prompt = self.root / "prompt.md"
        prompt.write_text("Review and return exact JSON.")
        verified = []
        with patch.object(agent_launcher, "CLAUDE_WRAPPER", self.format_retry_wrapper(self.verdict)):
            result = run_cycle(
                self.root, prompt, bundle, self.root / "cycle",
                pre_admission_verify=lambda: verified.append(True), allow_format_retry=True,
            )
        self.assertEqual(result["status"], "DECIDED")
        self.assertIsNotNone(result["format_retry_launch"])
        self.assertEqual(len(verified), 3)
        self.assertTrue((self.root / "cycle/claude-format-retry/verdict-extraction.json").is_file())
        retry_prompt = (self.root / "cycle/claude-format-retry/input-prompt.md").read_text()
        self.assertIn("no decoded U+0000 through U+001F", retry_prompt)
        self.assertIn("never emit literal tabs", retry_prompt)
        self.assertFalse((self.root / "inputs/verdict.json").exists())

    def test_format_retry_is_single_and_second_malformed_reply_fails_closed(self) -> None:
        bundle = self.helper._run_bundle("format-retry-fails")
        Path(self.root / "inputs/verdict.json").unlink()
        prompt = self.root / "prompt.md"
        prompt.write_text("Review and return exact JSON.")
        with patch.object(
            agent_launcher, "CLAUDE_WRAPPER", self.format_retry_wrapper(self.verdict, retry_exact=False)
        ):
            with self.assertRaisesRegex(agent_launcher.LaunchError, "exact JSON"):
                run_cycle(self.root, prompt, bundle, self.root / "cycle", allow_format_retry=True)
        record = json.loads((self.root / "cycle/cycle-result.json").read_text())
        self.assertEqual(record["status"], "FAILED_ADMISSION")
        self.assertTrue((self.root / "cycle/claude-format-retry/launch-result.json").is_file())
        self.assertFalse((self.root / "cycle/policy-runs").exists())

    def test_one_contract_only_retry_admits_repaired_exact_json(self) -> None:
        bundle = self.helper._run_bundle("contract-retry")
        Path(self.root / "inputs/verdict.json").unlink()
        prompt = self.root / "prompt.md"
        prompt.write_text("Review and obey the sealed contract.")
        verified = []
        verdict_path = Path(self.root / "inputs/verdict.json")
        def verify_without_generated_verdict():
            self.assertFalse(verdict_path.exists())
            verified.append(True)
        with patch.object(agent_launcher, "CLAUDE_WRAPPER", self.contract_retry_wrapper(self.verdict)):
            result = run_cycle(
                self.root, prompt, bundle, self.root / "cycle",
                pre_admission_verify=verify_without_generated_verdict, allow_contract_retry=True,
            )
        self.assertEqual(result["status"], "DECIDED")
        self.assertIsNotNone(result["contract_retry_launch"])
        self.assertEqual(len(verified), 3)
        self.assertTrue((self.root / "cycle/contract-repair-first-verdict.json").is_file())
        self.assertTrue((self.root / "cycle/contract-repair-first-admission/run-error.json").is_file())
        retry_prompt = (self.root / "cycle/claude-contract-retry/input-prompt.md").read_text()
        self.assertIn("schema_validation", retry_prompt)
        self.assertIn("no decoded U+0000 through U+001F", retry_prompt)
        self.assertIn("never emit literal tabs", retry_prompt)
        self.assertFalse((self.root / "inputs/verdict.json").exists())

    def test_contract_retry_is_single_and_second_invalid_reply_fails_closed(self) -> None:
        bundle = self.helper._run_bundle("contract-retry-fails")
        Path(self.root / "inputs/verdict.json").unlink()
        prompt = self.root / "prompt.md"
        prompt.write_text("Review.")
        with patch.object(
            agent_launcher, "CLAUDE_WRAPPER", self.contract_retry_wrapper(self.verdict, repair_valid=False)
        ):
            with self.assertRaises(ContractValidationError):
                run_cycle(self.root, prompt, bundle, self.root / "cycle", allow_contract_retry=True)
        record = json.loads((self.root / "cycle/cycle-result.json").read_text())
        self.assertEqual(record["status"], "FAILED_ADMISSION")
        self.assertTrue((self.root / "cycle/claude-contract-retry/launch-result.json").is_file())
        self.assertFalse((self.root / "inputs/verdict.json").exists())

    def test_contract_repair_gets_one_format_only_retry_for_non_exact_json(self) -> None:
        bundle = self.helper._run_bundle("contract-repair-format-retry")
        Path(self.root / "inputs/verdict.json").unlink()
        prompt = self.root / "prompt.md"
        prompt.write_text("Review and obey the sealed contract.")
        verified = []
        with patch.object(agent_launcher, "CLAUDE_WRAPPER", self.contract_retry_with_prose_wrapper(self.verdict)):
            result = run_cycle(
                self.root, prompt, bundle, self.root / "cycle",
                pre_admission_verify=lambda: verified.append(True), allow_contract_retry=True,
            )
        self.assertEqual(result["status"], "DECIDED")
        self.assertIsNotNone(result["contract_retry_launch"])
        self.assertIsNotNone(result["contract_format_retry_launch"])
        self.assertEqual(len(verified), 5)
        self.assertTrue((self.root / "cycle/claude-contract-format-retry/verdict-extraction.json").is_file())
        retry_prompt = (self.root / "cycle/claude-contract-format-retry/input-prompt.md").read_text()
        self.assertIn("no decoded U+0000 through U+001F", retry_prompt)
        self.assertIn("never emit literal tabs", retry_prompt)
        self.assertFalse((self.root / "inputs/verdict.json").exists())

    def test_contract_repair_format_retry_is_single_and_fails_closed(self) -> None:
        bundle = self.helper._run_bundle("contract-repair-format-retry-fails")
        Path(self.root / "inputs/verdict.json").unlink()
        prompt = self.root / "prompt.md"
        prompt.write_text("Review.")
        with patch.object(
            agent_launcher, "CLAUDE_WRAPPER",
            self.contract_retry_with_prose_wrapper(self.verdict, final_exact=False),
        ):
            with self.assertRaisesRegex(agent_launcher.LaunchError, "exact JSON"):
                run_cycle(self.root, prompt, bundle, self.root / "cycle", allow_contract_retry=True)
        record = json.loads((self.root / "cycle/cycle-result.json").read_text())
        self.assertEqual(record["status"], "FAILED_ADMISSION")
        self.assertTrue((self.root / "cycle/claude-contract-format-retry/launch-result.json").is_file())
        self.assertFalse((self.root / "inputs/verdict.json").exists())

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
