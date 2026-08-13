from __future__ import annotations

import tempfile
import unittest
import hashlib
import json
from pathlib import Path

from managed_one_cycle import CycleError, run_managed_cycle
from managed_policy_review import ManagedReviewError, admit_live_review


class ManagedOneCycleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "cycle"

    def tearDown(self) -> None:
        self.temp.cleanup()

    @staticmethod
    def ok(attempt, context, run_dir):
        run_dir.mkdir()
        return {"status": "OK", "attempt": attempt, "context": context}

    @staticmethod
    def decision(outcome, **extra):
        rules = {"ACCEPTED": "R17_ACCEPT", "REWORK": "R11_OPEN_FINDINGS",
                 "FAILED_INFRA": "R05_INFRA_RETRY", "ESCALATED": "R01_BINDING"}
        return {"document_type": "local_orchestrator_run_result", "outcome": outcome, "rule_id": rules.get(outcome, "UNKNOWN"), **extra}

    def test_accepts_first_attempt(self):
        result = run_managed_cycle(self.root, self.ok, lambda a, d: self.decision("ACCEPTED"))
        self.assertEqual((result["status"], result["attempts_used"]), ("ACCEPTED", 1))

    def test_one_rework_then_accept(self):
        seen = []
        def implement(attempt, context, run_dir):
            seen.append(context)
            return self.ok(attempt, context, run_dir)
        def review(attempt, run_dir):
            return self.decision("REWORK", rework_packet="fix F-1") if attempt == 1 else self.decision("ACCEPTED")
        result = run_managed_cycle(self.root, implement, review)
        self.assertEqual((result["status"], result["attempts_used"]), ("ACCEPTED", 2))
        self.assertEqual(seen, [None, "fix F-1"])

    def test_second_rework_escalates(self):
        result = run_managed_cycle(self.root, self.ok, lambda a, d: self.decision("REWORK", rework_packet="fix"))
        self.assertEqual(result["status"], "ESCALATED")

    def test_second_review_can_request_bounded_review_only_final_full(self):
        implemented = []
        def implement(attempt, context, run_dir):
            implemented.append(attempt)
            return self.ok(attempt, context, run_dir)
        def review(attempt, run_dir):
            if attempt == 1:
                return self.decision("REWORK", rework_packet="fix F-1")
            if attempt == 2:
                return self.decision("REWORK", rule_id="R15_NEED_FULL_REVIEW",
                                     rework_packet="required final full review only")
            return self.decision("ACCEPTED")
        result = run_managed_cycle(self.root, implement, review)
        self.assertEqual((result["status"], result["attempts_used"]), ("ACCEPTED", 3))
        self.assertEqual(implemented, [1, 2])
        self.assertEqual(result["history"][2]["implementation"]["status"], "SKIPPED_REVIEW_ONLY")

    def test_first_review_can_request_final_full_without_second_codex_attempt(self):
        implemented = []
        def implement(attempt, context, run_dir):
            implemented.append(attempt)
            return self.ok(attempt, context, run_dir)
        def review(attempt, run_dir):
            return (self.decision("REWORK", rule_id="R15_NEED_FULL_REVIEW",
                                  rework_packet="required final full review only")
                    if attempt == 1 else self.decision("ACCEPTED"))
        result = run_managed_cycle(self.root, implement, review)
        self.assertEqual(result["status"], "ACCEPTED")
        self.assertEqual(implemented, [1])

    def test_missing_rework_packet_escalates(self):
        result = run_managed_cycle(self.root, self.ok, lambda a, d: self.decision("REWORK"))
        self.assertEqual(result["status"], "ESCALATED")
        self.assertEqual(result["attempts_used"], 1)

    def test_known_and_unknown_implementation_failure(self):
        for classification, expected in (("KNOWN_INFRA", "FAILED_INFRA"), ("UNKNOWN", "ESCALATED")):
            root = self.root.with_name("cycle-" + classification.lower())
            result = run_managed_cycle(root, lambda a, c, d, x=classification: {"status": "FAILED", "classification": x}, lambda a, d: {})
            self.assertEqual(result["status"], expected)

    def test_unknown_review_outcome_escalates(self):
        result = run_managed_cycle(self.root, self.ok, lambda a, d: self.decision("MAYBE"))
        self.assertEqual(result["status"], "ESCALATED")

    def test_single_use_and_fixed_budget(self):
        run_managed_cycle(self.root, self.ok, lambda a, d: self.decision("ACCEPTED"))
        with self.assertRaises(CycleError):
            run_managed_cycle(self.root, self.ok, lambda a, d: self.decision("ACCEPTED"))
        with self.assertRaises(CycleError):
            run_managed_cycle(self.root.with_name("other"), self.ok, lambda a, d: {}, max_attempts=3)

    def test_untrusted_review_result_escalates(self):
        result = run_managed_cycle(self.root, self.ok, lambda a, d: {"outcome": "ACCEPTED"})
        self.assertEqual(result["status"], "ESCALATED")

    def test_rule_outcome_mismatch_escalates(self):
        result = run_managed_cycle(self.root, self.ok, lambda a, d: self.decision("ACCEPTED", rule_id="R11_OPEN_FINDINGS"))
        self.assertEqual(result["status"], "ESCALATED")

    def test_exception_writes_terminal_record(self):
        result = run_managed_cycle(self.root, lambda a, c, d: (_ for _ in ()).throw(RuntimeError("boom")), lambda a, d: {})
        self.assertEqual(result["status"], "ESCALATED")
        self.assertTrue((self.root / "cycle-result.json").is_file())

    def test_result_round_trip_and_rework_size_bound(self):
        result = run_managed_cycle(self.root, self.ok, lambda a, d: self.decision("REWORK", rework_packet="x" * 8193))
        self.assertEqual(result["status"], "ESCALATED")
        import json
        self.assertEqual(json.loads((self.root / "cycle-result.json").read_text()), result)


class ManagedPolicyReviewTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.cycle = Path(self.temp.name) / "live"
        self.run_dir = self.cycle / "policy-runs" / "run-1"
        self.run_dir.mkdir(parents=True)
        self.decision = {
            "outcome": "REWORK", "rule_id": "R11_OPEN_FINDINGS",
            "directives": [{"type": "FIX_FINDINGS", "finding_ids": ["F-1"]}],
        }
        self.projection = {"findings": [{"finding_id": "F-1", "severity": "major", "message": "wrong add", "path": "calc.py"}]}
        self._write("decision.json", self.decision)
        self._write("trusted-review-projection.json", self.projection)
        self.manifest = {
            "document_type": "local_orchestrator_run_result", "schema_version": "1.0.0",
            "outcome": "REWORK", "rule_id": "R11_OPEN_FINDINGS",
            "decision_digest_file": self._digest("decision.json"),
            "projection_digest": self._digest("trusted-review-projection.json"),
        }
        self._write("run-result.json", self.manifest)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _write(self, name, value):
        (self.run_dir / name).write_text(json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n")

    def _digest(self, name):
        return "sha256:" + hashlib.sha256((self.run_dir / name).read_bytes()).hexdigest()

    def live_result(self):
        return {"document_type": "local_live_review_cycle_result", "status": "DECIDED",
                "decision": self.manifest, "decision_dir": str(self.run_dir)}

    def test_derives_rework_only_from_policy_selected_projection(self):
        admitted = admit_live_review(self.live_result(), self.cycle)
        self.assertEqual(admitted["outcome"], "REWORK")
        self.assertIn("F-1 [major]: wrong add (calc.py)", admitted["rework_packet"])

    def test_tampered_decision_fails_closed(self):
        self.decision["rule_id"] = "R17_ACCEPT"
        self._write("decision.json", self.decision)
        with self.assertRaises(ManagedReviewError):
            admit_live_review(self.live_result(), self.cycle)

    def test_escaping_decision_directory_fails_closed(self):
        result = self.live_result()
        result["decision_dir"] = str(Path(self.temp.name))
        with self.assertRaises(ManagedReviewError):
            admit_live_review(result, self.cycle)

    def test_missing_projected_finding_fails_closed(self):
        self.projection["findings"] = []
        self._write("trusted-review-projection.json", self.projection)
        self.manifest["projection_digest"] = self._digest("trusted-review-projection.json")
        self._write("run-result.json", self.manifest)
        with self.assertRaises(ManagedReviewError):
            admit_live_review(self.live_result(), self.cycle)

    def test_derives_all_policy_rework_directives(self):
        cases = [
            ("R09_GATE_FAIL", {"type": "FIX_GATES", "gate_ids": ["unit_tests"]}, "failed mandatory gates: unit_tests"),
            ("R13_EVIDENCE", {"type": "PROVIDE_EVIDENCE", "req_ids": ["unit-log"]}, "required evidence artifacts: unit-log"),
            ("R15_NEED_FULL_REVIEW", {"type": "REVIEW_ONLY_FULL"}, "required final full review only"),
        ]
        for index, (rule_id, directive, expected) in enumerate(cases):
            with self.subTest(rule_id=rule_id):
                run_dir = self.cycle / "policy-runs" / f"case-{index}"
                run_dir.mkdir(parents=True)
                decision = {"outcome": "REWORK", "rule_id": rule_id, "directives": [directive]}
                projection = {"findings": []}
                for name, value in (("decision.json", decision), ("trusted-review-projection.json", projection)):
                    (run_dir / name).write_text(json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n")
                digest = lambda name: "sha256:" + hashlib.sha256((run_dir / name).read_bytes()).hexdigest()
                manifest = {"document_type": "local_orchestrator_run_result", "outcome": "REWORK", "rule_id": rule_id,
                            "decision_digest_file": digest("decision.json"), "projection_digest": digest("trusted-review-projection.json")}
                (run_dir / "run-result.json").write_text(json.dumps(manifest, sort_keys=True, separators=(",", ":")) + "\n")
                result = {"document_type": "local_live_review_cycle_result", "status": "DECIDED",
                          "decision": manifest, "decision_dir": str(run_dir)}
                self.assertIn(expected, admit_live_review(result, self.cycle)["rework_packet"])
