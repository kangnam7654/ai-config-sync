#!/bin/bash
# sync-openclaw.sh

OPENCLAW_DIR="$HOME/.openclaw"
WORKSPACE_DIR="$OPENCLAW_DIR/workspace"
SYNC_REPO_DIR="$HOME/openclaw-sync"

# 1. Sync용 저장소 폴더 생성 (없을 경우)
if [ ! -d "$SYNC_REPO_DIR" ]; then
    echo "Creating sync repository directory..."
    mkdir -p "$SYNC_REPO_DIR"
fi

cd "$SYNC_REPO_DIR"

# 2. .gitignore 설정 (민감 정보 제외)
cat <<EOF > .gitignore
# OpenClaw Sync Ignore
# --------------------
# 절대 공유되면 안 되는 보안 파일들
credentials/
*.db
*.sqlite
sessions/
logs/
.DS_Store
*.tgz
EOF

# 3. 설정 및 워크스페이스 복사 (민감 폴더 제외)
echo "Copying config and workspace..."
# config 파일 복사 (credentials 제외)
cp "$OPENCLAW_DIR/openclaw.json" . 2>/dev/null || echo "openclaw.json not found"

# 워크스페이스 복사 (전체)
rm -rf workspace
cp -r "$WORKSPACE_DIR" .
# 워크스페이스 내의 .git 폴더 제거 (서브모듈 충돌 방지)
rm -rf workspace/.git

# 4. Git 작업
if [ ! -d ".git" ]; then
    git init
    # GitHub 리포지토리가 없으면 생성 (private 권장)
    gh repo create openclaw-config-sync --private --source=. --remote=origin || git remote add origin "https://$(gh auth token)@github.com/kangnam7654/openclaw-config-sync.git"
fi

git add .
git commit -m "Sync OpenClaw settings: $(date)"
git push origin main

echo "Sync complete! Now you can clone this on your MacBook."
