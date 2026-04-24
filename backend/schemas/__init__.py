"""
schemas package

FastAPI 애플리케이션 전반에서 사용하는 데이터 구조(Type Schema)를 정의하고,
외부에서 사용할 수 있도록 export하는 모듈입니다.

구성:
- health_schemas: 헬스 체크 응답 구조
- user_schemas: 사용자(User) 관련 구조
- auth_schemas: 인증 요청/응답 구조
- resume_schemas: 이력서(JSON) 데이터 구조
- chat_schemas: 채팅 데이터 구조

주의:
- 이 패키지는 데이터 구조 정의만 담당합니다.
- 비즈니스 로직은 services, DB 접근은 repository에서 처리합니다.
"""

# health schemas
from .health_schemas import (
    DatabaseHealthResponse,
    DatabaseHealthItem,
    HealthResponse,
)

# auth schemas
from .auth_schemas import (
    SignupRequest,
    LoginRequest,
    AuthStatusResponse,
    LoginUserInfo,
    LoginResponse,
    SignupResponse,
)

# user schemas
from .user_schemas import (
    UserRow,
    UserWithResume,
)

# resume schemas
from .resume_schemas import (
    ResumeData,
    Personal,
    Education,
    Additional,
)

# chat schemas
from .chat_schemas import (
    ChatMessage,
)


__all__ = [
    # health
    "HealthResponse",
    "DatabaseHealthItem",
    "DatabaseHealthResponse",
    # auth
    "SignupRequest",
    "LoginRequest",
    "AuthStatusResponse",
    "LoginUserInfo",
    "LoginResponse",
    "SignupResponse",
    # user
    "UserRow",
    "UserWithResume",
    # resume
    "ResumeData",
    "Personal",
    "Education",
    "Additional",
    # chat
    "ChatMessage",
]
