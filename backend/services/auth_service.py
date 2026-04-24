"""
auth_service

인증 관련 비즈니스 로직을 담당합니다.
"""

from fastapi import HTTPException

from repository import get_user, add_user_via_web
from schemas import UserRow, LoginResponse, SignupResponse
from utils.security import hash_pw


def login_user(email: str, password: str) -> LoginResponse:
    """
    사용자 로그인 처리

    Args:
        email: 사용자 이메일
        password: 평문 비밀번호

    Returns:
        로그인 성공 상태와 사용자 정보.
        보안상 password는 응답에서 제외합니다.

    Raises:
        HTTPException: 인증 실패 시
    """
    user: UserRow | None = get_user(email)

    if user and user["password"] == hash_pw(password):
        return {
            "status": "success",
            "user_info": {
                "username": user["username"],
                "email": user["email"],
                "resume_data": user["resume_data"],
            },
        }

    raise HTTPException(
        status_code=401,
        detail="이메일 또는 비밀번호가 일치하지 않습니다.",
    )


def signup_user(name: str, email: str, password: str) -> SignupResponse:
    """
    사용자 회원가입 처리

    Args:
        name: 사용자 이름
        email: 이메일
        password: 평문 비밀번호

    Returns:
        회원가입 성공 상태와 메시지.

    Raises:
        HTTPException: 중복 이메일 또는 DB 오류
    """
    success, msg = add_user_via_web(
        name=name,
        password_hash=hash_pw(password),
        email=email,
    )

    if not success:
        raise HTTPException(status_code=400, detail=msg)

    return {
        "status": "success",
        "detail": msg,
    }
