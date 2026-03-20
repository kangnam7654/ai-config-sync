# MCP Gateway — Idea Forge 최종 리포트 (AI용)

> 이 문서는 LLM/AI 에이전트가 소비하는 것을 전제로, 구조화된 데이터와 정량적 지표를 중심으로 작성되었다.

---

## 메타데이터

```yaml
topic: "MCP 서버 개발 도구"
target_market: "B2B SaaS (규제산업 특화)"
final_product: "MCP Gateway — MCP 서버 프로덕션 거버넌스 레이어 SaaS"
phase_0: skipped (topic 제공됨)
phase_1_rounds: 2
phase_1_result: CSO Accept (Round 2)
phase_2_result: BM Score 7.5/10
```

---

## Phase 1: 아이디어 검증 루프 요약

### 라운드 흐름

| 라운드 | CEO 제안 핵심 | CSO 판정 | 주요 피벗 |
|--------|-------------|---------|----------|
| 1 | 범용 MCP 개발 올인원 SaaS (scaffolding→배포→모니터링 통합) | Rebuttal | 경쟁사(Postman/Speakeasy) 대비 차별화 부족 |
| 2 | 규제산업 전용 MCP 거버넌스 게이트웨이 (Visual Proof 특화) | Accept | 개발→운영, 범용→규제산업으로 이중 피벗 |

### 최종 제안 (Round 2 Accept)

```
제품명: MCP Gateway
카테고리: MCP 서버 프로덕션 거버넌스 SaaS
핵심 기능:
  1. 자동 감사 로그 + SOC2/HIPAA/GDPR 컴플라이언스 매핑
  2. RBAC + SSO/OAuth 2.1 통합
  3. 에이전트 행위 시각적 증적(Visual Proof) 대시보드
  4. 실시간 이상 탐지 + 비용 추적
배치 방식: 기존 MCP 서버 앞에 게이트웨이로 배치 (코드 변경 불필요)
타겟: 규제산업(금융/헬스케어/보험) 플랫폼 엔지니어링 + CISO + 컴플라이언스 팀
```

### CSO Accept 근거 (5개 기준)

```
시장_타당성: 긍정 — 7개 거버넌스 프레임워크 동시 출시, HIPAA 개정
실행_가능성: 긍정(조건부) — Visual Proof 기술적 도전, MCP+컴플라이언스 전문가 필요
리스크_수준: 관리가능 — MS/AWS 진출 리스크 있으나 Visual Proof gap으로 12~18개월 선점
경쟁_우위: 긍정 — Visual Proof(시장 0개), MCP 네이티브 게이트웨이, 코드 변경 불필요
재무적_잠재력: 긍정 — ACV $30K+, 규제산업 낮은 churn, LTV:CAC 7.5~18.8:1
```

---

## Phase 2: BM 설계 결과

### 수익 모델

```
프라이싱: 하이브리드 (플랫폼 기본료 + 사용량 과금)
  Starter: $499/월 + 50K 호출 포함
  Business: $1,999/월 + 500K 호출 포함
  Enterprise: 커스텀 ACV $50K~$150K
부가수익:
  컴플라이언스_패키지: $500~$2,000/월
  Visual_Proof_프리미엄: $300~$1,000/월
  프로페셔널_서비스: $200~$400/시간
```

### 유닛 이코노믹스

```
ARPU: $2,500/월 (blended)
ACV: $30,000
CAC: $8,000~$12,000
LTV: $90,000~$150,000
LTV_CAC_ratio: 7.5~18.8
CAC_payback_months: 3.2~4.8
gross_margin: 75~85%
```

### 5년 ARR 전망 (보수적)

```
Y1: $300K~$450K (10~15 고객)
Y2: $1.2M~$1.8M (40~60 고객)
Y3: $3M~$4.5M (100~150 고객)
Y4: $7.5M~$10.5M (250~350 고객)
Y5: $15M~$21M (500~700 고객)
```

### BM Score

```
시장_매력도: 8/10
차별화: 9/10
실행_가능성: 7/10
재무_건전성: 8/10
확장성: 7/10
리스크_관리: 6/10
종합: 7.5/10
```

---

## 핵심 리스크와 대응

| 리스크 | 심각도 | 대응 |
|--------|--------|------|
| MS/AWS 매니지드 MCP 거버넌스 진출 | 높음 | Visual Proof + 규제 도메인 전문성 + 조기 레퍼런스로 switching cost 형성 |
| MCP 프로토콜 대규모 변경 | 중간 | Working Group 참여 + 프록시 엔진 모듈화 |
| 규제산업 긴 세일즈 사이클 | 중간 | Starter 티어로 비규제 고객 조기 확보, 캐시플로우 안정화 |
| Visual Proof 기술 구현 난이도 | 중간 | MVP는 시퀀스 다이어그램 수준, 점진적 고도화 |
| 경쟁사 모방 | 낮음~중간 | 특허 출원 + 규제산업 레퍼런스 축적 |

---

## 경쟁 구도 맵

```
코드_생성(레드오션):
  - Speakeasy: OpenAPI→MCP 변환+SDK
  - Stainless: OpenAPI→MCP 생성
  - Postman: 범용 API 도구+MCP 추가
  - FastMCP: 오픈소스 Python 프레임워크

거버넌스(블루오션→경쟁 형성 중):
  - Microsoft mcp-gateway: 오픈소스, K8s 프록시 (매니지드 X)
  - Ithena SDK: RBAC/감사 (SDK 방식, 코드 수정 필요)
  - Obot: 관리형 게이트웨이 (규제 특화 X)
  - MCP Gateway(우리): Visual Proof + 컴플라이언스 자동 매핑 + 코드변경 불필요
```

---

## 시장 데이터 출처

- MCP 시장: $1.8B(2025) — [CData](https://www.cdata.com/blog/2026-year-enterprise-ready-mcp-adoption)
- AI SaaS: $30.33B(2026) — [Fortune Business Insights](https://www.fortunebusinessinsights.com/ai-saas-market-111182)
- MCP 채택: 800만+ 서버 다운로드, Fortune 500 다수 배포 — [Wikipedia](https://en.wikipedia.org/wiki/Model_Context_Protocol)
- Visual Proof 부재 지적 — [DEV Community](https://dev.to/custodiaadmin/enterprise-mcp-governance-is-here-and-its-missing-visual-proof-235k)
- DevTools ARPU $847/월 — [DollarPocket](https://www.dollarpocket.com/saas-pricing-benchmarks-guide-report)
- Infrastructure SaaS Churn 1.8% — [WeAreFounders](https://www.wearefounders.uk/saas-churn-rates-and-customer-acquisition-costs-by-industry-2025-data/)
- 하이브리드 프라이싱 43%→61% — [ZeonEdge](https://zeonedge.com/is/blog/saas-pricing-strategies-2026-usage-based-seat-hybrid)
- 규제산업 15~30% 프리미엄 — Deloitte
- MCP 2026 로드맵 — [MCP Blog](http://blog.modelcontextprotocol.io/posts/2026-mcp-roadmap/)

---

## 다음 단계

```
P0:
  - MVP 스펙 정의 (MCP 프록시 + 감사 로그 + 기본 RBAC) — 2주
  - 규제산업 CISO 5인 인터뷰 — 3주
P1:
  - Visual Proof PoC (도구 호출 체인 시각화) — 6주
  - SOC2 Type II 자체 인증 로드맵 — 4주
P2:
  - 시드 라운드 자료 준비 — 4주
  - Vanta/Drata 파트너십 논의 — 6주
```
