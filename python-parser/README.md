# Python Code Analysis API

Clean Architecture와 Domain-Driven Design을 적용한 Python 코드 분석 서비스입니다.

## 🏗️ 아키텍처

### Clean Architecture 구조

```
src/
├── domain/           # 도메인 계층 (비즈니스 로직)
│   ├── entities/     # 도메인 엔티티
│   ├── repositories/ # 리포지토리 인터페이스
│   └── services/     # 도메인 서비스
├── application/      # 애플리케이션 계층 (유스케이스)
│   ├── use_cases/    # 유스케이스
│   ├── interfaces/   # 인터페이스
│   └── dto/          # 데이터 전송 객체
├── infrastructure/   # 인프라 계층 (외부 의존성)
│   ├── parsers/      # 파서 구현
│   └── repositories/ # 리포지토리 구현
└── presentation/     # 프레젠테이션 계층 (API)
    ├── controllers/  # 컨트롤러
    └── schemas/      # API 스키마
```

### 주요 컴포넌트

#### 1. 도메인 엔티티

- **CodeSymbol**: 함수, 클래스, 변수 등의 심볼 정보
- **CallRelationship**: 함수/메서드 호출 관계
- **CodeChunk**: 분석된 코드 청크

#### 2. 리포지토리 패턴

- **SymbolRepository**: 심볼 저장/조회
- **CallRepository**: 호출 관계 저장/조회
- **ChunkRepository**: 코드 청크 저장/조회

#### 3. 유스케이스

- **AnalyzeCodeUseCase**: 코드 분석 메인 로직

#### 4. 파서

- **PythonParser**: Python AST 기반 코드 파싱

## 🚀 설치 및 실행

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. 서버 실행

```bash
python main.py
```

또는

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3. API 문서 확인

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📚 API 사용법

### 1. 코드 업로드 분석

```bash
curl -X POST "http://localhost:8000/api/v1/analysis/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your_project.zip" \
  -F "include_tests=true" \
  -F "include_docs=true"
```

### 2. 디렉토리 분석

```bash
curl -X POST "http://localhost:8000/api/v1/analysis/directory" \
  -H "Content-Type: application/json" \
  -d '{
    "directory_path": "/path/to/your/project",
    "include_tests": true,
    "include_docs": true
  }'
```

### 3. 심볼 조회

```bash
# 모든 심볼 조회
curl "http://localhost:8000/api/v1/analysis/symbols"

# 함수만 조회
curl "http://localhost:8000/api/v1/analysis/symbols?symbol_type=function"

# 특정 모듈 조회
curl "http://localhost:8000/api/v1/analysis/symbols?module_path=my_module"
```

### 4. 호출 관계 조회

```bash
# 모든 호출 관계 조회
curl "http://localhost:8000/api/v1/analysis/calls"

# 특정 함수의 호출 관계 조회
curl "http://localhost:8000/api/v1/analysis/calls?caller=my_function"
```

### 5. 코드 청크 조회

```bash
# 모든 청크 조회
curl "http://localhost:8000/api/v1/analysis/chunks"

# 함수 청크만 조회
curl "http://localhost:8000/api/v1/analysis/chunks?chunk_type=function"
```

### 6. 통계 정보 조회

```bash
curl "http://localhost:8000/api/v1/analysis/statistics"
```

## 🔧 주요 기능

### 1. 코드 파싱

- Python AST 기반 정확한 파싱
- 함수, 클래스, 변수 추출
- 데코레이터, 타입 힌트 분석
- 임포트 관계 분석

### 2. 호출 그래프 분석

- 함수/메서드 호출 관계 추출
- 순환 호출 감지
- 호출 통계 생성
- 의존성 분석

### 3. 코드 청킹

- 함수/클래스 단위 청킹
- 복잡도 계산
- 메타데이터 추출
- LangChain 호환

### 4. 통계 및 분석

- 심볼별 통계
- 호출 패턴 분석
- 복잡도 분포
- 코드 품질 지표

## 🧪 테스트

### 단위 테스트 실행

```bash
python -m pytest tests/ -v
```

### 통합 테스트 실행

```bash
python -m pytest tests/integration/ -v
```

## 📊 분석 결과 예시

### 심볼 정보

```json
{
  "name": "calculate_complexity",
  "type": "function",
  "file_path": "/path/to/file.py",
  "module_path": "my_module",
  "start_line": 10,
  "end_line": 25,
  "signature": "calculate_complexity(code: str) -> int",
  "docstring": "코드 복잡도를 계산합니다.",
  "visibility": "public",
  "decorators": ["@staticmethod"],
  "is_async": false,
  "is_static": true
}
```

### 호출 관계

```json
{
  "caller_symbol": "main",
  "callee_symbol": "calculate_complexity",
  "call_type": "function_call",
  "file_path": "/path/to/file.py",
  "line_number": 15,
  "column": 4,
  "context": "function_call",
  "arguments": ["code_string"],
  "keyword_arguments": {}
}
```

### 코드 청크

```json
{
  "content": "def calculate_complexity(code: str) -> int:\n    # 복잡도 계산 로직\n    return complexity",
  "chunk_type": "function",
  "file_path": "/path/to/file.py",
  "module_path": "my_module",
  "start_line": 10,
  "end_line": 25,
  "symbol_name": "calculate_complexity",
  "complexity": 3,
  "lines_count": 15,
  "characters_count": 120
}
```

## 🔄 확장 가능성

### 1. 새로운 언어 지원

- 새로운 파서 구현
- 언어별 특성 반영
- 통합 분석 지원

### 2. 데이터베이스 연동

- PostgreSQL + pgvector
- 벡터 검색 지원
- 영구 저장소 구현

### 3. 고급 분석 기능

- 코드 품질 메트릭
- 리팩토링 제안
- 보안 취약점 분석

## 🤝 기여하기

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 라이선스

MIT License

# MCP Python API 문서 자동화

## 사용법

### 1. 서버 실행

```bash
cd python-parser
python main.py
```

### 2. API 문서 생성

```bash
curl -X POST "http://localhost:8009/api/v1/docs/generate/ucms-be?base_url=http://localhost:8009" \
  -H "Content-Type: application/json" \
  -d '{"project_path": "/Users/namyoungpark/Downloads/mcp-docs-server-final/shared_repos/ucms-be"}'
```

### 3. 생성된 OpenAPI 문서 위치

- **API 응답**: 위 요청의 응답에서 `documentation` 필드에 OpenAPI 3.0 스펙이 포함되어 있습니다.
- **파일 저장**: 쿼리 파라미터 `save_to_file=true`로 요청 시,
  `python-parser/generated_docs/ucms-be_api_docs.json` 파일로 저장됩니다.

예시:

```bash
curl -X POST "http://localhost:8009/api/v1/docs/generate/ucms-be?base_url=http://localhost:8009&save_to_file=true" \
  -H "Content-Type: application/json" \
  -d '{"project_path": "/Users/namyoungpark/Downloads/mcp-docs-server-final/shared_repos/ucms-be"}'
```

---

## MCP 서버 (Spring Boot)에서 HTML 문서 제공 API 만들기

### 1. Spring Boot Controller 작성

**`src/main/java/com/odk/controller/ApiDocsController.java` 생성:**

```java
package com.odk.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.http.MediaType;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.Map;
import com.fasterxml.jackson.databind.ObjectMapper;

@RestController
public class ApiDocsController {

    @GetMapping(value = "/api-docs/html", produces = MediaType.TEXT_HTML_VALUE)
    public ResponseEntity<String> getApiDocsHtml() {
        try {
            // python-parser에서 생성된 JSON 파일 경로
            String docsPath = "../python-parser/generated_docs/ucms-be_api_docs.json";

            // JSON 파일 읽기
            String jsonContent = new String(Files.readAllBytes(Paths.get(docsPath)));
            ObjectMapper mapper = new ObjectMapper();
            Map<String, Object> openapi = mapper.readValue(jsonContent, Map.class);

            @SuppressWarnings("unchecked")
            Map<String, Object> paths = (Map<String, Object>) openapi.get("paths");

            // HTML 생성
            StringBuilder html = new StringBuilder();
            html.append("""
                <html>
                <head>
                    <title>API 문서</title>
                    <style>
                        body { font-family: sans-serif; margin: 2em; }
                        table { border-collapse: collapse; width: 100%; }
                        th, td { border: 1px solid #ccc; padding: 8px; }
                        th { background: #f5f5f5; }
                        tr:nth-child(even) { background: #fafafa; }
                        .method { font-weight: bold; color: #1565c0; }
                        .path { font-family: monospace; }
                    </style>
                </head>
                <body>
                    <h1>API 문서 (자동 생성)</h1>
                    <table>
                        <tr>
                            <th>Method</th>
                            <th>Path</th>
                            <th>Summary</th>
                        </tr>
                """);

            for (Map.Entry<String, Object> pathEntry : paths.entrySet()) {
                String path = pathEntry.getKey();
                @SuppressWarnings("unchecked")
                Map<String, Object> methods = (Map<String, Object>) pathEntry.getValue();

                for (Map.Entry<String, Object> methodEntry : methods.entrySet()) {
                    String method = methodEntry.getKey();
                    @SuppressWarnings("unchecked")
                    Map<String, Object> info = (Map<String, Object>) methodEntry.getValue();
                    String summary = (String) info.getOrDefault("summary", "");

                    html.append(String.format(
                        "<tr><td class='method'>%s</td><td class='path'>%s</td><td>%s</td></tr>",
                        method.toUpperCase(), path, summary
                    ));
                }
            }

            html.append("""
                    </table>
                    <p style='margin-top:2em;color:#888;'>본 문서는 자동 생성된 OpenAPI 3.0 스펙을 기반으로 합니다.</p>
                </body>
                </html>
                """);

            return ResponseEntity.ok(html.toString());

        } catch (IOException e) {
            return ResponseEntity.status(500)
                .body("<h2>문서 파일을 읽을 수 없습니다: " + e.getMessage() + "</h2>");
        } catch (Exception e) {
            return ResponseEntity.status(500)
                .body("<h2>오류가 발생했습니다: " + e.getMessage() + "</h2>");
        }
    }
}
```

---

## 결과

- **python-parser 서버**: `http://localhost:8009` (API 문서 생성)
- **MCP 서버**: `http://localhost:8000/api-docs/html` (HTML 문서 제공)
- 더 고급 스타일링, 상세 파라미터/스키마/응답 예시 등도 확장 가능합니다.
