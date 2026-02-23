#!/bin/bash
# sync-openclaw.sh - 어느 기기에서든 OpenClaw 워크스페이스 동기화
#
# 사용법:
#   sh sync-openclaw.sh         # 현재 기기 변경사항 → GitHub (push)
#   sh sync-openclaw.sh pull    # GitHub → 현재 기기 워크스페이스 (pull)

set -e

WORKSPACE_DIR="$HOME/.openclaw/workspace"
SYNC_DIR="$(cd "$(dirname "$0")" && pwd)"
ACTION="${1:-push}"

cd "$SYNC_DIR"

if [ "$ACTION" = "pull" ]; then
  echo "⬇️  GitHub에서 최신 워크스페이스 가져오는 중..."
  git pull origin main

  echo "📂 워크스페이스에 적용 중: $WORKSPACE_DIR"
  mkdir -p "$WORKSPACE_DIR"
  rsync -av --exclude='*.sh' --exclude='.git' \
    "$SYNC_DIR/workspace/" "$WORKSPACE_DIR/"

  echo "✅ Pull 완료! 최신 설정이 적용됐습니다."

elif [ "$ACTION" = "push" ]; then
  echo "📂 워크스페이스 복사 중..."
  rm -rf workspace
  cp -r "$WORKSPACE_DIR" .
  find workspace -name ".git" -type d -exec rm -rf {} + 2>/dev/null || true
  rm -f workspace/notion_data_*.json workspace/tmp_*.json

  echo "📤 GitHub에 push 중..."
  git add .
  git status --short

  if git diff --cached --quiet && git diff HEAD --quiet; then
    echo "✅ 변경 사항 없음"
  else
    git commit -m "Sync [$(hostname -s)]: $(date '+%Y-%m-%d %H:%M KST')"
    git push origin main
    echo "✅ Push 완료!"
  fi

else
  echo "❌ 알 수 없는 명령: $ACTION"
  echo "사용법: sh sync-openclaw.sh [push|pull]"
  exit 1
fi
