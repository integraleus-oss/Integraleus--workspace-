import unittest

from openclaw_foreground_adapter import AdapterError, run_one


class ForegroundAdapterTests(unittest.TestCase):
    def test_user_space_adapter_is_permanently_fail_closed(self):
        with self.assertRaisesRegex(AdapterError, "root-owned"):
            run_one("packet", "token")


if __name__ == "__main__":
    unittest.main()
