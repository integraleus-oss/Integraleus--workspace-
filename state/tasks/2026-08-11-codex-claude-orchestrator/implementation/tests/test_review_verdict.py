from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import validate_review_verdict as validator


INITIAL_MANIFEST = ROOT / "fixtures" / "trusted" / "manifest_initial.json"
TARGETED_MANIFEST = ROOT / "fixtures" / "trusted" / "manifest_targeted.json"
TARGETED_PRIOR = ROOT / "fixtures" / "trusted" / "prior_findings_targeted.json"


class ReviewVerdictContractTests(unittest.TestCase):
    maxDiff = None

    def _load(self, relative: str) -> dict[str, Any]:
        return json.loads((ROOT / relative).read_text(encoding="utf-8"))

    def _write(self, directory: Path, name: str, value: dict[str, Any]) -> Path:
        path = directory / name
        path.write_text(json.dumps(value, indent=2, sort_keys=True), encoding="utf-8")
        return path

    def _validate_value(
        self,
        value: dict[str, Any],
        trusted_manifest: Path = INITIAL_MANIFEST,
        prior_findings: Path | None = None,
    ) -> dict[str, Any]:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = self._write(Path(temp_dir), "document.json", value)
            return validator.validate_document(path, trusted_manifest_path=trusted_manifest, prior_findings_path=prior_findings)

    def _codes(self, result: dict[str, Any]) -> set[str]:
        return {error["code"] for error in result["errors"]}

    def test_schema_self_check_mode_is_not_document_validation(self) -> None:
        result = validator.check_schema_file(ROOT / "review-verdict.schema.json")
        self.assertTrue(result["contract_valid"], result)
        self.assertEqual("schema_self_check", result["mode"])
        self.assertIsNone(result["layers"]["semantic"])

    def test_valid_fixtures_pass_with_trusted_inputs(self) -> None:
        cases = [
            ("initial_blocker.json", INITIAL_MANIFEST, None),
            ("targeted_verification.json", TARGETED_MANIFEST, TARGETED_PRIOR),
        ]
        for name, manifest, prior in cases:
            with self.subTest(fixture=name):
                result = validator.validate_document(ROOT / "fixtures" / "valid" / name, trusted_manifest_path=manifest, prior_findings_path=prior)
                self.assertTrue(result["contract_valid"], result)
                self.assertEqual([], result["errors"])

    def test_invalid_fixtures_fail_for_expected_reason(self) -> None:
        expected_codes = {
            "acceptance_field.json": "schema_validation",
            "bad_line_order.json": "bad_line_order",
            "bad_reference.json": "bad_occurrence_reference",
            "bad_targeted_mode.json": "schema_validation",
            "bad_timestamps.json": "bad_timestamp_order",
            "count_mismatch.json": "count_mismatch",
            "duplicate_key.json": "duplicate_key",
            "fingerprint_mismatch.json": "finding_id_mismatch",
            "missing_evidence.json": "schema_validation",
            "null_criterion_omission.json": "schema_validation",
            "occurrence_mismatch.json": "occurrence_id_mismatch",
            "prior_digest_mismatch.json": "prior_digest_mismatch",
            "reviewer_infra_classification.json": "schema_validation",
            "severity_floor_bypass.json": "schema_validation",
            "trailing_json.json": "trailing_json",
        }
        targeted = {"bad_targeted_mode.json", "prior_digest_mismatch.json"}
        fixtures = {path.name: path for path in (ROOT / "fixtures" / "invalid").glob("*.json")}
        self.assertEqual(set(expected_codes), set(fixtures))
        for name, expected_code in expected_codes.items():
            with self.subTest(fixture=name, expected_code=expected_code):
                manifest = TARGETED_MANIFEST if name in targeted else INITIAL_MANIFEST
                prior = TARGETED_PRIOR if name in targeted else None
                result = validator.validate_document(fixtures[name], trusted_manifest_path=manifest, prior_findings_path=prior)
                self.assertFalse(result["contract_valid"], result)
                self.assertIn(expected_code, self._codes(result))

    def test_cli_outputs_machine_json_and_no_decision_token(self) -> None:
        fixture = ROOT / "fixtures" / "invalid" / "acceptance_field.json"
        proc = subprocess.run(
            [
                sys.executable,
                str(ROOT / "validate_review_verdict.py"),
                str(fixture),
                "--trusted-manifest",
                str(INITIAL_MANIFEST),
            ],
            cwd=ROOT,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertEqual(1, proc.returncode)
        self.assertEqual("", proc.stderr)
        output = json.loads(proc.stdout)
        self.assertFalse(output["contract_valid"])
        self.assertEqual("contract_failure", output["failure_kind"])
        for forbidden in ("ACCEPTED", "REWORK", "FAILED_INFRA", "ESCALATED"):
            self.assertNotIn(forbidden, proc.stdout)

    def test_transport_rejects_escaped_lone_surrogate_and_control_character(self) -> None:
        cases = [
            (b'{"x":"\\uD800"}', "invalid_utf8"),
            (b'{"x":"\\u0000"}', "disallowed_control_character"),
        ]
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            for data, expected_code in cases:
                path = temp_path / f"{expected_code}.json"
                path.write_bytes(data)
                result = validator.validate_document(path, trusted_manifest_path=INITIAL_MANIFEST)
                self.assertFalse(result["contract_valid"], result)
                self.assertEqual(expected_code, result["errors"][0]["code"])

    def test_transport_and_tool_failures_are_machine_readable(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            cases: list[tuple[str, Path, str, str]] = []
            missing = temp_path / "missing.json"
            cases.append(("absent_file", missing, "io_error", "tool_input_failure"))
            directory = temp_path / "dir.json"
            directory.mkdir()
            cases.append(("directory_path", directory, "io_error", "tool_input_failure"))

            deep = temp_path / "deep.json"
            deep.write_text('{"x":' + "[" * 2000 + "0" + "]" * 2000 + "}", encoding="ascii")
            cases.append(("deep_during_parse", deep, "too_deep", "contract_failure"))

            huge = temp_path / "huge.json"
            huge.write_text('{"x":' + "1" * 5000 + "}", encoding="ascii")
            cases.append(("huge_int", huge, "huge_number", "contract_failure"))

            for name, path, expected_code, expected_kind in cases:
                with self.subTest(name=name):
                    result = validator.validate_document(path, trusted_manifest_path=INITIAL_MANIFEST)
                    self.assertFalse(result["contract_valid"], result)
                    self.assertEqual(expected_code, result["errors"][0]["code"])
                    self.assertEqual(expected_kind, result["failure_kind"])

            result = validator.validate_document(ROOT / "fixtures" / "valid" / "initial_blocker.json", schema_path=temp_path / "missing_schema.json")
            self.assertFalse(result["contract_valid"], result)
            self.assertEqual("io_error", result["errors"][0]["code"])
            self.assertEqual("tool_input_failure", result["failure_kind"])

    def test_leading_whitespace_is_accepted_and_trailing_json_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            valid_data = (ROOT / "fixtures" / "valid" / "initial_blocker.json").read_bytes()
            leading = temp_path / "leading.json"
            leading.write_bytes(b"\n  " + valid_data)
            leading_result = validator.validate_document(leading, trusted_manifest_path=INITIAL_MANIFEST)
            self.assertTrue(leading_result["contract_valid"], leading_result)

            trailing = temp_path / "trailing.json"
            trailing.write_bytes(valid_data + b"\n{}")
            trailing_result = validator.validate_document(trailing, trusted_manifest_path=INITIAL_MANIFEST)
            self.assertFalse(trailing_result["contract_valid"], trailing_result)
            self.assertEqual("trailing_json", trailing_result["errors"][0]["code"])

    def test_evidence_must_be_substantive_unique_and_kind_consistent(self) -> None:
        empty_excerpt = self._load("fixtures/valid/initial_blocker.json")
        empty_excerpt["findings"][0]["evidence"][0] = {
            "evidence_id": "ev_11111111111111111111111111111111",
            "kind": "file_excerpt",
            "description": "Whitespace-only excerpt must not satisfy evidence.",
            "excerpt": "   ",
            "collected_at": "2026-08-11T09:04:00Z",
        }
        result = self._validate_value(empty_excerpt)
        self.assertFalse(result["contract_valid"], result)
        self.assertIn("empty_evidence_excerpt", self._codes(result))

        duplicate = self._load("fixtures/valid/initial_blocker.json")
        duplicate["infra_symptoms"].append(
            {
                "symptom_code": "timeout_exceeded",
                "observed_at": "2026-08-11T09:04:30Z",
                "description": "Duplicate evidence id probe.",
                "evidence": [copy.deepcopy(duplicate["findings"][0]["evidence"][0])],
            }
        )
        result = self._validate_value(duplicate)
        self.assertFalse(result["contract_valid"], result)
        self.assertIn("duplicate_evidence_id", self._codes(result))

        bad_kind = self._load("fixtures/valid/initial_blocker.json")
        bad_kind["findings"][0]["evidence"][0].pop("command")
        result = self._validate_value(bad_kind)
        self.assertFalse(result["contract_valid"], result)
        self.assertIn("kind_inconsistent_evidence", self._codes(result))

    def test_targeted_verification_requires_trusted_prior_exactly_once(self) -> None:
        targeted = ROOT / "fixtures" / "valid" / "targeted_verification.json"
        missing = validator.validate_document(targeted, trusted_manifest_path=TARGETED_MANIFEST)
        self.assertFalse(missing["contract_valid"], missing)
        self.assertIn("prior_findings_missing", self._codes(missing))

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            forged = self._load("fixtures/valid/targeted_verification.json")
            forged["verification"]["results"][0]["finding_id"] = "fnd_ffffffffffffffffffffffffffffffff"
            forged_path = self._write(temp_path, "forged.json", forged)
            forged_result = validator.validate_document(forged_path, trusted_manifest_path=TARGETED_MANIFEST, prior_findings_path=TARGETED_PRIOR)
            self.assertFalse(forged_result["contract_valid"], forged_result)
            self.assertIn("prior_findings_coverage_mismatch", self._codes(forged_result))

            partial_prior = {
                "document_type": "prior_findings",
                "schema_version": "1.0.0",
                "findings": [
                    {"finding_id": "fnd_284c8194ba9e0e62f010013bcd46aa68", "status": "open"},
                    {"finding_id": "fnd_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", "status": "open"},
                ],
            }
            partial_prior_path = self._write(temp_path, "partial_prior.json", partial_prior)
            partial_doc = self._load("fixtures/valid/targeted_verification.json")
            digest = validator._canonical_digest(partial_prior)
            partial_doc["review"]["inputs_digest"]["prior_findings_digest"] = digest
            partial_doc["verification"]["prior_findings_digest"] = digest
            partial_doc_path = self._write(temp_path, "partial_doc.json", partial_doc)
            partial_result = validator.validate_document(partial_doc_path, trusted_manifest_path=TARGETED_MANIFEST, prior_findings_path=partial_prior_path)
            self.assertFalse(partial_result["contract_valid"], partial_result)
            self.assertIn("prior_findings_coverage_mismatch", self._codes(partial_result))

            duplicate = self._load("fixtures/valid/targeted_verification.json")
            duplicate["verification"]["results"].append(copy.deepcopy(duplicate["verification"]["results"][0]))
            duplicate_path = self._write(temp_path, "duplicate_results.json", duplicate)
            duplicate_result = validator.validate_document(duplicate_path, trusted_manifest_path=TARGETED_MANIFEST, prior_findings_path=TARGETED_PRIOR)
            self.assertFalse(duplicate_result["contract_valid"], duplicate_result)
            self.assertIn("duplicate_verification_finding_id", self._codes(duplicate_result))

    def test_criteria_coverage_can_reference_verification_and_infra_evidence(self) -> None:
        targeted = self._load("fixtures/valid/targeted_verification.json")
        targeted["criteria_coverage"][0]["status"] = "satisfied"
        targeted["criteria_coverage"][0]["verification_method"] = "static_analysis"
        targeted["criteria_coverage"][0]["evidence_ids"] = ["ev_33333333333333333333333333333333"]
        targeted["criteria_coverage"][0].pop("notes", None)
        targeted_result = self._validate_value(targeted, TARGETED_MANIFEST, TARGETED_PRIOR)
        self.assertTrue(targeted_result["contract_valid"], targeted_result)

        clean = self._load("fixtures/valid/initial_blocker.json")
        clean["findings"] = []
        clean["counts"] = {"blocker": 0, "major": 0, "nit": 0, "total": 0}
        clean["criteria_coverage"][0]["status"] = "satisfied"
        clean["criteria_coverage"][0]["verification_method"] = "gate_artifact_review"
        clean["criteria_coverage"][0]["evidence_ids"] = ["ev_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"]
        clean["criteria_coverage"][0].pop("linked_occurrence_ids", None)
        clean["criteria_coverage"][0].pop("notes", None)
        clean["infra_symptoms"] = [
            {
                "symptom_code": "timeout_exceeded",
                "observed_at": "2026-08-11T09:04:30Z",
                "description": "Gate artifact evidence was reviewed without classifying failed infra.",
                "evidence": [
                    {
                        "evidence_id": "ev_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                        "kind": "gate_artifact",
                        "description": "Gate artifact summary.",
                        "artifact_ref": "artifacts/gates/summary.json",
                        "content_digest": "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                        "collected_at": "2026-08-11T09:04:30Z",
                    }
                ],
            }
        ]
        clean["conclusion"] = {"status": "no_findings", "summary": "No findings after reviewed coverage.", "unable_to_complete_reason": None}
        clean_result = self._validate_value(clean)
        self.assertTrue(clean_result["contract_valid"], clean_result)

    def test_timestamp_semantics_and_review_window_are_enforced(self) -> None:
        invalid = self._load("fixtures/valid/initial_blocker.json")
        invalid["findings"][0]["evidence"][0]["collected_at"] = "2026-13-40T25:61:61Z"
        result = self._validate_value(invalid)
        self.assertFalse(result["contract_valid"], result)
        self.assertIn("invalid_timestamp", self._codes(result))

        out_of_window = self._load("fixtures/valid/initial_blocker.json")
        out_of_window["findings"][0]["evidence"][0]["collected_at"] = "2026-08-11T08:59:59Z"
        result = self._validate_value(out_of_window)
        self.assertFalse(result["contract_valid"], result)
        self.assertIn("timestamp_out_of_review_window", self._codes(result))

        leap_second = self._load("fixtures/valid/initial_blocker.json")
        leap_second["review"]["started_at"] = "2026-08-11T09:00:60Z"
        result = self._validate_value(leap_second)
        self.assertFalse(result["contract_valid"], result)
        self.assertIn("invalid_timestamp", self._codes(result))

    def test_check_schema_with_document_is_rejected(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(ROOT / "validate_review_verdict.py"), str(ROOT / "fixtures" / "valid" / "initial_blocker.json"), "--check-schema"],
            cwd=ROOT,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertEqual(2, proc.returncode)
        output = json.loads(proc.stdout)
        self.assertEqual("schema_self_check", output["mode"])
        self.assertEqual("invalid_cli_usage", output["errors"][0]["code"])

    def test_conclusion_criteria_and_findings_must_be_consistent(self) -> None:
        empty_clean = self._load("fixtures/valid/initial_blocker.json")
        empty_clean["findings"] = []
        empty_clean["counts"] = {"blocker": 0, "major": 0, "nit": 0, "total": 0}
        empty_clean["criteria_coverage"] = []
        empty_clean["conclusion"] = {"status": "no_findings", "summary": "Nothing was found.", "unable_to_complete_reason": None}
        result = self._validate_value(empty_clean)
        self.assertFalse(result["contract_valid"], result)
        self.assertIn("empty_clean_coverage", self._codes(result))

        unreviewed_clean = self._load("fixtures/valid/initial_blocker.json")
        unreviewed_clean["findings"] = []
        unreviewed_clean["counts"] = {"blocker": 0, "major": 0, "nit": 0, "total": 0}
        unreviewed_clean["criteria_coverage"][0]["status"] = "not_reviewed"
        unreviewed_clean["criteria_coverage"][0]["verification_method"] = "not_attempted"
        unreviewed_clean["criteria_coverage"][0].pop("evidence_ids", None)
        unreviewed_clean["criteria_coverage"][0].pop("linked_occurrence_ids", None)
        unreviewed_clean["criteria_coverage"][0]["notes"] = "This criterion was not reviewed."
        unreviewed_clean["conclusion"] = {"status": "no_findings", "summary": "Nothing was found.", "unable_to_complete_reason": None}
        result = self._validate_value(unreviewed_clean)
        self.assertFalse(result["contract_valid"], result)
        self.assertIn("unreviewed_clean_coverage", self._codes(result))

        contradiction = self._load("fixtures/valid/initial_blocker.json")
        contradiction["criteria_coverage"][0]["status"] = "satisfied"
        contradiction["criteria_coverage"][0].pop("linked_occurrence_ids", None)
        result = self._validate_value(contradiction)
        self.assertFalse(result["contract_valid"], result)
        self.assertIn("criterion_finding_contradiction", self._codes(result))

    def test_trusted_manifest_bindings_are_enforced(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            manifest = self._load("fixtures/trusted/manifest_initial.json")
            manifest["subject"]["head_commit"] = "9999999999999999999999999999999999999999"
            result = validator.validate_document(
                ROOT / "fixtures" / "valid" / "initial_blocker.json",
                trusted_manifest_path=self._write(temp_path, "subject_manifest.json", manifest),
            )
            self.assertFalse(result["contract_valid"], result)
            self.assertIn("trusted_binding_mismatch", self._codes(result))

            manifest = self._load("fixtures/trusted/manifest_initial.json")
            manifest["acceptance_criteria_digest"] = "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
            result = validator.validate_document(
                ROOT / "fixtures" / "valid" / "initial_blocker.json",
                trusted_manifest_path=self._write(temp_path, "criteria_manifest.json", manifest),
            )
            self.assertFalse(result["contract_valid"], result)
            self.assertIn("trusted_binding_mismatch", self._codes(result))

            manifest = self._load("fixtures/trusted/manifest_initial.json")
            manifest["review_instructions_digest"] = "sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
            result = validator.validate_document(
                ROOT / "fixtures" / "valid" / "initial_blocker.json",
                trusted_manifest_path=self._write(temp_path, "instructions_manifest.json", manifest),
            )
            self.assertFalse(result["contract_valid"], result)
            self.assertIn("trusted_binding_mismatch", self._codes(result))

    def test_incomplete_trusted_manifest_fails_closed_with_specific_code(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            manifest = self._write(Path(temp_dir), "incomplete_manifest.json", {"document_type": "trusted_review_manifest"})
            result = validator.validate_document(ROOT / "fixtures" / "valid" / "initial_blocker.json", trusted_manifest_path=manifest)
        self.assertFalse(result["contract_valid"], result)
        self.assertEqual("tool_input_failure", result["failure_kind"])
        self.assertIn("trusted_manifest_invalid", self._codes(result))
        self.assertNotIn("schema_validation", self._codes(result))

    def test_malformed_prior_findings_outputs_one_json_object_and_exit_2(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            prior = self._write(Path(temp_dir), "bad_prior.json", {"document_type": "prior_findings", "findings": 5})
            proc = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "validate_review_verdict.py"),
                    str(ROOT / "fixtures" / "valid" / "targeted_verification.json"),
                    "--trusted-manifest",
                    str(TARGETED_MANIFEST),
                    "--prior-findings",
                    str(prior),
                ],
                cwd=ROOT,
                check=False,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        self.assertEqual(2, proc.returncode)
        self.assertEqual("", proc.stderr)
        self.assertEqual(1, len(proc.stdout.splitlines()))
        output = json.loads(proc.stdout)
        self.assertFalse(output["contract_valid"])
        self.assertEqual("tool_input_failure", output["failure_kind"])
        codes = {error["code"] for error in output["errors"]}
        self.assertIn("prior_findings_invalid", codes)
        self.assertNotIn("schema_validation", codes)

    def test_prior_findings_container_status_outputs_one_json_object_and_exit_2(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            prior = self._write(
                Path(temp_dir),
                "container_status_prior.json",
                {
                    "document_type": "prior_findings",
                    "schema_version": "1.0.0",
                    "findings": [
                        {
                            "finding_id": "fnd_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                            "status": [],
                        }
                    ],
                },
            )
            proc = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "validate_review_verdict.py"),
                    str(ROOT / "fixtures" / "valid" / "targeted_verification.json"),
                    "--trusted-manifest",
                    str(TARGETED_MANIFEST),
                    "--prior-findings",
                    str(prior),
                ],
                cwd=ROOT,
                check=False,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        self.assertEqual(2, proc.returncode)
        self.assertEqual("", proc.stderr)
        self.assertEqual(1, len(proc.stdout.splitlines()))
        output = json.loads(proc.stdout)
        self.assertFalse(output["contract_valid"])
        self.assertEqual("tool_input_failure", output["failure_kind"])
        codes = {error["code"] for error in output["errors"]}
        self.assertIn("prior_findings_invalid", codes)
        self.assertNotIn("schema_validation", codes)

    def test_detailed_prior_finding_is_admitted_as_trusted_tool_input(self) -> None:
        prior = self._load("fixtures/trusted/prior_findings_targeted.json")
        finding = self._load("fixtures/valid/targeted_verification.json")["findings"][0]
        prior["findings"] = [{**finding, "status": "open"}]
        verdict = self._load("fixtures/valid/targeted_verification.json")
        digest = validator._canonical_digest(prior)
        verdict["review"]["inputs_digest"]["prior_findings_digest"] = digest
        verdict["verification"]["prior_findings_digest"] = digest
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            result = validator.validate_document(
                self._write(temp, "verdict.json", verdict),
                trusted_manifest_path=TARGETED_MANIFEST,
                prior_findings_path=self._write(temp, "prior.json", prior),
            )
        self.assertTrue(result["contract_valid"], result)

    def test_advisory_prior_finding_may_omit_major_only_details(self) -> None:
        prior = self._load("fixtures/trusted/prior_findings_targeted.json")
        source = self._load("fixtures/valid/targeted_verification.json")["findings"][0]
        advisory = {key: value for key, value in source.items()
                    if key not in {"rationale", "evidence", "location", "location_absent_reason"}}
        advisory["severity"] = "nit"
        advisory["category"] = "test_gap"
        advisory["fingerprint"]["category"] = "test_gap"
        prior["findings"] = [{**advisory, "status": "open"}]
        errors = []
        self.assertTrue(validator._validate_prior_findings_structure(prior, errors), errors)

    def test_major_prior_finding_without_evidence_is_rejected(self) -> None:
        prior = self._load("fixtures/trusted/prior_findings_targeted.json")
        finding = self._load("fixtures/valid/targeted_verification.json")["findings"][0]
        finding.pop("evidence")
        prior["findings"] = [{**finding, "status": "open"}]
        verdict = self._load("fixtures/valid/targeted_verification.json")
        digest = validator._canonical_digest(prior)
        verdict["review"]["inputs_digest"]["prior_findings_digest"] = digest
        verdict["verification"]["prior_findings_digest"] = digest
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            result = validator.validate_document(
                self._write(temp, "verdict.json", verdict),
                trusted_manifest_path=TARGETED_MANIFEST,
                prior_findings_path=self._write(temp, "prior.json", prior),
            )
        self.assertFalse(result["contract_valid"])
        self.assertIn("prior_findings_invalid", {item["code"] for item in result["errors"]})

    def test_trusted_manifest_container_enum_outputs_one_json_object_and_exit_2(self) -> None:
        cases = [
            ("expected_review_mode", []),
            ("expected_coverage_scope", []),
        ]
        for key, value in cases:
            with self.subTest(key=key), tempfile.TemporaryDirectory() as temp_dir:
                manifest = self._load("fixtures/trusted/manifest_initial.json")
                manifest[key] = value
                manifest_path = self._write(Path(temp_dir), "container_enum_manifest.json", manifest)
                proc = subprocess.run(
                    [
                        sys.executable,
                        str(ROOT / "validate_review_verdict.py"),
                        str(ROOT / "fixtures" / "valid" / "initial_blocker.json"),
                        "--trusted-manifest",
                        str(manifest_path),
                    ],
                    cwd=ROOT,
                    check=False,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                self.assertEqual(2, proc.returncode)
                self.assertEqual("", proc.stderr)
                self.assertEqual(1, len(proc.stdout.splitlines()))
                output = json.loads(proc.stdout)
                self.assertFalse(output["contract_valid"])
                self.assertEqual("tool_input_failure", output["failure_kind"])
                codes = {error["code"] for error in output["errors"]}
                self.assertIn("trusted_manifest_invalid", codes)
                self.assertNotIn("schema_validation", codes)

    def test_expected_targeted_mode_cannot_be_bypassed_by_final_full_document(self) -> None:
        forged = self._load("fixtures/valid/targeted_verification.json")
        forged["review"]["review_mode"] = "final_full"
        forged["coverage_scope"] = "full"
        result = self._validate_value(forged, TARGETED_MANIFEST)
        self.assertFalse(result["contract_valid"], result)
        self.assertIn("prior_findings_missing", self._codes(result))
        self.assertIn("trusted_binding_mismatch", self._codes(result))
        self.assertNotIn("schema_validation", self._codes(result))

    def test_final_full_document_with_verification_validates_prior_without_false_mismatch(self) -> None:
        final_full = self._load("fixtures/valid/targeted_verification.json")
        final_full["review"]["review_mode"] = "final_full"
        final_full["coverage_scope"] = "full"
        manifest = self._load("fixtures/trusted/manifest_targeted.json")
        manifest["expected_review_mode"] = "final_full"
        manifest["expected_coverage_scope"] = "full"
        with tempfile.TemporaryDirectory() as temp_dir:
            manifest_path = self._write(Path(temp_dir), "final_manifest.json", manifest)
            result = self._validate_value(final_full, manifest_path, TARGETED_PRIOR)
        self.assertTrue(result["contract_valid"], result)
        self.assertEqual([], result["errors"])

    def test_null_criterion_requires_non_contradictory_meaningful_reason(self) -> None:
        contradictory = self._load("fixtures/valid/targeted_verification.json")
        contradictory["findings"][0]["category"] = "acceptance_criterion_violation"
        contradictory["findings"][0]["fingerprint"]["category"] = "acceptance_criterion_violation"
        contradictory["findings"][0]["finding_id"] = validator.expected_finding_id(contradictory["findings"][0]["fingerprint"])
        contradictory["findings"][0]["occurrence_id"] = validator.expected_occurrence_id(
            contradictory["review"]["review_id"],
            contradictory["findings"][0]["finding_id"],
            1,
        )
        contradictory["verification"]["results"][0]["finding_id"] = contradictory["findings"][0]["finding_id"]
        result = self._validate_value(contradictory, TARGETED_MANIFEST, TARGETED_PRIOR)
        self.assertFalse(result["contract_valid"], result)
        self.assertTrue({"schema_validation", "null_criterion_category_conflict"} & self._codes(result), result)

        trivial = self._load("fixtures/valid/targeted_verification.json")
        trivial["findings"][0]["rationale"] = "too short"
        result = self._validate_value(trivial, TARGETED_MANIFEST, TARGETED_PRIOR)
        self.assertFalse(result["contract_valid"], result)
        self.assertTrue({"schema_validation", "null_criterion_reason_too_short"} & self._codes(result), result)

    def test_location_and_supersession_rules(self) -> None:
        location_conflict = self._load("fixtures/valid/initial_blocker.json")
        location_conflict["findings"][0]["location_absent_reason"] = "cross_cutting"
        result = self._validate_value(location_conflict)
        self.assertFalse(result["contract_valid"], result)
        self.assertIn("location_conflict", self._codes(result))

        superseded = self._load("fixtures/valid/initial_blocker.json")
        superseded["findings"][0]["proposed_disposition"] = "propose_superseded"
        superseded["findings"][0]["proposal_rationale"] = "This finding is claimed to be superseded by another stable finding id."
        result = self._validate_value(superseded)
        self.assertFalse(result["contract_valid"], result)
        self.assertTrue({"schema_validation", "missing_supersession_reference"} & self._codes(result), result)


if __name__ == "__main__":
    unittest.main()
