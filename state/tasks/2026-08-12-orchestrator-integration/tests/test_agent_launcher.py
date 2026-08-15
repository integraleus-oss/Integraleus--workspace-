from __future__ import annotations

import json
import os
import signal
import stat
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import patch

import agent_launcher
from agent_launcher import LaunchError, extract_claude_verdict, launch


class AgentLauncherTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.project = self.root / "project"
        self.project.mkdir()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def wrapper(self, body: str) -> Path:
        path = self.root / "wrapper"
        path.write_text("#!/bin/sh\nset -eu\n" + body, encoding="utf-8")
        path.chmod(path.stat().st_mode | stat.S_IXUSR)
        return path

    def test_codex_uses_fixed_argv_and_persists_evidence(self) -> None:
        wrapper = self.wrapper('printf "%s\\n" "$@"\n')
        run_dir = self.root / "run"
        with patch.object(agent_launcher, "CODEX_WRAPPER", wrapper):
            result = launch("codex", self.project, "hello; touch /tmp/no", run_dir)
        self.assertEqual(result["status"], "OK")
        lines = (run_dir / "stdout.log").read_text().splitlines()
        self.assertEqual(lines[:5], ["--cd", str(self.project), "--read-only", "--", "hello; touch /tmp/no"])
        self.assertTrue((run_dir / "launch-result.json").is_file())
        self.assertEqual(stat.S_IMODE((run_dir / "input-prompt.md").stat().st_mode), 0o444)

    def test_nonzero_fails_closed_but_keeps_logs(self) -> None:
        wrapper = self.wrapper('echo bad >&2\nexit 7\n')
        with patch.object(agent_launcher, "CODEX_WRAPPER", wrapper):
            result = launch("codex", self.project, "hello", self.root / "run")
        self.assertEqual((result["status"], result["exit_code"]), ("FAILED", 7))
        self.assertEqual((self.root / "run/stderr.log").read_text().strip(), "bad")

    def test_rejects_reuse_and_invalid_timeout(self) -> None:
        wrapper = self.wrapper("exit 0\n")
        run_dir = self.root / "run"
        with patch.object(agent_launcher, "CODEX_WRAPPER", wrapper):
            launch("codex", self.project, "hello", run_dir)
            with self.assertRaises(LaunchError):
                launch("codex", self.project, "hello", run_dir)
            with self.assertRaises(LaunchError):
                launch("codex", self.project, "hello", self.root / "other", timeout_seconds=0)

    def test_rejects_unknown_role_and_missing_project(self) -> None:
        with self.assertRaises(LaunchError):
            launch("other", self.project, "hello", self.root / "role-run")
        with self.assertRaises(LaunchError):
            launch("codex", self.root / "missing", "hello", self.root / "project-run")

    def test_timeout_kills_wrapper_process_group(self) -> None:
        marker = self.root / "late-marker"
        wrapper = self.wrapper(f'(sleep 3; touch "{marker}") &\nwait\n')
        started = time.monotonic()
        with patch.object(agent_launcher, "CODEX_WRAPPER", wrapper):
            result = launch("codex", self.project, "hello", self.root / "run", timeout_seconds=1)
        self.assertLess(time.monotonic() - started, 4)
        self.assertEqual((result["status"], result["timed_out"]), ("FAILED", True))
        time.sleep(3)
        self.assertFalse(marker.exists())

    def test_operator_interrupt_kills_wrapper_and_persists_structured_result(self) -> None:
        marker = self.root / "late-marker"
        wrapper = self.wrapper(f'(sleep 3; touch "{marker}") &\nwait\n')
        timer = threading.Timer(0.2, lambda: os.kill(os.getpid(), signal.SIGINT))
        timer.start()
        try:
            with patch.object(agent_launcher, "CODEX_WRAPPER", wrapper):
                result = launch("codex", self.project, "hello", self.root / "run", timeout_seconds=5)
        finally:
            timer.cancel()
        self.assertEqual((result["status"], result["exit_code"]), ("INTERRUPTED", 130))
        self.assertFalse(result["timed_out"])
        self.assertEqual(json.loads((self.root / "run/launch-result.json").read_text()), result)
        time.sleep(3)
        self.assertFalse(marker.exists())

    def test_repeated_operator_interrupt_does_not_break_teardown_evidence(self) -> None:
        marker = self.root / "late-marker"
        wrapper = self.wrapper(f'(sleep 3; touch "{marker}") &\nwait\n')
        first = threading.Timer(0.2, lambda: os.kill(os.getpid(), signal.SIGINT))
        observed_handlers = []

        def interrupt_during_teardown(process):
            observed_handlers.append(signal.getsignal(signal.SIGINT))
            os.kill(os.getpid(), signal.SIGINT)
            os.killpg(process.pid, signal.SIGKILL)
            return process.communicate(timeout=2)

        first.start()
        try:
            with patch.object(agent_launcher, "CODEX_WRAPPER", wrapper), \
                    patch.object(agent_launcher, "_terminate_process_group", side_effect=interrupt_during_teardown):
                result = launch("codex", self.project, "hello", self.root / "run", timeout_seconds=5)
        finally:
            first.cancel()
        self.assertEqual((result["status"], result["exit_code"]), ("INTERRUPTED", 130))
        self.assertEqual(observed_handlers, [signal.SIG_IGN])
        self.assertNotEqual(signal.getsignal(signal.SIGINT), signal.SIG_IGN)
        self.assertEqual(json.loads((self.root / "run/launch-result.json").read_text()), result)
        time.sleep(3)
        self.assertFalse(marker.exists())

    def test_extracts_exact_json_from_claude_envelope(self) -> None:
        run_dir = self.root / "claude"
        run_dir.mkdir()
        expected = {"document_type": "review_verdict", "schema_version": "1.0.0"}
        (run_dir / "wrapper-output.json").write_text(json.dumps({"result": json.dumps(expected)}))
        output = self.root / "verdict.json"
        self.assertEqual(extract_claude_verdict(run_dir, output), expected)
        self.assertEqual(json.loads(output.read_text()), expected)

    def test_rejects_prose_claude_result(self) -> None:
        run_dir = self.root / "claude"
        run_dir.mkdir()
        (run_dir / "wrapper-output.json").write_text(json.dumps({"result": "not json"}))
        with self.assertRaises(LaunchError):
            extract_claude_verdict(run_dir, self.root / "verdict.json")

    def test_rejects_error_or_missing_result_envelope(self) -> None:
        for value in ({"is_error": True, "result": "{}"}, {"error": "bad"}):
            run_dir = self.root / ("case-" + str(len(list(self.root.glob("case-*")))))
            run_dir.mkdir()
            (run_dir / "wrapper-output.json").write_text(json.dumps(value))
            with self.assertRaises(LaunchError):
                extract_claude_verdict(run_dir, self.root / "verdict.json")

    def test_rejects_missing_wrapper_output(self) -> None:
        run_dir = self.root / "missing-output"
        run_dir.mkdir()
        with self.assertRaises(LaunchError):
            extract_claude_verdict(run_dir, self.root / "verdict.json")

    def test_claude_argv_contract(self) -> None:
        wrapper = self.wrapper('printf "%s\\n" "$@"\n')
        with patch.object(agent_launcher, "CLAUDE_WRAPPER", wrapper):
            launch("claude", self.project, "review", self.root / "run", timeout_seconds=7)
        lines = (self.root / "run/stdout.log").read_text().splitlines()
        self.assertEqual(lines[0], str(self.project))
        self.assertEqual(lines[1], str(self.root / "run/input-prompt.md"))
        self.assertEqual(lines[2], str(self.root / "run/wrapper-output.json"))
        self.assertEqual(lines[3], "7")

    def test_relative_run_dir_survives_wrapper_chdir(self) -> None:
        wrapper = self.wrapper('cd "$1"\nprintf "ok" > "$3"\n')
        relative = Path(self.root.name) / "relative-run"
        previous = Path.cwd()
        self.addCleanup(os.chdir, previous)
        os.chdir(self.root.parent)
        with patch.object(agent_launcher, "CLAUDE_WRAPPER", wrapper):
            result = launch("claude", self.project, "review", relative)
        self.assertEqual(result["status"], "OK")
        self.assertTrue((self.root / "relative-run/wrapper-output.json").is_file())


if __name__ == "__main__":
    unittest.main()
