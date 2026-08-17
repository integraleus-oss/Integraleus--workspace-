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

    def _normalize(
        self,
        verdict: dict,
        manifest_path: Path | None = None,
        prior_path: Path | None = None,
    ) -> tuple[dict, list[dict]]:
        verdict_path = self.root / "normalize-input.json"
        write_json(verdict_path, verdict)
        validation = projection.VALIDATOR.validate_document(
            verdict_path,
            trusted_manifest_path=manifest_path or self.manifest_path,
            prior_findings_path=prior_path,
        )
        return projection.normalize_transport_defects(verdict, validation["errors"])

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

    def test_overlong_finding_title_is_truncated_without_changing_rationale(self) -> None:
        verdict = copy.deepcopy(self.verdict)
        original_rationale = verdict["findings"][0]["rationale"]
        verdict["findings"][0]["title"] = "T" * 200
        verdict_path = self.root / "overlong-title.json"
        write_json(verdict_path, verdict)
        value, validation = projection.build_projection(
            verdict_path, self.manifest_path, self.binding_path
        )
        second_value, second_validation = projection.build_projection(
            verdict_path, self.manifest_path, self.binding_path
        )
        self.assertEqual(value, second_value)
        self.assertEqual(
            validation["transport_normalizations"],
            second_validation["transport_normalizations"],
        )
        self.assertEqual(value["findings"][0]["message"], "T" * 160)
        self.assertEqual(verdict["findings"][0]["rationale"], original_rationale)
        self.assertEqual(
            validation["transport_normalizations"][0]["operation"],
            "truncate_finding_title",
        )

    def test_unknown_fingerprint_properties_are_removed_before_id_normalization(self) -> None:
        verdict = copy.deepcopy(self.verdict)
        verdict["findings"][0]["fingerprint"]["excerptless"] = True
        verdict_path = self.root / "unknown-fingerprint-property.json"
        write_json(verdict_path, verdict)

        value, validation = projection.build_projection(
            verdict_path, self.manifest_path, self.binding_path
        )
        second_value, second_validation = projection.build_projection(
            verdict_path, self.manifest_path, self.binding_path
        )
        self.assertEqual(value, second_value)
        self.assertEqual(
            validation["transport_normalizations"],
            second_validation["transport_normalizations"],
        )

        cleaned_fingerprint = copy.deepcopy(verdict["findings"][0]["fingerprint"])
        del cleaned_fingerprint["excerptless"]
        self.assertEqual(
            value["findings"][0]["finding_id"],
            projection.VALIDATOR.expected_finding_id(cleaned_fingerprint),
        )
        self.assertEqual(len(validation["transport_normalizations"]), 1)
        self.assertEqual(
            validation["transport_normalizations"][0],
            {
                "operation": "remove_unknown_fingerprint_properties",
                "pointer": "/findings/0/fingerprint",
                "removed": ["excerptless"],
            },
        )

    def test_fingerprint_key_derivation_matches_flat_closed_canonical_schema(self) -> None:
        schema = json.loads(projection.VALIDATOR.DEFAULT_SCHEMA.read_text(encoding="utf-8"))
        fingerprint_schema = schema["$defs"]["fingerprint"]
        self.assertEqual(
            set(fingerprint_schema),
            {"type", "properties", "required", "additionalProperties"},
        )
        self.assertIs(fingerprint_schema["additionalProperties"], False)
        self.assertNotIn("allOf", fingerprint_schema)
        self.assertNotIn("patternProperties", fingerprint_schema)
        self.assertEqual(
            projection.FINGERPRINT_KEYS,
            frozenset(fingerprint_schema["properties"]),
        )
        self.assertEqual(
            projection.FINGERPRINT_KEYS,
            frozenset(fingerprint_schema["required"]),
        )
        fixture_paths = list((CORE / "fixtures/valid").glob("*.json"))
        self.assertTrue(fixture_paths)
        for fixture_path in fixture_paths:
            fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
            for finding in fixture.get("findings", []):
                self.assertLessEqual(
                    set(finding["fingerprint"]),
                    projection.FINGERPRINT_KEYS,
                    fixture_path.name,
                )

    def test_fingerprint_key_derivation_rejects_noncanonical_shapes(self) -> None:
        schema = json.loads(projection.VALIDATOR.DEFAULT_SCHEMA.read_text(encoding="utf-8"))
        mutations = (
            lambda value: value["$defs"]["fingerprint"].update({"anyOf": []}),
            lambda value: value["$defs"]["fingerprint"].update({"type": "array"}),
            lambda value: value["$defs"]["fingerprint"].update(
                {"additionalProperties": True}
            ),
            lambda value: value["$defs"]["fingerprint"]["required"].pop(),
            lambda value: value["$defs"]["fingerprint"].update({"properties": []}),
            lambda value: value["$defs"].pop("fingerprint"),
        )
        for mutate in mutations:
            with self.subTest(mutation=mutate):
                candidate = copy.deepcopy(schema)
                mutate(candidate)
                with self.assertRaises(RuntimeError):
                    projection._derive_fingerprint_keys(candidate)

    def test_positive_verification_statuses_are_schema_derived(self) -> None:
        schema = json.loads(projection.VALIDATOR.DEFAULT_SCHEMA.read_text(encoding="utf-8"))
        statuses = schema["$defs"]["verification"]["properties"]["results"][
            "items"
        ]["properties"]["observed_status"]["enum"]
        self.assertEqual(set(statuses), {
            "still_open", "appears_fixed", "not_verifiable", "no_longer_applicable"
        })
        self.assertEqual(projection.POSITIVE_VERIFICATION_STATUSES, frozenset({
            "appears_fixed", "no_longer_applicable"
        }))
        self.assertEqual(
            projection.SCHEMA_POSITIVE_VERIFICATION_STATUSES,
            projection.POSITIVE_VERIFICATION_STATUSES,
        )
        changed = copy.deepcopy(schema)
        changed["$defs"]["verification"]["properties"]["results"]["items"][
            "properties"
        ]["observed_status"]["enum"].append("regressed")
        with self.assertRaises(RuntimeError):
            projection._derive_positive_verification_statuses(changed)

    def test_criteria_contract_enums_are_pinned(self) -> None:
        schema = json.loads(projection.VALIDATOR.DEFAULT_SCHEMA.read_text(encoding="utf-8"))
        projection._assert_criteria_contract_enums(schema)
        for property_name in ("status", "verification_method"):
            with self.subTest(property_name=property_name):
                changed = copy.deepcopy(schema)
                changed["$defs"]["criterion_coverage"]["properties"][property_name][
                    "enum"
                ].append("future_value")
                with self.assertRaises(RuntimeError):
                    projection._assert_criteria_contract_enums(changed)

    def test_command_evidence_kinds_match_validator_requirement(self) -> None:
        schema = json.loads(projection.VALIDATOR.DEFAULT_SCHEMA.read_text(encoding="utf-8"))
        kinds = schema["$defs"]["evidence"]["properties"]["kind"]["enum"]
        rejected_without_command = set()
        for kind in kinds:
            verdict = copy.deepcopy(self.verdict)
            evidence = verdict["findings"][0]["evidence"][0]
            evidence["kind"] = kind
            evidence.pop("command", None)
            verdict_path = self.root / f"command-requirement-{kind}.json"
            write_json(verdict_path, verdict)
            validation = projection.VALIDATOR.validate_document(
                verdict_path, trusted_manifest_path=self.manifest_path
            )
            command_errors = [
                error for error in validation["errors"]
                if error.get("pointer") == "/findings/0/evidence/0/command"
                and "requires a command block" in error.get("message", "")
            ]
            if command_errors:
                rejected_without_command.add(kind)
        self.assertEqual(
            projection.COMMAND_EVIDENCE_KINDS,
            frozenset(rejected_without_command),
        )

    def test_test_result_without_command_is_discarded_and_claim_becomes_unverified(self) -> None:
        verdict, manifest = self._nonblocking_final_verdict_and_manifest()
        invalid_evidence_id = "ev_" + "0" * 32
        verdict["findings"][0]["evidence"].append({
            "evidence_id": invalid_evidence_id,
            "kind": "test_result",
            "description": "Claimed test result without the required command block.",
            "excerpt": "48 tests passed",
            "excerpt_truncated": False,
        })
        verdict["criteria_coverage"][0]["evidence_ids"].append(invalid_evidence_id)
        manifest_path = self.root / "missing-test-command-manifest.json"
        write_json(manifest_path, manifest)
        normalized, changes = self._normalize(verdict, manifest_path)

        self.assertNotIn(
            invalid_evidence_id,
            [item["evidence_id"] for item in normalized["findings"][0]["evidence"]],
        )
        coverage = normalized["criteria_coverage"][0]
        self.assertEqual(coverage["status"], "not_verifiable")
        self.assertEqual(coverage["verification_method"], "not_attempted")
        self.assertNotIn(invalid_evidence_id, coverage["evidence_ids"])
        self.assertEqual(
            [change["operation"] for change in changes],
            [
                "discard_evidence_without_required_command",
                "remove_undefined_evidence_ids",
                "mark_criterion_not_verifiable",
            ],
        )

        verdict_path = self.root / "missing-test-command.json"
        write_json(verdict_path, verdict)
        with self.assertRaisesRegex(
            projection.ProjectionError, "full review has incomplete criteria coverage"
        ):
            projection.build_projection(verdict_path, manifest_path, self.binding_path)

    def test_partially_satisfied_claim_losing_evidence_becomes_unverified(self) -> None:
        verdict, manifest = self._nonblocking_final_verdict_and_manifest()
        invalid_evidence_id = "ev_" + "0" * 32
        verdict["findings"][0]["evidence"].append({
            "evidence_id": invalid_evidence_id,
            "kind": "test_result",
            "description": "Claimed result without command.",
            "excerpt": "tests passed",
            "excerpt_truncated": False,
        })
        coverage = verdict["criteria_coverage"][0]
        coverage["status"] = "partially_satisfied"
        coverage["evidence_ids"] = [invalid_evidence_id]
        coverage["linked_occurrence_ids"] = [verdict["findings"][0]["occurrence_id"]]
        manifest_path = self.root / "partial-commandless-manifest.json"
        verdict_path = self.root / "partial-commandless.json"
        write_json(manifest_path, manifest)
        write_json(verdict_path, verdict)
        normalized, changes = self._normalize(verdict, manifest_path)
        self.assertEqual(normalized["criteria_coverage"][0]["status"], "not_verifiable")
        self.assertEqual(normalized["criteria_coverage"][0]["evidence_ids"], [])
        self.assertIn(
            "mark_criterion_not_verifiable",
            [change["operation"] for change in changes],
        )
        with self.assertRaisesRegex(
            projection.ProjectionError, "full review has incomplete criteria coverage"
        ):
            projection.build_projection(
                verdict_path, manifest_path, self.binding_path
            )

    def test_commandless_evidence_with_another_defect_is_not_laundered(self) -> None:
        cases = {
            "missing_description": lambda verdict, item: item.pop("description"),
            "duplicate_evidence_id": lambda verdict, item: item.update({
                "evidence_id": verdict["findings"][0]["evidence"][0]["evidence_id"]
            }),
            "missing_artifact_digest": lambda verdict, item: item.update({
                "artifact_ref": "artifacts/reviews/co-defect.log"
            }),
        }
        for name, mutate in cases.items():
            with self.subTest(name=name):
                verdict = copy.deepcopy(self.verdict)
                item = {
                    "evidence_id": "ev_" + "0" * 32,
                    "kind": "test_result",
                    "description": "Commandless evidence with another defect.",
                    "excerpt": "tests passed",
                    "excerpt_truncated": False,
                }
                mutate(verdict, item)
                verdict["findings"][0]["evidence"].append(item)
                verdict_path = self.root / f"commandless-co-defect-{name}.json"
                write_json(verdict_path, verdict)
                raw_validation = projection.VALIDATOR.validate_document(
                    verdict_path, trusted_manifest_path=self.manifest_path
                )
                if name == "missing_artifact_digest":
                    item_pointer = "/findings/0/evidence/1"
                    item_codes = {
                        error["code"] for error in raw_validation["errors"]
                        if error["pointer"] == item_pointer
                        or error["pointer"].startswith(item_pointer + "/")
                    }
                    self.assertEqual(
                        item_codes,
                        {"kind_inconsistent_evidence", "evidence_digest_required"},
                    )
                normalized, changes = self._normalize(verdict)
                self.assertIn(item, normalized["findings"][0]["evidence"])
                self.assertNotIn(
                    "discard_evidence_without_required_command",
                    [change["operation"] for change in changes],
                )
                with self.assertRaises(projection.ContractValidationError):
                    projection.build_projection(
                        verdict_path, self.manifest_path, self.binding_path
                    )

    def test_present_but_malformed_command_remains_contract_failure(self) -> None:
        verdict = copy.deepcopy(self.verdict)
        verdict["findings"][0]["evidence"][0]["kind"] = "test_result"
        verdict["findings"][0]["evidence"][0]["command"] = "python3 tests.py"
        normalized, changes = self._normalize(verdict)
        self.assertEqual(
            normalized["findings"][0]["evidence"][0]["command"],
            "python3 tests.py",
        )
        self.assertEqual(changes, [])

        verdict_path = self.root / "malformed-command.json"
        write_json(verdict_path, verdict)
        with self.assertRaises(projection.ContractValidationError):
            projection.build_projection(
                verdict_path, self.manifest_path, self.binding_path
            )

    def test_null_command_remains_contract_failure(self) -> None:
        verdict = copy.deepcopy(self.verdict)
        evidence = verdict["findings"][0]["evidence"][0]
        evidence["kind"] = "test_result"
        evidence["command"] = None
        normalized, changes = self._normalize(verdict)
        self.assertIsNone(normalized["findings"][0]["evidence"][0]["command"])
        self.assertEqual(changes, [])

        verdict_path = self.root / "null-command.json"
        write_json(verdict_path, verdict)
        with self.assertRaises(projection.ContractValidationError):
            projection.build_projection(
                verdict_path, self.manifest_path, self.binding_path
            )

    def test_noncommand_evidence_without_command_is_retained(self) -> None:
        verdict = copy.deepcopy(self.verdict)
        evidence = verdict["findings"][0]["evidence"][0]
        evidence["kind"] = "file_excerpt"
        evidence.pop("command", None)
        normalized, changes = self._normalize(verdict)
        self.assertEqual(normalized["findings"][0]["evidence"], [evidence])
        self.assertEqual(changes, [])

    def test_discarding_only_evidence_item_remains_contract_failure(self) -> None:
        verdict = copy.deepcopy(self.verdict)
        verdict["findings"][0]["evidence"] = [{
            "evidence_id": "ev_" + "0" * 32,
            "kind": "test_result",
            "description": "Only evidence is missing its command block.",
            "excerpt": "tests passed",
            "excerpt_truncated": False,
        }]
        normalized, changes = self._normalize(verdict)
        self.assertEqual(len(normalized["findings"][0]["evidence"]), 1)
        self.assertNotIn(
            "discard_evidence_without_required_command",
            [change["operation"] for change in changes],
        )

        verdict_path = self.root / "empty-evidence-after-discard.json"
        write_json(verdict_path, verdict)
        with self.assertRaises(projection.ContractValidationError):
            projection.build_projection(
                verdict_path, self.manifest_path, self.binding_path
            )

    def test_targeted_claim_with_discarded_evidence_becomes_not_verifiable(self) -> None:
        verdict_path = CORE / "fixtures/valid/targeted_verification.json"
        manifest_path = CORE / "fixtures/trusted/manifest_targeted.json"
        prior_path = CORE / "fixtures/trusted/prior_findings_targeted.json"
        for observed_status in ("appears_fixed", "no_longer_applicable"):
            with self.subTest(observed_status=observed_status):
                verdict = json.loads(verdict_path.read_text(encoding="utf-8"))
                result = verdict["verification"]["results"][0]
                result["observed_status"] = observed_status
                result["new_occurrence_id"] = None
                result["evidence"].append({
                    "evidence_id": "ev_" + "0" * 32,
                    "kind": "test_result",
                    "description": "Commandless claimed test result.",
                    "excerpt": "tests passed",
                    "excerpt_truncated": False,
                })
                input_path = self.root / f"targeted-commandless-{observed_status}.json"
                write_json(input_path, verdict)

                targeted_binding = copy.deepcopy(self.binding)
                targeted_binding.update({
                    "task_id": verdict["subject"]["task_id"],
                    "run_id": verdict["subject"]["run_id"],
                    "attempt_epoch": verdict["subject"]["attempt"],
                })
                targeted_binding_path = self.root / f"targeted-binding-{observed_status}.json"
                write_json(targeted_binding_path, targeted_binding)

                raw_validation = projection.VALIDATOR.validate_document(
                    input_path,
                    trusted_manifest_path=manifest_path,
                    prior_findings_path=prior_path,
                )
                item_pointer = "/verification/results/0/evidence/1"
                item_errors = [
                    error for error in raw_validation["errors"]
                    if error["pointer"] == item_pointer
                    or error["pointer"].startswith(item_pointer + "/")
                ]
                self.assertEqual(
                    {
                        (error["code"], error["pointer"])
                        for error in item_errors
                    },
                    {
                        ("kind_inconsistent_evidence", item_pointer + "/command"),
                        ("weak_appears_fixed_evidence", item_pointer),
                    }
                    if observed_status == "appears_fixed"
                    else {
                        ("kind_inconsistent_evidence", item_pointer + "/command")
                    },
                )

                value, validation = projection.build_projection(
                    input_path, manifest_path, targeted_binding_path, prior_path
                )
                second_value, second_validation = projection.build_projection(
                    input_path, manifest_path, targeted_binding_path, prior_path
                )
                self.assertEqual(value, second_value)
                self.assertEqual(
                    validation["transport_normalizations"],
                    second_validation["transport_normalizations"],
                )
                self.assertEqual(value["verified_finding_ids"], [])
                operations = [item["operation"] for item in validation["transport_normalizations"]]
                self.assertEqual(
                    operations,
                    [
                        "discard_evidence_without_required_command",
                        "mark_verification_not_verifiable",
                    ],
                )

    def test_positive_claim_downgrade_does_not_erase_occurrence(self) -> None:
        verdict_path = CORE / "fixtures/valid/targeted_verification.json"
        manifest_path = CORE / "fixtures/trusted/manifest_targeted.json"
        prior_path = CORE / "fixtures/trusted/prior_findings_targeted.json"
        verdict = json.loads(verdict_path.read_text(encoding="utf-8"))
        result = verdict["verification"]["results"][0]
        result["observed_status"] = "no_longer_applicable"
        result["new_occurrence_id"] = projection.VALIDATOR.expected_occurrence_id(
            verdict["review"]["review_id"], result["finding_id"], 99
        )
        original_occurrence_id = result["new_occurrence_id"]
        result["evidence"].append({
            "evidence_id": "ev_" + "0" * 32,
            "kind": "test_result",
            "description": "Commandless claimed test result.",
            "excerpt": "tests passed",
            "excerpt_truncated": False,
        })
        input_path = self.root / "targeted-positive-occurrence.json"
        write_json(input_path, verdict)
        targeted_binding = copy.deepcopy(self.binding)
        targeted_binding.update({
            "task_id": verdict["subject"]["task_id"],
            "run_id": verdict["subject"]["run_id"],
            "attempt_epoch": verdict["subject"]["attempt"],
        })
        targeted_binding_path = self.root / "targeted-positive-occurrence-binding.json"
        write_json(targeted_binding_path, targeted_binding)
        value, validation = projection.build_projection(
            input_path, manifest_path, targeted_binding_path, prior_path
        )
        self.assertEqual(value["verified_finding_ids"], [])
        self.assertIn(
            "mark_verification_not_verifiable",
            [item["operation"] for item in validation["transport_normalizations"]],
        )
        raw_validation = projection.VALIDATOR.validate_document(
            input_path,
            trusted_manifest_path=manifest_path,
            prior_findings_path=prior_path,
        )
        normalized, _ = projection.normalize_transport_defects(
            verdict, raw_validation["errors"]
        )
        self.assertEqual(
            normalized["verification"]["results"][0]["new_occurrence_id"],
            original_occurrence_id,
        )

    def test_still_open_claim_survives_discarded_commandless_evidence(self) -> None:
        verdict_path = CORE / "fixtures/valid/targeted_verification.json"
        manifest_path = CORE / "fixtures/trusted/manifest_targeted.json"
        prior_path = CORE / "fixtures/trusted/prior_findings_targeted.json"
        verdict = json.loads(verdict_path.read_text(encoding="utf-8"))
        result = verdict["verification"]["results"][0]
        result["observed_status"] = "still_open"
        original_occurrence_id = result["new_occurrence_id"]
        result["evidence"].append({
            "evidence_id": "ev_" + "0" * 32,
            "kind": "test_result",
            "description": "Commandless claimed test result.",
            "excerpt": "tests passed",
            "excerpt_truncated": False,
        })
        input_path = self.root / "targeted-commandless-still-open.json"
        write_json(input_path, verdict)
        targeted_binding = copy.deepcopy(self.binding)
        targeted_binding.update({
            "task_id": verdict["subject"]["task_id"],
            "run_id": verdict["subject"]["run_id"],
            "attempt_epoch": verdict["subject"]["attempt"],
        })
        targeted_binding_path = self.root / "targeted-binding-still-open.json"
        write_json(targeted_binding_path, targeted_binding)

        value, validation = projection.build_projection(
            input_path, manifest_path, targeted_binding_path, prior_path
        )
        self.assertEqual(value["verified_finding_ids"], [])
        normalized, _ = self._normalize(verdict, manifest_path, prior_path)
        normalized_result = normalized["verification"]["results"][0]
        self.assertEqual(normalized_result["observed_status"], "still_open")
        self.assertEqual(normalized_result["new_occurrence_id"], original_occurrence_id)
        self.assertEqual(
            [item["operation"] for item in validation["transport_normalizations"]],
            ["discard_evidence_without_required_command"],
        )

    def test_still_open_with_only_commandless_evidence_fails_contract(self) -> None:
        verdict_path = CORE / "fixtures/valid/targeted_verification.json"
        manifest_path = CORE / "fixtures/trusted/manifest_targeted.json"
        prior_path = CORE / "fixtures/trusted/prior_findings_targeted.json"
        verdict = json.loads(verdict_path.read_text(encoding="utf-8"))
        result = verdict["verification"]["results"][0]
        result["observed_status"] = "still_open"
        result["evidence"] = [{
            "evidence_id": "ev_" + "0" * 32,
            "kind": "test_result",
            "description": "Only evidence is commandless.",
            "excerpt": "tests passed",
            "excerpt_truncated": False,
        }]
        input_path = self.root / "targeted-only-commandless-still-open.json"
        write_json(input_path, verdict)
        targeted_binding = copy.deepcopy(self.binding)
        targeted_binding.update({
            "task_id": verdict["subject"]["task_id"],
            "run_id": verdict["subject"]["run_id"],
            "attempt_epoch": verdict["subject"]["attempt"],
        })
        targeted_binding_path = self.root / "targeted-only-commandless-binding.json"
        write_json(targeted_binding_path, targeted_binding)
        with self.assertRaises(projection.ContractValidationError):
            projection.build_projection(
                input_path, manifest_path, targeted_binding_path, prior_path
            )

    def test_unknown_fingerprint_cleanup_cannot_merge_findings(self) -> None:
        verdict = copy.deepcopy(self.verdict)
        first = verdict["findings"][0]
        first["fingerprint"]["excerptless"] = True
        second = copy.deepcopy(first)
        second["fingerprint"]["excerptless"] = False
        second["finding_id"] = projection.VALIDATOR.expected_finding_id(
            second["fingerprint"]
        )
        second["occurrence_id"] = projection.VALIDATOR.expected_occurrence_id(
            verdict["review"]["review_id"], second["finding_id"], 2
        )
        for evidence in second["evidence"]:
            evidence["evidence_id"] = "ev_" + "d" * 32
        verdict["findings"].append(second)
        verdict["counts"][first["severity"]] += 1
        verdict["counts"]["total"] += 1
        verdict_path = self.root / "fingerprint-cleanup-collision.json"
        write_json(verdict_path, verdict)
        with self.assertRaises(projection.ContractValidationError) as caught:
            projection.build_projection(
                verdict_path, self.manifest_path, self.binding_path
            )
        self.assertIn(
            "duplicate_finding_id",
            {error["code"] for error in caught.exception.validation["errors"]},
        )

    def test_infra_commandless_evidence_is_discarded(self) -> None:
        verdict = copy.deepcopy(self.verdict)
        verdict["infra_symptoms"] = [{
            "symptom_code": "timeout_exceeded",
            "observed_at": verdict["review"]["completed_at"],
            "description": "Reviewer timeout observation.",
            "evidence": [
                copy.deepcopy(verdict["findings"][0]["evidence"][0]),
                {
                    "evidence_id": "ev_" + "0" * 32,
                    "kind": "build_log",
                    "description": "Commandless build log.",
                    "excerpt": "timeout",
                    "excerpt_truncated": False,
                },
            ],
        }]
        normalized, changes = self._normalize(verdict)
        self.assertEqual(len(normalized["infra_symptoms"][0]["evidence"]), 1)
        self.assertEqual(changes[0]["operation"], "discard_evidence_without_required_command")

    def test_infra_with_only_commandless_evidence_remains_contract_failure(self) -> None:
        verdict = copy.deepcopy(self.verdict)
        verdict["infra_symptoms"] = [{
            "symptom_code": "timeout_exceeded",
            "observed_at": verdict["review"]["completed_at"],
            "description": "Reviewer timeout observation.",
            "evidence": [{
                "evidence_id": "ev_" + "0" * 32,
                "kind": "build_log",
                "description": "Commandless build log.",
                "excerpt": "timeout",
                "excerpt_truncated": False,
            }],
        }]
        normalized, _ = self._normalize(verdict)
        self.assertEqual(len(normalized["infra_symptoms"][0]["evidence"]), 1)

        verdict_path = self.root / "infra-empty-evidence-after-discard.json"
        write_json(verdict_path, verdict)
        with self.assertRaises(projection.ContractValidationError):
            projection.build_projection(
                verdict_path, self.manifest_path, self.binding_path
            )

    def test_dangling_criterion_evidence_fails_closed_as_not_verifiable(self) -> None:
        verdict, manifest = self._nonblocking_final_verdict_and_manifest()
        original_notes = verdict["criteria_coverage"][0]["notes"]
        verdict["criteria_coverage"][0]["evidence_ids"] = ["ev_" + "0" * 32]
        verdict_path = self.root / "dangling-evidence.json"
        manifest_path = self.root / "dangling-evidence-manifest.json"
        write_json(verdict_path, verdict)
        write_json(manifest_path, manifest)
        with self.assertRaisesRegex(
            projection.ProjectionError, "full review has incomplete criteria coverage"
        ):
            projection.build_projection(verdict_path, manifest_path, self.binding_path)

        normalized, changes = self._normalize(verdict)
        coverage = normalized["criteria_coverage"][0]
        self.assertEqual(coverage["status"], "not_verifiable")
        self.assertEqual(coverage["verification_method"], "not_attempted")
        self.assertEqual(coverage["evidence_ids"], [])
        self.assertEqual(coverage["notes"], original_notes)
        self.assertEqual(len(changes), 2)

    def test_max_length_criterion_notes_are_preserved(self) -> None:
        verdict, _ = self._nonblocking_final_verdict_and_manifest()
        verdict["criteria_coverage"][0]["notes"] = "N" * 2000
        verdict["criteria_coverage"][0]["evidence_ids"] = ["ev_" + "0" * 32]
        normalized, _ = self._normalize(verdict)
        self.assertEqual(normalized["criteria_coverage"][0]["notes"], "N" * 2000)

    def test_unsupported_evidence_shape_remains_contract_failure(self) -> None:
        verdict = copy.deepcopy(self.verdict)
        verdict["findings"][0]["evidence"] = None
        verdict_path = self.root / "bad-evidence-shape.json"
        write_json(verdict_path, verdict)
        with self.assertRaises(projection.ContractValidationError):
            projection.build_projection(
                verdict_path, self.manifest_path, self.binding_path
            )

    def test_unsupported_collection_shapes_remain_contract_failures(self) -> None:
        cases = (
            ("findings", lambda value: value.__setitem__("findings", None)),
            ("criteria", lambda value: value.__setitem__("criteria_coverage", None)),
            ("limitations", lambda value: value.__setitem__("limitations", None)),
            ("infra", lambda value: value.__setitem__("infra_symptoms", None)),
        )
        for name, mutate in cases:
            with self.subTest(name=name):
                verdict = copy.deepcopy(self.verdict)
                mutate(verdict)
                verdict_path = self.root / f"bad-{name}-shape.json"
                write_json(verdict_path, verdict)
                with self.assertRaises(projection.ContractValidationError):
                    projection.build_projection(
                        verdict_path, self.manifest_path, self.binding_path
                    )

    def test_malformed_evidence_id_is_not_normalized_away(self) -> None:
        verdict = copy.deepcopy(self.verdict)
        verdict["criteria_coverage"][0]["evidence_ids"] = [42]
        verdict_path = self.root / "malformed-evidence-id.json"
        write_json(verdict_path, verdict)
        normalized, changes = self._normalize(verdict)
        self.assertEqual(normalized["criteria_coverage"][0]["evidence_ids"], [42])
        self.assertEqual(changes, [])
        with self.assertRaises(projection.ContractValidationError):
            projection.build_projection(
                verdict_path, self.manifest_path, self.binding_path
            )

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
