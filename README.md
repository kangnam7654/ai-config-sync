# AI Config Sync

Ubuntu ↔ MacBook Pro 간 OpenClaw + Claude Code 설정 양방향 동기화 저장소.

> **보안 주의:** API 키, 토큰 등 민감 정보는 이 레포에 포함되지 않습니다.

---

## 📁 구조

```
├── workspace/               # MEMORY.md, USER.md, SOUL.md 등 에이전트 워크스페이스
├── claude-code/             # Claude Code 설정 (~/.claude 동기화)
├── openclaw.template.json   # 설정 템플릿 (민감 값 제거됨)
├── setup-mac.sh             # 맥북 초기 설정 자동화 스크립트 (최초 1회)
└── sync.sh                  # 양방향 동기화 스크립트
```

---

## 🖥️ MacBook에서 처음 설정할 때 (최초 1회)

```bash
git clone https://github.com/kangnam7654/ai-config-sync.git ~/projects/ai-config-sync
cd ~/projects/ai-config-sync
bash setup-mac.sh

# Anthropic 인증
openclaw onboard --anthropic-api-key 'sk-ant-...'
```

---

## 🔄 일상적인 동기화

### 현재 기기 변경사항 → GitHub (push)
```bash
# Ubuntu 또는 MacBook 어디서든
bash sync.sh
```

### 흐름 예시
```
[MacBook에서 MEMORY.md 수정]
  bash sync.sh        # Mac → GitHub

[Ubuntu에서 변경 내용 받기]
  bash sync.sh        # GitHub → Ubuntu (자동 양방향)
```

---

## ⚠️ 직접 올리면 안 되는 것들

| 파일/폴더 | 이유 |
|---|---|
| `~/.openclaw/credentials/` | API 키, OAuth 토큰 |
| `~/.openclaw/auth-profiles.json` | 인증 정보 |
| `gateway.auth.token` (openclaw.json) | 게이트웨이 접속 토큰 |

Anthropic 등 API 인증은 각 기기에서 별도로 진행해야 합니다.
