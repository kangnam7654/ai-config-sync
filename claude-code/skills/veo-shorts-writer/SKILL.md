---
name: veo-shorts-writer
description: "VEO short-form video script generator. Creates VEO 3.1 prompts and dialogue for YouTube Shorts on fortune/money/destiny/love topics."
---

# VEO Shorts Writer

사주/운세/운명 주제의 유튜브 쇼츠(세로 9:16) 스크립트를 생성하는 스킬.

## 출력 구조

15초 영상 = **2개 파트**. Veo extend API로 이어붙인다.

```
파트 1 (0-8초):  Hook + Core — 시청자를 잡는 도입 + 핵심 정보
파트 2 (8-15초): Payoff — 반전/결론 + 여운
```

**기술적 구조**: Part 1 = create (8초), Part 2 = extend (+7초 = 15초 누적)

## 핵심 규칙 (절대 준수)

### VEO 프롬프트 규칙
1. **텍스트/글씨 절대 금지** — VEO가 글씨를 깨뜨린다. 특히 한글. 자막은 후처리(finalize)에서 넣음
2. **배경음악 완전 금지** — "ABSOLUTELY NO MUSIC. NO background music. NO instrumental sounds. NO soundtrack. Only her voice and soft ambient sounds" 반드시 포함
3. **3D 애니메이션 스타일 명시** — "3D animated character style matching the reference image throughout — NOT live action, NOT realistic" 반드시 포함
4. **상황묘사 명확하게** — 장소, 인물 외형, 조명, 카메라 움직임, 표정을 구체적으로 기술
5. **영어로 작성** — VEO 프롬프트는 영어. 대사 부분만 한국어를 직접 포함
6. **자막/텍스트 금지 반복** — 프롬프트 끝에 "No text, no titles, no subtitles, no captions, no watermarks" 반드시 포함

### 대사 규칙
7. **한국어 대사** — 등장인물이 한국어로 말한다
8. **대사 포맷** — `Exact spoken Korean dialogue:` 블록으로 대사를 프롬프트에 직접 포함
9. **음성 지시** — "She must speak the dialogue naturally in Korean, with a calm, soft, mysterious female voice, slow pacing, and short pauses between lines. Natural Korean lip sync." 포함
10. **파트 1 대사**: 2~3문장 (도입 + 핵심). 8초 안에 소화할 분량
11. **파트 2 대사**: 1~2문장 (결론). 짧고 임팩트 있게. 이후 여운을 위한 무언의 응시 시간 확보

### 파트 2 프롬프트 규칙
12. **연속성 명시** — "Continue the same scene in the SAME 3D animated illustration style — NOT live action, NOT photorealistic" 로 시작
13. **스타일 일관성** — "Maintain the same 3D animated character rendering from the previous part. Do NOT switch to live action or realistic style." 포함

### 연출/구도 규칙 (VEO 안정성 기반)
14. **배경은 추상적 공간** — "dark mystical space" 기본. 구체적 장소(연못, 숲, 방, 거리)는 VEO가 캐릭터 배치를 잘못함 (예: 연못 옆 → 물에 잠김)
15. **캐릭터는 항상 서 있는 포즈** — "She stands in..." 기본. 앉기/눕기/물가/기대기 등은 VEO가 비정상적 포즈로 해석할 위험 높음
16. **배경 효과는 부유 입자만** — golden particles, dust, light orbs, coins, fragments, fireflies 등 추상적 부유 요소. 동물(잉어, 새), 건축물, 가구 등 복잡한 3D 오브젝트는 퀄리티 저하
17. **물/액체 묘사 금지** — 물, 연못, 바다, 비, 강 등은 캐릭터가 잠기거나 젖는 결과 초래. 물 테마가 필요하면 "water-like light particles" 같은 추상적 표현으로 대체
18. **카메라는 단순하게** — close-up → slow pull back 또는 static shot만 사용. 패닝, 회전, 빠른 컷, wide→push in 금지. VEO는 단순한 카메라 무브에서 가장 안정적
19. **공간 배치 명확하게** — 모호한 전치사(beside, near, by) 대신 명확한 위치("standing on solid ground in", "standing alone in the center of") 사용
20. **파트 2 의상 고정** — Part 2 프롬프트에 "wearing the EXACT same outfit and colors as Part 1" 명시. extend 시 옷 색상 변경 방지
21. **이펙트 전환은 은은하게** — "bursting", "exploding", "brilliant sparks" 등 폭발적 전환 금지. "slowly begin to glow", "gradually reform", "gently drift upward" 같은 점진적/은은한 전환만 사용. 과한 이펙트 = 촌스러움

### 콘텐츠 규칙
22. **주제** — 사주팔자, 돈복, 운명, 사랑운, 재물운, 건강운 중 선택
23. **다양성** — 이전 스크립트를 참고해 반복 회피. `references/archive.md` 확인
24. **후편 가능** — 시리즈물로 이어질 수 있는 열린 결말 허용

## 캐릭터: 정빈 (Jeongbin)

현재 채널의 고정 캐릭터. 모든 프롬프트에 아래 외형 설명을 포함:

> Jeongbin is a mysterious Korean female saju interpreter in traditional hanbok with purple eyes, yin-yang earrings, and a crescent moon hair ornament, rendered in stylized 3D animation.

- 레퍼런스 이미지: `contents/character/jeong_bin/` (front, idle, black, smile, stand)
- `--image` 옵션으로 레퍼런스 이미지를 Veo에 전달

## 스크립트 포맷

```markdown
# [제목]
- 주제: [사주팔자/돈/운명/사랑 중]
- 분위기: [한 줄 설명]

## 파트 1 (0-8초) — Hook + Core
**VEO 프롬프트:** [영어 프롬프트]
**대사(한국어):** [2~3문장]
**상황:** [한국어 장면 설명]

## 파트 2 (8-15초) — Payoff
**VEO 프롬프트:** [영어 프롬프트. "Continue the same scene..." 으로 시작]
**대사(한국어):** [1~2문장 + 무언의 응시]
**상황:** [장면 설명]

## 음악 프롬프트
[Gemini Music용 한국어 프롬프트]
```

## JSON 출력 포맷

스크립트 작성 후 CLI에서 바로 쓸 수 있는 JSON도 함께 생성:

```json
[
  {
    "prompt": "A cinematic vertical short-form video, 9:16. 3D animated character style...",
    "dialogue": "대사 1줄\n대사 2줄"
  },
  {
    "prompt": "Continue the same scene in the SAME 3D animated illustration style...",
    "dialogue": "대사"
  }
]
```

저장 경로: `output/YYYY-MM-DD/prompts/{파일명}.json`

## 실행 절차

1. `references/archive.md` 읽어서 이전 스크립트 주제/캐릭터 확인
2. 겹치지 않는 새로운 조합 선택 (주제 × 분위기 × 시각 테마)
3. 위 포맷에 맞춰 스크립트 + JSON 생성
4. 생성된 스크립트를 `references/archive.md`에 추가 (제목, 날짜, 주제, 비고만 요약)
5. JSON을 `output/YYYY-MM-DD/prompts/` 에 저장

## 프롬프트 구조 템플릿 (파트 1)

```
A cinematic vertical short-form video, 9:16. 3D animated character style matching the reference image throughout — NOT live action, NOT realistic. The character Jeongbin is a mysterious Korean female saju interpreter in traditional hanbok with purple eyes, yin-yang earrings, and a crescent moon hair ornament, rendered in stylized 3D animation. She stands alone in the center of a dark mystical space. [배경 부유 입자/빛 효과 묘사 — 구체적 장소 금지]. Close-up on her face with [표정]. [단순 카메라: "Camera slowly pulls back" 또는 static].

Exact spoken Korean dialogue:
"[대사 1]"
"[대사 2]"

She must speak the dialogue naturally in Korean, with a calm, soft, mysterious female voice, slow pacing, and short pauses between lines. Natural Korean lip sync. Clear mouth movement matched to Korean syllables.

ABSOLUTELY NO MUSIC. NO background music. NO instrumental sounds. NO soundtrack. Only her voice and soft ambient sounds ([구체적 앰비언트 — wind, shimmer 등]). No subtitles. No on-screen text. No translation. No English speech. No other voices.

Visual progression: 0-2s close-up on her face as she delivers the first line, 2-8s camera slowly pulls back to reveal [부유 입자 효과] around her as she delivers the remaining lines. Maintain consistent 3D animated illustration style throughout — do NOT transition to live action or photorealistic rendering at any point.

Style: premium 3D animated fantasy, elegant, mystical, emotionally immersive. No text, no titles, no subtitles, no captions, no watermarks.
```

### 파트 1 체크리스트
- [ ] "She stands" 사용 (앉기/눕기 금지)
- [ ] "dark mystical space" 또는 추상적 공간 (구체적 장소 금지)
- [ ] 배경 효과는 particles/dust/orbs만 (동물/건축물/물 금지)
- [ ] 카메라: close-up → pull back (단순 줌아웃)
- [ ] 물/액체 묘사 없음

## 프롬프트 구조 템플릿 (파트 2)

```
Continue the same scene in the SAME 3D animated illustration style — NOT live action, NOT photorealistic. Jeongbin remains standing in the same position, wearing the EXACT same outfit and colors as Part 1. [부유 입자/빛 효과의 변화 묘사 — 전환/강화/수렴 등]. Her expression shifts to [표정 변화]. She looks directly at the camera.

Exact spoken Korean dialogue:
"[대사]"

She delivers this line slowly with [감정 묘사]. Then holds a [표정] for several seconds as [시각 효과 변화]. Natural Korean lip sync.

ABSOLUTELY NO MUSIC. NO background music. NO instrumental sounds. Only her voice and soft ambient sounds. No subtitles. No on-screen text.

Maintain the same 3D animated character rendering from the previous part. Do NOT switch to live action or realistic style. Same outfit, same colors, same accessories.

Style: premium 3D animated fantasy, elegant, mystical, emotionally immersive. No text, no titles, no subtitles, no captions, no watermarks.
```

### 파트 2 체크리스트
- [ ] "remains standing in the same position" (포즈 유지)
- [ ] "wearing the EXACT same outfit and colors as Part 1" (의상 고정)
- [ ] 부유 입자의 변화로 시각적 전환 (장소 변경 금지)
- [ ] "looks directly at the camera" (마무리 응시)
- [ ] 물/액체/새 장소 없음

## 검증된 배경 패턴 (조회수 기반)

아래 패턴이 VEO에서 안정적이고 높은 조회수를 기록한 조합:

| 패턴 | 부유 입자 | 조회수 | 예시 |
|------|----------|--------|------|
| 금빛 파편 변환 | dissolving fragments → golden particles rising | 343 | 잃고얻는재물 |
| 어둠 → 빛 전환 | dark clouds parting → golden particles | 322 | 판이바뀌는신호 |
| 금빛 동전/먼지 | golden coins + gold dust swirling | 304 | 돈조짐 |
| 초승달 + 반딧불 | crescent moon + firefly lights | 288 | 새벽태생외로움 |

**공통점**: 어두운 추상 공간 + 금빛/빛 입자 + 감정적 전환(어둠→빛)
