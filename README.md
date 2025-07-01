# MCP API 문서 자동화 시스템

Django REST Framework ViewSet을 자동으로 분석하여 OpenAPI 3.0 스펙의 API 문서를 생성하는 완전 자동화 시스템입니다.

## 📋 목차

- [프로젝트 개요](#프로젝트-개요)
- [시스템 아키텍처](#시스템-아키텍처)
- [주요 기능](#주요-기능)
- [기술 스택](#기술-스택)
- [프로젝트 구조](#프로젝트-구조)
- [로컬 환경 설정](#로컬-환경-설정)
- [실행 방법](#실행-방법)
- [API 사용법](#api-사용법)
- [구현 상세 내용](#구현-상세-내용)
- [테스트 방법](#테스트-방법)
- [생성된 API 문서 예시](#생성된-api-문서-예시)
- [트러블슈팅](#트러블슈팅)

## 🎯 프로젝트 개요

### 목적

- Django 프로젝트의 ViewSet을 자동으로 탐지하고 분석
- 실제 serializer 필드를 기반으로 정확한 OpenAPI 3.0 스펙 생성
- Request/Response 파라미터, 헤더, 바디 정보 완전 자동화
- Swagger UI를 통한 직관적인 API 문서 제공

### 핵심 특징

- ✅ **완전 자동화**: 수동 설정 없이 ViewSet 자동 탐지
- ✅ **정확한 스키마**: 실제 serializer 필드 1:1 반영
- ✅ **125개 엔드포인트**: 모든 ViewSet CRUD 작업 지원
- ✅ **실시간 생성**: 코드 변경 시 즉시 문서 업데이트
- ✅ **JavaScript 호환**: Swagger UI 완벽 지원

## 🏗️ 시스템 아키텍처

```
┌─────────────────┐    HTTP Request    ┌─────────────────┐
│   MCP Server    │ ──────────────────► │ Python Parser   │
│  (Spring Boot)  │                    │   (FastAPI)     │
│   Port: 8080    │                    │   Port: 8009    │
└─────────────────┘                    └─────────────────┘
         │                                       │
         │                                       │
         ▼                                       ▼
┌─────────────────┐                    ┌─────────────────┐
│   Swagger UI    │                    │ Django Project  │
│  API Docs HTML  │                    │  ViewSet Files  │
│  /api-docs/html │                    │  /shared_repos/ │
└─────────────────┘                    └─────────────────┘
```

### 컴포넌트 설명

1. **Python Parser (FastAPI)**

   - Django ViewSet 자동 탐지 및 분석
   - OpenAPI 3.0 스펙 생성
   - 실제 serializer 필드 추출

2. **MCP Server (Spring Boot)**

   - Swagger UI 제공
   - JSON API 문서 서빙
   - 프록시 역할

3. **Django Project**
   - 분석 대상 ViewSet 파일들
   - 실제 serializer 정의

## 🚀 주요 기능

### 1. ViewSet 자동 탐지

- `app/` 디렉토리 내 모든 앱 스캔
- `views.py` 또는 `views/` 폴더 내 파일 분석
- `class \w+ViewSet` 패턴 자동 발견

### 2. Serializer 필드 추출

- `serializer_class` 속성 자동 감지
- 실제 필드 타입, nullable, required 정보 추출
- 중첩 serializer 지원

### 3. OpenAPI 3.0 스펙 생성

- Request 파라미터 (쿼리, 헤더, 바디)
- Response 스키마 (상태 코드별)
- 인증 정보 (Authorization 헤더)
- Pagination, Search, Filtering 지원

### 4. CRUD 엔드포인트 자동 생성

- **GET** `/api/v1/{resource}/` - 목록 조회
- **POST** `/api/v1/{resource}/` - 생성
- **GET** `/api/v1/{resource}/{id}/` - 상세 조회
- **PUT** `/api/v1/{resource}/{id}/` - 수정
- **DELETE** `/api/v1/{resource}/{id}/` - 삭제

## 🛠️ 기술 스택

### Backend

- **Python 3.12.2**: 메인 파싱 로직
- **FastAPI**: Python Parser 서버
- **Django**: 분석 대상 프로젝트
- **Django REST Framework**: ViewSet 분석

### Frontend

- **Spring Boot**: MCP 서버
- **Swagger UI**: API 문서 인터페이스
- **Thymeleaf**: HTML 템플릿

### 개발 도구

- **Gradle**: Spring Boot 빌드
- **uvicorn**: FastAPI 서버
- **watchfiles**: 자동 리로드

## 📁 프로젝트 구조

```
mcp-docs-server-final/
├── python-parser/                    # Python Parser 서버
│   ├── main.py                      # FastAPI 서버 진입점
│   ├── src/
│   │   ├── application/             # 애플리케이션 레이어
│   │   │   └── use_cases/
│   │   │       └── generate_api_docs_use_case.py
│   │   ├── domain/                  # 도메인 레이어
│   │   │   └── entities/
│   │   │       ├── api_documentation.py
│   │   │       ├── api_endpoint.py
│   │   │       └── api_parameter.py
│   │   ├── infrastructure/          # 인프라 레이어
│   │   │   ├── generators/
│   │   │   │   └── api_documentation_generator.py
│   │   │   └── parsers/
│   │   │       └── python_parser.py
│   │   └── presentation/            # 프레젠테이션 레이어
│   │       └── controllers/
│   │           └── api_docs_controller.py
│   ├── generated_docs/              # 생성된 API 문서
│   │   └── ucms-be_api_docs.json
│   └── requirements.txt
├── shared_repos/                    # 분석 대상 Django 프로젝트
│   └── ucms-be/
│       └── app/
│           ├── account/
│           ├── revenue/
│           ├── content/
│           └── ... (기타 앱들)
├── src/                             # Spring Boot MCP 서버
│   └── main/
│       ├── java/
│       │   └── com/odk/
│       │       └── controller/
│       │           └── ApiDocsController.java
│       └── resources/
│           ├── templates/
│           │   └── swagger-viewer.html
│           └── static/
│               └── openapi/
├── build.gradle                     # Spring Boot 빌드 설정
└── docker-compose.override.yml      # Docker 설정
```

## 🔧 로컬 환경 설정

### 1. Python 환경 설정

```bash
# Python 3.12.2 설치 (pyenv 사용)
pyenv install 3.12.2
pyenv local 3.12.2

# 가상환경 생성 및 활성화
cd python-parser
python -m venv venv
source venv/bin/activate  # macOS/Linux
# 또는
venv\Scripts\activate     # Windows
```

### 2. Python 의존성 설치

```bash
cd python-parser
pip install -r requirements.txt
```

### 3. Spring Boot 환경 설정

```bash
# Java 17 이상 필요
java -version

# Gradle 빌드
./gradlew build
```

## 🚀 실행 방법

### 1. Python Parser 서버 시작

```bash
cd python-parser
python main.py
```

**서버 정보:**

- URL: `http://localhost:8009`
- 자동 리로드: 활성화
- Django 환경: 자동 설정

### 2. Spring Boot MCP 서버 시작

```bash
# 프로젝트 루트에서
./gradlew bootRun
```

**서버 정보:**

- URL: `http://localhost:8080`
- Swagger UI: `http://localhost:8080/api-docs/html`
- JSON API: `http://localhost:8080/api-docs/json`

### 3. API 문서 생성

```bash
# Python Parser 서버가 실행 중인 상태에서
curl -X POST "http://localhost:8009/api/v1/docs/generate/ucms-be?base_url=http://localhost:8009&save_to_file=true"
```

## 📖 API 사용법

### 1. API 문서 생성 엔드포인트

```http
POST /api/v1/docs/generate/{project_name}
```

**파라미터:**

- `project_name`: 프로젝트 이름 (예: ucms-be)
- `base_url`: 기본 URL (예: http://localhost:8009)
- `save_to_file`: 파일 저장 여부 (true/false)

**응답:**

```json
{
  "success": true,
  "message": "API documentation generated successfully",
  "data": {
    "endpoints_count": 125,
    "file_path": "generated_docs/ucms-be_api_docs.json"
  }
}
```

### 2. 생성된 문서 확인

- **Swagger UI**: `http://localhost:8080/api-docs/html`
- **JSON 파일**: `http://localhost:8080/api-docs/json`
- **로컬 파일**: `python-parser/generated_docs/ucms-be_api_docs.json`

## 🔍 구현 상세 내용

### 1. ViewSet 자동 탐지 로직

```python
def discover_viewsets(django_app_path: str) -> List[Tuple[str, str]]:
    """
    Django 앱 디렉토리에서 ViewSet 클래스 자동 탐지

    Args:
        django_app_path: Django 앱 경로

    Returns:
        List[Tuple[앱명.ViewSet명, URL경로]]
    """
    viewsets = []

    # app/ 디렉토리 내 모든 앱 스캔
    for app_dir in os.listdir(django_app_path):
        app_path = os.path.join(django_app_path, app_dir)

        if os.path.isdir(app_path):
            # views.py 파일 확인
            views_file = os.path.join(app_path, "views.py")
            if os.path.exists(views_file):
                viewsets.extend(extract_viewsets_from_file(views_file, app_dir))

            # views/ 폴더 확인
            views_dir = os.path.join(app_path, "views")
            if os.path.isdir(views_dir):
                for file in os.listdir(views_dir):
                    if file.endswith(".py"):
                        file_path = os.path.join(views_dir, file)
                        viewsets.extend(extract_viewsets_from_file(file_path, f"{app_dir}/views/{file[:-3]}"))

    return viewsets
```

### 2. Serializer 필드 추출 로직

```python
def extract_serializer_from_viewset(viewset_class, viewset_name: str) -> Dict[str, Any]:
    """
    ViewSet에서 실제 사용하는 serializer 필드 추출

    Args:
        viewset_class: ViewSet 클래스
        viewset_name: ViewSet 이름

    Returns:
        Dict[str, Any]: 필드 정보 딕셔너리
    """
    try:
        # 1. serializer_class 속성 확인
        if hasattr(viewset_class, 'serializer_class'):
            serializer_class = viewset_class.serializer_class
            return extract_serializer_fields(serializer_class)

        # 2. get_serializer_class 메서드 확인
        if hasattr(viewset_class, 'get_serializer_class'):
            serializer_class = viewset_class.get_serializer_class()
            return extract_serializer_fields(serializer_class)

        # 3. 소스 코드 분석으로 serializer 패턴 찾기
        return extract_serializer_from_source(viewset_class, viewset_name)

    except Exception as e:
        print(f"[문서 자동화] {viewset_name}에서 serializer 필드 추출 실패: {e}")
        return None
```

### 3. OpenAPI 스펙 생성 로직

```python
def generate_openapi_for_viewset(
    viewset_name: str,
    file_path: str,
    base_url: str,
    model_name: str = None,
) -> List[ApiEndpoint]:
    """
    ViewSet에서 OpenAPI 엔드포인트 생성

    Args:
        viewset_name: ViewSet 클래스명
        file_path: ViewSet 파일 경로
        base_url: 기본 URL
        model_name: 모델명 (선택사항)

    Returns:
        List[ApiEndpoint]: 생성된 엔드포인트 목록
    """
    # 1. ViewSet 클래스 import
    viewset_class = import_viewset_class(file_path, viewset_name)

    # 2. Serializer 필드 추출
    serializer_fields = extract_serializer_from_viewset(viewset_class, viewset_name)

    # 3. URL 경로 생성
    resource_name = model_name or viewset_name.replace('ViewSet', '').lower()
    base_path = f"/api/v1/{resource_name}/"

    # 4. CRUD 엔드포인트 생성
    endpoints = []

    # GET /api/v1/{resource}/ - 목록 조회
    endpoints.append(ApiEndpoint(
        path=base_path,
        method=HttpMethod.GET,
        summary=f"Get {resource_name} list",
        description=f"Retrieve a list of {resource_name}",
        parameters=generate_list_parameters(),
        responses=generate_list_responses(serializer_fields)
    ))

    # POST /api/v1/{resource}/ - 생성
    endpoints.append(ApiEndpoint(
        path=base_path,
        method=HttpMethod.POST,
        summary=f"Create {resource_name}",
        description=f"Create a new {resource_name}",
        parameters=generate_create_parameters(),
        request_body=generate_request_body(serializer_fields),
        responses=generate_create_responses(serializer_fields)
    ))

    # 기타 CRUD 엔드포인트들...

    return endpoints
```

## 🧪 테스트 방법

### 1. 단위 테스트

```bash
cd python-parser
python -m pytest tests/
```

### 2. 통합 테스트

```bash
# 1. Python Parser 서버 시작
cd python-parser
python main.py

# 2. API 문서 생성 요청
curl -X POST "http://localhost:8009/api/v1/docs/generate/ucms-be?base_url=http://localhost:8009&save_to_file=true"

# 3. 생성된 파일 확인
ls -la generated_docs/
cat generated_docs/ucms-be_api_docs.json | jq '.paths | keys | length'
```

### 3. Swagger UI 테스트

```bash
# 1. Spring Boot 서버 시작
./gradlew bootRun

# 2. 브라우저에서 확인
open http://localhost:8080/api-docs/html
```

### 4. 엔드포인트별 테스트

```bash
# Revenue API 테스트
curl -X GET "http://localhost:8080/api-docs/json" | jq '.paths | keys | grep revenue'

# AdminUser API 테스트
curl -X GET "http://localhost:8080/api-docs/json" | jq '.paths | keys | grep adminuser'
```

## 📊 생성된 API 문서 예시

### 1. Revenue API 엔드포인트

```json
{
  "/api/v1/revenues/": {
    "get": {
      "summary": "Get revenues list",
      "description": "Retrieve a list of revenues",
      "tags": ["revenue"],
      "parameters": [
        {
          "name": "Authorization",
          "in": "header",
          "required": true,
          "description": "Bearer token for authentication",
          "schema": { "type": "string" }
        },
        {
          "name": "page",
          "in": "query",
          "required": false,
          "description": "Page number for pagination",
          "schema": { "type": "integer" }
        }
      ],
      "responses": {
        "200": {
          "description": "Successful response",
          "content": {
            "application/json": {
              "schema": {
                "type": "object",
                "properties": {
                  "id": { "type": "integer" },
                  "amount": { "type": "number", "format": "decimal" },
                  "currency": { "type": "string" },
                  "created_at": { "type": "string", "format": "date-time" },
                  "updated_at": { "type": "string", "format": "date-time" }
                }
              }
            }
          }
        }
      }
    }
  }
}
```

### 2. 생성된 엔드포인트 통계

- **총 엔드포인트**: 125개
- **ViewSet 개수**: 25개
- **주요 ViewSet**:
  - Revenue (16개 필드)
  - RevenueShare (16개 필드)
  - AdminUser (8개 필드)
  - UserActionHistory (12개 필드)
  - VideoSource (23개 필드)
  - Series (18개 필드)
  - Content (다양한 필드)
  - 기타 모든 ViewSet

## 🔧 트러블슈팅

### 1. Django 환경 설정 문제

**문제**: `DJANGO_SETTINGS_MODULE` 미설정

```bash
Error: No module named 'django'
```

**해결책**:

```python
def setup_django_environment(django_app_path: str):
    """Django 환경 설정"""
    import os
    import sys
    import django

    # Django 설정 모듈 환경변수 설정
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

    # 프로젝트 및 앱 경로를 Python 경로에 추가
    project_root = os.path.dirname(django_app_path)
    sys.path.insert(0, project_root)
    sys.path.insert(0, django_app_path)

    # Django 설정
    django.setup()
```

### 2. ViewSet Import 실패

**문제**: 상대 import 오류

```bash
Error: attempted relative import with no known parent package
```

**해결책**:

```python
def import_viewset_class(file_path: str, viewset_name: str):
    """ViewSet 클래스 import"""
    try:
        # 1. 직접 import 시도
        module_name = get_module_name_from_path(file_path)
        module = importlib.import_module(module_name)
        return getattr(module, viewset_name)
    except ImportError:
        # 2. fallback: 파일 파싱
        return parse_viewset_from_file(file_path, viewset_name)
```

### 3. Serializer 필드 추출 실패

**문제**: `cached_property` 오류

```bash
Error: 'cached_property' object has no attribute 'get_fields'
```

**해결책**:

```python
def extract_serializer_fields(serializer_class):
    """Serializer 필드 추출"""
    try:
        # Serializer 인스턴스 생성
        serializer = serializer_class()

        # fields 속성에 안전하게 접근
        if hasattr(serializer, 'fields'):
            fields = serializer.fields
            return {name: extract_field_schema(field) for name, field in fields.items()}
    except Exception as e:
        print(f"Serializer 필드 추출 실패: {e}")
        return None
```

### 4. JavaScript 호환성 문제

**문제**: Swagger UI에서 `Object.keys()` 오류

```javascript
TypeError: Cannot convert undefined or null to object
```

**해결책**:

```python
def to_openapi_dict(self) -> Dict[str, Any]:
    """OpenAPI 3.0 형식으로 변환"""
    endpoint_dict = {
        "summary": endpoint.summary,
        "description": endpoint.description,
        "tags": endpoint.tags,
        "deprecated": endpoint.deprecated,
        "parameters": [...],
    }

    # null 값 제거로 JavaScript 호환성 확보
    if endpoint.request_body is not None:
        endpoint_dict["requestBody"] = endpoint.request_body

    if endpoint.responses is not None:
        endpoint_dict["responses"] = endpoint.responses

    return endpoint_dict
```

## 📈 성능 최적화

### 1. 캐싱 전략

- ViewSet 클래스 import 결과 캐싱
- Serializer 필드 추출 결과 캐싱
- 파일 변경 감지로 부분 업데이트

### 2. 병렬 처리

- 여러 ViewSet 동시 분석
- 파일 I/O 비동기 처리

### 3. 메모리 최적화

- 불필요한 객체 생성 방지
- 가비지 컬렉션 최적화

## 🔮 향후 개선 계획

### 1. 기능 확장

- [ ] GraphQL 스키마 생성 지원
- [ ] API 버전 관리
- [ ] 커스텀 필터링/정렬 지원
- [ ] API 테스트 코드 자동 생성

### 2. 성능 개선

- [ ] Redis 캐싱 도입
- [ ] 배치 처리 최적화
- [ ] 메모리 사용량 모니터링

### 3. 사용성 개선

- [ ] 웹 인터페이스 추가
- [ ] 실시간 문서 업데이트
- [ ] API 문서 버전 관리

## 📞 지원 및 문의

프로젝트 관련 문의사항이나 버그 리포트는 이슈를 통해 제출해 주세요.

---

**개발자**: AI Assistant  
**최종 업데이트**: 2024년 12월  
**버전**: 1.0.0
