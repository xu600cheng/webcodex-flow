# 排错与权限收紧

## 症状 → 先查这个

| 现象 | 先查 |
|---|---|
| 双击启动器报 `No such file or directory` | 启动脚本里的 node 路径失效了（升级 Node 后）。重跑本仓库 `install.sh` 会自动重写成「运行时探测 node」的版本 |
| 双击启动器没反应 / 打不开 | 文件被 macOS 打了隔离标记。`xattr -d com.apple.quarantine "<文件路径>"`。用本仓库生成的 `.app` 不会有这问题 |
| 面板端口被占用，换了个随机端口 | 同一时间开了两个实例。`lsof -nP -iTCP:8767 -sTCP:LISTEN -t` 拿 PID，`kill` 掉多余的那个 |
| 一直停在 `Waiting for successful OpenAI polling` | 正常的握手过程，**等 40 秒左右**。看到 `Connected; local MCP is ready` 才算好 |
| `CONFIG_ERROR: ... regular file ... without links` | 配置文件的硬链接数不是 1。`cp config.toml /tmp/c.toml && rm config.toml && cp /tmp/c.toml config.toml` |
| ChatGPT 说「功能是关闭的」 | ChatGPT 里的应用缓存了旧工具清单。去插件详情页点**刷新**，然后**新开对话** |
| 说「已写入」但文件夹没变化 | 让它报**实际调用的工具名和错误码**。没有工具调用记录＝它根本没动手 |
| 设置里找不到「开发者模式」 | 先确认在**浏览器网页版**，桌面 App 没有这个入口。菜单里有「创建自定义 MCP 服务器」就说明已经开了 |
| 工作区在外接硬盘上时访问失败 | 硬盘挂载了没有？ |

## 怎么收紧权限

默认配置是 `execution.mode = trusted-host` + `command_policy = all`，
意味着 ChatGPT 能通过本机命令看到你账号权限内的任何文件。

要收紧：

```sh
cd ~/.local/share/webcodex
./webcodex execution set-mode disabled     # 关掉本机命令执行
```

代价：它就跑不了 `npm run test` 这类命令了，只能读写文件。

也可以在面板「功能与权限」里改，或者把某个工作区设成只读：

```sh
./webcodex workspace add --id docs --root "/路径" --name "只读资料" --read-only
```

## 改了本机配置之后

ChatGPT 端**不会自动更新**。去插件详情页点「刷新工具」，然后新开对话。
