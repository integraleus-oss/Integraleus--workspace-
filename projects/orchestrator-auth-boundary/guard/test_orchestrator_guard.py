import importlib.util
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

MODULE_PATH = Path(__file__).with_name("orchestrator_guard.py")
spec = importlib.util.spec_from_file_location("orchestrator_guard", MODULE_PATH)
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)


class GuardValidationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.packet = self.root / "packet.json"
        self.packet.write_text("{}")
        self.root_patch = patch.object(guard, "PACKET_ROOT", self.root)
        self.root_patch.start()
        self.now = int(time.time())
        self.request = {
            "action": "run_one", "accountId": "default", "channelId": "telegram",
            "chatId": guard.CHAT_ID, "topicId": guard.TOPIC_ID, "messageId": "3301",
            "senderId": guard.OWNER_ID, "timestamp": self.now,
            "packetPath": str(self.packet), "packetDigest": guard._digest(self.packet),
        }
        self.request["content"] = f'RUN ORCHESTRATOR PILOT {self.request["packetDigest"]}'

    def tearDown(self):
        self.root_patch.stop()
        self.temp.cleanup()

    def test_accepts_exact_fresh_owner_request(self):
        self.assertEqual(guard._validate(self.request, self.now), self.packet.resolve())

    def test_rejects_wrong_owner_chat_topic_digest_and_expiry(self):
        cases = {
            "senderId": "1", "chatId": "-1001", "topicId": "1",
            "packetDigest": "sha256:" + "0" * 64, "timestamp": self.now - 121,
        }
        for field, value in cases.items():
            request = dict(self.request, **{field: value})
            with self.subTest(field=field), self.assertRaises(guard.GuardError):
                guard._validate(request, self.now)

    def test_rejects_command_not_bound_to_digest(self):
        with self.assertRaises(guard.GuardError):
            guard._validate(dict(self.request, content="Разрешаю"), self.now)

    def test_rejects_symlink_and_outside_packet(self):
        link = self.root / "link.json"
        link.symlink_to(self.packet)
        request = dict(self.request, packetPath=str(link))
        with self.assertRaises(guard.GuardError):
            guard._validate(request, self.now)
        outside = self.root.parent / "outside-guard.json"
        outside.write_text("{}")
        try:
            request = dict(self.request, packetPath=str(outside), packetDigest=guard._digest(outside))
            with self.assertRaises(guard.GuardError):
                guard._validate(request, self.now)
        finally:
            outside.unlink()

    def test_rejects_extra_fields(self):
        with self.assertRaises(guard.GuardError):
            guard._validate(dict(self.request, injected=True), self.now)


if __name__ == "__main__":
    unittest.main()
