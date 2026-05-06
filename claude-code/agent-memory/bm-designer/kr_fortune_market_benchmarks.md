---
name: Korea Saju/Fortune App Market Benchmarks
description: Korean fortune-telling app market data - 점신/포스텔러/신운세 monetization patterns, market size, ARPU (2024-2026)
type: reference
---

## Market Size (Korea, 2024-2026)
- Total fortune-telling market: 약 1.4조원 (혁신의숲, 2024.05)
- 10-39세 1인당 평균 소비: ~80,300원/년
- 2030 사용자 비중: 80%
- MoM 거래액 YoY: +30%

## Major Players
| App | Users | 2024 Revenue | OP Margin | Monetization |
|---|---|---|---|---|
| 점신 (TechLabs) | 1,900만 누적 DL | 978억원 | ~12% | 광고 강제(5-7초)+상담사 매칭 (B2C2B 마진), 기본 풀이 무료 |
| 포스텔러 (un7qi3) | 860만 가입자 | 비공개 | -- | 포스(point) 단건 결제, 100-200쪽 상세 풀이 패키지 |
| 신운세 | 비공개 | 비공개 | -- | 연간 구독 (7종 운세 무제한, 가격 비공개) |
| 마이파이 | 비공개 | -- | -- | 전화상담 중심 (1시간 단위) |

## Monetization Pattern
- **광고 게이팅**: 점신 = 모든 콘텐츠 강제 광고 5-7초. ARPU 핵심은 광고+상담사 매칭 마진 (단건 결제 비주류).
- **포인트 단건**: 포스텔러 = 가벼운 리포트~큰 패키지 단계별, 가입 시 1건 무료
- **구독**: 신운세 = 7종/1년 무제한 (가격 비공개, 19,900-49,000원 추정)
- **상담사 매칭**: 점신·마이파이·포스텔러 모두 운영. 회당 3만원~. 사주앱의 진짜 ARPU 엔진은 단건 풀이가 아니라 상담 redirect.

## Key Insights for Pricing
- 포인트팩이 단가 anchor를 의도적으로 흐림 (5,500원/11,000원 패키지 → 풀이당 가격 의도적으로 모호)
- 점집 오프라인 사주풀이 = 회당 30,000원 (SNS 비대면 동일)
- 신년운세 단건 anchor: 무료 freemium 다수 (신한라이프/농협/네이트/KB), 유료 단건 풀이 추정 5,000-15,000원
- 사용자 review: "사주는 포스텔러가 가장 낫다", "점신은 안맞아도 습관처럼 봄"
- 2030 강한 PMF, 점술 = 놀이문화화 (자기탐색 도구)

## Implication for 달결 SKU Design
1. 단건 영구 unlock 모델은 시장에서 검증됨 (포스텔러 패턴)
2. 직접 단가 노출보다 포인트팩 패킹이 결제 마찰 낮춤
3. 광고 보상 + 출석 보너스로 무료 사용자도 retention (점신 패턴 차용 가능)
4. 시간 운(세운/월운/일운)은 갱신 주기 짧아 영구 unlock 부적합 → 시기 인코딩 또는 구독
5. 일운은 매일 결제 마찰 너무 큼 → 광고시청 free 또는 월구독으로만 의미
