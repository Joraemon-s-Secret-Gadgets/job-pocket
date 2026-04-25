"""
chat_schemas.py

채팅 및 RAG 단계별 프로세스에 필요한 스키마를 정의합니다.
"""

from typing import List, Any, Optional, TypedDict
from pydantic import BaseModel, Field


# --- Internal Data Structures (TypedDict) ---
class ChatMessageDict(TypedDict):
    role: str
    content: str


# --- API Request/Response Schemas (BaseModel) ---
class ChatMessageRequest(BaseModel):
    email: str
    role: str
    content: str


class StepParseRequest(BaseModel):
    prompt: str
    model: str


class StepDraftRequest(BaseModel):
    prompt: str
    user_info: List[Any]
    model: str


class StepReviseRequest(BaseModel):
    existing_draft: str
    revision_request: str
    model: str


class StepRefineRequest(BaseModel):
    draft: str
    prompt: str
    model: str


class StepFitRequest(BaseModel):
    refined: str
    prompt: str
    model: str


class StepFinalRequest(BaseModel):
    adjusted: str
    prompt: str
    model: str
    result_label: str = Field(default="자소서 초안")
    change_summary: Optional[str] = None
