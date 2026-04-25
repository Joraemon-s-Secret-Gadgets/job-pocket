"""
chat_schemas.py

채팅 및 RAG 단계별 프로세스에 필요한 모든 데이터 구조를 정의합니다.
"""

from enum import Enum
from typing import List, Any, Optional, TypedDict, Dict
from pydantic import BaseModel, Field


# --- Enums ---
class QuestionType(str, Enum):
    """자소서 문항 유형"""
    MOTIVATION = "motivation"
    FUTURE_GOAL = "future_goal"
    COLLABORATION = "collaboration"
    PROBLEM_SOLVING = "problem_solving"
    GROWTH = "growth"
    GENERAL = "general"


class EvaluationLabel(str, Enum):
    """자소서 평가 결과 라벨"""
    GOOD = "좋다"
    NORMAL = "보통"
    POOR = "아쉬움"


# --- Internal Data Structures (TypedDict) ---
class ChatMessageDict(TypedDict):
    """채팅 메시지 구성을 위한 내부 딕셔너리 구조"""
    role: str
    content: str


# --- 도메인 모델 (내부 로직용) ---
class ChatUserProfile(BaseModel):
    """프롬프트 생성을 위해 정제된 사용자 정보 (평탄화된 구조)"""
    gender: str = Field(default="선택안함")
    school: str = Field(default="정보 없음")
    major: str = Field(default="정보 없음")
    experience: str = Field(default="정보 없음")
    awards: str = Field(default="정보 없음")
    skills: str = Field(default="정보 없음")


class ParsedUserRequest(BaseModel):
    """사용자 메시지에서 추출된 자소서 작성 조건 통합 데이터"""
    raw_message: str = Field(default="")
    company: str = Field(default="")
    job: str = Field(default="")
    question: str = Field(default="")
    char_limit: Optional[int] = Field(default=1000) # 기본값 1000으로 설정
    question_type: QuestionType = Field(default=QuestionType.GENERAL)


class SampleAnalysis(BaseModel):
    """검색된 샘플에서 추출된 분석 정보"""
    summary: str = Field(..., description="샘플 공통 패턴 요약 문자열")
    style_rules: str = Field(..., description="샘플 기반 작성 규칙 가이드")
    excerpt: str = Field(..., description="샘플 원문 발췌본")


# --- LLM JSON 출력 규격 (JsonOutputParser용) ---
class LLMParsedRequest(BaseModel):
    """Step 1: 사용자 요청 구조화 파서 출력 스키마"""
    company: str = Field(default="", description="지원 회사명")
    job: str = Field(default="", description="지원 직무명")
    question: str = Field(default="", description="자기소개서 문항")
    char_limit: Optional[int] = Field(default=1000, description="글자 수 제한 (숫자)") # 기본값 1000
    question_type: str = Field(default="general", description="문항 유형")


class LLMSampleSummary(BaseModel):
    """Step 2: 유사 사례 패턴 요약 출력 스키마"""
    strengths: List[str] = Field(description="공통 강점 리스트")
    structure: List[str] = Field(description="서술 구조 패턴 리스트")
    tone: List[str] = Field(description="표현 톤 특성 리스트")
    pitfalls: List[str] = Field(description="피해야 할 점 리스트")


class LLMEvaluationResult(BaseModel):
    """Step 6: 자소서 품질 평가 출력 스키마"""
    label: str = Field(description="평가 결과 (좋다, 보통, 아쉬움)")
    reason: str = Field(description="평가 이유 (한 문장)")
    points: List[str] = Field(description="보완 포인트 리스트 (최대 2개)")


# --- API 요청/응답 규격 (API Contract) ---
class ChatMessageRequest(BaseModel):
    email: str
    role: str
    content: str


class StepParseRequest(BaseModel):
    prompt: str
    model: str


class StepDraftRequest(BaseModel):
    parsed_data: ParsedUserRequest
    user_info: Any
    model: str


class StepReviseRequest(BaseModel):
    existing_draft: str
    revision_request: str
    model: str


class StepRefineRequest(BaseModel):
    draft: str
    parsed_data: ParsedUserRequest
    model: str


class StepFitRequest(BaseModel):
    refined: str
    parsed_data: ParsedUserRequest
    model: str


class StepFinalRequest(BaseModel):
    adjusted: str
    parsed_data: ParsedUserRequest
    model: str
    result_label: str = Field(default="자소서 초안")
    change_summary: Optional[str] = None
