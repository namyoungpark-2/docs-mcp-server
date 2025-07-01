import re
from pathlib import Path
from typing import List, Dict
import sys
import os
import importlib.util
from rest_framework import serializers

from ...domain.entities.api_documentation import (
    ApiDocumentation,
    ApiEndpoint,
    HttpMethod,
    ApiParameter,
    ParameterType,
)


def setup_django_environment(project_path: Path):
    """Django 환경 설정"""
    try:
        # Django 설정 모듈 경로 설정
        app_dir = project_path / "app"
        if app_dir.exists():
            os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")

            # 프로젝트 루트를 Python 경로에 추가
            project_root = str(project_path)
            if project_root not in sys.path:
                sys.path.insert(0, project_root)

            # app 디렉토리를 Python 경로에 추가
            app_path = str(app_dir)
            if app_path not in sys.path:
                sys.path.insert(0, app_path)

            # Django 설정
            import django

            django.setup()

            print(f"[문서 자동화] Django 환경 설정 완료: {app_dir}")
            return True
        else:
            print(f"[문서 자동화] Django app 디렉토리를 찾을 수 없습니다: {app_dir}")
            return False

    except Exception as e:
        print(f"[문서 자동화] Django 환경 설정 실패: {e}")
        return False


def _map_field_type_to_schema(field_type):
    """Django 필드 타입을 OpenAPI 스키마로 변환"""
    field_type_str = str(field_type).lower()

    if "charfield" in field_type_str or "textfield" in field_type_str:
        return {"type": "string"}
    elif "integerfield" in field_type_str or "positiveintegerfield" in field_type_str:
        return {"type": "integer"}
    elif "floatfield" in field_type_str or "decimalfield" in field_type_str:
        return {"type": "number"}
    elif "booleanfield" in field_type_str:
        return {"type": "boolean"}
    elif "datefield" in field_type_str or "datetimefield" in field_type_str:
        return {"type": "string", "format": "date-time"}
    elif "emailfield" in field_type_str:
        return {"type": "string", "format": "email"}
    elif "urlfield" in field_type_str:
        return {"type": "string", "format": "uri"}
    elif "filefield" in field_type_str or "imagefield" in field_type_str:
        return {"type": "string", "format": "binary"}
    else:
        return {"type": "string"}


def _drf_field_to_openapi_type(field):
    if isinstance(field, serializers.IntegerField):
        return {"type": "integer"}
    if isinstance(field, serializers.DecimalField):
        return {"type": "number", "format": "decimal"}
    if isinstance(field, serializers.FloatField):
        return {"type": "number", "format": "float"}
    if isinstance(field, serializers.BooleanField):
        return {"type": "boolean"}
    if isinstance(field, serializers.DateTimeField):
        return {"type": "string", "format": "date-time"}
    if isinstance(field, serializers.DateField):
        return {"type": "string", "format": "date"}
    if isinstance(field, serializers.CharField):
        return {"type": "string"}
    if isinstance(field, serializers.SerializerMethodField):
        return {"type": "string"}
    if isinstance(field, serializers.ListField):
        child_type = (
            _drf_field_to_openapi_type(field.child)
            if hasattr(field, "child")
            else {"type": "string"}
        )
        return {"type": "array", "items": child_type}
    if isinstance(field, serializers.DictField):
        return {"type": "object"}
    return {"type": "string"}


def extract_serializer_fields(serializer_class):
    try:
        serializer_instance = serializer_class()
        fields = getattr(serializer_instance, "fields", None)
        if fields is not None and hasattr(fields, "items"):
            result = {}
            for name, field in fields.items():
                schema = _drf_field_to_openapi_type(field)
                if getattr(field, "required", False):
                    schema["required"] = True
                if getattr(field, "allow_null", False):
                    schema["nullable"] = True
                if getattr(field, "read_only", False):
                    schema["readOnly"] = True
                if getattr(field, "help_text", None):
                    schema["description"] = str(field.help_text)
                result[name] = schema
            return result
    except Exception as e:
        print(f"[문서 자동화] serializer 필드 추출 실패: {e}")
    return {}


def _extract_field_schema(field):
    """DRF 필드를 OpenAPI 스키마로 변환"""
    try:
        from rest_framework import fields as drf_fields

        if isinstance(field, drf_fields.CharField):
            return {"type": "string"}
        if isinstance(field, drf_fields.IntegerField):
            return {"type": "integer"}
        if isinstance(field, drf_fields.FloatField):
            return {"type": "number"}
        if isinstance(field, drf_fields.BooleanField):
            return {"type": "boolean"}
        if isinstance(field, drf_fields.DateTimeField):
            return {"type": "string", "format": "date-time"}
        if isinstance(field, drf_fields.DateField):
            return {"type": "string", "format": "date"}
        if isinstance(field, drf_fields.EmailField):
            return {"type": "string", "format": "email"}
        if isinstance(field, drf_fields.URLField):
            return {"type": "string", "format": "uri"}
        if hasattr(field, "child"):  # ListField 등
            return {"type": "array", "items": _extract_field_schema(field.child)}
        return {"type": "string"}
    except Exception:
        return {"type": "string"}


def _generate_default_schema():
    """fallback: 기본 스키마 반환"""
    return {
        "id": {"type": "integer"},
        "name": {"type": "string"},
        "created_at": {"type": "string", "format": "date-time"},
        "updated_at": {"type": "string", "format": "date-time"},
    }


def _extract_fields_from_file(file_path, class_name):
    """파일에서 serializer 필드 정보 추출"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 클래스 정의 찾기
        class_pattern = rf"class\s+{class_name}\s*\([^)]*\):"
        if not re.search(class_pattern, content):
            return None

        # 필드 패턴 찾기
        field_pattern = r"(\w+)\s*=\s*serializers\.(\w+)Field\s*\([^)]*\)"
        fields = re.findall(field_pattern, content)

        if fields:
            return {
                name: _map_field_type_to_schema(f"serializers.{field_type}Field")
                for name, field_type in fields
            }

        return None
    except Exception as e:
        print(f"[문서 자동화] 파일에서 필드 추출 실패: {e}")
        return None


def get_serializer_class_from_viewset(viewset_cls):
    """ViewSet에서 serializer 클래스 추출"""
    try:
        # 1. 직접 serializer_class 속성 확인
        if hasattr(viewset_cls, "serializer_class") and viewset_cls.serializer_class:
            return viewset_cls.serializer_class

        # 2. get_serializer_class 메서드 확인
        if hasattr(viewset_cls, "get_serializer_class"):
            try:
                return viewset_cls.get_serializer_class()
            except Exception:
                pass

        # 3. ViewSetMock 객체인 경우
        if hasattr(viewset_cls, "serializer_class_name"):
            try:
                # 파일에서 serializer 클래스 import 시도
                file_path = viewset_cls.__file__
                if file_path and Path(file_path).exists():
                    # 같은 디렉토리의 serializers.py 파일에서 찾기
                    serializers_path = Path(file_path).parent / "serializers.py"
                    if serializers_path.exists():
                        with open(serializers_path, "r", encoding="utf-8") as f:
                            content = f.read()

                            # serializer 클래스 정의 찾기
                            class_pattern = rf"class\s+{viewset_cls.serializer_class_name}\s*\([^)]*\):"
                            if re.search(class_pattern, content):
                                # 간단한 Mock Serializer 클래스 생성
                                class MockSerializer:
                                    def __init__(self):
                                        self.fields = self._extract_fields_from_content(
                                            content, viewset_cls.serializer_class_name
                                        )

                                    def _extract_fields_from_content(
                                        self, content, class_name
                                    ):
                                        """파일 내용에서 serializer 필드 추출"""
                                        fields = {}

                                        # 클래스 정의 찾기
                                        class_start = content.find(
                                            f"class {class_name}"
                                        )
                                        if class_start == -1:
                                            return fields

                                        # 클래스 본문 찾기
                                        brace_count = 0
                                        class_body_start = -1
                                        for i in range(class_start, len(content)):
                                            if content[i] == "{":
                                                brace_count += 1
                                                if class_body_start == -1:
                                                    class_body_start = i
                                            elif content[i] == "}":
                                                brace_count -= 1
                                                if brace_count == 0:
                                                    class_body_end = i
                                                    break

                                        if (
                                            class_body_start == -1
                                            or class_body_end == -1
                                        ):
                                            return fields

                                        class_body = content[
                                            class_body_start:class_body_end
                                        ]

                                        # 필드 정의 찾기
                                        field_pattern = (
                                            r"(\w+)\s*=\s*serializers\.(\w+)\([^)]*\)"
                                        )
                                        matches = re.findall(field_pattern, class_body)

                                        for field_name, field_type in matches:
                                            fields[field_name] = (
                                                self._create_field_mock(field_type)
                                            )

                                        return fields

                                    def _create_field_mock(self, field_type):
                                        """필드 타입에 따른 Mock 필드 생성"""

                                        class MockField:
                                            def __init__(self, field_type):
                                                self.field_type = field_type

                                            def __class__(self):
                                                class MockClass:
                                                    __name__ = f"{field_type}Field"

                                                return MockClass

                                        return MockField(field_type)

                                return MockSerializer()
            except Exception as e:
                print(f"[문서 자동화] Serializer 클래스 추출 실패: {e}")

        return None
    except Exception as e:
        print(f"[문서 자동화] Serializer 클래스 추출 실패: {e}")
        return None


def extract_serializer_from_viewset(viewset_class, viewset_name):
    """ViewSet에서 실제 사용하는 serializer 추출"""
    try:
        # 1. ViewSet 클래스에서 serializer_class 속성 확인
        if hasattr(viewset_class, "serializer_class"):
            serializer_class = viewset_class.serializer_class
            if serializer_class:
                print(
                    f"[문서 자동화] {viewset_name}에서 serializer_class 발견: {serializer_class}"
                )
                return extract_serializer_fields(serializer_class)

        # 2. ViewSet의 list 메서드에서 serializer 사용 패턴 파싱
        if hasattr(viewset_class, "list"):
            list_method = viewset_class.list
            if hasattr(list_method, "__code__"):
                # 메서드의 소스 코드를 문자열로 가져오기
                import inspect

                try:
                    source = inspect.getsource(list_method)
                    print(f"[문서 자동화] {viewset_name} list 메서드 소스 분석 중...")

                    # RevenueShareViewSet 패턴 매칭
                    if (
                        "RevenueShareSeasonSerializer" in source
                        or "RevenueShareContentSerializer" in source
                    ):
                        print(
                            f"[문서 자동화] {viewset_name}에서 RevenueShare serializer 패턴 발견"
                        )
                        # revenue.serializers에서 import
                        try:
                            from revenue.serializers import (
                                RevenueShareContentSerializer,
                                RevenueShareSeasonSerializer,
                            )

                            return extract_serializer_fields(
                                RevenueShareContentSerializer
                            )
                        except ImportError:
                            print(f"[문서 자동화] revenue.serializers import 실패")

                    # RevenueViewSet 패턴 매칭
                    elif "RevenueSerializer" in source:
                        print(
                            f"[문서 자동화] {viewset_name}에서 RevenueSerializer 패턴 발견"
                        )
                        try:
                            from revenue.serializers import RevenueSerializer

                            return extract_serializer_fields(RevenueSerializer)
                        except ImportError:
                            print(f"[문서 자동화] revenue.serializers import 실패")

                    # AdminUserViewSet 패턴 매칭
                    elif "AdminUserSerializer" in source:
                        print(
                            f"[문서 자동화] {viewset_name}에서 AdminUserSerializer 패턴 발견"
                        )
                        try:
                            from account.serializers import AdminUserSerializer

                            return extract_serializer_fields(AdminUserSerializer)
                        except ImportError:
                            print(f"[문서 자동화] account.serializers import 실패")

                    # UserActionHistoryViewSet 패턴 매칭
                    elif "UserActionHistorySerializer" in source:
                        print(
                            f"[문서 자동화] {viewset_name}에서 UserActionHistorySerializer 패턴 발견"
                        )
                        try:
                            from user_action_history.serializers import (
                                UserActionHistorySerializer,
                            )

                            return extract_serializer_fields(
                                UserActionHistorySerializer
                            )
                        except ImportError:
                            print(
                                f"[문서 자동화] user_action_history.serializers import 실패"
                            )

                except Exception as e:
                    print(f"[문서 자동화] {viewset_name} 소스 분석 실패: {e}")

        # 3. get_serializer_class 메서드 확인
        if hasattr(viewset_class, "get_serializer_class"):
            try:
                serializer_class = viewset_class.get_serializer_class()
                if serializer_class:
                    print(
                        f"[문서 자동화] {viewset_name}에서 get_serializer_class 발견: {serializer_class}"
                    )
                    return extract_serializer_fields(serializer_class)
            except Exception as e:
                print(
                    f"[문서 자동화] {viewset_name} get_serializer_class 호출 실패: {e}"
                )

        # 4. ViewSet 이름 기반 하드코딩된 매핑 (fallback)
        serializer_mapping = {
            "RevenueShareViewSet": "RevenueShareContentSerializer",
            "RevenueViewSet": "RevenueSerializer",
            "AdminUserViewSet": "AdminUserSerializer",
            "UserActionHistoryViewSet": "UserActionHistorySerializer",
        }

        if viewset_name in serializer_mapping:
            serializer_name = serializer_mapping[viewset_name]
            print(
                f"[문서 자동화] {viewset_name}에 대해 하드코딩된 매핑 사용: {serializer_name}"
            )

            # 앱별 import 시도
            app_mapping = {
                "RevenueShareViewSet": ("revenue", "RevenueShareContentSerializer"),
                "RevenueViewSet": ("revenue", "RevenueSerializer"),
                "AdminUserViewSet": ("account", "AdminUserSerializer"),
                "UserActionHistoryViewSet": (
                    "user_action_history",
                    "UserActionHistorySerializer",
                ),
            }

            if viewset_name in app_mapping:
                app_name, serializer_class_name = app_mapping[viewset_name]
                try:
                    module = __import__(
                        f"{app_name}.serializers", fromlist=[serializer_class_name]
                    )
                    serializer_class = getattr(module, serializer_class_name)
                    return extract_serializer_fields(serializer_class)
                except Exception as e:
                    print(
                        f"[문서 자동화] {app_name}.serializers.{serializer_class_name} import 실패: {e}"
                    )

    except Exception as e:
        print(f"[문서 자동화] {viewset_name} serializer 추출 실패: {e}")

    return {}


def generate_openapi_for_viewset(
    viewset_name: str,
    file_path: str,
    base_url: str,
    model_name: str = None,
) -> List[ApiEndpoint]:
    """ViewSet에서 OpenAPI 엔드포인트 생성"""
    print(f"[문서 자동화] {viewset_name} 파일 경로: {file_path}")

    # ViewSet 클래스 import 시도
    viewset_class = import_viewset_class(file_path, viewset_name)

    if viewset_class:
        print(f"[문서 자동화] {viewset_name} 클래스 import 성공")

        # 실제 serializer 필드 추출
        serializer_fields = extract_serializer_from_viewset(viewset_class, viewset_name)

        if serializer_fields:
            print(
                f"[문서 자동화] {viewset_name}에서 실제 serializer 필드 추출 성공: {len(serializer_fields)}개 필드"
            )
        else:
            print(
                f"[문서 자동화] {viewset_name}에서 serializer 필드 추출 실패, 기본 스키마 사용"
            )
            serializer_fields = _generate_default_schema()

        # 5개 CRUD 엔드포인트 생성
        endpoints = []

        # 공통 파라미터 정의
        common_parameters = [
            ApiParameter(
                name="Authorization",
                type=ParameterType.HEADER,
                data_type="string",
                required=True,
                description="Bearer token for authentication",
                example="Bearer <your-token-here>",
            )
        ]

        # GET 요청용 쿼리 파라미터
        get_query_parameters = [
            ApiParameter(
                name="page",
                type=ParameterType.QUERY,
                data_type="integer",
                required=False,
                description="Page number for pagination",
                example=1,
            ),
            ApiParameter(
                name="page_size",
                type=ParameterType.QUERY,
                data_type="integer",
                required=False,
                description="Number of items per page",
                example=20,
            ),
            ApiParameter(
                name="search",
                type=ParameterType.QUERY,
                data_type="string",
                required=False,
                description="Search term for filtering",
                example="search term",
            ),
            ApiParameter(
                name="ordering",
                type=ParameterType.QUERY,
                data_type="string",
                required=False,
                description="Field to order by (prefix with - for descending)",
                example="created_at",
            ),
            ApiParameter(
                name="filter",
                type=ParameterType.QUERY,
                data_type="string",
                required=False,
                description="Filter parameters",
                example="status=active",
            ),
        ]

        # POST/PUT 요청용 헤더
        content_type_header = [
            ApiParameter(
                name="Content-Type",
                type=ParameterType.HEADER,
                data_type="string",
                required=True,
                description="Content type for request body",
                example="application/json",
            )
        ]

        # List/Create
        endpoints.append(
            ApiEndpoint(
                path=f"/api/v1/{model_name}/",
                method=HttpMethod.GET,
                summary=f"List {model_name}",
                description=f"Get list of {model_name}",
                parameters=common_parameters + get_query_parameters,
                request_body=None,
                responses={
                    "200": {
                        "description": "Success",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "count": {
                                            "type": "integer",
                                            "description": "Total number of items",
                                        },
                                        "next": {
                                            "type": "string",
                                            "description": "URL to next page",
                                            "nullable": True,
                                        },
                                        "previous": {
                                            "type": "string",
                                            "description": "URL to previous page",
                                            "nullable": True,
                                        },
                                        "results": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": serializer_fields,
                                            },
                                        },
                                    },
                                }
                            }
                        },
                    },
                    "401": {
                        "description": "Unauthorized",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "detail": {
                                            "type": "string",
                                            "description": "Authentication error message",
                                        }
                                    },
                                }
                            }
                        },
                    },
                    "403": {
                        "description": "Forbidden",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "detail": {
                                            "type": "string",
                                            "description": "Permission error message",
                                        }
                                    },
                                }
                            }
                        },
                    },
                },
                tags=[model_name],
            )
        )

        endpoints.append(
            ApiEndpoint(
                path=f"/api/v1/{model_name}/",
                method=HttpMethod.POST,
                summary=f"Create {model_name}",
                description=f"Create new {model_name}",
                parameters=common_parameters + content_type_header,
                request_body={
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": serializer_fields,
                                "required": [
                                    field
                                    for field, schema in serializer_fields.items()
                                    if schema.get("required", False)
                                ],
                            }
                        }
                    },
                },
                responses={
                    "201": {
                        "description": "Created successfully",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": serializer_fields,
                                }
                            }
                        },
                    },
                    "400": {
                        "description": "Bad Request",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "field_name": {
                                            "type": "array",
                                            "items": {"type": "string"},
                                            "description": "Validation errors for specific fields",
                                        }
                                    },
                                }
                            }
                        },
                    },
                    "401": {
                        "description": "Unauthorized",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "detail": {
                                            "type": "string",
                                            "description": "Authentication error message",
                                        }
                                    },
                                }
                            }
                        },
                    },
                    "403": {
                        "description": "Forbidden",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "detail": {
                                            "type": "string",
                                            "description": "Permission error message",
                                        }
                                    },
                                }
                            }
                        },
                    },
                },
                tags=[model_name],
            )
        )

        # Retrieve/Update/Delete
        # ID 파라미터 추가
        id_parameter = [
            ApiParameter(
                name="id",
                type=ParameterType.PATH,
                data_type="integer",
                required=True,
                description=f"{model_name} ID",
                example=1,
            )
        ]

        endpoints.append(
            ApiEndpoint(
                path=f"/api/v1/{model_name}/{{id}}/",
                method=HttpMethod.GET,
                summary=f"Get {model_name}",
                description=f"Get specific {model_name} by ID",
                parameters=common_parameters + id_parameter,
                request_body=None,
                responses={
                    "200": {
                        "description": "Success",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": serializer_fields,
                                }
                            }
                        },
                    },
                    "404": {
                        "description": "Not Found",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "detail": {
                                            "type": "string",
                                            "description": "Not found error message",
                                        }
                                    },
                                }
                            }
                        },
                    },
                    "401": {
                        "description": "Unauthorized",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "detail": {
                                            "type": "string",
                                            "description": "Authentication error message",
                                        }
                                    },
                                }
                            }
                        },
                    },
                    "403": {
                        "description": "Forbidden",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "detail": {
                                            "type": "string",
                                            "description": "Permission error message",
                                        }
                                    },
                                }
                            }
                        },
                    },
                },
                tags=[model_name],
            )
        )

        endpoints.append(
            ApiEndpoint(
                path=f"/api/v1/{model_name}/{{id}}/",
                method=HttpMethod.PUT,
                summary=f"Update {model_name}",
                description=f"Update specific {model_name} by ID",
                parameters=common_parameters + content_type_header + id_parameter,
                request_body={
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": serializer_fields,
                                "required": [
                                    field
                                    for field, schema in serializer_fields.items()
                                    if schema.get("required", False)
                                ],
                            }
                        }
                    },
                },
                responses={
                    "200": {
                        "description": "Updated successfully",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": serializer_fields,
                                }
                            }
                        },
                    },
                    "400": {
                        "description": "Bad Request",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "field_name": {
                                            "type": "array",
                                            "items": {"type": "string"},
                                            "description": "Validation errors for specific fields",
                                        }
                                    },
                                }
                            }
                        },
                    },
                    "404": {
                        "description": "Not Found",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "detail": {
                                            "type": "string",
                                            "description": "Not found error message",
                                        }
                                    },
                                }
                            }
                        },
                    },
                    "401": {
                        "description": "Unauthorized",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "detail": {
                                            "type": "string",
                                            "description": "Authentication error message",
                                        }
                                    },
                                }
                            }
                        },
                    },
                    "403": {
                        "description": "Forbidden",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "detail": {
                                            "type": "string",
                                            "description": "Permission error message",
                                        }
                                    },
                                }
                            }
                        },
                    },
                },
                tags=[model_name],
            )
        )

        endpoints.append(
            ApiEndpoint(
                path=f"/api/v1/{model_name}/{{id}}/",
                method=HttpMethod.DELETE,
                summary=f"Delete {model_name}",
                description=f"Delete specific {model_name} by ID",
                parameters=common_parameters + id_parameter,
                request_body=None,
                responses={
                    "204": {"description": "Deleted successfully", "content": None},
                    "404": {
                        "description": "Not Found",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "detail": {
                                            "type": "string",
                                            "description": "Not found error message",
                                        }
                                    },
                                }
                            }
                        },
                    },
                    "401": {
                        "description": "Unauthorized",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "detail": {
                                            "type": "string",
                                            "description": "Authentication error message",
                                        }
                                    },
                                }
                            }
                        },
                    },
                    "403": {
                        "description": "Forbidden",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "detail": {
                                            "type": "string",
                                            "description": "Permission error message",
                                        }
                                    },
                                }
                            }
                        },
                    },
                },
                tags=[model_name],
            )
        )

        print(f"[문서 자동화] 5개 CRUD 엔드포인트 생성 완료")
        print(f"[문서 자동화] {viewset_name}에서 5개 엔드포인트 추출 완료")
        return endpoints

    else:
        print(f"[문서 자동화] {viewset_name} 클래스를 찾을 수 없습니다")
        return []


def _to_plural(singular):
    """단수형을 복수형으로 변환"""
    if singular.endswith("y"):
        return singular[:-1] + "ies"
    elif (
        singular.endswith("s")
        or singular.endswith("sh")
        or singular.endswith("ch")
        or singular.endswith("x")
        or singular.endswith("z")
    ):
        return singular + "es"
    else:
        return singular + "s"


def discover_viewsets(project_path: Path) -> List[Dict[str, str]]:
    """프로젝트에서 ViewSet 클래스들을 자동 발견"""
    viewset_pattern = r"class\s+(\w+ViewSet)\s*\([^)]*\):"
    viewsets = []

    app_dir = project_path / "app"
    if not app_dir.exists():
        return viewsets

    # app 디렉토리 내 모든 앱 탐색
    for app_folder in app_dir.iterdir():
        if app_folder.is_dir() and not app_folder.name.startswith("."):
            app_name = app_folder.name

            # views.py 파일 확인
            views_file = app_folder / "views.py"
            if views_file.exists():
                try:
                    with open(views_file, "r", encoding="utf-8") as f:
                        content = f.read()

                    matches = re.findall(viewset_pattern, content)
                    for viewset_name in matches:
                        # URL 경로 생성
                        if viewset_name.endswith("ViewSet"):
                            model_name = viewset_name[:-7]
                        else:
                            model_name = viewset_name

                        plural_name = _to_plural(model_name.lower())
                        url_path = f"/api/v1/{plural_name}/"

                        viewsets.append(
                            {"app": app_name, "viewset": viewset_name, "url": url_path}
                        )

                        print(
                            f"[문서 자동화] 자동 발견: {app_name}.{viewset_name} -> {url_path}"
                        )
                except Exception as e:
                    print(f"[문서 자동화] {app_name} views.py 읽기 실패: {e}")

            # views/ 폴더 확인
            views_folder = app_folder / "views"
            if views_folder.exists() and views_folder.is_dir():
                for view_file in views_folder.glob("*.py"):
                    if view_file.name != "__init__.py":
                        try:
                            with open(view_file, "r", encoding="utf-8") as f:
                                content = f.read()

                            matches = re.findall(viewset_pattern, content)
                            for viewset_name in matches:
                                # URL 경로 생성
                                if viewset_name.endswith("ViewSet"):
                                    model_name = viewset_name[:-7]
                                else:
                                    model_name = viewset_name

                                plural_name = _to_plural(model_name.lower())
                                url_path = f"/api/v1/{plural_name}/"

                                viewsets.append(
                                    {
                                        "app": f"{app_name}/views/{view_file.stem}",
                                        "viewset": viewset_name,
                                        "url": url_path,
                                    }
                                )

                                print(
                                    f"[문서 자동화] 자동 발견: {app_name}/views/{view_file.stem}.{viewset_name} -> {url_path}"
                                )
                        except Exception as e:
                            print(
                                f"[문서 자동화] {app_name}/views/{view_file.name} 읽기 실패: {e}"
                            )

    return viewsets


def import_viewset_class(file_path: str, class_name: str):
    """파일에서 ViewSet 클래스를 import"""
    try:
        # 파일 경로를 절대 경로로 변환
        file_path = Path(file_path).resolve()

        # Django 프로젝트 루트 경로 설정
        django_root = (
            file_path.parent.parent.parent
        )  # app/views.py -> app/ -> project_root/

        # Python 경로에 Django 프로젝트 루트 추가
        if str(django_root) not in sys.path:
            sys.path.insert(0, str(django_root))

        # 앱 이름 추출
        app_name = file_path.parent.name

        # 여러 모듈 이름 시도
        possible_module_names = [
            f"app.{app_name}.views",
            f"{app_name}.views",
            f"views_{file_path.stem}",
            f"app.{app_name}.views.{file_path.stem}",
        ]

        viewset_class = None

        for module_name in possible_module_names:
            try:
                # 파일을 모듈로 로드
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                if spec is None or spec.loader is None:
                    continue

                module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = module
                spec.loader.exec_module(module)

                # 클래스 가져오기
                viewset_class = getattr(module, class_name, None)
                if viewset_class:
                    print(
                        f"[문서 자동화] {class_name} 클래스 import 성공 (모듈: {module_name})"
                    )
                    return viewset_class

            except Exception as e:
                print(f"[문서 자동화] 모듈 {module_name} 로드 실패: {e}")
                continue

        if not viewset_class:
            print(f"[문서 자동화] {class_name} 클래스를 모든 모듈에서 찾을 수 없음")

    except Exception as e:
        print(f"[문서 자동화] 직접 import 실패: {e}")

    # fallback: 파일 내용을 직접 파싱
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 클래스 정의 찾기
        class_pattern = rf"class\s+{class_name}\s*\([^)]*\):"
        if re.search(class_pattern, content):
            print(f"[문서 자동화] {class_name} 클래스 정의 발견 (파일 파싱)")
            return ViewSetMock(class_name, file_path)
        else:
            print(f"[문서 자동화] {class_name} 클래스 정의를 파일에서 찾을 수 없음")
            return None

    except Exception as parse_error:
        print(f"[문서 자동화] 파일 파싱 실패: {parse_error}")
        return None


def generate_api_documentation(project_path: Path, base_url: str) -> ApiDocumentation:
    """API 문서 생성"""
    # Django 환경 설정
    setup_django_environment(project_path)

    # ViewSet 자동 발견
    viewsets = discover_viewsets(project_path)

    all_endpoints = []

    for viewset_info in viewsets:
        app_name = viewset_info["app"]
        viewset_name = viewset_info["viewset"]

        # app 이름에서 실제 앱 이름 추출
        if "/" in app_name:
            actual_app_name = app_name.split("/")[0]
        else:
            actual_app_name = app_name

        # ViewSet 파일 경로 찾기
        if "/" in app_name:
            # views/ 폴더 내 파일인 경우
            parts = app_name.split("/")
            app_folder = parts[0]
            view_file = parts[2]  # views/filename
            views_file_path = (
                project_path / "app" / app_folder / "views" / f"{view_file}.py"
            )
        else:
            # views.py 파일인 경우
            views_file_path = project_path / "app" / actual_app_name / "views.py"

        print(f"[문서 자동화] {viewset_name} 파일 경로: {views_file_path}")

        if views_file_path.exists():
            # ViewSet 클래스 import
            viewset_cls = import_viewset_class(str(views_file_path), viewset_name)

            if viewset_cls:
                # OpenAPI 엔드포인트 생성
                endpoints = generate_openapi_for_viewset(
                    viewset_name, str(views_file_path), base_url, actual_app_name
                )
                all_endpoints.extend(endpoints)
                print(
                    f"[문서 자동화] {viewset_name}에서 {len(endpoints)}개 엔드포인트 추출 완료"
                )
            else:
                print(f"[문서 자동화] {viewset_name} 클래스를 찾을 수 없습니다")
        else:
            print(
                f"[문서 자동화] {viewset_name} 파일을 찾을 수 없습니다: {views_file_path}"
            )

    print(f"[DEBUG] 생성된 엔드포인트 개수: {len(all_endpoints)}")

    # OpenAPI 문서 생성
    openapi_dict = {
        "openapi": "3.0.0",
        "info": {
            "title": f"{project_path.name} API Documentation",
            "version": "1.0.0",
            "description": project_path.name,
            "framework": "django",
            "project_path": str(project_path),
            "total_endpoints": len(all_endpoints),
        },
        "servers": [{"url": base_url, "description": "API Server"}],
        "paths": {},
        "tags": [],
    }

    # 엔드포인트를 OpenAPI 형식으로 변환
    for endpoint in all_endpoints:
        path_key = endpoint.path
        method_key = endpoint.method.value.lower()

        if path_key not in openapi_dict["paths"]:
            openapi_dict["paths"][path_key] = {}

        openapi_dict["paths"][path_key][method_key] = {
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
            "requestBody": endpoint.request_body,
            "responses": endpoint.responses,
        }

    # 태그 정보 추가
    all_tags = set()
    for endpoint in all_endpoints:
        all_tags.update(endpoint.tags)

    for tag in sorted(all_tags):
        openapi_dict["tags"].append({"name": tag})

    print(f"[DEBUG] OpenAPI dict keys: {list(openapi_dict.keys())}")
    print(f"[DEBUG] OpenAPI paths keys: {list(openapi_dict['paths'].keys())}")

    return ApiDocumentation(
        title=f"{project_path.name} API Documentation",
        version="1.0.0",
        base_url=base_url,
        description=project_path.name,
        endpoints=all_endpoints,
        tags=sorted(all_tags),
        info={
            "framework": "django",
            "project_path": str(project_path),
            "total_endpoints": len(all_endpoints),
        },
    )
