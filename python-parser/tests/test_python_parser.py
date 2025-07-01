import pytest
from pathlib import Path
import tempfile
import os

from src.infrastructure.parsers.python_parser import PythonParser
from src.domain.entities.code_symbol import SymbolType
from src.domain.entities.call_relationship import CallType
from src.domain.entities.code_chunk import ChunkType


class TestPythonParser:
    """Python 파서 테스트"""

    @pytest.fixture
    def parser(self):
        """파서 인스턴스"""
        return PythonParser()

    @pytest.fixture
    def sample_code(self):
        """테스트용 샘플 코드"""
        return '''
import os
from typing import List, Optional

class Calculator:
    """계산기 클래스"""
    
    def __init__(self):
        self.result = 0
    
    def add(self, a: int, b: int) -> int:
        """두 수를 더합니다."""
        return a + b
    
    def multiply(self, a: int, b: int) -> int:
        """두 수를 곱합니다."""
        return a * b

def calculate_sum(numbers: List[int]) -> int:
    """숫자 리스트의 합을 계산합니다."""
    total = 0
    for num in numbers:
        total += num
    return total

def main():
    calc = Calculator()
    result = calc.add(5, 3)
    print(f"Result: {result}")
    
    numbers = [1, 2, 3, 4, 5]
    total = calculate_sum(numbers)
    print(f"Total: {total}")

if __name__ == "__main__":
    main()
'''

    def test_parse_file(self, parser, sample_code):
        """파일 파싱 테스트"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(sample_code)
            file_path = Path(f.name)

        try:
            symbols, calls, chunks = parser.parse_file(file_path)

            # 심볼 테스트
            assert len(symbols) > 0
            assert any(
                s.name == "Calculator" and s.type == SymbolType.CLASS for s in symbols
            )
            assert any(
                s.name == "add" and s.type == SymbolType.FUNCTION for s in symbols
            )
            assert any(
                s.name == "calculate_sum" and s.type == SymbolType.FUNCTION
                for s in symbols
            )

            # 호출 관계 테스트
            assert len(calls) > 0
            assert any(
                c.caller_symbol == "main" and "add" in c.callee_symbol for c in calls
            )

            # 청크 테스트
            assert len(chunks) > 0
            assert any(ch.chunk_type == ChunkType.CLASS for ch in chunks)
            assert any(ch.chunk_type == ChunkType.FUNCTION for ch in chunks)

        finally:
            os.unlink(file_path)

    def test_parse_empty_file(self, parser):
        """빈 파일 파싱 테스트"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("")
            file_path = Path(f.name)

        try:
            symbols, calls, chunks = parser.parse_file(file_path)
            assert len(symbols) == 0
            assert len(calls) == 0
            assert len(chunks) == 0
        finally:
            os.unlink(file_path)

    def test_parse_syntax_error(self, parser):
        """구문 오류 파일 파싱 테스트"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("def invalid syntax {")
            file_path = Path(f.name)

        try:
            symbols, calls, chunks = parser.parse_file(file_path)
            assert len(symbols) == 0
            assert len(calls) == 0
            assert len(chunks) == 0
        finally:
            os.unlink(file_path)

    def test_extract_symbols(self, parser, sample_code):
        """심볼 추출 테스트"""
        import ast

        tree = ast.parse(sample_code)

        symbols = parser._extract_symbols(tree, Path("test.py"), "test_module")

        # 클래스 심볼 확인
        calculator_symbol = next((s for s in symbols if s.name == "Calculator"), None)
        assert calculator_symbol is not None
        assert calculator_symbol.type == SymbolType.CLASS
        assert calculator_symbol.docstring == "계산기 클래스"

        # 함수 심볼 확인
        add_symbol = next((s for s in symbols if s.name == "add"), None)
        assert add_symbol is not None
        assert add_symbol.type == SymbolType.FUNCTION
        assert add_symbol.parent_class == "Calculator"
        assert add_symbol.signature == "add(a, b)"

    def test_extract_calls(self, parser, sample_code):
        """호출 관계 추출 테스트"""
        import ast

        tree = ast.parse(sample_code)

        calls = parser._extract_calls(tree, Path("test.py"), "test_module")

        # 메서드 호출 확인
        method_calls = [c for c in calls if c.call_type == CallType.METHOD_CALL]
        assert len(method_calls) > 0

        # 함수 호출 확인
        function_calls = [c for c in calls if c.call_type == CallType.FUNCTION_CALL]
        assert len(function_calls) > 0

    def test_create_chunks(self, parser, sample_code):
        """코드 청킹 테스트"""
        import ast

        tree = ast.parse(sample_code)
        source_lines = sample_code.splitlines()

        chunks = parser._create_chunks(
            tree, source_lines, Path("test.py"), "test_module", []
        )

        # 클래스 청크 확인
        class_chunks = [ch for ch in chunks if ch.chunk_type == ChunkType.CLASS]
        assert len(class_chunks) > 0

        # 함수 청크 확인
        function_chunks = [ch for ch in chunks if ch.chunk_type == ChunkType.FUNCTION]
        assert len(function_chunks) > 0

        # 복잡도 계산 확인
        for chunk in chunks:
            assert chunk.complexity is not None
            assert chunk.complexity >= 0
