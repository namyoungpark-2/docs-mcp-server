from abc import ABC, abstractmethod
from typing import List, Optional
from pathlib import Path

from ..entities.api_documentation import ApiDocumentation


class ApiDocumentationRepository(ABC):
    """API 문서 생성 리포지토리 인터페이스"""

    @abstractmethod
    def save(self, documentation: ApiDocumentation) -> None:
        """API 문서 저장"""
        pass

    @abstractmethod
    def save_to_file(self, documentation: ApiDocumentation, file_path: Path) -> None:
        """API 문서를 파일로 저장"""
        pass

    @abstractmethod
    def find_by_project(self, project_name: str) -> Optional[ApiDocumentation]:
        """프로젝트별 API 문서 조회"""
        pass

    @abstractmethod
    def get_all(self) -> List[ApiDocumentation]:
        """모든 API 문서 조회"""
        pass

    @abstractmethod
    def delete(self, project_name: str) -> None:
        """API 문서 삭제"""
        pass

    @abstractmethod
    def clear(self) -> None:
        """모든 API 문서 삭제"""
        pass
