import ast
from typing import List, Tuple, Optional, Dict
from pathlib import Path

from ...domain.entities.code_symbol import CodeSymbol, SymbolType, Visibility
from ...domain.entities.call_relationship import (
    CallRelationship,
    CallType,
    CallContext,
    CallArgument,
)
from ...domain.entities.code_chunk import CodeChunk, ChunkType


class PythonParser:
    """Python 코드 파서"""

    def __init__(self):
        self.current_class: Optional[str] = None
        self.current_function: Optional[str] = None
        self.import_map: Dict[str, str] = {}

    def parse_file(
        self, file_path: Path
    ) -> Tuple[List[CodeSymbol], List[CallRelationship], List[CodeChunk]]:
        """파일 파싱"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                source = f.read()
        except (UnicodeDecodeError, FileNotFoundError):
            return [], [], []

        try:
            tree = ast.parse(source)
        except SyntaxError:
            return [], [], []

        module_path = self._get_module_path(file_path)
        source_lines = source.splitlines()

        # 1. 임포트 분석
        self._analyze_imports(tree)

        # 2. 심볼 추출
        symbols = self._extract_symbols(tree, file_path, module_path)

        # 3. 호출 관계 분석
        calls = self._extract_calls(tree, file_path, module_path)

        # 4. 코드 청킹
        chunks = self._create_chunks(
            tree, source_lines, file_path, module_path, symbols
        )

        return symbols, calls, chunks

    def _get_module_path(self, file_path: Path) -> str:
        """모듈 경로 생성"""
        # 실제 구현에서는 프로젝트 루트를 기준으로 상대 경로 계산
        return file_path.stem

    def _analyze_imports(self, tree: ast.AST):
        """임포트 분석"""
        self.import_map.clear()

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self.import_map[alias.asname or alias.name] = alias.name

            elif isinstance(node, ast.ImportFrom) and node.module:
                for alias in node.names:
                    imported_name = f"{node.module}.{alias.name}"
                    local_name = alias.asname or alias.name
                    self.import_map[local_name] = imported_name

    def _extract_symbols(
        self, tree: ast.AST, file_path: Path, module_path: str
    ) -> List[CodeSymbol]:
        """심볼 추출"""
        symbols = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                symbol = self._create_class_symbol(node, file_path, module_path)
                symbols.append(symbol)

                # 클래스 내부 탐색
                previous_class = self.current_class
                self.current_class = node.name

                for child in node.body:
                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        child_symbol = self._create_function_symbol(
                            child, file_path, module_path
                        )
                        symbols.append(child_symbol)

                self.current_class = previous_class

            elif (
                isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                and not self.current_class
            ):
                symbol = self._create_function_symbol(node, file_path, module_path)
                symbols.append(symbol)

        return symbols

    def _create_class_symbol(
        self, node: ast.ClassDef, file_path: Path, module_path: str
    ) -> CodeSymbol:
        """클래스 심볼 생성"""
        return CodeSymbol(
            name=node.name,
            type=SymbolType.CLASS,
            file_path=file_path,
            module_path=module_path,
            start_line=node.lineno,
            end_line=getattr(node, "end_lineno", node.lineno),
            docstring=ast.get_docstring(node),
            decorators=[self._get_decorator_name(d) for d in node.decorator_list],
            visibility=self._determine_visibility(node.name),
        )

    def _create_function_symbol(
        self, node: ast.FunctionDef, file_path: Path, module_path: str
    ) -> CodeSymbol:
        """함수 심볼 생성"""
        return CodeSymbol(
            name=node.name,
            type=SymbolType.FUNCTION,
            file_path=file_path,
            module_path=module_path,
            start_line=node.lineno,
            end_line=getattr(node, "end_lineno", node.lineno),
            signature=self._get_function_signature(node),
            docstring=ast.get_docstring(node),
            parent_class=self.current_class,
            decorators=[self._get_decorator_name(d) for d in node.decorator_list],
            is_async=isinstance(node, ast.AsyncFunctionDef),
            visibility=self._determine_visibility(node.name),
        )

    def _get_decorator_name(self, decorator: ast.expr) -> str:
        """데코레이터 이름 추출"""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Attribute):
            return decorator.attr
        elif isinstance(decorator, ast.Call):
            if isinstance(decorator.func, ast.Name):
                return decorator.func.id
            elif isinstance(decorator.func, ast.Attribute):
                return decorator.func.attr
        return "unknown_decorator"

    def _get_function_signature(self, node: ast.FunctionDef) -> str:
        """함수 시그니처 추출"""
        args = [arg.arg for arg in node.args.args]
        # self/cls는 제외
        if args and args[0] in ("self", "cls"):
            args = args[1:]
        if node.args.vararg:
            args.append(f"*{node.args.vararg.arg}")
        if node.args.kwarg:
            args.append(f"**{node.args.kwarg.arg}")
        return f"{node.name}({', '.join(args)})"

    def _determine_visibility(self, name: str) -> Visibility:
        """가시성 판단"""
        if name.startswith("_"):
            return Visibility.PRIVATE
        return Visibility.PUBLIC

    def _extract_calls(
        self, tree: ast.AST, file_path: Path, module_path: str
    ) -> List[CallRelationship]:
        """호출 관계 추출"""
        calls = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # 클래스 내부 탐색
                previous_class = self.current_class
                self.current_class = node.name

                for child in node.body:
                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        child_calls = self._extract_function_calls(
                            child, file_path, module_path
                        )
                        calls.extend(child_calls)

                self.current_class = previous_class

            elif (
                isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                and not self.current_class
            ):
                function_calls = self._extract_function_calls(
                    node, file_path, module_path
                )
                calls.extend(function_calls)

        return calls

    def _extract_function_calls(
        self, node: ast.FunctionDef, file_path: Path, module_path: str
    ) -> List[CallRelationship]:
        """함수 내 호출 추출"""
        calls = []
        function_name = node.name
        if self.current_class:
            function_name = f"{self.current_class}.{function_name}"

        for subnode in ast.walk(node):
            if isinstance(subnode, ast.Call):
                call = self._create_call_relationship(
                    subnode, function_name, file_path, module_path
                )
                if call:
                    calls.append(call)

        return calls

    def _create_call_relationship(
        self, node: ast.Call, caller: str, file_path: Path, module_path: str
    ) -> Optional[CallRelationship]:
        """호출 관계 생성"""
        callee = self._resolve_call_target(node)
        if not callee:
            return None

        call_type = self._determine_call_type(node)
        context = self._determine_call_context(node)

        call = CallRelationship(
            caller_symbol=caller,
            callee_symbol=callee,
            call_type=call_type,
            file_path=file_path,
            line_number=node.lineno,
            column=getattr(node, "col_offset", 0),
            context=context,
        )

        # 인자 분석
        for i, arg in enumerate(node.args):
            argument = CallArgument(
                value=self._get_argument_value(arg), is_keyword=False
            )
            call.add_argument(None, argument.value)

        # 키워드 인자 분석
        for kw in node.keywords:
            call.add_keyword_argument(kw.arg, self._get_argument_value(kw.value))

        return call

    def _resolve_call_target(self, node: ast.Call) -> Optional[str]:
        """호출 대상 해석"""
        if isinstance(node.func, ast.Name):
            return self.import_map.get(node.func.id, node.func.id)

        elif isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                var_name = node.func.value.id
                method_name = node.func.attr

                # self나 cls 메서드 호출
                if var_name in ["self", "cls"] and self.current_class:
                    return f"{self.current_class}.{method_name}"

                # 임포트된 모듈의 메서드 호출
                imported_name = self.import_map.get(var_name)
                if imported_name:
                    return f"{imported_name}.{method_name}"

                return f"{var_name}.{method_name}"

        return None

    def _determine_call_type(self, node: ast.Call) -> CallType:
        """호출 타입 판단"""
        if isinstance(node.func, ast.Attribute):
            return CallType.METHOD_CALL
        return CallType.FUNCTION_CALL

    def _determine_call_context(self, node: ast.Call) -> CallContext:
        """호출 컨텍스트 판단"""
        # 간단한 구현 - 실제로는 더 정교한 로직 필요
        return CallContext.FUNCTION_CALL

    def _get_argument_value(self, node: ast.expr) -> str:
        """인자 값 추출 (ast.Constant만 사용)"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Constant):
            return str(node.value)
        else:
            return "complex_expression"

    def _create_chunks(
        self,
        tree: ast.AST,
        source_lines: List[str],
        file_path: Path,
        module_path: str,
        symbols: List[CodeSymbol],
    ) -> List[CodeChunk]:
        """코드 청킹"""
        chunks = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                chunk = self._create_node_chunk(
                    node, source_lines, file_path, module_path
                )
                if chunk:
                    chunks.append(chunk)

        return chunks

    def _create_node_chunk(
        self, node: ast.AST, source_lines: List[str], file_path: Path, module_path: str
    ) -> Optional[CodeChunk]:
        """노드 청크 생성"""
        start_line = node.lineno - 1
        end_line = getattr(node, "end_lineno", None)

        if not end_line:
            return None

        chunk_lines = source_lines[start_line:end_line]
        chunk_text = "\n".join(chunk_lines)

        chunk_type = self._determine_chunk_type(node)
        symbol_name = getattr(node, "name", None)

        chunk = CodeChunk(
            content=chunk_text,
            chunk_type=chunk_type,
            file_path=file_path,
            module_path=module_path,
            start_line=start_line + 1,
            end_line=end_line,
            symbol_name=symbol_name,
        )

        # 복잡도 계산
        chunk.calculate_complexity()

        return chunk

    def _determine_chunk_type(self, node: ast.AST) -> ChunkType:
        """청크 타입 판단"""
        if isinstance(node, ast.ClassDef):
            return ChunkType.CLASS
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return ChunkType.FUNCTION
        return ChunkType.MODULE
