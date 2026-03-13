---
name: veo-shorts-writer
description: VEO 숏폼 영상 스크립트 생성. 사주팔자/돈/운명/사랑 주제의 유튜브 쇼츠용 VEO 3.1 프롬프트와 대사를 작성한다. "영상 스크립트 만들어", "숏폼 스크립트", "사주 영상 대본", "VEO 프롬프트" 등의 요청에 트리거.
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

### 콘텐츠 규칙
14. **주제** — 사주팔자, 돈복, 운명, 사랑운, 재물운, 건강운 중 선택
15. **다양성** — 이전 스크립트를 참고해 반복 회피. `references/archive.md` 확인
16. **후편 가능** — 시리즈물로 이어질 수 있는 열린 결말 허용

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
A cinematic vertical short-form video, 9:16. 3D animated character style matching the reference image throughout — NOT live action, NOT realistic. The character Jeongbin is a mysterious Korean female saju interpreter in traditional hanbok with purple eyes, yin-yang earrings, and a crescent moon hair ornament, rendered in stylized 3D animation. [장면/배경 묘사]. [카메라 움직임].

Exact spoken Korean dialogue:
"[대사 1]"
"[대사 2]"

She must speak the dialogue naturally in Korean, with a calm, soft, mysterious female voice, slow pacing, and short pauses between lines. Natural Korean lip sync. Clear mouth movement matched to Korean syllables.

ABSOLUTELY NO MUSIC. NO background music. NO instrumental sounds. NO soundtrack. Only her voice and soft ambient sounds ([구체적 앰비언트]). No subtitles. No on-screen text. No translation. No English speech. No other voices.

Visual progression: [초별 진행 묘사]. Maintain consistent 3D animated illustration style throughout — do NOT transition to live action or photorealistic rendering at any point.

Style: premium 3D animated fantasy, elegant, mystical, emotionally immersive. No text, no titles, no subtitles, no captions, no watermarks.
```

## 프롬프트 구조 템플릿 (파트 2)

```
Continue the same scene in the SAME 3D animated illustration style — NOT live action, NOT photorealistic. [장면 전환/변화 묘사]. [정빈 표정/동작 변화].

Exact spoken Korean dialogue:
"[대사]"

She delivers this line slowly with [감정 묘사]. Then holds a [표정] for several seconds as [시각 효과 묘사]. Natural Korean lip sync.

ABSOLUTELY NO MUSIC. NO background music. NO instrumental sounds. Only her voice and soft ambient sounds. No subtitles. No on-screen text.

Maintain the same 3D animated character rendering from the previous part. Do NOT switch to live action or realistic style.

Style: premium 3D animated fantasy, elegant, mystical, emotionally immersive. No text, no titles, no subtitles, no captions, no watermarks.
```
