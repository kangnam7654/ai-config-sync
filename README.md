# AI Config Sync

Ubuntu ↔ MacBook ↔ Windows 간 OpenClaw + Claude Code 설정 양방향 동기화 저장소.

> **보안 주의:** API 키, 토큰 등 민감 정보는 이 레포에 포함되지 않습니다.

---

## 📁 구조

```
├── openclaw/                # OpenClaw 관련
│   ├── workspace/           # MEMORY.md, USER.md, SOUL.md 등 에이전트 워크스페이스
│   ├── openclaw.json        # OpenClaw 설정 파일
│   └── openclaw.template.json  # 설정 템플릿 (민감 값 제거됨)
├── claude-code/             # Claude Code 관련 (~/.claude/)
│   ├── CLAUDE.md            # 전역 지시사항
│   ├── settings.json        # Claude Code 설정
│   ├── agents/              # 커스텀 에이전트 정의
│   ├── memory/              # 전역 auto-memory
│   ├── agent-memory/        # 에이전트별 메모리
│   ├── plugins/             # 플러그인
│   ├── skills/              # 커스텀 스킬
│   ├── teams/               # 팀 설정
│   └── todos/               # TODO 목록
├── setup-mac.sh             # macOS 초기 설정 (최초 1회)
├── setup-windows.sh         # Windows 초기 설정 (Git Bash, 최초 1회)
└── sync.sh                  # 양방향 동기화 스크립트 (전 플랫폼)
```

---

## 🖥️ 초기 설정 (최초 1회)

### macOS / Ubuntu

```bash
git clone https://github.com/kangnam7654/ai-config-sync.git ~/projects/ai-config-sync
cd ~/projects/ai-config-sync
bash setup-mac.sh
```

### Windows (Git Bash)

> **필수:** [Git for Windows](https://gitforwindows.org/) + Python 설치

```bash
git clone https://github.com/kangnam7654/ai-config-sync.git ~/projects/ai-config-sync
cd ~/projects/ai-config-sync
bash setup-windows.sh
```

Task Scheduler가 자동 등록되며, 30분마다 동기화됩니다.

---

## 🔄 일상적인 동기화

```bash
# 모든 플랫폼 공통
bash sync.sh

# 흐름 예시
# [Mac에서 설정 수정]  →  bash sync.sh  →  GitHub
# [Ubuntu에서 받기]    →  bash sync.sh  →  자동 newest-wins 병합
# [Windows에서 받기]   →  bash sync.sh  →  자동 newest-wins 병합
```

---

## ⚠️ 직접 올리면 안 되는 것들

| 파일/폴더 | 이유 |
|---|---|
| `~/.openclaw/credentials/` | API 키, OAuth 토큰 |
| `~/.openclaw/auth-profiles.json` | 인증 정보 |
| `gateway.auth.token` (openclaw.json) | 게이트웨이 접속 토큰 |

Anthropic 등 API 인증은 각 기기에서 별도로 진행해야 합니다.
