# AGENTS.md

## 项目是什么

用 Telethon 从 Telegram 用户账号按计划向一小组配置好的 bot 发送命令，跑在 GitHub Actions 上。

## 技术栈

Python，Telethon。`python -m unittest discover -s tests` 跑离线测试。

## 目录

- `main.py` — 唯一入口。
- `tests/` — 离线测试。

## 本地验证

按改动选择相关离线检查，命令以仓库当前 CI 为准。先区分代码问题与环境条件，不为通过检查降低保护。

**离线测试**

```bash
python -m unittest discover -s tests
```

## 命名与文档

- 新增文档文件名小写、`-` 连接，中文版后缀 `.zh-CN.md`；`README.md`、`AGENTS.md` 等工具约定文件保留固定名称。源码沿用现有语言命名。
- 不提交审计报告、复盘、交接单、进度快照、升级计划。要追溯看 commit 历史。
- 改文件名时同一次提交改完所有引用。
- 提交前跑 `python scripts/check_hygiene.py`。

## 不要做

- 不要在代码、日志或 artifact 里输出 session 文件内容、API hash 或手机号。
- 不要扩大目标 bot 列表。这个账号只向配置里列出的 bot 发命令。
- 不要在测试里建立真实 Telegram 连接。

## 提交与 PR

Conventional Commits，标题中文，不超过 50 字。类型只用 `feat` `fix` `docs` `refactor` `test` `chore` `perf` `ci`。

分支名 `<type>/<主题>`，例如 `docs/normalize-filenames`。不直接推默认分支，不 force push 已 review 的分支。

提交、推送、合并及生产动作按用户已明确授权的范围执行；同范围已有授权不重复确认。

PR 描述写改了什么、为什么改、怎么验证。
