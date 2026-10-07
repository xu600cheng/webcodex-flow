---
name: webcodex-flow
description: 双枪干活工作流——桌面 Codex 写方案、网页 ChatGPT 写代码、桌面 Codex 验收。当用户要求「按双枪流程推进」「写派工提示词」「写 PRD/DEV/任务清单」「验收网页端改的代码」「更新 AGENTS.md」时使用。也用于部署 WebCodex 通道本身。
---

# 双枪干活工作流

贵的额度只用来「想清楚」，便宜的那份拿去「搬砖」。

## 角色分工

- **桌面 Codex（强模型、贵额度）**：澄清需求、PRD、技术方案、任务清单、验收、疑难 bug。**不批量写代码。**
- **网页 ChatGPT（弱一档、另一份额度）**：照着文档，一次一条地实现任务。**不做架构决策。**

两边唯一的桥是硬盘上的文件：`docs/PRD.md`、`docs/DEV.md`、`AGENTS.md`。

## 四步循环

1. 桌面 Codex 产出三份文档（不确定就先问，一次最多 5 个问题）
2. 网页端实现**一条**任务
3. 桌面 Codex 验收，问题按严重/中级/轻微分级，严重的直接改
4. 更新 `AGENTS.md`，回到第 2 步

## 派工提示词由你写

用户不需要准备模板。每次交付后**你**产出一段可直接复制到网页端的派工提示词，放在代码块里，包含：

- 项目目录（网页端用**相对**工作区根的路径；桌面端用绝对路径）
- 要读哪几份文档
- 本次只做哪一条任务
- 禁止事项：不许重构 / 改目录结构 / 新增依赖 / 碰清单外文件
- 禁止读取：`node_modules` `dist` `build` `release` `.git`
- 验证命令
- 动手前先复述理解
- 结尾提醒：WebCodex 服务已启动 / 聊天模式 / `@WebCodex`

## 三条红线

1. 方案必须落成文件——对话内容另一边看不到
2. 一次只派一条任务
3. 动手前让它复述理解

## 部署通道（WebCodex）

仓库 `https://github.com/xu600cheng/webcodex-flow`，核心通道依赖 `xq3427/WebCodex`。
一键部署：`sh install.sh --workspace "/绝对路径/项目目录"`。

必踩的坑（详见仓库 `docs/troubleshooting.md`）：

- 官方启动脚本写死 node 绝对路径，Node 升级后必炸 → 改成运行时探测
- 配置文件硬链接数必须是 1，否则全部 `CONFIG_ERROR`
- 官方安装器末尾报 `INTERNAL_ERROR` 是正常的（tunnel-client 其实装好了），补 `./webcodex init --no-tunnel`
- 隧道握手要 ~40 秒，别提前判失败
- `.command` 被桌面整理工具移动后会被 macOS 打隔离标记 → 用 `.app` 而不是 `.command`
- 本机改配置后，ChatGPT 端要点「刷新工具」并新开对话

## 前置条件

ChatGPT Plus/Pro（免费版没有开发者模式）、能建 OpenAI tunnel、macOS、Node ≥ 22.16。
