"""
cors_middleware

CORS(Cross-Origin Resource Sharing) 미들웨어 등록 로직을 담당합니다.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def setup_cors(app: FastAPI) -> None:
    """
    FastAPI 애플리케이션에 CORS 미들웨어를 등록합니다.

    Args:
        app: 미들웨어를 등록할 FastAPI 애플리케이션 인스턴스.
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 운영 환경에서는 허용 도메인을 명시적으로 제한하세요.
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
