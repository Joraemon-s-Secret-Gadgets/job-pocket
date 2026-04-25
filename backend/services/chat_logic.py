"""
chat_logic.py

자기소개서 생성 및 수정 프로세스를 총괄하는 오케스트레이터 모듈입니다.
각 단계(파싱, 분석, 생성, 평가)의 하위 모듈들을 조합하여 비즈니스 로직을 수행합니다.

주요 기능:
- 사용자 요청 분석 및 구조화
- 자소서 초안 생성 및 품질 기반 재생성 루프
- 기존 자소서 수정 및 첨삭
- 글자 수 조정 및 최종 응답 조립
"""

import sys
from pathlib import Path
from typing import Any, Optional, List

from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_huggingface import HuggingFaceEmbeddings
from langsmith import traceable

from common.config import (
    OPENAI_API_CONFIG,
    GROQ_API_CONFIG,
    EMBEDDING_CONFIG,
    RETRIEVER_CONFIG,
)
from utils import ensure_faiss_index_dir
from services import chat as chat_internal
from services.retrieval_service import RetrievalService
from schemas.chat_schemas import ParsedUserRequest

# -----------------------------
# 공통 리소스 초기화
# -----------------------------
llm_gpt = ChatOpenAI(**OPENAI_API_CONFIG)
llm_groq = ChatGroq(**GROQ_API_CONFIG)
hf_embeddings = HuggingFaceEmbeddings(**EMBEDDING_CONFIG)

# 리트리버 설정
faiss_index_path = ensure_faiss_index_dir(
    directory="utils",
    folder_name="faiss_index_high",
    folder_url="https://drive.google.com/drive/folders/1y7UKpJGDh-wMI2koNVzWywXW7sL-ee3D",
)
retrieval_svc = RetrievalService(
    embeddings=hf_embeddings,
    index_folder=str(faiss_index_path),
    top_k=RETRIEVER_CONFIG.get("top_k", 3),
)

# -----------------------------
# 내부 헬퍼 및 모델 매핑
# -----------------------------
MODEL_INSTANCES = {
    "GPT-4o-mini": llm_gpt,
    "GPT-OSS-120B (Groq)": llm_groq
}

def _get_active_llm(model_name: str):
    """모델 이름에 따라 사전 정의된 LLM 인스턴스를 정확히 반환합니다."""
    return MODEL_INSTANCES.get(model_name, llm_gpt)

# -----------------------------
# 최상위 API (Orchestrators) - 무분별한 API 호출 방지 버전
# -----------------------------

@traceable(run_type="chain", name="Parse_User_Request")
def parse_user_request(user_message: str, selected_model: str = "GPT-4o-mini"):
    """사용자 요청 분석 (Step 1) - 전체 프로세스에서 단 1회만 호출 권장"""
    active_llm = _get_active_llm(selected_model)
    parsed_obj = chat_internal.parse_user_request(user_message, active_llm)
    return parsed_obj.model_dump(mode='json')


@traceable(run_type="chain", name="Generate_Draft_Pipeline")
def regenerate_local_draft_if_needed(
    parsed: ParsedUserRequest,
    user_profile: Any,
    selected_model: str = "GPT-4o-mini",
    max_attempts: int = 3,
) -> str:
    """자소서 초안 생성 및 품질 미달 시 재생성 루프 (최적화 버전)"""
    active_llm = _get_active_llm(selected_model)
    profile = chat_internal.parse_user_profile(user_profile)
    
    # [최적화] 샘플 검색 및 분석은 루프 밖에서 단 1회만 수행
    sample = chat_internal.get_sample_context(profile, retrieval_svc, active_llm)
    
    last_text = ""
    current_parsed = parsed.model_copy(deep=True) # 원본 보존

    for attempt in range(max_attempts):
        # EXAONE 초안 생성 호출
        draft = chat_internal.build_draft_with_exaone(current_parsed, profile, sample)
        last_text = draft

        # 시스템 에러 발생 시 재생성 시도 없이 즉시 반환 (API 중복 호출 방지)
        if any(err in draft for err in ["에러:", "내부 오류:", "API 오류:", "예외 발생:"]):
            return draft

        # 품질 점검
        is_ok, reason = chat_internal.score_local_draft(draft, current_parsed)
        if is_ok:
            return draft

        # 품질 미달 시 재시도 로직
        if attempt < max_attempts - 1:
            # [최적화] 파서를 다시 호출하지 않고, 기존 데이터에 보완 지시사항만 추가
            current_parsed.raw_message += f"\n\n[이전 결과 보완 요청]: '{reason}' 문제를 해결하여 다시 작성해 주세요."

    return last_text


@traceable(run_type="chain", name="Revise_Draft_Pipeline")
def revise_existing_draft(
    existing_draft: str, 
    revision_request: str, 
    selected_model: str = "GPT-4o-mini"
) -> str:
    """기존 초안 수정 (Step 3)"""
    active_llm = _get_active_llm(selected_model)
    return chat_internal.revise_existing_draft(existing_draft, revision_request, active_llm)


@traceable(run_type="chain", name="Refine_Draft_Pipeline")
def refine_with_api(
    local_draft_body: str, 
    parsed: ParsedUserRequest, 
    selected_model: str
) -> str:
    """초안 첨삭 (Step 4)"""
    active_llm = _get_active_llm(selected_model)
    return chat_internal.refine_with_api(local_draft_body, parsed, active_llm)


@traceable(run_type="chain", name="Fit_Length_Pipeline")
def fit_length_if_needed(
    text: str, 
    parsed: ParsedUserRequest, 
    selected_model: str
) -> str:
    """글자 수 조정 (Step 5)"""
    active_llm = _get_active_llm(selected_model)
    return chat_internal.fit_length_if_needed(text, parsed, active_llm)


@traceable(run_type="chain", name="Final_Response_Pipeline")
def build_final_response(
    body: str,
    parsed: ParsedUserRequest,
    selected_model: str = "GPT-4o-mini",
    result_label: str = "자소서 초안",
    change_summary: str | None = None,
) -> str:
    """최종 응답 조립 (Step 6)"""
    active_llm = _get_active_llm(selected_model)
    
    # evaluator.py의 build_final_response 정의와 일치하도록 수정
    return chat_internal.build_final_response(
        body=body,
        parsed=parsed,
        active_llm=active_llm,
        result_label=result_label,
        change_summary=change_summary
    )
