import json
import hashlib
import subprocess
import tempfile
import unittest
from pathlib import Path

from trusted_review_builder import BuilderError, build_review_inputs, capture_clean_baseline, verify_seal
import local_orchestrator_runner
import review_projection
from requirements_traceability import generate_manifest


class TrustedReviewBuilderTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        subprocess.run(["git", "init", "-q", self.repo], check=True)
        subprocess.run(["git", "-C", self.repo, "config", "user.email", "test@example.invalid"], check=True)
        subprocess.run(["git", "-C", self.repo, "config", "user.name", "Test"], check=True)
        (self.repo / "src").mkdir()
        (self.repo / "src/app.py").write_text("print('old')\n")
        subprocess.run(["git", "-C", self.repo, "add", "."], check=True)
        subprocess.run(["git", "-C", self.repo, "commit", "-qm", "baseline"], check=True)
        self.instructions = self.root / "review.md"
        self.instructions.write_text("Review all changed paths.\n")
        self.policy = self.root / "policy.json"
        self.policy.write_text(json.dumps({"task_policy": {
            "budgets": {"rework": 1, "infra_total": 1, "infra_per_signature": {},
                        "final_full": 1, "no_progress": 1},
            "infra_signature_allowlist": []}}) + "\n")
        self.config = {
            "task_id": "builder-test", "repo_id": "fixture", "allowed_paths": ["src"],
            "gates": [{"id": "syntax", "argv": ["python3", "-c",
                "compile(open('src/app.py').read(), 'src/app.py', 'exec')"]}],
            "gate_timeout_seconds": 10,
            "acceptance_criteria": [{"id": "AC-1", "statement": "The focused change is correct."}],
            "review_instructions": str(self.instructions), "policy_fixture": str(self.policy),
            "review_verdict": "verdict.json",
        }
        self.baseline = capture_clean_baseline(self.repo)

    def tearDown(self):
        self.temp.cleanup()

    def build(self):
        (self.repo / "src/app.py").write_text("print('new')\n")
        return build_review_inputs(self.repo, self.root / "inputs", self.baseline, self.config, 1)

    def acceptance_digest(self):
        return "sha256:" + hashlib.sha256(
            b"AC-1\0The focused change is correct."
        ).hexdigest()

    def test_builds_observed_digest_bound_inputs(self):
        built = self.build()
        verify_seal(built["input_dir"], self.repo)
        evidence = json.loads((built["input_dir"] / "evidence.json").read_text())
        binding = json.loads((built["input_dir"] / "binding.json").read_text())
        self.assertEqual(evidence["changed_paths"], ["src/app.py"])
        self.assertEqual(binding["covered_paths"], ["src/app.py"])
        self.assertEqual(evidence["gates"][0]["exit_code"], 0)
        criteria = json.loads((built["input_dir"] / "acceptance-criteria.json").read_text())
        self.assertEqual(criteria["criteria"][0]["statement"], "The focused change is correct.")
        self.assertEqual(evidence["artifacts"]["acceptance_criteria"],
                         "sha256:" + hashlib.sha256(
                             (built["input_dir"] / "acceptance-criteria.json").read_bytes()).hexdigest())
        schema = built["input_dir"] / "review-verdict.schema.json"
        self.assertEqual(json.loads(schema.read_text())["properties"]["document_type"]["const"],
                         "review_verdict")
        self.assertEqual(evidence["artifacts"]["review_verdict_schema"],
                         "sha256:" + hashlib.sha256(schema.read_bytes()).hexdigest())
        context = json.loads((built["input_dir"] / "review-context.json").read_text())
        self.assertEqual(context["review_verdict_schema_digest"],
                         "sha256:" + hashlib.sha256(schema.read_bytes()).hexdigest())
        self.assertIsNone(context["prior_findings_canonical_digest"])
        self.assertEqual((built["input_dir"] / "manifest.json").stat().st_mode & 0o777, 0o444)

    def test_rework_rejects_changed_acceptance_criteria(self):
        (self.repo / "src/app.py").write_text("print('new')\n")
        first = build_review_inputs(self.repo, self.root / "first", self.baseline, self.config, 1)
        binding = json.loads((first["input_dir"] / "binding.json").read_text())
        context = {
            "frozen_acceptance_criteria_digest": binding["spec_digest"],
            "finding_registry": {"document_type": "finding_registry", "schema_version": "1.0.0",
                                 "findings": [{"finding_id": "F-1", "status": "open"}]},
            "prior_finding_details": {"F-1": {"finding_id": "F-1", "severity": "major",
                                                  "title": "Defect", "description": "Fix it",
                                                  "fingerprint": {"path": "src/app.py", "line_start": 1,
                                                                  "line_end": 1, "symbol": None,
                                                                  "excerpt_hash": None}}},
        }
        changed = dict(self.config)
        changed["acceptance_criteria"] = [{"id": "AC-1", "statement": "Expanded scope."}]
        with self.assertRaisesRegex(BuilderError, "acceptance criteria changed"):
            build_review_inputs(self.repo, self.root / "second", self.baseline, changed, 2, context)

    def test_builder_repair_failure_artifacts_are_sealed_into_next_review(self):
        (self.repo / "src/app.py").write_text("print('new')\n")
        source = self.root / "prior-gate"
        source.mkdir()
        (source / "stdout.log").write_text("assertion failed\n")
        (source / "stderr.log").write_text("")
        record = {"gate_id": "syntax", "argv": ["python3", "-c", "pass"], "exit_code": 1,
                  "timed_out": False, "duration_ms": 1,
                  "stdout_digest": "sha256:" + hashlib.sha256((source / "stdout.log").read_bytes()).hexdigest(),
                  "stderr_digest": "sha256:" + hashlib.sha256((source / "stderr.log").read_bytes()).hexdigest()}
        (source / "result.json").write_text(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n")
        context = {"builder_repair": True,
                   "frozen_acceptance_criteria_digest": self.acceptance_digest(),
                   "builder_failure": {"classification": "IMPLEMENTATION_FAILURE",
                                       "record": record, "source_dir": str(source)},
                   "budgets_after": {"rework_used": 1, "infra_total_used": 0,
                                     "infra_used_by_signature": {}, "final_full_used": 0,
                                     "no_progress_streak": 0}}
        built = build_review_inputs(self.repo, self.root / "repair-inputs", self.baseline,
                                    self.config, 2, context, force_initial_review=True)
        verify_seal(built["input_dir"], self.repo)
        evidence = json.loads((built["input_dir"] / "evidence.json").read_text())
        self.assertEqual(evidence["prior_builder_failure"]["record"]["exit_code"], 1)
        self.assertEqual((built["input_dir"] / "prior-builder-failure/stdout.log").read_text(),
                         "assertion failed\n")

    def test_proof_chain_is_sealed_and_tampering_is_detected(self):
        manifest = generate_manifest("builder-proof", "Build it.", ["Build it."])
        manifest["requirements"][0]["state"] = "implementing"
        digest = manifest["immutable_core_digest"]
        proof = {
            "manifest": manifest,
            "specification": {"document_type": "requirements_specification", "schema_version": "1.0.0",
                              "manifest_digest": digest, "requirements": [
                                  {"requirement_id": "R01", "specification": "It is built."}]},
            "task_map": {"document_type": "requirements_task_map", "schema_version": "1.0.0",
                         "manifest_digest": digest, "tasks": [
                             {"task_id": "build-it", "requirement_ids": ["R01"]}]},
        }
        (self.repo / "src/app.py").write_text("print('new')\n")
        built = build_review_inputs(self.repo, self.root / "proof-inputs", self.baseline, self.config, 1,
                                    proof_chain=proof)
        verify_seal(built["input_dir"], self.repo)
        evidence = json.loads((built["input_dir"] / "evidence.json").read_text())
        self.assertEqual(evidence["requirements_manifest_digest"], digest)
        target = built["input_dir"] / "requirements-manifest.json"
        target.chmod(0o644)
        target.write_text("{}\n")
        with self.assertRaisesRegex(BuilderError, "digest mismatch"):
            verify_seal(built["input_dir"])

    def test_rejects_dirty_baseline(self):
        (self.repo / "src/app.py").write_text("dirty\n")
        with self.assertRaisesRegex(BuilderError, "baseline is not clean"):
            capture_clean_baseline(self.repo)

    def test_rejects_out_of_scope_change(self):
        (self.repo / "outside.txt").write_text("no\n")
        with self.assertRaisesRegex(BuilderError, "outside allowed scope"):
            build_review_inputs(self.repo, self.root / "inputs", self.baseline, self.config, 1)

    def test_untracked_directory_is_resolved_to_individual_allowed_file(self):
        exact = dict(self.config)
        exact["allowed_paths"] = ["docs/evidence/report.md"]
        (self.repo / "docs/evidence").mkdir(parents=True)
        (self.repo / "docs/evidence/report.md").write_text("proof\n")
        exact["gates"] = [{"id": "content", "argv": ["python3", "-c",
            "from pathlib import Path; assert Path('docs/evidence/report.md').read_text() == 'proof\\n'"]}]
        built = build_review_inputs(self.repo, self.root / "exact-untracked", self.baseline, exact, 1)
        paths = json.loads((built["input_dir"] / "changed-paths.json").read_text())
        self.assertEqual(paths, ["docs/evidence/report.md"])

    def test_rejects_failed_or_unallowlisted_gate(self):
        (self.repo / "src/app.py").write_text("not python !!!\n")
        with self.assertRaisesRegex(BuilderError, "required gate failed"):
            build_review_inputs(self.repo, self.root / "failed", self.baseline, self.config, 1)
        config = dict(self.config)
        config["gates"] = [{"id": "bad", "argv": ["curl", "https://example.invalid"]}]
        with self.assertRaisesRegex(BuilderError, "not allowlisted"):
            build_review_inputs(self.repo, self.root / "bad-program", self.baseline, config, 1)

    def test_optional_expected_test_count_accepts_matching_tap_summary(self):
        (self.repo / "src/app.py").write_text("print('new')\n")
        config = dict(self.config)
        config["gates"] = [{
            "id": "tests",
            "argv": ["python3", "-c", "print('# tests 2')"],
            "expected_test_count": 2,
        }]
        built = build_review_inputs(self.repo, self.root / "matching-count", self.baseline, config, 1)
        result = json.loads((built["input_dir"] / "gates/tests/result.json").read_text())
        self.assertEqual(result["expected_test_count"], 2)
        self.assertEqual(result["observed_test_count"], 2)

    def test_optional_expected_test_count_fails_on_mismatch_or_missing_summary(self):
        (self.repo / "src/app.py").write_text("print('new')\n")
        for name, output in (("mismatch", "# tests 1"), ("missing", "all good"),
                             ("ambiguous", "# tests 2\n# tests 2")):
            config = dict(self.config)
            config["gates"] = [{
                "id": "tests",
                "argv": ["python3", "-c", f"print({output!r})"],
                "expected_test_count": 2,
            }]
            with self.assertRaisesRegex(BuilderError, "test count"):
                build_review_inputs(self.repo, self.root / name, self.baseline, config, 1)

    def test_optional_expected_test_count_rejects_invalid_values(self):
        (self.repo / "src/app.py").write_text("print('new')\n")
        for index, value in enumerate((None, 0, -1, True, "2")):
            config = dict(self.config)
            config["gates"] = [{
                "id": "tests",
                "argv": ["python3", "-c", "print('# tests 2')"],
                "expected_test_count": value,
            }]
            with self.assertRaisesRegex(BuilderError, "expected test count"):
                build_review_inputs(self.repo, self.root / f"invalid-{index}", self.baseline, config, 1)

    def test_gate_without_expected_count_preserves_record_shape(self):
        built = self.build()
        result = json.loads((built["input_dir"] / "gates/syntax/result.json").read_text())
        self.assertNotIn("expected_test_count", result)
        self.assertNotIn("observed_test_count", result)

    def test_rejects_empty_or_duplicate_gates(self):
        (self.repo / "src/app.py").write_text("print('new')\n")
        for gates, message in (([], "at least one"),
                               ([self.config["gates"][0], self.config["gates"][0]], "unique")):
            config = dict(self.config)
            config["gates"] = gates
            with self.assertRaisesRegex(BuilderError, message):
                build_review_inputs(self.repo, self.root / ("empty-gates" if not gates else "duplicate-gates"),
                                    self.baseline, config, 1)

    def test_rejects_ignored_change_and_gate_mutation(self):
        (self.repo / ".gitignore").write_text("*.cache\n")
        subprocess.run(["git", "-C", self.repo, "add", ".gitignore"], check=True)
        subprocess.run(["git", "-C", self.repo, "commit", "-qm", "ignore rule"], check=True)
        baseline = capture_clean_baseline(self.repo)
        (self.repo / "src/app.py").write_text("print('new')\n")
        (self.repo / "hidden.cache").write_text("hidden\n")
        with self.assertRaisesRegex(BuilderError, "ignored files changed"):
            build_review_inputs(self.repo, self.root / "ignored", baseline, self.config, 1)
        (self.repo / "hidden.cache").unlink()
        config = dict(self.config)
        config["gates"] = [{"id": "mutate", "argv": ["bash", "-c", "printf mutation >> src/app.py"]}]
        with self.assertRaisesRegex(BuilderError, "mutated the reviewed subject"):
            build_review_inputs(self.repo, self.root / "mutated", baseline, config, 1)

    def test_detects_tampering(self):
        built = self.build()
        path = built["input_dir"] / "evidence.json"
        path.chmod(0o644)
        path.write_text("{}\n")
        with self.assertRaisesRegex(BuilderError, "digest mismatch"):
            verify_seal(built["input_dir"])

    def test_detects_review_schema_tampering(self):
        built = self.build()
        schema = built["input_dir"] / "review-verdict.schema.json"
        schema.chmod(0o644)
        schema.write_text("{}\n")
        with self.assertRaisesRegex(BuilderError, "digest mismatch"):
            verify_seal(built["input_dir"])

    def test_external_seal_anchor_rejects_rewritten_root_of_trust(self):
        built = self.build()
        anchored = "sha256:" + __import__("hashlib").sha256(built["seal"].read_bytes()).hexdigest()
        seal = built["seal"]
        seal.chmod(0o644)
        value = json.loads(seal.read_text())
        value["manifest.json"] = "sha256:" + "0" * 64
        seal.write_text(json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n")
        with self.assertRaisesRegex(BuilderError, "seal root digest mismatch"):
            verify_seal(built["input_dir"], expected_seal_digest=anchored)

    def test_detects_gate_log_or_reviewed_tree_tampering(self):
        built = self.build()
        log = built["input_dir"] / "gates/syntax/stdout.log"
        log.chmod(0o644)
        log.write_text("tampered\n")
        with self.assertRaisesRegex(BuilderError, "gate evidence digest mismatch"):
            verify_seal(built["input_dir"])
        log.write_bytes(b"")
        (self.repo / "src/app.py").write_text("print('mutated again')\n")
        with self.assertRaisesRegex(BuilderError, "reviewed tree changed"):
            verify_seal(built["input_dir"], self.repo)

    def test_rejects_head_change_and_empty_change(self):
        with self.assertRaisesRegex(BuilderError, "no observable change"):
            build_review_inputs(self.repo, self.root / "empty", self.baseline, self.config, 1)
        (self.repo / "src/app.py").write_text("print('committed')\n")
        subprocess.run(["git", "-C", self.repo, "add", "."], check=True)
        subprocess.run(["git", "-C", self.repo, "commit", "-qm", "changed head"], check=True)
        with self.assertRaisesRegex(BuilderError, "HEAD changed"):
            build_review_inputs(self.repo, self.root / "head", self.baseline, self.config, 1)

    def test_initial_builder_bundle_never_impersonates_removed_third_review(self):
        (self.repo / "src/app.py").write_text("print('new')\n")
        built = build_review_inputs(self.repo, self.root / "accepted-inputs", self.baseline, self.config, 1)
        inputs = built["input_dir"]
        manifest = json.loads((inputs / "manifest.json").read_text())
        fixture_path = (Path(__file__).parents[2] / "2026-08-12-orchestrator-one-cycle/live-provenance-trial/"
                        "closure-inputs/expected-accepted-verdict.json")
        verdict = json.loads(fixture_path.read_text())
        verdict["subject"] = manifest["subject"]
        verdict["review"]["review_mode"] = manifest["expected_review_mode"]
        verdict["review"]["inputs_digest"]["acceptance_criteria_digest"] = manifest["acceptance_criteria_digest"]
        verdict["review"]["inputs_digest"]["review_instructions_digest"] = manifest["review_instructions_digest"]
        finding = verdict["findings"][0]
        finding["fingerprint"]["normalized_path"] = "src/app.py"
        finding["location"]["path"] = "src/app.py"
        finding["finding_id"] = review_projection.VALIDATOR.expected_finding_id(finding["fingerprint"])
        finding["occurrence_id"] = review_projection.VALIDATOR.expected_occurrence_id(
            verdict["review"]["review_id"], finding["finding_id"], 1)
        verdict["criteria_coverage"] = [{"criterion_id": item["criterion_id"],
            "statement_digest": item["statement_digest"], "status": "satisfied",
            "verification_method": "manual_execution", "evidence_ids": ["ev_11111111111111111111111111111111"],
            "linked_occurrence_ids": [finding["occurrence_id"]], "notes": "Verified."}
            for item in manifest["criteria"]]
        verdict_path = inputs / "verdict.json"
        verdict_path.write_text(json.dumps(verdict, sort_keys=True, separators=(",", ":")) + "\n")
        validation = review_projection.VALIDATOR.validate_document(
            verdict_path, trusted_manifest_path=inputs / "manifest.json")
        self.assertTrue(validation["contract_valid"], validation)
        run_dir, result = local_orchestrator_runner.run(built["bundle"], self.root / "policy-runs")
        self.assertEqual((result["outcome"], result["rule_id"]),
                         ("REWORK", "R15_NEED_FULL_REVIEW"))
        self.assertTrue((run_dir / "registry-after.json").is_file())

    def test_projection_canonicalizes_only_derived_review_ids(self):
        fixture_path = (Path(__file__).parents[2] / "2026-08-12-orchestrator-one-cycle/live-provenance-trial/"
                        "closure-inputs/expected-accepted-verdict.json")
        verdict = json.loads(fixture_path.read_text())
        original_title = verdict["findings"][0]["title"]
        verdict["findings"][0]["finding_id"] = "fnd_" + "a" * 32
        verdict["findings"][0]["occurrence_id"] = "occ_" + "b" * 32
        verdict["criteria_coverage"][0]["linked_occurrence_ids"] = ["occ_" + "b" * 32]
        normalized = review_projection.normalize_derived_review_ids(verdict)
        finding = normalized["findings"][0]
        self.assertEqual(finding["finding_id"],
                         review_projection.VALIDATOR.expected_finding_id(finding["fingerprint"]))
        self.assertNotEqual(finding["occurrence_id"], "occ_" + "b" * 32)
        self.assertEqual(normalized["criteria_coverage"][0]["linked_occurrence_ids"],
                         [finding["occurrence_id"]])
        self.assertEqual(finding["title"], original_title)

    def test_attempt_two_carries_schema_valid_decision_and_targets_prior_findings(self):
        (self.repo / "src/app.py").write_text("print('new')\n")
        finding_id = "fnd_" + "1" * 32
        prior_detail = {"occurrence_id": "occ_" + "2" * 32,
            "finding_id": finding_id, "status": "open", "title": "Valid path is untested",
            "severity": "major", "category": "test_gap", "criterion_id": "AC-1",
            "confidence": "high", "proposed_disposition": "none",
            "location": {"path": "src/app.py", "start_line": 1, "end_line": 1,
                "symbol": "main", "diff_side": "head"},
            "rationale": "The acceptance path lacks a deterministic assertion.",
            "failure_scenario": "A regression can pass the suite.",
            "suggested_remediation": "Add an acceptance-path test.",
            "evidence": [{"evidence_id": "ev_" + "1" * 32, "kind": "file_excerpt",
                "description": "Observed test gap.", "excerpt": "no acceptance assertion",
                "excerpt_truncated": False}],
            "reproduction": [{"index": 1, "action": "Run the acceptance path.",
                "expected": "The path is asserted.", "observed": "No assertion exists.",
                "command": None, "evidence_ids": ["ev_" + "1" * 32]}], "tags": ["test-gap"],
            "fingerprint": {"fingerprint_version": 1, "category": "test_gap",
                "criterion_id": "AC-1", "normalized_path": "src/app.py",
                "normalized_symbol": "main", "normalized_title": "valid path is untested"}}
        context = {"frozen_acceptance_criteria_digest": self.acceptance_digest(),
            "budgets_after": {"rework_used": 1, "infra_total_used": 0,
            "infra_used_by_signature": {}, "final_full_used": 0, "no_progress_streak": 0},
            "seen_nonces": ["run_builder-test.attempt-1-nonce"],
            "finding_registry": {"document_type": "finding_registry", "schema_version": "1.0.0",
                "findings": [{"finding_id": finding_id, "status": "open", "effective_severity": "major",
                    "occurrence_count": 1, "resolved_at": None, "history": []}]},
            "prior_finding_details": {finding_id: prior_detail},
            "prior_attempts": [], "last_decision": {"progress_identity": "sha256:" + "2" * 64,
                "decision_digest": "sha256:" + "3" * 64, "outcome": "REWORK",
                "rule_id": "R11_OPEN_FINDINGS"}}
        incomplete = json.loads(json.dumps(context))
        incomplete["prior_finding_details"][finding_id].pop("fingerprint")
        with self.assertRaisesRegex(BuilderError, "details are incomplete"):
            build_review_inputs(self.repo, self.root / "attempt-2-incomplete", self.baseline,
                                self.config, 2, incomplete)
        built = build_review_inputs(self.repo, self.root / "attempt-2", self.baseline, self.config, 2, context)
        inputs = built["input_dir"]
        policy = json.loads((inputs / "policy.json").read_text())
        manifest = json.loads((inputs / "manifest.json").read_text())
        bundle = json.loads((inputs / "bundle.json").read_text())
        self.assertEqual(manifest["expected_review_mode"], "targeted_verification")
        self.assertEqual(manifest["expected_coverage_scope"], "targeted")
        self.assertEqual(policy["ledger"]["prior_attempts"][0]["decision_digest"], "sha256:" + "3" * 64)
        self.assertEqual(bundle["prior_findings"], "prior-findings.json")
        self.assertEqual(json.loads((inputs / "prior-findings.json").read_text())["findings"],
                         [prior_detail])
        context = json.loads((inputs / "review-context.json").read_text())
        expected = hashlib.sha256(json.dumps(
            json.loads((inputs / "prior-findings.json").read_text()), sort_keys=True,
            separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
        self.assertEqual(context["prior_findings_canonical_digest"], "sha256:" + expected)

    def test_attempt_three_is_rejected_without_creating_evidence(self):
        (self.repo / "src/app.py").write_text("print('new')\n")
        output = self.root / "attempt-3"
        with self.assertRaisesRegex(BuilderError, "attempt must be 1 or 2"):
            build_review_inputs(self.repo, output, self.baseline, self.config, 3, {})
        self.assertFalse(output.exists())

    def test_attempt_two_requires_frozen_acceptance_digest(self):
        (self.repo / "src/app.py").write_text("print('new')\n")
        with self.assertRaisesRegex(BuilderError, "lacks frozen acceptance"):
            build_review_inputs(self.repo, self.root / "attempt-2-missing-freeze",
                                self.baseline, self.config, 2, {})


if __name__ == "__main__":
    unittest.main()
