# TelegramAutoSignBot

[English](README.md)

使用 Telethon 和 GitHub Actions，定时通过 Telegram 用户账户向少量指定机器人发送命令。

项目使用用户会话，而非 Telegram Bot API。会话字符串具有账户访问权限，必须保密；仅用于 Telegram 和目标机器人允许的自动化操作。

## 快速开始

1. 创建私有部署副本，检查[工作流](.github/workflows/main.yml)。
2. 获取自己的 Telegram 应用凭据，在可信设备上生成 Telethon StringSession。
3. 在 **Settings → Secrets and variables → Actions** 添加以下配置。
4. 运行 **Telegram Auto Sign**，并到 Telegram 对话中确认结果。

| 配置 | 存储位置 | 用途 |
| --- | --- | --- |
| `API_ID` | Secret | Telegram 应用 ID |
| `API_HASH` | Secret | Telegram 应用 hash |
| `SESSION_STRING` | Secret | 用户账户会话字符串 |
| `BOT_CONFIG` | Variable | 逗号分隔的 `机器人用户名:命令` |

目标配置示例：

```text
@example_bot:/qd,@another_bot:sign
```

省略命令时使用 `/qd`；其他命令按配置原样发送，不自动补斜杠。不要将会话字符串输出到公开日志，也不要通过不可信网站生成。

## 运行时间与失败处理

默认每天 00:00 UTC 运行，启动后随机等待 1–5 分钟，目标之间间隔 2–5 秒。运行互斥，最长 20 分钟。随机延迟不代表平台允许自动化。

单个目标的错误允许继续处理后续目标；账户错误、限流和传输结果未知会停止批次，不自动重发。任意失败都会返回非零退出码。

`logs` 分支的 `checkin.log` 记录时间和计数，包括部分失败。`submitted` 仅表示发送调用已返回，不代表对方机器人接受签到。更新日志分支需要 `contents: write` 权限。

## 开发与排障

按[离线测试工作流](.github/workflows/offline-regression.yml)配置 Python 和 Telethon，再运行：

```bash
python -m unittest discover -s tests
```

测试会模拟 Telegram 访问。使用真实配置运行 `main.py` 会发送消息。发送结果不明时，先检查 Telegram 再决定是否重跑；会话凭据泄露时撤销该会话。

## 支持与贡献

[问题与支持](SUPPORT.md) · [贡献指南](CONTRIBUTING.md) · [安全问题](SECURITY.md) · [行为准则](CODE_OF_CONDUCT.md)

## 许可证

[MIT](LICENSE)。
