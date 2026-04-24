"""
user_schemas

users 테이블 및 사용자 도메인에서 사용하는 데이터 구조를 정의합니다.

구성:
- UserRow: DB에서 조회한 원본 row (resume_data는 JSON 문자열)
- UserWithResume: resume_data를 파싱한 사용자 구조

주의:
- UserRow는 repository 계층에서 사용합니다.
- UserWithResume는 service 계층에서 JSON 파싱 후 사용합니다.
"""

from typing import TypedDict

from .resume_schemas import ResumeData


class UserRow(TypedDict):
    """
    users 테이블에서 조회한 원본 row 구조

    DB의 컬럼 구조를 그대로 반영합니다.

    Attributes:
        username: 사용자 이름
        password: 해싱된 비밀번호
        email: 사용자 이메일
        resume_data: JSON 문자열 형태의 이력서 데이터
    """

    username: str
    password: str
    email: str
    resume_data: str


class UserWithResume(TypedDict):
    """
    resume_data를 JSON 문자열에서 dict로 파싱한 사용자 구조

    service 계층에서 JSON 파싱 이후 사용됩니다.

    Attributes:
        username: 사용자 이름
        password: 해싱된 비밀번호
        email: 사용자 이메일
        resume_data: 파싱된 이력서 데이터
    """

    username: str
    password: str
    email: str
    resume_data: ResumeData
