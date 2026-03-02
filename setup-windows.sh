#!/bin/bash
# setup-windows.sh - Windows에서 OpenClaw + Claude Code 동기화 초기 설정
# Git Bash에서 실행: bash setup-windows.sh
set -e

WORKSPACE="$HOME/.openclaw/workspace"
CONFIG_DIR="$HOME/.openclaw"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "🦞 OpenClaw Windows 설정 복원 시작..."

# 1. 워크스페이스 복원
echo "📂 워크스페이스 복원 중: $WORKSPACE"
mkdir -p "$WORKSPACE"
cp -r "$SCRIPT_DIR/openclaw/workspace/"* "$WORKSPACE/" 2>/dev/null || true

# 2. openclaw.json 생성 (템플릿에서)
CONFIG_FILE="$CONFIG_DIR/openclaw.json"
TEMPLATE="$SCRIPT_DIR/openclaw/openclaw.template.json"

if [ ! -f "$CONFIG_FILE" ]; then
  echo ""
  echo "⚙️  openclaw.json 생성 중..."
  WORKSPACE_WIN=$(cygpath -w "$WORKSPACE" 2>/dev/null || echo "$WORKSPACE")
  sed "s|<REPLACE_WITH_YOUR_WORKSPACE_PATH>|$WORKSPACE_WIN|g" "$TEMPLATE" > "$CONFIG_FILE.tmp"

  NEW_TOKEN=$(openssl rand -hex 24 2>/dev/null || python -c "import secrets; print(secrets.token_hex(24))")
  sed "s|<REPLACE_WITH_NEW_TOKEN>|$NEW_TOKEN|g" "$CONFIG_FILE.tmp" > "$CONFIG_FILE"
  rm "$CONFIG_FILE.tmp"

  echo "✅ openclaw.json 생성 완료"
else
  echo "⚠️  openclaw.json 이미 존재함 — 건너뜀"
fi

# 3. Task Scheduler 등록 (30분마다 동기화)
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 Windows Task Scheduler 자동 등록을 시도합니다..."
SYNC_DIR_WIN=$(cygpath -w "$SCRIPT_DIR" 2>/dev/null || echo "$SCRIPT_DIR")
GIT_BASH_PATH=$(cygpath -w "$(which bash)" 2>/dev/null || echo "C:\\Program Files\\Git\\bin\\bash.exe")

schtasks //Create //TN "ai-config-sync" \
  //TR "\"$GIT_BASH_PATH\" -l -c 'cd \"$SYNC_DIR_WIN\" && bash sync.sh >> /tmp/ai-config-sync.log 2>&1'" \
  //SC MINUTE //MO 30 //F 2>/dev/null && echo "✅ Task Scheduler 등록 완료 (30분 간격)" || {
  echo "⚠️  자동 등록 실패. 수동으로 등록하세요:"
  echo ""
  echo "  schtasks /Create /TN \"ai-config-sync\" \\"
  echo "    /TR \"\\\"$GIT_BASH_PATH\\\" -l -c 'cd \\\"$SYNC_DIR_WIN\\\" && bash sync.sh'\" \\"
  echo "    /SC MINUTE /MO 30"
}
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 4. 인증 안내
echo ""
echo "🔑 Anthropic 인증이 필요합니다."
echo "  openclaw onboard --anthropic-api-key 'sk-ant-...'"
echo ""
echo "✅ 완료! 'bash sync.sh'로 첫 동기화를 실행하세요."
