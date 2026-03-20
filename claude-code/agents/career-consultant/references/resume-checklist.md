# Resume Review Checklist

이력서 리뷰 시 참조하는 상세 체크리스트. career-consultant 에이전트의 Step 2~4에서 이 파일을 읽어 평가 기준으로 사용한다.

## 1. Structure Checklist

### 필수 섹션 (순서대로)

| 순서 | 섹션 | 필수 여부 | 비고 |
|------|------|-----------|------|
| 1 | 연락처 (Contact) | 필수 | 이메일, 전화번호, LinkedIn, GitHub |
| 2 | 요약 (Summary/Objective) | 권장 | 시니어: Summary, 주니어: Objective |
| 3 | 기술 스택 (Skills) | 필수 | 시니어는 경력 뒤에 배치 가능 |
| 4 | 경력 (Experience) | 필수 | 최신순 정렬 |
| 5 | 프로젝트 (Projects) | 선택 | 경력이 짧으면 필수 |
| 6 | 학력 (Education) | 필수 | 시니어는 간략하게 |
| 7 | 자격증/수상 (Certifications) | 선택 | 관련성 있는 것만 |

### 분량 기준

| 경력 | 권장 분량 | 비고 |
|------|-----------|------|
| 0~2년 (주니어) | 1페이지 | 프로젝트, 인턴십 중심 |
| 3~10년 (미들~시니어) | 1페이지 | 경력 중심, 초기 경력 압축 |
| 10년 초과 (리드/매니저) | 1~2페이지 | 최근 5년 상세, 나머지 1줄 요약 |

### 가독성 기준

- 글머리 기호(bullet point)로 경력 기술: 한 bullet당 1~2줄
- 날짜 형식 일관성: "2022.03 - 2024.01" 또는 "Mar 2022 - Jan 2024" (혼용 금지)
- 폰트: 1~2종만 사용 (제목 + 본문)
- 여백: 상하좌우 최소 0.5인치 (1.27cm)
- 링크: 클릭 가능한 하이퍼링크로 삽입

## 2. Experience Description Quality

### 액션 동사 (강함 → 약함)

**강한 동사** (사용 권장):
- 구축: Architected, Engineered, Built, Developed, Implemented
- 개선: Optimized, Reduced, Improved, Accelerated, Streamlined
- 리더십: Led, Spearheaded, Mentored, Coordinated, Drove
- 분석: Analyzed, Diagnosed, Identified, Investigated, Resolved

**약한 동사** (사용 지양):
- Worked on, Helped, Assisted, Participated in, Was responsible for

### 성과 수치화 패턴

| 패턴 | Bad | Good |
|------|-----|------|
| 속도 | 서비스 속도를 개선했다 | API 응답 시간을 800ms에서 120ms로 85% 단축했다 |
| 규모 | 대규모 트래픽을 처리했다 | 일 평균 200만 요청을 처리하는 시스템을 구축했다 |
| 비용 | 인프라 비용을 줄였다 | AWS 비용을 월 $12,000에서 $4,500으로 62% 절감했다 |
| 품질 | 버그를 줄였다 | 프로덕션 에러율을 3.2%에서 0.4%로 감소시켰다 |
| 팀 | 팀을 이끌었다 | 5명의 엔지니어로 구성된 팀을 리드하여 3개월 내 MVP 출시했다 |

### STAR 구조 예시

```
Before: React와 TypeScript로 프론트엔드를 개발했습니다.

After: 레거시 jQuery 코드베이스(S)를 React + TypeScript로 마이그레이션하는 프로젝트를 리드(T)하여,
       컴포넌트 기반 아키텍처를 설계하고 80개 컴포넌트를 재작성(A)했다.
       번들 사이즈 40% 감소, 페이지 로드 시간 2.1초 → 0.8초 달성(R).
```

## 3. ATS Keyword Reference

### 공통 키워드 (직무 무관)

- Agile, Scrum, Kanban
- CI/CD, DevOps
- Git, GitHub, GitLab
- Code Review, Pair Programming
- Unit Testing, Integration Testing
- Technical Documentation

### 직무별 핵심 키워드

#### Backend Engineer
- REST API, GraphQL, gRPC
- Microservices, Monolith, Event-Driven
- PostgreSQL, MySQL, MongoDB, Redis
- Docker, Kubernetes, AWS/GCP/Azure
- Python, Go, Java, Node.js
- Message Queue (Kafka, RabbitMQ, SQS)
- Performance Optimization, Caching
- Database Design, ORM, Query Optimization

#### Frontend Engineer
- React, Vue, Angular, Svelte
- TypeScript, JavaScript (ES6+)
- HTML5, CSS3, Tailwind, Styled-Components
- State Management (Redux, Zustand, Pinia)
- Responsive Design, Mobile-First
- Web Performance, Lighthouse, Core Web Vitals
- Accessibility (WCAG 2.1)
- Webpack, Vite, Babel

#### Full-Stack Engineer
- 위 Backend + Frontend 키워드 모두 해당
- SSR (Next.js, Nuxt), SSG, ISR
- Monorepo (Turborepo, Nx)
- API Design, BFF Pattern

#### DevOps / SRE
- Terraform, Pulumi, CloudFormation
- Kubernetes, Helm, ArgoCD
- Monitoring (Prometheus, Grafana, Datadog)
- Logging (ELK, Loki)
- Incident Management, On-Call, SLO/SLI
- Infrastructure as Code, GitOps

#### Data Engineer
- ETL/ELT, Data Pipeline
- Apache Spark, Airflow, dbt
- Data Warehouse (BigQuery, Snowflake, Redshift)
- Streaming (Kafka, Flink, Kinesis)
- Data Modeling, Star Schema, Dimensional Modeling
- Python, SQL, Scala

#### Mobile Developer
- React Native, Flutter, SwiftUI, Jetpack Compose
- iOS, Android, Cross-Platform
- App Store Optimization, Push Notifications
- Mobile Performance, Offline Support
- Deep Linking, Universal Links

### 시니어리티별 키워드

| 시니어리티 | 추가 키워드 |
|-----------|------------|
| Junior | Eager to learn, Fast learner (사용 지양 — 구체적 프로젝트로 증명) |
| Mid-Level | Independently, Ownership, Cross-functional |
| Senior | Architecture, System Design, Mentoring, Tech Lead |
| Lead/Staff | Strategy, Roadmap, Organization-wide, Stakeholder Management |
| Manager | People Management, Hiring, Performance Review, OKR |
