# Contributing

Focused bug fixes, tests, documentation improvements, and security hardening are
welcome.

## Development

Install Telethon only when integration work requires it. Syntax validation does
not need account credentials:

```bash
python -m py_compile main.py
```

Do not run the script against a real account during routine pull request
validation.

## Pull requests

- Work from the latest `main` on a separate branch.
- Keep one pull request focused on one problem.
- Preserve the documented `BOT_CONFIG` parsing rules or update both READMEs.
- Never add session strings, Telegram API credentials, target lists, chat
  content, or real run logs.
- Mock network behavior where possible; document any test that contacted
  Telegram.
- Explain workflow permission, dependency, and schedule changes.
- Keep the English and Simplified Chinese README aligned.

Use [SECURITY.md](SECURITY.md) for vulnerabilities and follow the
[Code of Conduct](CODE_OF_CONDUCT.md). Contributions use the repository's
[MIT License](LICENSE).
