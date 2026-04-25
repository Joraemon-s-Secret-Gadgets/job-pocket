"""
chat_routers.py

채팅 이력 관리 및 RAG(Retrieval-Augmented Generation) 단계별 프로세스 API 라우터입니다.

역할:
- 클라이언트의 채팅 관련 요청(조회, 저장, 삭제)을 받아 service 계층으로 전달
- 자소서 생성을 위한 RAG 단계별 프로세스(분석, 초안, 수정, 정제, 조정, 확정) 엔드포인트 제공

구성:
- GET /history/{email}: 채팅 이력 조회
- POST /message: 채팅 메시지 저장
- DELETE /history/{email}: 채팅 이력 삭제
- POST /step-parse: 사용자 요청 분석
- POST /step-draft: 자소서 초안 생성
- POST /step-revise: 자소서 수정 요청 처리
- POST /step-refine: 문장 정제 및 고도화
- POST /step-fit: 글자 수 및 분량 조정
- POST /step-final: 최종 응답 조립 및 확정

주의:
- 모든 비즈니스 로직과 LLM 호출은 services.chat_service에서 처리합니다.
- 데이터 검증은 schemas 패키지의 Pydantic 모델을 사용합니다.
"""

from fastapi import APIRouter
from services import (
    get_chat_history,
    save_message,
    clear_history,
    parse_request,
    generate_draft,
    revise_draft,
    refine_draft,
    adjust_length,
    finalize_response,
)
from schemas import (
    ChatMessageRequest,
    StepParseRequest,
    StepDraftRequest,
    StepReviseRequest,
    StepRefineRequest,
    StepFitRequest,
    StepFinalRequest,
)

router = APIRouter(prefix="/chat", tags=["AI Chat Logic"])


@router.get("/history/{email}")
def history(email: str):
    return get_chat_history(email)


@router.post("/message")
def message(req: ChatMessageRequest):
    return save_message(req.email, req.role, req.content)


@router.delete("/history/{email}")
def delete_history(email: str):
    return clear_history(email)


@router.post("/step-parse")
def step_parse(req: StepParseRequest):
    return parse_request(req.prompt, req.model)


@router.post("/step-draft")
def step_draft(req: StepDraftRequest):
    return generate_draft(req.prompt, req.user_info, req.model)


@router.post("/step-revise")
def step_revise(req: StepReviseRequest):
    return revise_draft(req.existing_draft, req.revision_request, req.model)


@router.post("/step-refine")
def step_refine(req: StepRefineRequest):
    return refine_draft(req.draft, req.prompt, req.model)


@router.post("/step-fit")
def step_fit(req: StepFitRequest):
    return adjust_length(req.refined, req.prompt, req.model)


@router.post("/step-final")
def step_final(req: StepFinalRequest):
    return finalize_response(
        adjusted=req.adjusted,
        prompt=req.prompt,
        model=req.model,
        result_label=req.result_label,
        change_summary=req.change_summary,
    )
