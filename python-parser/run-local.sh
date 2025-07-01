#!/bin/bash

# Python-parser 로컬 실행 스크립트

echo "🐍 Python-parser 로컬 실행 시작"

# 현재 디렉토리 확인
CURRENT_DIR=$(pwd)
echo "현재 디렉토리: $CURRENT_DIR"

# 공유 디렉토리 경로 설정
SHARED_REPOS_PATH="$CURRENT_DIR/../shared_repos"
echo "공유 디렉토리 경로: $SHARED_REPOS_PATH"

# 공유 디렉토리 존재 확인
if [ ! -d "$SHARED_REPOS_PATH" ]; then
    echo "❌ 공유 디렉토리가 존재하지 않습니다: $SHARED_REPOS_PATH"
    echo "프로젝트 루트에서 ./start-local-test.sh를 먼저 실행하세요."
    exit 1
fi

echo "✅ 공유 디렉토리 확인됨: $SHARED_REPOS_PATH"

# 가상환경 활성화
if [ ! -d "venv" ]; then
    echo "❌ 가상환경이 존재하지 않습니다."
    echo "프로젝트 루트에서 ./start-local-test.sh를 먼저 실행하세요."
    exit 1
fi

echo "🔧 가상환경 활성화 중..."
source venv/bin/activate

# 환경변수 설정
export REPOS_DIRECTORY="$SHARED_REPOS_PATH"
echo "환경변수 설정: REPOS_DIRECTORY=$REPOS_DIRECTORY"

# Python-parser 실행
echo "🚀 Python-parser 시작 중..."
echo "서비스 URL: http://localhost:8000"
echo "API 문서: http://localhost:8000/docs"
echo ""
echo "테스트 명령어:"
echo "  curl http://localhost:8000/api/v1/analysis/health"
echo "  curl http://localhost:8000/api/v1/analysis/repositories"
echo ""

python main.py 