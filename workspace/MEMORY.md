# MEMORY.md - Long-Term Context
**User:** Kangnam (강남)
**Assistant:** Mori (모리)
**Started:** 2026-02-01
## Key Preferences
- **Honesty:** Values unvarnished truth over politeness. No sugarcoating.
- **Language:** Korean.
- **Communication:** Honest and direct to avoid errors, but maintains basic courtesy. Professional colleague vibe.
- **Local LLM:** Prefer using **Ollama `glm-4.7-flash`** by default (when feasible).
- **Tools:** **No Opencode.** Coding tasks via Opencode are discontinued.
## Ongoing Context
### Project: App Factory (autonomous local-first)
- **Goal:** “완전 자율 회사”처럼 주기적으로 작동 가능한 앱 산출 + 자동 리포트(텔레그램).
- **Repo:** `~/projects/app-factory`
- **Core flow:** 아이디어 → 비즈니스 타당성 게이트(통과 못하면 생산 없이 종료 허용) → 스펙 1pager → 빌드 → QA → 리포트.
- **Status:** Opencode usage discontinued due to instability (SIGKILL).
- **Blocked:** Previously blocked by Opencode SIGKILL issues; workflow needs reassessment without Opencode.
### Project: Offline Photo Translator App (Edge)
- **Goal:** 사진/카메라 입력 → OCR → (JA/EN→KO) 번역 → 원본 위 오버레이 (완전 오프라인)
- **Target:** Android + iOS
- **Path:** `~/projects/offline-translate-app`
- **Approved stack:** Flutter(UI) + Rust/C++ core + ONNX Runtime
- **Docs policy:** 개발 중 지속 업데이트, **한국어로 작성**
### Project: Company OS (company_simulator)
- **Goal:** 로컬 모델 기반으로 24시간 구동 가능한 ‘에이전트 팀/회사 시스템’
- **Path:** `~/projects/company_simulator`
- **Tech:** LangGraph + Postgres + Ollama(JSON schema 강제)
- **Org:** 도메인 에이전트가 자율 티켓 생성, CTO는 조율/방향 제시(옵션)
- **Note:** Ollama JSON timeout 이슈가 있어 타임아웃/프롬프트/실행 로깅 개선 중
### Project: Meme Translator
- **Goal:** Reddit 개발자 밈 수집 → 자동 한글 번역/합성 → 인스타그램 업로드 (수익화: 광고/홍보)
- **Status:** 2026-02-05 기준 **폐기/보류** (업로드 자동화 병목).
- **Path:** `~/projects/meme-translator`
- **Tech Stack:** Python, EasyOCR, SimpleLama, Qwen3-VL (Local), Pillow.
- **Tone:** 시니컬한 팩폭러 (개발자 유머).
- **Postmortem:** `~/projects/meme-translator/POSTMORTEM.md`
- **What happened:**
  - Reddit는 API 키 없이 JSON 엔드포인트(top.json)로 수집 가능하게 조정.
  - 파이프라인(생성/캡션)까지는 성공했으나, Instagram 업로드에서 `instagrapi` 로그인이 지속적으로 차단(HTTP 400 → BadPassword).
  - 공식 Instagram Graph API는 외부 `image_url`(스토리지/터널/서버) + FB Page 연결/토큰 설정이 필요해, 비용/운영 복잡도 때문에 중단.
## Archived / On Hold
### Meme Factory v2 (Agentic Workflow) — 아이디어 보관
- 프로젝트가 현재 **폐기/보류**라서 당장 진행하지 않음.
- 다만 품질 문제(과번역/검수 부재) 해결 아이디어로 아래 구조는 유효:
  1) **Editor:** OCR 결과 중 번역할 핵심 텍스트만 선별(JSON)
  2) **Designer:** 선별 텍스트만 지우고 번역어 합성
  3) **QC:** 결과물 1~5점 평가, 기준 미달이면 retry/discard
(구 opencode 프롬프트는 필요 시 `memory/2026-02-05.md` 및 프로젝트 `POSTMORTEM.md`를 참고)
