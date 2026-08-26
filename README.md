# TelegramAutoSignBot

[简体中文](README_CN.md)

[![Workflow](https://github.com/Pigbibi/TelegramAutoSignBot/actions/workflows/main.yml/badge.svg)](https://github.com/Pigbibi/TelegramAutoSignBot/actions/workflows/main.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Use a Telegram user account to send scheduled commands to configured bots with
Telethon and GitHub Actions.

## Important limitation

This project automates a personal Telegram account, not a Bot API account. A
Telethon session string grants account access and must be protected like a
password. Random delays do not guarantee that Telegram or a destination bot
will permit the automation. Use a private deployment, keep the target list
small, and follow Telegram's terms and each bot's rules.

## How it works

```text
GitHub Actions daily schedule
        │
        ▼
Telethon opens the configured user session
        │
        ▼
commands sent to BOT_CONFIG targets in order
        │
        ▼
run record appended on the logs branch
```

The workflow starts at `00:00 UTC` every day. The script waits a random 1–5
minutes before connecting and 2–5 seconds between targets. These delays reduce
burst traffic but are not an anti-abuse guarantee.

Runs are serialized so that a delayed schedule or manual trigger cannot overlap
another check-in. Each run is capped at 20 minutes to avoid leaving a stalled
Telegram connection active indefinitely.

## Configuration

Add these repository secrets:

| Secret | Purpose |
| --- | --- |
| `API_ID` | Telegram application ID from `my.telegram.org` |
| `API_HASH` | Telegram application hash |
| `SESSION_STRING` | Telethon StringSession credential for the user account |

Add this repository variable:

| Variable | Format |
| --- | --- |
| `BOT_CONFIG` | Comma-separated `bot_username:command` entries |

Examples:

```text
@bot1:/qd,@bot2:sign
@bot1:/qd,@bot2:sign,@bot3
```

An entry without a command uses `/qd`. Commands are otherwise sent exactly as
configured; the script does not add a leading slash.

## Create a session string

Install Telethon on a trusted local machine and use your own Telegram API
credentials to create a StringSession. Never run a session-generation tool from
an untrusted repository or website.

After generating the value, store it only as the `SESSION_STRING` Actions
secret. Do not paste it into workflow files, issues, logs, or screenshots.

## Deploy

1. Create a private fork or private copy for the account-specific deployment.
2. Review `.github/workflows/main.yml` before adding credentials.
3. Add `API_ID`, `API_HASH`, and `SESSION_STRING` as Actions secrets.
4. Add `BOT_CONFIG` as an Actions variable.
5. Confirm the workflow's `GITHUB_TOKEN` may write repository contents so it can
   update the `logs` branch.
6. Enable Actions and run **Telegram Auto Sign** manually.
7. Verify the target bot conversations from Telegram.

The public source repository contains no account configuration. Keeping the
deployment private reduces accidental disclosure through logs and future
configuration changes.

## Schedule and logs

Edit the cron expression in `.github/workflows/main.yml` to change the schedule.
GitHub Actions cron uses UTC and scheduled jobs may start late.

Run records are stored in `checkin.log` on the `logs` branch. They list target
usernames and commands but do not prove that a destination bot accepted or
processed a command.

## Local validation

Check Python syntax without connecting to Telegram:

```bash
python -m py_compile main.py
```

Running `main.py` requires real credentials and sends real messages. Use a
disposable account and test bot when integration testing is necessary.

## Security

- Treat `SESSION_STRING` as a full account credential.
- Use a dedicated Telegram account with minimal access where practical.
- Review every workflow change before approving it in a credentialed fork.
- Keep Actions logs and artifacts free of session values and private chats.
- Revoke active Telegram sessions immediately after suspected exposure.
- Do not accept pull requests that print environment variables or session data.

Follow [SECURITY.md](SECURITY.md) for vulnerability reports.

## Contributing and support

Read [CONTRIBUTING.md](CONTRIBUTING.md) before submitting a change. See
[SUPPORT.md](SUPPORT.md) for usage questions and bug reports. Participation is
governed by [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## License

TelegramAutoSignBot is available under the [MIT License](LICENSE).
