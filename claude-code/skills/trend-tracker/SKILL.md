---
name: trend-tracker
description: 오늘의 트렌드를 조사한다. Google Trends(한국/글로벌), Reddit 인기 글에서 실시간 트렌드 수집. "트렌드 알려줘", "요즘 뭐가 핫해?", "인기 키워드", "오늘의 이슈" 등의 요청에 트리거.
---

# Trend Tracker

Google Trends + Reddit에서 실시간 트렌드를 수집하는 스킬.

## 사용법

```bash
# 텍스트 출력 (한국)
python3 scripts/research.py KR text

# JSON 출력 (파이프라인용)
python3 scripts/research.py KR json

# 미국 트렌드
python3 scripts/research.py US text
```

## 데이터 소스

- **Google Trends**: 일간 인기 검색어 + 관련 뉴스 (RSS)
- **Reddit**: r/popular 일간 인기 글 (JSON API)

## 지원 지역

| 코드 | 지역 |
|------|------|
| KR | 한국 |
| US | 미국 |
| JP | 일본 |
| GB | 영국 |
| DE | 독일 |

이 외의 지역 코드를 요청받으면: "지원되는 지역은 KR, US, JP, GB, DE입니다. 다른 지역은 현재 지원하지 않습니다."라고 안내.

## Out of Scope — Do NOT Use This Skill For

- **과거 트렌드 분석** (historical trend data) → `researcher` 스킬 사용
- **소셜 미디어 모니터링** (특정 브랜드/키워드 추적) → 범위 밖
- **주식/금융 트렌드** → 범위 밖, 별도 금융 도구 필요
- **실시간 뉴스 알림 설정** → 범위 밖

## Edge Cases

- **스크립트 실행 실패**: 먼저 `python3 --version`으로 Python 설치 확인. `scripts/` 디렉토리가 존재하는지 확인 (`ls scripts/research.py`). 파일이 없으면 사용자에게 "scripts/research.py 파일을 찾을 수 없습니다. 스킬 설치 상태를 확인해주세요."라고 보고.
- **인터넷 연결 없음**: 스크립트가 네트워크 에러를 반환하면 "인터넷 연결을 확인해주세요. 트렌드 수집에는 네트워크 접속이 필요합니다."라고 보고.
- **API 레이트 리밋**: HTTP 429 또는 rate limit 에러 발생 시, 60초 대기 후 1회 재시도. 재시도도 실패하면 "API 요청 한도에 도달했습니다. 잠시 후 다시 시도해주세요."라고 보고.
- **결과 0건 (빈 결과)**: "현재 {지역}에서 수집된 트렌드 토픽이 없습니다. 잠시 후 다시 시도하거나 다른 지역을 선택해주세요."라고 보고.
- **스크립트 의존성 누락**: `ModuleNotFoundError` 발생 시, 에러 메시지에서 모듈명을 추출하고 `pip install {모듈명}` 안내.

## 파이프라인 연동

JSON 출력 시 다음 구조:
```json
{
  "date": "ISO날짜",
  "geo": "KR",
  "google_trends": [{"keyword": "...", "traffic": "...", "news": [...]}],
  "reddit": [{"title": "...", "subreddit": "...", "score": 0}]
}
```

트렌드 데이터를 기반으로 영상 스크립트 생성, 콘텐츠 기획 등에 활용.
