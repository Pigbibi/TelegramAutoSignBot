import contextlib
import io
import json
import os
import tempfile
import unittest
from unittest.mock import patch

import main

ENVIRONMENT = {
    "API_ID": "1",
    "API_HASH": "synthetic-placeholder",
    "SESSION_STRING": "synthetic-placeholder",
    "BOT_CONFIG": "@synthetic_first,@synthetic_second",
}


class MainTest(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.workdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.workdir.cleanup)
        previous = os.getcwd()
        os.chdir(self.workdir.name)
        self.addCleanup(os.chdir, previous)

    async def run_main(self, outcome=None):
        seen = {}

        async def fake_run(targets, report, credentials):
            seen["targets"] = targets
            for field, value in (outcome or {}).items():
                setattr(report, field, value)

        stdout = io.StringIO()
        with (
            patch.dict(os.environ, ENVIRONMENT),
            patch.object(main, "run", fake_run),
            contextlib.redirect_stdout(stdout),
        ):
            code = await main.main()
        return code, stdout.getvalue(), seen

    def logged_records(self):
        with open("checkin.log", encoding="utf-8") as log:
            return [json.loads(line) for line in log if line.strip()]

    async def test_successful_run_exits_zero_and_appends_one_record(self):
        code, stdout, seen = await self.run_main()
        self.assertEqual(code, 0)
        self.assertEqual(
            seen["targets"], [("@synthetic_first", "/qd"), ("@synthetic_second", "/qd")]
        )
        records = self.logged_records()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["kind"], "command_submission")
        self.assertEqual(records[0]["targets"], 2)
        self.assertEqual(records[0]["not_attempted"], 2)
        self.assertEqual(stdout, json.dumps(records[0], sort_keys=True) + "\n")

    async def test_each_run_appends_instead_of_replacing_the_log(self):
        await self.run_main()
        await self.run_main()
        self.assertEqual(len(self.logged_records()), 2)

    async def test_target_failure_exits_nonzero(self):
        code, _, _ = await self.run_main({"target_failed": 1})
        self.assertEqual(code, 1)

    async def test_any_counted_failure_exits_nonzero_even_without_the_stop_flag(self):
        for field in ("global_failed", "send_unconfirmed", "disconnect_failed", "stopped"):
            with self.subTest(field=field):
                code, _, _ = await self.run_main({field: 1})
                self.assertEqual(code, 1)

    async def test_unsaved_record_exits_nonzero(self):
        os.mkdir(main.LOG_PATH)
        code, stdout, _ = await self.run_main()
        self.assertEqual(code, 1)
        self.assertIn("Error: submission summary could not be saved.", stdout)

    async def test_missing_credentials_fail_before_anything_is_logged(self):
        with patch.dict(os.environ, {}, clear=True), contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaises(KeyError):
                await main.main()
        self.assertFalse(os.path.exists(main.LOG_PATH))

    async def test_target_names_never_reach_stdout(self):
        _, stdout, _ = await self.run_main()
        self.assertNotIn("@synthetic_", stdout)
