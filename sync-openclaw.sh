#!/bin/bash
# sync-openclaw.sh - 양방향 자동 동기화 (Mac ↔ Ubuntu)
# 사용법: bash sync-openclaw.sh

set -e

WORKSPACE_DIR="$HOME/.openclaw/workspace"
SYNC_DIR="$(cd "$(dirname "$0")" && pwd)"
HOSTNAME=$(hostname -s)

cd "$SYNC_DIR"

echo "🔄 [$HOSTNAME] OpenClaw 동기화 시작..."

# ── 1. 원격 변경사항 먼저 pull ────────────────────────────────────
echo "⬇️  원격 변경사항 가져오는 중..."
git fetch origin main

LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)

if [ "$LOCAL" != "$REMOTE" ]; then
  echo "  → 원격에 새 변경사항 있음. 병합 중..."
  git pull --rebase origin main

  # 원격 workspace 내용을 로컬에 반영
  echo "  → 워크스페이스에 적용 중..."
  rsync -a --exclude='.git' --exclude='*.sh' --exclude='README.md' \
    "$SYNC_DIR/workspace/" "$WORKSPACE_DIR/"
  echo "  ✅ 원격 변경사항 반영 완료"
else
  echo "  → 원격 이미 최신"
fi

# ── 2. 로컬 변경사항 push ─────────────────────────────────────────
echo "⬆️  로컬 변경사항 확인 중..."
rm -rf workspace
cp -r "$WORKSPACE_DIR" workspace
find workspace -name ".git" -type d -exec rm -rf {} + 2>/dev/null || true
rm -f workspace/notion_data_*.json workspace/tmp_*.json workspace/*.jsonl

git add .

if git diff --cached --quiet; then
  echo "  → 로컬 변경사항 없음"
else
  git commit -m "sync [$HOSTNAME]: $(date '+%Y-%m-%d %H:%M')"
  git push origin main
  echo "  ✅ 로컬 변경사항 push 완료"
fi

echo "✅ [$HOSTNAME] 동기화 완료!"
