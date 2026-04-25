"""
main

JobPocket FastAPI 애플리케이션의 부트스트랩 구성을 담당합니다.
"""

from fastapi import FastAPI

# middleware
from middlewares import setup_cors

# router
from routers import health_router, auth_router, resume_router, chat_router

# app
app: FastAPI = FastAPI(
    title="JobPocket API",
    description="AI Cover Letter Assistant Backend",
)
# middleware registration
setup_cors(app)

# router registration
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(resume_router)
app.include_router(chat_router)


@app.get("/")
def root() -> dict[str, str]:
    """
    루트 상태 확인 엔드포인트

    Returns:
        백엔드 서버 실행 상태 메시지.
    """
    return {"message": "JobPocket Backend is Running!"}
