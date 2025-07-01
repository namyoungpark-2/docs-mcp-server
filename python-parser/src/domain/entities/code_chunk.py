from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from pathlib import Path
from datetime import datetime
from enum import Enum


class ChunkType(Enum):
    """청크 타입 열거형"""

    FUNCTION = "function"
    CLASS = "class"
    MODULE = "module"
    LINE_CHUNK = "line_chunk"
    PARTIAL = "partial"


@dataclass
class CodeChunk:
    """코드 청크 엔티티"""

    content: str
    chunk_type: ChunkType
    file_path: Path
    module_path: str
    start_line: int
    end_line: int
    symbol_name: Optional[str] = None
    metadata: Dict[str, any] = field(default_factory=dict)
    calls: List[str] = field(default_factory=list)
    called_by: List[str] = field(default_factory=list)
    dependencies: Set[str] = field(default_factory=set)
    complexity: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """초기화 후 검증"""
        if not self.content:
            raise ValueError("content cannot be empty")

        if self.start_line > self.end_line:
            raise ValueError("start_line must be less than or equal to end_line")

        if not self.file_path:
            raise ValueError("file_path cannot be empty")

    @property
    def lines_count(self) -> int:
        """라인 수"""
        return self.end_line - self.start_line + 1

    @property
    def characters_count(self) -> int:
        """문자 수"""
        return len(self.content)

    @property
    def is_partial(self) -> bool:
        """부분 청크인지 확인"""
        return self.chunk_type == ChunkType.PARTIAL

    @property
    def is_function(self) -> bool:
        """함수 청크인지 확인"""
        return self.chunk_type == ChunkType.FUNCTION

    @property
    def is_class(self) -> bool:
        """클래스 청크인지 확인"""
        return self.chunk_type == ChunkType.CLASS

    def add_call(self, callee: str):
        """호출 관계 추가"""
        if callee not in self.calls:
            self.calls.append(callee)

    def add_called_by(self, caller: str):
        """호출자 관계 추가"""
        if caller not in self.called_by:
            self.called_by.append(caller)

    def add_dependency(self, dependency: str):
        """의존성 추가"""
        self.dependencies.add(dependency)

    def set_metadata(self, key: str, value: any):
        """메타데이터 설정"""
        self.metadata[key] = value

    def get_metadata(self, key: str, default: any = None) -> any:
        """메타데이터 조회"""
        return self.metadata.get(key, default)

    def calculate_complexity(self) -> int:
        """복잡도 계산 (간단한 구현)"""
        # 실제로는 더 정교한 복잡도 계산 알고리즘 사용
        lines = self.content.split("\n")
        complexity = 0

        for line in lines:
            line = line.strip()
            if any(
                keyword in line
                for keyword in [
                    "if ",
                    "elif ",
                    "for ",
                    "while ",
                    "except ",
                    "and ",
                    "or ",
                ]
            ):
                complexity += 1

        self.complexity = complexity
        return complexity

    def to_dict(self) -> dict:
        """딕셔너리로 변환"""
        return {
            "content": self.content,
            "chunk_type": self.chunk_type.value,
            "file_path": str(self.file_path),
            "module_path": self.module_path,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "symbol_name": self.symbol_name,
            "metadata": self.metadata,
            "calls": self.calls,
            "called_by": self.called_by,
            "dependencies": list(self.dependencies),
            "complexity": self.complexity,
            "lines_count": self.lines_count,
            "characters_count": self.characters_count,
            "is_partial": self.is_partial,
        }

    def to_langchain_document(self):
        """LangChain Document로 변환"""
        from langchain.schema import Document

        return Document(
            page_content=self.content,
            metadata={
                "file_path": str(self.file_path),
                "module_path": self.module_path,
                "type": self.chunk_type.value,
                "name": self.symbol_name,
                "start_line": self.start_line,
                "end_line": self.end_line,
                "calls": self.calls,
                "called_by": self.called_by,
                "dependencies": list(self.dependencies),
                "complexity": self.complexity,
                "lines_count": self.lines_count,
                "characters_count": self.characters_count,
                "is_partial": self.is_partial,
                **self.metadata,
            },
        )
