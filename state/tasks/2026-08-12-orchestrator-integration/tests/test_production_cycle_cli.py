import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from io import StringIO

import production_cycle_cli
from production_cycle_cli import (PacketError, _load_prior_finding_details, _requirements_acceptance,
                                  _run_loaded_packet, _targeted_closure_verified, load_packet, main, run_packet)


class ProductionCycleCliTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.safe_base = self.root / "projects"
        self.project = self.safe_base / "project"
        self.packet_dir = self.root / "packet"
        self.project.mkdir(parents=True)
        (self.project / ".git").mkdir()
        self.packet_dir.mkdir()
        (self.packet_dir / "task.md").write_text("Make the focused change.", encoding="utf-8")
        for attempt in (1, 2):
            (self.packet_dir / f"review-{attempt}.md").write_text("Return exact review JSON.", encoding="utf-8")
            inputs = self.packet_dir / f"inputs-{attempt}"
            inputs.mkdir()
            (inputs / "bundle.json").write_text("{}\n", encoding="utf-8")
        self.packet_path = self.packet_dir / "task.json"
        self.packet = {
            "document_type": "production_cycle_task", "schema_version": "1.0.0",
            "project_root": str(self.project), "task_note": "task.md",
            "run_root": str(self.root / "run"), "codex_timeout_seconds": 30,
            "claude_timeout_seconds": 30,
            "reviews": [
                {"prompt": "review-1.md", "input_dir": "inputs-1", "bundle": "bundle.json"},
                {"prompt": "review-2.md", "input_dir": "inputs-2", "bundle": "bundle.json"},
            ],
        }
        self.write_packet()
        self.safe_bases = patch.object(production_cycle_cli, "SAFE_PROJECT_BASES", (self.safe_base,))
        self.safe_bases.start()

    def tearDown(self):
        self.safe_bases.stop()
        self.temp.cleanup()

    def write_packet(self):
        self.packet_path.write_text(json.dumps(self.packet), encoding="utf-8")

    def test_valid_packet(self):
        loaded = load_packet(self.packet_path)
        self.assertEqual(loaded["project_root"], self.project)
        self.assertEqual(len(loaded["reviews"]), 2)

    def test_legacy_packet_is_not_executable_by_default(self):
        with self.assertRaisesRegex(PacketError, "validation/replay-only"):
            run_packet(self.packet_path)

    def test_v12_requires_complete_requirements_proof_chain(self):
        from requirements_traceability import canonical_digest, generate_manifest
        policy = self.packet_dir / "policy.json"
        policy.write_text("{}", encoding="utf-8")
        manifest = generate_manifest("proof-task", "Build the behavior.", ["Build the behavior."])
        manifest["requirements"][0]["state"] = "implementing"
        digest = manifest["immutable_core_digest"]
        documents = {
            "manifest.json": manifest,
            "spec.json": {"document_type": "requirements_specification", "schema_version": "1.0.0",
                          "manifest_digest": digest, "requirements": [
                              {"requirement_id": "R01", "specification": "Behavior is observable."}]},
            "tasks.json": {"document_type": "requirements_task_map", "schema_version": "1.0.0",
                           "manifest_digest": digest, "tasks": [
                               {"task_id": "implement-behavior", "requirement_ids": ["R01"]}]},
        }
        for name, value in documents.items():
            (self.packet_dir / name).write_text(json.dumps(value), encoding="utf-8")
        brief = self.packet_dir / "brief.txt"
        brief.write_text(manifest["original_brief"], encoding="utf-8")
        self.packet = {
            "document_type": "production_cycle_task", "schema_version": "1.2.0",
            "project_root": str(self.project), "task_note": "task.md", "run_root": str(self.root / "run"),
            "codex_timeout_seconds": 30, "claude_timeout_seconds": 30,
            "original_brief": "brief.txt", "original_brief_digest": manifest["original_brief_digest"],
            "previous_requirements_manifest": None,
            "requirements_manifest": "manifest.json", "requirements_specification": "spec.json",
            "requirements_task_map": "tasks.json",
            "builder": {"task_id": "task", "repo_id": "fixture", "allowed_paths": ["app.py"],
                        "gates": [{"id": "syntax", "argv": ["python3", "-c", "pass"]}],
                        "gate_timeout_seconds": 10,
                        "acceptance_criteria": [{"id": "AC-1", "statement": "Behavior works."}],
                        "review_instructions": "review-1.md", "policy_fixture": "policy.json",
                        "review_verdict": "verdict.json"},
        }
        self.write_packet()
        loaded = load_packet(self.packet_path)
        self.assertEqual(loaded["proof_chain"]["manifest"]["manifest_id"], "proof-task")
        self.assertEqual(len(loaded["reviews"]), 2)
        self.packet.update({"schema_version": "1.3.0", "control_mode": "manual", "depth": "strict",
                            "blind_acceptance": {"timeout_seconds": 30,
                                                 "verification_commands": [["python3", "-m", "unittest"]]}})
        self.packet["builder"]["acceptance_criteria"][0]["requirement_ids"] = ["R01"]
        self.write_packet()
        loaded_v13 = load_packet(self.packet_path)
        self.assertEqual(loaded_v13["blind_config"]["timeout_seconds"], 30)
        add_dir = Path(tempfile.mkdtemp(prefix="orchestrator-v14-", dir="/tmp"))
        self.addCleanup(shutil.rmtree, add_dir, ignore_errors=True)
        self.packet.update({"schema_version": "1.4.0", "codex_add_dirs": [str(add_dir)]})
        self.write_packet()
        loaded_v14 = load_packet(self.packet_path)
        self.assertEqual(len(loaded_v14["reviews"]), 2)
        self.assertEqual(loaded_v14["codex_add_dirs"], [add_dir.resolve()])
        self.packet["codex_add_dirs"] = ["/tmp"]
        self.write_packet()
        with self.assertRaisesRegex(PacketError, "bounded directories"):
            load_packet(self.packet_path)
        self.packet.update({"schema_version": "1.3.0"})
        self.packet.pop("codex_add_dirs")
        self.write_packet()
        loaded_v13["run_root"].mkdir()
        with (patch("production_cycle_cli.trusted_review_builder.capture_clean_baseline", return_value={}),
              patch("production_cycle_cli.run_managed_cycle", return_value={"status": "ACCEPTED", "history": [
                  {"outcome": "ACCEPTED", "review": {"requirements_acceptance": {
                      "document_type": "requirements_acceptance", "schema_version": "1.0.0",
                      "manifest_digest": manifest["immutable_core_digest"], "results": [
                          {"requirement_id": "R01", "outcome": "pass", "evidence": "AC-1"}]}}}] }),
              patch("production_cycle_cli.blind_acceptance.run_blind_acceptance",
                    return_value={"status": "ACCEPTED"}) as blind):
            result = _run_loaded_packet(loaded_v13)
        self.assertEqual(result["status"], "ACCEPTED")
        blind.assert_called_once()
        self.assertTrue((loaded_v13["run_root"] / "dashboard.html").is_file())
        self.assertTrue((loaded_v13["run_root"] / "dashboard-evidence.json").is_file())
        self.packet["run_root"] = str(self.root / "run-modes")
        self.packet["control_mode"] = "automatic"
        self.write_packet()
        with self.assertRaisesRegex(PacketError, "manual"):
            load_packet(self.packet_path)
        self.packet["control_mode"] = "manual"
        self.packet["depth"] = "deep"
        self.write_packet()
        with self.assertRaisesRegex(PacketError, "strict/normal"):
            load_packet(self.packet_path)
        self.packet["depth"] = "strict"
        self.write_packet()
        brief.write_text("Rewritten brief.", encoding="utf-8")
        self.packet["original_brief_digest"] = __import__("requirements_traceability").digest_text("Rewritten brief.")
        self.write_packet()
        with self.assertRaisesRegex(PacketError, "not bound"):
            load_packet(self.packet_path)
        brief.write_text(manifest["original_brief"], encoding="utf-8")
        self.packet["original_brief_digest"] = manifest["original_brief_digest"]
        self.write_packet()
        documents["tasks.json"]["tasks"] = []
        (self.packet_dir / "tasks.json").write_text(json.dumps(documents["tasks.json"]), encoding="utf-8")
        with self.assertRaisesRegex(PacketError, "proof-chain preflight"):
            load_packet(self.packet_path)

    @patch("production_cycle_cli.review_projection.normalize_derived_review_ids")
    def test_prior_finding_details_use_canonical_derived_ids(self, normalize):
        decision_dir = self.root / "decision"
        decision_dir.mkdir()
        (decision_dir / "input-review_verdict.json").write_text(
            json.dumps({"findings": [{"finding_id": "fnd_" + "1" * 32, "title": "raw"}]}),
            encoding="utf-8",
        )
        canonical_id = "fnd_" + "2" * 32
        normalize.return_value = {"findings": [{"finding_id": canonical_id, "title": "canonical"}]}
        verdict_path = decision_dir / "input-review_verdict.json"
        digest = "sha256:" + production_cycle_cli.hashlib.sha256(verdict_path.read_bytes()).hexdigest()
        details = _load_prior_finding_details(decision_dir, digest)
        self.assertEqual(details, {canonical_id: {"finding_id": canonical_id,
                                                  "title": "canonical", "status": "open"}})

    def test_prior_finding_details_reject_digest_mismatch(self):
        decision_dir = self.root / "decision"
        decision_dir.mkdir()
        (decision_dir / "input-review_verdict.json").write_text(json.dumps({"findings": []}))
        with self.assertRaises(PacketError):
            _load_prior_finding_details(decision_dir, "sha256:" + "0" * 64)

    def test_rejects_path_escape_and_existing_run(self):
        self.packet["task_note"] = "../outside.md"
        self.write_packet()
        with self.assertRaises(PacketError):
            load_packet(self.packet_path)
        self.packet["task_note"] = "task.md"
        Path(self.packet["run_root"]).mkdir()
        self.write_packet()
        with self.assertRaises(PacketError):
            load_packet(self.packet_path)

    def test_rejects_symlink_in_review_inputs(self):
        (self.packet_dir / "inputs-1" / "link").symlink_to(self.packet_dir / "task.md")
        with self.assertRaises(PacketError):
            load_packet(self.packet_path)

    def test_rejects_symlink_as_direct_packet_path(self):
        (self.packet_dir / "task-link.md").symlink_to(self.packet_dir / "task.md")
        self.packet["task_note"] = "task-link.md"
        self.write_packet()
        with self.assertRaises(PacketError):
            load_packet(self.packet_path)

    def test_rejects_empty_root_paths(self):
        self.packet["project_root"] = ""
        self.write_packet()
        with self.assertRaises(PacketError):
            load_packet(self.packet_path)

    def test_rejects_project_outside_allowlist_or_without_git_marker(self):
        self.packet["project_root"] = str(self.root)
        self.write_packet()
        with self.assertRaises(PacketError):
            load_packet(self.packet_path)
        self.packet["project_root"] = str(self.safe_base / "not-a-repo")
        (self.safe_base / "not-a-repo").mkdir()
        self.write_packet()
        with self.assertRaises(PacketError):
            load_packet(self.packet_path)

    @patch("production_cycle_cli.admit_live_review")
    @patch("production_cycle_cli.live_review_cycle.run_cycle")
    @patch("production_cycle_cli.agent_launcher.launch")
    def test_accepted_single_attempt(self, launch, live, admit):
        launch.return_value = {"status": "OK"}
        live.return_value = {"status": "DECIDED"}
        admit.return_value = {
            "document_type": "local_orchestrator_run_result", "outcome": "ACCEPTED", "rule_id": "R17_ACCEPT"
        }
        result = run_packet(self.packet_path, allow_legacy=True)
        self.assertEqual(result["status"], "ACCEPTED")
        events = [json.loads(line) for line in
                  (Path(self.packet["run_root"]) / "RUN_EVIDENCE.jsonl").read_text().splitlines()]
        self.assertEqual([item["event"] for item in events],
                         ["start", "agent_launch", "review", "terminal"])
        self.assertEqual(events[-1]["payload"]["status"], "ACCEPTED")
        self.assertEqual(result["attempts_used"], 1)
        self.assertTrue((self.root / "run" / "cycle-result.json").is_file())

    @patch("production_cycle_cli.admit_live_review")
    @patch("production_cycle_cli.live_review_cycle.run_cycle")
    @patch("production_cycle_cli.agent_launcher.launch")
    def test_one_authenticated_rework_then_accept(self, launch, live, admit):
        launch.return_value = {"status": "OK"}
        live.return_value = {"status": "DECIDED"}
        admit.side_effect = [
            {"document_type": "local_orchestrator_run_result", "outcome": "REWORK",
             "rule_id": "R11_OPEN_FINDINGS", "rework_packet": "Fix F-1"},
            {"document_type": "local_orchestrator_run_result", "outcome": "ACCEPTED", "rule_id": "R17_ACCEPT"},
        ]
        result = run_packet(self.packet_path, allow_legacy=True)
        self.assertEqual(result["status"], "ACCEPTED")
        events = [json.loads(line) for line in
                  (Path(self.packet["run_root"]) / "RUN_EVIDENCE.jsonl").read_text().splitlines()]
        self.assertEqual([item["event"] for item in events],
                         ["start", "agent_launch", "review", "agent_launch", "review", "terminal"])
        self.assertEqual(events[-1]["payload"]["status"], "ACCEPTED")
        self.assertEqual(result["attempts_used"], 2)
        self.assertIn("Policy-authenticated rework:\nFix F-1", launch.call_args_list[1].args[2])
        self.assertIn("ORIGINAL_SEALED_TASK:\nMake the focused change.", launch.call_args_list[1].args[2])

    @patch("production_cycle_cli.agent_launcher.launch")
    def test_codex_timeout_escalates(self, launch):
        launch.return_value = {"status": "FAILED", "timed_out": True}
        result = run_packet(self.packet_path, allow_legacy=True)
        self.assertEqual(result["status"], "ESCALATED")

    @patch("production_cycle_cli.agent_launcher.launch")
    def test_codex_operator_interrupt_is_preserved(self, launch):
        launch.return_value = {"status": "INTERRUPTED", "exit_code": 130, "timed_out": False}
        result = run_packet(self.packet_path, allow_legacy=True)
        implementation = result["history"][0]["implementation"]
        self.assertEqual(result["status"], "INTERRUPTED")
        self.assertNotIn("classification", implementation)
        events = [json.loads(line) for line in
                  (Path(self.packet["run_root"]) / "RUN_EVIDENCE.jsonl").read_text().splitlines()]
        self.assertEqual(events[-1]["payload"]["status"], "INTERRUPTED")
        self.assertEqual([item["event"] for item in events], ["start", "agent_launch", "terminal"])

    @patch("production_cycle_cli._run_loaded_packet", side_effect=RuntimeError("synthetic failure"))
    def test_run_packet_persists_error_terminal_event(self, run):
        with self.assertRaisesRegex(RuntimeError, "synthetic failure"):
            run_packet(self.packet_path, allow_legacy=True)
        events = [json.loads(line) for line in
                  (Path(self.packet["run_root"]) / "RUN_EVIDENCE.jsonl").read_text().splitlines()]
        self.assertEqual([item["event"] for item in events], ["start", "terminal"])
        self.assertEqual(events[-1]["payload"], {
            "status": "ERROR", "error_type": "RuntimeError", "exit_code": 2,
        })

    @patch("production_cycle_cli._run_loaded_packet", return_value={"status": "ACCEPTED"})
    def test_run_packet_rejects_existing_or_symlink_run_root_without_mutation(self, run):
        root = Path(self.packet["run_root"])
        root.mkdir()
        marker = root / "historical.json"
        marker.write_text("{}\n", encoding="utf-8")
        with self.assertRaisesRegex(Exception, "run_root must be new|run root already exists"):
            run_packet(self.packet_path, allow_legacy=True)
        self.assertEqual(list(root.iterdir()), [marker])
        shutil.rmtree(root)
        target = self.root / "target"
        target.mkdir()
        root.symlink_to(target, target_is_directory=True)
        with self.assertRaisesRegex(Exception, "run_root must be new|run root already exists"):
            run_packet(self.packet_path, allow_legacy=True)
        self.assertEqual(list(target.iterdir()), [])

    @patch("production_cycle_cli._run_loaded_packet", side_effect=KeyboardInterrupt)
    def test_terminal_evidence_failure_does_not_mask_interrupt(self, run):
        original = production_cycle_cli.run_evidence.EvidenceStream.append

        def append(stream, event, payload):
            if event == "terminal":
                raise production_cycle_cli.run_evidence.EvidenceError("disk failure")
            return original(stream, event, payload)

        with patch.object(production_cycle_cli.run_evidence.EvidenceStream, "append", new=append):
            with self.assertRaises(KeyboardInterrupt):
                run_packet(self.packet_path, allow_legacy=True)

    @patch("production_cycle_cli.admit_live_review", side_effect=RuntimeError("bad digest"))
    @patch("production_cycle_cli.live_review_cycle.run_cycle", return_value={"status": "DECIDED"})
    @patch("production_cycle_cli.agent_launcher.launch", return_value={"status": "OK"})
    def test_admission_error_escalates(self, launch, live, admit):
        result = run_packet(self.packet_path, allow_legacy=True)
        self.assertEqual(result["status"], "ESCALATED")
        self.assertEqual(result["history"][-1]["error"]["message"], "bad digest")

    def invoke_main(self, args, result=None):
        stdout = StringIO()
        patches = [patch.object(production_cycle_cli.sys, "argv", ["production_cycle_cli.py", *args]),
                   patch("sys.stdout", stdout)]
        if result is not None:
            patches.append(patch("production_cycle_cli._run_loaded_packet", return_value=result))
        for item in patches:
            item.start()
        try:
            code = main()
        finally:
            for item in reversed(patches):
                item.stop()
        return code, json.loads(stdout.getvalue())

    def test_main_exit_contract(self):
        for status, expected in (("ACCEPTED", 0), ("FAILED_INFRA", 3),
                                 ("ESCALATED", 4), ("INTERRUPTED", 130)):
            with self.subTest(status=status):
                shutil.rmtree(self.packet["run_root"], ignore_errors=True)
                code, output = self.invoke_main([str(self.packet_path)], {"status": status})
                self.assertEqual(code, expected)
                self.assertEqual(output["status"], status)

    def test_main_validate_only_and_malformed_packet(self):
        code, output = self.invoke_main([str(self.packet_path), "--validate-only"])
        self.assertEqual((code, output["status"]), (0, "VALID"))
        self.assertFalse(Path(self.packet["run_root"]).exists())
        self.packet_path.write_text("not json", encoding="utf-8")
        code, output = self.invoke_main([str(self.packet_path)])
        self.assertEqual((code, output["status"]), (2, "ERROR"))

    def test_guard_flag_requires_root_guard_parent_and_cgroup(self):
        with patch("production_cycle_cli._guard_parent_authorized", return_value=False):
            code, output = self.invoke_main([str(self.packet_path), "--guard-authorized"], {"status": "ACCEPTED"})
        self.assertEqual((code, output["status"]), (2, "ERROR"))
        self.assertIn("root-owned guard", output["error"]["message"])

    def test_guard_flag_admits_only_after_parent_check(self):
        with patch("production_cycle_cli._guard_parent_authorized", return_value=True):
            code, output = self.invoke_main([str(self.packet_path), "--guard-authorized"], {"status": "ACCEPTED"})
        self.assertEqual((code, output["status"]), (0, "ACCEPTED"))

    def test_controlled_manual_flag_admits_without_guard_parent(self):
        with patch("production_cycle_cli._guard_parent_authorized", return_value=False):
            code, output = self.invoke_main([str(self.packet_path), "--controlled-manual"],
                                            {"status": "ACCEPTED"})
        self.assertEqual((code, output["status"]), (0, "ACCEPTED"))

    def test_light_review_profile_is_forwarded(self):
        stdout = StringIO()
        with patch.object(production_cycle_cli.sys, "argv", [
                "production_cycle_cli.py", str(self.packet_path), "--controlled-manual",
                "--review-profile", "light"]), patch("sys.stdout", stdout), \
                patch("production_cycle_cli._run_loaded_packet", return_value={"status": "ACCEPTED"}) as run:
            code = main()
        self.assertEqual(code, 0)
        self.assertEqual(run.call_args.kwargs["review_profile"], "light")

    def test_targeted_closure_requires_merged_passing_coverage_and_clean_registry(self):
        packet = {"depth": "strict", "proof_chain": {"manifest": {
            "immutable_core_digest": "sha256:test", "requirements": [
                {"requirement_id": "R01", "state": "implementing"}]}},
            "builder": {"acceptance_criteria": [
                {"id": "AC-1", "statement": "works", "requirement_ids": ["R01"]}]}}
        passing = {"AC-1": {"status": "satisfied", "verification_method": "executed_test"}}
        admitted = {"rule_id": "R15_NEED_FULL_REVIEW",
                    "requirements_acceptance": _requirements_acceptance(packet, passing)}
        self.assertTrue(_targeted_closure_verified(admitted, {"findings": []}))
        failing = {"AC-1": {"status": "violated", "verification_method": "executed_test"}}
        admitted["requirements_acceptance"] = _requirements_acceptance(packet, failing)
        self.assertFalse(_targeted_closure_verified(admitted, {"findings": []}))
        admitted["requirements_acceptance"] = _requirements_acceptance(packet, passing)
        self.assertFalse(_targeted_closure_verified(admitted, {"findings": [
            {"finding_id": "F-1", "status": "open", "severity": "major"}]}))

    @patch("production_cycle_cli.admit_live_review")
    @patch("production_cycle_cli.live_review_cycle.run_cycle")
    @patch("production_cycle_cli.agent_launcher.launch")
    def test_builder_packet_observes_change_and_connects_generated_bundle(self, launch, live, admit):
        # Replace the fake Git marker with a real clean repository.
        (self.project / ".git").rmdir()
        import subprocess
        subprocess.run(["git", "init", "-q", self.project], check=True)
        subprocess.run(["git", "-C", self.project, "config", "user.email", "test@example.invalid"], check=True)
        subprocess.run(["git", "-C", self.project, "config", "user.name", "Test"], check=True)
        (self.project / "app.py").write_text("VALUE = 1\n")
        subprocess.run(["git", "-C", self.project, "add", "."], check=True)
        subprocess.run(["git", "-C", self.project, "commit", "-qm", "baseline"], check=True)
        policy = self.packet_dir / "policy.json"
        policy.write_text(json.dumps({"task_policy": {"budgets": {"rework": 1, "infra_total": 1,
            "infra_per_signature": {}, "final_full": 1, "no_progress": 1},
            "infra_signature_allowlist": []}}))
        self.packet = {
            "document_type": "production_cycle_task", "schema_version": "1.1.0",
            "project_root": str(self.project), "task_note": "task.md", "run_root": str(self.root / "run"),
            "codex_timeout_seconds": 30, "claude_timeout_seconds": 30,
            "builder": {"task_id": "task", "repo_id": "fixture", "allowed_paths": ["app.py"],
                "gates": [{"id": "syntax", "argv": ["python3", "-c",
                    "compile(open('app.py').read(), 'app.py', 'exec')"]}],
                "gate_timeout_seconds": 10,
                "acceptance_criteria": [{"id": "AC-1", "statement": "VALUE is 2."}],
                "review_instructions": "review-1.md", "policy_fixture": "policy.json",
                "review_verdict": "verdict.json"},
        }
        self.write_packet()

        def implement(*args, **kwargs):
            (self.project / "app.py").write_text("VALUE = 2\n")
            return {"status": "OK"}
        launch.side_effect = implement

        def inspect_bundle(project, prompt, bundle, live_root, timeout_seconds, pre_admission_verify=None,
                           allow_format_retry=False, allow_contract_retry=False):
            inputs = bundle.parent
            binding = json.loads((inputs / "binding.json").read_text())
            fixture = json.loads((inputs / "policy.json").read_text())
            self.assertEqual(fixture["task_policy"]["run_id"], binding["run_id"])
            self.assertEqual(fixture["execution_report"]["subject"]["tree_digest"],
                             binding["reviewed_tree_digest"])
            self.assertIn(str(inputs), prompt.read_text())
            self.assertIn((inputs / "review-instructions.md").read_text().strip(), prompt.read_text())
            self.assertIn("review-verdict.schema.json", prompt.read_text())
            self.assertIn("conclusion.unable_to_complete_reason", prompt.read_text())
            self.assertIsNotNone(pre_admission_verify)
            self.assertTrue(allow_format_retry)
            self.assertTrue(allow_contract_retry)
            pre_admission_verify()
            return {"status": "DECIDED"}
        live.side_effect = inspect_bundle
        admit.return_value = {"document_type": "local_orchestrator_run_result", "outcome": "ACCEPTED",
                              "rule_id": "R17_ACCEPT"}
        result = run_packet(self.packet_path, allow_legacy=True)
        self.assertEqual(result["status"], "ACCEPTED")
        events = [json.loads(line) for line in
                  (Path(self.packet["run_root"]) / "RUN_EVIDENCE.jsonl").read_text().splitlines()]
        self.assertEqual([item["event"] for item in events],
                         ["start", "agent_launch", "changed_paths", "gate", "review", "terminal"])
        self.assertEqual(events[2]["payload"]["paths"], ["app.py"])
        self.assertEqual(events[-1]["payload"]["status"], "ACCEPTED")

    @patch("production_cycle_cli.admit_live_review")
    @patch("production_cycle_cli.live_review_cycle.run_cycle", return_value={"status": "DECIDED"})
    @patch("production_cycle_cli.agent_launcher.launch")
    def test_repairable_builder_failure_gets_one_authenticated_repair(self, launch, live, admit):
        (self.project / ".git").rmdir()
        import subprocess
        subprocess.run(["git", "init", "-q", self.project], check=True)
        subprocess.run(["git", "-C", self.project, "config", "user.email", "test@example.invalid"], check=True)
        subprocess.run(["git", "-C", self.project, "config", "user.name", "Test"], check=True)
        (self.project / "app.py").write_text("VALUE = 1\n")
        subprocess.run(["git", "-C", self.project, "add", "."], check=True)
        subprocess.run(["git", "-C", self.project, "commit", "-qm", "baseline"], check=True)
        policy = self.packet_dir / "policy.json"
        policy.write_text(json.dumps({"task_policy": {"budgets": {"rework": 1, "infra_total": 1,
            "infra_per_signature": {}, "final_full": 1, "no_progress": 1},
            "infra_signature_allowlist": []}}))
        self.packet = {
            "document_type": "production_cycle_task", "schema_version": "1.1.0",
            "project_root": str(self.project), "task_note": "task.md", "run_root": str(self.root / "run"),
            "codex_timeout_seconds": 30, "claude_timeout_seconds": 30,
            "builder": {"task_id": "repair-test", "repo_id": "fixture", "allowed_paths": ["app.py"],
                "gates": [{"id": "value", "argv": ["python3", "-c",
                    "import pathlib,sys; sys.exit(0 if 'VALUE = 3' in pathlib.Path('app.py').read_text() else 1)"]}],
                "gate_timeout_seconds": 10,
                "acceptance_criteria": [{"id": "AC-1", "statement": "VALUE is 3."}],
                "review_instructions": "review-1.md", "policy_fixture": "policy.json",
                "review_verdict": "verdict.json"},
        }
        self.write_packet()

        def implement(role, project, prompt, run_dir, **kwargs):
            attempt = len(launch.call_args_list)
            (self.project / "app.py").write_text("VALUE = 2\n" if attempt == 1 else "VALUE = 3\n")
            return {"status": "OK"}
        launch.side_effect = implement
        admit.return_value = {"document_type": "local_orchestrator_run_result", "outcome": "ACCEPTED",
                              "rule_id": "R17_ACCEPT"}

        result = run_packet(self.packet_path, allow_legacy=True)

        self.assertEqual((result["status"], result["attempts_used"]), ("ACCEPTED", 2))
        self.assertEqual(live.call_count, 1)
        repair_prompt = launch.call_args_list[1].args[2]
        self.assertIn("Policy-authenticated rework:", repair_prompt)
        self.assertIn("ORIGINAL_SEALED_TASK:", repair_prompt)
        self.assertIn("Make the focused change.", repair_prompt)
        self.assertIn("Trusted builder gate `value` failed", repair_prompt)
        events = [json.loads(line) for line in
                  (Path(self.packet["run_root"]) / "RUN_EVIDENCE.jsonl").read_text().splitlines()]
        reviews = [item for item in events if item["event"] == "review"]
        self.assertEqual(len(reviews), 2)
        self.assertEqual(reviews[0]["payload"], {
            "attempt": 1, "outcome": "REWORK", "rule_id": "R09_GATE_FAIL",
            "source": "builder_gate",
        })
        self.assertEqual(reviews[1]["payload"]["outcome"], "ACCEPTED")


if __name__ == "__main__":
    unittest.main()
