"""One check-in batch: what to send, what happened, and what it means."""

import asyncio
import enum
import json
import random
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone

from telethon import TelegramClient
from telethon.errors import (
    ChatWriteForbiddenError,
    InputUserDeactivatedError,
    PeerIdInvalidError,
    RPCError,
    UserIsBlockedError,
    UsernameInvalidError,
    UsernameNotOccupiedError,
)
from telethon.sessions import StringSession

DEFAULT_COMMAND = "/qd"

# Telethon raises a plain ValueError when a username resolves to no entity.
TARGET_ERRORS = (
    ValueError, UsernameInvalidError, UsernameNotOccupiedError,
    ChatWriteForbiddenError, InputUserDeactivatedError, PeerIdInvalidError,
    UserIsBlockedError,
)

# The delays break up the pattern Telegram's anti-spam heuristics look for.
# They do not make automation permitted.
STARTUP_DELAY_SECONDS = (60, 300)
SEND_DELAY_SECONDS = (2, 5)

# Log timestamps use UTC+8 while the runner clock is UTC, so a run scheduled at
# 00:00 UTC is dated with the maintainers' local day.
LOG_TIMEZONE = timezone(timedelta(hours=8))


def parse_targets(raw: str) -> list[tuple[str, str]]:
    """Split `bot_username[:command],...` into (bot, command) pairs.

    Commands are sent exactly as written; an omitted command means DEFAULT_COMMAND.
    """
    targets: list[tuple[str, str]] = []
    for entry in raw.split(","):
        bot, _, command = entry.strip().partition(":")
        bot = bot.strip()
        if not bot:
            continue
        targets.append((bot, command.strip() or DEFAULT_COMMAND))
    return targets


class Outcome(enum.Enum):
    """What one send attempt means for the rest of the batch."""

    SUBMITTED = enum.auto()
    TARGET_FAILED = enum.auto()
    # Rate limits, account errors and other global RPC failures make every
    # remaining send pointless.
    GLOBAL_FAILED = enum.auto()
    # The message may already have reached Telegram, so resending could repeat it.
    UNCONFIRMED = enum.auto()


def classify(error: Exception) -> Outcome:
    if isinstance(error, TARGET_ERRORS):
        return Outcome.TARGET_FAILED
    if isinstance(error, RPCError):
        return Outcome.GLOBAL_FAILED
    return Outcome.UNCONFIRMED


@dataclass
class Report:
    """The counters of one batch. This is the whole log record."""

    targets: int
    attempted: int = 0
    submitted: int = 0
    target_failed: int = 0
    global_failed: int = 0
    send_unconfirmed: int = 0
    stopped: bool = False
    disconnect_failed: bool = False

    @property
    def failed(self) -> bool:
        return bool(
            self.target_failed
            or self.global_failed
            or self.send_unconfirmed
            or self.stopped
            or self.disconnect_failed
        )

    def record(self, outcome: Outcome) -> bool:
        """Count one outcome; returns whether the batch must stop."""
        if outcome is Outcome.SUBMITTED:
            self.submitted += 1
            return False
        if outcome is Outcome.TARGET_FAILED:
            self.target_failed += 1
            return False
        self.stopped = True
        if outcome is Outcome.GLOBAL_FAILED:
            self.global_failed += 1
        else:
            self.send_unconfirmed += 1
        return True

    def to_dict(self) -> dict:
        record = asdict(self)
        record["kind"] = "command_submission"
        record["not_attempted"] = self.targets - self.attempted
        record["time"] = datetime.now(LOG_TIMEZONE).isoformat()
        return record

    def to_line(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True) + "\n"


@dataclass(frozen=True)
class Credentials:
    api_id: int
    api_hash: str
    session_string: str


async def run(
    targets: list[tuple[str, str]], report: Report, credentials: Credentials, *, sleep=asyncio.sleep
) -> None:
    """Send every target, stopping the batch when continuing would be unsafe."""
    client = None
    try:
        await sleep(random.randint(*STARTUP_DELAY_SECONDS))
        client = TelegramClient(
            StringSession(credentials.session_string), credentials.api_id, credentials.api_hash
        )
        await client.start()
        for bot_username, command in targets:
            report.attempted += 1
            try:
                await client.send_message(bot_username, command)
            except asyncio.CancelledError:
                report.record(Outcome.UNCONFIRMED)
                raise
            except Exception as error:
                if report.record(classify(error)):
                    break
            else:
                report.record(Outcome.SUBMITTED)
            await sleep(random.randint(*SEND_DELAY_SECONDS))
    except asyncio.CancelledError:
        report.stopped = True
        raise
    except Exception:
        report.record(Outcome.GLOBAL_FAILED)
    finally:
        if client is not None:
            try:
                await client.disconnect()
            except Exception:
                report.disconnect_failed = True
