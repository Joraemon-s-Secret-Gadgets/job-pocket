"""
chat_service

채팅 및 RAG 프로세스에 대한 비즈니스 로직을 담당하는 서비스 계층입니다.
프론트엔드로부터 받은 데이터를 chat_logic의 각 단계로 전달합니다.
"""

from typing import List, Any, Dict, Optional
from repository import chat_repository
from services import chat_logic
from schemas.chat_schemas import ParsedUserRequest


def get_chat_history(email: str) -> Dict[str, List]:
    """사용자 채팅 기록 조회"""
    messages = chat_repository.load_chat_history(email)
    return {"messages": messages}


def save_message(email: str, role: str, content: str) -> Dict[str, str]:
    """채팅 메시지 저장"""
    chat_repository.save_chat_message(email, role, content)
    return {"status": "success"}


def clear_history(email: str) -> Dict[str, str]:
    """채팅 기록 삭제"""
    chat_repository.delete_chat_history(email)
    return {"status": "success"}


def parse_request(prompt: str, model: str):
    """사용자 요청 분석 (Step 1) - 원문을 구조화된 데이터로 변환"""
    return chat_logic.parse_user_request(prompt, model)


def generate_draft(prompt_dict: Any, user_info: Any, model: str):
    """자소서 초안 생성 (Step 2) - 이미 파싱된 데이터를 사용"""
    # prompt_dict는 ParsedUserRequest 구조의 딕셔너리임
    parsed = ParsedUserRequest(**prompt_dict) if isinstance(prompt_dict, dict) else prompt_dict
    draft = chat_logic.regenerate_local_draft_if_needed(parsed, user_info, model)
    return {"draft": draft}


def revise_draft(existing_draft: str, revision_request: str, model: str):
    """자소서 수정 (Step 3)"""
    revised = chat_logic.revise_existing_draft(existing_draft, revision_request, model)
    return {"revised": revised}


def refine_draft(draft: str, prompt_dict: Any, model: str):
    """자소서 문장 정제 (Step 4) - 이미 파싱된 데이터를 사용"""
    parsed = ParsedUserRequest(**prompt_dict) if isinstance(prompt_dict, dict) else prompt_dict
    try:
        refined = chat_logic.refine_with_api(draft, parsed, model)
    except Exception:
        refined = draft
    return {"refined": refined}


def adjust_length(refined: str, prompt_dict: Any, model: str):
    """자소서 길이 조정 (Step 5) - 이미 파싱된 데이터를 사용"""
    parsed = ParsedUserRequest(**prompt_dict) if isinstance(prompt_dict, dict) else prompt_dict
    try:
        adjusted = chat_logic.fit_length_if_needed(refined, parsed, model)
    except Exception:
        adjusted = refined
    return {"adjusted": adjusted}


def finalize_response(
    adjusted: str,
    prompt_dict: Any,
    model: str,
    result_label: str = "자소서 초안",
    change_summary: Optional[str] = None,
):
    """최종 응답 생성 (Step 6) - 이미 파싱된 데이터를 사용"""
    parsed = ParsedUserRequest(**prompt_dict) if isinstance(prompt_dict, dict) else prompt_dict
    final_response = chat_logic.build_final_response(
        body=adjusted,
        parsed=parsed,
        selected_model=model,
        result_label=result_label,
        change_summary=change_summary,
    )
    return {"final_response": final_response}
