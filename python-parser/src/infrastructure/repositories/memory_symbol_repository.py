from typing import List, Optional, Dict, Set
from pathlib import Path
from collections import defaultdict

from ...domain.repositories.symbol_repository import SymbolRepository
from ...domain.entities.code_symbol import CodeSymbol, SymbolType


class MemorySymbolRepository(SymbolRepository):
    """메모리 기반 심볼 리포지토리"""

    def __init__(self):
        self.symbols: Dict[str, CodeSymbol] = {}
        self.symbols_by_type: Dict[SymbolType, List[CodeSymbol]] = defaultdict(list)
        self.symbols_by_module: Dict[str, List[CodeSymbol]] = defaultdict(list)
        self.symbols_by_file: Dict[Path, List[CodeSymbol]] = defaultdict(list)
        self.references: Dict[str, List[str]] = defaultdict(list)

    def save(self, symbol: CodeSymbol) -> CodeSymbol:
        """심볼 저장"""
        symbol_key = symbol.full_name

        # 기존 심볼 제거
        if symbol_key in self.symbols:
            old_symbol = self.symbols[symbol_key]
            self._remove_from_indexes(old_symbol)

        # 새 심볼 저장
        self.symbols[symbol_key] = symbol
        self._add_to_indexes(symbol)

        return symbol

    def find_by_name(self, name: str) -> Optional[CodeSymbol]:
        """이름으로 심볼 조회"""
        # 정확한 매칭
        if name in self.symbols:
            return self.symbols[name]

        # 부분 매칭
        for symbol_key, symbol in self.symbols.items():
            if symbol.name == name or symbol_key.endswith(f".{name}"):
                return symbol

        return None

    def find_by_type(self, symbol_type: SymbolType) -> List[CodeSymbol]:
        """타입으로 심볼 조회"""
        return self.symbols_by_type[symbol_type].copy()

    def find_by_module(self, module_path: str) -> List[CodeSymbol]:
        """모듈로 심볼 조회"""
        return self.symbols_by_module[module_path].copy()

    def find_by_file(self, file_path: Path) -> List[CodeSymbol]:
        """파일로 심볼 조회"""
        return self.symbols_by_file[file_path].copy()

    def find_unused_symbols(self) -> List[CodeSymbol]:
        """사용되지 않는 심볼 조회"""
        unused = []
        for symbol in self.symbols.values():
            if symbol.full_name not in self.references:
                unused.append(symbol)
        return unused

    def get_all(self) -> List[CodeSymbol]:
        """모든 심볼 조회"""
        return list(self.symbols.values())

    def delete(self, symbol: CodeSymbol) -> bool:
        """심볼 삭제"""
        symbol_key = symbol.full_name
        if symbol_key in self.symbols:
            self._remove_from_indexes(symbol)
            del self.symbols[symbol_key]
            return True
        return False

    def clear(self) -> None:
        """모든 심볼 삭제"""
        self.symbols.clear()
        self.symbols_by_type.clear()
        self.symbols_by_module.clear()
        self.symbols_by_file.clear()
        self.references.clear()

    def get_statistics(self) -> Dict[str, any]:
        """통계 정보 조회"""
        total_symbols = len(self.symbols)
        symbols_by_type = {
            t.value: len(symbols) for t, symbols in self.symbols_by_type.items()
        }
        symbols_by_module = {
            m: len(symbols) for m, symbols in self.symbols_by_module.items()
        }
        symbols_by_file = {
            str(f): len(symbols) for f, symbols in self.symbols_by_file.items()
        }

        return {
            "total_symbols": total_symbols,
            "symbols_by_type": symbols_by_type,
            "symbols_by_module": symbols_by_module,
            "symbols_by_file": symbols_by_file,
            "unused_symbols_count": len(self.find_unused_symbols()),
        }

    def add_reference(self, symbol_name: str, reference: str):
        """심볼 참조 추가"""
        self.references[symbol_name].append(reference)

    def _add_to_indexes(self, symbol: CodeSymbol):
        """인덱스에 심볼 추가"""
        self.symbols_by_type[symbol.type].append(symbol)
        self.symbols_by_module[symbol.module_path].append(symbol)
        self.symbols_by_file[symbol.file_path].append(symbol)

    def _remove_from_indexes(self, symbol: CodeSymbol):
        """인덱스에서 심볼 제거"""
        if symbol in self.symbols_by_type[symbol.type]:
            self.symbols_by_type[symbol.type].remove(symbol)

        if symbol in self.symbols_by_module[symbol.module_path]:
            self.symbols_by_module[symbol.module_path].remove(symbol)

        if symbol in self.symbols_by_file[symbol.file_path]:
            self.symbols_by_file[symbol.file_path].remove(symbol)
