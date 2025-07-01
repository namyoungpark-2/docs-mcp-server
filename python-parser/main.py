from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from src.presentation.controllers.analysis_controller import router as analysis_router
from src.presentation.controllers.api_docs_controller import router as api_docs_router


def create_app() -> FastAPI:
    """FastAPI 애플리케이션 생성"""
    app = FastAPI(
        title="Python Code Analysis & API Documentation Generator",
        description="Clean Architecture 기반 Python 코드 분석 및 API 문서 생성 서비스",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS 설정
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 라우터 등록
    app.include_router(analysis_router)
    app.include_router(api_docs_router)

    @app.get("/")
    async def root():
        return {
            "message": "Python Code Analysis & API Documentation Generator",
            "version": "1.0.0",
            "docs": "/docs",
            "health": "/api/v1/analysis/health",
            "features": [
                "Code Analysis",
                "API Documentation Generation",
                "OpenAPI 3.0 Support",
                "Multiple Framework Support (Django, FastAPI, Flask)",
            ],
        }

    return app


app = create_app()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8009, reload=True, log_level="info")
