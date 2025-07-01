# Read Me First
The following was discovered as part of building this project:

* The original package name 'com.odk.mediahub.mcp-docs-server' is invalid and this project uses 'com.odk.mediahub.mcp_docs_server' instead.

# Getting Started

### Reference Documentation
For further reference, please consider the following sections:

* [Official Gradle documentation](https://docs.gradle.org)
* [Spring Boot Gradle Plugin Reference Guide](https://docs.spring.io/spring-boot/3.5.3/gradle-plugin)
* [Create an OCI image](https://docs.spring.io/spring-boot/3.5.3/gradle-plugin/packaging-oci-image.html)
* [Spring Web](https://docs.spring.io/spring-boot/3.5.3/reference/web/servlet.html)
* [Thymeleaf](https://docs.spring.io/spring-boot/3.5.3/reference/web/servlet.html#web.servlet.spring-mvc.template-engines)
* [Spring Boot DevTools](https://docs.spring.io/spring-boot/3.5.3/reference/using/devtools.html)

### Guides
The following guides illustrate how to use some features concretely:

* [Building a RESTful Web Service](https://spring.io/guides/gs/rest-service/)
* [Serving Web Content with Spring MVC](https://spring.io/guides/gs/serving-web-content/)
* [Building REST services with Spring](https://spring.io/guides/tutorials/rest/)
* [Handling Form Submission](https://spring.io/guides/gs/handling-form-submission/)

### Additional Links
These additional references should also help you:

* [Gradle Build Scans – insights for your project's build](https://scans.gradle.com#gradle)



### System Structure 
┌────────────────────────────────────────┐
│               Presentation             │ ← Controller (REST API)
└────────────────────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────┐
│             Application Layer          │ ← Service
│ - Business logic orchestration         │
│ - Coordination of repo, utils, AI, etc │
└────────────────────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────┐
│               Domain Layer             │ ← Models (API changes, diff result, etc)
│ - Pure logic: diff, mocking plan, etc  │
└────────────────────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────┐
│             Infrastructure Layer       │ ← Git puller, file I/O, LLM caller
│ - GitHub access                        │
│ - openapi.json reader/parser           │
│ - LLM / Prompt API 호출                 │
│ - HTML 템플릿, 파일 렌더링                 │
└────────────────────────────────────────┘


📁 mcp-docs-server
│
├── 📂 controllers       # REST API (입력 받기)
├── 📂 services          # 비즈니스 로직
├── 📂 domain            # 변경 모델, 결과 모델 등
├── 📂 infrastructure    # Git, OpenAPI diff, 파일 시스템, LLM API
├── 📂 templates         # HTML 템플릿 (Thymeleaf)
└── McpDocsServerApplication.java




#

1. Git Master / Staging
2. Staging 서버 push
3. github actions -> MCP ( push 되었으니 테스트 진행 요청 )
4. MCP - staging pull
5. MCP - staging swagger 생성
6. MCP - Master / Staging swagger 비교 분석
7. MCP - Staging Commit 수정 사항 읽어오기
8. MCP - Staging 수정된 내용을 기준으로 영향을 받는 API 만을 기준으로 테스트 실행
8 - 1. MCP - Staging 영향 받는 API 들 코드 분석
8 - 2. MCP - Staging 자동으로 엣지 케이스 및 정상 적인 케이스에 대한 목 데이터 생성
8 - 3. MCP - Staging 해당 데이터를 기준으로 테스트 실행
9. MCP - Master / Staging 에 대한 비교 및 테스트 결과를 위한 대시보드 또는 페이지 생성
10. MCP - Master <- Staging Merge 후 Master 기준으로 Swagger Api 문서 생성 