#!/bin/bash
# setup-windows.sh - Windows에서 Claude Code 설정 동기화 초기 설정
# Git Bash에서 실행: bash setup-windows.sh
# 참고: Windows는 Claude Code만 동기화 (OpenClaw 미사용)
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "⚙️  Claude Code Windows 동기화 설정 시작..."

# 1. Claude Code 설정 복원
CLAUDE_DIR="$HOME/.claude"
echo "📂 Claude Code 설정 복원 중: $CLAUDE_DIR"
mkdir -p "$CLAUDE_DIR"

# claude-code/ 내 설정 파일들을 ~/.claude/로 복사
for item in CLAUDE.md settings.json agents plugins skills agent-memory memory todos teams stop-hook-git-check.sh; do
  SRC="$SCRIPT_DIR/claude-code/$item"
  if [ -e "$SRC" ]; then
    cp -r "$SRC" "$CLAUDE_DIR/"
  fi
done
echo "  ✅ Claude Code 설정 복원 완료"

# 2. Task Scheduler 등록 (30분마다 동기화)
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

echo ""
echo "✅ 완료! 'bash sync.sh'로 첫 동기화를 실행하세요."
