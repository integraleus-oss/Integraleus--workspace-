from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import local_orchestrator_runner as runner
import review_projection as projection


CORE = projection.CORE


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


class LocalIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.verdict_path = CORE / "fixtures/valid/initial_blocker.json"
        self.manifest_path = CORE / "fixtures/trusted/manifest_initial.json"
        verdict = json.loads(self.verdict_path.read_text(encoding="utf-8"))
        self.verdict = verdict
        self.binding = {
            "document_type": "review_projection_binding",
            "schema_version": "1.0.0",
            "task_id": verdict["subject"]["task_id"],
            "spec_digest": "sha256:" + "a" * 64,
            "run_id": verdict["subject"]["run_id"],
            "attempt_epoch": verdict["subject"]["attempt"],
            "reviewed_tree_digest": "sha256:" + "b" * 64,
            "covered_paths": ["src/reviewer_contract.py"],
        }
        self.binding_path = self.root / "binding.json"
        write_json(self.binding_path, self.binding)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_projection_is_deterministic_and_preserves_blocking_finding(self) -> None:
        first, validation = projection.build_projection(
            self.verdict_path, self.manifest_path, self.binding_path
        )
        second, _ = projection.build_projection(
            self.verdict_path, self.manifest_path, self.binding_path
        )
        self.assertTrue(validation["contract_valid"])
        self.assertEqual(first, second)
        self.assertEqual(first["findings"][0]["severity"], "blocker")
        self.assertEqual(first["findings"][0]["path"], "src/reviewer_contract.py")
        self.assertEqual(first["verified_finding_ids"], [])

    def test_binding_mismatch_fails_closed(self) -> None:
        bad = dict(self.binding)
        bad["run_id"] = "wrong-run"
        bad_path = self.root / "bad-binding.json"
        write_json(bad_path, bad)
        with self.assertRaises(projection.ProjectionError):
            projection.build_projection(self.verdict_path, self.manifest_path, bad_path)

    def _policy_fixture(self, name: str = "accepted.json") -> dict:
        fixture = json.loads((CORE / "fixtures/policy/valid" / name).read_text(encoding="utf-8"))
        task_id = self.binding["task_id"]
        run_id = self.binding["run_id"]
        spec_digest = self.binding["spec_digest"]
        tree_digest = self.binding["reviewed_tree_digest"]
        for key in ("task_policy", "ledger", "execution_report"):
            fixture[key]["task_id"] = task_id
            fixture[key]["run_id"] = run_id
            fixture[key]["spec_digest"] = spec_digest
        fixture["ledger"]["current_epoch"] = self.binding["attempt_epoch"]
        fixture["ledger"]["last_epoch"] = self.binding["attempt_epoch"] - 1
        fixture["ledger"]["expected_subject"] = {
            "tree_digest": tree_digest,
            "changed_paths": self.binding["covered_paths"],
        }
        fixture["execution_report"]["attempt_epoch"] = self.binding["attempt_epoch"]
        fixture["execution_report"]["subject"] = copy.deepcopy(fixture["ledger"]["expected_subject"])
        return fixture

    def _nonblocking_final_verdict_and_manifest(self) -> tuple[dict, dict]:
        verdict = copy.deepcopy(self.verdict)
        verdict["review"]["review_mode"] = "final_full"
        finding = verdict["findings"][0]
        finding["severity"] = "nit"
        finding["category"] = "maintainability"
        finding["criterion_id"] = None
        finding["fingerprint"]["category"] = "maintainability"
        finding["fingerprint"]["criterion_id"] = None
        finding_id = projection.VALIDATOR.expected_finding_id(finding["fingerprint"])
        occurrence_id = projection.VALIDATOR.expected_occurrence_id(
            verdict["review"]["review_id"], finding_id, 1
        )
        finding["finding_id"] = finding_id
        finding["occurrence_id"] = occurrence_id
        verdict["counts"] = {"blocker": 0, "major": 0, "nit": 1, "total": 1}
        coverage = verdict["criteria_coverage"][0]
        coverage["status"] = "satisfied"
        coverage["linked_occurrence_ids"] = [occurrence_id]
        coverage["notes"] = "The criterion is satisfied; one advisory nit remains."
        verdict["conclusion"] = {
            "status": "findings_present",
            "summary": "Full review found one advisory nit and no blocking findings.",
            "unable_to_complete_reason": None,
        }
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        manifest["expected_review_mode"] = "final_full"
        return verdict, manifest

    def _run_bundle(
        self,
        run_name: str,
        *,
        verdict: dict | None = None,
        manifest: dict | None = None,
        policy_fixture: dict | None = None,
    ) -> Path:
        inputs = self.root / "inputs"
        inputs.mkdir(exist_ok=True)
        write_json(inputs / "policy.json", policy_fixture or self._policy_fixture())
        write_json(inputs / "verdict.json", verdict or self.verdict)
        write_json(inputs / "manifest.json", manifest or json.loads(self.manifest_path.read_text(encoding="utf-8")))
        write_json(inputs / "binding.json", self.binding)
        bundle = {
            "document_type": "local_orchestrator_run",
            "schema_version": "1.0.0",
            "run_name": run_name,
            "policy_fixture": "inputs/policy.json",
            "review_verdict": "inputs/verdict.json",
            "trusted_manifest": "inputs/manifest.json",
            "projection_binding": "inputs/binding.json",
            "prior_findings": None,
        }
        bundle_path = self.root / f"{run_name}.json"
        write_json(bundle_path, bundle)
        return bundle_path

    def test_runner_snapshots_inputs_and_returns_rework(self) -> None:
        run_dir, result = runner.run(self._run_bundle("run-one"), self.root / "runs")
        self.assertEqual(result["outcome"], "REWORK")
        self.assertEqual(result["rule_id"], "R11_OPEN_FINDINGS")
        self.assertTrue((run_dir / "decision.json").is_file())
        self.assertEqual((run_dir / "input-review_verdict.json").stat().st_mode & 0o777, 0o444)

    def test_replay_in_new_run_directory_is_byte_deterministic(self) -> None:
        first_dir, _ = runner.run(self._run_bundle("run-first"), self.root / "runs")
        second_dir, _ = runner.run(self._run_bundle("run-second"), self.root / "runs")
        self.assertEqual(
            (first_dir / "decision.json").read_bytes(),
            (second_dir / "decision.json").read_bytes(),
        )

    def test_existing_run_directory_is_never_overwritten(self) -> None:
        bundle = self._run_bundle("run-once")
        runner.run(bundle, self.root / "runs")
        with self.assertRaises(projection.ProjectionError):
            runner.run(bundle, self.root / "runs")

    def test_clean_final_review_can_reach_accepted(self) -> None:
        verdict, manifest = self._nonblocking_final_verdict_and_manifest()
        _, result = runner.run(
            self._run_bundle("run-accepted", verdict=verdict, manifest=manifest),
            self.root / "runs",
        )
        self.assertEqual((result["outcome"], result["rule_id"]), ("ACCEPTED", "R17_ACCEPT"))

    def test_known_infrastructure_failure_uses_allowlist_policy(self) -> None:
        verdict, manifest = self._nonblocking_final_verdict_and_manifest()
        fixture = self._policy_fixture("known_infra.json")
        _, result = runner.run(
            self._run_bundle(
                "run-infra", verdict=verdict, manifest=manifest, policy_fixture=fixture
            ),
            self.root / "runs",
        )
        self.assertEqual(result["outcome"], "FAILED_INFRA")

    def test_malformed_policy_input_escalates(self) -> None:
        verdict, manifest = self._nonblocking_final_verdict_and_manifest()
        fixture = self._policy_fixture()
        del fixture["task_policy"]["spec_digest"]
        _, result = runner.run(
            self._run_bundle(
                "run-escalated", verdict=verdict, manifest=manifest, policy_fixture=fixture
            ),
            self.root / "runs",
        )
        self.assertEqual((result["outcome"], result["rule_id"]), ("ESCALATED", "R01_BINDING"))

    def test_contract_invalid_review_produces_no_decision(self) -> None:
        invalid = copy.deepcopy(self.verdict)
        invalid["unauthorized_decision"] = "ACCEPTED"
        bundle = self._run_bundle("run-invalid-review", verdict=invalid)
        with self.assertRaises(projection.ProjectionError):
            runner.run(bundle, self.root / "runs")
        self.assertFalse((self.root / "runs/run-invalid-review/decision.json").exists())
        self.assertTrue((self.root / "runs/run-invalid-review/run-error.json").exists())

    def test_blocking_limitation_cannot_project(self) -> None:
        verdict, manifest = self._nonblocking_final_verdict_and_manifest()
        verdict["limitations"] = [{
            "code": "environment_unavailable",
            "description": "The review environment was unavailable.",
            "blocking": True,
            "affected_criteria": ["AC-1"],
            "evidence_ids": [],
        }]
        bundle = self._run_bundle("run-blocking-limit", verdict=verdict, manifest=manifest)
        with self.assertRaises(projection.ProjectionError):
            runner.run(bundle, self.root / "runs")
        self.assertTrue((self.root / "runs/run-blocking-limit/run-error.json").exists())

    def test_full_review_with_not_reviewed_criterion_cannot_project(self) -> None:
        verdict, manifest = self._nonblocking_final_verdict_and_manifest()
        verdict["criteria_coverage"][0]["status"] = "not_reviewed"
        verdict["criteria_coverage"][0]["verification_method"] = "not_attempted"
        verdict["criteria_coverage"][0].pop("evidence_ids", None)
        verdict["criteria_coverage"][0].pop("linked_occurrence_ids", None)
        bundle = self._run_bundle("run-incomplete-coverage", verdict=verdict, manifest=manifest)
        with self.assertRaises(projection.ProjectionError):
            runner.run(bundle, self.root / "runs")

    def test_locationless_nit_gets_deterministic_sentinel_path(self) -> None:
        verdict, manifest = self._nonblocking_final_verdict_and_manifest()
        finding = verdict["findings"][0]
        finding["location"] = None
        finding["location_absent_reason"] = "cross_cutting"
        finding["fingerprint"]["normalized_path"] = None
        finding_id = projection.VALIDATOR.expected_finding_id(finding["fingerprint"])
        occurrence_id = projection.VALIDATOR.expected_occurrence_id(verdict["review"]["review_id"], finding_id, 1)
        finding["finding_id"] = finding_id
        finding["occurrence_id"] = occurrence_id
        verdict["criteria_coverage"][0]["linked_occurrence_ids"] = [occurrence_id]
        verdict_path = self.root / "locationless.json"
        manifest_path = self.root / "locationless-manifest.json"
        write_json(verdict_path, verdict)
        write_json(manifest_path, manifest)
        value, _ = projection.build_projection(verdict_path, manifest_path, self.binding_path)
        self.assertEqual(value["findings"][0]["path"], "_no_location/cross_cutting")

    def test_bundle_input_path_escape_is_rejected_and_audited(self) -> None:
        bundle_path = self._run_bundle("run-escape")
        bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
        bundle["policy_fixture"] = "../outside.json"
        write_json(bundle_path, bundle)
        with self.assertRaises(projection.ProjectionError):
            runner.run(bundle_path, self.root / "runs")
        self.assertTrue((self.root / "runs/run-escape/run-error.json").exists())

    def test_targeted_still_open_never_enters_verified_ids(self) -> None:
        verdict_path = CORE / "fixtures/valid/targeted_verification.json"
        manifest_path = CORE / "fixtures/trusted/manifest_targeted.json"
        prior_path = CORE / "fixtures/trusted/prior_findings_targeted.json"
        verdict = json.loads(verdict_path.read_text(encoding="utf-8"))
        binding = {
            "document_type": "review_projection_binding",
            "schema_version": "1.0.0",
            "task_id": verdict["subject"]["task_id"],
            "spec_digest": "sha256:" + "a" * 64,
            "run_id": verdict["subject"]["run_id"],
            "attempt_epoch": verdict["subject"]["attempt"],
            "reviewed_tree_digest": "sha256:" + "b" * 64,
            "covered_paths": ["src/audit.py"],
        }
        binding_path = self.root / "targeted-binding.json"
        write_json(binding_path, binding)
        value, validation = projection.build_projection(
            verdict_path, manifest_path, binding_path, prior_path
        )
        self.assertTrue(validation["contract_valid"])
        self.assertEqual(value["verified_finding_ids"], [])
        self.assertEqual(value["findings"][0]["severity"], "major")


if __name__ == "__main__":
    unittest.main()
