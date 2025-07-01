from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum


class HttpMethod(Enum):
    """HTTP 메서드"""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"


class ParameterType(Enum):
    """파라미터 타입"""

    PATH = "path"
    QUERY = "query"
    BODY = "body"
    HEADER = "header"


@dataclass
class ApiParameter:
    """API 파라미터"""

    name: str
    type: ParameterType
    data_type: str
    required: bool = False
    description: Optional[str] = None
    example: Optional[Any] = None


@dataclass
class ApiEndpoint:
    """API 엔드포인트"""

    path: str
    method: HttpMethod
    summary: str
    description: Optional[str] = None
    parameters: List[ApiParameter] = field(default_factory=list)
    request_body: Optional[Dict[str, Any]] = None
    responses: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    deprecated: bool = False


@dataclass
class ApiDocumentation:
    """API 문서"""

    title: str
    version: str
    base_url: str
    description: Optional[str] = None
    endpoints: List[ApiEndpoint] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    info: Dict[str, Any] = field(default_factory=dict)

    def to_openapi_dict(self) -> Dict[str, Any]:
        """OpenAPI 3.0 형식으로 변환"""
        paths = {}

        for endpoint in self.endpoints:
            if endpoint.path not in paths:
                paths[endpoint.path] = {}

            method_lower = endpoint.method.value.lower()

            # 기본 엔드포인트 정보
            endpoint_dict = {
                "summary": endpoint.summary,
                "description": endpoint.description,
                "tags": endpoint.tags,
                "deprecated": endpoint.deprecated,
                "parameters": [
                    {
                        "name": param.name,
                        "in": param.type.value,
                        "required": param.required,
                        "description": param.description,
                        "schema": {"type": param.data_type},
                        "example": param.example,
                    }
                    for param in endpoint.parameters
                ],
                "responses": {},
            }

            # requestBody가 None이 아닐 때만 추가
            if endpoint.request_body is not None:
                endpoint_dict["requestBody"] = endpoint.request_body

            # responses 처리 - content가 None인 경우 제외
            for status_code, response in endpoint.responses.items():
                if response is None:
                    endpoint_dict["responses"][status_code] = {
                        "description": "No content"
                    }
                else:
                    # content가 None인 경우 제외
                    if "content" in response and response["content"] is None:
                        response_copy = response.copy()
                        del response_copy["content"]
                        endpoint_dict["responses"][status_code] = response_copy
                    else:
                        endpoint_dict["responses"][status_code] = response

            paths[endpoint.path][method_lower] = endpoint_dict

        return {
            "openapi": "3.0.0",
            "info": {
                "title": self.title,
                "version": self.version,
                "description": self.description,
                **self.info,
            },
            "servers": [{"url": self.base_url, "description": "API Server"}],
            "paths": paths,
            "tags": [{"name": tag} for tag in self.tags],
        }


@dataclass
class CodeAnalysisResult:
    """코드 분석 결과"""

    symbols: List[Any]
    calls: List[Any]
    chunks: List[Any]
    statistics: Dict[str, Any]
    duration: float
    api_endpoints: List[ApiEndpoint] = field(default_factory=list)
    framework_info: Dict[str, Any] = field(default_factory=dict)
