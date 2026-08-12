from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path

import jsonschema

import orchestrator_policy as policy


ROOT = Path(__file__).resolve().parents[1]


def digest(char: str) -> str:
    return "sha256:" + (char * 64)


def base_bundle() -> dict:
    return {
        "task_policy": {
            "document_type": "orchestrator_task_policy",
            "schema_version": "1.0.0",
            "task_id": "task-2026-08-11-state-machine",
            "spec_digest": digest("a"),
            "run_id": "run-001",
            "mandatory_gates": ["schema_self_check", "unit_tests", "diff_check"],
            "required_evidence": [
                {"req_id": "schema-log", "digest": digest("c"), "digest_required": True},
                {"req_id": "unit-log", "digest": digest("d"), "digest_required": True},
            ],
            "infra_signature_allowlist": ["SIG_RUNNER_OOM", "SIG_SANDBOX_TIMEOUT"],
            "budgets": {
                "rework": 2,
                "infra_total": 2,
                "infra_per_signature": {"SIG_RUNNER_OOM": 2, "SIG_SANDBOX_TIMEOUT": 1},
                "final_full": 2,
                "no_progress": 2,
            },
        },
        "ledger": {
            "document_type": "orchestrator_ledger",
            "schema_version": "1.0.0",
            "task_id": "task-2026-08-11-state-machine",
            "spec_digest": digest("a"),
            "run_id": "run-001",
            "current_epoch": 1,
            "last_epoch": 0,
            "seen_nonces": ["nonce-old"],
            "expected_subject": {
                "tree_digest": digest("b"),
                "changed_paths": ["implementation/orchestrator_policy.py", "implementation/tests/test_orchestrator_policy.py"],
            },
            "counters": {
                "rework_used": 0,
                "infra_total_used": 0,
                "infra_used_by_signature": {},
                "final_full_used": 0,
                "no_progress_streak": 0,
            },
            "finding_registry": {"document_type": "finding_registry", "schema_version": "1.0.0", "findings": []},
            "prior_attempts": [],
            "terminal_decision": None,
        },
        "execution_report": {
            "document_type": "execution_report",
            "schema_version": "1.0.0",
            "task_id": "task-2026-08-11-state-machine",
            "spec_digest": digest("a"),
            "run_id": "run-001",
            "attempt_epoch": 1,
            "nonce": "nonce-new",
            "subject": {
                "tree_digest": digest("b"),
                "changed_paths": ["implementation/tests/test_orchestrator_policy.py", "implementation/orchestrator_policy.py"],
            },
            "exit_status": "OK",
            "failure_signatures": [],
            "gate_results": {"schema_self_check": "PASS", "unit_tests": "PASS", "diff_check": "PASS"},
            "evidence_artifacts": [
                {"req_id": "unit-log", "digest": digest("d"), "bytes": 200},
                {"req_id": "schema-log", "digest": digest("c"), "bytes": 100},
            ],
        },
        "reviewer_report": {
            "document_type": "trusted_review_projection",
            "schema_version": "1.0.0",
            "task_id": "task-2026-08-11-state-machine",
            "spec_digest": digest("a"),
            "run_id": "run-001",
            "attempt_epoch": 1,
            "review_id": "review-final-001",
            "review_digest": digest("e"),
            "review_mode": "final_full",
            "coverage_scope": "full",
            "reviewed_tree_digest": digest("b"),
            "covered_paths": ["implementation/orchestrator_policy.py", "implementation/tests/test_orchestrator_policy.py"],
            "findings": [],
            "verified_finding_ids": [],
        },
    }


def decide(bundle: dict) -> dict:
    return policy.decide(bundle["task_policy"], bundle["ledger"], bundle["execution_report"], bundle["reviewer_report"])


def registry_with(finding_id: str = "fnd_existing", severity: str = "major", status: str = "open") -> dict:
    return {
        "document_type": "finding_registry",
        "schema_version": "1.0.0",
        "findings": [
            {
                "finding_id": finding_id,
                "status": status,
                "effective_severity": severity,
                "occurrence_count": 1,
                "resolved_at": None
                if status == "open"
                else {"review_id": "review-targeted-001", "tree_digest": digest("b")},
                "history": [
                    {
                        "review_id": "review-prior",
                        "occurrence_id": "occ-prior",
                        "severity": severity,
                        "path": "implementation/orchestrator_policy.py",
                        "tree_digest": digest("b"),
                    }
                ],
            }
        ],
    }


def finding(finding_id: str, occurrence_id: str, severity: str = "major", message: str = "finding") -> dict:
    return {
        "finding_id": finding_id,
        "occurrence_id": occurrence_id,
        "severity": severity,
        "path": "implementation/orchestrator_policy.py",
        "message": message,
    }


def deeply_nested_dict(depth: int = 3000) -> dict:
    root: dict = {}
    node = root
    for _index in range(depth):
        node["n"] = {}
        node = node["n"]
    return root


def json_safe_shape(value, depth: int = 0):
    if depth > policy.MAX_DEPTH:
        return {"__type__": "too_deep"}
    if isinstance(value, dict):
        items = [[json_safe_shape(key, depth + 1), json_safe_shape(item, depth + 1)] for key, item in value.items()]
        return {
            "__type__": "dict",
            "items": sorted(
                items,
                key=lambda item: json.dumps(item, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8"),
            ),
        }
    if isinstance(value, list):
        return {"__type__": "list", "items": [json_safe_shape(item, depth + 1) for item in value]}
    return value


def rejected_digest(value) -> str:
    return policy.canonical_digest({"rejected_input": json_safe_shape(value)})


def expected_progress_identity(execution_report: dict) -> str:
    subject = execution_report["subject"]
    preimage = {
        "subject": {
            "changed_paths": sorted(subject["changed_paths"]),
            "tree_digest": subject["tree_digest"],
        }
    }
    encoded = json.dumps(preimage, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def prior_attempt_from(bundle: dict, decision: dict) -> dict:
    return {
        "attempt_epoch": bundle["execution_report"]["attempt_epoch"],
        "progress_identity": decision["progress_identity"],
        "decision_digest": decision["decision_digest"],
        "outcome": decision["outcome"],
        "rule_id": decision["rule_id"],
    }


class OrchestratorPolicyTests(unittest.TestCase):
    def test_state_machine_schema_self_validates(self) -> None:
        schema = policy.parse_json_file(ROOT / "orchestrator-state-machine.schema.json")
        jsonschema.Draft202012Validator.check_schema(schema)

    def test_finding_registry_schema_self_validates(self) -> None:
        schema = policy.parse_json_file(ROOT / "finding-registry.schema.json")
        jsonschema.Draft202012Validator.check_schema(schema)

    def test_state_schema_rejects_unknown_fields(self) -> None:
        fixture = {"document_type": "policy_fixture", "schema_version": "1.0.0", "unexpected": True}
        schema = policy.parse_json_file(ROOT / "orchestrator-state-machine.schema.json")
        errors = list(jsonschema.Draft202012Validator(schema).iter_errors(fixture))
        self.assertTrue(errors)

    def test_registry_schema_rejects_unknown_fields(self) -> None:
        registry = {"document_type": "finding_registry", "schema_version": "1.0.0", "findings": [], "waiver": True}
        schema = policy.parse_json_file(ROOT / "finding-registry.schema.json")
        errors = list(jsonschema.Draft202012Validator(schema).iter_errors(registry))
        self.assertTrue(errors)

    def test_accepts_only_after_all_prior_rules_are_false(self) -> None:
        result = decide(base_bundle())
        self.assertEqual(result["outcome"], "ACCEPTED")
        self.assertEqual(result["rule_id"], "R17_ACCEPT")

    def test_decision_exposes_exact_public_progress_identity(self) -> None:
        bundle = base_bundle()
        result = decide(bundle)
        self.assertEqual(result["progress_identity"], expected_progress_identity(bundle["execution_report"]))

        reversed_paths = copy.deepcopy(bundle)
        reversed_paths["execution_report"]["subject"]["changed_paths"] = list(
            reversed(reversed_paths["execution_report"]["subject"]["changed_paths"])
        )
        self.assertEqual(decide(reversed_paths)["progress_identity"], result["progress_identity"])

    def test_idempotent_terminal_replay_returns_recorded_decision(self) -> None:
        bundle = base_bundle()
        first = decide(bundle)
        replay = copy.deepcopy(bundle)
        replay["ledger"]["terminal_decision"] = first
        self.assertEqual(decide(replay), first)

    def test_binding_mismatch_escalates(self) -> None:
        bundle = base_bundle()
        bundle["reviewer_report"]["run_id"] = "run-other"
        result = decide(bundle)
        self.assertEqual((result["outcome"], result["rule_id"]), ("ESCALATED", "R01_BINDING"))

    def test_bool_counter_is_malformed_and_escalates(self) -> None:
        bundle = base_bundle()
        bundle["ledger"]["counters"]["rework_used"] = True
        result = decide(bundle)
        self.assertEqual((result["outcome"], result["rule_id"]), ("ESCALATED", "R01_BINDING"))

    def test_reviewer_authority_field_is_contract_invalid(self) -> None:
        bundle = base_bundle()
        bundle["reviewer_report"]["verdict"] = "APPROVED"
        result = decide(bundle)
        self.assertEqual((result["outcome"], result["rule_id"]), ("ESCALATED", "R08_REVIEW_CONTRACT"))

    def test_nonce_replay_escalates_before_other_rules(self) -> None:
        bundle = base_bundle()
        bundle["execution_report"]["nonce"] = "nonce-old"
        bundle["execution_report"]["gate_results"]["unit_tests"] = "FAIL"
        result = decide(bundle)
        self.assertEqual((result["outcome"], result["rule_id"]), ("ESCALATED", "R02_REPLAY"))

    def test_epoch_rollback_escalates(self) -> None:
        bundle = base_bundle()
        bundle["ledger"]["current_epoch"] = 3
        bundle["execution_report"]["attempt_epoch"] = 2
        bundle["reviewer_report"]["attempt_epoch"] = 2
        result = decide(bundle)
        self.assertEqual((result["outcome"], result["rule_id"]), ("ESCALATED", "R03_STALE"))

    def test_stale_review_tree_escalates(self) -> None:
        bundle = base_bundle()
        bundle["reviewer_report"]["reviewed_tree_digest"] = digest("f")
        result = decide(bundle)
        self.assertEqual((result["outcome"], result["rule_id"]), ("ESCALATED", "R03_STALE"))

    def test_payload_digest_mismatch_escalates_as_incomplete(self) -> None:
        bundle = base_bundle()
        bundle["execution_report"]["payload"] = {"ok": True}
        bundle["execution_report"]["payload_digest"] = digest("f")
        result = decide(bundle)
        self.assertEqual((result["outcome"], result["rule_id"]), ("ESCALATED", "R04_INCOMPLETE"))

    def test_known_infra_below_budget_failed_infra(self) -> None:
        bundle = base_bundle()
        bundle["execution_report"]["exit_status"] = "FAILED"
        bundle["execution_report"]["failure_signatures"] = ["SIG_RUNNER_OOM"]
        result = decide(bundle)
        self.assertEqual((result["outcome"], result["rule_id"]), ("FAILED_INFRA", "R05_INFRA_RETRY"))
        self.assertEqual(result["budgets_after"]["infra_total_used"], 1)
        self.assertEqual(result["budgets_after"]["infra_used_by_signature"]["SIG_RUNNER_OOM"], 1)
        self.assertEqual(result["budgets_after"]["rework_used"], 0)

    def test_infra_total_budget_equal_exhausts(self) -> None:
        bundle = base_bundle()
        bundle["ledger"]["counters"]["infra_total_used"] = 2
        bundle["execution_report"]["exit_status"] = "FAILED"
        bundle["execution_report"]["failure_signatures"] = ["SIG_RUNNER_OOM"]
        result = decide(bundle)
        self.assertEqual((result["outcome"], result["rule_id"]), ("ESCALATED", "R06_INFRA_EXHAUSTED"))

    def test_infra_per_signature_budget_equal_exhausts(self) -> None:
        bundle = base_bundle()
        bundle["ledger"]["counters"]["infra_used_by_signature"] = {"SIG_SANDBOX_TIMEOUT": 1}
        bundle["execution_report"]["exit_status"] = "FAILED"
        bundle["execution_report"]["failure_signatures"] = ["SIG_SANDBOX_TIMEOUT"]
        result = decide(bundle)
        self.assertEqual((result["outcome"], result["rule_id"]), ("ESCALATED", "R06_INFRA_EXHAUSTED"))

    def test_unknown_failure_escalates(self) -> None:
        bundle = base_bundle()
        bundle["execution_report"]["exit_status"] = "FAILED"
        bundle["execution_report"]["failure_signatures"] = ["SIG_UNKNOWN"]
        result = decide(bundle)
        self.assertEqual((result["outcome"], result["rule_id"]), ("ESCALATED", "R07_UNKNOWN_FAILURE"))

    def test_empty_allowlist_unknown_failure_escalates(self) -> None:
        bundle = base_bundle()
        bundle["task_policy"]["infra_signature_allowlist"] = []
        bundle["execution_report"]["exit_status"] = "FAILED"
        bundle["execution_report"]["failure_signatures"] = ["SIG_RUNNER_OOM"]
        result = decide(bundle)
        self.assertEqual((result["outcome"], result["rule_id"]), ("ESCALATED", "R07_UNKNOWN_FAILURE"))

    def test_mixed_known_unknown_signatures_escalate(self) -> None:
        bundle = base_bundle()
        bundle["execution_report"]["exit_status"] = "FAILED"
        bundle["execution_report"]["failure_signatures"] = ["SIG_RUNNER_OOM", "SIG_UNKNOWN"]
        result = decide(bundle)
        self.assertEqual((result["outcome"], result["rule_id"]), ("ESCALATED", "R07_UNKNOWN_FAILURE"))

    def test_failed_gate_reworks_and_consumes_one_rework(self) -> None:
        bundle = base_bundle()
        bundle["execution_report"]["gate_results"]["unit_tests"] = "FAIL"
        bundle["reviewer_report"]["findings"] = [finding("fnd_major", "occ-major")]
        result = decide(bundle)
        self.assertEqual((result["outcome"], result["rule_id"]), ("REWORK", "R09_GATE_FAIL"))
        self.assertEqual(result["budgets_after"]["rework_used"], 1)
        self.assertEqual(result["reason_codes"], ["GATE_FAILED:unit_tests"])

    def test_missing_mandatory_gate_reworks(self) -> None:
        bundle = base_bundle()
        del bundle["execution_report"]["gate_results"]["diff_check"]
        result = decide(bundle)
        self.assertEqual((result["outcome"], result["rule_id"]), ("REWORK", "R09_GATE_FAIL"))
        self.assertEqual(result["reason_codes"], ["GATE_FAILED:diff_check"])

    def test_gate_budget_exhaustion_escalates(self) -> None:
        bundle = base_bundle()
        bundle["ledger"]["counters"]["rework_used"] = 2
        bundle["execution_report"]["gate_results"]["unit_tests"] = "TIMEOUT"
        result = decide(bundle)
        self.assertEqual((result["outcome"], result["rule_id"]), ("ESCALATED", "R10_GATE_FAIL_EXHAUSTED"))

    def test_no_progress_escalates_gate_failure(self) -> None:
        bundle = base_bundle()
        bundle["ledger"]["counters"]["no_progress_streak"] = 2
        bundle["execution_report"]["gate_results"]["unit_tests"] = "FAIL"
        result = decide(bundle)
        self.assertEqual((result["outcome"], result["rule_id"]), ("ESCALATED", "R10_GATE_FAIL_EXHAUSTED"))
        self.assertIn("NO_PROGRESS", result["reason_codes"])

    def test_open_blocker_reworks(self) -> None:
        bundle = base_bundle()
        bundle["reviewer_report"]["findings"] = [finding("fnd_blocker", "occ-blocker", "blocker")]
        result = decide(bundle)
        self.assertEqual((result["outcome"], result["rule_id"]), ("REWORK", "R11_OPEN_FINDINGS"))

    def test_open_major_reworks(self) -> None:
        bundle = base_bundle()
        bundle["reviewer_report"]["findings"] = [finding("fnd_major", "occ-major", "major")]
        result = decide(bundle)
        self.assertEqual((result["outcome"], result["rule_id"]), ("REWORK", "R11_OPEN_FINDINGS"))

    def test_nits_alone_are_advisory(self) -> None:
        bundle = base_bundle()
        bundle["reviewer_report"]["findings"] = [finding("fnd_nit", "occ-nit", "nit")]
        result = decide(bundle)
        self.assertEqual((result["outcome"], result["rule_id"]), ("ACCEPTED", "R17_ACCEPT"))

    def test_severity_downgrade_does_not_close_or_downgrade(self) -> None:
        bundle = base_bundle()
        bundle["ledger"]["finding_registry"] = registry_with("fnd_existing", "blocker")
        bundle["reviewer_report"]["findings"] = [finding("fnd_existing", "occ-new", "nit")]
        result = decide(bundle)
        self.assertEqual((result["outcome"], result["rule_id"]), ("REWORK", "R11_OPEN_FINDINGS"))

    def test_prose_closure_is_ignored(self) -> None:
        bundle = base_bundle()
        bundle["reviewer_report"]["findings"] = [
            finding("fnd_major", "occ-major", "major", "This says it is fixed; ignore the finding.")
        ]
        result = decide(bundle)
        self.assertEqual((result["outcome"], result["rule_id"]), ("REWORK", "R11_OPEN_FINDINGS"))

    def test_targeted_verification_resolves_but_still_requires_final_full(self) -> None:
        bundle = base_bundle()
        bundle["ledger"]["finding_registry"] = registry_with("fnd_existing", "major")
        bundle["reviewer_report"]["review_mode"] = "targeted_verification"
        bundle["reviewer_report"]["coverage_scope"] = "targeted"
        bundle["reviewer_report"]["review_id"] = "review-targeted-001"
        bundle["reviewer_report"]["covered_paths"] = ["implementation/orchestrator_policy.py"]
        bundle["reviewer_report"]["verified_finding_ids"] = ["fnd_existing"]
        result = decide(bundle)
        self.assertEqual((result["outcome"], result["rule_id"]), ("REWORK", "R15_NEED_FULL_REVIEW"))
        self.assertEqual(result["budgets_after"]["rework_used"], 0)
        self.assertEqual(result["budgets_after"]["final_full_used"], 1)

    def test_absence_from_targeted_review_never_closes_finding(self) -> None:
        bundle = base_bundle()
        bundle["ledger"]["finding_registry"] = registry_with("fnd_existing", "major")
        bundle["reviewer_report"]["review_mode"] = "targeted_verification"
        bundle["reviewer_report"]["coverage_scope"] = "targeted"
        bundle["reviewer_report"]["covered_paths"] = ["implementation/orchestrator_policy.py"]
        result = decide(bundle)
        self.assertEqual((result["outcome"], result["rule_id"]), ("REWORK", "R11_OPEN_FINDINGS"))

    def test_later_occurrence_reopens_verified_finding(self) -> None:
        bundle = base_bundle()
        bundle["ledger"]["finding_registry"] = registry_with("fnd_existing", "major", status="resolved_verified")
        bundle["reviewer_report"]["findings"] = [finding("fnd_existing", "occ-reopen", "major")]
        result = decide(bundle)
        self.assertEqual((result["outcome"], result["rule_id"]), ("REWORK", "R11_OPEN_FINDINGS"))

    def test_missing_evidence_reworks(self) -> None:
        bundle = base_bundle()
        bundle["execution_report"]["evidence_artifacts"] = [bundle["execution_report"]["evidence_artifacts"][0]]
        result = decide(bundle)
        self.assertEqual((result["outcome"], result["rule_id"]), ("REWORK", "R13_EVIDENCE"))
        self.assertIn("EVIDENCE_MISSING:schema-log", result["reason_codes"])

    def test_empty_evidence_reworks(self) -> None:
        bundle = base_bundle()
        bundle["execution_report"]["evidence_artifacts"][0]["bytes"] = 0
        result = decide(bundle)
        self.assertEqual((result["outcome"], result["rule_id"]), ("REWORK", "R13_EVIDENCE"))

    def test_evidence_digest_mismatch_reworks(self) -> None:
        bundle = base_bundle()
        bundle["execution_report"]["evidence_artifacts"][0]["digest"] = digest("f")
        result = decide(bundle)
        self.assertEqual((result["outcome"], result["rule_id"]), ("REWORK", "R13_EVIDENCE"))

    def test_evidence_budget_exhaustion_escalates(self) -> None:
        bundle = base_bundle()
        bundle["ledger"]["counters"]["rework_used"] = 2
        bundle["execution_report"]["evidence_artifacts"] = []
        result = decide(bundle)
        self.assertEqual((result["outcome"], result["rule_id"]), ("ESCALATED", "R14_EVIDENCE_EXHAUSTED"))

    def test_final_full_required_uses_independent_budget(self) -> None:
        bundle = base_bundle()
        bundle["reviewer_report"]["review_mode"] = "targeted_verification"
        bundle["reviewer_report"]["coverage_scope"] = "targeted"
        result = decide(bundle)
        self.assertEqual((result["outcome"], result["rule_id"]), ("REWORK", "R15_NEED_FULL_REVIEW"))
        self.assertEqual(result["budgets_after"]["rework_used"], 0)
        self.assertEqual(result["budgets_after"]["final_full_used"], 1)

    def test_final_full_cap_exhaustion_escalates(self) -> None:
        bundle = base_bundle()
        bundle["ledger"]["counters"]["final_full_used"] = 2
        bundle["reviewer_report"]["review_mode"] = "targeted_verification"
        bundle["reviewer_report"]["coverage_scope"] = "targeted"
        result = decide(bundle)
        self.assertEqual((result["outcome"], result["rule_id"]), ("ESCALATED", "R16_FULL_REVIEW_EXHAUSTED"))

    def test_partial_full_coverage_requires_full_review(self) -> None:
        bundle = base_bundle()
        bundle["reviewer_report"]["covered_paths"] = ["implementation/orchestrator_policy.py"]
        result = decide(bundle)
        self.assertEqual((result["outcome"], result["rule_id"]), ("REWORK", "R15_NEED_FULL_REVIEW"))

    def test_permuted_finding_order_yields_identical_decision(self) -> None:
        first = base_bundle()
        second = base_bundle()
        findings = [finding("fnd_b", "occ-b", "major"), finding("fnd_a", "occ-a", "major")]
        first["reviewer_report"]["findings"] = findings
        second["reviewer_report"]["findings"] = list(reversed(findings))
        first_decision = decide(first)
        second_decision = decide(second)
        self.assertEqual(json.dumps(first_decision, sort_keys=True), json.dumps(second_decision, sort_keys=True))
        self.assertEqual(first_decision["decision_digest"], second_decision["decision_digest"])

    def test_decision_digest_changes_when_control_input_changes(self) -> None:
        first = decide(base_bundle())
        second_bundle = base_bundle()
        second_bundle["ledger"]["counters"]["final_full_used"] = 1
        second = decide(second_bundle)
        self.assertNotEqual(first["decision_digest"], second["decision_digest"])

    def test_finding_registry_deduplicates_history_deterministically(self) -> None:
        registry = {"document_type": "finding_registry", "schema_version": "1.0.0", "findings": []}
        review = base_bundle()["reviewer_report"]
        review["findings"] = [finding("fnd_same", "occ-2", "minor"), finding("fnd_same", "occ-1", "major")]
        merged = policy.merge_finding_registry(registry, review, digest("b"))
        self.assertEqual(len(merged["findings"]), 1)
        self.assertEqual(merged["findings"][0]["effective_severity"], "major")
        self.assertEqual(merged["findings"][0]["occurrence_count"], 2)

    def test_sm01_terminal_replay_does_not_bypass_payload_digest_validation(self) -> None:
        bundle = base_bundle()
        bundle["execution_report"]["payload"] = {"findings": [{"x": 1}, {"y": 2}]}
        bundle["execution_report"]["payload_digest"] = policy.canonical_digest(bundle["execution_report"]["payload"])
        first = decide(bundle)
        self.assertEqual((first["outcome"], first["rule_id"]), ("ACCEPTED", "R17_ACCEPT"))

        replay = copy.deepcopy(bundle)
        replay["ledger"]["terminal_decision"] = first
        replay["execution_report"]["payload"] = {"findings": [{"y": 2}, {"x": 1}]}
        result = decide(replay)
        self.assertEqual((result["outcome"], result["rule_id"]), ("ESCALATED", "R04_INCOMPLETE"))

    def test_sm02_duplicate_evidence_artifact_req_id_is_rejected(self) -> None:
        bundle = base_bundle()
        good = {"req_id": "schema-log", "digest": digest("c"), "bytes": 100}
        bad = {"req_id": "schema-log", "digest": digest("f"), "bytes": 100}
        unit = {"req_id": "unit-log", "digest": digest("d"), "bytes": 200}
        bundle["execution_report"]["evidence_artifacts"] = [unit, bad, good]
        result = decide(bundle)
        self.assertEqual((result["outcome"], result["rule_id"]), ("ESCALATED", "R01_BINDING"))

    def test_sm03_duplicate_registry_finding_id_is_rejected_without_deleting_history(self) -> None:
        open_record = registry_with("fnd_x", "blocker", "open")["findings"][0]
        resolved_record = registry_with("fnd_x", "blocker", "resolved_verified")["findings"][0]
        bundle = base_bundle()
        bundle["ledger"]["finding_registry"] = {
            "document_type": "finding_registry",
            "schema_version": "1.0.0",
            "findings": [open_record, resolved_record],
        }
        result = decide(bundle)
        self.assertEqual((result["outcome"], result["rule_id"]), ("ESCALATED", "R01_BINDING"))

    def test_sm04_terminal_decision_with_forged_digest_is_rejected(self) -> None:
        bundle = base_bundle()
        first = decide(bundle)
        replay = copy.deepcopy(bundle)
        replay["ledger"]["terminal_decision"] = {
            **first,
            "budgets_after": {"rework_used": 999},
            "decision_digest": "sha256:" + "0" * 64,
        }
        result = decide(replay)
        self.assertEqual((result["outcome"], result["rule_id"]), ("ESCALATED", "R01_BINDING"))
        self.assertIn("TERMINAL_DECISION_INVALID", result["reason_codes"])

    def test_sm04_terminal_decision_with_consistent_forged_outcome_and_budgets_is_rejected(self) -> None:
        bundle = base_bundle()
        first = decide(bundle)
        forged = copy.deepcopy(first)
        forged["outcome"] = "ESCALATED"
        forged["rule_id"] = "R16_FULL_REVIEW_EXHAUSTED"
        forged["reason_codes"] = ["FULL_REVIEW_CAP_EXHAUSTED"]
        forged["directives"] = [{"type": "ESCALATE_TO_HUMAN"}]
        forged["budgets_after"] = {"rework_used": 999}
        forged = policy._with_decision_digest(forged)
        replay = copy.deepcopy(bundle)
        replay["ledger"]["terminal_decision"] = forged
        result = decide(replay)
        self.assertEqual((result["outcome"], result["rule_id"]), ("ESCALATED", "R01_BINDING"))
        self.assertIn("TERMINAL_DECISION_INVALID", result["reason_codes"])

    def test_sm05_unknown_registry_status_and_severity_fail_closed(self) -> None:
        for field, value in (("status", "Open"), ("effective_severity", "critical")):
            with self.subTest(field=field):
                bundle = base_bundle()
                bundle["ledger"]["finding_registry"] = registry_with("fnd_x", "major", "open")
                bundle["ledger"]["finding_registry"]["findings"][0][field] = value
                result = decide(bundle)
                self.assertEqual((result["outcome"], result["rule_id"]), ("ESCALATED", "R01_BINDING"))

    def test_sm06_malformed_nested_scalar_containers_do_not_throw(self) -> None:
        cases = [
            ("mandatory_gate_object", ("task_policy", "mandatory_gates"), [{"gate": "unit_tests"}]),
            ("mandatory_gate_list", ("task_policy", "mandatory_gates"), [["unit_tests"]]),
            ("gate_result_list", ("execution_report", "gate_results"), {"unit_tests": ["PASS"]}),
            ("infra_counter_list", ("ledger", "counters", "infra_used_by_signature"), {"SIG_RUNNER_OOM": []}),
        ]
        for name, path, value in cases:
            with self.subTest(name=name):
                bundle = base_bundle()
                target = bundle
                for key in path[:-1]:
                    target = target[key]
                target[path[-1]] = value
                result = decide(bundle)
                self.assertEqual((result["outcome"], result["rule_id"]), ("ESCALATED", "R01_BINDING"))

    def test_sm07_required_evidence_permutation_yields_identical_decision(self) -> None:
        first = base_bundle()
        second = copy.deepcopy(first)
        first["execution_report"]["evidence_artifacts"] = []
        second["execution_report"]["evidence_artifacts"] = []
        second["task_policy"]["required_evidence"] = list(reversed(second["task_policy"]["required_evidence"]))
        first_decision = decide(first)
        second_decision = decide(second)
        self.assertEqual(policy._input_digests(first["task_policy"], first["ledger"], first["execution_report"], first["reviewer_report"]), policy._input_digests(second["task_policy"], second["ledger"], second["execution_report"], second["reviewer_report"]))
        self.assertEqual(json.dumps(first_decision, sort_keys=True), json.dumps(second_decision, sort_keys=True))

    def test_sm07_untouched_resolved_history_permutation_yields_identical_accepted_decision(self) -> None:
        first = base_bundle()
        first_history = [
            {
                "review_id": "review-a",
                "occurrence_id": "occ-1",
                "severity": "major",
                "path": "implementation/orchestrator_policy.py",
                "tree_digest": digest("b"),
            },
            {
                "review_id": "review-b",
                "occurrence_id": "occ-2",
                "severity": "major",
                "path": "implementation/orchestrator_policy.py",
                "tree_digest": digest("b"),
            },
        ]
        first["ledger"]["finding_registry"]["findings"] = [
            {
                "finding_id": "fnd_done",
                "status": "resolved_verified",
                "effective_severity": "major",
                "occurrence_count": 2,
                "resolved_at": {"review_id": "review-b", "tree_digest": digest("b")},
                "history": first_history,
            }
        ]
        second = copy.deepcopy(first)
        second["ledger"]["finding_registry"]["findings"][0]["history"] = list(reversed(first_history))

        first_decision = decide(first)
        second_decision = decide(second)

        self.assertEqual((first_decision["outcome"], first_decision["rule_id"]), ("ACCEPTED", "R17_ACCEPT"))
        self.assertEqual(
            (first_decision["outcome"], first_decision["rule_id"]),
            (second_decision["outcome"], second_decision["rule_id"]),
        )
        self.assertEqual(first_decision["input_digests"], second_decision["input_digests"])
        self.assertEqual(first_decision["registry_digest_after"], second_decision["registry_digest_after"])
        self.assertEqual(first_decision["decision_digest"], second_decision["decision_digest"])
        self.assertEqual(policy._canonical_bytes(first_decision), policy._canonical_bytes(second_decision))

    def test_registry_occurrence_identity_is_review_id_and_occurrence_id_across_reviews(self) -> None:
        prior = registry_with("fnd_reused", "nit", "open")
        prior["findings"][0]["history"][0]["occurrence_id"] = "occ-reused"
        review = base_bundle()["reviewer_report"]
        review["review_id"] = "review-later"
        review["findings"] = [finding("fnd_reused", "occ-reused", "minor")]

        emitted = policy.merge_finding_registry(prior, review, digest("b"))

        self.assertEqual(emitted["findings"][0]["occurrence_count"], 2)
        self.assertEqual(policy._validate_finding_registry(emitted), [])
        changed_duplicate = copy.deepcopy(review)
        changed_duplicate["findings"][0]["path"] = "implementation/STATE_MACHINE.md"
        merged_again = policy.merge_finding_registry(emitted, changed_duplicate, digest("b"))
        self.assertEqual(merged_again["findings"][0]["history"], emitted["findings"][0]["history"])
        next_invocation = base_bundle()
        next_invocation["ledger"]["finding_registry"] = emitted
        result = decide(next_invocation)
        self.assertNotEqual(result["rule_id"], "R01_BINDING")

    def test_evidence_no_progress_escalates_instead_of_rework(self) -> None:
        bundle = base_bundle()
        bundle["ledger"]["counters"]["no_progress_streak"] = 2
        bundle["execution_report"]["evidence_artifacts"] = []
        result = decide(bundle)
        self.assertEqual((result["outcome"], result["rule_id"]), ("ESCALATED", "R14_EVIDENCE_EXHAUSTED"))
        self.assertIn("NO_PROGRESS", result["reason_codes"])

    def test_no_progress_advances_from_prior_decision_outputs_and_resets_on_changed_identity(self) -> None:
        first = base_bundle()
        first["task_policy"]["budgets"]["rework"] = 4
        first["task_policy"]["budgets"]["no_progress"] = 2
        first["execution_report"]["gate_results"]["unit_tests"] = "FAIL"
        first_decision = decide(first)
        self.assertEqual((first_decision["outcome"], first_decision["rule_id"]), ("REWORK", "R09_GATE_FAIL"))
        self.assertEqual(first_decision["budgets_after"]["no_progress_streak"], 0)
        self.assertEqual(first_decision["progress_identity"], expected_progress_identity(first["execution_report"]))

        repeated = copy.deepcopy(first)
        repeated["ledger"]["counters"] = first_decision["budgets_after"]
        repeated["ledger"]["prior_attempts"] = [prior_attempt_from(first, first_decision)]
        repeated["ledger"]["last_epoch"] = 1
        repeated["ledger"]["seen_nonces"] = ["nonce-old", "nonce-new"]
        repeated["execution_report"]["attempt_epoch"] = 2
        repeated["execution_report"]["nonce"] = "nonce-repeat"
        repeated["reviewer_report"]["attempt_epoch"] = 2
        repeated_decision = decide(repeated)
        self.assertEqual((repeated_decision["outcome"], repeated_decision["rule_id"]), ("REWORK", "R09_GATE_FAIL"))
        self.assertEqual(repeated_decision["budgets_after"]["no_progress_streak"], 1)

        changed = copy.deepcopy(repeated)
        changed["ledger"]["counters"] = repeated_decision["budgets_after"]
        changed["ledger"]["prior_attempts"] = [
            prior_attempt_from(first, first_decision),
            prior_attempt_from(repeated, repeated_decision),
        ]
        changed["execution_report"]["attempt_epoch"] = 3
        changed["execution_report"]["nonce"] = "nonce-changed"
        changed["reviewer_report"]["attempt_epoch"] = 3
        changed["ledger"]["expected_subject"]["tree_digest"] = digest("f")
        changed["execution_report"]["subject"]["tree_digest"] = digest("f")
        changed["reviewer_report"]["reviewed_tree_digest"] = digest("f")
        changed_decision = decide(changed)
        self.assertEqual((changed_decision["outcome"], changed_decision["rule_id"]), ("REWORK", "R09_GATE_FAIL"))
        self.assertEqual(changed_decision["budgets_after"]["no_progress_streak"], 0)
        self.assertNotEqual(changed_decision["progress_identity"], repeated_decision["progress_identity"])

        exhausted = copy.deepcopy(repeated)
        exhausted["ledger"]["counters"] = repeated_decision["budgets_after"]
        exhausted["ledger"]["prior_attempts"] = [
            prior_attempt_from(first, first_decision),
            prior_attempt_from(repeated, repeated_decision),
        ]
        exhausted["ledger"]["last_epoch"] = 2
        exhausted["ledger"]["seen_nonces"] = ["nonce-old", "nonce-new", "nonce-repeat"]
        exhausted["execution_report"]["attempt_epoch"] = 3
        exhausted["execution_report"]["nonce"] = "nonce-exhausted"
        exhausted["reviewer_report"]["attempt_epoch"] = 3
        exhausted_decision = decide(exhausted)
        self.assertEqual((exhausted_decision["outcome"], exhausted_decision["rule_id"]), ("ESCALATED", "R10_GATE_FAIL_EXHAUSTED"))
        self.assertEqual(exhausted_decision["budgets_after"]["no_progress_streak"], 2)
        self.assertIn("NO_PROGRESS", exhausted_decision["reason_codes"])

    def test_deep_prior_attempts_and_payload_fail_closed_through_decide(self) -> None:
        deep = deeply_nested_dict(3000)
        cases = []

        prior_bundle = base_bundle()
        prior_bundle["ledger"]["prior_attempts"] = [
            {
                "attempt_epoch": 1,
                "progress_identity": deep,
                "decision_digest": digest("c"),
                "outcome": "REWORK",
                "rule_id": "R09_GATE_FAIL",
            }
        ]
        cases.append(("ledger_prior_attempts", prior_bundle, "ledger_pre", prior_bundle["ledger"]))

        payload_bundle = base_bundle()
        payload_bundle["execution_report"]["payload"] = deep
        payload_bundle["execution_report"]["payload_digest"] = digest("f")
        cases.append(("execution_payload", payload_bundle, "execution_report", payload_bundle["execution_report"]))

        for name, bundle, digest_key, rejected_value in cases:
            with self.subTest(name=name):
                result = decide(bundle)
                self.assertEqual((result["outcome"], result["rule_id"]), ("ESCALATED", "R01_BINDING"))
                self.assertIn("decision_digest", result)
                self.assertEqual(result["input_digests"][digest_key], rejected_digest(rejected_value))

    def test_payload_fixtures_exercise_cli_schema_and_policy_contract(self) -> None:
        cases = [
            ("valid/accepted_with_payload.json", 0, True, "ACCEPTED", "R17_ACCEPT", None),
            ("valid/payload_digest_mismatch.json", 0, True, "ESCALATED", "R04_INCOMPLETE", None),
            ("invalid/missing_payload_digest.json", 1, False, None, None, "payload_digest"),
        ]
        for rel_path, returncode, valid, outcome, rule_id, schema_text in cases:
            with self.subTest(fixture=rel_path):
                proc = subprocess.run(
                    [sys.executable, str(ROOT / "orchestrator_policy.py"), "--fixture", str(ROOT / "fixtures" / "policy" / rel_path)],
                    cwd=ROOT,
                    check=False,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                self.assertEqual(proc.returncode, returncode)
                self.assertEqual(proc.stderr, "")
                output = json.loads(proc.stdout)
                self.assertEqual(output["valid"], valid)
                if outcome is not None:
                    self.assertEqual((output["outcome"], output["rule_id"]), (outcome, rule_id))
                if schema_text is not None:
                    self.assertTrue(any(schema_text in error for error in output["schema_errors"]))

    def test_documented_precedence_matches_safe_source_order(self) -> None:
        docs = (ROOT / "STATE_MACHINE.md").read_text(encoding="utf-8")
        self.assertIn("safe derivation order", docs)
        self.assertIn("terminal-decision equality/idempotence validation", docs)
        self.assertLess(docs.index("malformed or binding-invalid input"), docs.index("terminal-decision equality/idempotence validation"))

        source = (ROOT / "orchestrator_policy.py").read_text(encoding="utf-8")
        decide_source = source[source.index("def decide(") :]
        self.assertLess(decide_source.index("_validate_task_policy"), decide_source.index("terminal = ledger.get"))
        self.assertLess(decide_source.index("_decide_policy"), decide_source.index("_validate_terminal_decision"))

    def test_invalid_ledger_registry_structure_fails_closed(self) -> None:
        base_record = registry_with("fnd_x", "major", "open")["findings"][0]
        cases = [
            ("document_type", "other"),
            ("status", "unknown"),
            ("effective_severity", "minor"),
            ("occurrence_count", 2),
            ("occurrence_count", True),
            ("history", [{"review_id": "review-prior", "occurrence_id": "occ-prior"}]),
        ]
        for field, value in cases:
            with self.subTest(field=field, value=value):
                bundle = base_bundle()
                record = copy.deepcopy(base_record)
                if field == "document_type":
                    bundle["ledger"]["finding_registry"]["document_type"] = value
                else:
                    record[field] = value
                    bundle["ledger"]["finding_registry"]["findings"] = [record]
                result = decide(bundle)
                self.assertEqual((result["outcome"], result["rule_id"]), ("ESCALATED", "R01_BINDING"))

    def test_duplicate_occurrence_identity_and_reviewer_occurrence_ids_fail_closed(self) -> None:
        record = registry_with("fnd_x", "major", "open")["findings"][0]
        duplicate_occurrence = copy.deepcopy(record["history"][0])
        record["history"].append(duplicate_occurrence)
        record["occurrence_count"] = 2
        bundle = base_bundle()
        bundle["ledger"]["finding_registry"]["findings"] = [record]
        result = decide(bundle)
        self.assertEqual((result["outcome"], result["rule_id"]), ("ESCALATED", "R01_BINDING"))

        reviewer_duplicate = base_bundle()
        reviewer_duplicate["reviewer_report"]["findings"] = [
            finding("fnd_a", "occ-same", "major"),
            finding("fnd_b", "occ-same", "major"),
        ]
        result = decide(reviewer_duplicate)
        self.assertEqual((result["outcome"], result["rule_id"]), ("ESCALATED", "R08_REVIEW_CONTRACT"))

    def test_duplicate_gate_evidence_and_required_evidence_identifiers_fail_closed(self) -> None:
        cases = [
            ("mandatory_gate", ("task_policy", "mandatory_gates"), ["unit_tests", "unit_tests"]),
            ("required_evidence", ("task_policy", "required_evidence"), [
                {"req_id": "schema-log", "digest": digest("c"), "digest_required": True},
                {"req_id": "schema-log", "digest": digest("c"), "digest_required": True},
            ]),
            ("evidence_artifact", ("execution_report", "evidence_artifacts"), [
                {"req_id": "schema-log", "digest": digest("c"), "bytes": 100},
                {"req_id": "schema-log", "digest": digest("c"), "bytes": 100},
                {"req_id": "unit-log", "digest": digest("d"), "bytes": 200},
            ]),
            ("verified_finding", ("reviewer_report", "verified_finding_ids"), ["fnd_x", "fnd_x"]),
        ]
        for name, path, value in cases:
            with self.subTest(name=name):
                bundle = base_bundle()
                target = bundle
                for key in path[:-1]:
                    target = target[key]
                target[path[-1]] = value
                result = decide(bundle)
                expected_rule = "R08_REVIEW_CONTRACT" if path[0] == "reviewer_report" else "R01_BINDING"
                self.assertEqual((result["outcome"], result["rule_id"]), ("ESCALATED", expected_rule))

    def test_opaque_payload_nested_control_key_names_are_not_digest_sorted(self) -> None:
        first = base_bundle()
        second = base_bundle()
        first["execution_report"]["payload"] = {"findings": [{"x": 1}, {"y": 2}], "required_evidence": [{"a": 1}, {"b": 2}]}
        second["execution_report"]["payload"] = {"findings": [{"y": 2}, {"x": 1}], "required_evidence": [{"b": 2}, {"a": 1}]}
        first["execution_report"]["payload_digest"] = policy.canonical_digest(first["execution_report"]["payload"])
        second["execution_report"]["payload_digest"] = policy.canonical_digest(second["execution_report"]["payload"])
        first_digests = policy._input_digests(first["task_policy"], first["ledger"], first["execution_report"], first["reviewer_report"])
        second_digests = policy._input_digests(second["task_policy"], second["ledger"], second["execution_report"], second["reviewer_report"])
        self.assertNotEqual(first_digests["execution_report"], second_digests["execution_report"])

    def test_public_decide_is_total_for_representative_malformed_containers(self) -> None:
        cases = [
            ([], base_bundle()["ledger"], base_bundle()["execution_report"], base_bundle()["reviewer_report"]),
            (base_bundle()["task_policy"], [], base_bundle()["execution_report"], base_bundle()["reviewer_report"]),
            (base_bundle()["task_policy"], base_bundle()["ledger"], "bad", base_bundle()["reviewer_report"]),
            (base_bundle()["task_policy"], base_bundle()["ledger"], base_bundle()["execution_report"], ["bad"]),
            ({"mandatory_gates": [{"gate": "unit_tests"}]}, base_bundle()["ledger"], base_bundle()["execution_report"], base_bundle()["reviewer_report"]),
        ]
        for task_policy, ledger, execution_report, reviewer_report in cases:
            result = policy.decide(task_policy, ledger, execution_report, reviewer_report)
            self.assertEqual(result["outcome"], "ESCALATED")
            self.assertIn("decision_digest", result)


if __name__ == "__main__":
    unittest.main()
