#!/bin/bash
# sync-openclaw.sh - 양방향 자동 동기화 (Mac ↔ Ubuntu)
# OpenClaw 워크스페이스 + Claude Code 설정 동기화
# 사용법: bash sync-openclaw.sh

set -e

WORKSPACE_DIR="$HOME/.openclaw/workspace"
CLAUDE_DIR="$HOME/.claude"
SYNC_DIR="$(cd "$(dirname "$0")" && pwd)"
HOSTNAME=$(hostname -s)

cd "$SYNC_DIR"

echo "🔄 [$HOSTNAME] 동기화 시작..."

# ── 1. 원격 변경사항 먼저 pull ────────────────────────────────────
echo "⬇️  원격 변경사항 가져오는 중..."
git fetch origin main

LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)

if [ "$LOCAL" != "$REMOTE" ]; then
  echo "  → 원격에 새 변경사항 있음. 병합 중..."
  git pull --rebase origin main

  # OpenClaw 워크스페이스 반영
  if [ -d "$SYNC_DIR/workspace" ]; then
    echo "  → OpenClaw 워크스페이스 적용 중..."
    mkdir -p "$WORKSPACE_DIR"
    rsync -a --exclude='.git' "$SYNC_DIR/workspace/" "$WORKSPACE_DIR/"
  fi

  # Claude Code 설정 반영
  if [ -d "$SYNC_DIR/claude-config" ]; then
    echo "  → Claude Code 설정 적용 중..."
    mkdir -p "$CLAUDE_DIR"
    rsync -a "$SYNC_DIR/claude-config/" "$CLAUDE_DIR/"
  fi

  echo "  ✅ 원격 변경사항 반영 완료"
else
  echo "  → 원격 이미 최신"
fi

# ── 2. 로컬 변경사항 수집 ────────────────────────────────────────
echo "⬆️  로컬 변경사항 수집 중..."

# OpenClaw 워크스페이스
rm -rf workspace
cp -r "$WORKSPACE_DIR" workspace
find workspace -name ".git" -type d -exec rm -rf {} + 2>/dev/null || true
rm -f workspace/notion_data_*.json workspace/tmp_*.json workspace/*.jsonl

# Claude Code 설정 (민감/임시 파일 제외)
rm -rf claude-config
mkdir -p claude-config
rsync -a \
  --include='settings.json' \
  --include='CLAUDE.md' \
  --include='stop-hook-git-check.sh' \
  --include='agents/***' \
  --include='plugins/***' \
  --include='skills/***' \
  --include='agent-memory/***' \
  --include='todos/***' \
  --include='teams/***' \
  --exclude='*' \
  "$CLAUDE_DIR/" claude-config/
# 심볼릭 링크 제거 (claude-code-hud 의존)
find claude-config -type l -delete 2>/dev/null || true
# 민감/임시 파일 제거
rm -f claude-config/history.jsonl claude-config/usage-log.jsonl
rm -rf claude-config/cache claude-config/debug claude-config/backups \
       claude-config/file-history claude-config/telemetry \
       claude-config/session-env claude-config/shell-snapshots \
       claude-config/ide claude-config/downloads

# ── 3. 변경사항 push ──────────────────────────────────────────────
git add .

if git diff --cached --quiet; then
  echo "  → 변경사항 없음"
else
  git commit -m "sync [$HOSTNAME]: $(date '+%Y-%m-%d %H:%M')"
  git push origin main
  echo "  ✅ Push 완료"
fi

echo "✅ [$HOSTNAME] 동기화 완료!"
