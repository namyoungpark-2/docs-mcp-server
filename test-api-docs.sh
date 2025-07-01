#!/bin/bash

# API 문서 생성 테스트 스크립트

echo "📚 API 문서 생성 테스트 시작"
echo "=============================="

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
    elif [ "$method" = "DELETE" ]; then
        response=$(curl -s -w "\n%{http_code}" -X DELETE "$url")
    fi
    
    # 응답과 상태 코드 분리
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n -1)
    
    if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
        echo -e "${GREEN}✅ 성공 (HTTP $http_code)${NC}"
        echo "응답: $body" | head -c 300
        [ ${#body} -gt 300 ] && echo "..."
    else
        echo -e "${RED}❌ 실패 (HTTP $http_code)${NC}"
        echo "응답: $body"
    fi
}

# 1. 서비스 헬스체크
test_endpoint "서비스 헬스체크" "GET" "http://localhost:8000/"

# 2. API 문서 생성 기능 테스트
echo -e "\n${YELLOW}🔧 API 문서 생성 기능 테스트${NC}"

# 2-1. API 문서 목록 조회 (초기 상태)
test_endpoint "API 문서 목록 조회 (초기)" "GET" "http://localhost:8000/api/v1/docs/list"

# 2-2. 특정 프로젝트 API 문서 생성
test_endpoint "ucms-be API 문서 생성" "POST" "http://localhost:8000/api/v1/docs/generate/ucms-be?base_url=http://localhost:8000&save_to_file=true"

# 2-3. 생성된 API 문서 목록 조회
test_endpoint "API 문서 목록 조회 (생성 후)" "GET" "http://localhost:8000/api/v1/docs/list"

# 2-4. 특정 프로젝트 API 문서 조회
test_endpoint "ucms-be API 문서 조회" "GET" "http://localhost:8000/api/v1/docs/ucms-be"

# 2-5. OpenAPI 스펙 조회
test_endpoint "ucms-be OpenAPI 스펙 조회" "GET" "http://localhost:8000/api/v1/docs/ucms-be/openapi"

# 2-6. 모든 프로젝트 API 문서 생성
test_endpoint "모든 프로젝트 API 문서 생성" "POST" "http://localhost:8000/api/v1/docs/generate-all?base_url=http://localhost:8000&save_to_files=true"

# 2-7. 최종 API 문서 목록 조회
test_endpoint "최종 API 문서 목록 조회" "GET" "http://localhost:8000/api/v1/docs/list"

# 3. 생성된 파일 확인
echo -e "\n${YELLOW}📁 생성된 파일 확인${NC}"
if [ -d "generated_docs" ]; then
    echo "생성된 문서 파일:"
    ls -la generated_docs/
else
    echo "generated_docs 디렉토리가 없습니다."
fi

echo -e "\n${GREEN}🎉 API 문서 생성 테스트 완료!${NC}"
echo ""
echo "📋 사용 가능한 API 엔드포인트:"
echo "  POST /api/v1/docs/generate/{project_name} - 특정 프로젝트 API 문서 생성"
echo "  POST /api/v1/docs/generate-all - 모든 프로젝트 API 문서 생성"
echo "  GET  /api/v1/docs/list - API 문서 목록 조회"
echo "  GET  /api/v1/docs/{project_name} - 특정 프로젝트 API 문서 조회"
echo "  GET  /api/v1/docs/{project_name}/openapi - OpenAPI 스펙 조회"
echo "  DELETE /api/v1/docs/{project_name} - 특정 프로젝트 API 문서 삭제"
echo "  DELETE /api/v1/docs/ - 모든 API 문서 삭제" 