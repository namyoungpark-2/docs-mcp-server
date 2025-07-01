# API 문서 생성기 (API Documentation Generator)

코드 분석 결과를 기반으로 자동으로 API 문서를 생성하는 기능을 추가했습니다.

## 🎯 주요 기능

### 1. **프레임워크 자동 감지**

- Django
- FastAPI
- Flask
- 기타 Python 웹 프레임워크

### 2. **API 엔드포인트 자동 추출**

- URL 패턴 분석
- HTTP 메서드 감지
- 파라미터 추출
- 데코레이터 패턴 분석

### 3. **OpenAPI 3.0 호환 문서 생성**

- 표준 OpenAPI 스펙
- JSON 형식 출력
- Swagger UI 호환

## 🏗️ 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                       │
├─────────────────────────────────────────────────────────────┤
│  api_docs_controller.py - API 문서 생성 컨트롤러            │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                        │
├─────────────────────────────────────────────────────────────┤
│  generate_api_docs_use_case.py - API 문서 생성 유스케이스   │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    Domain Layer                             │
├─────────────────────────────────────────────────────────────┤
│  api_documentation.py - API 문서 도메인 엔티티              │
│  api_documentation_repository.py - 리포지토리 인터페이스    │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                 Infrastructure Layer                        │
├─────────────────────────────────────────────────────────────┤
│  api_documentation_generator.py - API 문서 생성기           │
│  memory_api_documentation_repository.py - 메모리 리포지토리 │
└─────────────────────────────────────────────────────────────┘
```

## 📋 API 엔드포인트

### **1. API 문서 생성**

#### 특정 프로젝트 API 문서 생성

```bash
POST /api/v1/docs/generate/{project_name}
```

**파라미터:**

- `project_name`: 프로젝트 이름 (path)
- `base_url`: API 기본 URL (query, 기본값: http://localhost:8000)
- `save_to_file`: 파일로 저장 여부 (query, 기본값: false)

**예시:**

```bash
curl -X POST "http://localhost:8000/api/v1/docs/generate/ucms-be?base_url=http://localhost:8000&save_to_file=true"
```

#### 모든 프로젝트 API 문서 생성

```bash
POST /api/v1/docs/generate-all
```

**파라미터:**

- `base_url`: API 기본 URL (query, 기본값: http://localhost:8000)
- `save_to_files`: 파일로 저장 여부 (query, 기본값: false)

**예시:**

```bash
curl -X POST "http://localhost:8000/api/v1/docs/generate-all?base_url=http://localhost:8000&save_to_files=true"
```

### **2. API 문서 조회**

#### API 문서 목록 조회

```bash
GET /api/v1/docs/list
```

#### 특정 프로젝트 API 문서 조회

```bash
GET /api/v1/docs/{project_name}
```

#### OpenAPI 스펙 조회

```bash
GET /api/v1/docs/{project_name}/openapi
```

### **3. API 문서 관리**

#### 특정 프로젝트 API 문서 삭제

```bash
DELETE /api/v1/docs/{project_name}
```

#### 모든 API 문서 삭제

```bash
DELETE /api/v1/docs/
```

## 🔧 사용 방법

### **1. 서비스 실행**

**터미널 1 - MCP 서버:**

```bash
./gradlew bootRun
```

**터미널 2 - Python-parser:**

```bash
cd python-parser
./run-local.sh
```

### **2. API 문서 생성**

#### 단일 프로젝트

```bash
# 1. 코드 분석
curl -X POST "http://localhost:8000/api/v1/analysis/analyze/ucms-be"

# 2. API 문서 생성
curl -X POST "http://localhost:8000/api/v1/docs/generate/ucms-be?save_to_file=true"
```

#### 모든 프로젝트

```bash
# 모든 프로젝트 API 문서 생성
curl -X POST "http://localhost:8000/api/v1/docs/generate-all?save_to_files=true"
```

### **3. 생성된 문서 확인**

#### 문서 목록 조회

```bash
curl "http://localhost:8000/api/v1/docs/list"
```

#### 특정 문서 조회

```bash
curl "http://localhost:8000/api/v1/docs/ucms-be"
```

#### OpenAPI 스펙 다운로드

```bash
curl "http://localhost:8000/api/v1/docs/ucms-be/openapi" > ucms-be-openapi.json
```

### **4. 자동 테스트**

```bash
./test-api-docs.sh
```

## 📁 생성된 파일

### **JSON 파일**

- `generated_docs/{project_name}_api_docs.json`
- OpenAPI 3.0 형식
- Swagger UI에서 바로 사용 가능

### **파일 구조**

```
generated_docs/
├── ucms-be_api_docs.json
├── python-parser_api_docs.json
└── ...
```

## 🎨 프레임워크별 지원

### **Django**

- URL 패턴 분석 (`urls.py`)
- View 함수 감지
- DRF (Django REST Framework) 지원
- API View 데코레이터 감지

### **FastAPI**

- 라우터 데코레이터 분석
- HTTP 메서드 자동 감지
- 경로 파라미터 추출
- 의존성 주입 패턴 분석

### **Flask**

- Route 데코레이터 분석
- Blueprint 패턴 지원
- HTTP 메서드 감지
- URL 규칙 분석

## 🔍 코드 분석 기반 추출

### **1. 심볼 분석**

- 함수/메서드 심볼 추출
- 데코레이터 패턴 분석
- 클래스 기반 뷰 감지

### **2. 파일 패턴 분석**

- 정규표현식 기반 패턴 매칭
- 프레임워크별 특화 패턴
- 설정 파일 분석

### **3. 프로젝트 정보 추출**

- `setup.py` 분석
- `pyproject.toml` 분석
- `requirements.txt` 분석

## 📊 응답 예시

### **API 문서 생성 응답**

```json
{
  "status": "success",
  "message": "API documentation generated for ucms-be",
  "data": {
    "project_name": "ucms-be",
    "version": "1.0.0",
    "framework": "django",
    "total_endpoints": 15,
    "base_url": "http://localhost:8000",
    "output_file": "generated_docs/ucms-be_api_docs.json",
    "documentation": {
      "openapi": "3.0.0",
      "info": {
        "title": "ucms-be API Documentation",
        "version": "1.0.0"
      },
      "paths": {
        "/api/users/": {
          "get": {
            "summary": "User list API",
            "tags": ["django"]
          }
        }
      }
    }
  }
}
```

### **API 문서 목록 응답**

```json
{
  "status": "success",
  "data": {
    "statistics": {
      "total_documentations": 2,
      "total_endpoints": 25,
      "frameworks": {
        "django": 1,
        "fastapi": 1
      },
      "projects": ["ucms-be", "python-parser"]
    },
    "documentations": [
      {
        "title": "ucms-be API Documentation",
        "version": "1.0.0",
        "framework": "django",
        "total_endpoints": 15,
        "base_url": "http://localhost:8000"
      }
    ]
  }
}
```

## 🚀 향후 개선 계획

### **1. 고급 기능**

- 요청/응답 스키마 자동 추출
- 인증/인가 정보 분석
- 에러 응답 패턴 분석
- API 버전 관리

### **2. 프레임워크 확장**

- Spring Boot (Java)
- Express.js (Node.js)
- Ruby on Rails
- ASP.NET Core

### **3. 문서 형식 확장**

- Markdown 출력
- HTML 문서 생성
- PDF 생성
- Postman Collection 생성

이제 코드 분석 결과를 기반으로 자동으로 API 문서를 생성할 수 있습니다!
