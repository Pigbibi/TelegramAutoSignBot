import unittest
from unittest.mock import AsyncMock, patch

from telethon.errors import FloodWaitError, UsernameInvalidError

import checkin

CREDENTIALS = checkin.Credentials(
    api_id=1, api_hash="synthetic-placeholder", session_string="synthetic-placeholder"
)
TARGETS = [
    ("@synthetic_first", "/qd"),
    ("@synthetic_second", "/qd"),
    ("@synthetic_third", "/qd"),
]


class ParseTargetsTest(unittest.TestCase):
    def test_omitted_command_defaults_to_qd(self):
        self.assertEqual(checkin.parse_targets("@bot"), [("@bot", "/qd")])

    def test_configured_command_is_sent_verbatim(self):
        self.assertEqual(checkin.parse_targets("@bot:sign"), [("@bot", "sign")])

    def test_entry_splits_on_the_first_colon_only(self):
        self.assertEqual(checkin.parse_targets("@bot:/a:b"), [("@bot", "/a:b")])

    def test_surrounding_whitespace_is_ignored(self):
        self.assertEqual(
            checkin.parse_targets("  @a : /qd ,  @b  "), [("@a", "/qd"), ("@b", "/qd")]
        )

    def test_empty_entries_target_nothing(self):
        self.assertEqual(checkin.parse_targets(""), [])
        self.assertEqual(checkin.parse_targets(" , ,"), [])

    def test_entry_without_a_username_is_dropped(self):
        self.assertEqual(checkin.parse_targets(":/qd"), [])


class RunTest(unittest.IsolatedAsyncioTestCase):
    async def run_batch(self, *, send_effect=None, start_effect=None, disconnect_effect=None):
        client = AsyncMock()
        client.send_message.side_effect = send_effect
        client.start.side_effect = start_effect
        client.disconnect.side_effect = disconnect_effect
        report = checkin.Report(len(TARGETS))
        with (
            patch.object(checkin, "TelegramClient", return_value=client),
            patch.object(checkin, "StringSession", return_value=object()),
        ):
            await checkin.run(TARGETS, report, CREDENTIALS, sleep=AsyncMock())
        return report, client

    async def test_target_failure_continues_with_the_remaining_targets(self):
        report, client = await self.run_batch(
            send_effect=[None, UsernameInvalidError(None), None]
        )
        self.assertEqual(client.send_message.await_count, 3)
        self.assertEqual(report.submitted, 2)
        self.assertEqual(report.target_failed, 1)
        self.assertEqual(report.attempted, 3)
        self.assertTrue(report.failed)

    async def test_global_failure_stops_without_retrying_the_rest(self):
        report, client = await self.run_batch(
            send_effect=[None, FloodWaitError(None, capture=60), None]
        )
        self.assertEqual(client.send_message.await_count, 2)
        self.assertEqual(report.submitted, 1)
        self.assertEqual(report.global_failed, 1)
        self.assertTrue(report.stopped)
        self.assertEqual(report.to_dict()["not_attempted"], 1)

    async def test_unknown_send_failure_stops_and_keeps_details_out_of_the_log(self):
        report, client = await self.run_batch(
            send_effect=[None, RuntimeError("SYNTHETIC_PRIVATE_DETAIL"), None]
        )
        self.assertEqual(client.send_message.await_count, 2)
        self.assertEqual(report.send_unconfirmed, 1)
        self.assertTrue(report.stopped)
        self.assertNotIn("SYNTHETIC_PRIVATE_DETAIL", report.to_line())

    async def test_start_failure_disconnects_and_leaves_every_target_unattempted(self):
        report, client = await self.run_batch(start_effect=RuntimeError("SYNTHETIC_PRIVATE_DETAIL"))
        client.send_message.assert_not_awaited()
        client.disconnect.assert_awaited_once()
        self.assertEqual(report.attempted, 0)
        self.assertEqual(report.to_dict()["not_attempted"], 3)
        self.assertEqual(report.global_failed, 1)
        self.assertTrue(report.stopped)

    async def test_disconnect_failure_keeps_the_submission_counts_and_fails(self):
        report, _ = await self.run_batch(disconnect_effect=RuntimeError("SYNTHETIC_PRIVATE_DETAIL"))
        self.assertEqual(report.submitted, 3)
        self.assertTrue(report.disconnect_failed)
        self.assertTrue(report.failed)

    async def test_successful_batch_submits_every_target(self):
        report, _ = await self.run_batch()
        self.assertEqual(report.attempted, 3)
        self.assertEqual(report.submitted, 3)
        self.assertFalse(report.failed)

    async def test_record_keeps_the_log_schema(self):
        report, _ = await self.run_batch()
        self.assertEqual(
            set(report.to_dict()),
            {
                "kind", "time", "targets", "attempted", "submitted", "target_failed",
                "global_failed", "send_unconfirmed", "stopped", "disconnect_failed",
                "not_attempted",
            },
        )
        self.assertEqual(report.to_dict()["kind"], "command_submission")

    async def test_credentials_never_reach_the_record(self):
        report, _ = await self.run_batch()
        self.assertNotIn("@synthetic_", report.to_line())
        self.assertNotIn("synthetic-placeholder", report.to_line())
