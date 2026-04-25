"""
middlewares

미들웨어 모듈의 공개 인터페이스를 정의합니다.
"""

from .cors import setup_cors

__all__ = ["setup_cors"]
