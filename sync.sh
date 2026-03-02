#!/bin/bash
# sync.sh - 양방향 자동 동기화 (Mac ↔ Ubuntu ↔ Windows)
# OpenClaw 워크스페이스 + Claude Code 설정 동기화 (newest-wins)
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
      OS_INFO="Windows $(cmd //c ver 2>/dev/null | grep -oP '[\d.]+' | head -1 || echo 'unknown') ($(uname -m))" ;;
    *)
      OS_INFO="$(lsb_release -ds 2>/dev/null || uname -s) ($(uname -m))" ;;
  esac

  OC_VERSION=$(openclaw --version 2>/dev/null || echo "N/A")
  OC_MODEL=$(openclaw config get agents.defaults.model.primary 2>/dev/null || echo "N/A")
  CLAUDE_VERSION=$(claude --version 2>/dev/null || echo "N/A")

  # 스케줄러 목록 (Unix: cron, Windows: Task Scheduler)
  if [ "$PLATFORM" = "windows" ]; then
    SCHEDULED_JOBS=$(schtasks /query /fo LIST /tn "ai-config-sync" 2>/dev/null || echo "(없음)")
  else
    SCHEDULED_JOBS=$(crontab -l 2>/dev/null | grep -v '^#' | grep -v '^$' || echo "(없음)")
  fi

  RECENT_FILES=$(find "$HOME/.openclaw/workspace" -type f \
    -not -path '*/.git/*' -newer "$HOME/.openclaw/workspace/MEMORY.md" 2>/dev/null \
    | sed "s|$HOME/.openclaw/workspace/||" | head -10 || echo "(없음)")

  cat > "$STATE_FILE" <<EOF
# State: $HOSTNAME
> 마지막 업데이트: $(date '+%Y-%m-%d %H:%M %Z')

## 환경
- **OS:** $OS_INFO
- **Hostname:** $HOSTNAME

## OpenClaw
- **버전:** $OC_VERSION
- **기본 모델:** $OC_MODEL

## Claude Code
- **버전:** $CLAUDE_VERSION

## 스케줄 목록
\`\`\`
$SCHEDULED_JOBS
\`\`\`

## 최근 변경된 워크스페이스 파일
\`\`\`
$RECENT_FILES
\`\`\`
EOF
  echo "  → 상태 기록: state/$HOSTNAME.md"
}

# ── 1. Fetch (아직 적용 안 함) ───────────────────────────────────
echo "⬇️  원격 변경사항 확인 중..."
git fetch origin main

LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)

if [ "$LOCAL" = "$REMOTE" ]; then
  echo "  → 원격 이미 최신"
else
  echo "  → 원격에 새 변경사항 있음"
fi

# ── 2. 파일별 최신 버전 병합 (newest-wins) ───────────────────────
echo "🔀 파일별 최신 버전 병합 중..."
$PYTHON_CMD "$SYNC_DIR/sync-timestamps.py" "$SYNC_DIR" "$HOSTNAME"

# ── 3. 상태 파일 생성 ────────────────────────────────────────────
generate_state

# ── 4. 변경사항 push (충돌 시 rebase 후 재시도) ──────────────────
# 동기화 산출물 경로만 add (의도치 않은 파일 커밋 방지)
git add -A openclaw/workspace claude-code timestamps state

if git diff --cached --quiet; then
  echo "  → 변경사항 없음"
else
  git commit -m "sync [$HOSTNAME]: $(date '+%Y-%m-%d %H:%M')"
  if ! git push origin main 2>/dev/null; then
    echo "  → push 충돌. rebase 후 재시도..."
    git pull --rebase origin main
    git push origin main
  fi
  echo "  ✅ Push 완료"
fi

# ── 5. 로컬 코드 최신화 (스크립트 자체 업데이트 포함) ─────────────
if git pull --rebase origin main 2>/dev/null; then
  echo "  → 코드 최신화 완료"
else
  echo "  ⚠️ 코드 최신화 실패 (다음 실행에서 재시도)"
fi

echo "✅ [$HOSTNAME] 동기화 완료!"
