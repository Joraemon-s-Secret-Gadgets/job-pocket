"""
evaluator.py

생성된 자기소개서의 품질을 점검하고 상세한 평가 피드백을 생성하는 모듈입니다.
글자 수, 반복도, 과장 표현 등을 규칙 기반으로 점검하고, LLM을 통해 정밀 품질 평가를 수행합니다.

주요 기능:
- 문장 반복 비율 및 최소 길이 등 품질 규칙(Rule-based) 점검
- 과장 표현 패턴(OVERSTATEMENT_PATTERNS) 검출
- LLM을 이용한 상세 품질 평가 및 보완 포인트 생성 (JsonOutputParser 사용)
- 평가 결과와 본문을 결합하여 최종 응답 형식 조립
"""

import re
from typing import List, Tuple, Any, Optional
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from schemas.chat_schemas import (
    ParsedUserRequest, 
    QuestionType,
    LLMEvaluationResult
)
from services.chat.prompts import (
    EVALUATOR_SYSTEM_PROMPT, 
    EVALUATOR_HUMAN_PROMPT_TEMPLATE,
    OVERSTATEMENT_PATTERNS
)

def split_sentences_korean(text: str) -> List[str]:
    """한국어 문장 단위 분리"""
    chunks = re.split(r"(?<=[.!?다요])\s+", text.strip())
    return [c.strip() for c in chunks if c.strip()]

def repetition_ratio(text: str) -> float:
    """반복 비율 계산"""
    sentences = split_sentences_korean(text)
    if not sentences: return 1.0
    unique_count = len(set(sentences))
    return 1 - (unique_count / len(sentences))

def score_local_draft(text: str, parsed: ParsedUserRequest) -> Tuple[bool, str]:
    """품질 요건 점검"""
    if not text or len(text.strip()) < 220:
        return False, "초안 길이가 너무 짧습니다."
    if repetition_ratio(text) > 0.48:
        return False, "문장 반복이 많습니다."
    if parsed.char_limit:
        target = parsed.char_limit
        current = len(text)
        if current < max(220, int(target * 0.55)):
            return False, "글자 수가 목표 대비 지나치게 짧습니다."
    if parsed.question_type == QuestionType.MOTIVATION:
        if parsed.company and parsed.company not in text:
            return False, "지원동기 문항인데 실제 지원 회사명이 반영되지 않았습니다."
        first_para = text.split("\n\n")[0].strip()
        if len(first_para) < 40:
            return False, "첫 문단에서 지원 이유가 충분히 드러나지 않습니다."
    for pattern in OVERSTATEMENT_PATTERNS:
        if pattern in text:
            return False, f"과장 표현이 포함되어 있습니다: {pattern}"
    return True, "통과"

def evaluate_draft_with_api(
    body: str,
    parsed: ParsedUserRequest,
    active_llm: Any
) -> str:
    """JsonOutputParser를 사용하여 자소서를 상세 평가하고 문자열 피드백을 반환합니다."""
    parser = JsonOutputParser(pydantic_object=LLMEvaluationResult)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", EVALUATOR_SYSTEM_PROMPT + "\n\n{format_instructions}"),
        ("human", EVALUATOR_HUMAN_PROMPT_TEMPLATE)
    ])

    chain = prompt | active_llm | parser
    try:
        data = chain.invoke({
            "user_message": parsed.raw_message,
            "company": parsed.company or "미기재",
            "job": parsed.job or "미기재",
            "question": parsed.question or "미기재",
            "question_type": parsed.question_type.value,
            "body": body,
            "format_instructions": parser.get_format_instructions()
        })
        
        # 구조화된 데이터를 기존 백업 파일의 문자열 형식으로 변환 (호환성 유지)
        lines = [
            f"평가 결과: {data.get('label', '보통')}",
            f"이유: {data.get('reason', '전반적으로 무난한 초안입니다.')}",
            "보완 포인트:"
        ]
        points = data.get('points', [])
        for pt in points[:2]: # 최대 2개 보장
            lines.append(f"- {pt}")
            
        return "\n".join(lines).strip()
    except Exception:
        raise RuntimeError("평가 데이터 파싱 실패")

def build_final_response(
    body: str,
    parsed: ParsedUserRequest,
    active_llm: Any,
    result_label: str = "자소서 초안",
    change_summary: Optional[str] = None
) -> str:
    """최종 응답 조립"""
    is_revision = result_label.endswith("수정안")
    
    try:
        evaluation_text = evaluate_draft_with_api(body, parsed, active_llm)
    except Exception:
        # 폴백 로직
        current_len = len(body)
        res_label = "좋다" if current_len >= 300 else "보통"
        reason = "요청한 수정 방향이 문장 흐름에 반영되도록 정리했습니다." if is_revision else "문항 의도와 사용자 경험이 자연스럽게 이어지도록 정리했습니다."
        evaluation_text = (
            f"평가 결과: {res_label}\n"
            f"이유: {reason}\n"
            "보완 포인트:\n"
            "- 첫 문장을 조금 더 구체적으로 다듬어 보세요.\n"
            "- 마지막 문단의 기여 방향을 조금 더 현실적인 표현으로 정리하면 좋습니다."
        )

    lines = [f"[{result_label}]", ""]
    if change_summary:
        lines.append(f"반영 사항: {change_summary}")
        lines.append("")

    lines.append(body)
    lines.append("")
    lines.append("[평가 및 코멘트]")
    lines.append(evaluation_text)

    return "\n".join(lines).strip()
