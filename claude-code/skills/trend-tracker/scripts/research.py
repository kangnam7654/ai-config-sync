#!/usr/bin/env python3
"""
트렌드 리서치 스크립트
Google Trends, Reddit에서 오늘의 트렌드를 수집한다.
Usage: python3 research.py [geo] [format]
  geo: KR (기본), US, JP 등
  format: text (기본), json
"""

import json
import sys
import urllib.request
from datetime import datetime
from xml.etree import ElementTree


def fetch(url, headers=None):
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")
    if headers:
        for k, v in headers.items():
            req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception:
        return None


def google_trends_daily(geo="KR"):
    """Google Trends 일간 트렌드 (RSS)"""
    url = f"https://trends.google.com/trending/rss?geo={geo}"
    xml = fetch(url)
    if not xml:
        return []

    ns = {"ht": "https://trends.google.com/trending/rss"}
    results = []
    try:
        root = ElementTree.fromstring(xml)
        for item in root.iter("item"):
            title = item.findtext("title", "")
            traffic = item.findtext("ht:approx_traffic", "", ns)
            news_items = []
            for ni in item.iter("{https://trends.google.com/trending/rss}news_item"):
                nt = ni.findtext("{https://trends.google.com/trending/rss}news_item_title", "")
                nu = ni.findtext("{https://trends.google.com/trending/rss}news_item_url", "")
                if nt:
                    news_items.append({"title": nt, "url": nu})
            results.append({
                "keyword": title,
                "traffic": traffic,
                "news": news_items[:2]
            })
    except Exception:
        pass
    return results[:15]


def reddit_trending(limit=15):
    """Reddit 인기 글 (글로벌)"""
    url = f"https://www.reddit.com/r/popular/top.json?t=day&limit={limit}"
    data = fetch(url)
    if not data:
        return []

    results = []
    try:
        j = json.loads(data)
        for post in j.get("data", {}).get("children", []):
            d = post.get("data", {})
            results.append({
                "title": d.get("title", ""),
                "subreddit": d.get("subreddit", ""),
                "score": d.get("score", 0),
                "url": f"https://reddit.com{d.get('permalink', '')}"
            })
    except Exception:
        pass
    return results


def reddit_trending_topic(subreddit="all", limit=10):
    """특정 서브레딧 트렌드"""
    url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit={limit}"
    data = fetch(url)
    if not data:
        return []

    results = []
    try:
        j = json.loads(data)
        for post in j.get("data", {}).get("children", []):
            d = post.get("data", {})
            if d.get("stickied"):
                continue
            results.append({
                "title": d.get("title", ""),
                "subreddit": d.get("subreddit", ""),
                "score": d.get("score", 0),
            })
    except Exception:
        pass
    return results


def main():
    geo = sys.argv[1] if len(sys.argv) > 1 else "KR"
    output_format = sys.argv[2] if len(sys.argv) > 2 else "text"

    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    # 데이터 수집
    gt = google_trends_daily(geo)
    rd = reddit_trending(10)

    if output_format == "json":
        result = {
            "date": datetime.now().isoformat(),
            "geo": geo,
            "google_trends": gt,
            "reddit": rd,
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    # 텍스트 출력
    print(f"[트렌드 리서치] {now} | 지역: {geo}")
    print("=" * 60)

    print("\n🔥 Google Trends (일간)")
    print("-" * 40)
    if gt:
        for i, t in enumerate(gt, 1):
            print(f"  {i}. {t['keyword']} ({t['traffic']})")
            for n in t.get("news", [])[:1]:
                print(f"     └ {n['title']}")
    else:
        print("  (데이터 없음)")

    print("\n📱 Reddit 인기 (글로벌)")
    print("-" * 40)
    if rd:
        for i, r in enumerate(rd, 1):
            print(f"  {i}. [{r['subreddit']}] {r['title']} (↑{r['score']})")
    else:
        print("  (데이터 없음)")


if __name__ == "__main__":
    main()
