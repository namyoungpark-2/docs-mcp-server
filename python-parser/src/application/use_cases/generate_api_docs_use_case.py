from pathlib import Path
from typing import Optional, Dict, Any

from ...domain.repositories.symbol_repository import SymbolRepository
from ...domain.repositories.api_documentation_repository import (
    ApiDocumentationRepository,
)
from ...domain.entities.api_documentation import ApiDocumentation
from ...infrastructure.generators.api_documentation_generator import (
    generate_api_documentation,
)


class GenerateApiDocsUseCase:
    """API 문서 생성 유스케이스"""

    def __init__(
        self,
        symbol_repository: SymbolRepository,
        api_documentation_repository: ApiDocumentationRepository,
    ):
        self.symbol_repository = symbol_repository
        self.api_documentation_repository = api_documentation_repository

    def execute(
        self,
        project_path: Path,
        base_url: str = "http://localhost:8000",
        output_file: Optional[Path] = None,
    ) -> Dict[str, Any]:
        """API 문서 생성 실행"""

        # 1. 심볼 데이터 조회
        symbols = self.symbol_repository.get_all()

        # 2. API 문서 생성 (함수 직접 호출)
        documentation = generate_api_documentation(
            project_path=project_path, base_url=base_url
        )
        print(f"[DEBUG] 생성된 엔드포인트 개수: {len(documentation.endpoints)}")
        openapi_dict = documentation.to_openapi_dict()
        print(f"[DEBUG] OpenAPI dict keys: {list(openapi_dict.keys())}")
        print(
            f"[DEBUG] OpenAPI paths keys: {list(openapi_dict.get('paths', {}).keys())}"
        )

        # 3. 리포지토리에 저장
        self.api_documentation_repository.save(documentation)

        # 4. 파일로 저장 (옵션)
        if output_file:
            self.api_documentation_repository.save_to_file(documentation, output_file)

        # 5. 결과 반환
        return {
            "project_name": documentation.title.replace(" API Documentation", ""),
            "version": documentation.version,
            "framework": documentation.info.get("framework", "unknown"),
            "total_endpoints": len(documentation.endpoints),
            "base_url": documentation.base_url,
            "output_file": str(output_file) if output_file else None,
            "documentation": documentation.to_openapi_dict(),
        }

    def generate_for_all_projects(
        self,
        projects_dir: Path,
        base_url: str = "http://localhost:8000",
        output_dir: Optional[Path] = None,
    ) -> Dict[str, Any]:
        """모든 프로젝트에 대해 API 문서 생성"""

        results = []

        # 프로젝트 디렉토리 탐색
        for project_path in projects_dir.iterdir():
            if project_path.is_dir() and (project_path / ".git").exists():
                try:
                    # 개별 프로젝트 API 문서 생성
                    output_file = None
                    if output_dir:
                        output_file = output_dir / f"{project_path.name}_api_docs.json"

                    result = self.execute(project_path, base_url, output_file)
                    results.append(result)

                except Exception as e:
                    results.append(
                        {
                            "project_name": project_path.name,
                            "error": str(e),
                            "status": "failed",
                        }
                    )

        return {
            "total_projects": len(results),
            "successful": len([r for r in results if "error" not in r]),
            "failed": len([r for r in results if "error" in r]),
            "results": results,
        }

    def get_documentation(self, project_name: str) -> Optional[ApiDocumentation]:
        """프로젝트별 API 문서 조회"""
        return self.api_documentation_repository.find_by_project(project_name)

    def get_all_documentations(self) -> Dict[str, Any]:
        """모든 API 문서 조회"""
        docs = self.api_documentation_repository.get_all()
        stats = self.api_documentation_repository.get_statistics()

        return {
            "statistics": stats,
            "documentations": [
                {
                    "title": doc.title,
                    "version": doc.version,
                    "framework": doc.info.get("framework", "unknown"),
                    "total_endpoints": len(doc.endpoints),
                    "base_url": doc.base_url,
                }
                for doc in docs
            ],
        }
