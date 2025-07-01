from abc import ABC, abstractmethod
from typing import List, Dict
from pathlib import Path

from ..entities.code_chunk import CodeChunk, ChunkType


class ChunkRepository(ABC):
    """청크 리포지토리 인터페이스"""

    @abstractmethod
    def save(self, chunk: CodeChunk) -> CodeChunk:
        """청크 저장"""
        pass

    @abstractmethod
    def find_by_type(self, chunk_type: ChunkType) -> List[CodeChunk]:
        """타입으로 청크 조회"""
        pass

    @abstractmethod
    def find_by_file(self, file_path: Path) -> List[CodeChunk]:
        """파일로 청크 조회"""
        pass

    @abstractmethod
    def find_by_module(self, module_path: str) -> List[CodeChunk]:
        """모듈로 청크 조회"""
        pass

    @abstractmethod
    def find_by_symbol(self, symbol_name: str) -> List[CodeChunk]:
        """심볼로 청크 조회"""
        pass

    @abstractmethod
    def find_by_complexity_range(
        self, min_complexity: int, max_complexity: int
    ) -> List[CodeChunk]:
        """복잡도 범위로 청크 조회"""
        pass

    @abstractmethod
    def find_large_chunks(self, min_lines: int) -> List[CodeChunk]:
        """큰 청크 조회"""
        pass

    @abstractmethod
    def get_all(self) -> List[CodeChunk]:
        """모든 청크 조회"""
        pass

    @abstractmethod
    def delete(self, chunk: CodeChunk) -> bool:
        """청크 삭제"""
        pass

    @abstractmethod
    def clear(self) -> None:
        """모든 청크 삭제"""
        pass

    @abstractmethod
    def get_statistics(self) -> Dict[str, any]:
        """통계 정보 조회"""
        pass
