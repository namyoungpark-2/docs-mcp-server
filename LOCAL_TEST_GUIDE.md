# 로컬 테스트 가이드

Docker 없이 로컬에서 MCP 서버와 Python-parser를 테스트하는 방법을 설명합니다.

## 📋 사전 요구사항

- Java 17 이상
- Python 3.8 이상
- Git
- curl (API 테스트용)

## 🚀 빠른 시작

### 1. 초기 설정

```bash
# 프로젝트 루트에서 실행
./start-local-test.sh
```

이 스크립트는 다음을 수행합니다:

- 공유 디렉토리 생성 (`shared_repos/`)
- Python 가상환경 생성 및 의존성 설치
- MCP 서버 빌드

### 2. 서비스 실행

**터미널 1 - MCP 서버:**

```bash
./gradlew bootRun
```

**터미널 2 - Python-parser:**

```bash
cd python-parser
source venv/bin/activate
python main.py
```

### 3. API 테스트

```bash
./test-api.sh
```

## 📁 디렉토리 구조

```
mcp-docs-server-final/
├── shared_repos/           # 공유 레포지토리 디렉토리
├── python-parser/          # Python-parser 서비스
│   ├── venv/              # Python 가상환경
│   └── src/               # 소스 코드
├── src/                   # MCP 서버 소스 코드
├── start-local-test.sh    # 초기 설정 스크립트
├── test-api.sh           # API 테스트 스크립트
└── ...
```

## 🔧 수동 설정

### 1. 공유 디렉토리 생성

```bash
mkdir -p shared_repos
```

### 2. Python-parser 설정

```bash
cd python-parser

# 가상환경 생성
python3 -m venv venv

# 가상환경 활성화
source venv/bin/activate  # macOS/Linux
# 또는
venv\Scripts\activate     # Windows

# 의존성 설치
pip install -r requirements.txt
```

### 3. MCP 서버 빌드

```bash
./gradlew build -x test
```

## 🧪 API 테스트

### 기본 헬스체크

```bash
# MCP 서버
curl http://localhost:8080/actuator/health

# Python-parser
curl http://localhost:8000/api/v1/analysis/health
```

### 레포지토리 클론 및 분석

```bash
# 1. 레포지토리 클론
curl -X POST http://localhost:8080/openapi/clone \
  -H "Content-Type: application/json" \
  -d '{
    "repoUrl": "https://github.com/octocat/Hello-World.git",
    "branch": "main"
  }'

# 2. 레포지토리 목록 조회
curl http://localhost:8000/api/v1/analysis/repositories

# 3. 특정 레포지토리 분석
curl -X POST http://localhost:8000/api/v1/analysis/analyze/Hello-World

# 4. 모든 레포지토리 분석
curl http://localhost:8000/api/v1/analysis/analyze-all
```

## 🔍 디버깅

### 1. 로그 확인

**MCP 서버 로그:**

```bash
# Gradle 실행 시 로그 레벨 설정
./gradlew bootRun --args='--logging.level.com.odk.mediahub=DEBUG'
```

**Python-parser 로그:**

```bash
# 로그 레벨 설정
export LOG_LEVEL=DEBUG
python main.py
```

### 2. 공유 디렉토리 확인

```bash
# 레포지토리 목록 확인
ls -la shared_repos/

# 특정 레포지토리 내용 확인
ls -la shared_repos/Hello-World/
```

### 3. 포트 확인

```bash
# 사용 중인 포트 확인
lsof -i :8080  # MCP 서버
lsof -i :8000  # Python-parser
```

## 🐛 문제 해결

### 1. 포트 충돌

```bash
# 포트 사용 중인 프로세스 확인
lsof -i :8080
lsof -i :8000

# 프로세스 종료
kill -9 <PID>
```

### 2. 권한 문제

```bash
# 공유 디렉토리 권한 설정
chmod 755 shared_repos/
```

### 3. Python 가상환경 문제

```bash
# 가상환경 재생성
cd python-parser
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Java 빌드 문제

```bash
# Gradle 캐시 정리
./gradlew clean

# 의존성 새로고침
./gradlew --refresh-dependencies build
```

## 📊 모니터링

### 1. 실시간 로그 모니터링

```bash
# MCP 서버 로그
tail -f build/tmp/bootRun/output.txt

# Python-parser 로그 (터미널에서 직접 확인)
```

### 2. 리소스 사용량 확인

```bash
# 프로세스 확인
ps aux | grep java
ps aux | grep python

# 메모리 사용량
top -p $(pgrep java)
top -p $(pgrep python)
```

## 🔄 개발 워크플로우

### 1. 코드 변경 시

**MCP 서버:**

```bash
# 자동 재시작 (Gradle bootRun 사용 시)
# 코드 변경 후 저장하면 자동으로 재시작됨
```

**Python-parser:**

```bash
# 수동 재시작 필요
# Ctrl+C로 중지 후 다시 실행
python main.py
```

### 2. 의존성 변경 시

**Python-parser:**

```bash
cd python-parser
source venv/bin/activate
pip install -r requirements.txt
```

**MCP 서버:**

```bash
./gradlew build
```

## 🎯 테스트 시나리오

### 1. 기본 기능 테스트

```bash
# 1. 서비스 시작 확인
curl http://localhost:8080/actuator/health
curl http://localhost:8000/api/v1/analysis/health

# 2. 레포지토리 클론
curl -X POST http://localhost:8080/openapi/clone \
  -d '{"repoUrl": "https://github.com/octocat/Hello-World.git", "branch": "main"}'

# 3. 분석 실행
curl http://localhost:8000/api/v1/analysis/analyze/Hello-World
```

### 2. 에러 케이스 테스트

```bash
# 존재하지 않는 레포지토리
curl -X POST http://localhost:8000/api/v1/analysis/analyze/nonexistent

# 잘못된 레포지토리 URL
curl -X POST http://localhost:8080/openapi/clone \
  -d '{"repoUrl": "https://github.com/nonexistent/repo.git", "branch": "main"}'
```

이 가이드를 따라하면 Docker 없이도 로컬에서 두 서비스를 테스트할 수 있습니다.
