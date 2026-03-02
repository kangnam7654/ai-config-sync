#!/bin/bash
# sync.sh - 양방향 자동 동기화 (Mac ↔ Ubuntu)
# OpenClaw 워크스페이스 + Claude Code 설정 동기화 (newest-wins)
# 사용법: bash sync.sh

set -e

SYNC_DIR="$(cd "$(dirname "$0")" && pwd)"
HOSTNAME=$(hostname -s)

cd "$SYNC_DIR"

echo "🔄 [$HOSTNAME] 동기화 시작..."

# ══════════════════════════════════════════════════
# 함수: 현재 기기 상태를 state/{hostname}.md에 기록
# ══════════════════════════════════════════════════
generate_state() {
  mkdir -p "$SYNC_DIR/state"
  STATE_FILE="$SYNC_DIR/state/$HOSTNAME.md"

  if [[ "$OSTYPE" == "darwin"* ]]; then
    OS_INFO="macOS $(sw_vers -productVersion) ($(uname -m))"
  else
    OS_INFO="$(lsb_release -ds 2>/dev/null || uname -s) ($(uname -m))"
  fi

  OC_VERSION=$(openclaw --version 2>/dev/null || echo "N/A")
  OC_MODEL=$(openclaw config get agents.defaults.model.primary 2>/dev/null || echo "N/A")
  CLAUDE_VERSION=$(claude --version 2>/dev/null || echo "N/A")
  CRON_JOBS=$(crontab -l 2>/dev/null | grep -v '^#' | grep -v '^$' || echo "(없음)")
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

## Cron 목록
\`\`\`
$CRON_JOBS
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
python3 "$SYNC_DIR/sync-timestamps.py" "$SYNC_DIR" "$HOSTNAME"

# ── 3. 상태 파일 생성 ────────────────────────────────────────────
generate_state

# ── 4. 변경사항 push (충돌 시 rebase 후 재시도) ──────────────────
git add .

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
git pull --rebase origin main 2>/dev/null || true

echo "✅ [$HOSTNAME] 동기화 완료!"
