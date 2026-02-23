#!/bin/bash
# sync-openclaw.sh - Ubuntu에서 GitHub으로 설정 동기화

set -e

WORKSPACE_DIR="$HOME/.openclaw/workspace"
SYNC_DIR="$(cd "$(dirname "$0")" && pwd)"

cd "$SYNC_DIR"

echo "📂 워크스페이스 복사 중..."
rm -rf workspace
cp -r "$WORKSPACE_DIR" .
# 서브 git 레포 제거 (예: tools/flutter)
find workspace -name ".git" -type d -exec rm -rf {} + 2>/dev/null || true
# 민감 데이터 제거
rm -f workspace/notion_data_*.json workspace/tmp_*.json

echo "📤 GitHub에 push 중..."
git add .
git status --short

if git diff --cached --quiet; then
  echo "✅ 변경 사항 없음"
else
  git commit -m "Sync: $(date '+%Y-%m-%d %H:%M KST')"
  git push origin main
  echo "✅ 동기화 완료!"
fi
