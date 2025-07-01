#!/bin/bash

# 로컬 테스트 실행 스크립트

echo "🚀 MCP Docs Server 로컬 테스트 시작"

# 공유 디렉토리 확인
SHARED_DIR="./shared_repos"
if [ ! -d "$SHARED_DIR" ]; then
    echo "📁 공유 디렉토리 생성: $SHARED_DIR"
    mkdir -p "$SHARED_DIR"
fi

# Python-parser 의존성 설치
echo "🐍 Python-parser 의존성 설치 중..."
cd python-parser
if [ ! -d "venv" ]; then
    echo "📦 Python 가상환경 생성"
    python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt
cd ..

# MCP 서버 빌드
echo "☕ MCP 서버 빌드 중..."
./gradlew build -x test

echo ""
echo "✅ 준비 완료!"
echo ""
echo "다음 명령어로 서비스를 실행하세요:"
echo ""
echo "1. MCP 서버 실행 (새 터미널에서):"
echo "   ./gradlew bootRun"
echo ""
echo "2. Python-parser 실행 (새 터미널에서):"
echo "   cd python-parser && source venv/bin/activate && python main.py"
echo ""
echo "3. 테스트 API 호출:"
echo "   # MCP 서버 헬스체크:"
echo "   curl http://localhost:8080/actuator/health"
echo ""
echo "   # Python-parser 헬스체크:"
echo "   curl http://localhost:8000/api/v1/analysis/health"
echo ""
echo "   # 레포지토리 클론 (MCP 서버):"
echo "   curl -X POST http://localhost:8080/openapi/clone \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"repoUrl\": \"https://github.com/user/repo.git\", \"branch\": \"main\"}'"
echo ""
echo "   # 레포지토리 분석 (Python-parser):"
echo "   curl http://localhost:8000/api/v1/analysis/repositories"
echo "" 