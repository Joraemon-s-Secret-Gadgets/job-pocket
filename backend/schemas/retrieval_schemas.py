"""
retrieval_schemas.py

리트리벌(검색) 관련 데이터 스키마를 정의합니다.
"""

from typing import List
from pydantic import BaseModel, Field


class RetrievalResult(BaseModel):
    """
    최종 검색 결과 Document를 표현하는 스키마
    """

    id: int = Field(..., description="DB 레코드 ID")
    content: str = Field(..., description="자소서 본문 내용")
    selfintro_score: int = Field(0, description="자소서 평가 점수")
    relevance_score: float = Field(0.0, description="검색 유사도 점수")


class RetrievalResponse(BaseModel):
    """
    검색 서비스의 응답 구조
    """

    query: str
    top_k: int
    results: List[RetrievalResult]
