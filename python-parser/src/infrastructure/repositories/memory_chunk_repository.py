from typing import List, Dict
from pathlib import Path
from collections import defaultdict

from ...domain.repositories.chunk_repository import ChunkRepository
from ...domain.entities.code_chunk import CodeChunk, ChunkType


class MemoryChunkRepository(ChunkRepository):
    """메모리 기반 청크 리포지토리"""

    def __init__(self):
        self.chunks: List[CodeChunk] = []
        self.chunks_by_type: Dict[ChunkType, List[CodeChunk]] = defaultdict(list)
        self.chunks_by_file: Dict[Path, List[CodeChunk]] = defaultdict(list)
        self.chunks_by_module: Dict[str, List[CodeChunk]] = defaultdict(list)
        self.chunks_by_symbol: Dict[str, List[CodeChunk]] = defaultdict(list)
        self.chunks_by_complexity: Dict[int, List[CodeChunk]] = defaultdict(list)

    def save(self, chunk: CodeChunk) -> CodeChunk:
        """청크 저장"""
        self.chunks.append(chunk)
        self._add_to_indexes(chunk)
        return chunk

    def find_by_type(self, chunk_type: ChunkType) -> List[CodeChunk]:
        """타입으로 청크 조회"""
        return self.chunks_by_type[chunk_type].copy()

    def find_by_file(self, file_path: Path) -> List[CodeChunk]:
        """파일로 청크 조회"""
        return self.chunks_by_file[file_path].copy()

    def find_by_module(self, module_path: str) -> List[CodeChunk]:
        """모듈로 청크 조회"""
        return self.chunks_by_module[module_path].copy()

    def find_by_symbol(self, symbol_name: str) -> List[CodeChunk]:
        """심볼로 청크 조회"""
        return self.chunks_by_symbol[symbol_name].copy()

    def find_by_complexity_range(
        self, min_complexity: int, max_complexity: int
    ) -> List[CodeChunk]:
        """복잡도 범위로 청크 조회"""
        result = []
        for complexity in range(min_complexity, max_complexity + 1):
            result.extend(self.chunks_by_complexity.get(complexity, []))
        return result

    def find_large_chunks(self, min_lines: int) -> List[CodeChunk]:
        """큰 청크 조회"""
        return [chunk for chunk in self.chunks if chunk.lines_count >= min_lines]

    def get_all(self) -> List[CodeChunk]:
        """모든 청크 조회"""
        return self.chunks.copy()

    def delete(self, chunk: CodeChunk) -> bool:
        """청크 삭제"""
        if chunk in self.chunks:
            self.chunks.remove(chunk)
            self._remove_from_indexes(chunk)
            return True
        return False

    def clear(self) -> None:
        """모든 청크 삭제"""
        self.chunks.clear()
        self.chunks_by_type.clear()
        self.chunks_by_file.clear()
        self.chunks_by_module.clear()
        self.chunks_by_symbol.clear()
        self.chunks_by_complexity.clear()

    def get_statistics(self) -> Dict[str, any]:
        """통계 정보 조회"""
        total_chunks = len(self.chunks)
        chunks_by_type = {
            t.value: len(chunks) for t, chunks in self.chunks_by_type.items()
        }
        chunks_by_file = {
            str(f): len(chunks) for f, chunks in self.chunks_by_file.items()
        }
        chunks_by_module = {
            m: len(chunks) for m, chunks in self.chunks_by_module.items()
        }

        # 복잡도 통계
        complexities = [
            chunk.complexity for chunk in self.chunks if chunk.complexity is not None
        ]
        avg_complexity = sum(complexities) / len(complexities) if complexities else 0
        max_complexity = max(complexities) if complexities else 0
        min_complexity = min(complexities) if complexities else 0

        # 라인 수 통계
        line_counts = [chunk.lines_count for chunk in self.chunks]
        avg_lines = sum(line_counts) / len(line_counts) if line_counts else 0
        max_lines = max(line_counts) if line_counts else 0
        min_lines = min(line_counts) if line_counts else 0

        # 문자 수 통계
        char_counts = [chunk.characters_count for chunk in self.chunks]
        avg_chars = sum(char_counts) / len(char_counts) if char_counts else 0
        max_chars = max(char_counts) if char_counts else 0
        min_chars = min(char_counts) if char_counts else 0

        return {
            "total_chunks": total_chunks,
            "chunks_by_type": chunks_by_type,
            "chunks_by_file": chunks_by_file,
            "chunks_by_module": chunks_by_module,
            "complexity": {
                "average": avg_complexity,
                "max": max_complexity,
                "min": min_complexity,
                "distribution": {
                    str(k): len(v) for k, v in self.chunks_by_complexity.items()
                },
            },
            "lines": {"average": avg_lines, "max": max_lines, "min": min_lines},
            "characters": {"average": avg_chars, "max": max_chars, "min": min_chars},
        }

    def _add_to_indexes(self, chunk: CodeChunk):
        """인덱스에 청크 추가"""
        self.chunks_by_type[chunk.chunk_type].append(chunk)
        self.chunks_by_file[chunk.file_path].append(chunk)
        self.chunks_by_module[chunk.module_path].append(chunk)

        if chunk.symbol_name:
            self.chunks_by_symbol[chunk.symbol_name].append(chunk)

        if chunk.complexity is not None:
            self.chunks_by_complexity[chunk.complexity].append(chunk)

    def _remove_from_indexes(self, chunk: CodeChunk):
        """인덱스에서 청크 제거"""
        if chunk in self.chunks_by_type[chunk.chunk_type]:
            self.chunks_by_type[chunk.chunk_type].remove(chunk)

        if chunk in self.chunks_by_file[chunk.file_path]:
            self.chunks_by_file[chunk.file_path].remove(chunk)

        if chunk in self.chunks_by_module[chunk.module_path]:
            self.chunks_by_module[chunk.module_path].remove(chunk)

        if chunk.symbol_name and chunk in self.chunks_by_symbol[chunk.symbol_name]:
            self.chunks_by_symbol[chunk.symbol_name].remove(chunk)

        if (
            chunk.complexity is not None
            and chunk in self.chunks_by_complexity[chunk.complexity]
        ):
            self.chunks_by_complexity[chunk.complexity].remove(chunk)
