#!/bin/bash
# restore-openclaw.sh

SYNC_REPO_DIR="$HOME/openclaw-sync"
OPENCLAW_DIR="$HOME/.openclaw"
WORKSPACE_DIR="$OPENCLAW_DIR/workspace"

if [ ! -d "$SYNC_REPO_DIR" ]; then
    echo "Cloning sync repository..."
    gh repo clone openclaw-config-sync "$SYNC_REPO_DIR"
fi

cd "$SYNC_REPO_DIR"
git pull origin main

echo "Restoring config and workspace..."
mkdir -p "$OPENCLAW_DIR"

# 설정 파일 복원
cp openclaw.json "$OPENCLAW_DIR/"

# 워크스페이스 복원 (기존 워크스페이스가 있다면 백업 권장)
if [ -d "$WORKSPACE_DIR" ]; then
    mv "$WORKSPACE_DIR" "${WORKSPACE_DIR}_backup_$(date +%Y%m%d_%H%M%S)"
fi
cp -r workspace "$OPENCLAW_DIR/"

echo "Restore complete! Run 'openclaw doctor' to verify."
