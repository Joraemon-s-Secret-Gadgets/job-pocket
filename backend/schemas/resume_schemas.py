from typing import TypedDict


class Personal(TypedDict):
    """
    개인 기본 정보 영역

    Attributes:
        eng_name: 영문 이름
        gender: 성별
    """

    eng_name: str
    gender: str


class Education(TypedDict):
    """
    학력 정보 영역

    Attributes:
        school: 학교명
        major: 전공
    """

    school: str
    major: str


class Additional(TypedDict):
    """
    추가 정보 영역

    Attributes:
        internship: 인턴, 경험, 자기소개 관련 내용
        awards: 수상 및 활동 이력
        tech_stack: 기술 스택
    """

    internship: str
    awards: str
    tech_stack: str


class ResumeData(TypedDict):
    """
    users.resume_data 컬럼의 JSON 구조

    Attributes:
        personal: 개인 기본 정보
        education: 학력 정보
        additional: 추가 이력 정보
    """

    personal: Personal
    education: Education
    additional: Additional
