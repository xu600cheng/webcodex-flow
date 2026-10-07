#!/bin/sh
# webcodex-flow 一键部署
# 用法：sh install.sh --workspace "/绝对路径/你的项目目录"
# 可选：--version <WebCodex 版本>  默认 0.16.0-preview.18

set -eu

WC_VERSION='0.16.0-preview.18'
WORKSPACE=''
WC_HOME="${HOME}/.local/share/webcodex"
SETUP_URL="https://github.com/xq3427/WebCodex/releases/download/v${WC_VERSION}/WebCodex-${WC_VERSION}-setup.zip"

while [ "$#" -gt 0 ]; do
  case "$1" in
    --workspace|-w) WORKSPACE="$2"; shift 2 ;;
    --version) WC_VERSION="$2"
      SETUP_URL="https://github.com/xq3427/WebCodex/releases/download/v${WC_VERSION}/WebCodex-${WC_VERSION}-setup.zip"
      shift 2 ;;
    -h|--help)
      echo "用法：sh install.sh --workspace \"/绝对路径/项目目录\" [--version 0.16.0-preview.18]"; exit 0 ;;
    *) echo "不认识的参数：$1"; exit 1 ;;
  esac
done

say() { printf '\n\033[1m%s\033[0m\n' "$1"; }
info() { printf '  %s\n' "$1"; }
die() { printf '\n\033[31m%s\033[0m\n' "$1" >&2; exit 1; }

say '0/7 检查运行环境'
[ "$(uname -s)" = 'Darwin' ] || die '本项目只在 macOS 上验证过。Linux 可自行改路径尝试，Windows 未支持。'
command -v curl >/dev/null 2>&1 || die '缺少 curl'
command -v unzip >/dev/null 2>&1 || die '缺少 unzip'
command -v git >/dev/null 2>&1 || info '未检测到 git，WebCodex 部分功能会受限（建议装 Xcode Command Line Tools）'

NODE_BIN=''
for cand in "${HOME}"/.workbuddy/binaries/node/versions/*/bin/node; do
  [ -x "$cand" ] && NODE_BIN="$cand"
done
[ -z "$NODE_BIN" ] && NODE_BIN="$(command -v node 2>/dev/null || true)"
if [ -z "$NODE_BIN" ]; then
  die '没找到 Node.js。请先安装 22.16 或更高版本：https://nodejs.org/'
fi
NODE_MAJOR=$("$NODE_BIN" -p 'process.versions.node.split(".")[0]' 2>/dev/null || echo 0)
NODE_MINOR=$("$NODE_BIN" -p 'process.versions.node.split(".")[1]' 2>/dev/null || echo 0)
if [ "$NODE_MAJOR" -lt 22 ] || { [ "$NODE_MAJOR" -eq 22 ] && [ "$NODE_MINOR" -lt 16 ]; }; then
  die "Node 版本过低（$("$NODE_BIN" -v)），需要 >= 22.16"
fi
info "Node：$NODE_BIN $("$NODE_BIN" -v)"

say '1/7 下载 WebCodex 安装包'
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
curl -fL --progress-bar -o "$TMP/setup.zip" "$SETUP_URL" || die '下载失败，检查网络或代理'
unzip -q -o "$TMP/setup.zip" -d "$TMP/setup"
info '下载完成'

say '2/7 运行官方安装器（这一步末尾报 INTERNAL_ERROR 是正常的，忽略即可）'
( cd "$TMP/setup" && sh install.sh --no-panel ) || true

say '3/7 生成本机配置'
[ -x "$WC_HOME/webcodex" ] || die "没找到 $WC_HOME/webcodex，官方安装器可能失败了"
cd "$WC_HOME"
./webcodex init --no-tunnel >/dev/null 2>&1 || true

say '4/7 修复两处官方安装器的遗留问题'
# 4a 配置文件的硬链接数必须等于 1，否则 doctor / connect 全部报 CONFIG_ERROR
NLINK=$(ls -l "$WC_HOME/config.toml" 2>/dev/null | awk '{print $2}')
if [ -n "$NLINK" ] && [ "$NLINK" != '1' ]; then
  cp "$WC_HOME/config.toml" "$WC_HOME/.config.new" && mv "$WC_HOME/.config.new" "$WC_HOME/config.toml"
  chmod 600 "$WC_HOME/config.toml"
  info '已修复配置文件的硬链接计数'
fi
# 4b 官方启动脚本写死了 node 绝对路径，Node 升级后会失效
APPDIR=$(ls -d "$WC_HOME"/app/*/ 2>/dev/null | tail -1)
APPBASE=$(basename "${APPDIR%/}")
[ -n "$APPBASE" ] || die "没找到 WebCodex 程序目录（$WC_HOME/app），官方安装器可能失败了"
cat > "$WC_HOME/webcodex" <<EOS
#!/bin/sh
set -eu
# 运行时解析路径与 node，避免 Node 升级后脚本失效
WC_HOME="\${HOME}/.local/share/webcodex"
APP="\$WC_HOME/app/${APPBASE}/node_modules/webcodex-mcp/dist/src/cli.js"
CONFIG="\$WC_HOME/config.toml"
NODE_BIN=''
for cand in "\${HOME}"/.workbuddy/binaries/node/versions/*/bin/node /opt/homebrew/bin/node /usr/local/bin/node; do
  [ -x "\$cand" ] && NODE_BIN="\$cand" && break
done
[ -z "\$NODE_BIN" ] && NODE_BIN="\$(command -v node 2>/dev/null || true)"
[ -z "\$NODE_BIN" ] && { echo '[WebCodex] 找不到 node（需要 >= 22.16）' >&2; exit 1; }
if [ "\$#" -eq 0 ]; then set -- setup; fi
exec "\$NODE_BIN" "\$APP" "\$@" --config "\$CONFIG"
EOS
chmod +x "$WC_HOME/webcodex"
info '已改为运行时自动探测 node'

say '5/7 配置工作区'
if [ -n "$WORKSPACE" ]; then
  mkdir -p "$WORKSPACE" || die "无法创建 $WORKSPACE"
  ./webcodex workspace add --id main --root "$WORKSPACE" --name "$(basename "$WORKSPACE")" >/dev/null 2>&1 || \
    ./webcodex workspace rebind --id main --root "$WORKSPACE" --name "$(basename "$WORKSPACE")" >/dev/null 2>&1 || true
  ./webcodex workspace remove --id default >/dev/null 2>&1 || true
  info "已开放：$WORKSPACE"
else
  info '没有指定 --workspace，稍后在本机面板里自己添加（「我的工作区」→「添加工作区」）'
fi

say '6/7 生成双击即用的启动器'
mkdir -p "${HOME}/Applications/WebCodex.app/Contents/MacOS" "${HOME}/Applications/停止WebCodex.app/Contents/MacOS"
cat > "${HOME}/Applications/WebCodex.app/Contents/Info.plist" <<'EOS'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
<key>CFBundleName</key><string>WebCodex</string>
<key>CFBundleIdentifier</key><string>com.webcodex.launcher</string>
<key>CFBundleVersion</key><string>1.0</string>
<key>CFBundlePackageType</key><string>APPL</string>
<key>CFBundleExecutable</key><string>WebCodex</string>
<key>LSUIElement</key><true/>
</dict></plist>
EOS
cat > "${HOME}/Applications/WebCodex.app/Contents/MacOS/WebCodex" <<EOS
#!/bin/sh
pkill -f 'webcodex-mcp/dist/src/cli.js' 2>/dev/null
pkill -f 'tools/tunnel-client' 2>/dev/null
sleep 3
cd '$WC_HOME' || exit 1
rm -f /tmp/webcodex_app.log
nohup ./webcodex connect > /tmp/webcodex_app.log 2>&1 &
URL=''
I=0
while [ "\$I" -lt 120 ]; do
  URL=\$(grep -o 'http://127\\.0\\.0\\.1:[0-9]*/#token=[A-Za-z0-9_-]*' /tmp/webcodex_app.log 2>/dev/null | head -1)
  [ -n "\$URL" ] && break
  sleep 1; I=\$((I + 1))
done
if [ -n "\$URL" ]; then
  open "\$URL"
  osascript -e 'display notification "服务已启动，面板已打开。隧道约 40 秒内连上。" with title "WebCodex"' 2>/dev/null
else
  osascript -e 'display notification "启动超时，日志在 /tmp/webcodex_app.log" with title "WebCodex"' 2>/dev/null
fi
exit 0
EOS
cat > "${HOME}/Applications/停止WebCodex.app/Contents/Info.plist" <<'EOS'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
<key>CFBundleName</key><string>停止WebCodex</string>
<key>CFBundleIdentifier</key><string>com.webcodex.stopper</string>
<key>CFBundleVersion</key><string>1.0</string>
<key>CFBundlePackageType</key><string>APPL</string>
<key>CFBundleExecutable</key><string>StopWebCodex</string>
<key>LSUIElement</key><true/>
</dict></plist>
EOS
cat > "${HOME}/Applications/停止WebCodex.app/Contents/MacOS/StopWebCodex" <<'EOS'
#!/bin/sh
pkill -f 'webcodex-mcp/dist/src/cli.js' 2>/dev/null
pkill -f 'tools/tunnel-client' 2>/dev/null
sleep 2
osascript -e 'display notification "已停止，ChatGPT 现在够不着本机了" with title "WebCodex"' 2>/dev/null
exit 0
EOS
chmod +x "${HOME}/Applications/WebCodex.app/Contents/MacOS/WebCodex" \
         "${HOME}/Applications/停止WebCodex.app/Contents/MacOS/StopWebCodex"
info '已生成：应用程序/WebCodex.app、应用程序/停止WebCodex.app'

say '7/7 本机自检'
DOCTOR=$(./webcodex doctor 2>&1 || true)
echo "$DOCTOR" | head -40
if echo "$DOCTOR" | grep -q '"ok"[[:space:]]*:[[:space:]]*true'; then
  info '自检通过'
else
  info '自检没通过。看上面的报错，对照 docs/troubleshooting.md 处理'
fi

cat <<'EOF'

──────────────────────────────────────────
 剩下的三步必须你自己登录 OpenAI 做（脚本替不了）：

 1) https://platform.openai.com/settings/organization/tunnels
    建隧道，复制 tunnel_ 开头的 ID

 2) https://platform.openai.com/api-keys
    新建 Restricted key，权限只勾 Tunnels 的 Read + Use

 3) 双击「应用程序/WebCodex.app」
    面板会自动打开 → 填上面两样 → 保存 → 启动服务

 然后去 ChatGPT 网页版：
    设置 → 账户安全与登录 → 开「开发者模式」
    chatgpt.com/plugins → ➕ → 创建自定义 MCP 服务器
    连接选「隧道」，身份验证选 No Auth

 ⚠️ 使用时必须是「聊天」模式，选工作/Codex 模式就白折腾
──────────────────────────────────────────
EOF
