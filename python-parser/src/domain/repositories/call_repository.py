from abc import ABC, abstractmethod
from typing import List, Dict, Set
from pathlib import Path

from ..entities.call_relationship import CallRelationship, CallType


class CallRepository(ABC):
    """호출 관계 리포지토리 인터페이스"""

    @abstractmethod
    def save(self, call: CallRelationship) -> CallRelationship:
        """호출 관계 저장"""
        pass

    @abstractmethod
    def find_by_caller(self, caller_symbol: str) -> List[CallRelationship]:
        """호출자로 호출 관계 조회"""
        pass

    @abstractmethod
    def find_by_callee(self, callee_symbol: str) -> List[CallRelationship]:
        """호출 대상으로 호출 관계 조회"""
        pass

    @abstractmethod
    def find_by_type(self, call_type: CallType) -> List[CallRelationship]:
        """호출 타입으로 조회"""
        pass

    @abstractmethod
    def find_by_file(self, file_path: Path) -> List[CallRelationship]:
        """파일로 호출 관계 조회"""
        pass

    @abstractmethod
    def find_cycles(self) -> List[List[str]]:
        """순환 호출 찾기"""
        pass

    @abstractmethod
    def get_call_graph(self) -> Dict[str, Set[str]]:
        """호출 그래프 조회"""
        pass

    @abstractmethod
    def get_reverse_call_graph(self) -> Dict[str, Set[str]]:
        """역방향 호출 그래프 조회"""
        pass

    @abstractmethod
    def get_all(self) -> List[CallRelationship]:
        """모든 호출 관계 조회"""
        pass

    @abstractmethod
    def delete(self, call: CallRelationship) -> bool:
        """호출 관계 삭제"""
        pass

    @abstractmethod
    def clear(self) -> None:
        """모든 호출 관계 삭제"""
        pass

    @abstractmethod
    def get_statistics(self) -> Dict[str, any]:
        """통계 정보 조회"""
        pass
