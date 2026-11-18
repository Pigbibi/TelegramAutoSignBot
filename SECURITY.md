# Security policy

Security fixes target the latest release and `main` branch.

## Reporting a vulnerability

Report security vulnerabilities through [GitHub private vulnerability reporting](https://github.com/Pigbibi/TelegramAutoSignBot/security/advisories/new). Do not post exploit details, credentials, private sessions or personal data in public issues or PRs.

Include the affected version, impact and minimal redacted reproduction. The maintainer handles reports on a best-effort basis; no bounty or response-time guarantee is implied.

## Relevant issues

- session or API credential exposure;
- workflow changes that can exfiltrate Actions secrets;
- unsafe logging of chats, targets, or environment variables;
- command parsing that sends content to an unintended target;
- dependency or artifact handling that exposes account data.

If a session string may be compromised, revoke the Telegram session
immediately. Do not wait for a maintainer response.
