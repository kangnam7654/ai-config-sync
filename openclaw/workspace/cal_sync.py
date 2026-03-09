#!/usr/bin/env python3
"""
Notion ↔ Google Calendar 양방향 증분 동기화
- 상태 파일(cal_sync_state.json)로 이미 동기화된 이벤트 추적
- 신규 이벤트만 반대편에 추가 (삭제는 미지원)
"""
import json, subprocess, os, re, time, sys
from datetime import datetime, timezone, timedelta
import urllib.request, urllib.error

NOTION_KEY = os.environ.get("NOTION_API_KEY", "")
NOTION_DB  = "b53115d0-3307-4f56-a76b-2ea22dae80a0"
CALENDAR_ID = "kangnam7653@gmail.com"
STATE_FILE = os.path.expanduser("~/.openclaw/workspace/cal_sync_state.json")

# ─── 상태 로드/저장 ────────────────────────────────────────────
def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"notion_ids": [], "gcal_ids": [], "last_sync": None}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

# ─── 유틸 ─────────────────────────────────────────────────────
def normalize_date(s):
    if not s: return ""
    m = re.match(r"(\d{4}-\d{2}-\d{2})", s)
    return m.group(1) if m else s

def name_key(name):
    return re.sub(r"[\s\[\]\(\)\-→\->♥️♥:@]", "", str(name)).lower()

def fix_datetime(s):
    """Notion/GCal 날짜 포맷 정규화"""
    if not s: return s
    s = re.sub(r"\.000", "", s)
    if "T" in s and "+" not in s and "Z" not in s:
        s += "+09:00"
    return s

# ─── Notion 이벤트 조회 ────────────────────────────────────────
def get_notion_events():
    events = []
    cursor = None
    while True:
        body = {"page_size": 100}
        if cursor:
            body["start_cursor"] = cursor
        data = json.dumps(body).encode()
        req = urllib.request.Request(
            f"https://api.notion.com/v1/databases/{NOTION_DB}/query",
            data=data,
            headers={
                "Authorization": f"Bearer {NOTION_KEY}",
                "Notion-Version": "2022-06-28",
                "Content-Type": "application/json"
            }, method="POST"
        )
        with urllib.request.urlopen(req) as resp:
            result = json.load(resp)
        for page in result.get("results", []):
            props = page.get("properties", {})
            name = ""
            title_arr = props.get("이름", {}).get("title", [])
            if title_arr:
                name = title_arr[0].get("plain_text", "")
            date_obj = props.get("날짜", {}).get("date")
            if not date_obj or not date_obj.get("start"):
                continue
            location = ""
            loc_arr = props.get("장소", {}).get("rich_text", [])
            if loc_arr:
                location = loc_arr[0].get("plain_text", "")
            events.append({
                "id": page["id"],
                "name": name,
                "start": date_obj.get("start", ""),
                "end": date_obj.get("end"),
                "location": location,
            })
        if not result.get("has_more"):
            break
        cursor = result.get("next_cursor")
    return events

# ─── GCal 이벤트 조회 ─────────────────────────────────────────
def get_gcal_events():
    now = datetime.now()
    from_dt = (now - timedelta(days=90)).strftime("%Y-%m-%dT00:00:00+09:00")
    to_dt   = (now + timedelta(days=365)).strftime("%Y-%m-%dT23:59:59+09:00")
    result = subprocess.run(
        ["gog", "calendar", "events", CALENDAR_ID,
         "--from", from_dt,
         "--to", to_dt,
         "--all-pages", "--max", "500", "--json"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"GCal 조회 실패: {result.stderr}")
        return []
    data = json.loads(result.stdout)
    events = []
    for e in data.get("events", []):
        events.append({
            "id": e["id"],
            "name": e.get("summary", ""),
            "start": e.get("start", {}).get("dateTime") or e.get("start", {}).get("date", ""),
            "end": e.get("end", {}).get("dateTime") or e.get("end", {}).get("date"),
            "location": e.get("location", ""),
        })
    return events

# ─── Notion에 이벤트 추가 ──────────────────────────────────────
def add_to_notion(name, start, end=None, location=""):
    start_clean = fix_datetime(start)
    date_obj = {"start": start_clean}
    if end:
        end_clean = normalize_date(end)
        if end_clean != normalize_date(start):
            date_obj["end"] = end_clean

    payload = {
        "parent": {"database_id": NOTION_DB},
        "properties": {
            "이름": {"title": [{"text": {"content": name[:200]}}]},
            "날짜": {"date": date_obj}
        }
    }
    if location:
        payload["properties"]["장소"] = {"rich_text": [{"text": {"content": location[:200]}}]}

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        "https://api.notion.com/v1/pages",
        data=data,
        headers={
            "Authorization": f"Bearer {NOTION_KEY}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }, method="POST"
    )
    try:
        with urllib.request.urlopen(req) as resp:
            result = json.load(resp)
            return result.get("id")
    except urllib.error.HTTPError as e:
        print(f"    Notion 추가 실패 ({e.code}): {e.read().decode()[:100]}")
        return None

# ─── GCal에 이벤트 추가 ───────────────────────────────────────
def add_to_gcal(name, start, end=None, location=""):
    start_clean = fix_datetime(start)

    if "T" in start_clean and "00:00:00" not in start_clean:
        # datetime 이벤트
        if end and "T" in end:
            end_clean = fix_datetime(end)
        else:
            # start + 1시간
            try:
                dt = datetime.fromisoformat(start_clean)
                end_dt = dt + timedelta(hours=1)
                end_clean = end_dt.isoformat()
            except:
                end_clean = start_clean
        cmd = ["gog", "calendar", "create", CALENDAR_ID,
               "--summary", name, "--from", start_clean, "--to", end_clean, "--force"]
    else:
        # 종일 이벤트
        date_only = normalize_date(start)
        cmd = ["gog", "calendar", "create", CALENDAR_ID,
               "--summary", name,
               "--from", f"{date_only}T00:00:00+09:00",
               "--to", f"{date_only}T23:59:59+09:00",
               "--force"]

    if location:
        cmd += ["--location", location]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        # ID 파싱
        out = result.stdout.strip()
        # gog output에서 event id 추출 시도
        m = re.search(r'"id":\s*"([^"]+)"', out)
        return m.group(1) if m else "created"
    else:
        print(f"    GCal 추가 실패: {result.stderr[:100]}")
        return None

# ─── 메인 동기화 ──────────────────────────────────────────────
def main():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] 양방향 동기화 시작")
    state = load_state()
    known_notion_ids = set(state.get("notion_ids", []))
    known_gcal_ids   = set(state.get("gcal_ids", []))

    notion_events = get_notion_events()
    gcal_events   = get_gcal_events()
    print(f"  Notion: {len(notion_events)}개, GCal: {len(gcal_events)}개")

    # 인덱스 (name_key + date → id)
    notion_index = {}
    for e in notion_events:
        key = (name_key(e["name"]), normalize_date(e["start"]))
        notion_index[key] = e["id"]

    gcal_index = {}
    for e in gcal_events:
        key = (name_key(e["name"]), normalize_date(e["start"]))
        gcal_index[key] = e["id"]

    # ── Notion → GCal ──────────────────────────────────────────
    notion_to_gcal = 0
    for e in notion_events:
        if e["id"] in known_notion_ids:
            continue  # 이미 처리됨
        key = (name_key(e["name"]), normalize_date(e["start"]))
        if key in gcal_index:
            # GCal에 이미 있음 → 상태에만 등록
            known_notion_ids.add(e["id"])
            known_gcal_ids.add(gcal_index[key])
            continue
        if not e["start"]:
            continue
        print(f"  [N→G] {e['name']} [{e['start']}] ... ", end="", flush=True)
        gid = add_to_gcal(e["name"], e["start"], e.get("end"), e.get("location", ""))
        if gid:
            print("✅")
            known_notion_ids.add(e["id"])
            if gid != "created":
                known_gcal_ids.add(gid)
            notion_to_gcal += 1
        else:
            print("❌")
        time.sleep(0.3)

    # ── GCal → Notion ──────────────────────────────────────────
    gcal_to_notion = 0
    for e in gcal_events:
        if e["id"] in known_gcal_ids:
            continue
        key = (name_key(e["name"]), normalize_date(e["start"]))
        if key in notion_index:
            known_gcal_ids.add(e["id"])
            known_notion_ids.add(notion_index[key])
            continue
        if not e["start"] or not e["name"]:
            continue
        print(f"  [G→N] {e['name']} [{e['start']}] ... ", end="", flush=True)
        nid = add_to_notion(e["name"], e["start"], e.get("end"), e.get("location", ""))
        if nid:
            print("✅")
            known_gcal_ids.add(e["id"])
            known_notion_ids.add(nid)
            gcal_to_notion += 1
        else:
            print("❌")
        time.sleep(0.35)

    state["notion_ids"] = list(known_notion_ids)
    state["gcal_ids"]   = list(known_gcal_ids)
    state["last_sync"]  = datetime.now(timezone.utc).isoformat()
    save_state(state)

    print(f"\n✅ 동기화 완료: Notion→GCal {notion_to_gcal}개, GCal→Notion {gcal_to_notion}개")
    return notion_to_gcal + gcal_to_notion

if __name__ == "__main__":
    count = main()
    sys.exit(0)
