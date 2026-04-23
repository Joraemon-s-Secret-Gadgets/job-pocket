from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# router
from routers import health_router, auth, resume, chat

# app
app = FastAPI()

# route add
app.include_router(health_router)

app = FastAPI(title="JobPocket API", description="AI Cover Letter Assistant Backend")

# CORS 설정 (Streamlit 프론트엔드 포트 8501에서의 접근을 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 상용 배포 시 ["http://localhost:8501"] 등으로 제한 권장
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 연결
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(resume.router, prefix="/api/resume", tags=["Resume"])
app.include_router(chat.router, prefix="/api/chat", tags=["AI Chat Logic"])


@app.get("/")
def root():
    return {"message": "JobPocket Backend is Running!"}
