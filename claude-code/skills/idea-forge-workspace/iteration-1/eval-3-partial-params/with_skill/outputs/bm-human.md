# MCP Gateway -- 사업 아이디어 검증 및 BM 설계 리포트

## 한 줄 요약

**MCP 서버의 프로덕션 거버넌스를 자동화하는 B2B SaaS.** 규제산업 기업이 AI 에이전트의 도구 호출을 감사하고, 컴플라이언스를 증명하고, "에이전트가 실제로 무엇을 했는지" 시각적으로 보여줄 수 있게 한다.

---

## 1. 아이디어 검증 과정

### 어떻게 이 아이디어에 도달했나

처음에는 "MCP 서버 개발 도구를 올인원 SaaS로 만들자"라는 범용 접근을 시도했다. 코드 생성부터 배포, 모니터링까지 전체 수명주기를 하나로 묶는 플랫폼이었다.

그러나 조사 결과, 이미 Postman, Speakeasy, FastMCP 등 강력한 플레이어들이 MCP 서버 "생성" 영역에 진출해 있었다. 스타트업이 이들과 정면 경쟁하는 것은 불리했다.

핵심 발견은 이것이었다: **MCP 서버를 "만드는" 것보다 "운영하면서 감사하는" 것이 더 큰 문제다.** 2026년 초, 7개의 엔터프라이즈 거버넌스 프레임워크가 동시에 등장할 만큼 이 영역의 수요가 폭발하고 있었다. 그리고 이 7개 솔루션 모두 "에이전트가 실제로 무엇을 했는지 시각적으로 증명하는 기능(Visual Proof)"을 갖추지 못했다.

이 gap에 집중하여 **"규제산업 전용 MCP 거버넌스 게이트웨이"**로 피벗했고, 전략 검증을 통과했다.

### 검증 요약

| 항목 | 평가 |
|------|------|
| 시장 크기 | AI SaaS 보안/거버넌스 $3~5B, MCP 시장 $1.8B(2025) |
| 경쟁 구도 | 거버넌스 시장 형성 초기. MS 오픈소스 존재하나 매니지드 서비스 부재 |
| 차별화 | Visual Proof (시장 유일), 코드 변경 없는 게이트웨이 패턴 |
| 타이밍 | 엔터프라이즈 MCP 채택 본격화 + HIPAA 보안 규칙 강화 |
| 리스크 | MS/AWS의 매니지드 서비스 진출 가능성 (12~18개월 선점 기회) |

---

## 2. 제품 설명

### MCP Gateway란?

기존 MCP 서버 앞에 배치하는 "거버넌스 레이어"다. 개발팀이 기존 MCP 서버 코드를 전혀 수정하지 않아도 된다.

제공 기능:
1. **자동 감사 로그**: 모든 도구 호출을 기록하고, SOC2/HIPAA/GDPR 컨트롤에 자동 매핑
2. **접근 제어**: 역할별로 어떤 도구를 사용할 수 있는지 관리 (RBAC + SSO)
3. **Visual Proof**: AI 에이전트의 도구 호출 체인을 시각적으로 재구성하여 감사인에게 제시 -- "에이전트가 실제로 무엇을 했는지" 증명
4. **실시간 모니터링**: 이상 행위 탐지, 비용 추적, 성능 대시보드

### 누구를 위한 제품인가?

- **1차 타겟**: 금융, 헬스케어, 보험 등 규제산업의 플랫폼 엔지니어링 팀 + CISO + 컴플라이언스 팀
- **2차 타겟**: SOC2 인증이 필요한 B2B SaaS 기업

### 왜 지금인가?

- MCP가 AI 에이전트의 사실상 표준이 됨 (OpenAI, Google, Microsoft 모두 채택)
- 2026년이 엔터프라이즈 MCP 본격 채택의 해
- HIPAA 보안 규칙이 2003년 이후 최대 규모로 개정 중 -- 암호화, MFA 의무화
- "에이전트가 뭘 했는지 보여줄 수 없다"는 것이 업계 공통 문제로 지적됨

---

## 3. 비즈니스 모델

### 가격 체계

| 플랜 | 월 가격 | 포함 범위 | 대상 |
|------|---------|----------|------|
| Starter | $499 | MCP 호출 5만 건, 기본 감사 로그 | SOC2 준비 중인 스타트업 |
| Business | $1,999 | MCP 호출 50만 건, 컴플라이언스 매핑 | 중견 기업 |
| Enterprise | 연 계약 $50K~$150K | 무제한, 전용 배포, 전담 지원 | 규제산업 대기업 |

추가 수익: 컴플라이언스 패키지($500~$2,000/월), Visual Proof 프리미엄($300~$1,000/월), 컨설팅($200~$400/시간)

### 핵심 재무 지표

| 지표 | 수치 | 의미 |
|------|------|------|
| 평균 고객 연 매출 | $30,000 | 건전한 B2B SaaS 수준 |
| 고객 획득 비용 | $8,000~$12,000 | 엔터프라이즈 보안 SaaS 평균 |
| 고객 생애 가치 | $90,000~$150,000 | 규제산업의 낮은 이탈률 반영 |
| LTV:CAC 비율 | 7.5~18.8 | 매우 건전 (기준: 3 이상) |
| 투자금 회수 기간 | 3.2~4.8개월 | 빠른 편 (기준: 12개월 미만) |

### 5년 성장 로드맵

| 연도 | 고객 수 | 연 매출 | 마일스톤 |
|------|---------|---------|---------|
| 1년 차 | 10~15 | $300K~$450K | MVP 출시, 금융 POC |
| 2년 차 | 40~60 | $1.2M~$1.8M | 시드 라운드, 레퍼런스 확보 |
| 3년 차 | 100~150 | $3M~$4.5M | 시리즈A, 채널 파트너십 |
| 4년 차 | 250~350 | $7.5M~$10.5M | 시리즈B, EU 진출 |
| 5년 차 | 500~700 | $15M~$21M | 수익성 달성 |

---

## 4. BM Score: 7.5/10

| 평가 항목 | 점수 | 한 줄 근거 |
|----------|------|----------|
| 시장 매력도 | 8 | MCP 엔터프라이즈 채택 본격화, 거버넌스 수요 폭발 |
| 차별화 | 9 | Visual Proof는 시장 유일, MCP 네이티브 게이트웨이 |
| 실행 가능성 | 7 | 기술적 도전 있으나 구현 가능, 팀 구성이 관건 |
| 재무 건전성 | 8 | LTV:CAC 우수, 규제산업 낮은 이탈률 |
| 확장성 | 7 | 규제산업 -> SOC2 기업 -> 글로벌 확장 경로 명확 |
| 리스크 관리 | 6 | MS/AWS 진출 리스크 존재, 12~18개월 선점이 핵심 |

---

## 5. 핵심 리스크와 대응

### 리스크 1: MS/AWS가 매니지드 MCP 거버넌스를 출시하면?
- **심각도**: 높음
- **대응**: Visual Proof + 규제산업 도메인 전문성은 범용 플랫폼이 쉽게 모방하기 어려운 영역. 조기에 금융/헬스케어 레퍼런스를 확보하여 switching cost를 형성한다.

### 리스크 2: MCP 프로토콜이 크게 변경되면?
- **심각도**: 중간
- **대응**: MCP Working Group에 적극 참여하여 변경 사항을 미리 파악하고, 프록시 엔진을 모듈화하여 업데이트를 용이하게 한다.

### 리스크 3: 규제산업 영업이 오래 걸리면?
- **심각도**: 중간
- **대응**: Starter 티어($499/월)로 비규제 B2B SaaS 고객을 먼저 확보하여 캐시플로우를 안정시키고, 규제산업은 POC를 통해 진입한다.

### 리스크 4: Visual Proof 기술 구현이 어려우면?
- **심각도**: 중간
- **대응**: MVP에서는 도구 호출의 시퀀스 다이어그램 수준으로 시작한다. 감사인과 직접 피드백 루프를 구축하여 필요한 수준을 점진적으로 파악한다.

---

## 6. 경쟁 환경

### MCP 서버 "생성" 도구 (우리가 경쟁하지 않는 영역)
- **Speakeasy**: OpenAPI에서 MCP 서버 자동 생성 + SDK 통합
- **Postman**: 기존 API 도구의 지배자, MCP 기능 추가
- **FastMCP**: 오픈소스 Python 프레임워크, 커뮤니티 성장 중

### MCP 서버 "거버넌스" 도구 (우리가 경쟁하는 영역)
- **Microsoft mcp-gateway**: 오픈소스 K8s 프록시. 매니지드 서비스 아님, 컴플라이언스 매핑 없음
- **Ithena SDK**: RBAC/감사 제공하지만 SDK 방식이라 코드 수정 필요
- **Obot**: 관리형 게이트웨이이나 규제산업 특화 기능 불명확

### 우리의 포지셔닝
"코드 변경 없이 배치하는 MCP 거버넌스 게이트웨이 + 시장 유일의 Visual Proof"

---

## 7. 다음 단계

### 즉시 실행 (P0)
1. **MVP 스펙 정의** -- MCP 프록시 + 감사 로그 + 기본 RBAC (2주)
2. **규제산업 CISO 인터뷰 5건** -- 거버넌스 pain point 검증 (3주)

### 단기 (P1)
3. **Visual Proof PoC** -- 도구 호출 체인 시각화 프로토타입 (6주)
4. **SOC2 Type II 인증 로드맵** 수립 (4주)

### 중기 (P2)
5. **시드 라운드 준비** -- 피치 덱 + 재무 모델 (4주)
6. **파트너십 논의** -- Vanta/Drata 컴플라이언스 자동화 도구와 통합 (6주)

---

## 출처

- [CData - 2026: The Year for Enterprise-Ready MCP Adoption](https://www.cdata.com/blog/2026-year-enterprise-ready-mcp-adoption)
- [Fortune Business Insights - AI SaaS Market](https://www.fortunebusinessinsights.com/ai-saas-market-111182)
- [DEV Community - Enterprise MCP Governance Is Here and It's Missing Visual Proof](https://dev.to/custodiaadmin/enterprise-mcp-governance-is-here-and-its-missing-visual-proof-235k)
- [MCP Blog - 2026 Roadmap](http://blog.modelcontextprotocol.io/posts/2026-mcp-roadmap/)
- [Wikipedia - Model Context Protocol](https://en.wikipedia.org/wiki/Model_Context_Protocol)
- [Speakeasy - MCP Server Generators Comparison](https://www.speakeasy.com/blog/comparison-mcp-server-generators)
- [Composio - 10 Best MCP Gateways 2026](https://composio.dev/content/best-mcp-gateway-for-developers)
- [GitHub - Ithena Governance SDK](https://github.com/ithena-one/mcp-governance-sdk)
- [GitHub - Microsoft MCP Gateway](https://github.com/microsoft/mcp-gateway)
- [DollarPocket - SaaS Pricing Benchmarks](https://www.dollarpocket.com/saas-pricing-benchmarks-guide-report)
- [WeAreFounders - SaaS Churn Rates by Industry](https://www.wearefounders.uk/saas-churn-rates-and-customer-acquisition-costs-by-industry-2025-data/)
- [SaaS Hero - LTV:CAC Ratio Benchmarks](https://www.saashero.net/customer-retention/b2b-saas-ltv-cac-ratio/)
- [ZeonEdge - SaaS Pricing Strategies 2026](https://zeonedge.com/is/blog/saas-pricing-strategies-2026-usage-based-seat-hybrid)
