#!/bin/bash
# sync.sh - 양방향 자동 동기화 (Mac ↔ Ubuntu ↔ Windows)
# OpenClaw 워크스페이스 + Claude Code 설정 동기화 (newest-wins)
# Windows는 pull-only (수신만, 푸시 안 함)
# 사용법: bash sync.sh

set -e

SYNC_DIR="$(cd "$(dirname "$0")" && pwd)"
HOSTNAME=$(hostname -s 2>/dev/null || hostname)

cd "$SYNC_DIR"

# ── 플랫폼 감지 ──────────────────────────────────────────────────
detect_platform() {
  case "$OSTYPE" in
    darwin*)  PLATFORM="macos" ;;
    msys*|mingw*|cygwin*) PLATFORM="windows" ;;
    *)        PLATFORM="linux" ;;
  esac
}

detect_platform

# Python 명령어 (Windows: python, Unix: python3)
if [ "$PLATFORM" = "windows" ]; then
  PYTHON_CMD="python"
  export PYTHONUTF8=1
  export PYTHONIOENCODING=utf-8
else
  PYTHON_CMD="python3"
fi

echo "🔄 [$HOSTNAME] ($PLATFORM) 동기화 시작..."

# ══════════════════════════════════════════════════
# 함수: 현재 기기 상태를 state/{hostname}.md에 기록
# ══════════════════════════════════════════════════
generate_state() {
  mkdir -p "$SYNC_DIR/state"
  STATE_FILE="$SYNC_DIR/state/$HOSTNAME.md"

  case "$PLATFORM" in
    macos)
      OS_INFO="macOS $(sw_vers -productVersion) ($(uname -m))" ;;
    windows)
      OS_INFO="Windows ($(uname -m))" ;;
    *)
      OS_INFO="$(lsb_release -ds 2>/dev/null || uname -s) ($(uname -m))" ;;
  esac

  OC_VERSION=$(openclaw --version 2>/dev/null || echo "N/A")
  OC_MODEL=$(openclaw config get agents.defaults.model.primary 2>/dev/null || echo "N/A")
  CLAUDE_VERSION=$(claude --version 2>/dev/null || echo "N/A")

  # 스케줄러 목록 (Unix: cron, Windows: Task Scheduler)
  if [ "$PLATFORM" = "windows" ]; then
    SCHEDULED_JOBS=$(schtasks /query /fo LIST /tn "ai-config-sync" 2>/dev/null || echo "(none)")
  else
    SCHEDULED_JOBS=$(crontab -l 2>/dev/null | grep -v '^#' | grep -v '^$' || echo "(none)")
  fi

  RECENT_FILES=$(find "$HOME/.openclaw/workspace" -type f \
    -not -path '*/.git/*' -newer "$HOME/.openclaw/workspace/MEMORY.md" 2>/dev/null \
    | sed "s|$HOME/.openclaw/workspace/||" | head -10 || echo "(none)")

  cat > "$STATE_FILE" <<EOF
# State: $HOSTNAME
> Last updated: $(date '+%Y-%m-%d %H:%M %Z')

## Environment
- **OS:** $OS_INFO
- **Hostname:** $HOSTNAME

## OpenClaw
- **Version:** $OC_VERSION
- **Model:** $OC_MODEL

## Claude Code
- **Version:** $CLAUDE_VERSION

## Scheduled Jobs
\`\`\`
$SCHEDULED_JOBS
\`\`\`

## Recent Workspace Changes
\`\`\`
$RECENT_FILES
\`\`\`
EOF
  echo "  -> state/$HOSTNAME.md"
}

# ── 1. Fetch ─────────────────────────────────────────────────────
echo "  Fetching remote..."
git fetch origin main

LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)

if [ "$LOCAL" = "$REMOTE" ]; then
  echo "  -> Already up to date"
else
  echo "  -> Remote has new changes"
fi

# ── 2. newest-wins merge ─────────────────────────────────────────
echo "  Merging (newest-wins)..."
$PYTHON_CMD "$SYNC_DIR/sync-timestamps.py" "$SYNC_DIR" "$HOSTNAME"

# ── 3. Generate state ────────────────────────────────────────────
generate_state

# ── 4. Push (Windows는 pull-only → 스킵) ─────────────────────────
if [ "$PLATFORM" = "windows" ]; then
  echo "  -> Windows: pull-only mode (skip push)"
else
  # 동기화 산출물 경로만 add (의도치 않은 파일 커밋 방지)
  git add -A openclaw/workspace claude-code timestamps state

  if git diff --cached --quiet; then
    echo "  -> No changes"
  else
    git commit -m "sync [$HOSTNAME]: $(date '+%Y-%m-%d %H:%M')"
    if ! git push origin main 2>/dev/null; then
      echo "  -> Push conflict, rebasing..."
      git pull --rebase origin main
      git push origin main
    fi
    echo "  Push OK"
  fi
fi

# ── 5. Pull latest code ──────────────────────────────────────────
if [ "$PLATFORM" = "windows" ]; then
  # Windows는 push하지 않으므로 repo를 remote에 맞춰 리셋
  git reset --hard origin/main 2>/dev/null
  echo "  -> Code reset to origin/main"
else
  if git pull --rebase origin main 2>/dev/null; then
    echo "  -> Code updated"
  else
    echo "  [WARN] Code update failed (will retry next run)"
  fi
fi

echo "Done [$HOSTNAME]"
