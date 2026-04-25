"""
generator.py

자기소개서 초안을 생성하고, 첨삭 및 수정, 글자 수 조정을 담당하는 핵심 LLM 로직 모듈입니다.
EXAONE(RunPod) 모델과 상용 API 모델(GPT-4o 등)을 적재적소에 활용합니다.

주요 기능:
- EXAONE 모델을 이용한 고품질 자소서 초안 생성
- 사용자 요청에 따른 기존 자소서 수정 및 첨삭
- 목표 글자 수에 맞춘 문장 압축 및 보강
- LLM 출력물에서 불필요한 헤더 및 기호 제거
"""

import re
from typing import Any, Optional, List, Callable
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from schemas.chat_schemas import (
    ChatUserProfile, 
    ParsedUserRequest, 
    SampleAnalysis, 
    QuestionType
)
from services.chat.prompts import (
    get_draft_system_prompt,
    DRAFT_HUMAN_PROMPT_TEMPLATE,
    get_refine_system_prompt,
    REFINE_HUMAN_PROMPT_TEMPLATE,
    REVISE_SYSTEM_PROMPT,
    REVISE_HUMAN_PROMPT_TEMPLATE,
    LENGTH_ADJUST_SYSTEM_PROMPT,
    LENGTH_ADJUST_HUMAN_PROMPT_TEMPLATE
)
from services.chat.run_exaone import call_exaone
from services.chat.parser import convert_messages_to_dict

# -----------------------------
# 유틸리티 및 래퍼
# -----------------------------
def wrap_call_exaone(messages: List[dict]) -> str:
    """RunPod EXAONE API 응답에서 결과 텍스트만 안전하게 추출합니다."""
    try:
        response = call_exaone(messages)
        if not response or not isinstance(response, dict):
            return "에러: API 응답이 비어있거나 올바르지 않습니다."
            
        if response.get("status") == "COMPLETED":
            output = response.get("output", {})
            if isinstance(output, dict) and output.get("ok"):
                return output.get("text") or ""
            return f"내부 오류: {output.get('error', '결과가 없습니다.')}"
        
        return f"API 오류: {response.get('error', '서버 응답 실패')}"
    except Exception as e:
        return f"추론 도중 예외 발생: {str(e)}"

def clean_text(text: str) -> str:
    """텍스트 정제"""
    if not text: return ""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def remove_forbidden_headers(text: str) -> str:
    """헤더 제거"""
    if not text: return ""
    cleaned = text.strip()
    block_patterns = [r"\[평가 및 코멘트\][\s\S]*$"]
    for pattern in block_patterns:
        cleaned = re.sub(pattern, "", cleaned, flags=re.MULTILINE)

    line_patterns = [
        r"^\[자소서 초안\]\s*",
        r"^\[\d+차 수정안\]\s*",
        r"^초안\s*[:：]\s*",
        r"^본문\s*[:：]\s*",
        r"^반영 사항:\s*.*$",
    ]
    for pattern in line_patterns:
        cleaned = re.sub(pattern, "", cleaned, flags=re.MULTILINE)

    return cleaned.strip()


# -----------------------------
# 생성 핵심 로직
# -----------------------------
def build_draft_with_exaone(
    parsed: ParsedUserRequest,
    profile: ChatUserProfile,
    sample: SampleAnalysis,
    inference_func: Callable[[List[dict]], str] = wrap_call_exaone
) -> str:
    """초안 생성 - 상세 Human Prompt 적용"""
    prompt = ChatPromptTemplate.from_messages([
        ("system", get_draft_system_prompt(parsed.question_type)),
        ("human", DRAFT_HUMAN_PROMPT_TEMPLATE)
    ])

    final_prompt = prompt.invoke({
        "gender": profile.gender,
        "school": profile.school,
        "major": profile.major,
        "exp": profile.experience,
        "awards": profile.awards,
        "tech": profile.skills,
        "user_message": parsed.raw_message,
        "company": parsed.company or "미기재",
        "job": parsed.job or "미기재",
        "question": parsed.question or "미기재",
        "question_type": parsed.question_type.value,
        "char_limit": parsed.char_limit or "미기재",
        "sample_summary": sample.summary,
        "style_rules": sample.style_rules,
        "sample_excerpt": sample.excerpt or "없음",
    })

    messages = convert_messages_to_dict(final_prompt.to_messages())
    result = inference_func(messages)
    return clean_text(remove_forbidden_headers(result))


def refine_with_api(
    local_draft_body: str, 
    parsed: ParsedUserRequest, 
    active_llm: Any
) -> str:
    """API 모델을 통한 초안 첨삭 - 이미 분석된 parsed 객체 사용"""
    sys_prompt = get_refine_system_prompt(parsed.question_type)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", sys_prompt),
        ("human", REFINE_HUMAN_PROMPT_TEMPLATE)
    ])

    try:
        result = (prompt | active_llm | StrOutputParser()).invoke({
            "user_message": parsed.raw_message,
            "company": parsed.company or "미기재",
            "job": parsed.job or "미기재",
            "question": parsed.question or "미기재",
            "question_type": parsed.question_type.value,
            "char_limit": parsed.char_limit or "미기재",
            "local_draft_body": local_draft_body or "",
        })
        return clean_text(remove_forbidden_headers(result))
    except Exception as e:
        return local_draft_body or f"첨삭 중 오류 발생: {str(e)}"


def revise_existing_draft(
    existing_draft: str, 
    revision_request: str, 
    active_llm: Any
) -> str:
    """수정 요청 반영 - 상세 Human Prompt 적용"""
    prompt = ChatPromptTemplate.from_messages([
        ("system", REVISE_SYSTEM_PROMPT),
        ("human", REVISE_HUMAN_PROMPT_TEMPLATE)
    ])
    
    try:
        result = (prompt | active_llm | StrOutputParser()).invoke({
            "existing_draft": existing_draft or "",
            "revision_request": revision_request or "",
        })
        return clean_text(remove_forbidden_headers(result))
    except Exception as e:
        return existing_draft or f"수정 중 오류 발생: {str(e)}"


def fit_length_if_needed(
    text: str, 
    parsed: ParsedUserRequest, 
    active_llm: Any
) -> str:
    """글자 수 조정 - 이미 분석된 parsed 객체 사용"""
    target = parsed.char_limit
    if not target: return text or ""
    
    current = len(text or "")
    lower = int(target * 0.9)
    upper = int(target * 1.05)

    if lower <= current <= upper:
        return text or ""

    direction = (
        "조금 더 압축해 주세요."
        if current > upper
        else "조금 더 내용을 보강해 주세요. 단, 없는 경험은 추가하지 마세요."
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", LENGTH_ADJUST_SYSTEM_PROMPT),
        ("human", LENGTH_ADJUST_HUMAN_PROMPT_TEMPLATE)
    ])
    
    try:
        result = (prompt | active_llm | StrOutputParser()).invoke({
            "user_message": parsed.raw_message,
            "text": text or "",
            "target": target,
            "current": current,
            "direction": direction,
        })
        return clean_text(remove_forbidden_headers(result))
    except Exception:
        return text or ""
