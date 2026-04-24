"""
Job-Pocket 공용 pytest fixture

외부 LLM API는 mocking하고,
DB는 같은 MySQL DB 안에서 test_ prefix 테이블을 생성/삭제하여 격리한다.

테스트 DB 전략:
- CREATE DATABASE / DROP DATABASE를 사용하지 않는다.
- 기존 테이블 구조를 CREATE TABLE ... LIKE ... 로 복제한다.
- 테스트 중에는 database.TABLE_PREFIX = "test_" 로 변경한다.
- 테스트 종료 후 test_ 테이블만 삭제한다.
"""

import os
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.engine import Engine


@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """
    테스트 세션 시작 시 환경변수를 설정한다.
    """
    os.environ["PYTEST_MOCK_LLM"] = "true"
    os.environ.setdefault("OPENAI_API_KEY", "sk-fake-for-test")
    os.environ.setdefault("GROQ_API_KEY", "fake-for-test")
    os.environ.setdefault("LANGSMITH_TRACING", "false")

    yield


TEST_TABLE_PREFIX = "test_"

BASE_TABLES: tuple[str, ...] = (
    "users",
    "chat_history",
)


@pytest.fixture(scope="session")
def test_engine() -> Engine:
    """
    현재 RDB_URL이 가리키는 MySQL DB에 연결한다.
    """
    from common.db import create_rdb_engine

    engine = create_rdb_engine()

    yield engine

    engine.dispose()


@pytest.fixture(autouse=True)
def set_test_table_prefix(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    repository 계층의 테이블 prefix를 테스트용으로 변경합니다.
    """
    import repository.base as repository_base

    monkeypatch.setattr(
        repository_base,
        "TABLE_PREFIX",
        TEST_TABLE_PREFIX,
    )


@pytest.fixture(scope="function")
def clean_db(test_engine: Engine):
    """
    각 테스트 함수마다 test_ prefix 테이블을 생성하고 삭제한다.

    생성:
    - users -> test_users
    - chat_history -> test_chat_history

    삭제:
    - test_chat_history
    - test_users
    """
    with test_engine.connect() as conn:
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))

        for base_table in BASE_TABLES:
            test_table = f"{TEST_TABLE_PREFIX}{base_table}"
            conn.execute(text(f"DROP TABLE IF EXISTS `{test_table}`"))
            conn.execute(text(f"CREATE TABLE `{test_table}` LIKE `{base_table}`"))

        conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
        conn.commit()

    yield test_engine

    with test_engine.connect() as conn:
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))

        for base_table in reversed(BASE_TABLES):
            test_table = f"{TEST_TABLE_PREFIX}{base_table}"
            conn.execute(text(f"DROP TABLE IF EXISTS `{test_table}`"))

        conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
        conn.commit()


@pytest.fixture(scope="module")
def client():
    """
    FastAPI TestClient.

    주의: 이 fixture는 D-001 결함(main.py 라우터 등록) 해결 후 정상 동작한다.
    해결 전에는 /health/z만 접근 가능하고 나머지는 404 반환.
    """
    # import는 fixture 안에서 수행 (환경변수 먼저 설정되어야 함)
    import main  # backend/main.py

    with TestClient(main.app) as tc:
        yield tc


@pytest.fixture
def test_user(clean_db):
    """
    사전에 가입된 테스트 유저를 제공한다.
    """
    import repository.base as repository_base
    from repository import add_user_via_web
    from utils.security import hash_pw

    repository_base.TABLE_PREFIX = TEST_TABLE_PREFIX

    user_data = {
        "name": "테스트유저",
        "email": "test@example.com",
        "password": "pass123",
        "password_hash": hash_pw("pass123"),
    }

    success, detail = add_user_via_web(
        name=user_data["name"],
        password_hash=user_data["password_hash"],
        email=user_data["email"],
    )

    assert success, f"테스트 유저 생성 실패: {detail}"

    return user_data


@pytest.fixture
def sample_user_info():
    """
    로그인 응답의 user_info 형태를 제공한다.

    Returns:
        list: [username, password_hash, email, reset_token, resume_data]
    """
    import json

    resume_data = {
        "personal": {"gender": "남성"},
        "education": {"school": "○○대학교", "major": "컴퓨터공학"},
        "additional": {
            "internship": "ABC 인턴 3개월",
            "awards": "2024 해커톤 대상",
            "tech_stack": "Python, SQL, Docker",
        },
    }

    return [
        "테스트유저",
        "hashed_password",
        "test@example.com",
        None,
        json.dumps(resume_data, ensure_ascii=False),
    ]


@pytest.fixture
def mock_llm_responses():
    """
    chat_logic.py의 모든 LLM 호출을 고정 응답으로 mocking한다.
    """
    responses = {
        "parse": (
            '{"company": "네이버", "job": "백엔드", '
            '"question": "지원동기", "char_limit": 500, '
            '"question_type": "motivation"}'
        ),
        "draft": (
            "저는 데이터를 활용 가능한 형태로 정리하는 과정에 관심이 많습니다. "
            "학부에서 서로 다른 형식의 데이터를 정리하고 일관된 기준으로 관리하는 작업을 "
            "맡으며 데이터 품질의 중요성을 배웠습니다. ABC 인턴에서는 데이터 파이프라인 "
            "구축 경험을 통해 신뢰할 수 있는 구조를 만드는 일의 중요성을 실감했습니다. "
            "네이버 백엔드 조직에서 안정적이고 신뢰할 수 있는 데이터 기반을 만드는 데 "
            "기여하고 싶습니다."
        ),
        "refine": (
            "저는 데이터를 단순 수집보다 활용 가능한 구조로 정리하는 과정에 관심이 많습니다. "
            "학부 프로젝트에서 서로 다른 형식의 데이터를 일관된 기준으로 관리하며 품질 확보의 "
            "중요성을 배웠습니다. ABC 인턴에서는 데이터 파이프라인 구축을 통해 신뢰할 수 있는 "
            "구조를 만드는 일을 경험했습니다. 네이버 백엔드 조직에서 안정적인 데이터 기반을 "
            "함께 만들어가고 싶습니다."
        ),
        "evaluate": (
            "평가 결과: 좋다\n"
            "이유: 문항 의도와 사용자 경험이 자연스럽게 이어집니다.\n"
            "보완 포인트:\n"
            "- 첫 문장을 조금 더 구체적으로 다듬어 보세요.\n"
            "- 마지막 문단의 기여 방향을 더 현실적인 표현으로 정리하면 좋습니다."
        ),
    }

    mock_chain = MagicMock()
    mock_chain.invoke.side_effect = [
        responses["parse"],
        responses["draft"],
        responses["refine"],
        responses["evaluate"],
    ]

    with patch("services.chat_logic.llm_gpt") as mock_gpt, patch(
        "services.chat_logic.llm_groq"
    ) as mock_groq, patch("services.chat_logic.local_llm") as mock_local:

        mock_gpt.return_value = MagicMock()
        mock_groq.return_value = MagicMock()
        mock_local.return_value = MagicMock()

        yield {
            "gpt": mock_gpt,
            "groq": mock_groq,
            "local": mock_local,
            "responses": responses,
        }


@pytest.fixture
def mock_retriever():
    """
    HybridRetriever가 고정된 Document 리스트를 반환하도록 mocking한다.
    """
    from langchain_core.documents import Document

    fake_docs = [
        Document(
            page_content=(
                "저는 데이터를 체계적으로 정리하는 데 관심이 많습니다. "
                "학부 프로젝트에서 전처리 기준을 세우고 결과를 "
                "해석하기 쉬운 구조로 만드는 경험을 쌓았습니다."
            ),
            metadata={"id": 1, "selfintro_score": 55, "relevance_score": 0.42},
        ),
        Document(
            page_content=(
                "분석 결과보다 그 결과가 실제로 쓰일 수 있도록 만드는 "
                "구조와 기준에 더 관심이 많습니다. 데이터 정제, SQL 경험이 있습니다."
            ),
            metadata={"id": 2, "selfintro_score": 52, "relevance_score": 0.38},
        ),
        Document(
            page_content=(
                "팀 프로젝트에서 데이터의 양보다 신뢰할 수 있는 구조를 "
                "만드는 일이 중요하다는 점을 배웠습니다."
            ),
            metadata={"id": 3, "selfintro_score": 50, "relevance_score": 0.35},
        ),
    ]

    mock = MagicMock()
    mock.invoke.return_value = fake_docs

    with patch("services.chat_logic.selfintro_retriever", mock):
        yield mock


@pytest.fixture
def logged_in_client(client, test_user):
    """
    로그인이 완료된 상태의 TestClient를 제공한다.
    """
    response = client.post(
        "auth/login",
        json={"email": test_user["email"], "password": test_user["password"]},
    )
    assert response.status_code == 200, f"로그인 실패: {response.text}"

    return {
        "client": client,
        "user_info": response.json().get("user_info"),
        "email": test_user["email"],
    }
