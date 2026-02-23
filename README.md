# OpenClaw Config Sync

Ubuntu ↔ MacBook Pro 간 OpenClaw 설정 동기화 저장소.

> **보안 주의:** API 키, 토큰 등 민감 정보는 이 레포에 포함되지 않습니다. `.gitignore` 참고.

---

## 📁 구조

```
├── workspace/          # MEMORY.md, USER.md, SOUL.md 등 에이전트 워크스페이스
├── openclaw.template.json  # 설정 템플릿 (민감 값 제거됨)
├── setup-mac.sh        # 맥북 초기 설정 자동화 스크립트
└── sync-openclaw.sh    # Ubuntu에서 동기화 push 스크립트
```

---

## 🖥️ MacBook에서 처음 설정하는 법

```bash
# 1. 이 레포 클론
git clone https://github.com/kangnam7654/openclaw-config-sync.git ~/openclaw-sync

# 2. 셋업 스크립트 실행 (Node.js 필요)
cd ~/openclaw-sync
bash setup-mac.sh

# 3. Anthropic 인증 (API Key 또는 Claude 구독)
openclaw onboard --anthropic-api-key 'sk-ant-...'
# 또는
openclaw models auth paste-token --provider anthropic
```

---

## 🔄 Ubuntu에서 설정 업데이트 후 동기화

```bash
bash ~/openclaw-sync/sync-openclaw.sh
```

## ⬇️ MacBook에서 최신 설정 가져오기

```bash
cd ~/openclaw-sync && git pull
# workspace 파일들을 ~/.openclaw/workspace 에 복사
rsync -av ~/openclaw-sync/workspace/ ~/.openclaw/workspace/
```

---

## ⚠️ 직접 올리면 안 되는 것들

| 파일/폴더 | 이유 |
|---|---|
| `~/.openclaw/credentials/` | API 키, OAuth 토큰 |
| `~/.openclaw/auth-profiles.json` | 인증 정보 |
| `gateway.auth.token` (openclaw.json) | 게이트웨이 접속 토큰 |

Anthropic 등 API 인증은 각 기기에서 별도로 진행해야 합니다.
