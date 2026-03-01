---
name: transport-search
description: 브라우저를 직접 열어 항공권, 기차, 고속버스, 배편 등 모든 교통편을 실시간 검색하고 스크린샷으로 결과를 확인하는 스킬. 출발지/목적지/날짜/인원을 받아 최적 교통편을 찾을 때 사용. 항공권 가격 비교, 열차 시간표, 고속버스 예약, 페리 운항 조회 등 모든 교통 관련 검색에 트리거. "비행기 찾아줘", "기차편 알아봐", "배편 있어?", "이동 방법 검색해줘" 등의 요청에 사용.
---

# Transport Search

브라우저 자동화로 실시간 교통편을 검색한다. 모든 결과는 스크린샷으로 확인.

## 공통 워크플로우

1. 출발지 / 목적지 / 날짜 / 인원 확인 (없으면 물어보기)
2. 교통편 유형 판단 → 해당 사이트 열기
3. 페이지 로딩 기다린 후 스크린샷
4. 결과 읽어서 가격/시간/항공사 등 요약 전달
5. 필요시 날짜 바꿔 재검색 비교

## 교통편별 검색 사이트

### ✈️ 항공권

**국제선 (스카이스캐너)**
```
https://www.skyscanner.co.kr/transport/flights/{출발IATA}/{도착IATA}/{YYMMDD출발}/{YYMMDD귀국}/?adults={인원}&cabinclass=economy
```
예: ICN→OKA, 2인, 4/17 출발 4/20 귀국
→ `https://www.skyscanner.co.kr/transport/flights/ICN/OKA/260417/260420/?adults=2&cabinclass=economy`

**국내선 (네이버 항공)**
```
https://flight.naver.com/flights/domestic/{출발공항}-{도착공항}-{YYYYMMDD}?adult={인원}
```

**주요 IATA 코드 참고:** → `references/iata-codes.md`

### 🚄 기차 (KTX/ITX/무궁화)

**코레일 승차권 조회**
```
https://www.korail.com/ticket/main
```
- 검색창에 출발역 / 도착역 / 날짜 입력 필요 → 브라우저 `act` 사용
- 또는 레츠코레일 앱이 더 빠를 수 있음

**네이버 기차 조회 (더 간편)**
```
https://search.naver.com/search.naver?query={출발역}+{도착역}+기차+{날짜}
```

### 🚌 고속버스/시외버스

**고속버스 통합예매**
```
https://www.kobus.co.kr/web/reservation/step1.do
```

**네이버 버스 조회**
```
https://search.naver.com/search.naver?query={출발지}+{도착지}+고속버스+{날짜}
```

### ⛴️ 배편 (페리)

**국내 여객선**
```
https://www.ferry.or.kr (한국해운조합)
```

**일본 페리 (부산→후쿠오카 등)**
```
https://www.camellia-line.co.kr (카멜리아라인)
https://www.panstarline.co.kr (팬스타라인)
```

**제주 배편**
```
https://search.naver.com/search.naver?query=제주+배편+{날짜}
```

## 브라우저 사용 요령

- `profile: openclaw` 사용
- 페이지 로딩 후 **2~3초 대기** 후 screenshot
- 로그인 팝업 뜨면 `act`으로 닫기 또는 무시하고 뒤 결과 읽기
- 캡챠 막히면 → 네이버 항공이나 다른 사이트로 전환
- 결과가 JS 렌더링이라 web_fetch 안됨 → 반드시 브라우저 사용

## 결과 전달 형식

검색 후 아래 형식으로 요약:

```
[항공사/교통사] 출발시간 → 도착시간 (소요시간)
가격: ₩XXX,XXX (1인 / 왕복)
경유: 있음/없음
```

여러 옵션이 있으면 **최저가 3개** 위주로 정리.  
날짜별 가격 차이가 있으면 비교표도 제공.

## 주의사항

- 스카이스캐너는 **성인 수(adults)** URL 파라미터로 제어 가능
- 코레일/고속버스는 직접 폼 조작 필요 → `act` 사용
- 가격은 실시간 변동 → 캡처 시점 기준임을 고지
- 국제운전면허 필요 여부 등 부가정보도 함께 안내
