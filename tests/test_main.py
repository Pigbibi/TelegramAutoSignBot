import contextlib
import io
import json
import os
import unittest
from unittest.mock import AsyncMock, mock_open, patch

from telethon.errors import FloodWaitError, UsernameInvalidError

with patch.dict(os.environ, {
    "API_ID": "1", "API_HASH": "synthetic-placeholder",
    "SESSION_STRING": "synthetic-placeholder",
}):
    import main


class MainTests(unittest.IsolatedAsyncioTestCase):
    async def run_script(self, *, send_effect=None, start_effect=None, disconnect_effect=None):
        client = AsyncMock()
        client.send_message.side_effect = send_effect
        client.start.side_effect = start_effect
        client.disconnect.side_effect = disconnect_effect
        log = mock_open()
        stdout = io.StringIO()
        with (
            patch.object(main, "TelegramClient", return_value=client),
            patch.object(main, "StringSession", return_value=object()),
            patch.object(main, "BOT_CONFIG_RAW", "@synthetic_first:/qd,@synthetic_second:/qd,@synthetic_third:/qd"),
            patch.object(main.asyncio, "sleep", new=AsyncMock()),
            patch("main.open", log, create=True),
            contextlib.redirect_stdout(stdout),
        ):
            code = await main.main()
        record = json.loads(log().write.call_args.args[0])
        self.assertNotIn("@synthetic_", stdout.getvalue())
        self.assertNotIn("SYNTHETIC_PRIVATE_DETAIL", stdout.getvalue())
        self.assertNotIn("SYNTHETIC_PRIVATE_DETAIL", json.dumps(record))
        client.disconnect.assert_awaited_once()
        return code, record, client

    async def test_target_failure_continues_and_records_partial_counts(self):
        code, record, client = await self.run_script(send_effect=[None, UsernameInvalidError(None), None])
        self.assertEqual(code, 1)
        self.assertEqual(client.send_message.await_count, 3)
        self.assertEqual(record["submitted"], 2)
        self.assertEqual(record["target_failed"], 1)
        self.assertEqual(record["not_attempted"], 0)

    async def test_global_rate_limit_stops_without_retry(self):
        code, record, client = await self.run_script(send_effect=[None, FloodWaitError(None, capture=60), None])
        self.assertEqual(code, 1)
        self.assertEqual(client.send_message.await_count, 2)
        self.assertEqual(record["submitted"], 1)
        self.assertEqual(record["global_failed"], 1)
        self.assertEqual(record["not_attempted"], 1)

    async def test_unknown_send_stops_and_never_logs_exception(self):
        code, record, client = await self.run_script(send_effect=[None, RuntimeError("SYNTHETIC_PRIVATE_DETAIL"), None])
        self.assertEqual(code, 1)
        self.assertEqual(client.send_message.await_count, 2)
        self.assertEqual(record["send_unconfirmed"], 1)
        self.assertEqual(record["not_attempted"], 1)

    async def test_start_failure_still_disconnects_and_records_unattempted(self):
        code, record, client = await self.run_script(start_effect=RuntimeError("SYNTHETIC_PRIVATE_DETAIL"))
        self.assertEqual(code, 1)
        client.send_message.assert_not_awaited()
        self.assertEqual(record["attempted"], 0)
        self.assertEqual(record["not_attempted"], 3)
        self.assertTrue(record["stopped"])

    async def test_disconnect_failure_keeps_submission_counts_and_fails(self):
        code, record, _ = await self.run_script(disconnect_effect=RuntimeError("SYNTHETIC_PRIVATE_DETAIL"))
        self.assertEqual(code, 1)
        self.assertEqual(record["submitted"], 3)
        self.assertTrue(record["disconnect_failed"])

    async def test_all_submissions_return_zero_without_claiming_checkin(self):
        code, record, _ = await self.run_script()
        self.assertEqual(code, 0)
        self.assertEqual(record["attempted"], 3)
        self.assertEqual(record["submitted"], 3)
        self.assertEqual(record["kind"], "command_submission")
