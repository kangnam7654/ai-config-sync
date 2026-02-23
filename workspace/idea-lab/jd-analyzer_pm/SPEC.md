# SPEC: 주니어 서비스기획 JD 분석기 (JD Analyzer for Junior PMs)

## 1. 개요
채용 공고(JD)의 텍스트를 분석하여 주니어 기획자에게 필요한 핵심 역량, 키워드, 자소서/포트폴리오 대응 전략을 도출하는 웹 서비스.

## 2. 기술 스택
- **Frontend**: Next.js 14+ (App Router), Tailwind CSS
- **UI Components**: Shadcn UI (Lucide Icons)
- **Deployment**: Vercel (Free Tier)
- **AI/LLM**: 
  - 1단계: Client-side에서 LLM 프롬프트 생성 후 사용자 가이드 (직접 입력 유도)
  - 2단계: Gemini 1.5 Flash API (Free tier) 또는 사용자의 Ollama 로컬 연동 선택 가능하게 설계

## 3. 주요 화면 구성 (Single Page)
### [Section 1: Input]
- JD 텍스트 입력창 (Textarea)
- 도메인 선택 (커머스, 핀테크, 콘텐츠, 플랫폼, 기타)
- '분석하기' 버튼

### [Section 2: Analysis Results]
- **3줄 요약 카드**: 이 포지션의 핵심 한 문장 정의 + 예상 협업 부서 + 주요 성공 지표(KPI).
- **키워드 클러스터**: 문제정의, 데이터, 협업, 산출물 카테고리별 핵심 단어 강조.
- **체크리스트**: "자소서에 이 경험이 있나요?" 형식의 8~12개 문항.
- **함정 경고(Red Flags)**: JD에 숨겨진 리스크(예: 기획보다 운영 비중 높음) 고지.

## 4. 데이터 구조 (Prompt Schema)
LLM에게 요청할 JSON 출력 스키마:
```json
{
  "summary": { "role": "", "collab": "", "kpi": "" },
  "keywords": { "logic": [], "data": [], "process": [], "tools": [] },
  "checklist": [ { "item": "", "reason": "" } ],
  "warnings": [ "" ]
}
```

## 5. 단계별 구현 계획
- **Phase 1**: UI 퍼블리싱 + 기본 프롬프트 생성 로직
- **Phase 2**: LLM API 연동 (Gemini Flash)
- **Phase 3**: SEO 최적화 및 도메인별 랜딩 페이지 생성
