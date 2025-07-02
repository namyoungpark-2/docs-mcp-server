import os
from pathlib import Path
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
import traceback

from ...application.use_cases.generate_api_docs_use_case import GenerateApiDocsUseCase
from ...infrastructure.repositories.memory_symbol_repository import (
    MemorySymbolRepository,
)
from ...infrastructure.repositories.memory_api_documentation_repository import (
    MemoryApiDocumentationRepository,
)

router = APIRouter(prefix="/api/v1/docs", tags=["api-documentation"])

# 환경변수에서 공유 디렉토리 설정 가져오기
REPOS_DIRECTORY = os.getenv(
    "REPOS_DIRECTORY", os.path.join(os.path.dirname(os.getcwd()), "shared_repos")
)

# 의존성 주입
symbol_repository = MemorySymbolRepository()
api_documentation_repository = MemoryApiDocumentationRepository()
generate_api_docs_use_case = GenerateApiDocsUseCase(
    symbol_repository=symbol_repository,
    api_documentation_repository=api_documentation_repository,
)


@router.post("/generate/{project_name}")
async def generate_api_documentation(
    project_name: str,
    base_url: str = Query("http://localhost:8000", description="API base URL"),
    save_to_file: bool = Query(False, description="Save documentation to file"),
):
    """특정 프로젝트의 API 문서 생성"""
    try:
        print(f"REPOS_DIRECTORY : {REPOS_DIRECTORY}")
        project_path = Path(REPOS_DIRECTORY) / project_name
        if not project_path.exists():
            raise HTTPException(
                status_code=404, detail=f"Project {project_name} not found"
            )

        # 출력 파일 설정
        output_file = None
        if save_to_file:
            output_dir = Path(os.path.join(os.path.dirname(os.getcwd()), "api-docs"))
            output_dir.mkdir(exist_ok=True)
            output_file = output_dir / f"{project_name}_api_docs.json"

        # API 문서 생성
        result = generate_api_docs_use_case.execute(
            project_path=project_path, base_url=base_url, output_file=output_file
        )

        return {
            "status": "success",
            "message": f"API documentation generated for {project_name}",
            "data": result,
        }

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Error generating API documentation: {str(e)}"
        )


@router.post("/generate-all")
async def generate_all_api_documentations(
    base_url: str = Query("http://localhost:8000", description="API base URL"),
    save_to_files: bool = Query(False, description="Save documentation to files"),
):
    """모든 프로젝트의 API 문서 생성"""
    try:
        projects_dir = Path(REPOS_DIRECTORY)
        if not projects_dir.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Projects directory not found: {REPOS_DIRECTORY}",
            )

        # 출력 디렉토리 설정
        output_dir = None
        if save_to_files:
            output_dir = Path("generated_docs")
            output_dir.mkdir(exist_ok=True)

        # 모든 프로젝트 API 문서 생성
        result = generate_api_docs_use_case.generate_for_all_projects(
            projects_dir=projects_dir, base_url=base_url, output_dir=output_dir
        )

        return {
            "status": "success",
            "message": f"API documentation generated for {result['total_projects']} projects",
            "data": result,
        }

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Error generating API documentation: {str(e)}"
        )


@router.get("/list")
async def list_api_documentations():
    """생성된 API 문서 목록 조회"""
    try:
        result = generate_api_docs_use_case.get_all_documentations()

        return {"status": "success", "data": result}

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Error listing API documentation: {str(e)}"
        )


@router.get("/{project_name}")
async def get_api_documentation(project_name: str):
    """특정 프로젝트의 API 문서 조회"""
    try:
        documentation = generate_api_docs_use_case.get_documentation(project_name)

        if not documentation:
            raise HTTPException(
                status_code=404,
                detail=f"API documentation for {project_name} not found",
            )

        return {
            "status": "success",
            "data": {
                "title": documentation.title,
                "version": documentation.version,
                "description": documentation.description,
                "base_url": documentation.base_url,
                "total_endpoints": len(documentation.endpoints),
                "framework": documentation.info.get("framework", "unknown"),
                "endpoints": [
                    {
                        "path": endpoint.path,
                        "method": endpoint.method.value,
                        "summary": endpoint.summary,
                        "description": endpoint.description,
                        "tags": endpoint.tags,
                    }
                    for endpoint in documentation.endpoints
                ],
                "openapi_spec": documentation.to_openapi_dict(),
            },
        }

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Error retrieving API documentation: {str(e)}"
        )


@router.get("/{project_name}/openapi")
async def get_openapi_spec(project_name: str):
    """특정 프로젝트의 OpenAPI 스펙 조회"""
    try:
        documentation = generate_api_docs_use_case.get_documentation(project_name)

        if not documentation:
            raise HTTPException(
                status_code=404,
                detail=f"API documentation for {project_name} not found",
            )

        return JSONResponse(
            content=documentation.to_openapi_dict(), media_type="application/json"
        )

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Error retrieving OpenAPI spec: {str(e)}"
        )


@router.delete("/{project_name}")
async def delete_api_documentation(project_name: str):
    """특정 프로젝트의 API 문서 삭제"""
    try:
        api_documentation_repository.delete(project_name)

        return {
            "status": "success",
            "message": f"API documentation for {project_name} deleted",
        }

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Error deleting API documentation: {str(e)}"
        )


@router.delete("/")
async def clear_all_api_documentations():
    """모든 API 문서 삭제"""
    try:
        api_documentation_repository.clear()

        return {"status": "success", "message": "All API documentation cleared"}

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Error clearing API documentation: {str(e)}"
        )
