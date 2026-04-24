"""
auth_schemas

인증(Auth) 관련 요청(Request) 및 응답(Response) 스키마를 정의합니다.

구성:
- EmailBase: 이메일 필드를 공통으로 사용하는 Base 모델
- LoginRequest: 로그인 요청
- SignupRequest: 회원가입 요청
- LoginUserInfo: 로그인 성공 시 반환되는 사용자 정보
- LoginResponse: 로그인 응답 구조
- SignupResponse: 회원가입 응답 구조
- AuthStatusResponse: 단순 상태 응답

주의:
- Request는 Pydantic(BaseModel)로 정의하여 입력 검증을 수행합니다.
- Response는 TypedDict로 정의하여 타입 안정성을 제공합니다.
"""

from typing import TypedDict

from pydantic import BaseModel, EmailStr


class EmailBase(BaseModel):
    """
    공통 이메일 필드를 가지는 Base 모델.

    Attributes:
        email: 사용자 이메일
            - EmailStr을 사용하여 이메일 형식 자동 검증 수행
    """

    email: EmailStr


class LoginRequest(EmailBase):
    """
    로그인 요청 모델.

    Attributes:
        email: 로그인에 사용할 이메일
        password: 사용자 비밀번호 (평문 입력, 서버에서 해싱 필요)
    """

    password: str


class SignupRequest(EmailBase):
    """
    회원가입 요청 모델.

    Attributes:
        email: 가입할 이메일
        name: 사용자 이름
        password: 사용자 비밀번호 (저장 시 해싱 필요)
    """

    name: str
    password: str


class LoginUserInfo(TypedDict):
    """
    로그인 성공 시 반환되는 사용자 정보.

    보안상 password는 포함하지 않습니다.

    Attributes:
        username: 사용자 이름
        email: 사용자 이메일
        resume_data: JSON 문자열 형태의 이력서 데이터
    """

    username: str
    email: str
    resume_data: str


class LoginResponse(TypedDict):
    """
    로그인 응답 구조.

    Attributes:
        status: 처리 결과 상태 ("success")
        user_info: 로그인한 사용자 정보
    """

    status: str
    user_info: LoginUserInfo


class SignupResponse(TypedDict):
    """
    회원가입 응답 구조.

    Attributes:
        status: 처리 결과 상태 ("success")
        detail: 처리 결과 메시지
    """

    status: str
    detail: str


class AuthStatusResponse(TypedDict):
    """
    인증 관련 API에서 공통으로 사용하는 최소 응답 구조.

    단순 성공/실패 여부만 전달할 때 사용합니다.
    (예: 로그인 성공, 회원가입 성공 등)

    Attributes:
        status: 처리 결과 상태 문자열
            - "success": 정상 처리
            - (필요 시) "fail" 또는 기타 상태로 확장 가능
    """

    status: str
