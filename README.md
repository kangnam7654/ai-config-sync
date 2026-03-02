# AI Config Sync

Ubuntu ↔ MacBook ↔ Windows 간 OpenClaw + Claude Code 설정 양방향 동기화 저장소.

> **보안 주의:** 민감 정보는 템플릿/로컬 파일로 분리해 관리합니다. `openclaw/openclaw.json`은 추적하지 않습니다.

---

## 📁 구조

```
├── openclaw/                # OpenClaw 관련
│   ├── workspace/           # MEMORY.md, USER.md, SOUL.md 등 에이전트 워크스페이스
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
├── setup-mac.sh             # macOS/Ubuntu 초기 설정 (최초 1회)
├── setup-windows.sh         # Windows 초기 설정 (Git Bash, 최초 1회)
└── sync.sh                  # 양방향 동기화 스크립트 (전 플랫폼)
```

---

## 🖥️ 플랫폼별 동기화 범위

| 플랫폼 | OpenClaw | Claude Code |
|---|---|---|
| macOS (개인) | ✅ | ✅ |
| Ubuntu (개인) | ✅ | ✅ |
| Windows (회사) | ❌ | ✅ |

> Windows는 회사 보안 정책상 Claude Code 설정만 동기화합니다.
> OpenClaw 디렉토리(`~/.openclaw`)가 없으면 자동으로 건너뜁니다.

---

## 🛠️ 초기 설정 (최초 1회)

### macOS / Ubuntu

```bash
git clone https://github.com/kangnam7654/ai-config-sync.git ~/projects/ai-config-sync
cd ~/projects/ai-config-sync
bash setup-mac.sh

# Anthropic 인증
openclaw onboard --anthropic-api-key 'sk-ant-...'
```

`setup-mac.sh`는 템플릿(`openclaw/openclaw.template.json`)에서 로컬 `~/.openclaw/openclaw.json`을 생성합니다.

### Windows (Git Bash)

> **필수:** [Git for Windows](https://gitforwindows.org/) + [Python](https://python.org) 설치

```bash
git clone https://github.com/kangnam7654/ai-config-sync.git ~/projects/ai-config-sync
cd ~/projects/ai-config-sync
bash setup-windows.sh
```

Claude Code 설정이 복원되고, Task Scheduler(30분 간격)가 자동 등록됩니다.

---

## 🔄 일상적인 동기화

```bash
# 모든 플랫폼 공통
bash sync.sh

# 흐름 예시
# [Mac에서 설정 수정]     →  bash sync.sh  →  GitHub
# [Ubuntu에서 받기]       →  bash sync.sh  →  자동 newest-wins 병합
# [Windows에서 받기]      →  bash sync.sh  →  Claude Code 설정만 동기화
```

---

## ⚠️ 직접 올리면 안 되는 것들

| 파일/폴더 | 이유 |
|---|---|
| `openclaw/openclaw.json` | 실환경 토큰/프로필 포함 가능 (레포에서 추적 금지) |
| `~/.openclaw/credentials/` | API 키, OAuth 토큰 |
| `~/.openclaw/auth-profiles.json` | 인증 정보 |
| `gateway.auth.token` (openclaw.json) | 게이트웨이 접속 토큰 |

Anthropic 등 API 인증은 각 기기에서 별도로 진행해야 합니다.

이미 토큰이 레포 이력에 노출된 적이 있다면 즉시 재발급/폐기하세요.
