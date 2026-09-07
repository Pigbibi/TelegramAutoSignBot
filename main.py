import os
import asyncio
import random
import json
from datetime import datetime, timezone, timedelta
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import (
    ChatWriteForbiddenError,
    InputUserDeactivatedError,
    PeerIdInvalidError,
    RPCError,
    UserIsBlockedError,
    UsernameInvalidError,
    UsernameNotOccupiedError,
)

# Load credentials and bot configuration from environment
API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
SESSION_STRING = os.environ["SESSION_STRING"]
# Combined mapping of bot usernames and commands, e.g. "@bot1:/qd,@bot2:sign,@bot3"
BOT_CONFIG_RAW = os.environ.get("BOT_CONFIG", "").strip()
TARGET_ERRORS = (
    ValueError, UsernameInvalidError, UsernameNotOccupiedError,
    ChatWriteForbiddenError, InputUserDeactivatedError, PeerIdInvalidError,
    UserIsBlockedError,
)


def _resolve_command(cmd: str) -> str:
    """Use the configured command as-is, defaulting to '/qd' when omitted."""
    cmd = (cmd or "").strip()
    if not cmd:
        return "/qd"
    return cmd


def get_bot_command_list() -> list[tuple[str, str]]:
    """
    Build (bot_username, command) pairs from BOT_CONFIG.

    BOT_CONFIG example: "@bot1:/qd,@bot2:sign,@bot3"
    - Each entry: "bot_username:command"
    - Commands are sent exactly as configured; no leading slash is added automatically.
    - If command is omitted, default "/qd" is used.
    """
    result: list[tuple[str, str]] = []

    if not BOT_CONFIG_RAW:
        return result

    entries = [e.strip() for e in BOT_CONFIG_RAW.split(",") if e.strip()]
    for entry in entries:
        if ":" in entry:
            bot, cmd_raw = entry.split(":", 1)
        else:
            bot, cmd_raw = entry, ""
        bot = bot.strip()
        if not bot:
            continue
        cmd = _resolve_command(cmd_raw)
        result.append((bot, cmd))

    return result


async def main() -> int:
    # Random startup delay to mimic human behavior and reduce spam risk
    delay_seconds = random.randint(60, 300)
    bot_command_list = get_bot_command_list()
    record = {
        "kind": "command_submission", "targets": len(bot_command_list),
        "attempted": 0, "submitted": 0, "target_failed": 0,
        "global_failed": 0, "send_unconfirmed": 0,
        "stopped": False, "disconnect_failed": False,
    }
    client = None
    log_failed = False
    try:
        await asyncio.sleep(delay_seconds)
        client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
        await client.start()
        for bot_username, sign_cmd in bot_command_list:
            record["attempted"] += 1
            try:
                await client.send_message(bot_username, sign_cmd)
            except TARGET_ERRORS:
                record["target_failed"] += 1
            except RPCError:
                # Authentication, account limits and other global RPC failures
                # must not be retried against every remaining destination.
                record["global_failed"] += 1
                record["stopped"] = True
                break
            except asyncio.CancelledError:
                record["send_unconfirmed"] += 1
                record["stopped"] = True
                raise
            except Exception:
                # A transport failure may happen after Telegram accepted input.
                record["send_unconfirmed"] += 1
                record["stopped"] = True
                break
            else:
                record["submitted"] += 1
            await asyncio.sleep(random.randint(2, 5))
    except asyncio.CancelledError:
        record["stopped"] = True
        raise
    except Exception:
        record["global_failed"] += 1
        record["stopped"] = True
    finally:
        if client is not None:
            try:
                await client.disconnect()
            except Exception:
                record["disconnect_failed"] = True
        record["not_attempted"] = record["targets"] - record["attempted"]
        record["time"] = datetime.now(timezone(timedelta(hours=8))).isoformat()
        log_msg = json.dumps(record, sort_keys=True) + "\n"
        print(log_msg, end="")
        try:
            with open("checkin.log", "a", encoding="utf-8") as f:
                f.write(log_msg)
        except OSError:
            log_failed = True
            print("Error: submission summary could not be saved.")
    return int(log_failed or record["target_failed"] > 0 or record["stopped"] or record["disconnect_failed"])


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
