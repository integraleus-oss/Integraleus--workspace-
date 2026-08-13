import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from io import StringIO

import production_cycle_cli
from production_cycle_cli import PacketError, load_packet, main, run_packet


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
        result = run_packet(self.packet_path)
        self.assertEqual(result["status"], "ACCEPTED")
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
        result = run_packet(self.packet_path)
        self.assertEqual(result["status"], "ACCEPTED")
        self.assertEqual(result["attempts_used"], 2)
        self.assertIn("Policy-authenticated rework:\nFix F-1", launch.call_args_list[1].args[2])
        self.assertNotIn("Make the focused change.", launch.call_args_list[1].args[2])

    @patch("production_cycle_cli.agent_launcher.launch")
    def test_codex_timeout_escalates(self, launch):
        launch.return_value = {"status": "FAILED", "timed_out": True}
        result = run_packet(self.packet_path)
        self.assertEqual(result["status"], "ESCALATED")

    @patch("production_cycle_cli.admit_live_review", side_effect=RuntimeError("bad digest"))
    @patch("production_cycle_cli.live_review_cycle.run_cycle", return_value={"status": "DECIDED"})
    @patch("production_cycle_cli.agent_launcher.launch", return_value={"status": "OK"})
    def test_admission_error_escalates(self, launch, live, admit):
        result = run_packet(self.packet_path)
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
        for status, expected in (("ACCEPTED", 0), ("FAILED_INFRA", 3), ("ESCALATED", 4)):
            with self.subTest(status=status):
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
        result = run_packet(self.packet_path)
        self.assertEqual(result["status"], "ACCEPTED")


if __name__ == "__main__":
    unittest.main()
