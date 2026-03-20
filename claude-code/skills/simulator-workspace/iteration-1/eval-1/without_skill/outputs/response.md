## 수행 결과 요약

1. **시뮬레이터 확인**: iPhone 17 Pro (iOS 26.2, UDID: `3ED9A4F3-BFD5-4B1C-902D-0F9A1EB9ABC1`)가 이미 Booted 상태였으므로 별도 부팅 없이 바로 사용했습니다.
2. **Safari에서 example.com 열기**: `xcrun simctl openurl` 명령으로 Safari에서 `https://example.com`을 열었습니다.
3. **스크린샷 촬영**: `xcrun simctl io screenshot` 명령으로 스크린샷을 촬영했습니다. 처음에는 Safari 시작 페이지 팝업과 팁 배너가 표시되었으나, URL을 다시 열어 팝업을 해제하고 깔끔한 스크린샷을 확보했습니다.

**최종 스크린샷 파일**: `/tmp/ios_sim_final2.png` (1206x2622 PNG, "Example Domain" 페이지가 정상 표시됨)
