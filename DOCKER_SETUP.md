# Docker 설정 및 사용법

## 개요

이 문서는 MCP 서버와 Python-parser를 Docker 컨테이너로 실행하고, 두 서비스 간에 레포지토리를 공유하는 방법을 설명합니다.

## 아키텍처

```
┌─────────────────┐    ┌─────────────────┐
│   MCP Server    │    │ Python Parser   │
│   (Spring Boot) │    │   (FastAPI)     │
│   Port: 8080    │    │   Port: 8000    │
└─────────────────┘    └─────────────────┘
         │                       │
         └───────────────────────┘
                    │
         ┌─────────────────┐
         │  Shared Volume  │
         │ /shared/repos   │
         └─────────────────┘
```

## 1. Docker 설정 방법

### 1.1 공유 볼륨 설정

두 컨테이너가 같은 볼륨을 마운트하여 레포지토리를 공유합니다:

```yaml
volumes:
  shared_repos: {} # Docker 볼륨 정의

services:
  mcp-server:
    volumes:
      - shared_repos:/shared/repos # MCP 서버에서 마운트

  python-parser:
    volumes:
      - shared_repos:/shared/repos # Python-parser에서 마운트
```

### 1.2 네트워크 설정

두 서비스가 통신할 수 있도록 같은 네트워크에 연결:

```yaml
networks:
  mcp-network:
    driver: bridge

services:
  mcp-server:
    networks:
      - mcp-network

  python-parser:
    networks:
      - mcp-network
```

## 2. 실행 방법

### 2.1 프로덕션 환경

```bash
# 모든 서비스 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 특정 서비스 로그 확인
docker-compose logs -f mcp-server
docker-compose logs -f python-parser
```

### 2.2 개발 환경

```bash
# 개발용 오버라이드 설정과 함께 실행
docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d

# 소스 코드 변경 시 자동 재시작
docker-compose -f docker-compose.yml -f docker-compose.override.yml up --build
```

### 2.3 서비스 중지

```bash
# 모든 서비스 중지
docker-compose down

# 볼륨까지 삭제 (주의: 데이터 손실)
docker-compose down -v
```

## 3. 구체적 사용 예시

### 3.1 Git 트리거 처리 흐름

1. **Git 웹훅 트리거**

   ```
   POST /openapi/clone
   {
     "repoUrl": "https://github.com/user/repo.git",
     "branch": "main"
   }
   ```

2. **MCP 서버에서 레포지토리 클론**

   ```java
   // CodebaseCloner.java
   File destination = new File("/shared/repos/repo-name");
   // Git 클론 실행
   ```

3. **Python-parser에서 분석**
   ```python
   # analysis_controller.py
   repo_path = "/shared/repos/repo-name"
   result = analyze_use_case.execute(repo_path)
   ```

### 3.2 API 호출 예시

```bash
# 1. 레포지토리 클론 (MCP 서버)
curl -X POST http://localhost:8080/openapi/clone \
  -H "Content-Type: application/json" \
  -d '{"repoUrl": "https://github.com/user/repo.git", "branch": "main"}'

# 2. 레포지토리 목록 조회 (Python-parser)
curl http://localhost:8000/api/v1/analysis/repositories

# 3. 특정 레포지토리 분석 (Python-parser)
curl -X POST http://localhost:8000/api/v1/analysis/analyze/repo-name

# 4. 모든 레포지토리 분석 (Python-parser)
curl http://localhost:8000/api/v1/analysis/analyze-all
```

## 4. 레포지토리 버전 관리

### 4.1 브랜치별 관리

```java
// CodebaseCloner.java에서 브랜치별 디렉토리 생성
String repoName = extractRepoName(repoUrl);
String branchDir = repoName + "-" + branch.replace("/", "-");
File destination = new File(reposDir, branchDir);
```

### 4.2 커밋별 스냅샷

```java
// 특정 커밋으로 체크아웃
executeCommand(destination, "git", "checkout", commitHash);
```

### 4.3 버전 정리

```bash
# 오래된 레포지토리 정리 스크립트
#!/bin/bash
REPOS_DIR="/shared/repos"
DAYS_OLD=30

find $REPOS_DIR -type d -name "*.git" -mtime +$DAYS_OLD -exec rm -rf {} \;
```

## 5. 모니터링 및 디버깅

### 5.1 볼륨 확인

```bash
# 공유 볼륨 내용 확인
docker run --rm -v shared_repos:/shared alpine ls -la /shared/repos

# 볼륨 상세 정보
docker volume inspect shared_repos
```

### 5.2 컨테이너 내부 확인

```bash
# MCP 서버 컨테이너 접속
docker-compose exec mcp-server bash

# Python-parser 컨테이너 접속
docker-compose exec python-parser bash

# 공유 디렉토리 확인
ls -la /shared/repos
```

### 5.3 로그 모니터링

```bash
# 실시간 로그 확인
docker-compose logs -f --tail=100

# 특정 서비스 로그 필터링
docker-compose logs -f mcp-server | grep "clone"
docker-compose logs -f python-parser | grep "analysis"
```

## 6. 문제 해결

### 6.1 권한 문제

```bash
# 볼륨 권한 설정
docker run --rm -v shared_repos:/shared alpine chown -R 1000:1000 /shared/repos
```

### 6.2 네트워크 연결 문제

```bash
# 컨테이너 간 통신 테스트
docker-compose exec mcp-server ping python-parser
docker-compose exec python-parser ping mcp-server
```

### 6.3 디스크 공간 부족

```bash
# 볼륨 사용량 확인
docker system df -v

# 불필요한 이미지/컨테이너 정리
docker system prune -a
```

## 7. 성능 최적화

### 7.1 멀티스테이지 빌드

```dockerfile
# Dockerfile.mcp 최적화
FROM openjdk:17-jdk-slim as builder
# 빌드 단계

FROM openjdk:17-jre-slim
# 실행 단계
```

### 7.2 볼륨 캐싱

```yaml
# 자주 변경되지 않는 레이어 캐싱
volumes:
  - ./gradle:/root/.gradle # Gradle 캐시
  - ./maven:/root/.m2 # Maven 캐시
```

이 설정을 통해 MCP 서버와 Python-parser가 효율적으로 통신하고 레포지토리를 공유할 수 있습니다.
