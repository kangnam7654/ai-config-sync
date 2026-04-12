# Transport Search Reference

브라우저 자동화로 실시간 교통편을 검색한다. 모든 결과는 스크린샷으로 확인.

## Out of Scope

- 렌터카/택시 예약
- 호텔/숙소 검색 (→ planning.md)
- 여행 보험
- 실시간 가격 알림
- 국제운전면허 발급
- 해외 현지 교통 (신칸센, TGV, 유럽 철도 등 — 한국 출발/도착 구간만 담당)

## 공통 워크플로우

1. 출발지 / 목적지 / 날짜 / 인원 확인 (없으면 물어보기)
2. **편도/왕복 확인** — 언급 없으면 왕복 기본값, 편도면 URL/폼에 반영
3. 교통편 유형 판단 → 해당 사이트 열기
4. 페이지 로딩 기다린 후 `agent-browser screenshot`
5. 결과 읽어서 가격/시간/항공사 요약 전달
6. 날짜 바꿔 재검색 비교

## 교통편별 검색 사이트

### 항공권

**국제선 (스카이스캐너)**

왕복:
```
https://www.skyscanner.co.kr/transport/flights/{출발IATA}/{도착IATA}/{YYMMDD출발}/{YYMMDD귀국}/?adults={인원}&cabinclass=economy
```
편도 (귀국 날짜 생략):
```
https://www.skyscanner.co.kr/transport/flights/{출발IATA}/{도착IATA}/{YYMMDD출발}/?adults={인원}&cabinclass=economy
```
예: ICN→OKA, 2인, 4/17 출발 4/20 귀국
→ `https://www.skyscanner.co.kr/transport/flights/ICN/OKA/260417/260420/?adults=2&cabinclass=economy`

**국내선 (네이버 항공)**
```
https://flight.naver.com/flights/domestic/{출발공항}-{도착공항}-{YYYYMMDD}?adult={인원}
```

**주요 IATA 코드 참고:** → `travel/references/iata-codes.md`

### 기차 (KTX/SRT/ITX/무궁화)

출발역이 **수서**이거나 사용자가 SRT를 명시하면 → SRT 검색. 그 외 → 코레일 검색.

**SRT 승차권 조회**
```
https://etk.srail.kr/hpg/hra/01/selectScheduleList.do
```
브라우저 자동화 단계:
1. 페이지 로딩 후 3초 대기 → `agent-browser screenshot`으로 폼 구조 확인
2. 출발역 입력: `agent-browser click` 출발역 필드 → `agent-browser fill` 역 이름 (예: "수서") → 자동완성에서 선택
3. 도착역 입력: `agent-browser click` 도착역 필드 → `agent-browser fill` 역 이름 (예: "부산") → 자동완성에서 선택
4. 날짜 선택: 캘린더에서 원하는 날짜 `agent-browser click`
5. `agent-browser click` "조회하기" 버튼 → 3초 대기 → `agent-browser screenshot`으로 결과 확인
6. 결과가 안 보이면 → 네이버 기차 조회로 폴백

**코레일 승차권 조회**
```
https://www.korail.com/ticket/main
```
브라우저 자동화 단계:
1. 페이지 로딩 후 3초 대기 → `agent-browser screenshot`으로 폼 구조 확인
2. 출발역 입력: `agent-browser click` 출발역 필드 → `agent-browser fill` 역 이름 (예: "서울") → 자동완성 드롭다운에서 `agent-browser click`으로 선택
3. 도착역 입력: `agent-browser click` 도착역 필드 → `agent-browser fill` 역 이름 (예: "부산") → 자동완성 드롭다운에서 `agent-browser click`으로 선택
4. 날짜 선택: `agent-browser click` 날짜 영역 → 캘린더 팝업에서 원하는 날짜 `agent-browser click`
5. 인원 변경 시: "어른" 옆 +/- 버튼 `agent-browser click`
6. `agent-browser click` "조회하기" 버튼 → 3초 대기 → `agent-browser screenshot`으로 결과 확인
7. 결과가 안 보이면 → 네이버 기차 조회로 폴백

**네이버 기차 조회 (더 간편, 폴백용)**
```
https://search.naver.com/search.naver?query={출발역}+{도착역}+기차+{날짜}
```

### 고속버스/시외버스

**고속버스 통합예매 (코버스)**
```
https://www.kobus.co.kr/web/reservation/step1.do
```
브라우저 자동화 단계:
1. 페이지 로딩 후 3초 대기 → `agent-browser screenshot`으로 폼 구조 확인
2. 출발지 입력: `agent-browser click` 출발지 필드 → `agent-browser fill` 터미널명 (예: "서울경부") → 자동완성 목록에서 `agent-browser click`으로 선택
3. 도착지 입력: `agent-browser click` 도착지 필드 → `agent-browser fill` 터미널명 (예: "동대구") → 자동완성 목록에서 `agent-browser click`으로 선택
4. 날짜 선택: `agent-browser click` 날짜 영역 → 캘린더에서 원하는 날짜 `agent-browser click`
5. `agent-browser click` "조회" 버튼 → 3초 대기 → `agent-browser screenshot`으로 결과 확인
6. 결과 로딩 실패 시 → 네이버 버스 조회로 폴백

**네이버 버스 조회 (폴백용)**
```
https://search.naver.com/search.naver?query={출발지}+{도착지}+고속버스+{날짜}
```

### 배편 (페리)

**국내 여객선**
```
https://www.ferry.or.kr (한국해운조합)
```

**일본 페리 (부산→후쿠오카)**
```
https://www.camellia-line.co.kr (카멜리아라인)
https://www.panstarline.co.kr (팬스타라인)
```

**제주 배편**
```
https://search.naver.com/search.naver?query=제주+배편+{날짜}
```

## 브라우저 사용 요령

- `agent-browser open --profile openclaw <url>` — openclaw 프로필을 사용해야 쿠키/세션이 유지되어 로그인 팝업을 줄일 수 있다
- 페이지 로딩 후 **2~3초 대기** 후 `agent-browser screenshot`
- 로그인 팝업 뜨면 `agent-browser click`으로 닫기 또는 무시하고 뒤 결과 읽기
- 캡챠 막히면 → 네이버 항공이나 다른 사이트로 전환
- 결과가 JS 렌더링이라 `WebFetch` 안됨 → 반드시 `agent-browser` 사용

## 결과 전달 형식

검색 후 아래 형식으로 요약:

```
[항공사/교통사] 출발시간 → 도착시간 (소요시간)
가격: ₩XXX,XXX (1인 / 편도 또는 왕복)
경유: 있음/없음
```

- 항공권은 편도/왕복 여부를 명시. 기차/버스/배편은 편도 가격이 기본.
- 여러 옵션이 있으면 **최저가 3개** 위주로 정리.
- 날짜별 가격 차이가 있으면 비교표도 제공.

## 에지 케이스

- **폼 자동완성이 안 뜰 때**: 1초 대기 후 재시도. 그래도 실패 시 네이버 검색 폴백
- **캡챠/로그인 차단**: 해당 사이트 포기 → 네이버 검색 또는 다른 사이트로 전환
- **결과 0건**: 날짜/출발지/도착지 오타 확인 → 없으면 "해당 노선에 직통 교통편이 없습니다" 안내 후 대안 경로 제안
- **사이트 점검 중**: 에러 페이지 감지 시 폴백 사이트로 전환, 사용자에게 점검 사실 고지

## 주의사항

- 스카이스캐너는 **성인 수(adults)** URL 파라미터로 제어 가능
- 코레일/SRT/고속버스는 직접 폼 조작 필요 → `agent-browser` 사용
- 가격은 실시간 변동 → 캡처 시점 기준임을 고지
