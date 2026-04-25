"""
chat_routers.py

채팅 이력 관리 및 RAG 단계별 프로세스 API 라우터입니다.
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
    # req.prompt 대신 req.parsed_data 사용 (스키마 변경 반영)
    return generate_draft(req.parsed_data, req.user_info, req.model)


@router.post("/step-revise")
def step_revise(req: StepReviseRequest):
    return revise_draft(req.existing_draft, req.revision_request, req.model)


@router.post("/step-refine")
def step_refine(req: StepRefineRequest):
    # req.prompt 대신 req.parsed_data 사용
    return refine_draft(req.draft, req.parsed_data, req.model)


@router.post("/step-fit")
def step_fit(req: StepFitRequest):
    # req.prompt 대신 req.parsed_data 사용
    return adjust_length(req.refined, req.parsed_data, req.model)


@router.post("/step-final")
def step_final(req: StepFinalRequest):
    # req.prompt 대신 req.parsed_data 사용
    return finalize_response(
        adjusted=req.adjusted,
        prompt_dict=req.parsed_data,
        model=req.model,
        result_label=req.result_label,
        change_summary=req.change_summary,
    )
