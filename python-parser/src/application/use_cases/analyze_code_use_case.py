from typing import List, Dict, Optional, Any
from pathlib import Path
from dataclasses import dataclass

from ...domain.repositories.call_repository import CallRepository
from ...domain.repositories.chunk_repository import ChunkRepository
from ...domain.entities.code_symbol import CodeSymbol
from ...domain.entities.call_relationship import CallRelationship
from ...domain.entities.code_chunk import CodeChunk
from ...domain.repositories.symbol_repository import SymbolRepository
from ...infrastructure.parsers.hybrid_parser import HybridParser
from ...infrastructure.parsers.python_parser import PythonParser
from ...infrastructure.repositories.memory_symbol_repository import (
    MemorySymbolRepository,
)
from ...infrastructure.repositories.memory_call_repository import MemoryCallRepository
from ...infrastructure.repositories.memory_chunk_repository import MemoryChunkRepository


@dataclass
class AnalysisRequest:
    """분석 요청"""

    project_path: Path
    include_tests: bool = True
    include_docs: bool = True
    max_file_size: Optional[int] = None
    exclude_patterns: List[str] = None

    def __post_init__(self):
        if self.exclude_patterns is None:
            self.exclude_patterns = []


@dataclass
class AnalysisResult:
    """분석 결과"""

    symbols: List[CodeSymbol]
    calls: List[CallRelationship]
    chunks: List[CodeChunk]
    statistics: Dict[str, any]
    duration: float


class AnalyzeCodeUseCase:
    """코드 분석 유스케이스"""

    def __init__(
        self,
        symbol_repository: Optional[SymbolRepository] = None,
        call_repository: Optional[CallRepository] = None,
        chunk_repository: Optional[ChunkRepository] = None,
    ):
        self.hybrid_parser = HybridParser()
        self.python_parser = PythonParser()
        self.symbol_repository = symbol_repository or MemorySymbolRepository()
        self.call_repository = call_repository or MemoryCallRepository()
        self.chunk_repository = chunk_repository or MemoryChunkRepository()

    def execute(self, request: AnalysisRequest) -> AnalysisResult:
        """프로젝트 분석 실행"""
        import time

        start_time = time.time()

        # 기존 데이터 클리어
        self._clear_existing_data()

        # 프로젝트 파일 스캔
        files = self._scan_project_files(request)

        all_symbols = []
        all_calls = []
        all_chunks = []

        # 각 파일 분석
        for file_path in files:
            try:
                symbols, calls, chunks = self._analyze_file(file_path, request)
                all_symbols.extend(symbols)
                all_calls.extend(calls)
                all_chunks.extend(chunks)
            except Exception as e:
                print(f"파일 분석 중 오류 발생: {file_path} - {e}")
                continue

        # 결과 저장
        self._save_analysis_results(all_symbols, all_calls, all_chunks)

        # 통계 생성
        statistics = self._generate_statistics(all_symbols, all_calls, all_chunks)

        duration = time.time() - start_time

        return AnalysisResult(
            symbols=all_symbols,
            calls=all_calls,
            chunks=all_chunks,
            statistics=statistics,
            duration=duration,
        )

    def execute_file(
        self, file_path: str, analysis_type: str = "hybrid"
    ) -> Dict[str, Any]:
        """파일 분석 실행"""
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"파일을 찾을 수 없습니다: {file_path}")

        if analysis_type == "hybrid":
            return self._analyze_with_hybrid_parser(path)
        elif analysis_type == "ast":
            return self._analyze_with_ast_parser(path)
        elif analysis_type == "semantic":
            return self._analyze_with_semantic_parser(path)
        else:
            raise ValueError(f"지원하지 않는 분석 타입: {analysis_type}")

    def _analyze_with_hybrid_parser(self, file_path: Path) -> Dict[str, Any]:
        """하이브리드 파서로 분석"""
        symbols, calls, chunks = self.hybrid_parser.parse_file(file_path)

        # 저장
        for symbol in symbols:
            self.symbol_repository.save(symbol)
        for call in calls:
            self.call_repository.save(call)
        for chunk in chunks:
            self.chunk_repository.save(chunk)

        return {
            "symbols": [symbol.to_dict() for symbol in symbols],
            "calls": [call.to_dict() for call in calls],
            "chunks": [chunk.to_dict() for chunk in chunks],
            "analysis_type": "hybrid",
        }

    def _analyze_with_ast_parser(self, file_path: Path) -> Dict[str, Any]:
        """AST 파서로 분석"""
        symbols, calls = self.python_parser.parse_file(file_path)

        # 저장
        for symbol in symbols:
            self.symbol_repository.save(symbol)
        for call in calls:
            self.call_repository.save(call)

        return {
            "symbols": [symbol.to_dict() for symbol in symbols],
            "calls": [call.to_dict() for call in calls],
            "chunks": [],
            "analysis_type": "ast",
        }

    def _analyze_with_semantic_parser(self, file_path: Path) -> Dict[str, Any]:
        """의미 기반 파서로 분석 (하이브리드의 의미적 부분만)"""
        symbols, calls, chunks = self.hybrid_parser.parse_file(file_path)

        # 의미적 청킹만 필터링
        semantic_chunks = [chunk for chunk in chunks if chunk.chunk_type == "semantic"]

        # 저장
        for symbol in symbols:
            self.symbol_repository.save(symbol)
        for call in calls:
            self.call_repository.save(call)
        for chunk in semantic_chunks:
            self.chunk_repository.save(chunk)

        return {
            "symbols": [symbol.to_dict() for symbol in symbols],
            "calls": [call.to_dict() for call in calls],
            "chunks": [chunk.to_dict() for chunk in semantic_chunks],
            "analysis_type": "semantic",
        }

    def search_semantic(
        self, query: str, file_path: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """의미 기반 코드 검색"""
        if file_path:
            # 특정 파일에서 검색
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(f"파일을 찾을 수 없습니다: {file_path}")

            symbols, calls, chunks = self.hybrid_parser.parse_file(path)
            semantic_chunks = [
                chunk for chunk in chunks if chunk.chunk_type == "semantic"
            ]

            # 쿼리와 매칭되는 청킹 찾기
            results = []
            for chunk in semantic_chunks:
                if self._matches_query(chunk, query):
                    results.append(chunk.to_dict())

            return results
        else:
            # 저장된 모든 청킹에서 검색
            all_chunks = self.chunk_repository.find_all()
            semantic_chunks = [
                chunk for chunk in all_chunks if chunk.chunk_type == "semantic"
            ]

            results = []
            for chunk in semantic_chunks:
                if self._matches_query(chunk, query):
                    results.append(chunk.to_dict())

            return results

    def _matches_query(self, chunk: CodeChunk, query: str) -> bool:
        """쿼리와 청킹 매칭 검사"""
        query_lower = query.lower()

        # 청킹의 의미적 정보에서 검색
        if hasattr(chunk, "semantic_info") and chunk.semantic_info:
            for key, value in chunk.semantic_info.items():
                if isinstance(value, str) and query_lower in value.lower():
                    return True
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, str) and query_lower in item.lower():
                            return True

        # 청킹의 내용에서 검색
        if chunk.content and query_lower in chunk.content.lower():
            return True

        return False

    def get_code_chunks(
        self, file_path: str, chunk_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """코드 청킹 결과 조회"""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"파일을 찾을 수 없습니다: {file_path}")

        symbols, calls, chunks = self.hybrid_parser.parse_file(path)

        if chunk_type == "semantic":
            chunks = [chunk for chunk in chunks if chunk.chunk_type == "semantic"]
        elif chunk_type == "structural":
            chunks = [chunk for chunk in chunks if chunk.chunk_type == "structural"]

        return [chunk.to_dict() for chunk in chunks]

    def _clear_existing_data(self):
        """기존 데이터 클리어"""
        self.symbol_repository.clear()
        self.call_repository.clear()
        self.chunk_repository.clear()

    def _scan_project_files(self, request: AnalysisRequest) -> List[Path]:
        """프로젝트 파일 스캔"""
        files = []

        for file_path in request.project_path.rglob("*.py"):
            # 제외 패턴 확인
            if any(pattern in str(file_path) for pattern in request.exclude_patterns):
                continue

            # 테스트 파일 제외
            if not request.include_tests and self._is_test_file(file_path):
                continue

            # 문서 파일 제외
            if not request.include_docs and self._is_doc_file(file_path):
                continue

            # 파일 크기 확인
            if (
                request.max_file_size
                and file_path.stat().st_size > request.max_file_size
            ):
                continue

            files.append(file_path)

        return files

    def _is_test_file(self, file_path: Path) -> bool:
        """테스트 파일인지 확인"""
        test_patterns = ["test_", "_test.py", "tests/"]
        return any(pattern in str(file_path) for pattern in test_patterns)

    def _is_doc_file(self, file_path: Path) -> bool:
        """문서 파일인지 확인"""
        doc_patterns = ["docs/", "documentation/", "README"]
        return any(pattern in str(file_path) for pattern in doc_patterns)

    def _analyze_file(
        self, file_path: Path, request: AnalysisRequest
    ) -> tuple[List[CodeSymbol], List[CallRelationship], List[CodeChunk]]:
        """파일 분석"""
        # 실제 구현에서는 파서 서비스를 주입받아 사용
        # 여기서는 간단한 예시로 구현
        from ...infrastructure.parsers.python_parser import PythonParser

        parser = PythonParser()
        return parser.parse_file(file_path)

    def _save_analysis_results(
        self,
        symbols: List[CodeSymbol],
        calls: List[CallRelationship],
        chunks: List[CodeChunk],
    ):
        """분석 결과 저장"""
        for symbol in symbols:
            self.symbol_repository.save(symbol)

        for call in calls:
            self.call_repository.save(call)

        for chunk in chunks:
            self.chunk_repository.save(chunk)

    def _generate_statistics(
        self,
        symbols: List[CodeSymbol],
        calls: List[CallRelationship],
        chunks: List[CodeChunk],
    ) -> Dict[str, any]:
        """통계 생성"""
        from collections import Counter

        # 심볼 통계
        symbol_types = Counter(symbol.type.value for symbol in symbols)

        # 호출 통계
        call_types = Counter(call.call_type.value for call in calls)

        # 청크 통계
        chunk_types = Counter(chunk.chunk_type.value for chunk in chunks)

        # 복잡도 통계
        complexities = [
            chunk.complexity for chunk in chunks if chunk.complexity is not None
        ]
        avg_complexity = sum(complexities) / len(complexities) if complexities else 0

        return {
            "total_symbols": len(symbols),
            "total_calls": len(calls),
            "total_chunks": len(chunks),
            "symbol_types": dict(symbol_types),
            "call_types": dict(call_types),
            "chunk_types": dict(chunk_types),
            "average_complexity": avg_complexity,
            "max_complexity": max(complexities) if complexities else 0,
            "min_complexity": min(complexities) if complexities else 0,
        }
