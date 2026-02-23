#!/bin/bash
# sync-openclaw.sh - 양방향 자동 동기화 (Mac ↔ Ubuntu)
# OpenClaw 워크스페이스 + Claude Code 설정 동기화
# 사용법: bash sync-openclaw.sh

set -e

WORKSPACE_DIR="$HOME/.openclaw/workspace"
CLAUDE_DIR="$HOME/.claude"
SYNC_DIR="$(cd "$(dirname "$0")" && pwd)"
HOSTNAME=$(hostname -s)
STATE_DIR="$SYNC_DIR/state"

cd "$SYNC_DIR"

echo "🔄 [$HOSTNAME] 동기화 시작..."

# ══════════════════════════════════════════════════
# 함수: 현재 기기 상태를 state/{hostname}.md에 기록
# ══════════════════════════════════════════════════
generate_state() {
  mkdir -p "$STATE_DIR"
  STATE_FILE="$STATE_DIR/$HOSTNAME.md"

  # OS 정보
  if [[ "$OSTYPE" == "darwin"* ]]; then
    OS_INFO="macOS $(sw_vers -productVersion) ($(uname -m))"
  else
    OS_INFO="$(lsb_release -ds 2>/dev/null || uname -s) ($(uname -m))"
  fi

  # OpenClaw 상태
  OC_VERSION=$(openclaw --version 2>/dev/null || echo "N/A")
  OC_MODEL=$(openclaw config get agents.defaults.model.primary 2>/dev/null || echo "N/A")
  OC_CHANNELS=$(openclaw channels list --json 2>/dev/null \
    | grep -o '"name":"[^"]*"' | sed 's/"name":"//;s/"//' | tr '\n' ', ' | sed 's/, $//' \
    || echo "N/A")

  # Claude Code 상태
  CLAUDE_VERSION=$(claude --version 2>/dev/null || echo "N/A")

  # Cron 목록
  CRON_JOBS=$(crontab -l 2>/dev/null | grep -v '^#' | grep -v '^$' || echo "(없음)")

  # 최근 변경된 워크스페이스 파일 (5일 이내)
  RECENT_FILES=$(find "$WORKSPACE_DIR" -type f -newer "$WORKSPACE_DIR/MEMORY.md" \
    -not -path '*/.git/*' 2>/dev/null \
    | sed "s|$WORKSPACE_DIR/||" | head -10 || echo "(없음)")

  cat > "$STATE_FILE" <<EOF
# State: $HOSTNAME
> 마지막 업데이트: $(date '+%Y-%m-%d %H:%M %Z')

## 환경
- **OS:** $OS_INFO
- **Hostname:** $HOSTNAME

## OpenClaw
- **버전:** $OC_VERSION
- **기본 모델:** $OC_MODEL
- **활성 채널:** ${OC_CHANNELS:-없음}

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

  echo "  → 상태 기록 완료: state/$HOSTNAME.md"
}

# ══════════════════════════════════════════════════
# 함수: 상대방 기기 상태 요약 출력
# ══════════════════════════════════════════════════
read_peer_state() {
  for f in "$STATE_DIR"/*.md; do
    PEER=$(basename "$f" .md)
    [ "$PEER" = "$HOSTNAME" ] && continue
    [ -f "$f" ] || continue

    echo ""
    echo "  📋 [$PEER] 상태:"
    # 주요 항목만 추출해서 출력
    grep -E "^\-\s\*\*|^>\s마지막" "$f" | sed 's/^/     /' || true
    echo ""
  done
}

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

  # 상대방 기기 상태 출력
  read_peer_state
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
find claude-config -type l -delete 2>/dev/null || true
rm -f claude-config/history.jsonl claude-config/usage-log.jsonl
rm -rf claude-config/cache claude-config/debug claude-config/backups \
       claude-config/file-history claude-config/telemetry \
       claude-config/session-env claude-config/shell-snapshots \
       claude-config/ide claude-config/downloads

# ── 3. 현재 기기 상태 기록 ────────────────────────────────────────
generate_state

# ── 4. 변경사항 push (충돌 시 rebase 후 재시도) ────────────────────
git add .

if git diff --cached --quiet; then
  echo "  → 변경사항 없음"
else
  git commit -m "sync [$HOSTNAME]: $(date '+%Y-%m-%d %H:%M')"

  # push 실패 시 rebase 후 1회 재시도
  if ! git push origin main 2>&1; then
    echo "  → push 충돌 감지. rebase 후 재시도..."
    git pull --rebase origin main
    git push origin main
  fi
  echo "  ✅ Push 완료"
fi

echo "✅ [$HOSTNAME] 동기화 완료!"
