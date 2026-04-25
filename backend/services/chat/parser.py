"""
parser.py

사용자 정보 및 요청 메시지를 분석하고 구조화된 데이터로 변환하는 모듈입니다.
LangChain의 JsonOutputParser를 사용하여 사용자 의도를 정밀하게 추출합니다.

주요 기능:
- DB 및 API로부터 받은 사용자 프로필 파싱
- 사용자 메시지 기반 자소서 문항 유형 감지
- 정규표현식 및 LLM을 결합한 자소서 작성 조건(ParsedUserRequest) 추출
- LangChain 메시지 객체를 dict 리스트로 변환
"""

import json
import re
from typing import Any, Optional, List, Dict

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import BaseMessage

from schemas.chat_schemas import (
    ChatUserProfile, 
    ParsedUserRequest, 
    QuestionType, 
    LLMParsedRequest
)
from services.chat.prompts import PARSER_SYSTEM_PROMPT

def parse_user_profile(user_profile: Any) -> ChatUserProfile:
    """사용자 프로필 데이터를 정제된 ChatUserProfile 객체로 변환합니다."""
    resume_data = {}
    if isinstance(user_profile, dict):
        resume_raw = user_profile.get("resume_data", {})
        if isinstance(resume_raw, str):
            try: resume_data = json.loads(resume_raw)
            except: resume_data = {}
        else: resume_data = resume_raw
    elif isinstance(user_profile, (tuple, list)):
        resume_raw = user_profile[3] if len(user_profile) > 3 else "{}"
        if isinstance(resume_raw, str):
            try: resume_data = json.loads(resume_raw)
            except: resume_data = {}
        else: resume_data = resume_raw

    personal = resume_data.get("personal", {})
    edu = resume_data.get("education", {})
    add = resume_data.get("additional", {})

    return ChatUserProfile(
        gender=personal.get("gender", "선택안함"),
        school=edu.get("school", "정보 없음"),
        major=edu.get("major", "정보 없음"),
        experience=add.get("internship", "정보 없음"),
        awards=add.get("awards", "정보 없음"),
        skills=add.get("tech_stack", "정보 없음"),
    )


def detect_question_type(user_message: str) -> QuestionType:
    """메시지 키워드 기반 문항 유형 감지"""
    text = user_message.lower()
    if any(k in text for k in ["지원 이유", "지원이유", "지원 동기", "지원동기", "왜 지원", "입사 이유"]):
        return QuestionType.MOTIVATION
    if any(k in text for k in ["입사 후 포부", "포부", "입사후"]):
        return QuestionType.FUTURE_GOAL
    if any(k in text for k in ["협업", "팀워크", "같이", "소통"]):
        return QuestionType.COLLABORATION
    if any(k in text for k in ["문제 해결", "문제해결", "해결 경험", "어려움", "개선"]):
        return QuestionType.PROBLEM_SOLVING
    if any(k in text for k in ["성장", "노력", "배운 점", "배움"]):
        return QuestionType.GROWTH
    return QuestionType.GENERAL


def parse_user_request_regex(user_message: str) -> ParsedUserRequest:
    """정규표현식 기반 파싱"""
    text = user_message.strip()
    char_limit = None
    patterns = [r"(\d{3,4})\s*자\s*이내", r"(\d{3,4})\s*자\s*내외", r"(\d{3,4})\s*자\s*정도", r"(\d{3,4})\s*자", r"(\d{3,4})\s*byte"]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                char_limit = int(match.group(1))
                break
            except: pass

    company, job, question = "", "", ""
    company_match = re.search(r"(회사|기업|지원회사)\s*[:：]\s*(.+)", text)
    if company_match: company = company_match.group(2).splitlines()[0].strip()

    job_match = re.search(r"(직무|포지션|지원직무)\s*[:：]\s*(.+)", text)
    if job_match: job = job_match.group(2).splitlines()[0].strip()

    natural_patterns = [r"(.+?)에\s+(.+?)\s*직무로\s+지원", r"(.+?)\s+(.+?)\s*직무에\s+지원", r"(.+?)에\s+지원"]
    for idx, pattern in enumerate(natural_patterns):
        match = re.search(pattern, text)
        if match:
            if idx < 2:
                if not company: company = match.group(1).strip()
                if not job: job = match.group(2).strip()
            else:
                if not company: company = match.group(1).strip()

    q_patterns = [r"(.+?)(?:를|을)\s*물어봤", r"문항\s*[:：]\s*(.+)", r"질문\s*[:：]\s*(.+)",]
    for pattern in q_patterns:
        match = re.search(pattern, text)
        if match:
            question = match.group(1).strip()
            break

    return ParsedUserRequest(
        raw_message=text,
        company=company,
        job=job,
        question=question,
        char_limit=char_limit,
        question_type=detect_question_type(text)
    )


def llm_parse_user_request(user_message: str, active_llm: Any) -> dict[str, Any]:
    """JsonOutputParser를 사용하여 안정적으로 구조화된 데이터를 추출합니다."""
    parser = JsonOutputParser(pydantic_object=LLMParsedRequest)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", PARSER_SYSTEM_PROMPT + "\n\n{format_instructions}"),
        ("human", "사용자 요청:\n{user_message}")
    ])
    
    chain = prompt | active_llm | parser
    try:
        return chain.invoke({
            "user_message": user_message,
            "format_instructions": parser.get_format_instructions()
        })
    except:
        return {}


def parse_user_request(user_message: str, active_llm: Any) -> ParsedUserRequest:
    """통합 파싱 로직 (Regex + JSON Parser)"""
    base = parse_user_request_regex(user_message)
    
    if not base.company or not base.job or base.question_type == QuestionType.GENERAL:
        llm_data = llm_parse_user_request(user_message, active_llm)

        if not base.company: base.company = str(llm_data.get("company", "") or "").strip()
        if not base.job: base.job = str(llm_data.get("job", "") or "").strip()
        if not base.question: base.question = str(llm_data.get("question", "") or "").strip()
        if not base.char_limit and llm_data.get("char_limit"):
            try: base.char_limit = int(llm_data["char_limit"])
            except: pass
        if base.question_type == QuestionType.GENERAL and llm_data.get("question_type"):
            try: base.question_type = QuestionType(llm_data["question_type"])
            except: pass

    if not base.question:
        qtype_map = {
            QuestionType.MOTIVATION: "지원한 이유",
            QuestionType.FUTURE_GOAL: "입사 후 포부",
            QuestionType.COLLABORATION: "협업 경험",
            QuestionType.PROBLEM_SOLVING: "문제 해결 경험",
            QuestionType.GROWTH: "성장 과정 또는 노력 경험",
        }
        base.question = qtype_map.get(base.question_type, "자기소개서 문항")

    return base

def convert_messages_to_dict(messages: List[BaseMessage]) -> List[Dict[str, str]]:
    """메시지 변환 유틸리티"""
    role_map = {"human": "user", "ai": "assistant", "system": "system", "chat": "user"}
    converted = []
    for msg in messages:
        role = role_map.get(msg.type, "user")
        content = msg.content if isinstance(msg.content, str) else str(msg.content)
        converted.append({"role": role, "content": content})
    return converted
