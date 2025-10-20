---
name: alfred:1-plan
description: 계획 수립 (브레인스토밍, 계획 작성, 설계 논의) + 브랜치/PR 생성
argument-hint: "제목1 제목2 ... | SPEC-ID 수정내용"
allowed-tools:
  - Read
  - Write
  - Edit
  - MultiEdit
  - Grep
  - Glob
  - TodoWrite
  - Bash(git:*)
  - Bash(gh:*)
  - Bash(rg:*)
  - Bash(mkdir:*)
---

# 🏗️ MoAI-ADK 1단계: 계획 수립 (Plan) - 항상 계획을 먼저 세우고 진행한다

## 🎯 커맨드 목적

**"계획(Plan) → 실행(Run) → 동기화(Sync)"** 워크플로우의 첫 단계로, 아이디어 구상부터 계획 작성까지 계획 수립 전반을 지원합니다.

**계획 수립 대상**: $ARGUMENTS

## 💡 계획 철학: "항상 계획을 먼저 세우고 진행한다"

`/alfred:1-plan`은 단순히 SPEC 문서를 "작성"하는 것이 아니라, **계획을 수립**하는 범용 커맨드입니다.

### 3가지 주요 시나리오

#### 시나리오 1: 계획 작성 (주 사용 방식) ⭐
```bash
/alfred:1-plan "사용자 인증 기능"
→ 아이디어 구체화
→ EARS 구문으로 요구사항 명세
→ feature/SPEC-XXX 브랜치 생성
→ Draft PR 생성
```

#### 시나리오 2: 브레인스토밍
```bash
/alfred:1-plan "결제 시스템 개선 아이디어"
→ 아이디어 정리 및 구조화
→ 요구사항 후보 도출
→ 기술적 검토 및 리스크 분석
```

#### 시나리오 3: 기존 SPEC 개선
```bash
/alfred:1-plan "SPEC-AUTH-001 보안 강화"
→ 기존 계획 분석
→ 개선 방향 수립
→ 새 버전 계획 작성
```

> **표준 2단계 워크플로우** (자세한 내용: `CLAUDE.md` - "Alfred 커맨드 실행 패턴" 참조)

## 📋 실행 흐름

1. **프로젝트 분석**: product/structure/tech.md 심층 분석
2. **SPEC 후보 발굴**: 비즈니스 요구사항 기반 우선순위 결정
3. **사용자 확인**: 작성 계획 검토 및 승인
4. **계획 작성**: EARS 구조의 명세서 생성 (spec.md, plan.md, acceptance.md)
5. **Git 작업**: git-manager를 통한 브랜치/PR 생성

## 🔗 연관 에이전트

- **Primary**: spec-builder (🏗️ 시스템 아키텍트) - SPEC 문서 작성 전담
- **Secondary**: git-manager (🚀 릴리스 엔지니어) - Git 브랜치/PR 생성 전담

## 💡 사용 예시

사용자가 다음과 같이 커맨드를 실행할 수 있습니다:
- `/alfred:1-plan` - 프로젝트 문서 기반 자동 제안
- `/alfred:1-plan "JWT 인증 시스템"` - 단일 SPEC 수동 생성
- `/alfred:1-plan SPEC-001 "보안 보강"` - 기존 SPEC 보완

## 🔍 STEP 1: 프로젝트 분석 및 계획 수립

프로젝트 문서를 분석하여 SPEC 후보를 제안하고 구현 전략을 수립한 후 사용자 확인을 받습니다.

**spec-builder 에이전트가 자동으로 필요한 문서를 로드하여 분석합니다.**

### 🔍 코드베이스 탐색 (선택사항)

**사용자 요청이 불명확하거나 기존 코드 파악이 필요한 경우** Explore 에이전트를 먼저 활용합니다:

```
Task tool 호출 (Explore 에이전트):
- subagent_type: "Explore"
- description: "코드베이스에서 관련 파일 탐색"
- prompt: "다음 키워드와 관련된 모든 파일을 찾아주세요: $ARGUMENTS
          - 파일 위치 (src/, tests/, docs/)
          - 관련 SPEC 문서 (.moai/specs/)
          - 기존 구현 코드
          thoroughness 레벨: medium"
```

**Explore 에이전트 사용 기준**:
- ✅ 사용자가 "어디에 있는지", "찾아줘" 등의 키워드 사용
- ✅ 기존 코드 구조 파악이 필요한 경우
- ✅ 여러 파일에 걸쳐있는 기능 조사
- ❌ 명확한 SPEC 제목이 주어진 경우 (바로 spec-builder로)

### ⚙️ 에이전트 호출 방법

**STEP 1에서는 Task tool을 사용하여 spec-builder 에이전트를 호출합니다**:

```
Task tool 호출:
- subagent_type: "spec-builder"
- description: "계획 분석 및 작성 계획 수립"
- prompt: "프로젝트 문서를 분석하여 SPEC 후보를 제안해주세요.
          분석 모드로 실행하며, 다음을 포함해야 합니다:
          1. product/structure/tech.md 심층 분석
          2. SPEC 후보 발굴 및 우선순위 결정
          3. EARS 구조 설계
          4. 사용자 승인 대기
          사용자 입력: $ARGUMENTS
          (선택) Explore 결과: $EXPLORE_RESULTS"
```

### 계획 분석 진행

1. **프로젝트 문서 분석**
   - product/structure/tech.md 심층 분석
   - 기존 SPEC 목록 및 우선순위 검토 (.moai/specs/ 스캔)
   - 구현 가능성 및 복잡도 평가
   - (선택) Explore 결과 반영하여 기존 코드 구조 파악

2. **SPEC 후보 발굴**
   - 핵심 비즈니스 요구사항 추출
   - 기술적 제약사항 반영
   - 우선순위별 SPEC 후보 리스트 생성

3. **구현 계획 보고**
   - 단계별 계획 작성 계획 제시
   - 예상 작업 범위 및 의존성 분석
   - EARS 구조 및 Acceptance Criteria 설계

### 사용자 확인 단계

구현 계획 검토 후 다음 중 선택하세요:
- **"진행"** 또는 **"시작"**: 계획대로 계획 작성 시작
- **"수정 [내용]"**: 계획 수정 요청
- **"중단"**: 계획 작성 중단

---

## 🚀 STEP 2: 계획 문서 작성 (사용자 승인 후)

사용자 승인 후 **Task tool을 사용하여 spec-builder와 git-manager 에이전트를 호출**합니다.

### ⚙️ 에이전트 호출 방법

```
1. spec-builder 호출 (계획 작성):
   - subagent_type: "spec-builder"
   - description: "SPEC 문서 작성"
   - prompt: "STEP 1에서 승인된 계획에 따라 SPEC 문서를 작성해주세요.
             EARS 구조의 명세서를 생성합니다."

2. git-manager 호출 (Git 작업):
   - subagent_type: "git-manager"
   - description: "Git 브랜치/PR 생성"
   - prompt: "계획 작성 완료 후 브랜치와 Draft PR을 생성해주세요."
```

## 기능

- **프로젝트 문서 분석**: `.moai/project/{product,structure,tech}.md`를 분석해 구현 후보를 제안하고 사용자 승인 후 SPEC을 생성합니다.
- **Personal 모드**: `.moai/specs/SPEC-{ID}/` 디렉터리와 템플릿 문서를 만듭니다 (**디렉토리명 형식 필수**: `SPEC-` 접두어 + TAG ID).
- **Team 모드**: GitHub Issue(또는 Discussion)를 생성하고 브랜치 템플릿과 연결합니다.

## 사용법

사용자가 다음과 같은 형태로 커맨드를 실행합니다:
- `/alfred:1-plan` - 프로젝트 문서 기반 자동 제안 (권장)
- `/alfred:1-plan "JWT 인증 시스템"` - 단일 SPEC 수동 생성
- `/alfred:1-plan SPEC-001 "보안 보강"` - 기존 SPEC 보완

입력하지 않으면 Q&A 결과를 기반으로 우선순위 3~5건을 제안하며, 승인한 항목만 실제 SPEC으로 확정됩니다.

## 모드별 처리 요약

| 모드     | 산출물                                                               | 브랜치 전략                                     | 추가 작업                                       |
| -------- | -------------------------------------------------------------------- | ----------------------------------------------- | ----------------------------------------------- |
| Personal | `.moai/specs/SPEC-XXX/spec.md`, `plan.md`, `acceptance.md` 등 템플릿 | `main` 또는 `develop`에서 분기 (설정 기준)      | git-manager 에이전트가 자동으로 체크포인트 생성 |
| Team     | GitHub Issue(`[SPEC-XXX] 제목`), Draft PR(옵션)                      | **항상 `develop`에서 분기** (GitFlow 표준)      | `gh` CLI 로그인 유지, Draft PR → develop 생성   |

## 입력 옵션

- **자동 제안**: `/alfred:1-plan` → 프로젝트 문서 핵심 bullet을 기반으로 후보 리스트 작성
- **수동 생성**: 제목을 인수로 전달 → 1건만 생성, Acceptance 템플릿은 회신 후 보완
- **보완 모드**: `SPEC-ID "메모"` 형식으로 전달 → 기존 SPEC 문서/Issue를 업데이트

## 📋 STEP 1 실행 가이드: 프로젝트 분석 및 계획 수립

### ⚠️ 필수 규칙: 디렉토리 명명 규칙

**반드시 준수해야 할 형식**: `.moai/specs/SPEC-{ID}/`

**올바른 예시**:
- ✅ `SPEC-AUTH-001/`
- ✅ `SPEC-REFACTOR-001/`
- ✅ `SPEC-UPDATE-REFACTOR-001/`

**잘못된 예시**:
- ❌ `AUTH-001/` (SPEC- 접두어 누락)
- ❌ `SPEC-001-auth/` (ID 뒤 추가 텍스트)
- ❌ `SPEC-AUTH-001-jwt/` (ID 뒤 추가 텍스트)

**중복 확인 필수**: 새 SPEC ID를 생성하기 전에 반드시 기존 TAG ID를 검색하여 중복을 방지합니다.

**복합 도메인 규칙**:
- ✅ 허용: `UPDATE-REFACTOR-001` (2개 도메인)
- ⚠️ 주의: `UPDATE-REFACTOR-FIX-001` (3개 이상 도메인, 단순화 권장)

---

### 1. 프로젝트 문서 분석

Alfred는 spec-builder 에이전트를 호출하여 프로젝트 문서 기반 계획 분석 및 계획 수립을 수행합니다.

#### 분석 체크리스트

- [ ] **요구사항 추출**: product.md의 핵심 비즈니스 요구사항 파악
- [ ] **아키텍처 제약**: structure.md의 시스템 설계 제약사항 확인
- [ ] **기술적 제약**: tech.md의 기술 스택 및 품질 정책
- [ ] **기존 SPEC**: 현재 SPEC 목록 및 우선순위 검토

### 2. SPEC 후보 발굴 전략

#### 우선순위 결정 기준

| 우선순위 | 기준 | SPEC 후보 유형 |
|---------|------|----------------|
| **높음** | 핵심 비즈니스 가치 | 사용자 핵심 기능, API 설계 |
| **중간** | 시스템 안정성 | 인증/보안, 데이터 관리 |
| **낮음** | 개선 및 확장 | UI/UX 개선, 성능 최적화 |

#### SPEC 타입별 접근법

- **API/백엔드**: 엔드포인트 설계, 데이터 모델, 인증
- **프론트엔드**: 사용자 인터페이스, 상태 관리, 라우팅
- **인프라**: 배포, 모니터링, 보안 정책
- **품질**: 테스트 전략, 성능 기준, 문서화

### 3. 계획 작성 계획 보고서 생성

다음 형식으로 계획을 제시합니다:

```
## 계획 작성 계획 보고서: [TARGET]

### 📊 분석 결과
- **발굴된 SPEC 후보**: [개수 및 카테고리]
- **우선순위 높음**: [핵심 SPEC 목록]
- **예상 작업시간**: [시간 산정]

### 🎯 작성 전략
- **선택된 SPEC**: [작성할 SPEC ID 및 제목]
- **EARS 구조**: [Event-Action-Response-State 설계]
- **Acceptance Criteria**: [Given-When-Then 시나리오]

### 📦 기술 스택 및 라이브러리 버전 (선택사항)
**기술 스택이 계획 작성 단계에서 결정되는 경우에만 포함**:
- **웹 검색**: `WebSearch`를 통해 사용할 주요 라이브러리의 최신 안정 버전 확인
- **버전 명시**: 라이브러리별 정확한 버전 명시 (예: `fastapi>=0.118.3`)
- **안정성 우선**: 베타/알파 버전 제외, 프로덕션 안정 버전만 선택
- **참고**: 상세 버전은 `/alfred:2-build` 단계에서 최종 확정

### ⚠️ 주의사항
- **기술적 제약**: [고려해야 할 제약사항]
- **의존성**: [다른 SPEC과의 연관성]
- **브랜치 전략**: [Personal/Team 모드별 처리]

### ✅ 예상 산출물
- **spec.md**: [EARS 구조의 핵심 명세]
- **plan.md**: [구현 계획서]
- **acceptance.md**: [인수 기준]
- **브랜치/PR**: [모드별 Git 작업]

---
**승인 요청**: 위 계획으로 계획 작성을 진행하시겠습니까?
("진행", "수정 [내용]", "중단" 중 선택)
```

---

## 🚀 STEP 2 실행 가이드: 계획 작성 (승인 후)

사용자가 **"진행"** 또는 **"시작"**을 선택한 경우에만 Alfred는 spec-builder 에이전트를 호출하여 SPEC 문서 작성을 시작합니다.

### EARS 명세 작성 가이드

1. **Event**: 시스템에 발생하는 트리거 이벤트 정의
2. **Action**: 이벤트에 대한 시스템의 행동 명세
3. **Response**: 행동의 결과로 나타나는 응답 정의
4. **State**: 시스템 상태 변화 및 부작용 명시

**예시** (상세 내용은 `development-guide.md` 참조):
```markdown
### Ubiquitous Requirements (기본 요구사항)
- 시스템은 사용자 인증 기능을 제공해야 한다

### Event-driven Requirements (이벤트 기반)
- WHEN 사용자가 유효한 자격증명으로 로그인하면, 시스템은 JWT 토큰을 발급해야 한다

### State-driven Requirements (상태 기반)
- WHILE 토큰이 만료되지 않은 상태일 때, 시스템은 보호된 리소스에 대한 접근을 허용해야 한다

### Constraints (제약사항)
- IF 토큰이 만료되었으면, 시스템은 401 Unauthorized 응답을 반환해야 한다
```

### 📄 SPEC 문서 템플릿

#### YAML Front Matter 스키마

> **📋 SPEC 메타데이터 표준 (SSOT)**: `.moai/memory/spec-metadata.md`

**spec.md 파일 상단에 반드시 포함**해야 하는 메타데이터:
- **필수 필드 7개**: id, version, status, created, updated, author, priority
- **선택 필드 9개**: category, labels, depends_on, blocks, related_specs, related_issue, scope

**간단한 참조 예시**:
```yaml
---
id: AUTH-001
version: 0.0.1
status: draft
created: 2025-09-15
updated: 2025-09-15
author: @Goos
priority: high
---
```

**핵심 규칙**:
- **id**: TAG ID와 동일 (`<도메인>-<3자리>`) - 생성 후 절대 변경 금지
  - **디렉토리명**: `.moai/specs/SPEC-{ID}/` (예: `SPEC-AUTH-001/`)
  - **중복 확인**: `rg "@SPEC:{ID}" -n .moai/specs/` 필수
- **version**: v0.0.1 (INITIAL) → v0.1.0 (구현 완료) → v1.0.0 (안정화)
- **author**: GitHub ID 앞에 @ 접두사 필수 (예: `@Goos`)
- **priority**: critical | high | medium | low

**전체 필드 설명 및 검증 방법**: `.moai/memory/spec-metadata.md` 참조

#### HISTORY 섹션 (필수)

**YAML Front Matter 직후**에 반드시 HISTORY 섹션을 포함해야 합니다:

```markdown
# @SPEC:AUTH-001: JWT 기반 인증 시스템

## HISTORY

### v0.0.1 (2025-09-15)
- **INITIAL**: JWT 기반 인증 시스템 명세 최초 작성
- **AUTHOR**: @Goos
- **SCOPE**: 토큰 발급, 검증, 갱신 로직
- **CONTEXT**: 사용자 인증 강화 요구사항 반영

### v0.0.2 (2025-09-20)
- **ADDED**: 소셜 로그인 요구사항 추가 (Draft 수정)
- **AUTHOR**: @Goos
- **REVIEW**: @security-team (승인)
- **CHANGES**:
  - OAuth2 통합 요구사항
  - Google/GitHub 로그인 지원

### v0.1.0 (2025-10-01)
- **IMPLEMENTATION COMPLETED**: TDD 구현 완료 (status: draft → completed)
- **TDD CYCLE**: RED → GREEN → REFACTOR
- **COMMITS**: [구현 커밋 해시 목록]
- **FILES**: [생성/수정된 파일 목록]
```

**HISTORY 작성 규칙**:
- **버전 체계**: v0.0.1 (INITIAL) → v0.1.0 (구현 완료) → v1.0.0 (안정화)
  - 상세 버전 체계: `.moai/memory/spec-metadata.md#버전-체계` 참조
- **버전 순서**: 최신 버전이 위로 (역순)
- **변경 타입 태그**: INITIAL, ADDED, CHANGED, IMPLEMENTATION COMPLETED, BREAKING, DEPRECATED, REMOVED, FIXED
  - 상세 설명: `.moai/memory/spec-metadata.md#history-작성-가이드` 참조
- **필수 항목**: 버전, 날짜, AUTHOR, 변경 내용
- **선택 항목**: REVIEW, SCOPE, CONTEXT, MIGRATION

#### SPEC 문서 전체 구조

```markdown
---
id: AUTH-001
version: 1.0.0
status: draft
created: 2025-09-15
updated: 2025-09-15
author: @username
---

# @SPEC:AUTH-001: [SPEC 제목]

## HISTORY
[버전별 변경 이력 - 위 예시 참조]

## Environment (환경)
[시스템 환경 및 전제 조건]

## Assumptions (가정)
[설계 가정 사항]

## Requirements (요구사항)
### Ubiquitous (필수 기능)
- 시스템은 [기능]을 제공해야 한다

### Event-driven (이벤트 기반)
- WHEN [조건]이면, 시스템은 [동작]해야 한다

### State-driven (상태 기반)
- WHILE [상태]일 때, 시스템은 [동작]해야 한다

### Optional (선택 기능)
- WHERE [조건]이면, 시스템은 [동작]할 수 있다

### Constraints (제약사항)
- IF [조건]이면, 시스템은 [제약]해야 한다

## Traceability (@TAG)
- **SPEC**: @SPEC:AUTH-001
- **TEST**: tests/auth/test_service.py
- **CODE**: src/auth/service.py
- **DOC**: docs/api/authentication.md
```

### 에이전트 협업 구조

- **1단계**: `spec-builder` 에이전트가 프로젝트 문서 분석 및 SPEC 문서 작성을 전담합니다.
- **2단계**: `git-manager` 에이전트가 브랜치 생성, GitHub Issue/PR 생성을 전담합니다.
- **단일 책임 원칙**: spec-builder는 계획 작성만, git-manager는 Git/GitHub 작업만 수행합니다.
- **순차 실행**: spec-builder → git-manager 순서로 실행하여 명확한 의존성을 유지합니다.
- **에이전트 간 호출 금지**: 각 에이전트는 다른 에이전트를 직접 호출하지 않고, 커맨드 레벨에서만 순차 실행합니다.

## 🚀 최적화된 워크플로우 실행 순서

### Phase 1: 병렬 프로젝트 분석 (성능 최적화)

**동시에 수행**:

```
Task 1 (haiku): 프로젝트 구조 스캔
├── 언어/프레임워크 감지
├── 기존 SPEC 목록 수집
└── 우선순위 백로그 초안

Task 2 (sonnet): 심화 문서 분석
├── product.md 요구사항 추출
├── structure.md 아키텍처 분석
└── tech.md 기술적 제약사항
```

**성능 향상**: 기본 스캔과 심화 분석을 병렬 처리하여 대기 시간 최소화

### Phase 2: SPEC 문서 통합 작성

`spec-builder` 에이전트(sonnet)가 병렬 분석 결과를 통합하여:

- 프로젝트 문서 기반 기능 후보 제안
- 사용자 승인 후 SPEC 문서 작성 (MultiEdit 활용)
- 3개 파일 동시 생성 (spec.md, plan.md, acceptance.md)

### Phase 3: Git 작업 처리

`git-manager` 에이전트(haiku)가 최종 처리:

- **브랜치 생성**: 모드별 전략 적용
  - **Personal 모드**: `main` 또는 `develop`에서 분기 (프로젝트 설정 기준)
  - **Team 모드**: **항상 `develop`에서 분기** (GitFlow 표준)
  - 브랜치명: `feature/SPEC-{ID}` 형식
- **GitHub Issue 생성**: Team 모드에서 SPEC Issue 생성
- **Draft PR 생성**: Team 모드에서 `feature/SPEC-{ID}` → `develop` PR 생성
- **초기 커밋**: SPEC 문서 커밋 및 태그 생성

**중요**: 각 에이전트는 독립적으로 실행되며, 에이전트 간 직접 호출은 금지됩니다.

## 에이전트 역할 분리

### spec-builder 전담 영역

- 프로젝트 문서 분석 및 SPEC 후보 발굴
- EARS 구조의 명세서 작성
- Acceptance Criteria 작성 (Given-When-Then)
- SPEC 문서 품질 검증
- @TAG 시스템 적용

### git-manager 전담 영역

- 모든 Git 브랜치 생성 및 관리
- **모드별 브랜치 전략 적용**
  - Personal: `main` 또는 `develop`에서 분기
  - Team: **항상 `develop`에서 분기** (GitFlow)
- GitHub Issue/PR 생성
  - Team 모드: Draft PR 생성 (`feature/SPEC-{ID}` → `develop`)
- 초기 커밋 및 태그 생성
- 원격 동기화 처리

## 2단계 워크플로우 실행 순서

### Phase 1: 분석 및 계획 단계

**계획 분석기**가 다음을 수행:

1. **프로젝트 문서 로딩**: product/structure/tech.md 심층 분석
2. **SPEC 후보 발굴**: 비즈니스 요구사항 기반 우선순위 결정
3. **구현 전략 수립**: EARS 구조 및 Acceptance 설계
4. **작성 계획 생성**: 단계별 계획 작성 접근 방식 제시
5. **사용자 승인 대기**: 계획 검토 및 피드백 수집

### Phase 2: 계획 작성 단계 (승인 후)

`spec-builder` 에이전트가 사용자 승인 후 **연속적으로** 수행:

1. **EARS 명세 작성**: Event-Action-Response-State 구조화
2. **Acceptance Criteria**: Given-When-Then 시나리오 작성
3. **문서 품질 검증**: TRUST 원칙 및 @TAG 적용
4. **템플릿 생성**: spec.md, plan.md, acceptance.md 동시 생성

### Phase 3: Git 작업 (git-manager)

`git-manager` 에이전트가 SPEC 완료 후 **한 번에** 수행:

1. **브랜치 생성**: 모드별 브랜치 전략 적용
2. **GitHub Issue**: Team 모드에서 SPEC Issue 생성
3. **초기 커밋**: SPEC 문서 커밋 및 태그 생성
4. **원격 동기화**: 모드별 동기화 전략 적용

## 작성 팁

- product/structure/tech 문서에 없는 정보는 새로 질문해 보완합니다.
- Acceptance Criteria는 Given/When/Then 3단으로 최소 2개 이상 작성하도록 유도합니다.
- TRUST 원칙 중 Readable(읽기 쉬움) 기준 완화로 인해 모듈 수가 권장치(기본 5)를 초과하는 경우, 근거를 SPEC `context` 섹션에 함께 기록하세요.

---

## 🧠 Context Management (컨텍스트 관리)

> 자세한 내용: `.moai/memory/development-guide.md` - "Context Engineering" 섹션 참조

### 이 커맨드의 핵심 전략

**우선 로드**: `.moai/project/product.md` (비즈니스 요구사항)

**권장사항**: 계획 작성이 완료되었습니다. 다음 단계(`/alfred:2-build`) 진행 전 `/clear` 또는 `/new` 명령으로 새로운 대화 세션을 시작하면 더 나은 성능과 컨텍스트 관리를 경험할 수 있습니다.

---

## 다음 단계

**권장사항**: 다음 단계 진행 전 `/clear` 또는 `/new` 명령으로 새로운 대화 세션을 시작하면 더 나은 성능과 컨텍스트 관리를 경험할 수 있습니다.

- `/alfred:2-build SPEC-XXX`로 TDD 구현 시작
- 팀 모드: Issue 생성 후 git-manager 에이전트가 자동으로 브랜치 생성
