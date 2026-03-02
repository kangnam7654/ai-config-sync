#!/bin/bash
# setup-mac.sh - 맥북에서 OpenClaw 설정을 복원하는 스크립트
# 사용법: bash setup-mac.sh

set -e

WORKSPACE="$HOME/.openclaw/workspace"
CONFIG_DIR="$HOME/.openclaw"

echo "🦞 OpenClaw MacBook 설정 복원 시작..."

# 1. OpenClaw CLI 설치 (없으면)
if ! command -v openclaw &> /dev/null; then
  echo "📦 OpenClaw 설치 중..."
  npm install -g openclaw
fi

# 2. 워크스페이스 복원
echo "📂 워크스페이스 복원 중: $WORKSPACE"
mkdir -p "$WORKSPACE"
rsync -av --exclude='*.sh' "$(dirname "$0")/openclaw/workspace/" "$WORKSPACE/"

# 3. openclaw.json 생성 (템플릿에서)
CONFIG_FILE="$CONFIG_DIR/openclaw.json"
TEMPLATE="$(dirname "$0")/openclaw/openclaw.template.json"

if [ ! -f "$CONFIG_FILE" ]; then
  echo ""
  echo "⚙️  openclaw.json 생성 중..."
  # 워크스페이스 경로 치환
  sed "s|<REPLACE_WITH_YOUR_WORKSPACE_PATH>|$WORKSPACE|g" "$TEMPLATE" > "$CONFIG_FILE.tmp"

  # 게이트웨이 토큰 생성
  NEW_TOKEN=$(openssl rand -hex 24)
  sed "s|<REPLACE_WITH_NEW_TOKEN>|$NEW_TOKEN|g" "$CONFIG_FILE.tmp" > "$CONFIG_FILE"
  rm "$CONFIG_FILE.tmp"

  echo "✅ openclaw.json 생성 완료 (토큰 자동 생성됨)"
else
  echo "⚠️  openclaw.json 이미 존재함 — 건너뜀 (수동으로 openclaw.template.json 참고)"
fi

# 4. Anthropic 인증 안내
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔑 Anthropic 인증이 필요합니다."
echo "아래 중 하나를 실행하세요:"
echo ""
echo "  [API Key 방식]"
echo "  openclaw onboard --anthropic-api-key 'sk-ant-...'"
echo ""
echo "  [Claude 구독 방식]"
echo "  claude setup-token  # Claude CLI에서 토큰 생성"
echo "  openclaw models auth paste-token --provider anthropic"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 5. 게이트웨이 실행
echo "🚀 OpenClaw Gateway 시작..."
openclaw gateway install
openclaw gateway start

echo ""
echo "✅ 완료! 'openclaw status'로 상태를 확인하세요."
