"""
chat package initialization

chat 서비스 패키지의 주요 인터페이스를 외부로 노출합니다.
각 하위 모듈(parser, analyzer, generator, evaluator)에서 핵심 함수들을 가져와 편리한 접근을 제공합니다.
"""

from .parser import (
    parse_user_profile,
    parse_user_request,
    convert_messages_to_dict
)
from .analyzer import (
    get_sample_context
)
from .generator import (
    build_draft_with_exaone,
    refine_with_api,
    revise_existing_draft,
    fit_length_if_needed,
    wrap_call_exaone
)
from .evaluator import (
    score_local_draft,
    evaluate_draft_with_api,
    build_final_response
)
from .run_exaone import (
    call_exaone
)

__all__ = [
    "parse_user_profile",
    "parse_user_request",
    "convert_messages_to_dict",
    "get_sample_context",
    "build_draft_with_exaone",
    "refine_with_api",
    "revise_existing_draft",
    "fit_length_if_needed",
    "wrap_call_exaone",
    "score_local_draft",
    "evaluate_draft_with_api",
    "build_final_response",
    "call_exaone",
]
