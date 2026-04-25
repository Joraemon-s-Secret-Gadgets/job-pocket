"""
analyzer.py

유사 자소서 샘플을 검색하고 패턴을 분석하는 모듈입니다.
검색된 샘플들로부터 공통 강점, 서술 구조, 표현 톤 등을 추출하여 초안 생성의 재료로 제공합니다.

주요 기능:
- RetrievalService를 이용한 유사 자소서 검색
- 검색된 샘플들의 공통 패턴 요약 (JsonOutputParser 사용)
- 샘플 기반의 구체적인 작성 규칙 추출
- 초안 생성을 위한 종합 컨텍스트(SampleAnalysis) 구성
"""

import re
from typing import Any, List

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate

from schemas.chat_schemas import ChatUserProfile, SampleAnalysis, LLMSampleSummary
from services.chat.prompts import (
    SAMPLE_SUMMARIZER_SYSTEM_PROMPT, 
    STYLE_RULE_EXTRACTOR_SYSTEM_PROMPT,
    SAMPLE_SUMMARY_FALLBACK,
    STYLE_RULES_FALLBACK
)

def clean_text(text: str) -> str:
    """텍스트 정제"""
    if not text: return ""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def retrieve_raw_samples(query: str, retriever: Any) -> List[str]:
    """유사 자소서 샘플 검색"""
    search_results = retriever.search(query)
    return [doc.page_content.strip() for doc in search_results]


def build_sample_excerpt(samples: List[str], max_chars_per_sample: int = 700) -> str:
    """샘플 발췌본 구성"""
    trimmed = []
    for idx, sample in enumerate(samples, start=1):
        cleaned = sample.strip()
        if len(cleaned) > max_chars_per_sample:
            cleaned = cleaned[:max_chars_per_sample].rstrip() + "..."
        trimmed.append(f"[샘플 {idx}]\n{cleaned}")
    return "\n\n".join(trimmed)


def summarize_samples(samples: List[str], active_llm: Any) -> str:
    """JsonOutputParser를 사용하여 샘플 패턴을 정밀 요약하고 문자열로 변환합니다."""
    if not samples:
        return (
            "공통 강점:\n- 유사 샘플이 없어 기본 패턴만 참고\n\n"
            "서술 구조:\n- 사용자의 경험을 중심으로 문항에 직접 답변\n\n"
            "표현 톤:\n- 담백하고 과장 없는 문장"
        )

    joined = build_sample_excerpt(samples)
    parser = JsonOutputParser(pydantic_object=LLMSampleSummary)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", SAMPLE_SUMMARIZER_SYSTEM_PROMPT + "\n\n{format_instructions}"),
        ("human", "유사 자소서 샘플:\n{joined}")
    ])

    chain = prompt | active_llm | parser
    try:
        data = chain.invoke({
            "joined": joined,
            "format_instructions": parser.get_format_instructions()
        })
        
        # 구조화된 데이터를 기존 줄글 포맷으로 역직렬화 (호환성 유지)
        lines = []
        if data.get("strengths"):
            lines.append("공통 강점:")
            lines.extend([f"- {s}" for s in data["strengths"]])
            lines.append("")
        if data.get("structure"):
            lines.append("서술 구조:")
            lines.extend([f"- {s}" for s in data["structure"]])
            lines.append("")
        if data.get("tone"):
            lines.append("표현 톤:")
            lines.extend([f"- {s}" for s in data["tone"]])
            lines.append("")
        if data.get("pitfalls"):
            lines.append("피해야 할 점:")
            lines.extend([f"- {s}" for s in data["pitfalls"]])
            
        return "\n".join(lines).strip()
    except Exception:
        return SAMPLE_SUMMARY_FALLBACK


def extract_sample_style_rules(sample_summary: str, active_llm: Any) -> str:
    """작성 규칙 추출"""
    prompt = ChatPromptTemplate.from_messages([
        ("system", STYLE_RULE_EXTRACTOR_SYSTEM_PROMPT),
        ("human", "샘플 요약 내용:\n{sample_summary}")
    ])
    from langchain_core.output_parsers import StrOutputParser
    chain = prompt | active_llm | StrOutputParser()
    try:
        return clean_text(chain.invoke({"sample_summary": sample_summary}))
    except Exception:
        return STYLE_RULES_FALLBACK


def get_sample_context(
    profile: ChatUserProfile,
    retriever: Any,
    active_llm: Any
) -> SampleAnalysis:
    """통합 분석 수행"""
    query = f"""[최종학력] {profile.school} {profile.major}
    [경력 및 경험]
    {profile.experience}
    {profile.awards}
    [기술 및 역량]
    {profile.skills}
    """
    samples = retrieve_raw_samples(query, retriever)
    sample_summary = summarize_samples(samples, active_llm)
    style_rules = extract_sample_style_rules(sample_summary, active_llm)
    excerpt = build_sample_excerpt(samples)

    return SampleAnalysis(
        summary=sample_summary,
        style_rules=style_rules,
        excerpt=excerpt or "없음"
    )
