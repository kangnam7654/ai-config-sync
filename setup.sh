#!/bin/bash
# setup.sh - 대화형 통합 셋업
# 사용법: git clone <repo> && cd ai-config-sync && bash setup.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
HOSTNAME=$(hostname -s 2>/dev/null || hostname)

# ── 플랫폼 감지 ──────────────────────────────────────────────────
case "$OSTYPE" in
  darwin*)  PLATFORM="macos" ;;
  msys*|mingw*|cygwin*) PLATFORM="windows" ;;
  *)        PLATFORM="linux" ;;
esac

# Python 명령어 (Windows: python, Unix: python3)
if [ "$PLATFORM" = "windows" ]; then
  PYTHON_CMD="python"
else
  PYTHON_CMD="python3"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ai-config-sync 셋업"
echo "  호스트: $HOSTNAME ($PLATFORM)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# ── 1. 동기화 모드 ───────────────────────────────────────────────
echo "동기화 모드를 선택하세요:"
echo "  [1] 양방향 — 내 설정도 공유 (기본)"
echo "  [2] 수신 전용 — 다른 기기 설정만 받기 (pull-only)"
echo ""
read -p "선택 [1/2]: " SYNC_MODE
SYNC_MODE=${SYNC_MODE:-1}

if [ "$SYNC_MODE" = "2" ]; then
  touch "$SCRIPT_DIR/.pull-only"
  echo "  -> .pull-only 생성 완료 (수신 전용 모드)"
else
  rm -f "$SCRIPT_DIR/.pull-only"
  echo "  -> 양방향 모드"
fi
echo ""

# ── 2. 자동 동기화 (크론) ────────────────────────────────────────
read -p "자동 동기화(30분 간격)를 설정할까요? (y/n) [n]: " SETUP_CRON
SETUP_CRON=${SETUP_CRON:-n}

if [ "$SETUP_CRON" = "y" ] || [ "$SETUP_CRON" = "Y" ]; then
  if [ "$PLATFORM" = "windows" ]; then
    SYNC_DIR_WIN=$(cygpath -w "$SCRIPT_DIR" 2>/dev/null || echo "$SCRIPT_DIR")
    GIT_BASH_PATH=$(cygpath -w "$(which bash)" 2>/dev/null || echo "C:\\Program Files\\Git\\bin\\bash.exe")
    WIN_LOG_DIR="$HOME/.local/share/ai-config-sync"
    mkdir -p "$WIN_LOG_DIR"
    schtasks //Create //TN "ai-config-sync" \
      //TR "\"$GIT_BASH_PATH\" -l -c 'cd \"$SYNC_DIR_WIN\" && bash sync.sh >> \"$WIN_LOG_DIR/sync.log\" 2>&1'" \
      //SC MINUTE //MO 30 //F 2>/dev/null \
      && echo "  -> Task Scheduler 등록 완료 (30분)" \
      || echo "  -> Task Scheduler 등록 실패. 수동 등록 필요."
  else
    # 기존 ai-config-sync 크론 제거 후 재등록
    LOG_DIR="$HOME/.local/share/ai-config-sync"
    mkdir -p "$LOG_DIR"
    chmod 700 "$LOG_DIR"
    CRON_CMD="*/30 * * * * cd $SCRIPT_DIR && bash sync.sh >> $LOG_DIR/sync.log 2>&1"
    ( crontab -l 2>/dev/null | grep -v "ai-config-sync" ; echo "$CRON_CMD" ) | crontab -
    echo "  -> 크론 등록 완료 (30분 간격)"
  fi
else
  echo "  -> 크론 미설정 (수동 실행: bash sync.sh)"
fi
echo ""

# ── 3. Claude Code 설정 복원 ────────────────────────────────────
CLAUDE_SRC="$SCRIPT_DIR/claude-code"
CLAUDE_DST="$HOME/.claude"

if [ -d "$CLAUDE_SRC" ]; then
  read -p "Claude Code 설정을 복원할까요? (y/n) [y]: " RESTORE_CLAUDE
  RESTORE_CLAUDE=${RESTORE_CLAUDE:-y}

  if [ "$RESTORE_CLAUDE" = "y" ] || [ "$RESTORE_CLAUDE" = "Y" ]; then
    mkdir -p "$CLAUDE_DST"
    CLAUDE_ITEMS=$($PYTHON_CMD "$SCRIPT_DIR/sync-timestamps.py" --list-includes 2>/dev/null)
    if [ -z "$CLAUDE_ITEMS" ]; then
      CLAUDE_ITEMS="CLAUDE.md agents agent-memory memory plugins settings.json skills stop-hook-git-check.sh teams todos"
    fi
    for item in $CLAUDE_ITEMS; do
      SRC="$CLAUDE_SRC/$item"
      if [ -e "$SRC" ]; then
        if [ -d "$SRC" ]; then
          cp -r "$SRC" "$CLAUDE_DST/"
        else
          cp "$SRC" "$CLAUDE_DST/"
        fi
      fi
    done
    echo "  -> Claude Code 설정 복원 완료 (~/.claude/)"
  else
    echo "  -> Claude Code 복원 건너뜀"
  fi
else
  echo "  -> claude-code/ 디렉토리 없음 — 건너뜀"
fi
echo ""

# ── 4. OpenClaw 복원 (워크스페이스 존재 시) ──────────────────────
OPENCLAW_SRC="$SCRIPT_DIR/openclaw/workspace"

if [ -d "$OPENCLAW_SRC" ]; then
  read -p "OpenClaw 워크스페이스를 복원할까요? (y/n) [n]: " RESTORE_OC
  RESTORE_OC=${RESTORE_OC:-n}

  if [ "$RESTORE_OC" = "y" ] || [ "$RESTORE_OC" = "Y" ]; then
    WORKSPACE="$HOME/.openclaw/workspace"
    mkdir -p "$WORKSPACE"
    rsync -av --exclude='*.sh' "$OPENCLAW_SRC/" "$WORKSPACE/"
    echo "  -> OpenClaw 워크스페이스 복원 완료"

    # openclaw.json 생성 (템플릿에서)
    CONFIG_FILE="$HOME/.openclaw/openclaw.json"
    TEMPLATE="$SCRIPT_DIR/openclaw/openclaw.template.json"
    if [ ! -f "$CONFIG_FILE" ] && [ -f "$TEMPLATE" ]; then
      (umask 077 && sed "s|<REPLACE_WITH_YOUR_WORKSPACE_PATH>|$WORKSPACE|g" "$TEMPLATE" > "$CONFIG_FILE.tmp")
      NEW_TOKEN=$(openssl rand -hex 24)
      (umask 077 && sed "s|<REPLACE_WITH_NEW_TOKEN>|$NEW_TOKEN|g" "$CONFIG_FILE.tmp" > "$CONFIG_FILE")
      rm -f "$CONFIG_FILE.tmp"
      echo "  -> openclaw.json 생성 완료"
    fi
  else
    echo "  -> OpenClaw 복원 건너뜀"
  fi
fi
echo ""

# ── 5. 첫 동기화 실행 ───────────────────────────────────────────
read -p "지금 첫 동기화를 실행할까요? (y/n) [y]: " RUN_SYNC
RUN_SYNC=${RUN_SYNC:-y}

if [ "$RUN_SYNC" = "y" ] || [ "$RUN_SYNC" = "Y" ]; then
  echo ""
  bash "$SCRIPT_DIR/sync.sh"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  셋업 완료!"
if [ -f "$SCRIPT_DIR/.pull-only" ]; then
  echo "  모드: 수신 전용 (pull-only)"
else
  echo "  모드: 양방향"
fi
if [ "$SETUP_CRON" = "y" ] || [ "$SETUP_CRON" = "Y" ]; then
  echo "  자동 동기화: 30분 간격"
else
  echo "  자동 동기화: 미설정 (bash sync.sh)"
fi
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
