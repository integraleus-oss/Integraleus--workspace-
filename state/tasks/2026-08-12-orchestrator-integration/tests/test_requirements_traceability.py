import copy
import unittest

from requirements_traceability import (
    TraceabilityError, canonical_digest, generate_manifest, validate_acceptance_completeness,
    validate_manifest, validate_preflight, validate_transition,
)


class RequirementsTraceabilityTests(unittest.TestCase):
    def setUp(self):
        self.manifest = generate_manifest("pilot-proof", "Build A and preserve B.", ["Build A.", "Preserve B."])
        self.manifest["requirements"][0]["state"] = "implementing"
        self.manifest["requirements"][1]["state"] = "implemented"
        digest = self.manifest["immutable_core_digest"]
        self.spec = {"document_type": "requirements_specification", "schema_version": "1.0.0",
                     "manifest_digest": digest, "requirements": [
                         {"requirement_id": "R01", "specification": "A has observable behavior."},
                         {"requirement_id": "R02", "specification": "B remains byte-identical."},
                     ]}
        self.tasks = {"document_type": "requirements_task_map", "schema_version": "1.0.0",
                      "manifest_digest": digest, "tasks": [
                          {"task_id": "task-a", "requirement_ids": ["R01"]},
                          {"task_id": "task-b", "requirement_ids": ["R02"]},
                      ]}
        self.acceptance = {"document_type": "requirements_acceptance", "schema_version": "1.0.0",
                           "manifest_digest": digest, "results": [
                               {"requirement_id": "R01", "outcome": "pass", "evidence": "test A"},
                               {"requirement_id": "R02", "outcome": "pass", "evidence": "digest B"},
                           ]}

    def test_positive_full_chain(self):
        validate_preflight(self.manifest, self.spec, self.tasks)
        validate_acceptance_completeness(self.manifest, self.acceptance)

    def test_generator_retains_exact_brief_and_stable_ids(self):
        self.assertEqual(self.manifest["original_brief"], "Build A and preserve B.")
        self.assertEqual([item["requirement_id"] for item in self.manifest["requirements"]], ["R01", "R02"])
        validate_manifest(self.manifest)

    def test_tampered_brief_or_requirement_fails(self):
        for path in ("brief", "requirement"):
            broken = copy.deepcopy(self.manifest)
            if path == "brief":
                broken["original_brief"] += " changed"
            else:
                broken["requirements"][0]["original_text"] += " changed"
            with self.subTest(path=path), self.assertRaises(TraceabilityError):
                validate_manifest(broken)

    def test_non_contiguous_ids_fail(self):
        broken = copy.deepcopy(self.manifest)
        broken["requirements"][1]["requirement_id"] = "R03"
        with self.assertRaises(TraceabilityError):
            validate_manifest(broken)

    def test_revision_chain_blocks_removal_and_state_regression(self):
        previous = copy.deepcopy(self.manifest)
        current = copy.deepcopy(previous)
        current["revision"] = 2
        current["previous_manifest_digest"] = canonical_digest(previous)
        current["requirements"][0]["state"] = "implemented"
        validate_transition(previous, current)
        removed = copy.deepcopy(current)
        removed["requirements"].pop()
        with self.assertRaises(TraceabilityError):
            validate_transition(previous, removed)
        regressed = copy.deepcopy(current)
        regressed["requirements"][1]["state"] = "accepted"
        with self.assertRaisesRegex(TraceabilityError, "regression"):
            validate_transition(previous, regressed)

    def test_ids_do_not_support_renumbering_boundary(self):
        manifest = generate_manifest("max-proof", "Many requirements.", [f"Requirement {i}" for i in range(99)])
        self.assertEqual(manifest["requirements"][-1]["requirement_id"], "R99")
        with self.assertRaises(TraceabilityError):
            generate_manifest("too-many", "Too many.", [str(i) for i in range(100)])

    def test_user_disposition_is_mandatory_and_explicit(self):
        broken = copy.deepcopy(self.manifest)
        broken["requirements"][0]["state"] = "removed_by_user"
        with self.assertRaises(TraceabilityError):
            validate_manifest(broken)
        broken["requirements"][0]["owner_disposition"] = {"decision_id": "D-1", "reason": "Owner removed it."}
        validate_manifest(broken)

    def test_missing_spec_or_reverse_task_link_fails(self):
        broken_spec = copy.deepcopy(self.spec)
        broken_spec["requirements"].pop()
        with self.assertRaisesRegex(TraceabilityError, "lack specification"):
            validate_preflight(self.manifest, broken_spec, self.tasks)
        broken_tasks = copy.deepcopy(self.tasks)
        broken_tasks["tasks"][0]["requirement_ids"] = []
        with self.assertRaisesRegex(TraceabilityError, "task traceability"):
            validate_preflight(self.manifest, self.spec, broken_tasks)

    def test_implementing_requirement_requires_task(self):
        broken = copy.deepcopy(self.tasks)
        broken["tasks"] = [broken["tasks"][0]]
        with self.assertRaisesRegex(TraceabilityError, "lack tasks"):
            validate_preflight(self.manifest, self.spec, broken)

    def test_every_active_requirement_requires_task(self):
        manifest = generate_manifest("accepted-proof", "Do it.", ["Do it."])
        digest = manifest["immutable_core_digest"]
        spec = {"document_type": "requirements_specification", "schema_version": "1.0.0",
                "manifest_digest": digest, "requirements": [{"requirement_id": "R01", "specification": "Done."}]}
        tasks = {"document_type": "requirements_task_map", "schema_version": "1.0.0",
                 "manifest_digest": digest, "tasks": []}
        with self.assertRaisesRegex(TraceabilityError, "lack tasks"):
            validate_preflight(manifest, spec, tasks)

    def test_acceptance_must_cover_every_active_requirement(self):
        broken = copy.deepcopy(self.acceptance)
        broken["results"].pop()
        with self.assertRaisesRegex(TraceabilityError, "lack acceptance"):
            validate_acceptance_completeness(self.manifest, broken)

    def test_active_requirement_cannot_be_reported_removed(self):
        broken = copy.deepcopy(self.acceptance)
        broken["results"][0]["outcome"] = "removed"
        with self.assertRaisesRegex(TraceabilityError, "incompatible"):
            validate_acceptance_completeness(self.manifest, broken)


if __name__ == "__main__":
    unittest.main()
