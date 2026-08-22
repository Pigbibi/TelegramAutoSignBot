# TelegramAutoSignBot

[English](README.md)

[![Workflow](https://github.com/Pigbibi/TelegramAutoSignBot/actions/workflows/main.yml/badge.svg)](https://github.com/Pigbibi/TelegramAutoSignBot/actions/workflows/main.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

使用 Telethon 和 GitHub Actions，让 Telegram 用户账号定时向配置的 bot 发送命令。

## 重要说明

本项目自动操作的是个人 Telegram 账号，不是 Bot API 账号。Telethon session string
具备账号访问能力，必须像密码一样保护。随机延迟不能保证 Telegram 或目标 bot 会
允许自动化操作。建议使用私有部署、控制目标数量，并遵守 Telegram 服务条款和各
目标 bot 的规则。

## 工作流程

```text
GitHub Actions 每日定时任务
        │
        ▼
Telethon 打开配置的用户会话
        │
        ▼
按顺序向 BOT_CONFIG 目标发送命令
        │
        ▼
在 logs 分支追加运行记录
```

workflow 每天 `00:00 UTC` 启动。脚本连接前随机等待 1–5 分钟，每个目标之间随机
等待 2–5 秒。延迟只能减少集中请求，不能作为规避风控的保证。

## 配置

添加以下 GitHub Actions secrets：

| Secret | 用途 |
| --- | --- |
| `API_ID` | 从 `my.telegram.org` 获取的 Telegram application ID |
| `API_HASH` | Telegram application hash |
| `SESSION_STRING` | 用户账号的 Telethon StringSession 凭据 |

添加以下 repository variable：

| Variable | 格式 |
| --- | --- |
| `BOT_CONFIG` | 逗号分隔的 `bot_username:command` |

示例：

```text
@bot1:/qd,@bot2:sign
@bot1:/qd,@bot2:sign,@bot3
```

没有填写命令的目标默认使用 `/qd`。其他命令会原样发送，脚本不会自动补 `/`。

## 创建 session string

在可信电脑上安装 Telethon，使用自己的 Telegram API 凭据创建 StringSession。
不要在不可信网站或仓库提供的脚本中生成会话。

生成后只把它保存为 Actions 的 `SESSION_STRING` secret。不要写进 workflow、issue、
日志或截图。

## 部署

1. 为账号专属部署创建私有 fork 或私有副本。
2. 添加凭据前先审查 `.github/workflows/main.yml`。
3. 把 `API_ID`、`API_HASH` 和 `SESSION_STRING` 添加为 Actions secrets。
4. 把 `BOT_CONFIG` 添加为 Actions variable。
5. 确认 workflow 的 `GITHUB_TOKEN` 可以写入仓库，以便更新 `logs` 分支。
6. 启用 Actions，手动运行一次 **Telegram Auto Sign**。
7. 回到 Telegram 检查目标 bot 会话。

公开源码仓库不包含账号配置。账号专属部署使用私有仓库，可以降低日志或后续配置
改动造成意外泄露的风险。

## 运行时间与日志

修改 `.github/workflows/main.yml` 中的 cron 可以调整时间。GitHub Actions cron 使用
UTC，定时任务可能晚于配置时间启动。

运行记录保存在 `logs` 分支的 `checkin.log`。它会记录目标用户名和命令，但不能证明
目标 bot 已经接受或处理命令。

## 本地检查

不连接 Telegram，仅检查 Python 语法：

```bash
python -m py_compile main.py
```

直接运行 `main.py` 需要真实凭据并会发送真实消息。必须联调时，请使用独立测试账号
和测试 bot。

## 安全

- 把 `SESSION_STRING` 当作完整账号凭据保护。
- 条件允许时使用权限和联系人最少的独立 Telegram 账号。
- 在带凭据的 fork 中批准 workflow 改动前，逐行检查差异。
- Actions 日志和 artifact 中不得出现 session 或私有聊天内容。
- 怀疑泄露时，立即在 Telegram 中撤销对应活跃会话。
- 不接受打印环境变量或 session 数据的代码改动。

安全问题请按 [SECURITY.md](SECURITY.md) 报告。

## 贡献与支持

提交改动前请阅读 [CONTRIBUTING.md](CONTRIBUTING.md)。使用问题和 bug 报告渠道见
[SUPPORT.md](SUPPORT.md)。参与社区时请遵守
[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)。

## 许可证

本项目使用 [MIT License](LICENSE)。
