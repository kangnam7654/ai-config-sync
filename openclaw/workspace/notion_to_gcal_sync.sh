#!/bin/bash
# Notion 스케줄 → Google Calendar 동기화
# Calendar ID: kangnam7653@gmail.com

CALENDAR_ID="kangnam7653@gmail.com"
SUCCESS=0
FAIL=0

sync_event() {
  local name="$1"
  local start="$2"
  local end="$3"
  local location="$4"
  local tags="$5"

  # 날짜만 있는 경우 (all-day) vs datetime
  if [[ "$start" =~ T ]]; then
    # datetime 이벤트 (1시간 기본)
    local start_iso=$(echo "$start" | sed 's/\.000//')
    # end가 없으면 start + 1시간 계산
    if [ -z "$end" ]; then
      # gog는 --from --to 필요
      local end_iso=$(date -j -f "%Y-%m-%dT%H:%M:%S%z" -v+1H "$(echo $start_iso | tr -d 'Z')+0000" "+%Y-%m-%dT%H:%M:%S+09:00" 2>/dev/null || echo "${start_iso%+*}:00:00+09:00")
    else
      local end_iso="$end"
    fi
    
    if [ -n "$location" ]; then
      gog calendar create "$CALENDAR_ID" \
        --summary "$name" \
        --from "$start_iso" \
        --to "$end_iso" \
        --location "$location" \
        --description "태그: $tags" \
        --force 2>&1
    else
      gog calendar create "$CALENDAR_ID" \
        --summary "$name" \
        --from "$start_iso" \
        --to "$end_iso" \
        --description "태그: $tags" \
        --force 2>&1
    fi
  else
    # all-day 이벤트
    local end_day="$end"
    if [ -z "$end_day" ]; then
      end_day="$start"
    fi
    
    if [ -n "$location" ]; then
      gog calendar create "$CALENDAR_ID" \
        --summary "$name" \
        --from "${start}T00:00:00+09:00" \
        --to "${end_day}T23:59:59+09:00" \
        --location "$location" \
        --description "태그: $tags" \
        --force 2>&1
    else
      gog calendar create "$CALENDAR_ID" \
        --summary "$name" \
        --from "${start}T00:00:00+09:00" \
        --to "${end_day}T23:59:59+09:00" \
        --description "태그: $tags" \
        --force 2>&1
    fi
  fi
}

# 이벤트 목록 (name|start|end|location|tags)
events=(
  "크레버스 퇴사|2025-06-17|||"
  "일본여행|2025-04-30||후쿠오카|여행"
  "메타월드 사람들 만남|2025-04-03|||"
  "집 비워주는 날|2025-02-28|||"
  "[이사] 동작구 상도동 → 강동구 둔촌동|2025-02-25||서울 동작구 둔총동 올림픽파크 포레온 1단지 104동 206호|이사"
  "[대출] 포레온 잔금 실행|2025-02-14|||대출"
  "엄마에게 전세|2025-02-11|||"
  "보이저 엑스 면접|2024-12-18T15:00:00+09:00|||"
  "크레버스 입사|2024-04-22|||"
  "메타버스월드 퇴사|2024-01-31|||퇴사"
  "통일 노래방 증여|2023-06-12|||"
  "[이사] 송파구 삼전동 → 동작구 상도동|2023-05-16||동작구 상도로 54길 54 이에스하임 12차 1동 401호|이사"
  "국민대 납부 기한|2023-01-09|||"
  "건대 예치금|2022-12-26|||"
  "메타버스월드 급여|2022-12-23|||"
  "코로나 확진|2022-12-14|||"
  "2023년 건국대 발표|2022-12-09|||"
  "한양대 면접|2022-12-03T10:00:00+09:00|||"
  "서울시립대 면접|2022-12-03|||"
  "서강대 면접|2022-12-03|||"
  "2023년 국민대 소프트웨어 발표|2022-12-01|||"
  "건국대 면접|2022-11-26|||"
  "메타버스월드 급여 (2022년 11월분)|2022-11-25|||"
  "경식이형 만남|2022-11-22|||"
  "국민대 대학원 면접|2022-11-19|||"
  "2023년 서강대 정보통신대학원 데이터사이언스 인공지능|2022-11-18|||대학원"
  "2023년 전기 한양대 대학원 접수|2022-11-17|||대학원"
  "2023년 서울시립대 과학기술대학원 컴퓨터과학|2022-11-16T17:00:00+09:00|||대학원"
  "국민대 경영대학원 AI빅데이터전공|2022-11-14|||대학원"
  "AICE BASIC 시험|2022-11-12T00:00:00+09:00||온라인|시험"
  "2023년 건국대 정보통신대학원 인공지능전공|2022-11-11|||대학원"
  "2023년 국민대 소프트웨어융합대학원 인공지능전공|2022-11-10T17:00:00+09:00|||대학원"
  "김재우 팀장님 복귀|2022-10-28|||메타버스월드"
  "메타버스월드 회식|2022-10-27|||메타버스월드"
  "메타버스월드 급여 (2022년 10월분)|2022-10-25|||급여,메타버스월드"
  "아이패드 도착|2022-10-16|||"
  "[구매] 아이패드 주문|2022-10-16|||구매"
  "2022 GDF|2022-10-13||G타워|메타버스월드"
  "휴대폰 구매|2022-10-10|||"
  "폰 분실|2022-10-08|||"
  "메타버스월드 출근|2022-10-05T10:30:00+09:00||역삼 포스코타워|메타버스월드"
  "자동차 검사|2022-10-01T11:30:00+09:00|||"
  "빅분기 시험|2022-10-01|||"
  "아임클라우드 퇴사|2022-09-30|||아임클라우드,입사"
  "아임클라우드 급여|2022-09-23|||아임클라우드,급여"
  "채용검진|2022-09-21|||"
  "메타버스월드 2차 면접|2022-09-16T14:00:00+09:00|||면접"
  "메타버스월드 면접|2022-09-08T11:00:00+09:00||서울 강남구 테헤란로 134 (포스코타워 역삼) 12F|면접"
  "아임클라우드 휴가|2022-09-08|||"
  "빅데이터 분석 기사 접수 마무리|2022-09-02|||시험"
)

echo "=== Notion → Google Calendar 동기화 시작 ==="
echo "총 ${#events[@]}개 이벤트"
echo ""

for event in "${events[@]}"; do
  IFS='|' read -r name start end location tags <<< "$event"
  echo -n "📅 $name ($start) ... "
  result=$(sync_event "$name" "$start" "$end" "$location" "$tags" 2>&1)
  if echo "$result" | grep -q "error\|Error\|failed\|Failed"; then
    echo "❌ 실패: $result"
    ((FAIL++))
  else
    echo "✅"
    ((SUCCESS++))
  fi
  sleep 0.3  # rate limit 방지
done

echo ""
echo "=== 완료: 성공 $SUCCESS / 실패 $FAIL ==="
