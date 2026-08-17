import importlib.util
import io
import os
import socket
import subprocess
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

MODULE_PATH = Path(__file__).with_name("orchestrator_guard.py")
spec = importlib.util.spec_from_file_location("orchestrator_guard", MODULE_PATH)
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)


class GuardTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.root = Path(self.temp.name)
        self.packet_dir = self.root / "packet"; self.packet_dir.mkdir()
        self.packet = self.packet_dir / "packet.json"; self.packet.write_text("{}")
        (self.packet_dir / "task.md").write_text("task")
        self.patches = [patch.object(guard, "PACKET_ROOT", self.root),
                        patch.object(guard, "SNAPSHOT_ROOT", self.root / "snapshots"),
                        patch.object(guard, "USED_ROOT", self.root / "used"),
                        patch.object(guard, "AUDIT", self.root / "audit" / "audit.jsonl")]
        for item in self.patches: item.start()
        guard.SNAPSHOT_ROOT.mkdir()
        guard.prepared.clear(); self.now = int(time.time())
        self.base = {"accountId": "default", "channelId": "telegram", "chatId": guard.CHAT_ID,
                     "topicId": guard.TOPIC_ID, "messageId": "3301", "senderId": guard.OWNER_ID,
                     "timestamp": self.now}

    def tearDown(self):
        for item in reversed(self.patches): item.stop()
        self.temp.cleanup()

    def prepare_request(self):
        digest = guard._digest(self.packet)
        return {**self.base, "action": "prepare",
                "content": f"PREPARE ORCHESTRATOR PILOT {digest} packet/packet.json",
                "packetPath": str(self.packet), "packetDigest": digest}

    def test_prepare_creates_readable_immutable_snapshot_and_run_command(self):
        response = guard._prepare(self.prepare_request(), self.now)
        record = guard.prepared[response["snapshotId"]]
        self.assertEqual(record["packet"].read_text(), "{}")
        self.assertEqual((record["packet"].parent / "task.md").read_text(), "task")
        self.assertEqual(record["packet"].stat().st_mode & 0o777, 0o640)
        self.assertEqual(record["packet"].parent.stat().st_mode & 0o777, 0o750)
        self.assertEqual(response["runCommand"], f'RUN ORCHESTRATOR PILOT {response["snapshotDigest"]}')

    def test_snapshot_digest_changes_when_any_input_changes(self):
        first = guard._prepare(self.prepare_request(), self.now)["snapshotDigest"]
        self.base["messageId"] = "3302"; (self.packet_dir / "task.md").write_text("changed")
        second = guard._prepare(self.prepare_request(), self.now)["snapshotDigest"]
        self.assertNotEqual(first, second)

    def test_prepare_rejects_symlink_and_size_limit(self):
        (self.packet_dir / "link").symlink_to("/etc/passwd")
        with self.assertRaises(guard.GuardError): guard._prepare(self.prepare_request(), self.now)
        (self.packet_dir / "link").unlink(); (self.packet_dir / "large").write_bytes(b"x" * (guard.MAX_BYTES + 1))
        self.base["messageId"] = "3302"
        with self.assertRaises(guard.GuardError): guard._prepare(self.prepare_request(), self.now)

    def test_prepare_rejects_unbound_command_and_directory_fanout(self):
        request = self.prepare_request()
        with self.assertRaises(guard.GuardError):
            guard._prepare(dict(request, content="PREPARE ORCHESTRATOR PILOT"), self.now)
        self.base["messageId"] = "3302"
        for index in range(guard.MAX_ENTRIES + 1):
            (self.packet_dir / f"d{index}").mkdir()
        with self.assertRaisesRegex(guard.GuardError, "entry count"):
            guard._prepare(self.prepare_request(), self.now)

    def test_prepare_rejects_hardlinked_input(self):
        os.link(self.packet_dir / "task.md", self.packet_dir / "hardlink.md")
        with self.assertRaisesRegex(guard.GuardError, "link count"):
            guard._prepare(self.prepare_request(), self.now)

    def test_metadata_and_replay_fail_closed(self):
        for field, value in {"senderId": "1", "chatId": "-1", "topicId": "1",
                             "timestamp": self.now - 121}.items():
            with self.subTest(field=field), self.assertRaises(guard.GuardError):
                guard._prepare(dict(self.prepare_request(), **{field: value}), self.now)
        request = self.prepare_request(); guard._prepare(request, self.now)
        with self.assertRaisesRegex(guard.GuardError, "already consumed"): guard._prepare(request, self.now)

    def test_run_consumes_only_matching_prepared_snapshot(self):
        prepared = guard._prepare(self.prepare_request(), self.now)
        run = {**dict(self.base, messageId="3302"), "action": "run", "snapshotId": prepared["snapshotId"],
               "content": prepared["runCommand"]}
        with patch.object(guard, "_run_child", return_value={"status": "ACCEPTED"}) as child:
            result = guard._run_prepared(run, self.now)
        self.assertEqual(result["result"]["status"], "ACCEPTED"); child.assert_called_once()
        with self.assertRaises(guard.GuardError): guard._run_prepared(run, self.now)

    def test_framing_supports_split_stream_and_rejects_multiple_records(self):
        left, right = socket.socketpair()
        try:
            right.sendall(b'{"action":"prepare"}\n')
            self.assertEqual(guard._read_request(left)["action"], "prepare")
        finally: left.close(); right.close()

    def test_bounded_drain_caps_output(self):
        output = bytearray(); overflow = guard.threading.Event()
        guard._bounded_drain(io.BytesIO(b"x" * 1_100_000), output, overflow)
        self.assertEqual(len(output), 1_048_576)
        self.assertTrue(overflow.is_set())

    def test_wait_kills_background_process_group_before_reap(self):
        process = subprocess.Popen(["/bin/sh", "-c", "sleep 30 & exit 0"], start_new_session=True)
        code = guard._wait_without_reaping(process, 5, guard.threading.Event())
        self.assertEqual(code, 0)
        with self.assertRaises(ProcessLookupError):
            os.killpg(process.pid, 0)

    def test_expired_snapshot_is_removed(self):
        response = guard._prepare(self.prepare_request(), self.now)
        target = guard.prepared[response["snapshotId"]]["packet"].parent
        guard._purge_expired(self.now + guard.SNAPSHOT_TTL_SECONDS + 1)
        self.assertFalse(target.exists())
        self.assertNotIn(response["snapshotId"], guard.prepared)
        left, right = socket.socketpair()
        try:
            right.sendall(b'{}\n{}\n')
            with self.assertRaises(guard.GuardError): guard._read_request(left)
        finally: left.close(); right.close()


if __name__ == "__main__": unittest.main()
