---
name: user_planning_style
description: 사용자의 플랜 작성 스타일 특성 — 구조는 탄탄하지만 done-when 조건이 빠지는 경향
type: user
---

사용자는 1인 개발자로 iOS(SwiftUI) + Rust(Axum) 풀스택 개발을 하고 있다. 플랜을 작성할 때 마일스톤 구조, 우선순위(P0/P1/P2), 크리티컬 패스, 리스크 분석까지 잘 갖추는 편이다. 초기에는 done-when을 빠뜨리는 경향이 있었으나, 피드백 후 `cargo test` 명칭/개수, `grep` 검증, Xcode 빌드 체크 등 구체적인 측정 기준을 잘 작성한다. 배포 단계도 초기에 누락하는 경향이 있었으나 피드백 후 fly deploy + TestFlight + smoke test까지 포함시킨다. 남은 개선 포인트: (1) 주요 가정(assumptions)을 명시적으로 기술하지 않는 편 (2) 설계 문서의 done-when이 내용 품질보다 형식 검증(grep 카운트)에 의존하는 경향.
