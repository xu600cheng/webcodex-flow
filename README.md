# webcodex-flow（双枪干活套件）

> **贵的额度只用来「想清楚」，便宜的那份拿去「搬砖」。**
> 桌面 Codex（强模型）写方案 → 网页 ChatGPT（另一份额度）照着写代码 → 桌面 Codex 验收。

本项目不发明新技术。它把三件麻烦事打包成一条命令：

1. **一键部署 [WebCodex](https://github.com/xq3427/WebCodex)**（让 ChatGPT 网页版读写你本机的开源 MCP 服务），并绕开几个必踩的坑
2. **生成双击即用的启动器**（macOS 上做成正规 `.app`，没有会被误关的黑窗口）
3. **灌入一整套提示词模板**：给桌面 Codex 的初始化提示词、给网页端的派工模板、验收模板、项目文档骨架

---

## 先别急着装：你必须有这些

| 条件 | 说明 |
|---|---|
| ChatGPT **Plus / Pro**（或 Business / Enterprise / Edu） | 免费版没有开发者模式，装了也用不了 |
| 能登录 [platform.openai.com](https://platform.openai.com) | 要建隧道和 API Key |
| macOS（Apple 芯片或 Intel） | **本项目只在 macOS 上验证过**。Linux 主体可用但未充分测试，Windows 未测试 |
| Node.js 22.16+ | 没有的话脚本会给你下载地址 |

> ⚠️ **安全提示，认真读一遍**
> 部署完成后，ChatGPT 网页端能读写你指定的项目目录。默认还会开放本机命令执行，
> 也就是说它在理论上能看到你账号权限内的**任何文件**。
> **只开放专用项目目录**，别把桌面、下载根目录、整块硬盘扔进去。
> 介意的话看 [docs/troubleshooting.md](docs/troubleshooting.md) 里「怎么收紧权限」。

---

## 一分钟上手

```sh
git clone https://github.com/xu600cheng/webcodex-flow.git
cd webcodex-flow
sh install.sh --workspace "$HOME/Desktop/我的项目"
```

`--workspace` 填你打算让 ChatGPT 碰的那个目录。**建议放一个「项目大本营」，下面每个子目录是一个项目，加一次全都能用。**

装完脚本会让你做剩下三步（都必须在浏览器里，脚本替不了）：

1. 去 [Tunnels 页面](https://platform.openai.com/settings/organization/tunnels) 建隧道，复制 `tunnel_` 开头的 ID
2. 去 [API Keys 页面](https://platform.openai.com/api-keys) 建一个 **Restricted** key，权限**只勾 Tunnels 的 Read + Use**
3. 打开本机面板（启动器会自动开浏览器）填入这两样 → 保存 → 启动服务

然后到 ChatGPT 网页版：

4. 设置 → **账户安全与登录** → 开**开发者模式**（找不到开关就去插件页点 ➕，菜单里有「创建自定义 MCP 服务器」就说明已经开了）
5. `chatgpt.com/plugins` → ➕ → **创建自定义 MCP 服务器** → 连接选**隧道**、身份验证选 **No Auth** → 创建
6. 新开对话，**必须是「聊天」模式**，用 ➕ 或 `@WebCodex` 唤出

验收：让它列出你的项目目录。**真的列出来了才算通，它嘴上说路径不算。**

---

## 日常怎么用：四步循环

| 步骤 | 谁干 | 干什么 | 你要手动搬的东西 | 
|---|---|---|---|
| 1 | 桌面 Codex | 澄清需求 → 产出 `docs/PRD.md`、`docs/DEV.md`、`AGENTS.md`（任务清单）→ 生成派工单 `docs/DISPATCH-00N.md` | **一行**：`读 <项目>/docs/DISPATCH-001.md，照着做。` |
| 2 | 网页 ChatGPT | 照派工单**一次只做一条任务**，代码直写本机；完工把报告写回同一份派工单 | 无（代码自动落盘） |
| 3 | 桌面 Codex | **一行**：`看 docs/DISPATCH-001.md 的产出，按 PRD 验收。`它自己读文件 | **一行** |
| 4 | 桌面 Codex | 更新任务清单，生成下一张派工单，回到第 2 步 | 无 |

> **你只搬文本，从不搬代码。** 这一步最容易搞混：网页端写的不是聊天记录里的代码块，
> 它通过隧道**直接写进你本机那个文件夹**，改完在编辑器里就能看到。
> 而文本搬运已经被压到一行——因为三条路径全写在那份派工单里，网页端自己读。

模板都在 `templates/` 里，直接复制：

| 文件 | 什么时候用 |
|---|---|
| `CODEX_INIT_PROMPT.md` | **每个新项目发一次**，让桌面 Codex 学会这套流程并写进它自己的记忆 |
| `AGENTS_COLLAB.md` | 粘进项目 `AGENTS.md` 的协作章节 |
| `PRD_TEMPLATE.md` / `DEV_TEMPLATE.md` | 新项目起步时的文档骨架 |
| `DISPATCH_CARD.md` | **派工单（落盘版）**，让桌面端把派工写成文件，你只需复制一行 |
| `WEB_DISPATCH.md` | 网页端派工：一句话版（推荐）+ 整段版（临时加约束时用） |
| `REVIEW_PROMPT.md` | 回桌面 Codex 验收用 |

### 三条红线

1. **方案必须落成文件。** 两边唯一的桥是硬盘上的 md 文件，对话里说过的话另一边永远看不到。
2. **一次只派一条任务。** 派一堆，只会得到一堆半成品。
3. **动手前让它复述理解。** 几乎零成本，能挡掉一半返工。

---

## 为什么值得这么折腾

Codex 客户端和 ChatGPT 网页聊天是**两份额度，分开算**。
写代码是批量烧 token 的活，甩给网页那一份；贵额度留给真正需要判断力的地方——想清楚要做什么。

代价要说清楚：**网页端的模型通常比 Codex 客户端弱一档**。
所以第 3 步的验收不能省。代码质量靠流程兜，不靠模型自觉。

---

## 已知限制（诚实版）

- **只在 macOS 上完整验证过。** Linux 没跑过，Windows 不支持。
- **写死了 WebCodex 版本** `0.16.0-preview.18`。上游改了 CLI 参数或目录结构，脚本会失效。可用 `--version` 指定别的版本试。
- **没有自动化测试。** 靠人肉在隔离目录里跑，不是 CI。
- **重试是安全的**：再跑一次 `install.sh` 不会冲掉你已经填好的隧道 ID 和 API Key（已实测）。
- **启动器会先杀掉已有的 WebCodex 进程**再启动，这是故意的——同时开两个会抢端口。别手动另开一份。
- 核心依赖上游 `xq3427/WebCodex`，它要是哪天把部署也做顺了，这个仓库就只剩模板有价值。

## 目录结构

```
webcodex-flow/
├─ install.sh              一键部署
├─ templates/              提示词与文档模板
├─ skills/webcodex-flow/   给 AI 助手读的 Skill（让 AI 也懂这套流程）
└─ docs/troubleshooting.md 排错与权限收紧
```

## 和其他项目的关系

核心通道是 [xq3427/WebCodex](https://github.com/xq3427/WebCodex)（MIT），
由它负责本机 MCP 服务和 OpenAI 官方隧道。**本项目只是它外面的一层：部署脚本 + 工作流模板。**
上游有问题请先去那边看 issue。

## 许可证

MIT。见 [LICENSE](LICENSE)。
