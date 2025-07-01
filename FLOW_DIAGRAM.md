# MCP Docs Server - 전체 동작 흐름

## 1. 코드 기반 API 문서 작성 흐름

```mermaid
graph TD
    A[사용자 요청] --> B[ApiDocsController]
    B --> C[ApiDocsService]
    C --> D[CodeCollectorService]
    D --> E[레포지토리 스캔]
    E --> F[Java 컨트롤러 파일 수집]
    F --> G[API 엔드포인트 파싱]
    G --> H[정규식 패턴 매칭]
    H --> I[엔드포인트 정보 추출]
    I --> J[OpenAPI 스펙 생성]
    J --> K[LLM 프롬프트 생성]
    K --> L[PromptService]
    L --> M[LLM 호출]
    M --> N[향상된 API 문서]
    N --> O[사용자에게 반환]
```

## 2. 코드 기반 테스트 생성 흐름

```mermaid
graph TD
    A[사용자 요청] --> B[TestController]
    B --> C[TestGenerationService]
    C --> D[ApiDocsService]
    D --> E[API 엔드포인트 추출]
    E --> F[엔드포인트별 테스트 생성]
    F --> G[정상 케이스 테스트]
    F --> H[엣지 케이스 테스트]
    F --> I[유닛 테스트]
    F --> J[통합 테스트]
    G --> K[목 데이터 생성]
    H --> K
    I --> K
    J --> K
    K --> L[JUnit 테스트 코드 생성]
    L --> M[테스트 통계 생성]
    M --> N[사용자에게 반환]
```

## 3. 테스트 커버리지 분석 흐름

```mermaid
graph TD
    A[테스트 실행] --> B[코드 커버리지 측정]
    B --> C[라인 커버리지 계산]
    B --> D[브랜치 커버리지 계산]
    B --> E[메서드 커버리지 계산]
    C --> F[커버리지 리포트 생성]
    D --> F
    E --> F
    F --> G[미커버 영역 식별]
    G --> H[추가 테스트 케이스 제안]
    H --> I[커버리지 대시보드 업데이트]
```

## 4. 프론트엔드 대시보드 흐름

```mermaid
graph TD
    A[사용자 접속] --> B[대시보드 페이지 로드]
    B --> C[레포지토리 선택]
    C --> D[API 통계 요청]
    C --> E[테스트 통계 요청]
    C --> F[커버리지 데이터 요청]
    D --> G[차트 렌더링]
    E --> G
    F --> G
    G --> H[대시보드 표시]

    I[API 문서 탭] --> J[엔드포인트 목록 표시]
    J --> K[OpenAPI 스펙 생성]
    K --> L[Swagger UI 렌더링]

    M[테스트 탭] --> N[테스트 케이스 목록]
    N --> O[JUnit 코드 생성]
    O --> P[다운로드 제공]

    Q[커버리지 탭] --> R[커버리지 차트]
    R --> S[미커버 영역 하이라이트]
```

## 5. 전체 시스템 아키텍처

```mermaid
graph TB
    subgraph "Presentation Layer"
        A[Dashboard HTML]
        B[ApiDocsController]
        C[TestController]
        D[CodeAnalysisController]
    end

    subgraph "Service Layer"
        E[ApiDocsService]
        F[TestGenerationService]
        G[CodeCollectorService]
        H[LLMService]
        I[OpenApiDiffService]
    end

    subgraph "Domain Layer"
        J[ApiEndpoint]
        K[TestCase]
        L[TestCoverage]
        M[CodeFile]
        N[RepositoryCode]
    end

    subgraph "Infrastructure Layer"
        O[PromptService]
        P[GitService]
        Q[File System]
    end

    A --> B
    A --> C
    A --> D
    B --> E
    C --> F
    D --> G
    E --> G
    F --> E
    F --> G
    G --> H
    H --> O
    E --> J
    F --> K
    F --> L
    G --> M
    G --> N
    O --> P
    P --> Q
```

## 6. 데이터 흐름

```mermaid
sequenceDiagram
    participant U as 사용자
    participant C as Controller
    participant S as Service
    participant D as Domain
    participant I as Infrastructure

    U->>C: 레포지토리 분석 요청
    C->>S: 코드 수집 요청
    S->>I: 파일 시스템 접근
    I->>S: 코드 파일 반환
    S->>D: 도메인 객체 생성
    D->>S: 분석 결과
    S->>C: 서비스 결과
    C->>U: 응답

    U->>C: API 문서 생성 요청
    C->>S: 엔드포인트 추출
    S->>D: API 엔드포인트 객체
    D->>S: 추출 결과
    S->>I: LLM 호출
    I->>S: 향상된 문서
    S->>C: 문서 결과
    C->>U: API 문서

    U->>C: 테스트 생성 요청
    C->>S: 테스트 케이스 생성
    S->>D: 테스트 객체들
    D->>S: 생성된 테스트
    S->>C: 테스트 결과
    C->>U: 테스트 케이스
```

## 7. 주요 기능별 상세 흐름

### 7.1 API 엔드포인트 추출

1. **파일 스캔**: Java 컨트롤러 파일 식별
2. **정규식 파싱**: `@GetMapping`, `@PostMapping` 등 어노테이션 추출
3. **메타데이터 수집**: 경로, 메서드, 파라미터, 설명 등
4. **OpenAPI 변환**: 표준 OpenAPI 3.0 스펙으로 변환

### 7.2 테스트 케이스 생성

1. **엔드포인트 분석**: 각 API의 특성 파악
2. **테스트 타입 결정**: UNIT, INTEGRATION, E2E, EDGE
3. **목 데이터 생성**: 테스트 타입별 적절한 데이터
4. **JUnit 코드 생성**: 실행 가능한 테스트 코드

### 7.3 커버리지 분석

1. **테스트 실행**: 생성된 테스트 실행
2. **커버리지 측정**: 라인, 브랜치, 메서드 커버리지
3. **미커버 영역 식별**: 테스트되지 않은 코드 부분
4. **추가 테스트 제안**: 커버리지 향상을 위한 테스트 케이스

### 7.4 프론트엔드 대시보드

1. **데이터 수집**: API, 테스트, 커버리지 통계
2. **차트 렌더링**: Chart.js를 사용한 시각화
3. **인터랙티브 기능**: 실시간 데이터 업데이트
4. **다운로드 기능**: 생성된 문서/코드 다운로드
