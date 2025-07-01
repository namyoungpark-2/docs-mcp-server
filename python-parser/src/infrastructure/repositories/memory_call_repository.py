from typing import List, Dict, Set
from pathlib import Path
from collections import defaultdict

from ...domain.repositories.call_repository import CallRepository
from ...domain.entities.call_relationship import CallRelationship, CallType


class MemoryCallRepository(CallRepository):
    """메모리 기반 호출 관계 리포지토리"""

    def __init__(self):
        self.calls: List[CallRelationship] = []
        self.calls_by_caller: Dict[str, List[CallRelationship]] = defaultdict(list)
        self.calls_by_callee: Dict[str, List[CallRelationship]] = defaultdict(list)
        self.calls_by_type: Dict[CallType, List[CallRelationship]] = defaultdict(list)
        self.calls_by_file: Dict[Path, List[CallRelationship]] = defaultdict(list)
        self.call_graph: Dict[str, Set[str]] = defaultdict(set)
        self.reverse_call_graph: Dict[str, Set[str]] = defaultdict(set)

    def save(self, call: CallRelationship) -> CallRelationship:
        """호출 관계 저장"""
        self.calls.append(call)
        self._add_to_indexes(call)
        self._update_call_graph(call)
        return call

    def find_by_caller(self, caller_symbol: str) -> List[CallRelationship]:
        """호출자로 호출 관계 조회"""
        return self.calls_by_caller[caller_symbol].copy()

    def find_by_callee(self, callee_symbol: str) -> List[CallRelationship]:
        """호출 대상으로 호출 관계 조회"""
        return self.calls_by_callee[callee_symbol].copy()

    def find_by_type(self, call_type: CallType) -> List[CallRelationship]:
        """호출 타입으로 조회"""
        return self.calls_by_type[call_type].copy()

    def find_by_file(self, file_path: Path) -> List[CallRelationship]:
        """파일로 호출 관계 조회"""
        return self.calls_by_file[file_path].copy()

    def find_cycles(self) -> List[List[str]]:
        """순환 호출 찾기"""
        visited = set()
        cycles = []

        def dfs(node: str, path: List[str]):
            if node in path:
                cycle_start = path.index(node)
                cycles.append(path[cycle_start:] + [node])
                return

            if node in visited:
                return

            visited.add(node)
            path.append(node)

            for callee in self.call_graph.get(node, []):
                dfs(callee, path.copy())

        for node in self.call_graph:
            if node not in visited:
                dfs(node, [])

        return cycles

    def get_call_graph(self) -> Dict[str, Set[str]]:
        """호출 그래프 조회"""
        return {k: v.copy() for k, v in self.call_graph.items()}

    def get_reverse_call_graph(self) -> Dict[str, Set[str]]:
        """역방향 호출 그래프 조회"""
        return {k: v.copy() for k, v in self.reverse_call_graph.items()}

    def get_all(self) -> List[CallRelationship]:
        """모든 호출 관계 조회"""
        return self.calls.copy()

    def delete(self, call: CallRelationship) -> bool:
        """호출 관계 삭제"""
        if call in self.calls:
            self.calls.remove(call)
            self._remove_from_indexes(call)
            self._remove_from_call_graph(call)
            return True
        return False

    def clear(self) -> None:
        """모든 호출 관계 삭제"""
        self.calls.clear()
        self.calls_by_caller.clear()
        self.calls_by_callee.clear()
        self.calls_by_type.clear()
        self.calls_by_file.clear()
        self.call_graph.clear()
        self.reverse_call_graph.clear()

    def get_statistics(self) -> Dict[str, any]:
        """통계 정보 조회"""
        total_calls = len(self.calls)
        calls_by_type = {t.value: len(calls) for t, calls in self.calls_by_type.items()}
        calls_by_file = {str(f): len(calls) for f, calls in self.calls_by_file.items()}

        # 가장 많이 호출되는 함수
        callee_counts = defaultdict(int)
        for call in self.calls:
            callee_counts[call.callee_symbol] += 1

        most_called = sorted(callee_counts.items(), key=lambda x: x[1], reverse=True)[
            :5
        ]

        # 가장 많이 호출하는 함수
        caller_counts = defaultdict(int)
        for call in self.calls:
            caller_counts[call.caller_symbol] += 1

        most_calling = sorted(caller_counts.items(), key=lambda x: x[1], reverse=True)[
            :5
        ]

        return {
            "total_calls": total_calls,
            "calls_by_type": calls_by_type,
            "calls_by_file": calls_by_file,
            "most_called_functions": most_called,
            "most_calling_functions": most_calling,
            "cycles": len(self.find_cycles()),
            "unique_callers": len(self.call_graph),
            "unique_callees": len(self.reverse_call_graph),
        }

    def _add_to_indexes(self, call: CallRelationship):
        """인덱스에 호출 관계 추가"""
        self.calls_by_caller[call.caller_symbol].append(call)
        self.calls_by_callee[call.callee_symbol].append(call)
        self.calls_by_type[call.call_type].append(call)
        self.calls_by_file[call.file_path].append(call)

    def _remove_from_indexes(self, call: CallRelationship):
        """인덱스에서 호출 관계 제거"""
        if call in self.calls_by_caller[call.caller_symbol]:
            self.calls_by_caller[call.caller_symbol].remove(call)

        if call in self.calls_by_callee[call.callee_symbol]:
            self.calls_by_callee[call.callee_symbol].remove(call)

        if call in self.calls_by_type[call.call_type]:
            self.calls_by_type[call.call_type].remove(call)

        if call in self.calls_by_file[call.file_path]:
            self.calls_by_file[call.file_path].remove(call)

    def _update_call_graph(self, call: CallRelationship):
        """호출 그래프 업데이트"""
        self.call_graph[call.caller_symbol].add(call.callee_symbol)
        self.reverse_call_graph[call.callee_symbol].add(call.caller_symbol)

    def _remove_from_call_graph(self, call: CallRelationship):
        """호출 그래프에서 제거"""
        if call.callee_symbol in self.call_graph[call.caller_symbol]:
            self.call_graph[call.caller_symbol].remove(call.callee_symbol)

        if call.caller_symbol in self.reverse_call_graph[call.callee_symbol]:
            self.reverse_call_graph[call.callee_symbol].remove(call.caller_symbol)
