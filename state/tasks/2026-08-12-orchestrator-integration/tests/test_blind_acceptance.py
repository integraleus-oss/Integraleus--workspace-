import copy
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import blind_acceptance
from blind_acceptance import BlindAcceptanceError, build_prompt, compare_acceptance, run_blind_acceptance
from requirements_traceability import generate_manifest


class BlindAcceptanceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.project = self.root / "project"
        self.project.mkdir()
        subprocess.run(["git", "init", "-q", self.project], check=True)
        subprocess.run(["git", "-C", self.project, "config", "user.email", "test@example.invalid"], check=True)
        subprocess.run(["git", "-C", self.project, "config", "user.name", "Test"], check=True)
        (self.project / "app.txt").write_text("baseline\n")
        subprocess.run(["git", "-C", self.project, "add", "."], check=True)
        subprocess.run(["git", "-C", self.project, "commit", "-qm", "baseline"], check=True)
        self.manifest = generate_manifest("blind-proof", "Build A.\nDo not change B.",
                                          ["Build A.", "Do not change B."])
        self.internal = {"document_type": "requirements_acceptance", "schema_version": "1.0.0",
                         "manifest_digest": self.manifest["immutable_core_digest"], "results": [
                             {"requirement_id": "R01", "outcome": "pass", "evidence": "internal test"},
                             {"requirement_id": "R02", "outcome": "pass", "evidence": "internal digest"}]}

    def tearDown(self):
        self.temp.cleanup()

    def test_prompt_excludes_internal_material_and_keeps_exact_brief(self):
        prompt = build_prompt(self.manifest, [["python3", "-m", "unittest"]])
        self.assertIn(self.manifest["original_brief"], prompt)
        self.assertIn("R01: Build A.", prompt)
        self.assertNotIn("internal test", prompt)
        self.assertNotIn("specification", prompt.lower().replace("internal specifications", ""))

    def test_disagreement_or_unverified_blocks_acceptance(self):
        blind = copy.deepcopy(self.internal)
        blind["results"][1]["outcome"] = "fail"
        with self.assertRaisesRegex(BlindAcceptanceError, "disagreement"):
            compare_acceptance(self.manifest, self.internal, blind)
        both = copy.deepcopy(self.internal)
        both["results"][0]["outcome"] = "unable_to_verify"
        with self.assertRaisesRegex(BlindAcceptanceError, "did not pass"):
            compare_acceptance(self.manifest, both, both)

    @patch("blind_acceptance.agent_launcher.extract_claude_verdict")
    @patch("blind_acceptance.agent_launcher.launch")
    def test_successful_run_is_read_only_and_digest_bound(self, launch, extract):
        launch.return_value = {"status": "OK"}
        def fake_extract(run_dir, path):
            path.write_text(json.dumps({}) + "\n")
            return {"document_type": "blind_acceptance_verdict", "schema_version": "1.0.0",
                    "manifest_digest": self.manifest["immutable_core_digest"], "results": self.internal["results"]}
        extract.side_effect = fake_extract
        run = self.root / "run"

        def fake_launch(role, project, prompt, launch_dir, **kwargs):
            launch_dir.mkdir(parents=True)
            (launch_dir / "input-prompt.md").write_text(prompt)
            return {"status": "OK"}
        launch.side_effect = fake_launch
        result = run_blind_acceptance(self.project, run, self.manifest, self.internal,
                                      [["python3", "-c", "pass"]], 30)
        self.assertEqual(result["status"], "ACCEPTED")
        self.assertFalse(launch.call_args.kwargs["codex_write"])


if __name__ == "__main__":
    unittest.main()
