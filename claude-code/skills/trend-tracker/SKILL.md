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
