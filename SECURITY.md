# Security policy

Security fixes target the latest release and `main` branch.

## Reporting

Do not open a public issue containing `SESSION_STRING`, API credentials,
private chats, target lists, workflow logs with account data, or exploit
details. Use GitHub's
[private vulnerability reporting](https://github.com/Pigbibi/TelegramAutoSignBot/security/advisories/new).
If that form is unavailable, ask for a private contact through information on
the repository owner's GitHub profile without sharing technical details
publicly.

Include the affected commit, reproduction steps, required attacker access,
impact, and mitigation in the private report.

## Relevant issues

- session or API credential exposure;
- workflow changes that can exfiltrate Actions secrets;
- unsafe logging of chats, targets, or environment variables;
- command parsing that sends content to an unintended target;
- dependency or artifact handling that exposes account data.

If a session string may be compromised, revoke the Telegram session
immediately. Do not wait for a maintainer response.
