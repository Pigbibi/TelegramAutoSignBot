# TelegramAutoSignBot

[简体中文](README_CN.md)

Send scheduled commands from a Telegram user account to a small, configured list of bots using Telethon and GitHub Actions.

This uses a user session, not the Telegram Bot API. A session string grants account access: keep it private and use only automation permitted by Telegram and the target bots.

## Quick start

1. Create a private deployment copy and review the [workflow](.github/workflows/main.yml).
2. Obtain your Telegram application credentials and create a Telethon StringSession on a trusted machine.
3. Add the settings below to **Settings → Secrets and variables → Actions**.
4. Run **Telegram Auto Sign** and verify the conversations in Telegram.

| Setting | Store as | Purpose |
| --- | --- | --- |
| `API_ID` | Secret | Telegram application ID |
| `API_HASH` | Secret | Telegram application hash |
| `SESSION_STRING` | Secret | User account StringSession |
| `BOT_CONFIG` | Variable | Comma-separated `bot_username:command` entries |

Example target configuration:

```text
@example_bot:/qd,@another_bot:sign
```

An entry without a command uses `/qd`. Other commands are sent as configured; no slash is added automatically. Never print a session string to public logs or generate it through an untrusted website.

## Schedule and failures

The workflow runs daily at 00:00 UTC, with a random initial delay of 1–5 minutes and 2–5 seconds between targets. Runs are serialized and capped at 20 minutes. Delays do not guarantee that automation is permitted.

Target-specific errors allow later targets to run. Account errors, rate limits and uncertain transport outcomes stop the batch without automatic resending. Any failure produces a nonzero exit.

`checkin.log` on the `logs` branch records timestamps and counts, including partial runs. `submitted` means the send call returned; it does not prove the destination bot accepted a check-in. Updating this branch needs `contents: write` permission.

## Development

Use the Python version and Telethon dependency declared in the [offline test workflow](.github/workflows/offline-regression.yml), then run:

```bash
python -m unittest discover -s tests
```

The tests mock Telegram access. Running `main.py` with real settings sends messages. If a send outcome is uncertain, check Telegram before rerunning. Revoke the session if its credential is exposed.

## Support and contributing

[Support](SUPPORT.md) · [Contributing](CONTRIBUTING.md) · [Security](SECURITY.md) · [Code of conduct](CODE_OF_CONDUCT.md)

## License

[MIT](LICENSE).
