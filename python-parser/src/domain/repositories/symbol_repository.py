from abc import ABC, abstractmethod
from typing import List, Optional, Dict
from pathlib import Path

from ..entities.code_symbol import CodeSymbol, SymbolType


class SymbolRepository(ABC):
    """심볼 리포지토리 인터페이스"""

    @abstractmethod
    def save(self, symbol: CodeSymbol) -> CodeSymbol:
        """심볼 저장"""
        pass

    @abstractmethod
    def find_by_name(self, name: str) -> Optional[CodeSymbol]:
        """이름으로 심볼 조회"""
        pass

    @abstractmethod
    def find_by_type(self, symbol_type: SymbolType) -> List[CodeSymbol]:
        """타입으로 심볼 조회"""
        pass

    @abstractmethod
    def find_by_module(self, module_path: str) -> List[CodeSymbol]:
        """모듈로 심볼 조회"""
        pass

    @abstractmethod
    def find_by_file(self, file_path: Path) -> List[CodeSymbol]:
        """파일로 심볼 조회"""
        pass

    @abstractmethod
    def find_unused_symbols(self) -> List[CodeSymbol]:
        """사용되지 않는 심볼 조회"""
        pass

    @abstractmethod
    def get_all(self) -> List[CodeSymbol]:
        """모든 심볼 조회"""
        pass

    @abstractmethod
    def delete(self, symbol: CodeSymbol) -> bool:
        """심볼 삭제"""
        pass

    @abstractmethod
    def clear(self) -> None:
        """모든 심볼 삭제"""
        pass

    @abstractmethod
    def get_statistics(self) -> Dict[str, any]:
        """통계 정보 조회"""
        pass
