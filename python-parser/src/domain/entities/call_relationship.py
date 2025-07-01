from dataclasses import dataclass, field
from typing import List, Dict, Optional
from pathlib import Path
from datetime import datetime
from enum import Enum


class CallType(Enum):
    """호출 타입 열거형"""

    FUNCTION_CALL = "function_call"
    METHOD_CALL = "method_call"
    CONSTRUCTOR_CALL = "constructor_call"
    IMPORT_CALL = "import_call"


class CallContext(Enum):
    """호출 컨텍스트 열거형"""

    ASSIGNMENT = "assignment"
    RETURN = "return"
    CONDITION = "condition"
    LOOP = "loop"
    EXCEPTION = "exception"
    FUNCTION_CALL = "function_call"


@dataclass
class CallArgument:
    """호출 인자"""

    name: Optional[str] = None
    value: str = ""
    type_hint: Optional[str] = None
    is_keyword: bool = False


@dataclass
class CallRelationship:
    """호출 관계 엔티티"""

    caller_symbol: str
    callee_symbol: str
    call_type: CallType
    file_path: Path
    line_number: int
    column: int
    context: CallContext
    arguments: List[CallArgument] = field(default_factory=list)
    keyword_arguments: Dict[str, str] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """초기화 후 검증"""
        if not self.caller_symbol or not self.callee_symbol:
            raise ValueError("caller_symbol and callee_symbol cannot be empty")

        if self.line_number < 1:
            raise ValueError("line_number must be greater than 0")

    @property
    def is_method_call(self) -> bool:
        """메서드 호출인지 확인"""
        return self.call_type == CallType.METHOD_CALL

    @property
    def is_function_call(self) -> bool:
        """함수 호출인지 확인"""
        return self.call_type == CallType.FUNCTION_CALL

    @property
    def arguments_count(self) -> int:
        """인자 개수"""
        return len(self.arguments)

    @property
    def keyword_arguments_count(self) -> int:
        """키워드 인자 개수"""
        return len(self.keyword_arguments)

    def add_argument(
        self,
        name: Optional[str],
        value: str,
        type_hint: Optional[str] = None,
        is_keyword: bool = False,
    ):
        """인자 추가"""
        argument = CallArgument(
            name=name, value=value, type_hint=type_hint, is_keyword=is_keyword
        )
        self.arguments.append(argument)

    def add_keyword_argument(self, key: str, value: str):
        """키워드 인자 추가"""
        self.keyword_arguments[key] = value

    def to_dict(self) -> dict:
        """딕셔너리로 변환"""
        return {
            "caller_symbol": self.caller_symbol,
            "callee_symbol": self.callee_symbol,
            "call_type": self.call_type.value,
            "file_path": str(self.file_path),
            "line_number": self.line_number,
            "column": self.column,
            "context": self.context.value,
            "arguments": [
                {
                    "name": arg.name,
                    "value": arg.value,
                    "type_hint": arg.type_hint,
                    "is_keyword": arg.is_keyword,
                }
                for arg in self.arguments
            ],
            "keyword_arguments": self.keyword_arguments,
            "arguments_count": self.arguments_count,
            "keyword_arguments_count": self.keyword_arguments_count,
        }
