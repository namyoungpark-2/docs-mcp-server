import ast
from typing import List, Tuple, Optional, Dict, Any
from pathlib import Path
import re

from ...domain.entities.code_symbol import CodeSymbol, SymbolType, Visibility
from ...domain.entities.call_relationship import CallRelationship, CallType, CallContext
from ...domain.entities.code_chunk import CodeChunk, ChunkType


class HybridParser:
    """AST + 의미 기반 하이브리드 파서"""

    def __init__(self):
        self.current_class: Optional[str] = None
        self.current_function: Optional[str] = None
        self.import_map: Dict[str, str] = {}
        self.semantic_patterns = self._init_semantic_patterns()

    def _init_semantic_patterns(self) -> Dict[str, List[str]]:
        """의미적 패턴 초기화"""
        return {
            "business_logic": [
                r"calculate.*revenue",
                r"process.*payment",
                r"validate.*user",
                r"generate.*report",
                r"handle.*request",
                r"transform.*data",
                r"compute.*score",
                r"analyze.*performance",
            ],
            "data_processing": [
                r"parse.*json",
                r"convert.*format",
                r"filter.*data",
                r"sort.*list",
                r"aggregate.*results",
                r"normalize.*values",
            ],
            "authentication": [
                r"authenticate.*user",
                r"verify.*token",
                r"check.*permission",
                r"validate.*credentials",
                r"authorize.*access",
            ],
            "database": [
                r"query.*database",
                r"save.*record",
                r"update.*table",
                r"delete.*entry",
                r"fetch.*data",
            ],
            "api": [
                r"handle.*api",
                r"process.*request",
                r"format.*response",
                r"validate.*input",
                r"serialize.*data",
            ],
        }

    def parse_file(
        self, file_path: Path
    ) -> Tuple[List[CodeSymbol], List[CallRelationship], List[CodeChunk]]:
        """하이브리드 파일 파싱"""
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

        # 1. AST 기반 구조 분석
        symbols = self._extract_symbols_ast(tree, file_path, module_path)
        calls = self._extract_calls_ast(tree, file_path, module_path)

        # 2. 의미 기반 청킹
        semantic_chunks = self._create_semantic_chunks(
            tree, source_lines, file_path, module_path, symbols
        )

        # 3. 구조적 청킹 (AST 기반)
        structural_chunks = self._create_structural_chunks(
            tree, source_lines, file_path, module_path, symbols
        )

        # 4. 청킹 통합
        chunks = self._merge_chunks(semantic_chunks, structural_chunks)

        return symbols, calls, chunks

    def _get_module_path(self, file_path: Path) -> str:
        """모듈 경로 생성"""
        return file_path.stem

    def _extract_symbols_ast(
        self, tree: ast.AST, file_path: Path, module_path: str
    ) -> List[CodeSymbol]:
        """AST 기반 심볼 추출"""
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

    def _extract_calls_ast(
        self, tree: ast.AST, file_path: Path, module_path: str
    ) -> List[CallRelationship]:
        """AST 기반 호출 관계 추출"""
        calls = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
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
        for arg in node.args:
            call.add_argument(None, self._get_argument_value(arg))

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

                if var_name in ["self", "cls"] and self.current_class:
                    return f"{self.current_class}.{method_name}"

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
        return CallContext.FUNCTION_CALL

    def _get_argument_value(self, node: ast.expr) -> str:
        """인자 값 추출"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Constant):
            return str(node.value)
        else:
            return "complex_expression"

    def _create_semantic_chunks(
        self,
        tree: ast.AST,
        source_lines: List[str],
        file_path: Path,
        module_path: str,
        symbols: List[CodeSymbol],
    ) -> List[CodeChunk]:
        """의미 기반 청킹"""
        chunks = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                semantic_info = self._analyze_semantic_meaning(node, source_lines)

                if semantic_info["semantic_type"]:
                    chunk = self._create_semantic_chunk(
                        node, source_lines, file_path, module_path, semantic_info
                    )
                    if chunk:
                        chunks.append(chunk)

        return chunks

    def _analyze_semantic_meaning(
        self, node: ast.AST, source_lines: List[str]
    ) -> Dict[str, Any]:
        """의미적 의미 분석"""
        semantic_info = {
            "semantic_type": None,
            "business_domain": None,
            "complexity_level": "simple",
            "key_phrases": [],
        }

        # 함수/클래스 이름 분석
        name = getattr(node, "name", "")
        docstring = ast.get_docstring(node) or ""

        # 소스 코드 추출
        start_line = node.lineno - 1
        end_line = getattr(node, "end_lineno", None)
        if end_line:
            code_lines = source_lines[start_line:end_line]
            code_text = "\n".join(code_lines)
        else:
            code_text = ""

        # 의미적 패턴 매칭
        for semantic_type, patterns in self.semantic_patterns.items():
            for pattern in patterns:
                if re.search(pattern, name.lower()) or re.search(
                    pattern, docstring.lower()
                ):
                    semantic_info["semantic_type"] = semantic_type
                    semantic_info["key_phrases"].append(pattern)
                    break

        # 비즈니스 도메인 추정
        if "revenue" in name.lower() or "payment" in name.lower():
            semantic_info["business_domain"] = "finance"
        elif "user" in name.lower() or "auth" in name.lower():
            semantic_info["business_domain"] = "user_management"
        elif "data" in name.lower() or "process" in name.lower():
            semantic_info["business_domain"] = "data_processing"

        # 복잡도 분석
        if len(code_text.split("\n")) > 50:
            semantic_info["complexity_level"] = "complex"
        elif len(code_text.split("\n")) > 20:
            semantic_info["complexity_level"] = "medium"

        return semantic_info

    def _create_semantic_chunk(
        self,
        node: ast.AST,
        source_lines: List[str],
        file_path: Path,
        module_path: str,
        semantic_info: Dict[str, Any],
    ) -> Optional[CodeChunk]:
        """의미적 청크 생성"""
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

        # 의미적 메타데이터 추가
        chunk.set_metadata("semantic_type", semantic_info["semantic_type"])
        chunk.set_metadata("business_domain", semantic_info["business_domain"])
        chunk.set_metadata("complexity_level", semantic_info["complexity_level"])
        chunk.set_metadata("key_phrases", semantic_info["key_phrases"])
        chunk.set_metadata("is_semantic_chunk", True)

        chunk.calculate_complexity()
        return chunk

    def _create_structural_chunks(
        self,
        tree: ast.AST,
        source_lines: List[str],
        file_path: Path,
        module_path: str,
        symbols: List[CodeSymbol],
    ) -> List[CodeChunk]:
        """구조적 청킹 (AST 기반)"""
        chunks = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                chunk = self._create_structural_chunk(
                    node, source_lines, file_path, module_path
                )
                if chunk:
                    chunks.append(chunk)

        return chunks

    def _create_structural_chunk(
        self, node: ast.AST, source_lines: List[str], file_path: Path, module_path: str
    ) -> Optional[CodeChunk]:
        """구조적 청크 생성"""
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

        # 구조적 메타데이터 추가
        chunk.set_metadata("is_structural_chunk", True)
        chunk.set_metadata("ast_node_type", type(node).__name__)
        chunk.set_metadata("has_docstring", bool(ast.get_docstring(node)))
        chunk.set_metadata("decorator_count", len(getattr(node, "decorator_list", [])))

        chunk.calculate_complexity()
        return chunk

    def _determine_chunk_type(self, node: ast.AST) -> ChunkType:
        """청크 타입 판단"""
        if isinstance(node, ast.ClassDef):
            return ChunkType.CLASS
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return ChunkType.FUNCTION
        return ChunkType.MODULE

    def _merge_chunks(
        self, semantic_chunks: List[CodeChunk], structural_chunks: List[CodeChunk]
    ) -> List[CodeChunk]:
        """청킹 통합"""
        merged_chunks = []

        # 의미적 청킹 우선
        for semantic_chunk in semantic_chunks:
            merged_chunks.append(semantic_chunk)

        # 구조적 청킹에서 중복되지 않는 것만 추가
        for structural_chunk in structural_chunks:
            is_duplicate = False
            for semantic_chunk in semantic_chunks:
                if (
                    structural_chunk.symbol_name == semantic_chunk.symbol_name
                    and structural_chunk.start_line == semantic_chunk.start_line
                ):
                    is_duplicate = True
                    break

            if not is_duplicate:
                merged_chunks.append(structural_chunk)

        return merged_chunks
