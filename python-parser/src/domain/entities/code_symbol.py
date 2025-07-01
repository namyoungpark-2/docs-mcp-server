from dataclasses import dataclass, field
from typing import List, Optional
from pathlib import Path
from datetime import datetime
from enum import Enum


class SymbolType(Enum):
    """심볼 타입 열거형"""

    FUNCTION = "function"
    CLASS = "class"
    MODULE = "module"
    VARIABLE = "variable"
    IMPORT = "import"


class Visibility(Enum):
    """가시성 열거형"""

    PUBLIC = "public"
    PRIVATE = "private"
    PROTECTED = "protected"


@dataclass
class CodeSymbol:
    """코드 심볼 엔티티"""

    name: str
    type: SymbolType
    file_path: Path
    module_path: str
    start_line: int
    end_line: int
    signature: Optional[str] = None
    docstring: Optional[str] = None
    visibility: Visibility = Visibility.PUBLIC
    decorators: List[str] = field(default_factory=list)
    parent_class: Optional[str] = None
    is_async: bool = False
    is_static: bool = False
    is_abstract: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """초기화 후 검증"""
        if self.start_line > self.end_line:
            raise ValueError("start_line must be less than or equal to end_line")

        if not self.name:
            raise ValueError("name cannot be empty")

    @property
    def full_name(self) -> str:
        """전체 이름 (모듈.심볼)"""
        return f"{self.module_path}.{self.name}"

    @property
    def lines_count(self) -> int:
        """라인 수"""
        return self.end_line - self.start_line + 1

    def is_method(self) -> bool:
        """메서드인지 확인"""
        return self.type == SymbolType.FUNCTION and self.parent_class is not None

    def is_class_method(self) -> bool:
        """클래스 메서드인지 확인"""
        return self.is_method() and "classmethod" in self.decorators

    def is_static_method(self) -> bool:
        """정적 메서드인지 확인"""
        return self.is_method() and "staticmethod" in self.decorators

    def update(self, **kwargs):
        """심볼 정보 업데이트"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.now()

    def to_dict(self) -> dict:
        """딕셔너리로 변환"""
        return {
            "name": self.name,
            "type": self.type.value,
            "file_path": str(self.file_path),
            "module_path": self.module_path,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "signature": self.signature,
            "docstring": self.docstring,
            "visibility": self.visibility.value,
            "decorators": self.decorators,
            "parent_class": self.parent_class,
            "is_async": self.is_async,
            "is_static": self.is_static,
            "is_abstract": self.is_abstract,
            "full_name": self.full_name,
            "lines_count": self.lines_count,
        }
