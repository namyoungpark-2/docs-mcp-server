import json
from pathlib import Path
from typing import List, Optional, Dict

from ...domain.repositories.api_documentation_repository import (
    ApiDocumentationRepository,
)
from ...domain.entities.api_documentation import ApiDocumentation


class MemoryApiDocumentationRepository(ApiDocumentationRepository):
    """메모리 기반 API 문서 리포지토리"""

    def __init__(self):
        self._documentations: Dict[str, ApiDocumentation] = {}

    def save(self, documentation: ApiDocumentation) -> None:
        """API 문서 저장"""
        project_name = documentation.title.replace(" API Documentation", "")
        self._documentations[project_name] = documentation

    def save_to_file(self, documentation: ApiDocumentation, file_path: Path) -> None:
        """API 문서를 파일로 저장"""
        # OpenAPI JSON 형식으로 저장
        openapi_dict = documentation.to_openapi_dict()

        # 디렉토리 생성
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # JSON 파일로 저장
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(openapi_dict, f, indent=2, ensure_ascii=False)

        # 메모리에도 저장
        self.save(documentation)

    def find_by_project(self, project_name: str) -> Optional[ApiDocumentation]:
        """프로젝트별 API 문서 조회"""
        return self._documentations.get(project_name)

    def get_all(self) -> List[ApiDocumentation]:
        """모든 API 문서 조회"""
        return list(self._documentations.values())

    def delete(self, project_name: str) -> None:
        """API 문서 삭제"""
        if project_name in self._documentations:
            del self._documentations[project_name]

    def clear(self) -> None:
        """모든 API 문서 삭제"""
        self._documentations.clear()

    def get_statistics(self) -> Dict[str, any]:
        """통계 정보 조회"""
        total_docs = len(self._documentations)
        total_endpoints = sum(
            len(doc.endpoints) for doc in self._documentations.values()
        )

        frameworks = {}
        for doc in self._documentations.values():
            framework = doc.info.get("framework", "unknown")
            frameworks[framework] = frameworks.get(framework, 0) + 1

        return {
            "total_documentations": total_docs,
            "total_endpoints": total_endpoints,
            "frameworks": frameworks,
            "projects": list(self._documentations.keys()),
        }
