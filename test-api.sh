#!/bin/bash

# API 테스트 스크립트

echo "🧪 API 테스트 시작"
echo "=================="

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 테스트 함수
test_endpoint() {
    local name="$1"
    local method="$2"
    local url="$3"
    local data="$4"
    
    echo -e "\n${YELLOW}테스트: $name${NC}"
    echo "URL: $url"
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" "$url")
    elif [ "$method" = "POST" ]; then
        response=$(curl -s -w "\n%{http_code}" -X POST -H "Content-Type: application/json" -d "$data" "$url")
    fi
    
    # 응답과 상태 코드 분리
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n -1)
    
    if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
        echo -e "${GREEN}✅ 성공 (HTTP $http_code)${NC}"
        echo "응답: $body" | head -c 200
        [ ${#body} -gt 200 ] && echo "..."
    else
        echo -e "${RED}❌ 실패 (HTTP $http_code)${NC}"
        echo "응답: $body"
    fi
}

# 1. MCP 서버 헬스체크
test_endpoint "MCP 서버 헬스체크" "GET" "http://localhost:8080/actuator/health"

# 2. Python-parser 헬스체크
test_endpoint "Python-parser 헬스체크" "GET" "http://localhost:8009/api/v1/analysis/health"

# 3. 레포지토리 목록 조회
test_endpoint "레포지토리 목록 조회" "GET" "http://localhost:8000/api/v1/analysis/repositories"

# 4. 테스트 레포지토리 클론 (간단한 공개 레포)
test_endpoint "테스트 레포지토리 클론" "POST" "http://localhost:8080/openapi/clone" '{"repoUrl": "https://github.com/octocat/Hello-World.git", "branch": "main"}'

# 5. 클론 후 레포지토리 목록 다시 조회
sleep 3
test_endpoint "클론 후 레포지토리 목록 조회" "GET" "http://localhost:8000/api/v1/analysis/repositories"

# 6. 특정 레포지토리 분석
test_endpoint "Hello-World 레포지토리 분석" "POST" "http://localhost:8009/api/v1/analysis/analyze/shared_repos/ucms-be"

echo -e "\n${GREEN}🎉 API 테스트 완료!${NC}" 