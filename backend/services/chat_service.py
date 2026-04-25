"""
chat_service

채팅 및 RAG 프로세스에 대한 비즈니스 로직을 담당하는 서비스 계층입니다.
DB 접근은 repository를, LLM 프로세스는 chat_logic을 호출하여 수행합니다.
"""

from typing import List, Any, Dict, Optional
from repository import chat_repository
from services import chat_logic


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
    """사용자 요청 분석 (Step 1)"""
    return chat_logic.parse_user_request(prompt, model)


def generate_draft(prompt: str, user_info: List[Any], model: str):
    """자소서 초안 생성 (Step 2)"""
    draft = chat_logic.regenerate_local_draft_if_needed(prompt, tuple(user_info), model)
    return {"draft": draft}


def revise_draft(existing_draft: str, revision_request: str, model: str):
    """자소서 수정 (Step 3)"""
    revised = chat_logic.revise_existing_draft(existing_draft, revision_request, model)
    return {"revised": revised}


def refine_draft(draft: str, prompt: str, model: str):
    """자소서 문장 정제 (Step 4)"""
    try:
        refined = chat_logic.refine_with_api(draft, prompt, model)
    except Exception:
        refined = draft
    return {"refined": refined}


def adjust_length(refined: str, prompt: str, model: str):
    """자소서 길이 조정 (Step 5)"""
    try:
        adjusted = chat_logic.fit_length_if_needed(refined, prompt, model)
    except Exception:
        adjusted = refined
    return {"adjusted": adjusted}


def finalize_response(
    adjusted: str,
    prompt: str,
    model: str,
    result_label: str = "자소서 초안",
    change_summary: Optional[str] = None,
):
    """최종 응답 생성 (Step 6)"""
    final_response = chat_logic.build_final_response(
        body=adjusted,
        user_message=prompt,
        selected_model=model,
        result_label=result_label,
        change_summary=change_summary,
    )
    return {"final_response": final_response}
