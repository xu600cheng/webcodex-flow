# 粘进项目 AGENTS.md 的协作章节

把下面这段追加到项目根目录 `AGENTS.md` **末尾**（不要覆盖已有内容）。
如果项目里有 `CLAUDE.md`，在它末尾补一行：`协作方式见 AGENTS.md 的双枪协作章节`。

```markdown
## 双枪协作（桌面 Codex ↔ 网页 ChatGPT）

- 分工：本客户端负责方案、文档、任务清单、验收；
  网页 ChatGPT（聊天模式 + @WebCodex）负责逐条实现。
- 前提：本机运行 WebCodex（双击「应用程序/WebCodex.app」），否则网页端够不着项目。
- 交接媒介只有文件：docs/PRD.md（需求与红线）、docs/DEV.md（方案与约定）、
  AGENTS.md（任务清单）。
- 任务清单格式：编号｜任务名｜要改的文件｜具体做什么｜怎么验证。一次只派一条。
- 网页端禁止：重构、改目录结构、新增依赖、碰清单外的文件。
- 网页端禁止读取：node_modules / dist / build / release / .git。
- 派工提示词由本客户端产出，用户只负责复制到网页端。
```
