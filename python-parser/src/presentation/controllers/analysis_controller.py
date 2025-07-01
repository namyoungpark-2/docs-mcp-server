from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import JSONResponse
from typing import Optional
from pathlib import Path
import tempfile
import zipfile
import os

from ...application.use_cases.analyze_code_use_case import (
    AnalyzeCodeUseCase,
    AnalysisRequest,
)
from ...infrastructure.repositories.memory_symbol_repository import (
    MemorySymbolRepository,
)
from ...infrastructure.repositories.memory_call_repository import MemoryCallRepository
from ...infrastructure.repositories.memory_chunk_repository import MemoryChunkRepository
from ...infrastructure.parsers.python_parser import PythonParser

router = APIRouter(prefix="/api/v1/analysis", tags=["analysis"])

# 환경변수에서 공유 디렉토리 설정 가져오기 (로컬 테스트용)
# python-parser 디렉토리에서 상위 디렉토리의 shared_repos를 참조
REPOS_DIRECTORY = os.getenv(
    "REPOS_DIRECTORY", os.path.join(os.path.dirname(os.getcwd()), "shared_repos")
)

# 의존성 주입 (실제로는 DI 컨테이너 사용)
symbol_repository = MemorySymbolRepository()
call_repository = MemoryCallRepository()
chunk_repository = MemoryChunkRepository()
parser = PythonParser()
analyze_use_case = AnalyzeCodeUseCase(
    symbol_repository=symbol_repository,
    call_repository=call_repository,
    chunk_repository=chunk_repository,
)


@router.post("/upload")
async def analyze_uploaded_code(
    file: UploadFile = File(...),
    include_tests: bool = Form(True),
    include_docs: bool = Form(True),
    max_file_size: Optional[int] = Form(None),
):
    """업로드된 코드 분석"""
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            # 파일 압축 해제
            zip_path = Path(tmpdir) / file.filename
            with open(zip_path, "wb") as f:
                f.write(await file.read())

            with zipfile.ZipFile(zip_path) as z:
                z.extractall(tmpdir)

            # 분석 요청 생성
            request = AnalysisRequest(
                project_path=Path(tmpdir),
                include_tests=include_tests,
                include_docs=include_docs,
                max_file_size=max_file_size,
            )

            # 분석 실행
            result = analyze_use_case.execute(request)

            return JSONResponse(
                content={
                    "status": "success",
                    "data": {
                        "symbols_count": len(result.symbols),
                        "calls_count": len(result.calls),
                        "chunks_count": len(result.chunks),
                        "statistics": result.statistics,
                        "duration": result.duration,
                    },
                }
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/directory")
async def analyze_directory(
    directory_path: str,
    include_tests: bool = True,
    include_docs: bool = True,
    max_file_size: Optional[int] = None,
):
    """디렉토리 분석"""
    try:
        project_path = Path(directory_path)
        if not project_path.exists():
            raise HTTPException(status_code=404, detail="Directory not found")

        request = AnalysisRequest(
            project_path=project_path,
            include_tests=include_tests,
            include_docs=include_docs,
            max_file_size=max_file_size,
        )

        result = analyze_use_case.execute(request)

        return JSONResponse(
            content={
                "status": "success",
                "data": {
                    "symbols_count": len(result.symbols),
                    "calls_count": len(result.calls),
                    "chunks_count": len(result.chunks),
                    "statistics": result.statistics,
                    "duration": result.duration,
                },
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/symbols")
async def get_symbols(
    symbol_type: Optional[str] = None,
    module_path: Optional[str] = None,
    file_path: Optional[str] = None,
):
    """심볼 조회"""
    try:
        if symbol_type:
            from ...domain.entities.code_symbol import SymbolType

            symbols = symbol_repository.find_by_type(SymbolType(symbol_type))
        elif module_path:
            symbols = symbol_repository.find_by_module(module_path)
        elif file_path:
            symbols = symbol_repository.find_by_file(Path(file_path))
        else:
            symbols = symbol_repository.get_all()

        return JSONResponse(
            content={
                "status": "success",
                "data": {
                    "symbols": [symbol.to_dict() for symbol in symbols],
                    "count": len(symbols),
                },
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/calls")
async def get_calls(
    caller: Optional[str] = None,
    callee: Optional[str] = None,
    call_type: Optional[str] = None,
):
    """호출 관계 조회"""
    try:
        if caller:
            calls = call_repository.find_by_caller(caller)
        elif callee:
            calls = call_repository.find_by_callee(callee)
        elif call_type:
            from ...domain.entities.call_relationship import CallType

            calls = call_repository.find_by_type(CallType(call_type))
        else:
            calls = call_repository.get_all()

        return JSONResponse(
            content={
                "status": "success",
                "data": {
                    "calls": [call.to_dict() for call in calls],
                    "count": len(calls),
                },
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chunks")
async def get_chunks(
    chunk_type: Optional[str] = None,
    file_path: Optional[str] = None,
    module_path: Optional[str] = None,
):
    """청크 조회"""
    try:
        if chunk_type:
            from ...domain.entities.code_chunk import ChunkType

            chunks = chunk_repository.find_by_type(ChunkType(chunk_type))
        elif file_path:
            chunks = chunk_repository.find_by_file(Path(file_path))
        elif module_path:
            chunks = chunk_repository.find_by_module(module_path)
        else:
            chunks = chunk_repository.get_all()

        return JSONResponse(
            content={
                "status": "success",
                "data": {
                    "chunks": [chunk.to_dict() for chunk in chunks],
                    "count": len(chunks),
                },
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics")
async def get_statistics():
    """통계 정보 조회"""
    try:
        symbol_stats = symbol_repository.get_statistics()
        call_stats = call_repository.get_statistics()
        chunk_stats = chunk_repository.get_statistics()

        return JSONResponse(
            content={
                "status": "success",
                "data": {
                    "symbols": symbol_stats,
                    "calls": call_stats,
                    "chunks": chunk_stats,
                },
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {
        "status": "healthy",
        "service": "Python Code Analysis API",
        "repos_directory": REPOS_DIRECTORY,
        "repos_directory_exists": os.path.exists(REPOS_DIRECTORY),
        "current_working_dir": os.getcwd(),
        "script_location": __file__,
    }


@router.get("/repositories")
async def list_repositories():
    """공유 디렉토리의 모든 레포지토리 목록 조회"""
    try:
        if not os.path.exists(REPOS_DIRECTORY):
            return {
                "repositories": [],
                "message": f"Directory {REPOS_DIRECTORY} does not exist",
            }

        repos = []
        for item in os.listdir(REPOS_DIRECTORY):
            item_path = os.path.join(REPOS_DIRECTORY, item)
            if os.path.isdir(item_path) and os.path.exists(
                os.path.join(item_path, ".git")
            ):
                repos.append({"name": item, "path": item_path, "is_git_repo": True})

        return {
            "repositories": repos,
            "total_count": len(repos),
            "directory": REPOS_DIRECTORY,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error listing repositories: {str(e)}"
        )


@router.post("/analyze/{repo_name}")
async def analyze_repository(repo_name: str):
    """특정 레포지토리 분석"""
    try:
        repo_path = os.path.join(REPOS_DIRECTORY, repo_name)
        if not os.path.exists(repo_path):
            raise HTTPException(
                status_code=404, detail=f"Repository {repo_name} not found"
            )

        # AnalysisRequest 생성
        request = AnalysisRequest(
            project_path=Path(repo_path),
            include_tests=True,
            include_docs=True,
            exclude_patterns=["__pycache__", ".git", "node_modules", "venv"],
        )

        # 레포지토리 분석 실행
        result = analyze_use_case.execute(request)

        return {
            "repository": repo_name,
            "path": repo_path,
            "analysis": {
                "symbols_count": len(result.symbols),
                "calls_count": len(result.calls),
                "chunks_count": len(result.chunks),
                "statistics": result.statistics,
                "duration": result.duration,
            },
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error analyzing repository: {str(e)}"
        )


@router.get("/analyze-all")
async def analyze_all_repositories():
    """모든 레포지토리 분석"""
    try:
        if not os.path.exists(REPOS_DIRECTORY):
            return {
                "repositories": [],
                "message": f"Directory {REPOS_DIRECTORY} does not exist",
            }

        results = []
        for item in os.listdir(REPOS_DIRECTORY):
            item_path = os.path.join(REPOS_DIRECTORY, item)
            if os.path.isdir(item_path) and os.path.exists(
                os.path.join(item_path, ".git")
            ):
                try:
                    request = AnalysisRequest(
                        project_path=Path(item_path),
                        include_tests=True,
                        include_docs=True,
                        exclude_patterns=[
                            "__pycache__",
                            ".git",
                            "node_modules",
                            "venv",
                        ],
                    )
                    result = analyze_use_case.execute(request)
                    results.append(
                        {
                            "repository": item,
                            "path": item_path,
                            "analysis": {
                                "symbols_count": len(result.symbols),
                                "calls_count": len(result.calls),
                                "chunks_count": len(result.chunks),
                                "statistics": result.statistics,
                                "duration": result.duration,
                            },
                        }
                    )
                except Exception as e:
                    results.append(
                        {"repository": item, "path": item_path, "error": str(e)}
                    )

        return {
            "total_repositories": len(results),
            "successful_analyses": len([r for r in results if "error" not in r]),
            "failed_analyses": len([r for r in results if "error" in r]),
            "results": results,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error analyzing all repositories: {str(e)}"
        )


@router.post("/analyze-file")
async def analyze_file(
    file_path: str,
    analysis_type: str = Query(
        "hybrid", description="분석 타입: ast, semantic, hybrid"
    ),
):
    """파일 분석 엔드포인트 - 하이브리드 파서 사용"""
    try:
        result = analyze_use_case.execute_file(file_path, analysis_type)
        return {
            "success": True,
            "file_path": file_path,
            "analysis_type": analysis_type,
            "symbols_count": len(result.get("symbols", [])),
            "calls_count": len(result.get("calls", [])),
            "chunks_count": len(result.get("chunks", [])),
            "data": result,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search-semantic")
async def search_semantic(query: str, file_path: Optional[str] = None):
    """의미 기반 코드 검색 - 하이브리드 파서의 의미적 청킹 활용"""
    try:
        result = analyze_use_case.search_semantic(query, file_path)
        return {
            "success": True,
            "query": query,
            "results_count": len(result),
            "results": result,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/code-chunks")
async def get_code_chunks(
    file_path: str,
    chunk_type: Optional[str] = Query(
        None, description="청킹 타입: semantic, structural, all"
    ),
):
    """코드 청킹 결과 조회"""
    try:
        chunks = analyze_use_case.get_code_chunks(file_path, chunk_type)
        return {
            "success": True,
            "file_path": file_path,
            "chunk_type": chunk_type or "all",
            "chunks_count": len(chunks),
            "chunks": chunks,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
